# 1) Бегущий по лезвию 2049 (589290)
mkdir -p "html_dump/1/589290"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/589290/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/1/589290/1.html"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/589290/reviews/ord/rating/status/all/perpage/200/page/2/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/1/589290/2.html"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/589290/reviews/ord/rating/status/all/perpage/200/page/3/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/1/589290/3.html"

# 2) Она (577488)
mkdir -p "html_dump/2/577488"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/577488/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/2/577488/1.html"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/577488/reviews/ord/rating/status/all/perpage/200/page/2/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/2/577488/2.html"

# 3) Превосходство (687670)
mkdir -p "html_dump/3/687670"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/687670/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/3/687670/1.html"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/687670/reviews/ord/rating/status/all/perpage/200/page/2/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/3/687670/2.html"

# 4) Призрак в доспехах (843789)
mkdir -p "html_dump/4/843789"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/843789/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/4/843789/1.html"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/843789/reviews/ord/rating/status/all/perpage/200/page/2/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/4/843789/2.html"

# 5) Робот по имени Чаппи (591485)
mkdir -p "html_dump/5/591485"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/591485/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/5/591485/1.html"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/591485/reviews/ord/rating/status/all/perpage/200/page/2/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/5/591485/2.html"

# 6) 2001: Космическая одиссея (380)
mkdir -p "html_dump/6/380"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/380/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/6/380/1.html"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/380/reviews/ord/rating/status/all/perpage/200/page/2/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/6/380/2.html"

# 7) Бегущий по лезвию (403)
mkdir -p "html_dump/7/403"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/403/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/7/403/1.html"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/403/reviews/ord/rating/status/all/perpage/200/page/2/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/7/403/2.html"

# 8) Искусственный разум (594)
mkdir -p "html_dump/8/594"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/594/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/8/594/1.html"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/594/reviews/ord/rating/status/all/perpage/200/page/2/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/8/594/2.html"

# 9) Чёрное зеркало (655800) (одна страница)
mkdir -p "html_dump/9/655800"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/655800/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/9/655800/.html"

# 10) Мир дикого Запада (195523)
mkdir -p "html_dump/10/195523"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/195523/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/10/195523/.html"

# 11) Аэлита: Боевой ангел (88173)
mkdir -p "html_dump/11/88173"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/88173/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/11/88173/.html"

# 12) Из машины (197532)
mkdir -p "html_dump/12/197532"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/197532/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/12/197532/.html"

# 13) Я, робот (4886)
mkdir -p "html_dump/13/4886"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/4886/reviews/ord/rating/status/all/perpage/200/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/13/4886/.html"

# 14) Двухсотлетний человек (7640) perpage=100
mkdir -p "html_dump/14/7640"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/7640/reviews/ord/rating/status/all/perpage/100/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/14/7640/.html"

# 15) Теорема Зеро (696977) perpage=75
mkdir -p "html_dump/15/696977"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/696977/reviews/ord/rating/status/all/perpage/75/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/15/696977/.html"

# 16) eXistenZ (7569) perpage=75
mkdir -p "html_dump/16/7569"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/7569/reviews/ord/rating/status/all/perpage/75/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/16/7569/.html"

# 17) Страховщик (596231) perpage=75
mkdir -p "html_dump/17/596231"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/596231/reviews/ord/rating/status/all/perpage/75/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/17/596231/.html"

# 18) Трон (17463) perpage=75
mkdir -p "html_dump/18/17463"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/17463/reviews/ord/rating/status/all/perpage/75/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/18/17463/.html"

# 19) Кибердеревня (5019944) perpage=50
mkdir -p "html_dump/19/5019944"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/5019944/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/19/5019944/.html"

# 20) Анна Николаевна (1322389) perpage=50
mkdir -p "html_dump/20/1322389"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/1322389/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/20/1322389/.html"

# 21) Анон (979121) perpage=50
mkdir -p "html_dump/21/979121"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/979121/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/21/979121/.html"

# 22) Воспитанные волками (1231016) perpage=50
mkdir -p "html_dump/22/1231016"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/1231016/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/22/1231016/.html"

# 23) Дитя робота (1067645) perpage=50
mkdir -p "html_dump/23/1067645"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/1067645/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/23/1067645/.html"

# 24) Лучше, чем люди (996399) perpage=50
mkdir -p "html_dump/24/996399"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/996399/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/24/996399/.html"

# 25) Ева (493452) perpage=50
mkdir -p "html_dump/25/493452"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/493452/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/25/493452/.html"

# 26) Почти человек (733636) perpage=50
mkdir -p "html_dump/26/733636"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/733636/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/26/733636/.html"

# 27) Робот (430542) perpage=50
mkdir -p "html_dump/27/430542"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/430542/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/27/430542/.html"

# 28) Мой создатель (1055319) perpage=50
mkdir -p "html_dump/28/1055319"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/1055319/reviews/ord/rating/status/all/perpage/50/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/28/1055319/.html"

# 29) Затерянные в космосе (993176) perpage=25
mkdir -p "html_dump/29/993176"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/993176/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/29/993176/.html"

# 30) Приключения Электроника (77284) perpage=25
mkdir -p "html_dump/30/77284"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/77284/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/30/77284/.html"

# 31) После Янга (1261977) perpage=25
mkdir -p "html_dump/31/1261977"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/1261977/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/31/1261977/.html"

# 32) Электрический штат (5024992) perpage=25
mkdir -p "html_dump/32/5024992"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/5024992/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/32/5024992/.html"

# 33) Робо (1228540) perpage=25
mkdir -p "html_dump/33/1228540"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/1228540/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/33/1228540/.html"

# 34) Альфавиль (7776) perpage=25
mkdir -p "html_dump/34/7776"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/7776/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/34/7776/.html"

# 35) Компаньон (6275518) perpage=25
mkdir -p "html_dump/35/6275518"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/6275518/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/35/6275518/.html"

# 36) Робот и Фрэнк (596232) perpage=25
mkdir -p "html_dump/36/596232"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/596232/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/36/596232/.html"

# 37) Люди (855925) perpage=25
mkdir -p "html_dump/37/855925"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/855925/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/37/855925/.html"

# 38) Короткое замыкание (18282) perpage=25
mkdir -p "html_dump/38/18282"
curl -sS -L --compressed 'https://www.kinopoisk.ru/film/18282/reviews/ord/rating/status/all/perpage/25/' \
  -H 'User-Agent: Mozilla/5.0' -H 'Accept-Language: ru,en;q=0.9' -b "$(cat cookie_header.txt)" \
  -o "html_dump/38/18282/.html"