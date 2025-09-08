import os
import re
from datetime import datetime

BASE_CSS = """
:root{--bg:#0b0f14;--fg:#d7e3f4;--muted:#8aa4bf;--accent:#5aa9ff;}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,Arial}
a{color:var(--accent);text-decoration:none} a:hover{text-decoration:underline}
header{padding:28px 16px;border-bottom:1px solid #1b2838;background:#0e131a}
.container{max-width:980px;margin:0 auto;padding:20px 16px}
.badge{display:inline-block;padding:2px 8px;border:1px solid #1c2a3a;border-radius:12px;color:var(--muted);font-size:12px;margin-right:8px}
.card{background:#0e141b;border:1px solid #142132;border-radius:12px;padding:16px;margin:12px 0;transition:.2s}
.card:hover{border-color:#1e3350}
h1{font-size:20px;margin:0 0 8px} h2{font-size:16px;margin:0 0 6px}
.meta{color:var(--muted);font-size:12px;margin-bottom:8px}
.footer{color:#6a819c;font-size:12px;margin:26px 0 0;border-top:1px solid #142132;padding-top:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
"""

LANG_TEXTS = {
    "en": {
        "today_hot": "Today's Hot Topics",
        "subscription": "Subscription",
        "no_news": "No hot topics available",
        "archive_note":
        "This page is a static archive of a hot news item. Visit the original article:",
        "home": "Home",
        "updated": "Updated",
        "published": "Published"
    },
    "zh-CN": {
        "today_hot": "今日热点",
        "subscription": "订阅",
        "no_news": "暂无热点",
        "archive_note": "本页面为热点新闻静态存档，原文请访问：",
        "home": "首页",
        "updated": "更新于",
        "published": "发布时间"
    },
    "ja": {
        "today_hot": "本日の注目ニュース",
        "subscription": "購読",
        "no_news": "注目ニュースはありません",
        "archive_note": "このページは注目ニュースの静的アーカイブです。元記事はこちら：",
        "home": "ホーム",
        "updated": "更新日時",
        "published": "公開日"
    },
    "fr": {
        "today_hot": "Actualités du jour",
        "subscription": "Abonnement",
        "no_news": "Aucune actualité disponible",
        "archive_note":
        "Cette page est une archive statique d'une actualité. Article original :",
        "home": "Accueil",
        "updated": "Mis à jour",
        "published": "Publié"
    }
    # 其他语言可按需扩展
}


def get_lang_code(country_code):
    mapping = {
        "CN": "zh-CN",
        "TW": "zh-CN",
        "HK": "zh-CN",
        "JP": "ja",
        "FR": "fr",
    }
    return mapping.get((country_code or "").upper(), "en")


def slugify(title):
    """将标题转为文件名友好的 slug"""
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    return slug or "news"


def render_news_page(meta, topic):
    lang_code = get_lang_code(meta.get("country"))
    t = LANG_TEXTS.get(lang_code, LANG_TEXTS["en"])

    city = meta.get("city") or "Unknown City"
    country = meta.get("country") or "Unknown Country"
    isp = meta.get("asOrganization") or "Unknown ISP"
    colo = meta.get("colo") or "N/A"
    now = topic.get("published") or ""
    title = topic.get("title") or "Untitled"
    link = topic.get("link") or "#"
    source = topic.get("source") or ""

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title} - Local Pulse</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>{BASE_CSS}</style>
</head>
<body>
  <header>
    <div class="container">
      <div class="badge">POP: {colo}</div>
      <div class="badge">Region: {city}, {country}</div>
      <div class="badge">{t['published']}: {now}</div>
      <div style="float:right"><a href="../index.html">{t['home']}</a></div>
    </div>
  </header>
  <main class="container">
    <h1>{title}</h1>
    <div class="meta">{source} · {now}</div>
    <p>{t['archive_note']}
       <a href="{link}" target="_blank" rel="noopener">{link}</a>
    </p>
  </main>
</body>
</html>"""
    return html


def write_news_pages(public_dir, meta, topics):
    news_dir = os.path.join(public_dir, "news")
    os.makedirs(news_dir, exist_ok=True)
    pages = []
    for t in topics:
        slug = slugify(t.get("title", ""))
        filename = f"{slug}.html"
        path = os.path.join(news_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(render_news_page(meta, t))
        pages.append((t, f"news/{filename}"))
    return pages


def render_blog_html(meta: dict, topics_with_pages: list):
    lang_code = get_lang_code(meta.get("country"))
    t = LANG_TEXTS.get(lang_code, LANG_TEXTS["en"])

    city = meta.get("city") or "Unknown City"
    country = meta.get("country") or "Unknown Country"
    colo = meta.get("colo") or "N/A"
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    cards = []
    for topic, local_link in topics_with_pages:
        title = (topic.get("title")
                 or "").replace("<", "&lt;").replace(">", "&gt;")
        source = topic.get("source") or ""
        published = topic.get("published") or ""
        cards.append(f"""
        <article class="card">
          <a href="{local_link}">
            <h2>{title}</h2>
          </a>
          <div class="meta">{source} · {published}</div>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{city}, {country} · Local Pulse</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>{BASE_CSS}</style>
</head>
<body>
  <header>
    <div class="container">
      <div class="badge">POP: {colo}</div>
      <div class="badge">Region: {city}, {country}</div>
      <div class="badge">Updated: {now}</div>
    </div>
  </header>
  <main class="container">
    <h1>{city} · {t['today_hot']}</h1>
    <section class="grid">
      {''.join(cards) if cards else '<div class="card"><div class="meta">{t["no_news"]}</div></div>'}
    </section>
    <div class="footer">This page updates on each app start. Data: Google News RSS · Cloudflare meta</div>
  </main>
</body>
</html>"""
    return html


def write_blog(public_dir: str, html: str):
    os.makedirs(public_dir, exist_ok=True)
    path = os.path.join(public_dir, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
