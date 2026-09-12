#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO / AEO / GEO 基礎工程 — 一次把整站的 meta、og、JSON-LD、sitemap、robots 產好。

用法：
    python3 seo.py            # 寫入
    python3 seo.py --check    # 只看會改什麼，不寫檔

★ 買到自訂網域後，只要改下面 SITE_URL 這一行，再跑一次就好。
"""

import re
import sys
import os
import json
import datetime

# ─────────────────────────────────────────────────────────────
# ★★★ 買到網域後改這裡（結尾不要斜線）★★★
SITE_URL = "https://nina-about-me.vercel.app"
# ─────────────────────────────────────────────────────────────

HERE = os.path.dirname(os.path.abspath(__file__))
BEGIN = "<!-- SEO:BEGIN 由 seo.py 產生，請勿手改；要改請改 seo.py 再重跑 -->"
END = "<!-- SEO:END -->"

SITE_NAME = "Nina 雙胞胎媽咪"
DEFAULT_OG = "img/og-default.jpg"

# ── 實體一致性：這段文字要跟 IG bio、Threads bio、文章署名用同一套說法 ──
PERSON = {
    "@type": "Person",
    "@id": SITE_URL + "/#nina",
    "name": "Nina",
    "alternateName": ["1minaday.nina", "Nina 雙胞胎媽咪"],
    "description": (
        "Nina，台灣雙胞胎媽媽，極早產雙胞胎（出生 898g / 890g）的媽媽，"
        "在 IG @1minaday.nina 分享雙胞胎育兒、早產兒照護與真實家庭日常。"
    ),
    "jobTitle": "自媒體創作者",
    "knowsAbout": [
        "雙胞胎育兒", "早產兒照護", "矯正年齡", "早期療育",
        "試管嬰兒", "親子出遊", "懶人料理",
    ],
    "nationality": {"@type": "Country", "name": "台灣"},
    "url": SITE_URL + "/",
    "image": SITE_URL + "/img/avatar.jpg",
    "sameAs": [
        "https://www.instagram.com/1minaday.nina/",
        "https://www.threads.net/@1minaday.nina",
    ],
}

WEBSITE = {
    "@type": "WebSite",
    "@id": SITE_URL + "/#website",
    "url": SITE_URL + "/",
    "name": SITE_NAME,
    "inLanguage": "zh-TW",
    "publisher": {"@id": PERSON["@id"]},
}

# ── 每一頁的設定 ──
#   desc      : 150–160 字內的摘要，AI 常直接拿這句當答案
#   schema    : person / article / recipe / webpage
#   noindex   : True = 不進 Google、也不進 sitemap
PAGES = {
    "index.html": {
        "desc": "Nina，台灣雙胞胎媽媽，極早產雙寶 898g／890g 的媽媽。這裡有團購檔期、私心愛用好物、媽咪私房菜食譜，和那些把苦日子過成段子的真實故事。",
        "schema": "person",
        "priority": "1.0",
        "changefreq": "weekly",
    },
    # 2026-09-13 暫時 noindex：頁內受眾數據是示意佔位數字，不是真的。
    # 首頁的「合作資料」按鈕也一併註解隱藏了。數據更新後刪掉 noindex 那行、
    # 並把 index.html footer 的註解拿掉即可恢復。
    "media-kit.html": {
        "desc": "Nina（@1minaday.nina）的合作資料：受眾輪廓、合作形式、內容原則與洽詢方式。以 25–44 歲媽媽族群為核心受眾，主打雙胞胎育兒與早產兒照護的真實內容。",
        "schema": "person",
        "noindex": True,
        "priority": "0.8",
        "changefreq": "monthly",
    },
    # ── 文章 ──
    "article-milk-bank.html": {
        "desc": "母乳可以捐嗎？台灣有四間母乳庫，北中南東各一間。捐贈流程、要不要抽血、一定要親送嗎、運費誰出、為什麼只收產後六個月內的母乳，一次整理。作者是母乳庫的受惠者家屬。",
        "schema": "article",
        "section": "早產與 NICU",
        "date": "2026-09-13",
        "priority": "0.9",
        "changefreq": "monthly",
    },
    "article-corrected-age.html": {
        "desc": "矯正年齡＝實際年齡減掉早出生的那段時間，一般算到矯正年齡滿兩歲。27 週早產雙胞胎媽媽的實際算法、什麼時候可以不用再算，以及為什麼每次都標兩個數字。",
        "schema": "article",
        "section": "早產與療育",
        "date": "2026-09-13",
        "priority": "0.9",
        "changefreq": "monthly",
    },
    "article-shared-reading.html": {
        "desc": "親子共讀不是把字唸完就好。固定角色建立預測感、語調誇張加手勢、把書裡的動作做一次、平行說話、問完停下來等——聽語治療師教的五個技巧，一般孩子也適用。",
        "schema": "article",
        "section": "語言發展",
        "date": "2026-09-13",
        "priority": "0.9",
        "changefreq": "monthly",
    },

    # ── 食譜 ──
    "recipe-beef-noodle.html": {
        "desc": "用高壓鍋 35 分鐘煮出軟嫩紅燒牛肉麵，材料、步驟一頁看完。調味只用一瓶冰糖紅滷，不用滷包、不用豆瓣醬，湯頭靠番茄和蔬菜自然回甜。",
        "schema": "recipe",
        "priority": "0.7",
        "changefreq": "yearly",
    },
    "recipe-garlic-lazy-week.html": {
        "desc": "一罐蒜醬、一瓶醬油、一包海藻，七天七道晚餐再加碼兩道，每道動手不超過 10 分鐘。給聰明但懶惰的爸媽。",
        "schema": "article",
        "priority": "0.7",
        "changefreq": "yearly",
    },
    "huilai.html": {
        "desc": "會來尖石溫泉渡假村完整費用與規則整理：露營車、大眾池、湯屋、套房價格，未滿 110 公分孩童免費。帶小小孩出發前對一次就好。",
        "schema": "article",
        "priority": "0.6",
        "changefreq": "monthly",
    },
    # 樹洞：原始檔本來就設 noindex，是刻意不讓它進搜尋的，維持原樣。
    # 要開放被搜尋／被 AI 引用，把 noindex 那行刪掉再重跑就好。
    "shudong.html": {
        "desc": "樹洞：匿名寫下你現在最難的那件事，會收到一封 Nina 寫給你的信。不留名字、不存 IP，不會叫你加油。",
        "schema": "webpage",
        "noindex": True,
        "priority": "0.6",
        "changefreq": "monthly",
    },
    # 過期團購頁：價格與檔期已失效，不要讓 AI 拿舊價格回答
    "showerhead-colors.html": {
        "desc": "蓮蓬頭選色試搭小工具：上傳浴室照片，拖曳蓮蓬頭比對顏色。",
        "schema": "webpage",
        "noindex": True,
    },
    # 後台
    "admin.html": {
        "desc": "Nina 管理後台。",
        "schema": "webpage",
        "noindex": True,
        "nofollow": True,
    },
}


def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", s).strip()


def extract_recipe(html, page, url, desc):
    """從食譜頁 HTML 直接抓食材與步驟，維持跟頁面同步。"""
    name = re.search(r'<h1[^>]*class="signboard"[^>]*>(.*?)</h1>', html, re.S)
    name = strip_tags(name.group(1)) if name else SITE_NAME

    ingredients = [strip_tags(m) for m in re.findall(r'<span class="txt">(.*?)</span>', html, re.S)]
    ingredients = [i for i in ingredients if i]

    # 步驟：整段 step-body 的敘述都收進來。
    # 有「電子壓力鍋／瓦斯爐快鍋」這種分頁切換的步驟，要把分頁標籤和對應內容配成對，
    # 否則只抓到第一句「你用的是哪一種鍋？」，AI 引用時就會變成殘缺的步驟。
    body = html[html.find("</head>"):]
    chunks = body.split('<div class="step">')[1:]
    steps = []
    for blk in chunks:
        for stop in ('<p class="note"', "<footer"):
            if stop in blk:
                blk = blk[:blk.index(stop)]
        h3 = re.search(r"<h3[^>]*>(.*?)</h3>", blk, re.S)
        name = strip_tags(h3.group(1)) if h3 else ""
        head_part = blk[:h3.end()] if h3 else ""
        rest_part = blk[h3.end():] if h3 else blk

        # 分頁：用 aria-controls 把按鈕文字接到對應 panel 的內容前面
        tabs = dict(re.findall(r'aria-controls="([^"]+)"[^>]*>(.*?)</button>', rest_part, re.S))
        panels = dict(re.findall(r'<div class="panel" id="([^"]+)"[^>]*>(.*?)</div>', rest_part, re.S))

        parts = []
        if tabs and panels:
            intro = re.search(r"<p[^>]*>(.*?)</p>", rest_part, re.S)
            if intro:
                parts.append(strip_tags(intro.group(1)))
            for pid, label in tabs.items():
                if pid in panels:
                    parts.append("%s：%s" % (strip_tags(label), strip_tags(panels[pid])))
            for extra in re.findall(r'<p class="warn"[^>]*>(.*?)</p>', rest_part, re.S):
                parts.append(strip_tags(extra))
            for extra in re.findall(r'<div class="tip">(.*?)</div>', rest_part, re.S):
                parts.append(strip_tags(extra))
        else:
            for ptxt in re.findall(r"<p[^>]*>(.*?)</p>", rest_part, re.S):
                t = strip_tags(ptxt)
                if t:
                    parts.append(t)
            for extra in re.findall(r'<div class="tip">(.*?)</div>', rest_part, re.S):
                parts.append(strip_tags(extra))

        text = " ".join(x for x in parts if x)
        if text:
            steps.append({"@type": "HowToStep", "name": name, "text": text})

    if not ingredients or not steps:
        return None  # 抓不到就退回 Article，不要產出空殼 schema

    facts = re.findall(r"<div><b>(.*?)</b><span>(.*?)</span></div>", html, re.S)
    yield_ = None
    cook_min = None
    for val, label in facts:
        val, label = strip_tags(val), strip_tags(label)
        if "人份" in label:
            yield_ = val + " 人份"
        if "分鐘" in label and val.isdigit():
            cook_min = int(val)

    node = {
        "@type": "Recipe",
        "@id": url + "#recipe",
        "name": name,
        "description": desc,
        "image": [SITE_URL + "/" + DEFAULT_OG],
        "author": {"@id": PERSON["@id"]},
        "inLanguage": "zh-TW",
        "recipeCuisine": "台灣",
        "recipeCategory": "主菜",
        "recipeIngredient": ingredients,
        "recipeInstructions": steps,
    }
    if yield_:
        node["recipeYield"] = yield_
    if cook_min:
        node["cookTime"] = "PT%dM" % cook_min
        node["totalTime"] = "PT%dM" % (cook_min + 15)
    return node


def extract_faq(html, url):
    """從文章頁的 .faq 區塊抓問答，產生 FAQPage。AI 最愛引用的就是這一段。"""
    body = html[html.find("</head>"):]
    qas = []
    for blk in re.findall(r'<div class="qa">(.*?)</div>', body, re.S):
        q = re.search(r'<p class="q">(.*?)</p>', blk, re.S)
        a = re.search(r'<p class="a">(.*?)</p>', blk, re.S)
        if q and a:
            qas.append({
                "@type": "Question",
                "name": strip_tags(q.group(1)),
                "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a.group(1))},
            })
    if not qas:
        return None
    return {"@type": "FAQPage", "@id": url + "#faq", "inLanguage": "zh-TW", "mainEntity": qas}


def build_jsonld(page, cfg, html, title, url, desc):
    graph = [dict(WEBSITE), dict(PERSON)]
    kind = cfg.get("schema", "webpage")

    if kind == "person":
        graph.append({
            "@type": "ProfilePage",
            "@id": url + "#page",
            "url": url,
            "name": title,
            "description": desc,
            "inLanguage": "zh-TW",
            "isPartOf": {"@id": WEBSITE["@id"]},
            "mainEntity": {"@id": PERSON["@id"]},
            "about": {"@id": PERSON["@id"]},
        })
    elif kind == "recipe":
        node = extract_recipe(html, page, url, desc)
        if node:
            graph.append(node)
            graph.append({
                "@type": "WebPage", "@id": url + "#page", "url": url, "name": title,
                "description": desc, "inLanguage": "zh-TW",
                "isPartOf": {"@id": WEBSITE["@id"]}, "about": {"@id": PERSON["@id"]},
            })
        else:
            kind = "article"
    if kind == "article":
        node = {
            "@type": "Article",
            "@id": url + "#page",
            "url": url,
            "headline": title,
            "description": desc,
            "inLanguage": "zh-TW",
            "author": {"@id": PERSON["@id"]},
            "publisher": {"@id": PERSON["@id"]},
            "isPartOf": {"@id": WEBSITE["@id"]},
            "image": SITE_URL + "/" + DEFAULT_OG,
        }
        if cfg.get("date"):
            node["datePublished"] = cfg["date"]
            node["dateModified"] = cfg.get("modified", cfg["date"])
        if cfg.get("section"):
            node["articleSection"] = cfg["section"]
        graph.append(node)
    elif kind == "webpage":
        graph.append({
            "@type": "WebPage", "@id": url + "#page", "url": url, "name": title,
            "description": desc, "inLanguage": "zh-TW",
            "isPartOf": {"@id": WEBSITE["@id"]}, "about": {"@id": PERSON["@id"]},
        })

    faq = extract_faq(html, url)
    if faq:
        graph.append(faq)

    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=2)


def build_block(page, cfg, html, title):
    url = SITE_URL + "/" + ("" if page == "index.html" else page)
    desc = cfg["desc"]
    og_img = SITE_URL + "/" + DEFAULT_OG
    lines = [BEGIN]

    if cfg.get("noindex"):
        # 內容頁只下 noindex（維持原檔寫法）；後台才連 nofollow 一起下
        rule = "noindex, nofollow" if cfg.get("nofollow") else "noindex"
        lines.append('  <meta name="robots" content="%s">' % rule)
        lines.append('  <meta name="description" content="%s">' % desc)
        lines.append(END)
        return "\n".join(lines)

    lines += [
        '  <meta name="description" content="%s">' % desc,
        '  <link rel="canonical" href="%s">' % url,
        '  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">',
        '  <meta name="author" content="Nina">',
        '',
        '  <meta property="og:type" content="%s">' % ("profile" if cfg.get("schema") == "person" else "article"),
        '  <meta property="og:site_name" content="%s">' % SITE_NAME,
        '  <meta property="og:locale" content="zh_TW">',
        '  <meta property="og:url" content="%s">' % url,
        '  <meta property="og:title" content="%s">' % title,
        '  <meta property="og:description" content="%s">' % desc,
        '  <meta property="og:image" content="%s">' % og_img,
        '  <meta property="og:image:width" content="1200">',
        '  <meta property="og:image:height" content="630">',
        '',
        '  <meta name="twitter:card" content="summary_large_image">',
        '  <meta name="twitter:title" content="%s">' % title,
        '  <meta name="twitter:description" content="%s">' % desc,
        '  <meta name="twitter:image" content="%s">' % og_img,
        '',
        '  <script type="application/ld+json">',
        build_jsonld(page, cfg, html, title, url, desc),
        '  </script>',
        END,
    ]
    return "\n".join(lines)


def process(page, cfg, write=True):
    path = os.path.join(HERE, page)
    if not os.path.exists(path):
        return "略過（找不到檔案）"
    html = open(path, encoding="utf-8").read()
    orig = html

    # 1) 拿掉上一次產生的區塊（可重跑）
    html = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", html, flags=re.S)

    # 2) 拿掉散落在外、手寫的 description / canonical / og / twitter，避免重複
    head_end = html.find("</head>")
    head, rest = html[:head_end], html[head_end:]
    head = re.sub(r'[ \t]*<meta\s+name="description"[^>]*>\n?', "", head)
    head = re.sub(r'[ \t]*<meta\s+name="robots"[^>]*>\n?', "", head)
    head = re.sub(r'[ \t]*<meta\s+(?:name|property)="(?:og|twitter):[^"]*"[^>]*>\n?', "", head)
    head = re.sub(r'[ \t]*<link\s+rel="canonical"[^>]*>\n?', "", head)

    title = re.search(r"<title>(.*?)</title>", head, re.S)
    title = strip_tags(title.group(1)) if title else SITE_NAME

    block = build_block(page, cfg, html, title)
    html = head.rstrip() + "\n\n" + block + "\n" + rest

    if html == orig:
        return "無變化"
    if write:
        open(path, "w", encoding="utf-8").write(html)
    kind = "noindex" if cfg.get("noindex") else cfg.get("schema")
    return "已寫入（%s）" % kind


def write_sitemap(write=True):
    today = datetime.date.today().isoformat()
    rows = []
    for page, cfg in PAGES.items():
        if cfg.get("noindex"):
            continue
        loc = SITE_URL + "/" + ("" if page == "index.html" else page)
        rows.append(
            "  <url>\n"
            "    <loc>%s</loc>\n"
            "    <lastmod>%s</lastmod>\n"
            "    <changefreq>%s</changefreq>\n"
            "    <priority>%s</priority>\n"
            "  </url>" % (loc, today, cfg.get("changefreq", "monthly"), cfg.get("priority", "0.5"))
        )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    if write:
        open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8").write(xml)
    return len(rows)


AI_BOTS = [
    ("GPTBot", "ChatGPT 訓練"), ("OAI-SearchBot", "ChatGPT 搜尋"), ("ChatGPT-User", "ChatGPT 即時瀏覽"),
    ("ClaudeBot", "Claude"), ("Claude-User", "Claude 即時瀏覽"), ("Claude-SearchBot", "Claude 搜尋"),
    ("PerplexityBot", "Perplexity"), ("Perplexity-User", "Perplexity 即時瀏覽"),
    ("Google-Extended", "Google AI Overview / Gemini"), ("Applebot-Extended", "Apple Intelligence"),
    ("Bingbot", "Bing / Copilot"), ("meta-externalagent", "Meta AI"), ("Amazonbot", "Amazon"),
]


def write_robots(write=True):
    out = ["# robots.txt — 目標是「歡迎 AI 來抓」，所以全部放行。",
           "# 不想被引用的頁面用 <meta name=\"robots\" content=\"noindex\"> 擋，不要在這裡 Disallow，",
           "# 否則爬蟲讀不到 noindex，反而可能留下沒有內容的搜尋結果。",
           "", "User-agent: *", "Allow: /", ""]
    out.append("# 以下明確列出各家 AI 爬蟲，表明允許被引用（預設本來就是允許，這裡是寫清楚）")
    for bot, note in AI_BOTS:
        out += ["User-agent: %s  # %s" % (bot, note), "Allow: /", ""]
    out.append("Sitemap: %s/sitemap.xml" % SITE_URL)
    txt = "\n".join(out) + "\n"
    if write:
        open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8").write(txt)
    return txt


def main():
    write = "--check" not in sys.argv
    print("網域：%s%s\n" % (SITE_URL, "" if write else "　（--check 模式，不寫檔）"))
    for page, cfg in PAGES.items():
        print("  %-32s %s" % (page, process(page, cfg, write)))
    n = write_sitemap(write)
    write_robots(write)
    print("\n  sitemap.xml                      %d 個網址" % n)
    print("  robots.txt                       已放行 %d 家 AI 爬蟲" % len(AI_BOTS))
    if "vercel.app" in SITE_URL:
        print("\n⚠️  目前還掛在 vercel.app 子網域，權重算給 Vercel。")
        print("   買到網域後改 seo.py 第 15 行的 SITE_URL，再跑一次 python3 seo.py 就好。")


if __name__ == "__main__":
    main()
