from pathlib import Path
import shutil
import pandas as pd

ROOT = Path(__file__).resolve().parent
src = ROOT / "data" / "labels" / "labeled_fragments_5000.xlsx"
dst = ROOT / "data" / "labels" / "labeled_fragments.xlsx"
backup = ROOT / "data" / "labels" / "labeled_fragments_1000_backup.xlsx"

if not src.exists():
    raise FileNotFoundError(f"Не найден {src}. Положите туда файл labeled_fragments_5000.xlsx")

if dst.exists():
    df_old = pd.read_excel(dst)
    old_count = int(df_old.get("label", pd.Series(dtype=str)).isin(["optimism", "skepticism", "mixed"]).sum()) if "label" in df_old.columns else len(df_old)
    if old_count < 5000 and not backup.exists():
        shutil.copy2(dst, backup)
        print(f"Старый файл сохранён как backup: {backup}")

shutil.copy2(src, dst)
df = pd.read_excel(dst)
valid = df[df["label"].isin(["optimism", "skepticism", "mixed"])]
print(f"Установлен файл разметки для обучения: {dst}")
print(f"Валидных размеченных фрагментов: {len(valid)}")
print(valid["label"].value_counts().to_string())
if len(valid) < 5000:
    raise SystemExit("Ошибка: после установки валидных строк меньше 5000.")
