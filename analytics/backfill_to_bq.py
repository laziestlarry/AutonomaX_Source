
import os, io, ndjson, requests, json
from google.cloud import bigquery
from shopify.graphql.bulk import run_bulk, poll_for_url, products_query, orders_query
from utils.slack import send as slack_send

PROJECT=os.getenv("GCP_PROJECT_ID"); DATASET=os.getenv("BQ_DATASET","autonomax")
TBLP=os.getenv("BQ_TABLE_PRODUCTS","shopify_products"); TBLO=os.getenv("BQ_TABLE_ORDERS","shopify_orders")

def bq(): return bigquery.Client(project=PROJECT)
def ensure_tables():
    c=bq(); ds=bigquery.Dataset(f"{c.project}.{DATASET}")
    try:c.get_dataset(ds)
    except Exception: c.create_dataset(ds, exists_ok=True)
    def ensure(table, schema):
        ref=f"{c.project}.{DATASET}.{table}"
        try:c.get_table(ref)
        except Exception: c.create_table(bigquery.Table(ref, schema=schema))
    ensure(TBLP,[bigquery.SchemaField("id","STRING"),bigquery.SchemaField("title","STRING"),bigquery.SchemaField("vendor","STRING"),bigquery.SchemaField("productType","STRING"),bigquery.SchemaField("status","STRING"),bigquery.SchemaField("tags","STRING"),bigquery.SchemaField("created_at","TIMESTAMP"),bigquery.SchemaField("updated_at","TIMESTAMP"),bigquery.SchemaField("variants_count","INTEGER"),bigquery.SchemaField("price_min","FLOAT"),bigquery.SchemaField("price_max","FLOAT"),bigquery.SchemaField("raw","STRING")])
    ensure(TBLO,[bigquery.SchemaField("id","STRING"),bigquery.SchemaField("name","STRING"),bigquery.SchemaField("created_at","TIMESTAMP"),bigquery.SchemaField("updated_at","TIMESTAMP"),bigquery.SchemaField("processed_at","TIMESTAMP"),bigquery.SchemaField("currency","STRING"),bigquery.SchemaField("subtotal","FLOAT"),bigquery.SchemaField("total","FLOAT"),bigquery.SchemaField("customer_email","STRING"),bigquery.SchemaField("line_items_count","INTEGER"),bigquery.SchemaField("raw","STRING")])
def _flatten_product(o):
    variants=o.get("variants",{}).get("edges",[]); prices=[]
    for e in variants:
        n=e.get("node",{}); 
        try: prices.append(float(n.get("price") or 0.0))
        except: pass
    return {"id":o.get("id"),"title":o.get("title"),"vendor":o.get("vendor"),"productType":o.get("productType"),"status":o.get("status"),"tags":",".join(o.get("tags",[]) if isinstance(o.get("tags",[]),list) else [o.get("tags","")]),"created_at":o.get("createdAt"),"updated_at":o.get("updatedAt"),"variants_count":len(variants),"price_min":min(prices) if prices else None,"price_max":max(prices) if prices else None,"raw":json.dumps(o)}
def _flatten_order(o):
    subtotal=o.get("currentSubtotalPriceSet",{}).get("shopMoney",{}).get("amount")
    total=o.get("currentTotalPriceSet",{}).get("shopMoney",{}).get("amount")
    items=o.get("lineItems",{}).get("edges",[])
    return {"id":o.get("id"),"name":o.get("name"),"created_at":o.get("createdAt"),"updated_at":o.get("updatedAt"),"processed_at":o.get("processedAt"),"currency":o.get("currencyCode"),"subtotal":float(subtotal) if subtotal else None,"total":float(total) if total else None,"customer_email":(o.get("customer") or {}).get("email"),"line_items_count":len(items),"raw":json.dumps(o)}
def _load_rows(table, rows):
    c=bq(); ref=f"{c.project}.{DATASET}.{table}"; job=c.load_table_from_json(rows, ref); job.result()
def backfill_products():
    ensure_tables()
    try:
        run_bulk(products_query()); url=poll_for_url(); r=requests.get(url, timeout=300); r.raise_for_status()
    except Exception as e:
        slack_send(f"bulk products error: {e}", level="error"); raise
    batch=[]; count=0
    for obj in ndjson.reader(io.StringIO(r.text)):
        if "id" not in obj: continue
        batch.append(_flatten_product(obj))
        if len(batch)>=5000: _load_rows(TBLP,batch); count+=len(batch); batch=[]
    if batch: _load_rows(TBLP,batch); count+=len(batch)
    return {"inserted": count}
def backfill_orders(since=None):
    ensure_tables()
    try:
        run_bulk(orders_query(since)); url=poll_for_url(); r=requests.get(url, timeout=300); r.raise_for_status()
    except Exception as e:
        slack_send(f"bulk orders error: {e}", level="error"); raise
    batch=[]; count=0
    for obj in ndjson.reader(io.StringIO(r.text)):
        if "id" not in obj: continue
        batch.append(_flatten_order(obj))
        if len(batch)>=5000: _load_rows(TBLO,batch); count+=len(batch); batch=[]
    if batch: _load_rows(TBLO,batch); count+=len(batch)
    return {"inserted": count}
