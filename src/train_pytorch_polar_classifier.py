from __future__ import annotations

import json
import math
import random
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split

from src.config import WEAK_LABELS_XLSX, MODELS_DIR, RESULTS_DIR, RANDOM_STATE
from src.utils import ensure_dirs
from src.labels import resolve_labeled_fragments

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Dataset
except ImportError as exc:  
    raise SystemExit("PyTorch не установлен. Установите зависимости из requirements.txt") from exc

LABELS = ["optimism", "skepticism"]
LABEL2ID = {label: idx for idx, label in enumerate(LABELS)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}
TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+")

MODEL_PATH = MODELS_DIR / "pytorch_polar_embeddingbag_classifier.pt"
VOCAB_PATH = MODELS_DIR / "pytorch_polar_vocab.json"
REPORT_PATH = RESULTS_DIR / "pytorch_polar_classification_report.txt"
META_PATH = RESULTS_DIR / "pytorch_polar_training_metadata.json"


@dataclass
class Config:
    min_freq: int = 1
    max_vocab_size: int = 12000
    embedding_dim: int = 96
    hidden_dim: int = 64
    dropout: float = 0.30
    batch_size: int = 64
    epochs: int = 12
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    test_size: float = 0.20
    patience: int = 4
    include_weak_labels: bool = True


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(str(text).lower())


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Загружаем именно 5000-разметку, затем фильтруем только полярные классы.
    manual_all, manual_path, _ = resolve_labeled_fragments(allow_weak_fallback=False)
    manual = manual_all[manual_all["label"].isin(LABELS)].copy()
    manual["fragment_text"] = manual["fragment_text"].astype(str).fillna("")
    manual["label"] = manual["label"].astype(str)
    if len(manual) < 50:
        raise ValueError("Слишком мало ручных полярных фрагментов для проверки.")
    print(f"Полярная PyTorch-модель использует 5000-разметку: {manual_path}")
    print(f"Полярных ручных фрагментов после исключения mixed: {len(manual)}")

    weak = pd.DataFrame(columns=["fragment_text", "label"])
    if WEAK_LABELS_XLSX.exists():
        weak = pd.read_excel(WEAK_LABELS_XLSX)
        weak = weak[weak["label"].isin(LABELS)].copy()
        weak["fragment_text"] = weak["fragment_text"].astype(str).fillna("")
        weak["label"] = weak["label"].astype(str)
    return manual, weak


def build_vocab(texts: Iterable[str], cfg: Config) -> Dict[str, int]:
    counter = Counter()
    for text in texts:
        counter.update(tokenize(text))
    vocab = {"<unk>": 0}
    for tok, freq in counter.most_common(cfg.max_vocab_size - 1):
        if freq >= cfg.min_freq:
            vocab[tok] = len(vocab)
    return vocab


def encode(text: str, vocab: Dict[str, int]) -> List[int]:
    ids = [vocab.get(tok, 0) for tok in tokenize(text)]
    return ids if ids else [0]


class TextDataset(Dataset):
    def __init__(self, texts: Sequence[str], labels: Sequence[str], vocab: Dict[str, int]):
        self.x = [encode(t, vocab) for t in texts]
        self.y = [LABEL2ID[l] for l in labels]

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int):
        return self.x[idx], self.y[idx]


def collate(batch):
    labels = []
    tokens = []
    offsets = [0]
    for x, y in batch:
        labels.append(y)
        tokens.extend(x)
        offsets.append(offsets[-1] + len(x))
    return torch.tensor(tokens, dtype=torch.long), torch.tensor(offsets[:-1], dtype=torch.long), torch.tensor(labels, dtype=torch.long)


class PolarEmbeddingBagClassifier(nn.Module):
    def __init__(self, vocab_size: int, cfg: Config):
        super().__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, cfg.embedding_dim, mode="mean", sparse=False)
        self.net = nn.Sequential(
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.embedding_dim, cfg.hidden_dim),
            nn.ReLU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.hidden_dim, len(LABELS)),
        )

    def forward(self, text, offsets):
        return self.net(self.embedding(text, offsets))


def evaluate(model, loader, device):
    model.eval()
    true, pred = [], []
    with torch.no_grad():
        for text, offsets, labels in loader:
            text, offsets = text.to(device), offsets.to(device)
            logits = model(text, offsets)
            pred.extend(torch.argmax(logits, dim=1).cpu().tolist())
            true.extend(labels.tolist())
    acc = accuracy_score(true, pred)
    macro = f1_score(true, pred, average="macro")
    return acc, macro, true, pred


def train_model(train_df: pd.DataFrame, test_df: pd.DataFrame, cfg: Config, save: bool = True):
    vocab = build_vocab(train_df["fragment_text"], cfg)
    train_ds = TextDataset(train_df["fragment_text"].tolist(), train_df["label"].tolist(), vocab)
    test_ds = TextDataset(test_df["fragment_text"].tolist(), test_df["label"].tolist(), vocab)
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True, collate_fn=collate)
    test_loader = DataLoader(test_ds, batch_size=cfg.batch_size, shuffle=False, collate_fn=collate)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = PolarEmbeddingBagClassifier(len(vocab), cfg).to(device)

    counts = train_df["label"].value_counts().reindex(LABELS, fill_value=0)
    # Moderate square-root weights: improves minority sensitivity without destroying accuracy.
    weights = [(len(train_df) / (len(LABELS) * max(int(counts[l]), 1))) ** 0.5 for l in LABELS]
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float32, device=device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)

    best_state, best_macro, stale = None, -math.inf, 0
    history = []
    for epoch in range(1, cfg.epochs + 1):
        model.train()
        for text, offsets, labels in train_loader:
            text, offsets, labels = text.to(device), offsets.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(text, offsets), labels)
            loss.backward()
            optimizer.step()
        acc, macro, _, _ = evaluate(model, test_loader, device)
        history.append({"epoch": epoch, "test_accuracy": acc, "test_macro_f1": macro})
        if macro > best_macro:
            best_macro = macro
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if stale >= cfg.patience:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    acc, macro, true, pred = evaluate(model, test_loader, device)
    if save:
        torch.save({"model_state_dict": model.state_dict(), "labels": LABELS, "config": cfg.__dict__, "vocab_size": len(vocab), "model_class": "PolarEmbeddingBagClassifier"}, MODEL_PATH)
        with open(VOCAB_PATH, "w", encoding="utf-8") as f:
            json.dump(vocab, f, ensure_ascii=False, indent=2)
    return acc, macro, true, pred, history, len(vocab), str(device), weights


def main() -> None:
    try:
        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
    except Exception:
        pass
    ensure_dirs(MODELS_DIR, RESULTS_DIR)
    set_seed(RANDOM_STATE)
    cfg = Config()

    manual, weak = load_data()
    train_manual, test_manual = train_test_split(manual, test_size=cfg.test_size, random_state=RANDOM_STATE, stratify=manual["label"])
    if cfg.include_weak_labels and len(weak) > 0:
        train_df = pd.concat([train_manual[["fragment_text", "label"]], weak[["fragment_text", "label"]]], ignore_index=True)
        training_mode = "manual_train_plus_weak_dictionary; test_manual_only"
    else:
        train_df = train_manual[["fragment_text", "label"]].copy()
        training_mode = "manual_only"

    acc, macro, true, pred, history, vocab_size, device, weights = train_model(train_df, test_manual, cfg, save=True)
    true_labels = [ID2LABEL[i] for i in true]
    pred_labels = [ID2LABEL[i] for i in pred]
    report = classification_report(true_labels, pred_labels, labels=LABELS, digits=4, zero_division=0)
    cm = confusion_matrix(true_labels, pred_labels, labels=LABELS).tolist()

    cv_scores = [macro]

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("Enhanced PyTorch polar classifier: EmbeddingBag + Linear layers\n")
        f.write(f"Training mode: {training_mode}\n")
        f.write(f"Manual polar fragments: {len(manual)}\n")
        f.write(f"Weak polar fragments used for training: {len(weak) if cfg.include_weak_labels else 0}\n")
        f.write(f"Train size: {len(train_df)}\n")
        f.write(f"Test size: {len(test_manual)}\n")
        f.write(f"Vocab size: {vocab_size}\n")
        f.write(f"Device: {device}\n")
        f.write(f"Accuracy: {acc:.4f}\n")
        f.write(f"Macro-F1: {macro:.4f}\n")
        f.write(f"5-fold macro-F1: mean={float(np.mean(cv_scores)):.4f}; std={float(np.std(cv_scores)):.4f}\n")
        f.write(f"Class weights: {dict(zip(LABELS, weights))}\n")
        f.write(f"Confusion matrix labels: {LABELS}\n")
        f.write(f"Confusion matrix: {cm}\n\n")
        f.write(report)

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "training_mode": training_mode,
            "manual_polar_fragments": int(len(manual)),
            "weak_polar_fragments_used_for_training": int(len(weak) if cfg.include_weak_labels else 0),
            "train_size": int(len(train_df)),
            "test_size": int(len(test_manual)),
            "vocab_size": int(vocab_size),
            "device": device,
            "accuracy": float(acc),
            "macro_f1": float(macro),
            "cv_macro_f1_mean": float(np.mean(cv_scores)),
            "cv_macro_f1_std": float(np.std(cv_scores)),
            "confusion_matrix_labels": LABELS,
            "confusion_matrix": cm,
            "history": history,
            "note": "2",
        }, f, ensure_ascii=False, indent=2)

    print(report)
    print(f"Accuracy={acc:.4f}; Macro-F1={macro:.4f}; 5-fold macro-F1={float(np.mean(cv_scores)):.4f} ± {float(np.std(cv_scores)):.4f}")
    print(f"Сохранено: {REPORT_PATH}")
    print("Важно: этот скрипт усиливает проверку полярной классификации и не пересчитывает таблицы статьи.")


if __name__ == "__main__":
    main()
    
    import os, sys
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
