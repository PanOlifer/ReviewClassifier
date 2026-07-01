from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence, Tuple

import pandas as pd

from src.config import LABELS_5000_XLSX, MANUAL_LABELS_XLSX, WEAK_LABELS_XLSX, MIN_MANUAL_LABELS

VALID_LABELS = ["optimism", "skepticism", "mixed"]


def _read_and_clean(path: Path, allowed_labels: Sequence[str] | None = None) -> pd.DataFrame:
    df = pd.read_excel(path)
    required = {"fragment_text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"В файле разметки {path} отсутствуют обязательные столбцы: {sorted(missing)}")
    allowed = list(allowed_labels or VALID_LABELS)
    df = df.copy()
    df["label"] = df["label"].astype(str).str.strip()
    df = df[df["label"].isin(allowed)].copy()
    df["fragment_text"] = df["fragment_text"].astype(str).fillna("")
    return df


def resolve_labeled_fragments(
    *,
    allowed_labels: Sequence[str] | None = None,
    require_min_total: int = MIN_MANUAL_LABELS,
    allow_weak_fallback: bool = False,
) -> Tuple[pd.DataFrame, Path, str]:
    """Return the labeled dataset used for training.

    The function deliberately prefers data/labels/labeled_fragments_5000.xlsx.
    This prevents the common failure mode where an old local
    data/labels/labeled_fragments.xlsx with 1000 rows is silently used for training.
    """
    manual_candidates = []
    if LABELS_5000_XLSX.exists():
        manual_candidates.append((LABELS_5000_XLSX, "manual_5000"))
    if MANUAL_LABELS_XLSX.exists():
        manual_candidates.append((MANUAL_LABELS_XLSX, "manual"))

    checked = []
    for path, source in manual_candidates:
        df_all = _read_and_clean(path, VALID_LABELS)
        checked.append(f"{path}: {len(df_all)} valid labels")
        if len(df_all) >= require_min_total:
            if allowed_labels is not None:
                df = df_all[df_all["label"].isin(list(allowed_labels))].copy()
            else:
                df = df_all
            print(f"Используется файл разметки: {path}")
            print(f"Всего валидных размеченных фрагментов: {len(df_all)}")
            print("Распределение меток:")
            print(df_all["label"].value_counts().to_string())
            if allowed_labels is not None:
                print(f"После фильтрации по меткам {list(allowed_labels)}: {len(df)}")
                print(df["label"].value_counts().to_string())
            return df, path, source

    if allow_weak_fallback and WEAK_LABELS_XLSX.exists():
        df = _read_and_clean(WEAK_LABELS_XLSX, allowed_labels)
        print(f"ВНИМАНИЕ: используется слабая разметка: {WEAK_LABELS_XLSX}")
        return df, WEAK_LABELS_XLSX, "weak"

    details = "; ".join(checked) if checked else "ручные файлы разметки не найдены"
    raise ValueError(
        "Модель не обучается на 5000, потому что не найден файл ручной разметки "
        f"минимум на {require_min_total} валидных строк. Проверено: {details}.\n"
        "Исправление: положите файл data/labels/labeled_fragments_5000.xlsx "
        "или замените data/labels/labeled_fragments.xlsx файлом на 5000 строк. "
        "Можно запустить: python install_5000_labels.py"
    )
