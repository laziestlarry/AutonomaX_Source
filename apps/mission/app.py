import os, json, pathlib, time
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AutonomaX – Mission Brief", layout="wide")
st.title("AutonomaX – Mission, Strategy, Goals")

# Optional mission markdown
mission_md = pathlib.Path("docs/Mission_Brief.md")
if mission_md.exists():
    st.markdown(mission_md.read_text())
else:
    st.info("Add a mission brief at docs/Mission_Brief.md to display here.")

# Load latest blueprint summary
bp_dir = pathlib.Path("data_room/blueprints")
summaries = sorted(bp_dir.glob("summary_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
bp = {}
if summaries:
    try:
        bp = json.loads(summaries[0].read_text())
    except Exception:
        bp = {}

cols = st.columns(3)
with cols[0]:
    st.subheader("Phase Plan")
    phases = bp.get('phases') or []
    if phases:
        for ph in phases:
            st.write(f"- {ph.get('name')} ({ph.get('window')})")
    else:
        st.caption("No phases found; generate a blueprint.")
with cols[1]:
    st.subheader("First Pipeline")
    fp = bp.get('first_pipeline') or {}
    if fp:
        st.write(fp.get('name'))
        st.caption(fp.get('url') or fp.get('path') or '')
    else:
        st.caption("(none)")
with cols[2]:
    st.subheader("Tasks (counts)")
    tasks = bp.get('tasks') or []
    st.write({
        'total': len(tasks),
        'dev': sum(1 for t in tasks if t.get('role')=='dev'),
        'data': sum(1 for t in tasks if t.get('role')=='data'),
        'growth': sum(1 for t in tasks if t.get('role')=='growth'),
        'pm': sum(1 for t in tasks if t.get('role')=='pm'),
        'advisor': sum(1 for t in tasks if t.get('role')=='advisor'),
    })

st.markdown("---")
st.subheader("Execution Status")

tasks_csv = pathlib.Path("data_room/inventory/tasks.csv")
status_json = pathlib.Path("data_room/inventory/tasks_status.json")
if tasks_csv.exists():
    df = pd.read_csv(tasks_csv)
    st.caption(f"Tasks.csv rows: {len(df)}")
    if status_json.exists():
        try:
            status_map = json.loads(status_json.read_text())
        except Exception:
            status_map = {}
        # Derive status counts by joining keys
        def key_of(row): return f"{row.get('desc','')}|{row.get('path','')}"
        df['status'] = df.apply(lambda r: status_map.get(key_of(r), 'todo'), axis=1)
        st.write(df['status'].value_counts().to_dict())
    else:
        st.caption("No tasks_status.json found; update in Kanban to track status.")
else:
    st.caption("No tasks.csv found; import tasks via Commander Blueprints.")

st.markdown("---")
st.subheader("Admin Status Snapshot")
api_url = st.text_input("API Base URL", value=os.getenv("API_URL", "https://autonomax-api-71658389068.us-central1.run.app"))
if st.button("Fetch /admin/status"):
    import requests
    try:
        r = requests.get(f"{api_url}/admin/status", timeout=15)
        st.code(json.dumps(r.json(), indent=2))
    except Exception as e:
        st.error(f"/admin/status error: {e}")

