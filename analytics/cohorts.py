import os
import pandas as pd
from typing import Dict, Any
from google.cloud import bigquery

def _bq():
    return bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))

def retention_from_bq(dataset: str, table: str, signup_col: str = "signup_date", active_col: str = "active_date") -> Dict[str, Any]:
    sql = f"""
    WITH signups AS (
      SELECT DATE({signup_col}) AS d, COUNT(1) AS users FROM `{dataset}.{table}` GROUP BY 1
    ), actives AS (
      SELECT DATE({active_col}) AS d, COUNT(1) AS users FROM `{dataset}.{table}` GROUP BY 1
    )
    SELECT s.d AS date, s.users AS signups, IFNULL(a.users,0) AS actives
    FROM signups s LEFT JOIN actives a USING(d) ORDER BY 1
    """
    df = _bq().query(sql).result().to_dataframe(create_bqstorage_client=False)
    return {"rows": df.to_dict(orient="records")}

def retention_from_csv(path: str, signup_col: str = "signup_date", active_col: str = "active_date") -> Dict[str, Any]:
    df = pd.read_csv(path, parse_dates=[signup_col, active_col])
    df["signup_d"] = pd.to_datetime(df[signup_col]).dt.date
    df["active_d"] = pd.to_datetime(df[active_col]).dt.date
    s = df.groupby("signup_d").size().reset_index(name="signups")
    a = df.groupby("active_d").size().reset_index(name="actives")
    out = s.merge(a, left_on="signup_d", right_on="active_d", how="left").fillna(0)
    out.rename(columns={"signup_d":"date"}, inplace=True)
    out = out[["date","signups","actives"]]
    return {"rows": out.to_dict(orient="records")}

def ltv_from_csv(path: str, cohort_col: str = "cohort", revenue_col: str = "revenue") -> Dict[str, Any]:
    df = pd.read_csv(path)
    out = df.groupby(cohort_col)[revenue_col].mean().reset_index(name="ltv")
    return {"rows": out.to_dict(orient="records")}
