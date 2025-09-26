#!/usr/bin/env python3
import os, sys, csv, json, time, requests
from urllib.parse import urlparse, parse_qs

SHOP_DOMAIN=os.environ.get("SHOP_DOMAIN")
TOKEN=os.environ.get("SHOPIFY_ADMIN_TOKEN")
BASE=f"https://{SHOP_DOMAIN}/admin/api/2024-10" if SHOP_DOMAIN else None
H={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

def need_env():
    if not SHOP_DOMAIN or not TOKEN:
        print("Set SHOP_DOMAIN and SHOPIFY_ADMIN_TOKEN in your environment (or .env)", file=sys.stderr)
        sys.exit(1)

def get(path, params=None):
    r=requests.get(f"{BASE}{path}", headers=H, params=params, timeout=60)
    r.raise_for_status()
    return r

def post(path, payload):
    r=requests.post(f"{BASE}{path}", headers=H, data=json.dumps(payload), timeout=120)
    r.raise_for_status()
    return r.json() if r.text else {}

def put(path, payload):
    r=requests.put(f"{BASE}{path}", headers=H, data=json.dumps(payload), timeout=120)
    r.raise_for_status()
    return r.json() if r.text else {}

def paginate_variants_exact_sku(sku, limit=250, max_pages=40):
    # Cursor-based with Link header
    url=f"/variants.json"
    params={"limit":str(limit)}
    pages=0
    while pages<max_pages:
        resp=get(url, params=params)
        js=resp.json()
        for v in js.get("variants", []):
            if (v.get("sku") or "")==sku:
                return v["id"], v["product_id"]
        # follow rel="next"
        link=resp.headers.get("Link","")
        next_url=None
        for part in link.split(","):
            if 'rel="next"' in part:
                # <https://shop.myshopify.com/admin/api/2024-10/variants.json?page_info=...&limit=250>; rel="next"
                start=part.find("<")+1; end=part.find(">")
                if start>0 and end>start:
                    full=part[start:end]
                    parsed=urlparse(full)
                    q=parse_qs(parsed.query)
                    params={"limit": q.get("limit",[str(limit)])[0], "page_info": q["page_info"][0]}
                    next_url=f"{parsed.path}"
        if not next_url: break
        url=next_url; pages+=1
    return None, None

def ensure_collection(title="Zen & Calm"):
    js=get("/custom_collections.json", params={"title":title}).json()
    arr=js.get("custom_collections") or []
    if arr: return arr[0]["id"]
    return post("/custom_collections.json", {"custom_collection":{"title":title,"published":True}})["custom_collection"]["id"]

def add_to_collection(pid, cid):
    try:
        post("/collects.json", {"collect":{"product_id":pid,"collection_id":cid}})
    except requests.HTTPError as e:
        # 422 when already in collection — ignore quietly
        if e.response is None or e.response.status_code!=422:
            raise

def patch_product(pid):
    put(f"/products/{pid}.json", {"product":{"id":pid,"product_type":"Digital Art","tags":"digital,printable,abstract,zen,printbelle"}})

def patch_variant(vid):
    put(f"/variants/{vid}.json", {"variant":{"id":vid,"requires_shipping":False}})

def main():
    need_env()
    csv_path=sys.argv[1] if len(sys.argv)>1 else "shopify_products.csv"
    if not os.path.isfile(csv_path):
        print(f"CSV not found: {csv_path}", file=sys.stderr); sys.exit(1)

    cid=ensure_collection("Zen & Calm")
    print(f"Collection Zen & Calm id = {cid}")

    ok=miss=0
    with open(csv_path, newline="", encoding="utf-8") as f:
        r=csv.DictReader(f)
        for row in r:
            sku=(row.get("Variant SKU") or row.get("SKU") or "").strip()
            title=(row.get("Title") or "").strip()
            if not sku: continue
            print(f"→ {sku} — {title}")
            vid, pid = paginate_variants_exact_sku(sku)
            if not vid or not pid:
                print(f"  • Variant not found for SKU={sku}; skip"); miss+=1; continue
            try:
                patch_product(pid)
                patch_variant(vid)
                add_to_collection(pid, cid)
                print(f"  • Patched SKU {sku} (pid={pid}, vid={vid})")
                ok+=1
                time.sleep(0.25)
            except requests.HTTPError as e:
                print(f"  ! HTTP error: {e.response.status_code} {e.response.text}"); miss+=1
            except Exception as e:
                print(f"  ! Error: {e}"); miss+=1

    print(f"Done. Patched={ok}, Missed={miss}")

if __name__=="__main__": main()
