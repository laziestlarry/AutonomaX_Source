
#!/usr/bin/env python3
import os, json, requests
from dotenv import load_dotenv; load_dotenv()
SHOP_DOMAIN=os.getenv("SHOP_DOMAIN"); ADMIN_TOKEN=os.getenv("SHOPIFY_ADMIN_TOKEN"); PUBLIC_URL=os.getenv("WEBHOOK_PUBLIC_URL")
topics=["orders/create","products/create","customers/create","carts/update","app/uninstalled"]
def register(topic):
    url=f"https://{SHOP_DOMAIN}/admin/api/2024-07/webhooks.json"
    headers={"X-Shopify-Access-Token":ADMIN_TOKEN,"Content-Type":"application/json"}
    payload={"webhook":{"topic":topic,"address":f"{PUBLIC_URL}/{topic}","format":"json"}}
    r=requests.post(url,headers=headers,data=json.dumps(payload),timeout=30); print(topic, r.status_code, r.text[:200])
if __name__=="__main__":
    assert SHOP_DOMAIN and ADMIN_TOKEN and PUBLIC_URL
    for t in topics: register(t)
