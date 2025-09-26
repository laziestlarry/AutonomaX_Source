import os
from typing import Optional

import pandas as pd
from google.cloud import bigquery

from utils.slack import send as slack_send

PROJECT = os.getenv("GCP_PROJECT_ID")
DATASET = os.getenv("BQ_DATASET", "autonomax")


def _bq() -> Optional[bigquery.Client]:
    if not PROJECT:
        return None
    return bigquery.Client(project=PROJECT)


def _fetch() -> pd.DataFrame:
    client = _bq()
    if not client:
        return pd.DataFrame()
    sql = f"""SELECT DATE(created_at) dt, COUNT(1) orders_count, SUM(total) gmv
             FROM `{PROJECT}.{DATASET}.v_shopify_orders`
             WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
             GROUP BY 1 ORDER BY 1"""
    return client.query(sql).result().to_dataframe(create_bqstorage_client=False)


def run_check():
    try:
        if not PROJECT:
            return {"status": "disabled", "reason": "missing_gcp_project"}
        df = _fetch()
        if df.empty:
            return {"status": "no_data"}
        df["aov"] = df["gmv"] / df["orders_count"]
        for col in ["orders_count", "gmv", "aov"]:
            mu = df[col].mean()
            sigma = df[col].std() or 1.0
            latest = df[col].iloc[-1]
            z = (latest - mu) / sigma
            if abs(z) >= 2.5:
                slack_send(
                    f"Anomaly in {col}: z={z:.2f}",
                    level="warn",
                    context={"latest": latest, "mu": mu, "sigma": sigma},
                )
        return {"status": "ok", "days": len(df)}
    except Exception as e:
        slack_send(f"Anomaly check error: {e}", level="error")
        return {"status": "error", "error": str(e)}
