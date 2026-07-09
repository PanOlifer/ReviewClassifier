import joblib
import pandas as pd
from src.config import TECH_FRAGMENTS_CSV, MODEL_PATH, RESULTS_DIR, MIN_CLASS_PROB, MIN_PROB_MARGIN
from src.utils import ensure_dirs, safe_to_csv


def main():
    ensure_dirs(RESULTS_DIR)
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Модель не найдена. Запустите 04_train_baseline.py")
    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(TECH_FRAGMENTS_CSV)

    probs = model.predict_proba(df["fragment_text"].astype(str))
    classes = list(model.classes_)
    for i, cls in enumerate(classes):
        df[f"prob_{cls}"] = probs[:, i]

    df["opt_prob"] = df["prob_optimism"] if "prob_optimism" in df else 0.0
    df["skept_prob"] = df["prob_skepticism"] if "prob_skepticism" in df else 0.0
    df["mixed_prob"] = df["prob_mixed"] if "prob_mixed" in df else 0.0

    def final_label(row):
        opt, sk, mx = row["opt_prob"], row["skept_prob"], row["mixed_prob"]
        best = max(opt, sk, mx)
        if best < MIN_CLASS_PROB:
            return "uncertain"
        if opt == best and (opt - max(sk, mx)) >= MIN_PROB_MARGIN:
            return "confident_optimism"
        if sk == best and (sk - max(opt, mx)) >= MIN_PROB_MARGIN:
            return "confident_skepticism"
        if mx == best:
            return "mixed"
        return "uncertain"

    df["final_label"] = df.apply(final_label, axis=1)
    safe_to_csv(df, RESULTS_DIR / "classification_fragment_level.csv")
    print(df["final_label"].value_counts())
    print(f"Сохранено: {RESULTS_DIR / 'classification_fragment_level.csv'}")


if __name__ == "__main__":
    main()
