#!/usr/bin/env bash
set -euo pipefail

COOKIE_FILE="cookie_header.txt"
OUT_ROOT="html_dump"

UA="Mozilla/5.0"
LANG="ru,en;q=0.9"

if [[ ! -f "$COOKIE_FILE" ]]; then
  echo "ERROR: $COOKIE_FILE not found"
  exit 1
fi

# helper: curl -> file
fetch() {
  local url="$1"
  local out="$2"

  mkdir -p "$(dirname "$out")"

  echo "[GET] $url"
  curl -sS -L --compressed \
    "$url" \
    -H "User-Agent: ${UA}" \
    -H "Accept-Language: ${LANG}" \
    -b "$(cat "$COOKIE_FILE")" \
    -o "$out"

  # быстрый sanity-check: капча часто маленькая и содержит captcha-api
  if grep -qiE "captcha-api\.yandex\.ru|showcaptcha|smartcaptcha" "$out"; then
    echo "WARNING: CAPTCHA detected in saved file: $out"
  fi
}

# -----------------------------------------------------------------------------
# Формат записи:
# idx|kp_id|page|url
# page: число (1,2,3...) или пусто для одиночной страницы -> '.html'
# -----------------------------------------------------------------------------
ENTRIES=(
  # 1) Бегущий по лезвию 2049 (589290)
  "1|589290|1|https://www.kinopoisk.ru/film/589290/reviews/ord/rating/status/all/perpage/200/"
  "1|589290|2|https://www.kinopoisk.ru/film/589290/reviews/ord/rating/status/all/perpage/200/page/2/"
  "1|589290|3|https://www.kinopoisk.ru/film/589290/reviews/ord/rating/status/all/perpage/200/page/3/"

  # 2) Она (577488)
  "2|577488|1|https://www.kinopoisk.ru/film/577488/reviews/ord/rating/status/all/perpage/200/"
  "2|577488|2|https://www.kinopoisk.ru/film/577488/reviews/ord/rating/status/all/perpage/200/page/2/"

  # 3) Превосходство (687670)
  "3|687670|1|https://www.kinopoisk.ru/film/687670/reviews/ord/rating/status/all/perpage/200/"
  "3|687670|2|https://www.kinopoisk.ru/film/687670/reviews/ord/rating/status/all/perpage/200/page/2/"

  # 4) Призрак в доспехах (843789)
  "4|843789|1|https://www.kinopoisk.ru/film/843789/reviews/ord/rating/status/all/perpage/200/"
  "4|843789|2|https://www.kinopoisk.ru/film/843789/reviews/ord/rating/status/all/perpage/200/page/2/"

  # 5) Робот по имени Чаппи (591485)
  "5|591485|1|https://www.kinopoisk.ru/film/591485/reviews/ord/rating/status/all/perpage/200/"
  "5|591485|2|https://www.kinopoisk.ru/film/591485/reviews/ord/rating/status/all/perpage/200/page/2/"

  # 6) 2001: Космическая одиссея (380)
  "6|380|1|https://www.kinopoisk.ru/film/380/reviews/ord/rating/status/all/perpage/200/"
  "6|380|2|https://www.kinopoisk.ru/film/380/reviews/ord/rating/status/all/perpage/200/page/2/"

  # 7) Бегущий по лезвию (403)
  "7|403|1|https://www.kinopoisk.ru/film/403/reviews/ord/rating/status/all/perpage/200/"
  "7|403|2|https://www.kinopoisk.ru/film/403/reviews/ord/rating/status/all/perpage/200/page/2/"

  # 8) Искусственный разум (594)
  "8|594|1|https://www.kinopoisk.ru/film/594/reviews/ord/rating/status/all/perpage/200/"
  "8|594|2|https://www.kinopoisk.ru/film/594/reviews/ord/rating/status/all/perpage/200/page/2/"

  # 9) Чёрное зеркало (655800) (да, /film/.. на рецензиях)
  "9|655800||https://www.kinopoisk.ru/film/655800/reviews/ord/rating/status/all/perpage/200/"

  # 10) Мир дикого Запада (195523)
  "10|195523||https://www.kinopoisk.ru/film/195523/reviews/ord/rating/status/all/perpage/200/"

  # 11) Аэлита: Боевой ангел (88173)
  "11|88173||https://www.kinopoisk.ru/film/88173/reviews/ord/rating/status/all/perpage/200/"

  # 12) Из машины (197532)
  "12|197532||https://www.kinopoisk.ru/film/197532/reviews/ord/rating/status/all/perpage/200/"

  # 13) Я, робот (4886)
  "13|4886||https://www.kinopoisk.ru/film/4886/reviews/ord/rating/status/all/perpage/200/"

  # 14) Двухсотлетний человек (7640) perpage=100
  "14|7640||https://www.kinopoisk.ru/film/7640/reviews/ord/rating/status/all/perpage/100/"

  # 15) Теорема Зеро (696977) perpage=75
  "15|696977||https://www.kinopoisk.ru/film/696977/reviews/ord/rating/status/all/perpage/75/"

  # 16) Экзистенция (7569) perpage=75
  "16|7569||https://www.kinopoisk.ru/film/7569/reviews/ord/rating/status/all/perpage/75/"

  # 17) Страховщик (596231) perpage=75
  "17|596231||https://www.kinopoisk.ru/film/596231/reviews/ord/rating/status/all/perpage/75/"

  # 18) Трон (17463) perpage=75
  "18|17463||https://www.kinopoisk.ru/film/17463/reviews/ord/rating/status/all/perpage/75/"

  # 19) Кибердеревня (5019944) perpage=50
  "19|5019944||https://www.kinopoisk.ru/film/5019944/reviews/ord/rating/status/all/perpage/50/"

  # 20) Анна Николаевна (1322389) perpage=50
  "20|1322389||https://www.kinopoisk.ru/film/1322389/reviews/ord/rating/status/all/perpage/50/"

  # 21) Анон (979121) perpage=50
  "21|979121||https://www.kinopoisk.ru/film/979121/reviews/ord/rating/status/all/perpage/50/"

  # 22) Воспитанные волками (1231016) perpage=50
  "22|1231016||https://www.kinopoisk.ru/film/1231016/reviews/ord/rating/status/all/perpage/50/"

  # 23) Дитя робота (1067645) perpage=50
  "23|1067645||https://www.kinopoisk.ru/film/1067645/reviews/ord/rating/status/all/perpage/50/"

  # 24) Лучше, чем люди (996399) perpage=50
  "24|996399||https://www.kinopoisk.ru/film/996399/reviews/ord/rating/status/all/perpage/50/"

  # 25) Ева (493452) perpage=50
  "25|493452||https://www.kinopoisk.ru/film/493452/reviews/ord/rating/status/all/perpage/50/"

  # 26) Почти человек (733636) perpage=50
  "26|733636||https://www.kinopoisk.ru/film/733636/reviews/ord/rating/status/all/perpage/50/"

  # 27) Робот (430542) perpage=50
  "27|430542||https://www.kinopoisk.ru/film/430542/reviews/ord/rating/status/all/perpage/50/"

  # 28) Мой создатель (1055319) perpage=50
  "28|1055319||https://www.kinopoisk.ru/film/1055319/reviews/ord/rating/status/all/perpage/50/"

  # 29) Затерянные в космосе (993176) perpage=25
  "29|993176||https://www.kinopoisk.ru/film/993176/reviews/ord/rating/status/all/perpage/25/"

  # 30) Приключения Электроника (77284) perpage=25
  "30|77284||https://www.kinopoisk.ru/film/77284/reviews/ord/rating/status/all/perpage/25/"

  # 31) После Янга (1261977) perpage=25
  "31|1261977||https://www.kinopoisk.ru/film/1261977/reviews/ord/rating/status/all/perpage/25/"

  # 32) Электрический штат (5024992) perpage=25
  "32|5024992||https://www.kinopoisk.ru/film/5024992/reviews/ord/rating/status/all/perpage/25/"

  # 33) Робо (1228540) perpage=25
  "33|1228540||https://www.kinopoisk.ru/film/1228540/reviews/ord/rating/status/all/perpage/25/"

  # 34) Альфавиль (7776) perpage=25
  "34|7776||https://www.kinopoisk.ru/film/7776/reviews/ord/rating/status/all/perpage/25/"

  # 35) Компаньон (6275518) perpage=25
  "35|6275518||https://www.kinopoisk.ru/film/6275518/reviews/ord/rating/status/all/perpage/25/"

  # 36) Робот и Фрэнк (596232) perpage=25
  "36|596232||https://www.kinopoisk.ru/film/596232/reviews/ord/rating/status/all/perpage/25/"

  # 37) Люди (855925) perpage=25
  "37|855925||https://www.kinopoisk.ru/film/855925/reviews/ord/rating/status/all/perpage/25/"

  # 38) Короткое замыкание (18282) perpage=25
  "38|18282||https://www.kinopoisk.ru/film/18282/reviews/ord/rating/status/all/perpage/25/"
)

for entry in "${ENTRIES[@]}"; do
  IFS="|" read -r idx kp_id page url <<< "$entry"

  if [[ -z "$page" ]]; then
    # строго по твоей хотелке: ".html"
    out="${OUT_ROOT}/${idx}/${kp_id}/.html"
  else
    out="${OUT_ROOT}/${idx}/${kp_id}/${page}.html"
  fi

  fetch "$url" "$out"

  # мелкая пауза снижает шанс снова словить капчу
  sleep 1
done

echo "DONE. Saved to: ${OUT_ROOT}/"