import pandas as pd
from src.config import RAW_REVIEWS_XLSX, RAW_REVIEWS_FULL_XLSX, PROCESSED_DIR, FRAGMENTS_CSV, TECH_FRAGMENTS_CSV, TECH_MARKERS
from src.utils import ensure_dirs, read_all_sheet_or_concat, normalize_text, split_sentences, marker_score, year_from_review_date, safe_to_csv


def main():
    ensure_dirs(PROCESSED_DIR)
    input_path = RAW_REVIEWS_XLSX if RAW_REVIEWS_XLSX.exists() else RAW_REVIEWS_FULL_XLSX
    if not input_path.exists():
        raise FileNotFoundError("Не найден Excel-файл с рецензиями в data/raw/.")

    reviews = read_all_sheet_or_concat(input_path).copy()
    required = ["kp_id", "film_title", "review_id", "review_date", "review_text"]
    missing = [c for c in required if c not in reviews.columns]
    if missing:
        raise ValueError(f"В файле отсутствуют обязательные поля: {missing}")

    reviews["review_text"] = reviews["review_text"].map(normalize_text)
    reviews = reviews[reviews["review_text"].str.len() > 0].copy()
    reviews = reviews.drop_duplicates(subset=["kp_id", "review_id"]).copy()
    reviews["review_year"] = reviews["review_date"].map(year_from_review_date)
    reviews = reviews.dropna(subset=["review_year"]).copy()
    reviews["review_year"] = reviews["review_year"].astype(int)

    rows = []
    for _, r in reviews.iterrows():
        for idx, fragment in enumerate(split_sentences(r["review_text"])):
            rows.append({
                "fragment_id": f"{r['kp_id']}_{r['review_id']}_{idx}",
                "kp_id": r.get("kp_id"),
                "film_title": r.get("film_title"),
                "review_id": r.get("review_id"),
                "review_type": r.get("review_type"),
                "review_date": r.get("review_date"),
                "review_year": r.get("review_year"),
                "author": r.get("author"),
                "fragment_index": idx,
                "fragment_text": fragment,
                "tech_marker_hits": marker_score(fragment, TECH_MARKERS),
            })

    fragments = pd.DataFrame(rows)
    fragments["is_tech_relevant"] = fragments["tech_marker_hits"] > 0
    tech = fragments[fragments["is_tech_relevant"]].copy()

    safe_to_csv(fragments, FRAGMENTS_CSV)
    safe_to_csv(tech, TECH_FRAGMENTS_CSV)

    print(f"Рецензий после дедупликации: {len(reviews)}")
    print(f"Всего фрагментов: {len(fragments)}")
    print(f"Технологически релевантных фрагментов: {len(tech)}")
    print(f"Сохранено: {FRAGMENTS_CSV}")
    print(f"Сохранено: {TECH_FRAGMENTS_CSV}")


if __name__ == "__main__":
    main()
