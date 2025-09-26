import os, json, time, pathlib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Commander_AutonomaX", layout="wide")
st.title("Commander_AutonomaX — Control Center")

inv_path = pathlib.Path(os.getenv("INVENTORY_PATH", "data_room/inventory/inventory.json"))
if not inv_path.exists():
    st.warning("No inventory.json found. Run: ./ops/intake_inventory.sh --root . --label local")
    st.stop()

data = json.loads(inv_path.read_text())
df = pd.DataFrame(data.get("items", []))
st.caption(f"Items: {len(df)} • Generated at: {data.get('generated_at')}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Inventory", "Tagging", "Task Planner", "Agents", "Blueprints"])

with tab1:
    cols = st.columns(3)
    with cols[0]: kind = st.selectbox("Kind", options=["all","code","doc","data","media","other"], index=0)
    with cols[1]: label = st.text_input("Label contains", value="")
    with cols[2]: q = st.text_input("Path contains", value="")
    filt = df
    if kind != "all": filt = filt[filt["kind"] == kind]
    if label: filt = filt[filt["label"].str.contains(label, case=False, na=False)]
    if q: filt = filt[filt["path"].str.contains(q, case=False, na=False)]
    st.dataframe(filt[["label","kind","size","path"]].sort_values("size", ascending=False).head(500), use_container_width=True)

    st.markdown("### Remap Missing Paths")
    missing = df[df['kind'] == 'missing'] if 'kind' in df.columns else df.iloc[0:0]
    st.caption(f"Missing references: {len(missing)}")
    with st.expander("Remap by prefix (old → new)"):
        old = st.text_input("Old prefix", value="/old/base/path")
        new = st.text_input("New prefix", value="/new/base/path")
        if st.button("Generate remapped list (filelist)"):
            import csv
            out = pathlib.Path("data_room/inventory/remapped_filelist.csv")
            out.parent.mkdir(parents=True, exist_ok=True)
            # Apply prefix mapping on all paths (not only missing) to ease full refresh
            mapped = []
            for p in df['path'].tolist():
                mp = p
                if p.startswith(old):
                    mp = new + p[len(old):]
                mapped.append(mp)
            with open(out, 'w', newline='') as f:
                w = csv.writer(f)
                for p in mapped:
                    w.writerow([p])
            st.success(f"Wrote remapped filelist: {out}. Re-run intake: ./ops/intake_inventory.sh --filelist {out} --label remapped")

with tab2:
    st.subheader("Assign tags to items")
    tags_file = pathlib.Path("data_room/inventory/tags.json")
    tags = {}
    if tags_file.exists():
        try: tags = json.loads(tags_file.read_text())
        except Exception: tags = {}
    sample = df.sample(min(50, len(df))) if len(df) else df
    for _, row in sample.iterrows():
        key = row["path"]
        val = st.text_input(f"Tags for: {row['relpath']}", value=",".join(tags.get(key, [])))
        if val:
            tags[key] = [t.strip() for t in val.split(",") if t.strip()]
    if st.button("Save Tags"):
        tags_file.parent.mkdir(parents=True, exist_ok=True)
        tags_file.write_text(json.dumps(tags, indent=2))
        st.success("Tags saved")

with tab3:
    st.subheader("Plan tasks for teams")
    roles = ["research","analysis","dev","pm","advisor"]
    defaults = ["catalog assets","clean & dedupe","wire BI KPIs","prepare lander","review strategy"]
    colp = st.columns(2)
    with colp[0]: role = st.selectbox("Role", options=roles, index=2)
    with colp[1]: desc = st.text_input("Task description", value=defaults[2])
    selected = st.multiselect("Select items (by path)", options=df["path"].tolist()[:1000])
    if st.button("Append to tasks.csv"):
        out = pathlib.Path("data_room/inventory/tasks.csv")
        out.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if out.exists() else "w"
        import csv
        with open(out, mode, newline="") as f:
            w = csv.writer(f)
            if mode == "w": w.writerow(["ts","role","desc","path"])  # header
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            if not selected:
                w.writerow([ts, role, desc, "<none>"])
            else:
                for p in selected: w.writerow([ts, role, desc, p])
        st.success(f"Appended {max(1,len(selected))} row(s) to tasks.csv")

with tab4:
    st.subheader("Auto-suggestion Agents (rule-based)")
    st.caption("Proposes tags and tasks from inventory.json; add your resources list below to triage links/paths.")

    # Resource list management
    res_file = pathlib.Path("data_room/inventory/resources.json")
    resources = []
    if res_file.exists():
        try: resources = json.loads(res_file.read_text())
        except Exception: resources = []
    st.write("Tracked resources:")
    st.code(json.dumps(resources, indent=2) if resources else "[]", language="json")
    new_res = st.text_input("Add resource (URL or local path)", value="")
    if st.button("Add Resource") and new_res.strip():
        resources.append({"ts": time.time(), "value": new_res.strip()})
        res_file.parent.mkdir(parents=True, exist_ok=True)
        res_file.write_text(json.dumps(resources, indent=2))
        st.success("Resource added")

    # Suggestions from inventory
    from tools.agents import propose_from_inventory
    tag_sugs, task_sugs = propose_from_inventory(df.to_dict(orient='records'))
    st.write("Tag suggestions (sample):")
    st.dataframe(pd.DataFrame(tag_sugs).head(100), use_container_width=True)

    st.write("Task suggestions:")
    df_tasks = pd.DataFrame(task_sugs)
    st.dataframe(df_tasks.head(200), use_container_width=True)

    # Apply selected suggestions
    st.markdown("### Apply suggestions")
    sel_paths = st.multiselect("Select paths to apply tags from suggestions", options=[t['path'] for t in tag_sugs][:500])
    if st.button("Apply Tags to tags.json"):
        tags_file = pathlib.Path("data_room/inventory/tags.json")
        current = {}
        if tags_file.exists():
            try: current = json.loads(tags_file.read_text())
            except Exception: current = {}
        for s in tag_sugs:
            if s['path'] in sel_paths:
                current[s['path']] = list(sorted(set(current.get(s['path'], [])) | set(s['tags'])))
        tags_file.parent.mkdir(parents=True, exist_ok=True)
        tags_file.write_text(json.dumps(current, indent=2))
        st.success("Tags updated")

    sel_tasks = st.multiselect("Select tasks to append", options=[f"{t['role']} | {t['desc']} | {t['path']}" for t in task_sugs][:500])
    if st.button("Append Selected to tasks.csv"):
        out = pathlib.Path("data_room/inventory/tasks.csv")
        out.parent.mkdir(parents=True, exist_ok=True)
        import csv
        with open(out, "a" if out.exists() else "w", newline="") as f:
            w = csv.writer(f)
            if out.stat().st_size == 0:
                w.writerow(["ts","role","desc","path"])  # header
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            for row in sel_tasks:
                role, desc, path = [s.strip() for s in row.split('|', 2)]
                w.writerow([ts, role, desc, path])
        st.success("Tasks appended")

with tab5:
    st.subheader("Blueprints — Import tasks from latest plan")
    bp_dir = pathlib.Path("data_room/blueprints")
    if not bp_dir.exists():
        st.warning("No blueprints found. Generate one: ./ops/generate_blueprint.sh /path/to/my_repos_ranked.csv local 12")
        st.stop()
    # Find latest summary_*.json
    summaries = sorted(bp_dir.glob("summary_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not summaries:
        st.warning("No summary_*.json found in data_room/blueprints. Run the generator.")
        st.stop()
    sel = st.selectbox("Select blueprint", options=[p.name for p in summaries], index=0)
    bp = {}
    try:
        bp = json.loads((bp_dir / sel).read_text())
    except Exception as e:
        st.error(f"Failed to read blueprint: {e}")
        st.stop()

    st.caption(f"Generated at: {bp.get('generated_at','?')} • Selected: {bp.get('count_selected',0)} / {bp.get('count_total',0)}")
    first = bp.get('first_pipeline') or {}
    if first:
        st.info(f"First pipeline: {first.get('name')} — {first.get('url') or first.get('path')}")
    phases = [p.get('name') for p in bp.get('phases', [])]
    tasks = bp.get('tasks', [])
    if not tasks:
        st.warning("No tasks in blueprint.")
        st.stop()

    df_bp = pd.DataFrame(tasks)
    colf = st.columns(3)
    with colf[0]:
        roles = sorted(df_bp['role'].dropna().unique().tolist())
        role_sel = st.multiselect("Roles", roles, default=roles)
    with colf[1]:
        phs = sorted(df_bp['phase'].dropna().unique().tolist())
        phase_sel = st.multiselect("Phases", phs, default=phs)
    with colf[2]:
        pr_min, pr_max = int(df_bp['priority'].min()), int(df_bp['priority'].max())
        pr_rng = st.slider("Priority range", min_value=pr_min, max_value=pr_max, value=(pr_min, pr_max))

    filt = df_bp[
        df_bp['role'].isin(role_sel)
        & df_bp['phase'].isin(phase_sel)
        & (df_bp['priority'] >= pr_rng[0])
        & (df_bp['priority'] <= pr_rng[1])
    ]
    st.dataframe(filt[['role','task','phase','priority','ref']].sort_values(['priority','role']), use_container_width=True, height=360)

    st.markdown("### Actions")
    cols_act = st.columns(3)
    with cols_act[0]:
        append_all = st.button("Append filtered → tasks.csv")
    with cols_act[1]:
        import_all = st.button("Import ALL blueprint tasks → tasks.csv")
    with cols_act[2]:
        export_pair = st.button("Export filtered → GitHub/GitLab JSON")
    # Extra controls for direct issue creation via gh/glab CLIs (optional)
    repo_input = st.text_input("Repo (ORG/REPO or GROUP/REPO for GitLab)", value="")
    exec_now = st.checkbox("Execute now (run gh/glab commands)", value=False)
    cols_cli = st.columns(2)
    with cols_cli[0]: do_gh = st.button("Create filtered issues via gh (CLI)")
    with cols_cli[1]: do_glab = st.button("Create filtered issues via glab (CLI)")
    if append_all:
        out = pathlib.Path("data_room/inventory/tasks.csv")
        out.parent.mkdir(parents=True, exist_ok=True)
        import csv
        new_rows = filt[['role','task','phase','priority','ref']].to_dict(orient='records')
        with open(out, 'a' if out.exists() else 'w', newline='') as f:
            w = csv.writer(f)
            if not out.exists() or out.stat().st_size == 0:
                w.writerow(["ts","role","desc","path"])  # reuse schema; map fields
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            for r in new_rows:
                w.writerow([ts, r['role'], r['task'], r['ref']])
        st.success(f"Appended {len(new_rows)} task(s) to tasks.csv")
    if import_all:
        out = pathlib.Path("data_room/inventory/tasks.csv")
        out.parent.mkdir(parents=True, exist_ok=True)
        import csv
        all_rows = df_bp[['role','task','phase','priority','ref']].to_dict(orient='records')
        with open(out, 'a' if out.exists() else 'w', newline='') as f:
            w = csv.writer(f)
            if not out.exists() or out.stat().st_size == 0:
                w.writerow(["ts","role","desc","path"])  # reuse schema; map fields
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            for r in all_rows:
                w.writerow([ts, r['role'], r['task'], r['ref']])
        st.success(f"Imported {len(all_rows)} task(s) to tasks.csv")
    if export_pair:
        exp_dir = bp_dir / 'exports'
        exp_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime('%Y%m%d_%H%M%S')
        issues = []
        for r in filt[['role','task','phase','priority','ref']].to_dict(orient='records'):
            title = f"[{r['role']}] {r['task']}"
            body = f"Phase: {r['phase']}\nPriority: P{r['priority']}\nRef: {r['ref']}\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            labels = [r['role'], r['phase'].split(' ')[0] if isinstance(r['phase'], str) else 'phase']
            issues.append({'title': title, 'body': body, 'labels': labels, 'assignees': []})
        gh_path = exp_dir / f'issues_github_{ts}.json'
        gl_path = exp_dir / f'issues_gitlab_{ts}.json'
        try:
            (gh_path).write_text(json.dumps(issues, indent=2))
            (gl_path).write_text(json.dumps([{'title': i['title'], 'description': i['body'], 'labels': ','.join(i['labels'])} for i in issues], indent=2))
            st.success(f"Exported {len(issues)} issues to {gh_path.name} and {gl_path.name}")
            st.code((gh_path).read_text()[:800] + ('\n... (truncated)' if len((gh_path).read_text())>800 else ''))
        except Exception as e:
            st.error(f"Export error: {e}")
    # Execute gh/glab issue creation if requested
    import subprocess, shlex
    if (do_gh or do_glab) and not repo_input.strip():
        st.error("Repo is required for gh/glab issue creation")
    if do_gh and repo_input.strip():
        try:
            tmp_csv = bp_dir / 'exports' / 'tmp_tasks.csv'
            tmp_csv.parent.mkdir(parents=True, exist_ok=True)
            filt[['role','task','phase','priority','ref']].to_csv(tmp_csv, index=False)
            cmd = f"python3 tools/issues_export.py --csv {shlex.quote(str(tmp_csv))} --out . --format gh-cli --repo {shlex.quote(repo_input)}"
            st.code(cmd)
            res = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            st.write("gh commands:")
            st.code(res.stdout[:2000])
            if exec_now:
                # Execute each command line
                import shutil
                if not shutil.which('gh'):
                    st.error("gh CLI not found in PATH")
                else:
                    created = 0
                    for line in res.stdout.splitlines():
                        if not line.strip():
                            continue
                        try:
                            subprocess.run(line, shell=True, check=True)
                            created += 1
                        except Exception as e:
                            st.error(f"gh create failed: {e}")
                    st.success(f"Created {created} GitHub issues")
            else:
                st.info("Copy the commands above to your terminal, or pipe to bash to execute.")
        except Exception as e:
            st.error(f"gh export error: {e}")
    if do_glab and repo_input.strip():
        try:
            tmp_csv = bp_dir / 'exports' / 'tmp_tasks.csv'
            tmp_csv.parent.mkdir(parents=True, exist_ok=True)
            filt[['role','task','phase','priority','ref']].to_csv(tmp_csv, index=False)
            cmd = f"python3 tools/issues_export.py --csv {shlex.quote(str(tmp_csv))} --out . --format glab-cli --repo {shlex.quote(repo_input)}"
            st.code(cmd)
            res = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            st.write("glab commands:")
            st.code(res.stdout[:2000])
            if exec_now:
                import shutil
                if not shutil.which('glab'):
                    st.error("glab CLI not found in PATH")
                else:
                    created = 0
                    for line in res.stdout.splitlines():
                        if not line.strip():
                            continue
                        try:
                            subprocess.run(line, shell=True, check=True)
                            created += 1
                        except Exception as e:
                            st.error(f"glab create failed: {e}")
                    st.success(f"Created {created} GitLab issues")
            else:
                st.info("Copy the commands above to your terminal, or pipe to bash to execute.")
        except Exception as e:
            st.error(f"glab export error: {e}")
