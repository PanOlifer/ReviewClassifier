"""Optional PyTorch prediction script.

Writes a separate file and does not overwrite the main article outputs.
Run after: python -m src.09_train_pytorch_classifier
"""
from __future__ import annotations

import json
import re
from typing import Dict, List

import numpy as np
import pandas as pd

from src.config import TECH_FRAGMENTS_CSV, RESULTS_DIR, MODELS_DIR, MIN_CLASS_PROB, MIN_PROB_MARGIN
from src.utils import ensure_dirs, safe_to_csv

try:
    import torch
    import torch.nn as nn
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyTorch не установлен. Установите: pip install torch") from exc

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+")
MODEL_PATH = MODELS_DIR / "pytorch_embeddingbag_classifier.pt"
VOCAB_PATH = MODELS_DIR / "pytorch_vocab.json"
OUT_CSV = RESULTS_DIR / "classification_fragment_level_pytorch.csv"


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(str(text).lower())


def encode(text: str, vocab: Dict[str, int]) -> List[int]:
    ids = [vocab.get(tok, 0) for tok in tokenize(text)]
    return ids if ids else [0]


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
        return self.net(self.embedding(text, offsets))


def main() -> None:
    ensure_dirs(RESULTS_DIR)
    if not MODEL_PATH.exists() or not VOCAB_PATH.exists():
        raise FileNotFoundError("Нет PyTorch-модели. Сначала запустите: python -m src.09_train_pytorch_classifier")

    checkpoint = torch.load(MODEL_PATH, map_location="cpu")
    labels = checkpoint["labels"]
    cfg = checkpoint["config"]
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    model = EmbeddingBagClassifier(
        vocab_size=len(vocab),
        embedding_dim=cfg["embedding_dim"],
        hidden_dim=cfg["hidden_dim"],
        num_classes=len(labels),
        dropout=cfg["dropout"],
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    df = pd.read_csv(TECH_FRAGMENTS_CSV)
    probs = []
    with torch.no_grad():
        for text in df["fragment_text"].astype(str):
            token_ids = encode(text, vocab)
            text_tensor = torch.tensor(token_ids, dtype=torch.long)
            offsets = torch.tensor([0], dtype=torch.long)
            logits = model(text_tensor, offsets)
            prob = torch.softmax(logits, dim=1).cpu().numpy()[0]
            probs.append(prob)
    probs = np.asarray(probs)

    for idx, label in enumerate(labels):
        df[f"torch_prob_{label}"] = probs[:, idx]

    def final_label(row):
        values = {label: row[f"torch_prob_{label}"] for label in labels}
        best_label = max(values, key=values.get)
        best = values[best_label]
        second = max(v for k, v in values.items() if k != best_label)
        if best < MIN_CLASS_PROB:
            return "uncertain"
        if best_label == "optimism" and (best - second) >= MIN_PROB_MARGIN:
            return "confident_optimism"
        if best_label == "skepticism" and (best - second) >= MIN_PROB_MARGIN:
            return "confident_skepticism"
        if best_label == "mixed":
            return "mixed"
        return "uncertain"

    df["torch_final_label"] = df.apply(final_label, axis=1)
    safe_to_csv(df, OUT_CSV)
    print(df["torch_final_label"].value_counts())
    print(f"Сохранено: {OUT_CSV}")
    print("Важно: этот файл не используется основным pipeline и не перезаписывает таблицы статьи.")


if __name__ == "__main__":
    main()
