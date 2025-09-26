from analytics.backfill_to_bq import backfill_products

if __name__ == "__main__":
    res = backfill_products()
    print(res)
