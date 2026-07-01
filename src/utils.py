import re
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []
    # Регулярная сегментация на предложения/фрагменты.
    parts = re.split(r"(?<=[.!?…])\s+|\n+|(?<=;)\s+", text)
    out = []
    for part in parts:
        part = normalize_text(part)
        if len(part) >= 25:
            out.append(part)
    return out


def marker_score(text: str, markers: Iterable[str]) -> int:
    low = text.lower()
    return sum(1 for marker in markers if marker.lower() in low)


def contains_any_marker(text: str, markers: Iterable[str]) -> bool:
    return marker_score(text, markers) > 0


def year_from_review_date(value) -> Optional[int]:
    """Устойчивое извлечение года из review_date.

    Поддерживает:
    - datetime / pandas Timestamp;
    - Excel serial date;
    - строки вида 2020-01-31, 31.01.2020, 31/01/2020;
    - строки с русскими месяцами: 5 января 2017, 12 дек. 2020;
    - любые строки, где явно присутствует год 19xx или 20xx.

    Если год не найден, возвращает None, а не выбрасывает исключение.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    # Timestamp / datetime
    try:
        if hasattr(value, "year") and not isinstance(value, str):
            y = int(value.year)
            if 1900 <= y <= 2100:
                return y
    except Exception:
        pass

    # Excel serial date
    try:
        if isinstance(value, (int, float)) and not pd.isna(value):
            dt = pd.to_datetime(value, unit="D", origin="1899-12-30", errors="coerce")
            if not pd.isna(dt):
                y = int(dt.year)
                if 1900 <= y <= 2100:
                    return y
    except Exception:
        pass

    s = str(value).strip()
    if not s:
        return None

    # Direct year extraction. This is the safest for Russian dates.
    m = re.search(r"\b(19\d{2}|20\d{2})\b", s)
    if m:
        return int(m.group(1))

    # Russian month names without explicit standard parser support.
    months = {
        "января": "01", "янв": "01", "янв.": "01",
        "февраля": "02", "фев": "02", "фев.": "02",
        "марта": "03", "мар": "03", "мар.": "03",
        "апреля": "04", "апр": "04", "апр.": "04",
        "мая": "05",
        "июня": "06", "июн": "06", "июн.": "06",
        "июля": "07", "июл": "07", "июл.": "07",
        "августа": "08", "авг": "08", "авг.": "08",
        "сентября": "09", "сен": "09", "сен.": "09", "сент": "09", "сент.": "09",
        "октября": "10", "окт": "10", "окт.": "10",
        "ноября": "11", "ноя": "11", "ноя.": "11",
        "декабря": "12", "дек": "12", "дек.": "12",
    }

    s_low = s.lower()
    for ru, mm in months.items():
        if ru in s_low:
            s_low = s_low.replace(ru, mm)

    # Try common date parsers after normalization.
    for dayfirst in (True, False):
        dt = pd.to_datetime(s_low, errors="coerce", dayfirst=dayfirst)
        if not pd.isna(dt):
            y = int(dt.year)
            if 1900 <= y <= 2100:
                return y

    return None


def read_all_sheet_or_concat(path: Path) -> pd.DataFrame:
    xls = pd.ExcelFile(path)
    if "ALL" in xls.sheet_names:
        return pd.read_excel(path, sheet_name="ALL")

    required = {"kp_id", "film_title", "review_id", "review_text"}
    frames = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        if required.issubset(df.columns):
            frames.append(df)
    if not frames:
        raise ValueError("В Excel-файле нет листа ALL и нет листов с обязательными полями.")
    return pd.concat(frames, ignore_index=True)


def safe_to_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def safe_to_excel_sheets(sheets: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
