import requests

def get_cf_meta(timeout=8):
    try:
        resp = requests.get("https://speed.cloudflare.com/meta", timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"[错误] 请求 Cloudflare meta 失败: {e}")
        return None

def summarize_meta(meta: dict) -> dict:
    if not meta:
        return {}
    return {
        "asn": meta.get("asn"),
        "asOrganization": meta.get("asOrganization"),
        "colo": meta.get("colo"),
        "country": meta.get("country"),
        "city": meta.get("city"),
        "region": meta.get("region"),
        "latitude": meta.get("latitude"),
        "longitude": meta.get("longitude"),
        "clientIp": meta.get("clientIp"),
    }
