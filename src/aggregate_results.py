import pandas as pd
from src.config import RESULTS_DIR
from src.utils import ensure_dirs, safe_to_csv, safe_to_excel_sheets


def main():
    ensure_dirs(RESULTS_DIR)
    df = pd.read_csv(RESULTS_DIR / "classification_fragment_level.csv")

    total = len(df)
    conf_opt = int((df["final_label"] == "confident_optimism").sum())
    conf_sk = int((df["final_label"] == "confident_skepticism").sum())
    mixed = int((df["final_label"] == "mixed").sum())
    uncertain = int((df["final_label"] == "uncertain").sum())

    flow = pd.DataFrame([
        {"Этап": "Технологически релевантные высказывания", "Количество": total,
         "Основание": "Первичный отбор по технологическим маркерам"},
        {"Этап": "Уверенно технооптимистические высказывания", "Количество": conf_opt,
         "Основание": "Порог вероятности и минимальный разрыв между классами"},
        {"Этап": "Уверенно техноскептические высказывания", "Количество": conf_sk,
         "Основание": "Порог вероятности и минимальный разрыв между классами"},
        {"Этап": "Смешанные случаи", "Количество": mixed,
         "Основание": "Доминирование смешанного класса или пересечение признаков"},
        {"Этап": "Неуверенные случаи", "Количество": uncertain,
         "Основание": "Недостаточная вероятность или недостаточный разрыв между классами"},
        {"Этап": "Итоговый массив уверенно классифицированных", "Количество": conf_opt + conf_sk,
         "Основание": "Используется для полярного сравнения"},
    ])

    confident = df[df["final_label"].isin(["confident_optimism", "confident_skepticism"])].copy()
    yearly = confident.pivot_table(
        index="review_year", columns="final_label", values="fragment_id",
        aggfunc="count", fill_value=0
    ).reset_index()
    for c in ["confident_optimism", "confident_skepticism"]:
        if c not in yearly.columns:
            yearly[c] = 0
    yearly = yearly.rename(columns={
        "review_year": "Год",
        "confident_optimism": "Оптимистические высказывания",
        "confident_skepticism": "Скептические высказывания",
    })
    yearly["Всего уверенных высказываний"] = yearly["Оптимистические высказывания"] + yearly["Скептические высказывания"]
    yearly["Доля оптимистических"] = yearly["Оптимистические высказывания"] / yearly["Всего уверенных высказываний"]
    yearly["Доля скептических"] = yearly["Скептические высказывания"] / yearly["Всего уверенных высказываний"]
    yearly = yearly.sort_values("Год")

    film = confident.pivot_table(
        index="film_title", columns="final_label", values="fragment_id",
        aggfunc="count", fill_value=0
    ).reset_index()
    for c in ["confident_optimism", "confident_skepticism"]:
        if c not in film.columns:
            film[c] = 0
    film = film.rename(columns={
        "film_title": "Фильм",
        "confident_optimism": "Оптимистические высказывания",
        "confident_skepticism": "Скептические высказывания",
    })
    film["Всего уверенных высказываний"] = film["Оптимистические высказывания"] + film["Скептические высказывания"]
    film = film.sort_values("Всего уверенных высказываний", ascending=False)

    safe_to_csv(flow, RESULTS_DIR / "selection_flow.csv")
    safe_to_csv(yearly, RESULTS_DIR / "yearly_polarity.csv")
    safe_to_csv(film, RESULTS_DIR / "film_polarity.csv")
    safe_to_excel_sheets({
        "selection_flow": flow,
        "yearly_polarity": yearly,
        "film_polarity": film,
    }, RESULTS_DIR / "reviewer_tables.xlsx")

    print(f"Сохранено: {RESULTS_DIR / 'reviewer_tables.xlsx'}")


if __name__ == "__main__":
    main()
