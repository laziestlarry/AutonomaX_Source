import streamlit as st
import pandas as pd
from monetization.pricing import suggest_price
from analytics.cohorts import retention_from_csv, ltv_from_csv

st.set_page_config(page_title="Revenue Intelligence", layout="wide")
st.title("Revenue Intelligence")

st.header("Pricing Suggestion")
col1, col2 = st.columns(2)
with col1:
    current_price = st.number_input("Current price", min_value=0.0, value=10.0, step=0.1)
with col2:
    views = st.number_input("Views (period)", min_value=0, value=1000, step=10)
    purchases = st.number_input("Purchases (period)", min_value=0, value=20, step=1)
if st.button("Suggest price"):
    res = suggest_price([{"views": views, "purchases": purchases, "price": current_price}], current_price)
    st.success(res)

st.header("Cohort Retention (CSV)")
csv = st.file_uploader("Upload CSV with signup_date,active_date", type=["csv"])
if csv is not None:
    df = pd.read_csv(csv)
    st.dataframe(df.head())
    try:
        res = retention_from_csv(csv.name if hasattr(csv, 'name') else "uploaded.csv")
    except Exception:
        # In-memory fallback
        df["signup_d"] = pd.to_datetime(df["signup_date"]).dt.date
        df["active_d"] = pd.to_datetime(df["active_date"]).dt.date
        s = df.groupby("signup_d").size().reset_index(name="signups")
        a = df.groupby("active_d").size().reset_index(name="actives")
        out = s.merge(a, left_on="signup_d", right_on="active_d", how="left").fillna(0)
        out.rename(columns={"signup_d":"date"}, inplace=True)
        out = out[["date","signups","actives"]]
        res = {"rows": out.to_dict(orient="records")}
    st.subheader("Retention Summary")
    st.dataframe(pd.DataFrame(res["rows"]))

st.header("LTV (CSV)")
csv2 = st.file_uploader("Upload CSV with cohort,revenue", type=["csv"], key="ltv")
if csv2 is not None:
    df2 = pd.read_csv(csv2)
    st.dataframe(df2.head())
    st.subheader("Average LTV by Cohort")
    res2 = ltv_from_csv(csv2.name if hasattr(csv2, 'name') else "uploaded2.csv") if False else {"rows": df2.groupby("cohort")["revenue"].mean().reset_index(name="ltv").to_dict(orient="records")}
    st.dataframe(pd.DataFrame(res2["rows"]))
