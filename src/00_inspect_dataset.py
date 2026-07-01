import pandas as pd
from src.config import RAW_REVIEWS_XLSX, RAW_REVIEWS_FULL_XLSX, RAW_ANALYSIS_TABLES_XLSX, RESULTS_DIR, DATASET_INSPECTION_XLSX
from src.utils import ensure_dirs, read_all_sheet_or_concat, year_from_review_date, safe_to_excel_sheets


def safe_min(series):
    s = series.dropna()
    return int(s.min()) if len(s) else ""


def safe_max(series):
    s = series.dropna()
    return int(s.max()) if len(s) else ""


def main():
    ensure_dirs(RESULTS_DIR)
    input_path = RAW_REVIEWS_XLSX if RAW_REVIEWS_XLSX.exists() else RAW_REVIEWS_FULL_XLSX
    if not input_path.exists():
        raise FileNotFoundError("Не найден основной Excel-файл с рецензиями в data/raw/.")

    df = read_all_sheet_or_concat(input_path).copy()
    df["review_year"] = df["review_date"].map(year_from_review_date)
    df = df.drop_duplicates(subset=["kp_id", "review_id"])

    invalid_dates = df[df["review_year"].isna()][
        [c for c in ["kp_id", "film_title", "review_id", "review_date", "review_title"] if c in df.columns]
    ].copy()

    overview = pd.DataFrame([
        {"Показатель": "Файл", "Значение": str(input_path.name)},
        {"Показатель": "Количество рецензий после дедупликации", "Значение": len(df)},
        {"Показатель": "Количество уникальных произведений", "Значение": df["film_title"].nunique()},
        {"Показатель": "Минимальный год рецензии", "Значение": safe_min(df["review_year"])},
        {"Показатель": "Максимальный год рецензии", "Значение": safe_max(df["review_year"])},
        {"Показатель": "Нераспознанные даты", "Значение": int(df["review_year"].isna().sum())},
        {"Показатель": "Пустые review_text", "Значение": int(df["review_text"].isna().sum())},
        {"Показатель": "Пустые review_title", "Значение": int(df["review_title"].isna().sum()) if "review_title" in df.columns else "нет поля"},
    ])

    by_year = (
        df.dropna(subset=["review_year"])
        .groupby("review_year")
        .size()
        .reset_index(name="Количество рецензий")
        .sort_values("review_year")
    )
    if len(by_year):
        by_year["review_year"] = by_year["review_year"].astype(int)

    by_film = df.groupby("film_title").size().reset_index(name="Количество рецензий").sort_values("Количество рецензий", ascending=False)
    by_type = df.groupby("review_type").size().reset_index(name="Количество рецензий").sort_values("Количество рецензий", ascending=False)

    sheets = {
        "overview": overview,
        "reviews_by_year": by_year,
        "reviews_by_film": by_film,
        "reviews_by_type": by_type,
        "invalid_dates": invalid_dates,
    }

    if RAW_ANALYSIS_TABLES_XLSX.exists():
        xls = pd.ExcelFile(RAW_ANALYSIS_TABLES_XLSX)
        analysis_sheets = pd.DataFrame({"Лист аналитического файла": xls.sheet_names})
        sheets["analysis_sheets"] = analysis_sheets

    safe_to_excel_sheets(sheets, DATASET_INSPECTION_XLSX)
    print(f"Сохранён отчёт проверки набора данных: {DATASET_INSPECTION_XLSX}")
    print(overview)


if __name__ == "__main__":
    main()
