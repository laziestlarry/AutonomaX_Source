import os, json, requests, streamlit as st

st.set_page_config(page_title="Growth Ops", layout="wide")
st.title("Growth Ops")

api_url = st.text_input("API base URL", os.getenv("API_URL","http://127.0.0.1:8080"))
api_key = st.text_input("API key (x-api-key)", os.getenv("API_KEY",""))

st.header("Lifecycle Batch Execution")
users_json = st.text_area("Users JSON", '[{"id":"u1","stage":"new"},{"id":"u2","stage":"churn_risk"}]')
if st.button("Run batch"):
    try:
        users = json.loads(users_json)
        r = requests.post(f"{api_url}/ops/lifecycle/batch", json={"users": users}, headers={"x-api-key": api_key} if api_key else {}, timeout=30)
        st.write(r.status_code, r.text)
        if r.ok:
            st.success(r.json())
        else:
            st.error(f"Error: {r.text}")
    except Exception as e:
        st.error(str(e))

st.header("Referral Campaign")
seed = st.text_input("Seed", "segment-alpha")
tiers = st.number_input("Tiers", min_value=1, max_value=3, value=3)
if st.button("Create referral"):
    try:
        r = requests.get(f"{api_url}/growth/referral", params={"seed": seed, "tiers": tiers}, headers={"x-api-key": api_key} if api_key else {}, timeout=15)
        st.write(r.status_code, r.text)
        if r.ok:
            st.success(r.json())
        else:
            st.error(f"Error: {r.text}")
    except Exception as e:
        st.error(str(e))

st.header("Experiment Assign & Outcome")
uid = st.text_input("User ID", "u-test")
exp = st.text_input("Experiment", "pricing-banner")
ratio = st.slider("A ratio", 0.0, 1.0, 0.5)
if st.button("Assign Variant"):
    try:
        r = requests.get(f"{api_url}/experiments/assign", params={"user_id": uid, "experiment": exp, "ratio_a": ratio}, headers={"x-api-key": api_key} if api_key else {}, timeout=15)
        st.write(r.status_code, r.text)
        if r.ok:
            st.success(r.json())
        else:
            st.error(f"Error: {r.text}")
    except Exception as e:
        st.error(str(e))

outcome_json = st.text_area("Outcome JSON", '{"click":true,"purchase":0}')
variant = st.text_input("Variant", "A")
if st.button("Record Outcome"):
    try:
        body = {"user_id": uid, "experiment": exp, "variant": variant, "outcome": json.loads(outcome_json)}
        r = requests.post(f"{api_url}/experiments/outcome", json=body, headers={"x-api-key": api_key} if api_key else {}, timeout=15)
        st.write(r.status_code, r.text)
        if r.ok:
            st.success(r.json())
        else:
            st.error(f"Error: {r.text}")
    except Exception as e:
        st.error(str(e))

