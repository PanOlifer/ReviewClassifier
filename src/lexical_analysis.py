import re
from collections import Counter

import pandas as pd
from nltk.stem.snowball import SnowballStemmer

from src.config import RESULTS_DIR, STOPWORDS_RU
from src.utils import ensure_dirs, safe_to_csv


TOKEN_RE = re.compile(r"[А-Яа-яЁёA-Za-z]+")


def tokenize(text):
    return TOKEN_RE.findall(str(text).lower())


def main():
    ensure_dirs(RESULTS_DIR)
    df = pd.read_csv(RESULTS_DIR / "classification_fragment_level.csv")
    stemmer = SnowballStemmer("russian")

    outputs = {}
    for label, name in [
        ("confident_optimism", "lexemes_optimism.csv"),
        ("confident_skepticism", "lexemes_skepticism.csv"),
    ]:
        texts = df[df["final_label"] == label]["fragment_text"].astype(str)
        tokens = []
        for text in texts:
            for tok in tokenize(text):
                if tok in STOPWORDS_RU or len(tok) < 3:
                    continue
                tokens.append(stemmer.stem(tok))
        total = len(tokens)
        cnt = Counter(tokens)
        out = pd.DataFrame([
            {"Лексема/стем": k, "Абсолютная частота": v, "Относительная частота": v / total if total else 0}
            for k, v in cnt.most_common(100)
        ])
        safe_to_csv(out, RESULTS_DIR / name)
        outputs[name] = len(out)

    print(outputs)


if __name__ == "__main__":
    main()
