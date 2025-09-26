
import os, time, json, requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv; load_dotenv()
SHOP_DOMAIN=os.getenv("SHOP_DOMAIN"); ADMIN_TOKEN=os.getenv("SHOPIFY_ADMIN_TOKEN"); API_VER=os.getenv("SHOPIFY_API_VERSION","2024-07")
def _headers(): return {"X-Shopify-Access-Token":ADMIN_TOKEN,"Content-Type":"application/json"}
def graphql(query:str)->Dict[str,Any]:
    url=f"https://{SHOP_DOMAIN}/admin/api/{API_VER}/graphql.json"
    r=requests.post(url, headers=_headers(), data=json.dumps({"query":query}), timeout=60); r.raise_for_status(); return r.json()
def run_bulk(query:str)->Dict[str,Any]:
    q=f"""mutation {{ bulkOperationRunQuery(query: {json.dumps(query)}) {{ bulkOperation {{ id status }} userErrors {{ field message }} }} }}"""
    return graphql(q)
def current_bulk()->Dict[str,Any]: return graphql("query { currentBulkOperation { id status url errorCode } }")
def poll_for_url(timeout_sec:int=900, interval:int=5)->Optional[str]:
    t0=time.time()
    while time.time()-t0<timeout_sec:
        op=current_bulk().get("data",{}).get("currentBulkOperation",{})
        st=op.get("status")
        if st in ("COMPLETED","FAILED","CANCELED"):
            if st=="COMPLETED": return op.get("url")
            raise RuntimeError(f"Bulk status: {st} ({op.get('errorCode')})")
        time.sleep(interval)
    raise TimeoutError("Timed out")
def products_query()->str:
    return """{ products { edges { node { id title vendor productType status tags createdAt updatedAt variants { edges { node { id sku price inventoryQuantity createdAt updatedAt }}}}}}}"""
def orders_query(since: Optional[str]=None)->str:
    q=f"created_at:>={since}" if since else ""
    return f"""{{ orders(query: "{q}") {{ edges {{ node {{ id name createdAt updatedAt processedAt currencyCode currentSubtotalPriceSet {{ shopMoney {{ amount currencyCode }} }} currentTotalPriceSet {{ shopMoney {{ amount currencyCode }} }} customer {{ id email }} lineItems {{ edges {{ node {{ id name sku quantity originalUnitPriceSet {{ shopMoney {{ amount currencyCode }} }} }} }} }} }} }} }} }}"""
