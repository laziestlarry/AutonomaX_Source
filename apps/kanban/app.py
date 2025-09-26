import os, json, time, pathlib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AutonomaX – Kanban", layout="wide")
st.title("AutonomaX – Automated Kanban")

TASKS_CSV = pathlib.Path(os.getenv("TASKS_CSV", "data_room/inventory/tasks.csv"))
STATUS_JSON = pathlib.Path(os.getenv("TASKS_STATUS", "data_room/inventory/tasks_status.json"))

if not TASKS_CSV.exists():
    st.warning("No tasks.csv found. Use Commander → Blueprints/Agents to append tasks.")
    st.stop()

@st.cache_data
def load_tasks(path: pathlib.Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize columns
    cols = {c.lower(): c for c in df.columns}
    # Expect at least ts, role, desc, path
    for c in ['ts','role','desc','path']:
        if c not in (x.lower() for x in df.columns):
            df[c] = ''
    return df

def load_status() -> dict:
    if STATUS_JSON.exists():
        try:
            return json.loads(STATUS_JSON.read_text())
        except Exception:
            return {}
    return {}

def save_status(sts: dict):
    STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATUS_JSON.write_text(json.dumps(sts, indent=2))

df = load_tasks(TASKS_CSV)
status_map = load_status()  # key: task_key -> status

def task_key(row) -> str:
    return f"{row.get('desc','')}|{row.get('path','')}"

def derive_bus(role: str) -> str:
    r = (role or '').lower()
    if r in ("devops","platform"): return "platform"
    if r in ("dev","engineering"): return "engineering"
    if r in ("data","analysis","analytics"): return "data"
    if r in ("growth","marketing"): return "growth"
    if r in ("pm","advisor","product"): return "management"
    return r or "misc"

# Build working set
rows = []
for _, r in df.iterrows():
    d = {k.lower(): r[k] for k in r.keys()}
    d['bus'] = derive_bus(str(d.get('role','')))
    k = task_key(d)
    d['status'] = status_map.get(k, 'todo')
    rows.append(d)

kanban_df = pd.DataFrame(rows)

# Filters
cols = st.columns(4)
with cols[0]: bus_sel = st.multiselect("Bus", sorted(kanban_df['bus'].unique().tolist()), default=sorted(kanban_df['bus'].unique().tolist()))
with cols[1]: role_sel = st.multiselect("Role", sorted(kanban_df['role'].astype(str).unique().tolist()), default=sorted(kanban_df['role'].astype(str).unique().tolist()))
with cols[2]: q = st.text_input("Search", value="")
with cols[3]: show = st.selectbox("Show", options=["all","todo","in_progress","blocked","done"], index=0)

f = kanban_df[kanban_df['bus'].isin(bus_sel) & kanban_df['role'].astype(str).isin(role_sel)]
if q:
    ql = q.lower()
    f = f[f['desc'].astype(str).str.lower().str.contains(ql) | f['path'].astype(str).str.lower().str.contains(ql)]
if show != 'all':
    f = f[f['status'] == show]

st.caption(f"Tasks: {len(f)} filtered / {len(kanban_df)} total")

# Kanban columns
st.markdown("---")
col_todo, col_prog, col_block, col_done = st.columns(4)

def render_column(col, name, status):
    with col:
        st.subheader(name)
        subset = f[f['status'] == status]
        for _, row in subset.iterrows():
            with st.container(border=True):
                st.write(f"{row['desc']}")
                st.caption(f"{row['role']} • {row['bus']}\n{row['path']}")
                k = task_key(row)
                bcols = st.columns(4)
                with bcols[0]:
                    if st.button("→ Prog", key=f"to_prog_{k}"):
                        status_map[k] = 'in_progress'
                with bcols[1]:
                    if st.button("→ Block", key=f"to_block_{k}"):
                        status_map[k] = 'blocked'
                with bcols[2]:
                    if st.button("✓ Done", key=f"to_done_{k}"):
                        status_map[k] = 'done'
                with bcols[3]:
                    if st.button("⟲ Todo", key=f"to_todo_{k}"):
                        status_map[k] = 'todo'

render_column(col_todo, "To Do", 'todo')
render_column(col_prog, "In Progress", 'in_progress')
render_column(col_block, "Blocked", 'blocked')
render_column(col_done, "Done", 'done')

if st.button("Save Status"):
    save_status(status_map)
    st.success("Statuses saved")

