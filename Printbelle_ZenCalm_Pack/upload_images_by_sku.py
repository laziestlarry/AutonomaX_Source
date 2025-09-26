#!/usr/bin/env python3
import os, sys, csv, json, time, base64, requests
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

def paginate_variants_exact_sku(sku, limit=250, max_pages=40):
    url="/variants.json"; params={"limit":str(limit)}
    pages=0
    while pages<max_pages:
        resp=get(url, params=params)
        js=resp.json()
        for v in js.get("variants", []):
            if (v.get("sku") or "")==sku:
                return v["id"], v["product_id"]
        link=resp.headers.get("Link",""); next_url=None
        for part in link.split(","):
            if 'rel="next"' in part:
                start=part.find("<")+1; end=part.find(">")
                full=part[start:end]
                parsed=urlparse(full); q=parse_qs(parsed.query)
                params={"limit": q.get("limit",["250"])[0], "page_info": q["page_info"][0]}
                next_url=parsed.path
        if not next_url: break
        url=next_url; pages+=1
    return None, None

def attach_image(pid, vid, image_path):
    with open(image_path,"rb") as f:
        b64=base64.b64encode(f.read()).decode("utf-8")
    payload={"image":{"attachment":b64,"filename":os.path.basename(image_path),"variant_ids":[vid]}}
    js=post(f"/products/{pid}/images.json", payload)
    return js.get("image",{}).get("id")

def main():
    need_env()
    map_path=sys.argv[1] if len(sys.argv)>1 else "image_map.csv"
    root=os.path.dirname(map_path) or "."
    if not os.path.isfile(map_path):
        print(f"image map not found: {map_path}", file=sys.stderr); sys.exit(1)

    ok=miss=0
    with open(map_path, newline="", encoding="utf-8") as f:
        r=csv.DictReader(f)
        for row in r:
            sku=(row.get("SKU") or row.get("Variant SKU") or "").strip()
            rel=(row.get("LocalImagePath") or row.get("Path") or "").strip()
            if not sku or not rel: continue
            image_path=os.path.join(root, rel)
            print(f"→ {sku} — {image_path}")
            if not os.path.isfile(image_path):
                print("  • Missing image; skip"); miss+=1; continue
            vid, pid = paginate_variants_exact_sku(sku)
            if not vid or not pid:
                print(f"  • Variant not found for SKU={sku}; skip"); miss+=1; continue
            try:
                img_id=attach_image(pid, vid, image_path)
                print(f"  • Attached image id={img_id}")
                ok+=1; time.sleep(0.3)
            except requests.HTTPError as e:
                print(f"  ! HTTP {e.response.status_code}: {e.response.text}"); miss+=1
            except Exception as e:
                print(f"  ! Error: {e}"); miss+=1
    print(f"Done. Attached={ok}, Missed={miss}")

if __name__=='__main__': main()
