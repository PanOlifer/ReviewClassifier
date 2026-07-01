"""Optional PyTorch text classifier for reviewer-facing reproducibility.

This module trains a compact neural classifier on the existing labeled fragments.
It DOES NOT overwrite the article tables, heatmaps, or the main fragment-level
classification file. The script saves a separate PyTorch model and report.

Run:
    python -m src.09_train_pytorch_classifier
"""
from __future__ import annotations

import json
import math
import random
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split

from src.config import LABELS_DIR, MODELS_DIR, RESULTS_DIR, RANDOM_STATE
from src.utils import ensure_dirs
from src.labels import resolve_labeled_fragments

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Dataset
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyTorch не установлен. Установите его командой: pip install torch "
        "или используйте requirements.txt из обновлённого архива."
    ) from exc

LABELS = ["mixed", "optimism", "skepticism"]
LABEL2ID = {label: idx for idx, label in enumerate(LABELS)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+")

MODEL_PATH = MODELS_DIR / "pytorch_embeddingbag_classifier.pt"
VOCAB_PATH = MODELS_DIR / "pytorch_vocab.json"
REPORT_PATH = RESULTS_DIR / "pytorch_classification_report.txt"
TRAINING_META_PATH = RESULTS_DIR / "pytorch_training_metadata.json"


@dataclass
class TorchConfig:
    min_freq: int = 2
    max_vocab_size: int = 6000
    embedding_dim: int = 64
    hidden_dim: int = 64
    dropout: float = 0.25
    batch_size: int = 512
    epochs: int = 12
    learning_rate: float = 1e-3
    test_size: float = 0.20
    patience: int = 4


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(str(text).lower())


def load_labeled_fragments() -> Tuple[pd.DataFrame, Path, str]:
    df, path, source = resolve_labeled_fragments(allow_weak_fallback=False)
    required = {"fragment_text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"В файле разметки отсутствуют обязательные столбцы: {sorted(missing)}")
    if len(df) < 5000:
        raise ValueError(f"Ожидалось 5000 размеченных фрагментов для PyTorch-модели, получено {len(df)} из {path}")
    return df, path, source


def build_vocab(texts: Iterable[str], min_freq: int, max_vocab_size: int) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(tokenize(text))

    # 0 зарезервирован под unknown/padding.
    vocab = {"<unk>": 0}
    for token, freq in counter.most_common(max_vocab_size - 1):
        if freq < min_freq:
            continue
        vocab[token] = len(vocab)
    return vocab


def encode(text: str, vocab: Dict[str, int]) -> List[int]:
    ids = [vocab.get(tok, 0) for tok in tokenize(text)]
    return ids if ids else [0]


class FragmentDataset(Dataset):
    def __init__(self, texts: Sequence[str], labels: Sequence[str], vocab: Dict[str, int]):
        self.encoded = [encode(text, vocab) for text in texts]
        self.labels = [LABEL2ID[label] for label in labels]

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> Tuple[List[int], int]:
        return self.encoded[idx], self.labels[idx]


def collate_batch(batch: Sequence[Tuple[List[int], int]]) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    # EmbeddingBag ожидает один общий вектор токенов и offsets начала каждого примера.
    label_list: List[int] = []
    text_list: List[int] = []
    offsets: List[int] = [0]
    for tokens, label in batch:
        label_list.append(label)
        text_list.extend(tokens)
        offsets.append(offsets[-1] + len(tokens))
    offsets = offsets[:-1]
    return (
        torch.tensor(text_list, dtype=torch.long),
        torch.tensor(offsets, dtype=torch.long),
        torch.tensor(label_list, dtype=torch.long),
    )


class EmbeddingBagClassifier(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int, hidden_dim: int, num_classes: int, dropout: float):
        super().__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embedding_dim, sparse=False, mode="mean")
        self.net = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, text: torch.Tensor, offsets: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(text, offsets)
        return self.net(embedded)


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> Tuple[float, float, List[int], List[int]]:
    model.eval()
    true: List[int] = []
    pred: List[int] = []
    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()
    with torch.no_grad():
        for text, offsets, labels in loader:
            text, offsets, labels = text.to(device), offsets.to(device), labels.to(device)
            logits = model(text, offsets)
            loss = criterion(logits, labels)
            total_loss += loss.item() * labels.size(0)
            pred.extend(torch.argmax(logits, dim=1).cpu().tolist())
            true.extend(labels.cpu().tolist())
    avg_loss = total_loss / max(len(true), 1)
    macro_f1 = f1_score(true, pred, average="macro") if true else 0.0
    return avg_loss, macro_f1, true, pred


def main() -> None:
    try:
        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
    except Exception:
        pass
    ensure_dirs(MODELS_DIR, RESULTS_DIR, LABELS_DIR)
    set_seed(RANDOM_STATE)
    cfg = TorchConfig()

    df, label_path, label_source = load_labeled_fragments()
    y = df["label"].astype(str)
    stratify = y if y.value_counts().min() >= 2 else None
    train_df, test_df = train_test_split(
        df,
        test_size=cfg.test_size,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    print(f"Train size: {len(train_df)}; Test size: {len(test_df)}", flush=True)
    vocab = build_vocab(train_df["fragment_text"], cfg.min_freq, cfg.max_vocab_size)
    print(f"Vocab size: {len(vocab)}", flush=True)
    train_ds = FragmentDataset(train_df["fragment_text"].tolist(), train_df["label"].tolist(), vocab)
    test_ds = FragmentDataset(test_df["fragment_text"].tolist(), test_df["label"].tolist(), vocab)
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True, collate_fn=collate_batch)
    test_loader = DataLoader(test_ds, batch_size=cfg.batch_size, shuffle=False, collate_fn=collate_batch)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = EmbeddingBagClassifier(
        vocab_size=len(vocab),
        embedding_dim=cfg.embedding_dim,
        hidden_dim=cfg.hidden_dim,
        num_classes=len(LABELS),
        dropout=cfg.dropout,
    ).to(device)

    train_counts = train_df["label"].value_counts().reindex(LABELS, fill_value=0)
    class_weights = []
    for label in LABELS:
        count = max(int(train_counts[label]), 1)
        class_weights.append(len(train_df) / (len(LABELS) * count))
    weight_tensor = torch.tensor(class_weights, dtype=torch.float32, device=device)
    criterion = nn.CrossEntropyLoss(weight=weight_tensor)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=1e-4)

    best_state = None
    best_f1 = -math.inf
    epochs_without_improvement = 0
    history = []

    for epoch in range(1, cfg.epochs + 1):
        print(f"start epoch {epoch}", flush=True)
        model.train()
        train_loss = 0.0
        seen = 0
        for text, offsets, labels in train_loader:
            text, offsets, labels = text.to(device), offsets.to(device), labels.to(device)
            optimizer.zero_grad()
            logits = model(text, offsets)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * labels.size(0)
            seen += labels.size(0)

        test_loss, test_macro_f1, _, _ = evaluate(model, test_loader, device)
        train_loss = train_loss / max(seen, 1)
        history.append({"epoch": epoch, "train_loss": train_loss, "test_loss": test_loss, "test_macro_f1": test_macro_f1})
        print(f"epoch={epoch:02d} train_loss={train_loss:.4f} test_loss={test_loss:.4f} test_macro_f1={test_macro_f1:.4f}", flush=True)

        if test_macro_f1 > best_f1:
            best_f1 = test_macro_f1
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= cfg.patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    _, _, true_ids, pred_ids = evaluate(model, test_loader, device)
    true_labels = [ID2LABEL[i] for i in true_ids]
    pred_labels = [ID2LABEL[i] for i in pred_ids]
    acc = accuracy_score(true_labels, pred_labels)
    macro_f1 = f1_score(true_labels, pred_labels, average="macro")
    report = classification_report(true_labels, pred_labels, labels=LABELS, digits=4)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "labels": LABELS,
            "config": cfg.__dict__,
            "model_class": "EmbeddingBagClassifier",
            "vocab_size": len(vocab),
        },
        MODEL_PATH,
    )
    with open(VOCAB_PATH, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("PyTorch model: EmbeddingBag + Linear classifier\n")
        f.write(f"Label source: {label_source}\n")
        f.write(f"Label file: {label_path}\n")
        f.write(f"Total labeled fragments: {len(df)}\n")
        f.write(f"Train size: {len(train_df)}\n")
        f.write(f"Test size: {len(test_df)}\n")
        f.write(f"Vocab size: {len(vocab)}\n")
        f.write(f"Device: {device}\n")
        f.write(f"Accuracy: {acc:.4f}\n")
        f.write(f"Macro-F1: {macro_f1:.4f}\n")
        f.write(f"Class weights: {dict(zip(LABELS, class_weights))}\n\n")
        f.write(report)

    with open(TRAINING_META_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "label_source": label_source,
                "label_file": str(label_path),
                "total_labeled_fragments": int(len(df)),
                "train_size": int(len(train_df)),
                "test_size": int(len(test_df)),
                "vocab_size": int(len(vocab)),
                "device": str(device),
                "accuracy": float(acc),
                "macro_f1": float(macro_f1),
                "class_weights": {label: float(weight) for label, weight in zip(LABELS, class_weights)},
                "history": history,
                "note": "1",
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(report)
    print(f"Accuracy={acc:.4f}; Macro-F1={macro_f1:.4f}")
    print(f"PyTorch-модель сохранена: {MODEL_PATH}")
    print(f"Словарь сохранён: {VOCAB_PATH}")
    print(f"Отчёт сохранён: {REPORT_PATH}")


if __name__ == "__main__":
    main()
    # PyTorch/OpenMP finalizers can occasionally keep the process alive on some local setups.
    # Explicit exit prevents terminal hangs after all reports and models have been saved.
    import os, sys
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
