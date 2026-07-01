import argparse
import os
import re
from typing import List, Dict, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup

CAPTCHA_MARKERS = [
    "captcha-api.yandex.ru",
    "showcaptcha",
    "smartcaptcha",
    "/captcha",
    "i am not a robot",
    "не робот",
    "подтвердите, что вы не робот",
]

def has_captcha_markers(text: str) -> bool:
    t = (text or "").lower()
    return any(m in t for m in CAPTCHA_MARKERS)

def sanitize_sheet_name(name: str) -> str:
    name = re.sub(r'[:\\/?*\[\]]', " ", name).strip()
    name = re.sub(r"\s+", " ", name)
    name = name[:31].rstrip()
    return name if name else "Sheet"

def extract_yes_no(text: str) -> Tuple[Optional[int], Optional[int]]:
    m = re.search(r"(\d+)\s*/\s*(\d+)", text)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def pick_html_files(film_dir: str) -> List[str]:
    # your convention:
    # - single page -> .html
    # - multi -> 1.html, 2.html, ...
    dot_html = os.path.join(film_dir, ".html")
    if os.path.exists(dot_html):
        return [dot_html]

    pages = []
    for fn in os.listdir(film_dir):
        if re.fullmatch(r"\d+\.html", fn):
            pages.append(os.path.join(film_dir, fn))
    pages.sort(key=lambda p: int(os.path.basename(p).split(".")[0]))
    return pages

def parse_page(html_text: str, kp_id: int, film_title: str) -> List[Dict]:
    """
    IMPORTANT:
    - Не "детектим капчу" как причину не парсить.
    - Если в HTML есть reviewItem.userReview — значит там данные, и мы их берём.
    """
    soup = BeautifulSoup(html_text, "lxml")
    items = soup.select("div.reviewItem.userReview")
    rows: List[Dict] = []

    for it in items:
        review_id = it.get("data-id")

        # type good/bad/neutral
        review_type = None
        resp = it.select_one("div.response")
        if resp and resp.get("class"):
            for c in resp.get("class", []):
                if c in ("good", "bad", "neutral"):
                    review_type = c
                    break

        # title
        meta_headline = it.select_one('meta[itemprop="headline"]')
        review_title = meta_headline.get("content") if meta_headline else None

        # author
        author_a = it.select_one("p.profile_name a")
        author = author_a.get_text(strip=True) if author_a else None
        author_url = author_a.get("href") if author_a else None
        if author_url and author_url.startswith("/"):
            author_url = "https://www.kinopoisk.ru" + author_url

        # date
        date_span = it.select_one("span.date")
        review_date = date_span.get_text(strip=True) if date_span else None

        # text
        body_el = it.select_one('[itemprop="reviewBody"]')
        review_text = body_el.get_text("\n", strip=True) if body_el else None

        # useful yes/no
        useful_yes = useful_no = None
        useful_ul = it.find("ul", class_="useful")
        if useful_ul:
            li_texts = [li.get_text(" ", strip=True) for li in useful_ul.find_all("li")]
            for t in reversed(li_texts):
                y, n = extract_yes_no(t)
                if y is not None:
                    useful_yes, useful_no = y, n
                    break

        rows.append({
            "kp_id": kp_id,
            "film_title": film_title,
            "review_id": review_id,
            "review_type": review_type,
            "review_date": review_date,
            "author": author,
            "author_url": author_url,
            "review_title": review_title,
            "review_text": review_text,
            "useful_yes": useful_yes,
            "useful_no": useful_no,
        })

    return rows

def infer_film_title_from_html(html_text: str, kp_id: int) -> str:
    soup = BeautifulSoup(html_text, "lxml")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if title:
        # often: "<Film> — отзывы и рецензии — Кинопоиск"
        return title.split("—")[0].strip()
    return f"kp_{kp_id}"

def infer_film_title_from_files(files: List[str], kp_id: int) -> str:
    # Prefer a page where reviews exist, because title there is usually correct.
    for fp in files:
        html = read_text(fp)
        soup = BeautifulSoup(html, "lxml")
        if soup.select("div.reviewItem.userReview"):
            t = infer_film_title_from_html(html, kp_id)
            return t if t else f"kp_{kp_id}"

    # fallback to first file title
    if files:
        return infer_film_title_from_html(read_text(files[0]), kp_id)
    return f"kp_{kp_id}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html-root", required=True, help="Folder like html_dump/")
    ap.add_argument("--out", required=True, help="Output xlsx")
    args = ap.parse_args()

    html_root = args.html_root

    all_rows: List[Dict] = []
    sheets: Dict[str, pd.DataFrame] = {}

    # Logging sheets (optional but useful)
    pages_log: List[Dict] = []
    empty_films: List[Dict] = []

    idx_dirs = [d for d in os.listdir(html_root) if os.path.isdir(os.path.join(html_root, d))]
    idx_dirs.sort(key=lambda x: int(x) if x.isdigit() else 10**9)

    for idx in idx_dirs:
        idx_path = os.path.join(html_root, idx)
        kp_dirs = [d for d in os.listdir(idx_path) if os.path.isdir(os.path.join(idx_path, d))]
        kp_dirs.sort(key=lambda x: int(x) if x.isdigit() else 10**9)

        for kp_str in kp_dirs:
            if not kp_str.isdigit():
                continue

            kp_id = int(kp_str)
            film_dir = os.path.join(idx_path, kp_str)
            files = pick_html_files(film_dir)
            if not files:
                continue

            film_title = infer_film_title_from_files(files, kp_id)

            film_rows: List[Dict] = []
            parsed_pages = 0

            for fp in files:
                html = read_text(fp)
                rows = parse_page(html, kp_id, film_title)

                parsed_pages += 1
                film_rows.extend(rows)

                pages_log.append({
                    "idx": idx,
                    "kp_id": kp_id,
                    "film_title": film_title,
                    "file": os.path.relpath(fp, html_root),
                    "found_reviews": len(rows),
                    "has_captcha_markers": bool(has_captcha_markers(html)),
                })

            if not film_rows:
                empty_films.append({
                    "idx": idx,
                    "kp_id": kp_id,
                    "film_title": film_title,
                    "pages_total": len(files),
                    "note": "No reviewItem.userReview found in any page",
                })
                continue

            df = pd.DataFrame(film_rows)
            if not df.empty and "review_id" in df.columns:
                df = df.drop_duplicates(subset=["kp_id", "review_id"], keep="first")

            cols = [
                "kp_id","film_title","review_id","review_type","review_date",
                "author","author_url","review_title","review_text","useful_yes","useful_no"
            ]
            df = df[[c for c in cols if c in df.columns]]

            sheet_name = sanitize_sheet_name(film_title)
            if sheet_name in sheets:
                sheet_name = sanitize_sheet_name(f"{sheet_name}_{kp_id}")
            sheets[sheet_name] = df

            all_rows.extend(df.to_dict(orient="records"))

    all_df = pd.DataFrame(all_rows)
    if not all_df.empty and "review_id" in all_df.columns:
        all_df = all_df.drop_duplicates(subset=["kp_id", "review_id"], keep="first")

    with pd.ExcelWriter(args.out, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)

        all_df.to_excel(writer, sheet_name="ALL", index=False)

        if pages_log:
            pd.DataFrame(pages_log).to_excel(writer, sheet_name="PAGES_LOG", index=False)

        if empty_films:
            pd.DataFrame(empty_films).to_excel(writer, sheet_name="EMPTY_FILMS", index=False)

    print(f"OK: {args.out}")
    print(f"Films: {len(sheets)} | Total reviews: {len(all_df)}")
    if empty_films:
        print(f"Films with zero parsed reviews: {len(empty_films)} (see EMPTY_FILMS sheet)")
    print("Done.")

if __name__ == "__main__":
    main()