import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

from src.config import MODEL_PATH, RESULTS_DIR, MODELS_DIR, RANDOM_STATE
from src.utils import ensure_dirs
from src.labels import resolve_labeled_fragments


def load_labels():
    df, path, source = resolve_labeled_fragments(allow_weak_fallback=False)
    if len(df) < 5000:
        raise ValueError(f"Ожидалось 5000 размеченных фрагментов, получено {len(df)} из {path}")
    return df, source, path


def main():
    ensure_dirs(RESULTS_DIR, MODELS_DIR)
    df, source, path = load_labels()

    X = df["fragment_text"].astype(str)
    y = df["label"].astype(str)

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 1),
            min_df=2,
            max_df=0.90,
            max_features=10000,
            sublinear_tf=True
        )),
        ("clf", OneVsRestClassifier(LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            solver="liblinear"
        )))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y if y.value_counts().min() >= 2 else None
    )

    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    report = classification_report(y_test, pred, digits=4)
    acc = accuracy_score(y_test, pred)
    macro_f1 = f1_score(y_test, pred, average="macro")

    cv_text = ""
    if y.value_counts().min() >= 5:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        scores = cross_val_score(model, X, y, cv=cv, scoring="f1_macro")
        cv_text = f"5-fold macro-F1: mean={scores.mean():.4f}; std={scores.std():.4f}\\n"

    with open(RESULTS_DIR / "classification_report.txt", "w", encoding="utf-8") as f:
        f.write("Baseline model: TF-IDF + Logistic Regression\\n")
        f.write(f"Label source: {source}\\n")
        f.write(f"Label file: {path}\\n")
        f.write(f"Total labeled fragments: {len(df)}\\n")
        f.write(f"Train size: {len(X_train)}\\n")
        f.write(f"Test size: {len(X_test)}\\n")
        f.write(f"Accuracy: {acc:.4f}\\n")
        f.write(f"Macro-F1: {macro_f1:.4f}\\n")
        f.write(cv_text)
        f.write("\\n")
        f.write(report)

    joblib.dump(model, MODEL_PATH)
    print(report)
    print(f"Accuracy={acc:.4f}; Macro-F1={macro_f1:.4f}")
    print(cv_text.strip())
    print(f"Модель сохранена: {MODEL_PATH}")
    print(f"Отчёт сохранён: {RESULTS_DIR / 'classification_report.txt'}")


if __name__ == "__main__":
    main()
