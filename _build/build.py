"""«Кинезио» — пятый вариант сайта Орто-Рекавери. Статичные страницы на данных Next.js-версии.

Запуск из папки premium:  python3 _build/build.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIB = os.path.join(os.path.dirname(ROOT), 'orto-recovery-site', 'src', 'lib')
ts = lambda n: open(os.path.join(LIB, n), encoding='utf-8').read()

# ---------- данные ----------
nav_ts = ts('nav.ts'); nav_ts = nav_ts[nav_ts.index('export const SERVICES'):]
SERVICES = []
for block in re.findall(r"\{\s*slug: .*?chat: '[^']*',\s*\}", nav_ts, re.S):
    g = lambda k: re.search(k + r": '([^']*)'", block).group(1)
    SERVICES.append({
        'slug': g('slug'), 'menu': g('menu'), 'title': g('title'), 'lead': g('lead'),
        'doctors': re.findall(r"'([^']+)'", re.search(r"doctors: \[(.*?)\]", block).group(1)),
        'prices': re.findall(r"\['([^']+)', '([^']+)'\]", re.search(r"prices: \[(.*?)\],\n", block, re.S).group(1)),
        'conditions': re.findall(r"'(\w+)'", re.search(r"conditions: \[(.*?)\]", block).group(1)),
    })
CONDITIONS = {m.group(1): (m.group(2), re.findall(r"'([^']+)'", m.group(3))) for m in re.finditer(r"id: '(\w+)',\s*label: '([^']+)',\s*items: \[(.*?)\]", ts('content.ts'), re.S)}
clinic = ts('clinic.ts')
DOCTORS = []
# у части врачей между treats и price стоит photo — поля берём по отдельности внутри каждого блока
for blk in re.findall(r"\{\s*name: '[^']+',.*?chat: '[^']*',", clinic[clinic.index('export const DOCTORS'):clinic.index('export type BodyArea')], re.S):
    f = lambda k: re.search(k + r": '([^']*)'", blk).group(1)
    DOCTORS.append({'name': f('name'), 'role': f('role'), 'treats': f('treats'), 'price': f('price')})
AREAS = []
for m in re.finditer(r"id: '(\w+)',\s*label: '([^']+)',\s*complaints: '([^']+)',\s*options: \[(.*?)\],\s*doctor: '([^']+)',\s*doctorRole: '([^']+)',\s*visit: '([^']+)'", clinic, re.S):
    AREAS.append({'id': m.group(1), 'label': m.group(2), 'complaints': m.group(3), 'options': re.findall(r"name: '([^']+)', price: '([^']+)'", m.group(4)), 'doctor': m.group(5), 'role': m.group(6), 'visit': m.group(7)})
pg = clinic[clinic.index('export const PRICE_GROUPS'):clinic.index('// Экскурсия')]
PRICE_GROUPS = [(m.group(1), re.findall(r"name: '([^']+)', price: '([^']+)'", m.group(2))) for m in re.finditer(r"title: '([^']+)',\s*items: \[(.*?)\],\s*\}", pg, re.S)]
assert len(SERVICES) == 8 and len(DOCTORS) == 6 and len(AREAS) == 6 and len(PRICE_GROUPS) == 4, (len(SERVICES), len(DOCTORS), len(AREAS), len(PRICE_GROUPS))

PHOTO = {'ortopediya': 'knee', 'spina': 'back', 'reabilitaciya': 'lfk', 'fizioterapiya': 'physio', 'prp': 'lab', 'endoskopiya': 'endo', 'detyam': 'explain', 'pitanie-i-psiholog': 'consult'}
AREA_PHOTO = {'back': 'back', 'arm': 'physio', 'knee': 'knee', 'foot': 'massage', 'kids': 'lfk', 'endo': 'endo'}
DOC_PHOTO = {'Куделя Александр Павлович': 'd-kudelya-a', 'Нажмудинова Айшат Абдурахмановна': 'd-nazhmudinova', 'Мусаева Эльмира Ашурбеговна': 'd-musaeva'}
DOC_TONE = ['c', 'p', 'c', 's', 'p', 's']
# биографии — медиатека старого сайта (выгрузка WordPress, 25.10.2026)
BIO = {
    'Куделя Александр Павлович': ['Дагестанский государственный медицинский институт, лечебное дело (1979)', 'Переподготовка по эндоскопии — ГНЦ колопроктологии, Москва (1984)', 'Высшая квалификационная категория по эндоскопии (2004)', 'Повышение квалификации: РМАПО (1999, 2018), СПбМАПО (2009), ГНЦ колопроктологии (2014)'],
    'Нажмудинова Айшат Абдурахмановна': ['Первый МГМУ им. Сеченова, лечебное дело (2013)', 'Специализация по гастроэнтерологии — МГМСУ им. Евдокимова (2019)', 'Повышение квалификации по гастроэнтерологии и гепатологии — РНИМУ им. Пирогова (2023–2024)'],
    'Мусаева Эльмира Ашурбеговна': ['Лечебная гимнастика по методике SEAS (СИАС)', 'Ашхабадское медицинское училище (1994)', 'Северо-Кавказский государственный институт (2012)'],
    'Куделя Павел Александрович': ['Проводит авторские семинары по сухим иглам для специалистов'],
}
TEL, TEL_HREF, WA = '+7 (8722) 52-23-33', 'tel:+78722522333', 'https://wa.me/79883011805'
initials = lambda n: ''.join(w[0] for w in n.split()[:2])
doc_by = {d['name']: d for d in DOCTORS}

def ava(name, cls='ava'):
    if name in DOC_PHOTO:
        return '<img class="%s" src="{P}assets/%s.jpg" alt="">' % (cls, DOC_PHOTO[name])
    i = [d['name'] for d in DOCTORS].index(name)
    return '<span class="%s %s" aria-hidden="true">%s</span>' % (cls, DOC_TONE[i], initials(name))

# ---------- общие части ----------
NAV = [('', 'Главная'), ('uslugi/', 'Услуги'), ('vrachi/', 'Врачи'), ('ceny/', 'Цены'), ('o-centre/', 'О центре'), ('pacientam/', 'Пациентам'), ('kontakty/', 'Контакты')]

def header(active):
    items = []
    for h, l in NAV[1:]:
        on = ' class="on"' if h == active else ''
        if h == 'uslugi/':
            panel = ''.join('<a href="{P}uslugi/%s/">%s<span>%s</span></a>' % (s['slug'], s['menu'], s['prices'][0][1]) for s in SERVICES)
            items.append('<div class="mm"><a href="{P}uslugi/"%s>Услуги</a><div class="mm-panel">%s</div></div>' % (on, panel))
        else:
            items.append('<a href="{P}%s"%s>%s</a>' % (h, on, l))
    mob = ''.join('<a href="{P}%s">%s</a>' % (h, l) for h, l in NAV if h != 'uslugi/')
    mob_s = ''.join('<a href="{P}uslugi/%s/">%s<span>%s</span></a>' % (s['slug'], s['menu'], s['prices'][0][1]) for s in SERVICES)
    return '''<header class="top"><div class="wrap top-in">
  <a class="logo" href="{P}"><img src="{P}assets/logo-dark.png" alt="Орто-Рекавери, на главную"></a>
  <nav class="menu" aria-label="Основное меню">%s</nav>
  <div class="top-right"><a class="phone" href="%s">%s</a><a class="btn btn-blue btn-sm" href="%s">Записаться</a>
  <button class="burger" type="button" aria-expanded="false" aria-label="Открыть меню"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button></div>
</div></header>
<nav class="mnav" hidden aria-label="Меню">%s<h4>Услуги</h4><div class="sub">%s</div><p style="margin-top:28px"><a class="btn btn-blue" style="width:100%%;border:0" href="%s">Позвонить и записаться</a></p></nav>''' % (''.join(items), TEL_HREF, TEL, TEL_HREF, mob, mob_s, TEL_HREF)

def footer():
    svc = ''.join('<a href="{P}uslugi/%s/">%s</a>' % (s['slug'], s['menu']) for s in SERVICES)
    pages = ''.join('<a href="{P}%s">%s</a>' % (h, l) for h, l in NAV[2:])
    return '''<footer class="foot"><span class="tape pink stretch" aria-hidden="true"></span><div class="wrap">
  <div class="foot-cta"><h2>Начните с одного приёма</h2><div class="hero-cta" style="margin:0"><a class="btn btn-blue" href="%s">Позвонить %s</a><a class="btn btn-white" href="%s" target="_blank" rel="noreferrer">Написать в WhatsApp</a></div></div>
  <div class="foot-grid">
    <div><img src="{P}assets/logo-color.png" alt="Орто-Рекавери"><p>Махачкала, проспект Имама Шамиля, 35А, 1 этаж</p><p>Пн–Пт 9:00–18:00, Сб 9:00–16:00</p></div>
    <div><h4>Услуги</h4>%s</div>
    <div><h4>Центр</h4>%s</div>
    <div><h4>Реквизиты</h4><p>ООО ЦВМ «ОРТО-РЕКАВЕРИ»</p><p>ИНН 0572029293</p><p>ОГРН 1210500012392</p></div>
  </div>
  <p class="legal">Имеются противопоказания, необходима консультация специалиста. Цены — прайс центра на ПроДокторов от 19.10.2026. Демо-версия сайта для обсуждения с центром; фото — фотосессия центра 2024 года.</p>
</div></footer>
<nav class="dock" aria-label="Быстрая запись"><a href="%s" target="_blank" rel="noreferrer">WhatsApp</a><a href="%s">Позвонить и записаться</a></nav>''' % (TEL_HREF, TEL, WA, svc, pages, WA, TEL_HREF)

def page(P, active, title, desc, body):
    html = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>%s</title>
<meta name="description" content="%s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geologica:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{P}assets/site.css">
</head>
<body>
%s
<main>
%s
</main>
%s
%s
<script src="{P}assets/site.js"></script>
</body>
</html>
''' % (title, desc, header(active), body, footer(), dialog_data())
    return html.replace('{P}', P)

def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(html)

def dialog_data():
    # данные для окна врача: одна разметка на страницу, скрипт берёт нужную карточку
    out = []
    for d in DOCTORS:
        pic = '<img src="{P}assets/%s.jpg" alt="">' % DOC_PHOTO[d['name']] if d['name'] in DOC_PHOTO else '<span class="mono">%s</span>' % initials(d['name'])
        bio = ''.join('<li>%s</li>' % b for b in BIO.get(d['name'], []))
        out.append('<template id="doc-%s"><div class="pic">%s</div><div class="txt"><h3>%s</h3><p class="role">%s</p><p class="treats">%s</p>%s<div class="bot"><b>%s</b><a class="btn btn-blue" href="%s">Записаться к врачу</a></div></div></template>' % (
            initials(d['name']) + str(DOCTORS.index(d)), pic, d['name'], d['role'], d['treats'], '<ul>%s</ul>' % bio if bio else '', d['price'], TEL_HREF))
    return ''.join(out)

# ---------- блоки ----------
def hero():
    return '''<section class="hero"><div class="wrap hero-grid">
  <div>
    <h1><span class="ln"><span>Возвращаем</span></span><span class="ln"><span>движение</span></span><span class="ln"><span>без операции</span></span></h1>
    <p class="lead">Ортопеды, невролог и реабилитологи в Махачкале. Сначала находим причину боли, потом составляем план лечения — цену вы знаете до начала.</p>
    <div class="hero-cta"><a class="btn btn-blue" href="%s">Записаться на приём</a><a class="btn btn-line" href="#zones">Где болит?</a></div>
    <div class="hero-proof"><span><b>5,0</b>в 2ГИС, 121 оценка</span><span><b>4,9</b>на Яндекс Картах</span><span><b>23</b>методики восстановления</span></div>
  </div>
  <div class="hero-photo"><img src="{P}assets/hero.jpg" alt="Ударно-волновая терапия плеча в кабинете центра">
    <span class="tape stretch t1">Махачкала, Имама Шамиля, 35А</span><span class="tape pink stretch t2">Приём ортопеда — 3 000 ₽</span></div>
</div></section>''' % TEL_HREF

def zones():
    rows = []
    for i, a in enumerate(AREAS):
        opts = ''.join('<li><span>%s</span><b>%s</b></li>' % o for o in a['options'])
        rows.append('''<div class="zone%s"><button class="zone-btn" type="button" aria-expanded="%s"><span class="name">%s</span><span class="who">%s</span><span class="plus" aria-hidden="true"></span></button>
  <div class="zone-body"><div><div class="zone-in">
    <img src="{P}assets/%s.jpg" alt="" loading="lazy">
    <div class="zone-doc"><p class="complaint">%s</p><div class="doc-line">%s<div><b>%s</b><span>%s</span></div></div><div><a class="btn btn-blue btn-sm" href="%s">Записаться — %s</a></div></div>
    <ul>%s</ul>
  </div></div></div></div>''' % (' open' if i == 0 else '', 'true' if i == 0 else 'false', a['label'], a['role'].capitalize(), AREA_PHOTO[a['id']], a['complaints'], ava(a['doctor']), a['doctor'], a['role'], TEL_HREF, a['visit'], opts))
    return '''<section class="sec" id="zones"><div class="wrap">
  <div class="sec-head"><div><h2>Где болит?</h2><span class="tape under stretch" aria-hidden="true"></span></div><p>Выберите, что беспокоит, — покажем, кто ведёт приём, что может назначить врач и сколько это стоит.</p></div>
  <div class="zones">%s</div>
</div></section>''' % ''.join(rows)

STEPS = [('Расскажите, что беспокоит', 'Врач собирает жалобы и историю: когда началось, что усиливает боль, были ли травмы.'),
         ('Осмотр и простой тест', 'Смотрим, как двигается сустав или спина, проводим несложный физический тест.'),
         ('Разбор снимков', 'МРТ, рентген, заключения — объясняем простыми словами, что на них видно.'),
         ('План лечения с ценой', 'Курс процедур и его стоимость вы знаете до начала. Решение за вами.')]

def path(photos=True):
    li = ''.join('<li><h3>%s</h3><p>%s</p></li>' % s for s in STEPS)
    ph = '<div class="path-photo"><img src="{P}assets/mri.jpg" alt="Врачи разбирают снимок МРТ" loading="lazy"><img src="{P}assets/explain.jpg" alt="Врач объясняет диагноз на доске" loading="lazy"></div>' if photos else ''
    return '''<section class="sec dark"><div class="wrap">
  <div class="sec-head"><div><h2>Сначала причина, потом лечение</h2><span class="tape pink under stretch" aria-hidden="true"></span></div><p>Так проходит первый приём у ортопеда или невролога. Приём ортопеда длится 20–30 минут.</p></div>
  <ol class="path">%s</ol>%s
</div></section>''' % (li, ph)

def docs(title='Врачи, к которым приходят по имени', lead='Можно записаться к конкретному врачу. Если вам спокойнее со специалистом-женщиной, скажите об этом администратору.'):
    cards = []
    for i, d in enumerate(DOCTORS):
        pic = '<img src="{P}assets/%s.jpg" alt="%s" loading="lazy">' % (DOC_PHOTO[d['name']], d['name']) if d['name'] in DOC_PHOTO else '<span class="mono" aria-hidden="true">%s</span>' % initials(d['name'])
        tape = '<span class="tape%s stretch">%s</span>' % (' pink' if i % 2 else '', d['price'])
        cards.append('<button class="doc" type="button" data-doc="doc-%s%d"><span class="doc-pic">%s%s</span><span class="dname">%s</span><span class="role">%s</span><span class="more">Подробнее о враче</span></button>' % (initials(d['name']), i, pic, tape, d['name'], d['role']))
    return '''<section class="sec"><div class="wrap">
  <div class="sec-head"><div><h2>%s</h2><span class="tape under stretch" aria-hidden="true"></span></div><p>%s</p></div>
  <div class="docs">%s</div>
</div></section>''' % (title, lead, ''.join(cards))

def quote():
    return '''<section class="quote"><span class="tape stretch" aria-hidden="true"></span><div class="wrap">
  <blockquote>Для двух пациентов с одинаковым диагнозом нельзя использовать одну программу: для одного она будет слишком лёгкой, для другого — невыполнимой. <b>Поэтому план лечения мы составляем под вас.</b></blockquote>
  <cite>Принцип центра — со старого сайта «Орто-Рекавери»</cite>
</div></section>'''

def prices(groups=PRICE_GROUPS, more=False):
    g = ''.join('<div class="pgroup"><h3>%s</h3><ul>%s</ul></div>' % (t, ''.join('<li><span>%s</span><b>%s</b></li>' % it for it in items)) for t, items in groups)
    link = '<p class="price-note"><a class="btn btn-line btn-sm" href="{P}ceny/">Весь прайс</a></p>' if more else '<p class="price-note">Прайс центра на ПроДокторов от 19.10.2026. Есть рассрочка без переплат и справка для налогового вычета.</p>'
    return '''<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><div><h2>Цены</h2><span class="tape pink under stretch" aria-hidden="true"></span></div><p>Цену вы знаете до начала лечения. Курс можно оплатить частями, без переплаты.</p></div>
  <div class="prices">%s</div>%s
</div></section>''' % (g, link)

def visit():
    return '''<section class="sec" style="padding-top:0"><div class="wrap visit">
  <div><h2>Как нас найти</h2><span class="tape under stretch" aria-hidden="true"></span>
  <dl><div><dt>Адрес</dt><dd>Махачкала, проспект Имама Шамиля, 35А, 1 этаж</dd></div>
  <div><dt>Как пройти</dt><dd>Вход за шлагбаумом, рядом санаторий «Тарнаир». Остановка «Источник Тарнаир». Есть пандус и парковка.</dd></div>
  <div><dt>Часы работы</dt><dd>Пн–Пт 9:00–18:00, Сб 9:00–16:00</dd></div>
  <div><dt>Телефон и WhatsApp</dt><dd><a href="%s">%s</a>, <a href="%s" target="_blank" rel="noreferrer">+7 (988) 301-18-05</a></dd></div></dl></div>
  <div class="map"><iframe title="Орто-Рекавери на карте" loading="lazy" src="https://yandex.ru/map-widget/v1/?ll=47.498081%%2C42.965856&z=17&pt=47.498081%%2C42.965856%%2Cpm2rdm"></iframe></div>
</div></section>''' % (TEL_HREF, TEL, WA)

def phead(crumbs, title, lead):
    cr = '<nav class="crumbs" aria-label="Хлебные крошки"><a href="{P}">Главная</a>%s</nav>' % ''.join('<span><a href="{P}%s">%s</a></span>' % c if c[0] else '<span>%s</span>' % c[1] for c in crumbs)
    return '<section class="phead"><div class="wrap">%s<h1>%s</h1><p class="lead">%s</p></div></section>' % (cr, title, lead)

# ---------- страницы ----------
def build():
    open(os.path.join(ROOT, 'assets', 'site.css'), 'w', encoding='utf-8').write(open(os.path.join(HERE, 'site.css'), encoding='utf-8').read())
    open(os.path.join(ROOT, 'assets', 'site.js'), 'w', encoding='utf-8').write(open(os.path.join(HERE, 'site.js'), encoding='utf-8').read())

    write('index.html', page('', '', 'Орто-Рекавери — возвращаем движение без операции', 'Ортопеды, невролог и реабилитологи в Махачкале: лечение боли в спине и суставах без операции, реабилитация, ЛФК, физиотерапия, PRP, эндоскопия во сне.',
                             hero() + zones() + path() + docs() + quote() + prices(PRICE_GROUPS[:2], more=True) + visit()))

    rows = ''.join('<a class="svc-row" href="{P}uslugi/%s/"><span class="t">%s</span><span class="k">%s</span><span class="p">от %s</span></a>' % (s['slug'], s['menu'], s['doctors'][0], s['prices'][0][1].replace('от ', '')) for s in SERVICES)
    write('uslugi/index.html', page('../', 'uslugi/', 'Услуги — Орто-Рекавери', 'Восемь направлений в одном центре.',
                                    phead([('', 'Услуги')], 'Восемь направлений в одном центре', 'От консультации ортопеда до обследования во сне. Выберите направление — на странице цены, врачи и с чем к нам приходят.') +
                                    '<section class="sec"><div class="wrap"><div class="svc-list">%s</div></div></section>' % rows + quote()))

    for s in SERVICES:
        P = '../../'
        conds = [c for k in s['conditions'] for c in CONDITIONS[k][1]]
        cond_html = '<div><h2>С чем к нам приходят</h2><ul class="conds">%s</ul></div>' % ''.join('<li>%s</li>' % c for c in conds) if conds else '<div><h2>Что входит</h2><ul class="conds">%s</ul></div>' % ''.join('<li>%s</li>' % p[0] for p in s['prices'])
        side = ''.join('<button class="item doc" type="button" data-doc="doc-%s%d" style="width:100%%;text-align:left;border:0">%s<span><b>%s</b><span>%s</span></span></button>' % (initials(n), [d['name'] for d in DOCTORS].index(n), ava(n), n, doc_by[n]['role']) for n in s['doctors'] if n in doc_by)
        pr = ''.join('<li><span>%s</span><b>%s</b></li>' % p for p in s['prices'])
        others = ''.join('<a href="{P}uslugi/%s/">%s</a>' % (o['slug'], o['menu']) for o in SERVICES if o['slug'] != s['slug'])
        body = '''<section class="phead"><div class="wrap svc-hero"><div>
  <nav class="crumbs" aria-label="Хлебные крошки"><a href="{P}">Главная</a><span><a href="{P}uslugi/">Услуги</a></span><span>%s</span></nav>
  <h1>%s</h1><p class="lead">%s</p>
  <div class="hero-cta"><a class="btn btn-blue" href="%s">Записаться</a><span class="tape pink stretch" style="align-self:center">%s — %s</span></div>
</div><img src="{P}assets/%s.jpg" alt=""></div></section>
<section class="sec"><div class="wrap svc-cols">%s<div class="side-doc"><div class="pgroup"><h3>Цены</h3><ul>%s</ul></div><h3 style="margin-top:24px">%s</h3>%s</div></div></section>''' % (
            s['menu'], s['title'], s['lead'], TEL_HREF, s['prices'][0][0], s['prices'][0][1], PHOTO[s['slug']], cond_html, pr, 'Ведут приём' if len(s['doctors']) > 1 else 'Ведёт приём', side)
        body += path(photos=False) + '<section class="sec"><div class="wrap"><h2 style="font-size:clamp(28px,3vw,40px);margin-bottom:24px">Другие направления</h2><div class="others">%s</div></div></section>' % others
        write('uslugi/%s/index.html' % s['slug'], page(P, 'uslugi/', '%s — Орто-Рекавери, Махачкала' % s['menu'], s['lead'], body))

    P = '../'
    write('vrachi/index.html', page(P, 'vrachi/', 'Врачи — Орто-Рекавери', 'Врачи центра «Орто-Рекавери».',
                                    phead([('', 'Врачи')], 'Врачи центра', 'Ортопед, невролог, эндоскопист, гастроэнтеролог и инструкторы ЛФК. Нажмите на врача — расскажем об образовании и опыте.') +
                                    docs('Шесть специалистов', 'Павел Куделя проводит в центре авторские семинары по сухим иглам для других врачей, здесь же проходил семинар KinesioCourse по кинезиотейпированию.')))
    write('ceny/index.html', page(P, 'ceny/', 'Цены — Орто-Рекавери', 'Прайс центра.',
                                  phead([('', 'Цены')], 'Цены центра', 'Прайс на ПроДокторов от 19.10.2026. Курс можно оплатить частями без переплаты, справку для налогового вычета выдаём по запросу.') + '<div style="height:96px"></div>' + prices()))
    facts = [('Доказательная медицина', 'Применяем методы, доказавшие свою эффективность и безопасность.'), ('Лицензия Минздрава', 'Зарегистрированное медицинское учреждение с необходимыми лицензиями.'), ('Без операций', 'Только безоперационные методы восстановления.'),
             ('Консилиум врачей', 'В сложных случаях вас посмотрят несколько специалистов центра.'), ('Пандус и парковка', 'Первый этаж, вход без ступенек, парковка у входа.'), ('Чай и кофе, пока ждёте', 'Бесплатно — чтобы визит был спокойнее.')]
    gal = [('reception', 'Ресепшен'), ('ortho', 'Кабинет ортопеда'), ('physio', 'Аппаратная физиотерапия'), ('massage', 'Массаж'), ('lfk', 'Зал ЛФК'), ('endo', 'Эндоскопия')]
    write('o-centre/index.html', page(P, 'o-centre/', 'О центре — Орто-Рекавери', 'О центре.',
                                      phead([('', 'О центре')], 'Центр восстановительной медицины', 'Лечим и восстанавливаем пациентов с заболеваниями и травмами опорно-двигательной системы — без операций. Основатель проекта — Абдулла-Гаджи Магомеддов, генеральный директор — Артур Хумаров.') +
                                      '<section class="sec"><div class="wrap"><div class="sec-head"><div><h2>Почему нам доверяют</h2><span class="tape under stretch" aria-hidden="true"></span></div><p>Принципы центра — со старого сайта, без громких обещаний.</p></div><div class="facts">%s</div></div></section>' % ''.join('<div><b>%s</b><p>%s</p></div>' % f for f in facts) +
                                      '<section class="sec" style="padding-top:0"><div class="wrap"><div class="sec-head"><div><h2>Как выглядит центр</h2><span class="tape pink under stretch" aria-hidden="true"></span></div><p>Фотосессия центра 2024 года.</p></div><div class="gallery">%s</div></div></section>' % ''.join('<figure><img src="{P}assets/%s.jpg" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>' % (f, c, c) for f, c in gal) + quote()))
    prep = [('Снимки и заключения', 'МРТ, рентген, выписки — всё, что есть по вашей проблеме'), ('Список жалоб', 'когда началось, что усиливает боль, что помогает'), ('Спортивная одежда и сменная обувь', 'если записаны на ЛФК'), ('Перед PRP спросите врача о лекарствах', 'препараты, влияющие на свёртываемость, отменяют заранее — только по согласованию'), ('Около 30 минут', 'столько длится приём ортопеда'), ('Реабилитолог на дом — 4 000 ₽', 'если после операции или травмы тяжело выходить из дома')]
    write('pacientam/index.html', page(P, 'pacientam/', 'Пациентам — Орто-Рекавери', 'Как подготовиться к визиту.',
                                       phead([('', 'Пациентам')], 'Перед первым визитом', 'Что взять с собой, как проходит приём и что делать, если вам предложили операцию.') +
                                       '<section class="sec"><div class="wrap"><div class="sec-head"><div><h2>Что взять с собой</h2><span class="tape under stretch" aria-hidden="true"></span></div><p>Ничего сложного — но с этим приём пройдёт быстрее и точнее.</p></div><ul class="prep">%s</ul></div></section>' % ''.join('<li><b>%s</b><span>%s</span></li>' % p for p in prep) +
                                       path() + '<section class="sec"><div class="wrap svc-hero"><div><h2>Вам предложили операцию?</h2><span class="tape pink under stretch" aria-hidden="true"></span><p class="lead" style="margin-top:24px">Бывает, что от операции можно отказаться — если вовремя начать физиотерапию и ЛФК. Ортопед посмотрит снимки и честно скажет, есть ли смысл пробовать без операции. Если операция нужна — так и скажем.</p><div class="hero-cta"><a class="btn btn-blue" href="%s">Записаться на консультацию — 3 000 ₽</a></div></div><img src="{P}assets/ortho.jpg" alt="Ортопед центра" loading="lazy"></div></section>' % TEL_HREF))
    write('kontakty/index.html', page(P, 'kontakty/', 'Контакты — Орто-Рекавери', 'Адрес, телефон, часы работы.',
                                      phead([('', 'Контакты')], 'Контакты', 'Махачкала, проспект Имама Шамиля, 35А, 1 этаж. Звоните или пишите в WhatsApp — запишем к нужному врачу.') + '<div style="height:96px"></div>' + visit()))
    print('ok: 15 pages')

build()
