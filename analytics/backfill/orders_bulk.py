import os
from analytics.backfill_to_bq import backfill_orders

if __name__ == "__main__":
    since = os.getenv("SHOPIFY_ORDERS_SINCE")  # e.g., 2024-01-01
    res = backfill_orders(since=since)
    print(res)
