import pandas as pd
import matplotlib.pyplot as plt
from src.config import RESULTS_DIR, FIGURES_DIR
from src.utils import ensure_dirs


def heatmap(df, path, xlabel, ylabel, cbar_label):
    fig, ax = plt.subplots(figsize=(8.8, 9.2))
    im = ax.imshow(df.values, aspect="auto", cmap="Blues", vmin=0, vmax=df.values.max())
    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(df.columns, rotation=25, ha="right")
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(cbar_label)
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            val = int(df.iat[i, j])
            if val:
                ax.text(j, i, str(val), ha="center", va="center", fontsize=8.5, fontweight="bold", color="black")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main():
    ensure_dirs(FIGURES_DIR)
    yearly = pd.read_csv(RESULTS_DIR / "yearly_polarity.csv")
    yearly = yearly[(yearly["Год"] >= 2005) & (yearly["Год"] <= 2025)]
    heat_year = yearly.set_index("Год")[["Оптимистические высказывания", "Скептические высказывания"]]
    heatmap(
        heat_year,
        FIGURES_DIR / "heatmap_yearly_polarity_2005_2025.png",
        "Тип высказываний",
        "Год публикации рецензий",
        "Количество высказываний"
    )

    film = pd.read_csv(RESULTS_DIR / "film_polarity.csv").head(20)
    heat_film = film.set_index("Фильм")[["Оптимистические высказывания", "Скептические высказывания"]]
    heatmap(
        heat_film,
        FIGURES_DIR / "heatmap_film_polarity_top20.png",
        "Тип высказываний",
        "Произведения",
        "Количество высказываний"
    )

    print(f"Сохранено: {FIGURES_DIR / 'heatmap_yearly_polarity_2005_2025.png'}")
    print(f"Сохранено: {FIGURES_DIR / 'heatmap_film_polarity_top20.png'}")


if __name__ == "__main__":
    main()
