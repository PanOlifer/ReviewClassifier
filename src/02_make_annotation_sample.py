from __future__ import annotations

import argparse
import pandas as pd

from src.config import TECH_FRAGMENTS_CSV, LABELS_DIR, ANNOTATION_SAMPLE_XLSX, ANNOTATION_SAMPLE_SIZE, RANDOM_STATE
from src.utils import ensure_dirs


def stratified_exact_sample(df: pd.DataFrame, n: int) -> pd.DataFrame:
    if n <= 0:
        raise ValueError("Размер выборки должен быть положительным.")
    if len(df) < n:
        raise ValueError(f"Недостаточно технологически релевантных фрагментов: {len(df)} < {n}")

    df = df.copy()
    parts = []
    for _, part in df.groupby("review_year", dropna=False):
        quota = int(round(len(part) / len(df) * n))
        quota = max(1, quota)
        quota = min(quota, len(part))
        parts.append(part.sample(n=quota, random_state=RANDOM_STATE))

    sample = pd.concat(parts, axis=0)
    if len(sample) > n:
        sample = sample.sample(n=n, random_state=RANDOM_STATE)
    if len(sample) < n:
        need = n - len(sample)
        rest = df.drop(index=sample.index, errors="ignore")
        sample = pd.concat([sample, rest.sample(n=need, random_state=RANDOM_STATE)], axis=0)

    sample = sample.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    if len(sample) != n:
        raise RuntimeError(f"Не удалось собрать точную выборку: {len(sample)} != {n}")
    return sample


def main():
    parser = argparse.ArgumentParser(description="Создать файл для ручной разметки фрагментов.")
    parser.add_argument("--n", type=int, default=ANNOTATION_SAMPLE_SIZE, help="Размер выборки, по умолчанию из config.py")
    args = parser.parse_args()

    ensure_dirs(LABELS_DIR)
    df = pd.read_csv(TECH_FRAGMENTS_CSV)
    df = df.dropna(subset=["fragment_text"]).copy()

    sample = stratified_exact_sample(df, args.n)
    sample["label"] = ""
    sample["narrative_code"] = ""
    sample["coder_comment"] = ""

    cols = [
        "fragment_id", "kp_id", "film_title", "review_id", "review_year",
        "fragment_text", "label", "narrative_code", "coder_comment"
    ]
    sample[cols].to_excel(ANNOTATION_SAMPLE_XLSX, index=False)
    print(f"Создан файл для ручной разметки: {ANNOTATION_SAMPLE_XLSX}")
    print(f"Количество строк: {len(sample)}")
    print("Заполните столбец label значениями: optimism, skepticism, mixed.")


if __name__ == "__main__":
    main()
