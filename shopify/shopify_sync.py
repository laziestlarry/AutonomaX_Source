
#!/usr/bin/env python3
import os, json, requests
from dotenv import load_dotenv; load_dotenv()
SHOP_DOMAIN=os.getenv("SHOP_DOMAIN"); ADMIN_TOKEN=os.getenv("SHOPIFY_ADMIN_TOKEN")
def create_product(title, body_html, price):
    url=f"https://{SHOP_DOMAIN}/admin/api/2024-07/products.json"
    headers={"X-Shopify-Access-Token":ADMIN_TOKEN,"Content-Type":"application/json"}
    payload={"product":{"title":title,"body_html":body_html,"variants":[{"price":str(price)}]}}
    r=requests.post(url, headers=headers, data=json.dumps(payload), timeout=30); r.raise_for_status(); print(r.json())
if __name__=="__main__": create_product("AI Test Product","<p>By AutonomaX</p>",9.99)
