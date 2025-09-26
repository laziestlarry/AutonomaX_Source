import os, json, base64, mimetypes
from typing import Dict, Any, List
import requests

SHOP_DOMAIN = os.getenv("SHOP_DOMAIN")
ADMIN_TOKEN = os.getenv("SHOPIFY_ADMIN_TOKEN")
API_VER = os.getenv("SHOPIFY_API_VERSION", "2024-07")

def _headers() -> Dict[str, str]:
    return {
        "X-Shopify-Access-Token": ADMIN_TOKEN or "",
        "Content-Type": "application/json",
    }

def _api_url(path: str) -> str:
    if not SHOP_DOMAIN:
        raise RuntimeError("SHOP_DOMAIN not configured")
    return f"https://{SHOP_DOMAIN}/admin/api/{API_VER}{path}"

def _image_payload(p: str) -> Dict[str, Any]:
    if p.startswith("http://") or p.startswith("https://"):
        return {"src": p}
    try:
        with open(p, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        filename = os.path.basename(p)
        return {"attachment": data, "filename": filename}
    except Exception:
        return {}

def create_product(prod: Dict[str, Any]) -> Dict[str, Any]:
    """Create a product via Shopify REST API.

    prod fields: title (str), body_html (str), tags (list[str] or comma str),
    vendor (str), product_type (str), images (list[str path or url]).
    """
    payload: Dict[str, Any] = {
        "title": prod.get("title") or "Untitled",
        "body_html": prod.get("body_html") or "",
        "vendor": prod.get("vendor") or "AutonomaX",
        "product_type": prod.get("product_type") or "digital",
    }
    tags = prod.get("tags")
    if isinstance(tags, list):
        payload["tags"] = ",".join(tags)
    elif isinstance(tags, str):
        payload["tags"] = tags
    imgs = []
    for p in prod.get("images", []) or []:
        ip = _image_payload(p)
        if ip:
            imgs.append(ip)
    if imgs:
        payload["images"] = imgs
    url = _api_url("/products.json")
    r = requests.post(url, headers=_headers(), data=json.dumps({"product": payload}), timeout=60)
    r.raise_for_status()
    data = r.json().get("product", {})
    return {"id": data.get("id"), "title": data.get("title"), "handle": data.get("handle")}

