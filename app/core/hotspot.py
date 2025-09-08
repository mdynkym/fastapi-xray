import urllib.parse
import feedparser

COUNTRY_LANG_MAP = {
    "US": ("en", "US"), "GB": ("en", "GB"), "CA": ("en", "CA"),
    "AU": ("en", "AU"), "NZ": ("en", "NZ"), "SG": ("en", "SG"),
    "IN": ("en", "IN"), "CN": ("zh-CN", "CN"), "TW": ("zh-TW", "TW"),
    "HK": ("zh-HK", "HK"), "JP": ("ja", "JP"), "KR": ("ko", "KR"),
    "FR": ("fr", "FR"), "DE": ("de", "DE"), "ES": ("es", "ES"),
    "IT": ("it", "IT"), "RU": ("ru", "RU"), "BR": ("pt-BR", "BR"),
    "MX": ("es", "MX"), "AR": ("es", "AR"), "TR": ("tr", "TR"),
    "SA": ("ar", "SA"), "AE": ("ar", "AE"),
}

def get_lang_region_for_country(country_code: str):
    return COUNTRY_LANG_MAP.get((country_code or "").upper(), ("en", "US"))

def build_gnews_rss(city: str = None, country: str = None):
    lang, region = get_lang_region_for_country(country)
    if city and country:
        q = f"{city} {country}"
    elif country:
        q = country
    elif city:
        q = city
    else:
        q = "Cloudflare POP"
    qs = urllib.parse.urlencode({"q": q})
    return f"https://news.google.com/rss/search?{qs}&hl={lang}-{region}&gl={region}&ceid={region}:{lang}"

def fetch_hot_topics(city: str = None, country: str = None, limit: int = 12):
    url = build_gnews_rss(city, country)
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:limit]:
        items.append({
            "title": entry.get("title", "").strip(),
            "link": entry.get("link"),
            "source": (entry.get("source", {}) or {}).get("title") if isinstance(entry.get("source"), dict) else None,
            "published": entry.get("published", ""),
        })
    return items
