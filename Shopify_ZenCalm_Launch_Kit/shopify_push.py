#!/usr/bin/env python3
import os, csv, base64, json, time, requests

SHOP_DOMAIN = os.environ.get("SHOP_DOMAIN", "autonomax.myshopify.com")
ADMIN_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-04")
CSV_FILE = os.environ.get("PRODUCT_CSV", "products.csv")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

BASE = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}"
HEADERS = {"X-Shopify-Access-Token": ADMIN_TOKEN, "Content-Type": "application/json"}

def create_product(row):
    attachment = None
    if row.get("image_path") and os.path.exists(row["image_path"]):
        with open(row["image_path"], "rb") as imgf:
            b64 = base64.b64encode(imgf.read()).decode("utf-8")
            attachment = {"attachment": b64, "filename": os.path.basename(row["image_path"])}

    product_payload = {
        "product": {
            "title": row["title"],
            "body_html": row["body_html"],
            "vendor": row.get("vendor", "AutonomaX"),
            "product_type": row.get("product_type", "Digital"),
            "tags": row.get("tags", ""),
            "status": "draft",
            "variants": [{"price": row.get("price", "129.90"), "sku": row.get("sku", ""), "inventory_policy": "deny", "requires_shipping": False}],
            "images": [attachment] if attachment else []
        }
    }

    if DRY_RUN:
        print("DRY_RUN Product:", json.dumps(product_payload)[:200], "...")
        return None

    url = f"{BASE}/products.json"
    r = requests.post(url, headers=HEADERS, json=product_payload, timeout=60)
    if r.status_code >= 300:
        print("ERROR creating product:", r.status_code, r.text)
        return None
    prod = r.json().get("product", {})
    print(f"Created product id={prod.get('id')} title={row['title']}")
    return prod

def main():
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            create_product(row)
            time.sleep(0.5)

if __name__ == "__main__":
    main()