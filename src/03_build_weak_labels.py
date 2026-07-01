import pandas as pd
from src.config import TECH_FRAGMENTS_CSV, WEAK_LABELS_XLSX, MANUAL_LABELS_XLSX, LABELS_5000_XLSX, LABELS_DIR, OPTIMISM_MARKERS, SKEPTICISM_MARKERS, RANDOM_STATE
from src.utils import ensure_dirs, marker_score


def weak_label(text: str):
    opt = marker_score(text, OPTIMISM_MARKERS)
    sk = marker_score(text, SKEPTICISM_MARKERS)
    if opt == 0 and sk == 0:
        return None
    if opt >= sk + 1:
        return "optimism"
    if sk >= opt + 1:
        return "skepticism"
    return "mixed"


def main():
    ensure_dirs(LABELS_DIR)

    if LABELS_5000_XLSX.exists():
        print(f"Найдена 5000-разметка: {LABELS_5000_XLSX}")
        print("Слабая разметка не создаётся и не используется.")
        return
    if MANUAL_LABELS_XLSX.exists():
        print(f"Ручная разметка найдена: {MANUAL_LABELS_XLSX}")
        print("Слабая разметка не создаётся и не используется.")
        return

    df = pd.read_csv(TECH_FRAGMENTS_CSV).copy()
    df["label"] = df["fragment_text"].map(weak_label)
    weak = df[df["label"].isin(["optimism", "skepticism", "mixed"])].copy()

    parts = []
    for label, n in [("optimism", 700), ("skepticism", 700), ("mixed", 350)]:
        p = weak[weak["label"] == label]
        if len(p) > n:
            p = p.sample(n=n, random_state=RANDOM_STATE)
        parts.append(p)
    out = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=RANDOM_STATE)

    cols = ["fragment_id", "film_title", "review_id", "review_year", "fragment_text", "label"]
    out[cols].to_excel(WEAK_LABELS_XLSX, index=False)
    print(f"Создана слабая разметка: {WEAK_LABELS_XLSX}")
    print(out["label"].value_counts())


if __name__ == "__main__":
    main()
