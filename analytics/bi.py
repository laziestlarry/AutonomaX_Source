from typing import List, Dict, Any
import datetime as dt
import os
from google.cloud import bigquery

PROJECT=os.getenv("GCP_PROJECT_ID")
DATASET=os.getenv("BQ_DATASET","autonomax")
TBLO=os.getenv("BQ_TABLE_ORDERS","shopify_orders")

def _bq():
    return bigquery.Client(project=PROJECT) if PROJECT else None

def _sum_orders(days: int) -> Dict[str, Any]:
    c=_bq()
    if not c: return {"rev":0.0,"cnt":0}
    sql=f"""
      SELECT
        COALESCE(SUM(total),0.0) rev,
        COUNT(1) cnt
      FROM `{PROJECT}.{DATASET}.{TBLO}`
      WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
    """
    try:
        row = list(c.query(sql).result())[0]
        return {"rev": float(row[0] or 0), "cnt": int(row[1] or 0)}
    except Exception:
        return {"rev":0.0,"cnt":0}

def _freshness() -> Dict[str, Any]:
    c=_bq()
    if not c: return {"max_created_at": None, "age_days": None}
    sql=f"""
      SELECT MAX(created_at) AS max_created_at
      FROM `{PROJECT}.{DATASET}.{TBLO}`
    """
    try:
        row = list(c.query(sql).result())[0]
        mx = row[0]
        if not mx:
            return {"max_created_at": None, "age_days": None}
        # Compute age in days relative to now
        # BigQuery returns a datetime; cast to date string
        max_iso = str(mx)
        try:
            from datetime import datetime, timezone
            dtmax = datetime.fromisoformat(max_iso.replace('Z','+00:00'))
            age = (datetime.now(timezone.utc) - dtmax).total_seconds() / 86400.0
            age_days = round(age, 2)
        except Exception:
            age_days = None
        return {"max_created_at": max_iso, "age_days": age_days}
    except Exception:
        return {"max_created_at": None, "age_days": None}

def current_kpis() -> Dict[str, Any]:
    today = dt.date.today().isoformat()
    d1 = _sum_orders(1)
    d7 = _sum_orders(7)
    d28 = _sum_orders(28)
    fresh = _freshness()
    aov_today = round((d1["rev"] / d1["cnt"]) if d1["cnt"] else 0.0, 2)
    aov_28 = round((d28["rev"] / d28["cnt"]) if d28["cnt"] else 0.0, 2)
    return {
        "date": today,
        "revenue": {"today": round(d1["rev"],2), "7d": round(d7["rev"],2), "28d": round(d28["rev"],2)},
        "orders": {"today": d1["cnt"], "7d": d7["cnt"], "28d": d28["cnt"]},
        "aov": {"today": aov_today, "28d": aov_28},
        "data_source": f"{PROJECT}.{DATASET}.{TBLO}" if PROJECT else None,
        "freshness": fresh,
    }

def top_insights() -> List[str]:
    # Placeholder insights; wire to analytics when available
    return [
        "Consider bundling top SKUs to raise AOV",
        "Price test 9.99 vs 10.49 on top 5 SKUs",
        "Automate win-back email at D30 with 15% code",
    ]
