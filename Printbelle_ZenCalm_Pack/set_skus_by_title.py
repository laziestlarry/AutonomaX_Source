#!/usr/bin/env python3
import os, sys, csv, time, json, requests
from urllib.parse import urlparse, parse_qs

SHOP_DOMAIN=os.environ.get("SHOP_DOMAIN")
TOKEN=os.environ.get("SHOPIFY_ADMIN_TOKEN")
BASE=f"https://{SHOP_DOMAIN}/admin/api/2024-10" if SHOP_DOMAIN else None
H={"X-Shopify-Access-Token": TOKEN, "Content-Type":"application/json"}

def need_env():
    if not SHOP_DOMAIN or not TOKEN:
        print("Set SHOP_DOMAIN and SHOPIFY_ADMIN_TOKEN in your environment (or .env)"); sys.exit(1)

def get(path, params=None):
    r=requests.get(f"{BASE}{path}", headers=H, params=params, timeout=60)
    r.raise_for_status(); return r

def put(path, payload):
    r=requests.put(f"{BASE}{path}", headers=H, data=json.dumps(payload), timeout=60)
    r.raise_for_status(); return r.json() if r.text else {}

def find_product_by_exact_title(title, limit=250, max_pages=40):
    url="/products.json"; params={"limit":str(limit)}
    pages=0
    while pages<max_pages:
        resp=get(url, params=params); js=resp.json()
        for p in js.get("products", []):
            if (p.get("title") or "") == title:
                return p
        link=resp.headers.get("Link",""); next_url=None
        for part in link.split(","):
            if 'rel="next"' in part:
                start=part.find("<")+1; end=part.find(">")
                full=part[start:end]; parsed=urlparse(full); q=parse_qs(parsed.query)
                params={"limit": q.get("limit",["250"])[0], "page_info": q["page_info"][0]}
                next_url=parsed.path
        if not next_url: break
        url=next_url; pages+=1
    return None

def main():
    need_env()
    csv_path=sys.argv[1] if len(sys.argv)>1 else "shopify_products.csv"
    if not os.path.isfile(csv_path):
        print(f"CSV not found: {csv_path}"); sys.exit(1)

    ok=miss=0
    with open(csv_path, newline="", encoding="utf-8") as f:
        r=csv.DictReader(f)
        for row in r:
            title=(row.get("Title") or "").strip()
            sku=(row.get("Variant SKU") or row.get("SKU") or "").strip()
            price=(row.get("Variant Price") or "").strip()
            if not title or not sku:
                continue
            print(f"→ {title} :: set SKU={sku}{' price='+price if price else ''}")
            p = find_product_by_exact_title(title)
            if not p or not p.get("variants"):
                print("  • product or variant not found; skip"); miss+=1; continue
            v = p["variants"][0]
            payload={"variant":{"id": v["id"], "sku": sku}}
            if price: payload["variant"]["price"] = price
            try:
                put(f"/variants/{v['id']}.json", payload)
                print(f"  • updated variant {v['id']} on product {p['id']}")
                ok+=1; time.sleep(0.25)
            except requests.HTTPError as e:
                print(f"  ! HTTP {e.response.status_code}: {e.response.text}"); miss+=1
    print(f"Done. Updated={ok}, Missed={miss}")

if __name__=='__main__': main()
