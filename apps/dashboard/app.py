import os, json, time, pathlib, subprocess
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="AutonomaX – Executive Dashboard", layout="wide")
st.title("AutonomaX – Executive Dashboard")

api_url = st.text_input("API Base URL", value=os.getenv("API_URL", "https://autonomax-api-71658389068.us-central1.run.app"), help="Cloud Run URL or http://localhost:8080")

tab_status, tab_ops, tab_bi, tab_signals = st.tabs(["Status", "Ops", "BI/Strategy", "Signals"])

with tab_status:
    pid = os.getenv("GA4_PROPERTY_ID")
    if not pid or pid == "000000000":
        st.warning("GA4 not connected: `GA4_PROPERTY_ID` not set")
    else:
        st.success(f"GA4 connected • Property {pid}")

    # Metrics cards
    mcols = st.columns(4)
    try:
        bp_dir = pathlib.Path('data_room/blueprints')
        summaries = sorted(bp_dir.glob('summary_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
        tasks_cnt = 0
        if summaries:
            bp = json.loads(summaries[0].read_text())
            tasks_cnt = len(bp.get('tasks') or [])
    except Exception:
        tasks_cnt = 0
    try:
        inv = pathlib.Path('data_room/inventory/inventory.json')
        inv_cnt = (json.loads(inv.read_text()).get('count') or 0) if inv.exists() else 0
    except Exception:
        inv_cnt = 0
    try:
        cat = pathlib.Path('data_room/products/catalog.csv')
        prod_cnt = len(pd.read_csv(cat)) if cat.exists() else 0
    except Exception:
        prod_cnt = 0
    try:
        import glob
        logs = sorted(glob.glob('revenue_sprint_lite_payoneer/delivery/output_*.log'))
        ev_ok = 'Yes' if logs else 'No'
    except Exception:
        ev_ok = 'No'
    with mcols[0]:
        st.metric("Blueprint tasks", value=tasks_cnt)
    with mcols[1]:
        st.metric("Inventory items", value=inv_cnt)
    with mcols[2]:
        st.metric("Products selected", value=prod_cnt)
    with mcols[3]:
        st.metric("Evidence exists", value=ev_ok)

    cols = st.columns(3)
    with cols[0]:
        auto_fetch = st.checkbox("Auto-fetch status", value=False)
        if st.button("Check /health") or auto_fetch:
            try:
                r = requests.get(f"{api_url}/health", timeout=10)
                payload = r.json()
                st.success(f"/health {r.status_code}")
                st.code(json.dumps(payload, indent=2))
            except Exception as e:
                st.error(f"/health error: {e}")
    with cols[1]:
        if st.button("Check /ready") or auto_fetch:
            try:
                r = requests.get(f"{api_url}/ready", timeout=10)
                payload = r.json()
                st.success(f"/ready {r.status_code}")
                st.code(json.dumps(payload, indent=2))
            except Exception as e:
                st.error(f"/ready error: {e}")
    with cols[2]:
        if st.button("Fetch /admin/status") or auto_fetch:
            try:
                r = requests.get(f"{api_url}/admin/status", timeout=15)
                admin = r.json()
                st.code(json.dumps(admin, indent=2))
                # Color-coded quick chips
                ok = True
                if isinstance(admin, dict):
                    ok = ok and bool(admin.get('ready')) and admin.get('ready',{}).get('status') == 'ready' or True
                if ok:
                    st.success("Admin status OK")
                else:
                    st.warning("Admin status check has warnings")
            except Exception as e:
                st.error(f"/admin/status error: {e}")

    st.caption("Latest evidence log tail")
    try:
        import glob
        logs = sorted(glob.glob('revenue_sprint_lite_payoneer/delivery/output_*.log'))
        if logs:
            with open(logs[-1], 'r') as f:
                content = f.read()
            st.code(content[-2000:])
        else:
            st.caption("No evidence logs yet. Run ops/team_run_demo.sh.")
    except Exception:
        pass

    st.markdown("---")
    st.subheader("One-click Evidence Run")
    if st.button("Run team evidence now"):
        try:
            env = os.environ.copy()
            env['CLOUD_RUN_URL'] = api_url
            res = subprocess.run(["bash", "./ops/team_run_demo.sh"], capture_output=True, text=True, env=env, timeout=300)
            st.code(res.stdout[-2000:] if res.stdout else "(no stdout)")
            if res.stderr:
                st.caption("stderr:")
                st.code(res.stderr[-1000:])
        except Exception as e:
            st.error(f"Evidence run error: {e}")

with tab_ops:
    cols = st.columns(5)
    with cols[0]:
        if st.button("Trigger Orders Backfill"):
            try:
                r = requests.post(f"{api_url}/run/backfill/orders", timeout=30)
                st.info(f"orders backfill → {r.status_code}")
                st.code(json.dumps(r.json(), indent=2))
            except Exception as e:
                st.error(f"orders backfill error: {e}")
    with cols[1]:
        if st.button("Trigger Products Backfill"):
            try:
                r = requests.post(f"{api_url}/run/backfill/products", timeout=30)
                st.info(f"products backfill → {r.status_code}")
                st.code(json.dumps(r.json(), indent=2))
            except Exception as e:
                st.error(f"products backfill error: {e}")
    with cols[2]:
        if st.button("Run both backfills"):
            try:
                r1 = requests.post(f"{api_url}/run/backfill/orders", timeout=30)
                r2 = requests.post(f"{api_url}/run/backfill/products", timeout=30)
                st.info(f"orders → {r1.status_code}; products → {r2.status_code}")
            except Exception as e:
                st.error(f"backfills error: {e}")
    with cols[3]:
        cat = pathlib.Path('data_room/products/catalog.csv')
        if cat.exists():
            st.success("Products catalog ready")
            st.download_button("Download catalog.csv", data=cat.read_bytes(), file_name="catalog.csv")
        else:
            st.caption("No products catalog yet. Run pipeline.")
    with cols[4]:
        plan = pathlib.Path('data_room/products/plan.md')
        if plan.exists():
            st.success("Products plan ready")
            st.code(plan.read_text()[:1500])
        else:
            st.caption("No products plan yet. Run pipeline.")

    st.markdown("---")
    st.subheader("Products Overview")
    try:
        cat = pathlib.Path('data_room/products/catalog.csv')
        if cat.exists():
            dfp = pd.read_csv(cat)
            # Kind distribution
            if 'kind' in dfp.columns:
                kind_counts = dfp['kind'].value_counts()
                if not kind_counts.empty:
                    st.caption("By kind")
                    st.bar_chart(kind_counts.to_frame('count'))
                else:
                    st.caption("No kind data to chart.")
            # Tag distribution (explode)
            if 'tags' in dfp.columns:
                parts = []
                for t in dfp['tags'].dropna().tolist():
                    parts.extend([x.strip() for x in str(t).split(',') if x.strip()])
                if parts:
                    import collections
                    cnt = collections.Counter(parts)
                    top = pd.Series(dict(cnt.most_common(12)))
                    if not top.empty:
                        st.caption("Top tags")
                        st.bar_chart(top.to_frame('count'))
                else:
                    st.caption("No tags to chart.")
        else:
            st.caption("No catalog to summarize.")
    except Exception as e:
        st.error(f"Products overview error: {e}")

    st.markdown("---")
    st.subheader("Blueprint Batching")
    bcols = st.columns(3)
    with bcols[0]:
        batch_size = st.number_input("Batch size", min_value=1, max_value=200, value=20, step=1)
    with bcols[1]:
        if st.button("Append next batch"):
            try:
                res = subprocess.run(["python3","tools/batch_blueprint.py","--batch",str(batch_size)], capture_output=True, text=True, timeout=120)
                st.code(res.stdout or "(no stdout)")
                if res.stderr:
                    st.caption("stderr:")
                    st.code(res.stderr)
            except Exception as e:
                st.error(f"Batch append error: {e}")
    with bcols[2]:
        if st.button("Append all (loop)"):
            try:
                res = subprocess.run(["bash","./ops/batch_blueprint_all.sh",str(batch_size)], capture_output=True, text=True, timeout=600)
                st.code(res.stdout or "(no stdout)")
                if res.stderr:
                    st.caption("stderr:")
                    st.code(res.stderr)
            except Exception as e:
                st.error(f"Batch all error: {e}")

    st.markdown("---")
    st.subheader("Master Index Sprint")
    with st.expander("Path Fix Options (optional)"):
        old_prefix = st.text_input("Old prefix", value="")
        new_prefix = st.text_input("New prefix", value="")
    if st.button("Run Master Index Sprint"):
        try:
            env = os.environ.copy()
            if old_prefix:
                env['OLD_PREFIX'] = old_prefix
            if new_prefix:
                env['NEW_PREFIX'] = new_prefix
            res = subprocess.run(["bash","./ops/sprint_master_index.sh"], capture_output=True, text=True, timeout=1200, env=env)
            st.code(res.stdout or "(no stdout)")
            if res.stderr:
                st.caption("stderr:")
                st.code(res.stderr[-1500:])
        except Exception as e:
            st.error(f"Sprint run error: {e}")

    st.markdown("---")
    st.subheader("E-commerce Import (Shopify)")
    ecols = st.columns(3)
    with ecols[0]:
        imp_limit = st.number_input("Top N from catalog", min_value=1, max_value=500, value=20, step=1)
    with ecols[1]:
        dry_run = st.checkbox("Dry run (no creation)", value=False)
    with ecols[2]:
        if st.button("Import to Shopify"):
            try:
                # Build product JSON from catalog
                out_json = 'data_room/products/shopify_products.json'
                resb = subprocess.run(["python3", "tools/catalog_to_shopify_json.py", "--limit", str(imp_limit), "--out", out_json], capture_output=True, text=True, timeout=120)
                st.code(resb.stdout or "(no stdout)")
                # Post to API
                with open(out_json, 'r') as f:
                    payload = json.load(f)
                payload['dry_run'] = dry_run
                r = requests.post(f"{api_url}/ecom/shopify/import", json=payload, timeout=60)
                st.code(json.dumps(r.json(), indent=2))
                if r.status_code == 404:
                    st.warning("Endpoint not found. Redeploy the API so /ecom/shopify/import is available.")
            except Exception as e:
                st.error(f"Import error: {e}")

with tab_bi:
    cols2 = st.columns(3)
    with cols2[0]:
        if st.button("BI KPIs"):
            try:
                r = requests.get(f"{api_url}/bi/kpis", timeout=15)
                payload = r.json()
                st.code(json.dumps(payload, indent=2))
                fresh = payload.get('freshness') or {}
                if fresh.get('max_created_at'):
                    st.info(f"Data freshness: max_created_at={fresh.get('max_created_at')} • age_days={fresh.get('age_days')}")
            except Exception as e:
                st.error(f"/bi/kpis error: {e}")
    with cols2[1]:
        if st.button("Strategy Objectives"):
            try:
                r = requests.get(f"{api_url}/strategy/objectives", timeout=15)
                st.code(json.dumps(r.json(), indent=2))
            except Exception as e:
                st.error(f"/strategy/objectives error: {e}")
    with cols2[2]:
        if st.button("Marketing Suggestions"):
            try:
                payload = {"audience":"returning","budget":200,"channel":"email"}
                r = requests.post(f"{api_url}/marketing/campaigns/suggest", json=payload, timeout=20)
                st.code(json.dumps(r.json(), indent=2))
            except Exception as e:
                st.error(f"/marketing/campaigns/suggest error: {e}")

with tab_signals:
    st.caption("Quick latency probe")
    probe_count = st.slider("Probe count", min_value=3, max_value=20, value=5)
    latencies = []
    for _ in range(probe_count):
        t0 = time.time()
        try:
            r = requests.get(f"{api_url}/health", timeout=10)
        except Exception:
            r = None
        dt = (time.time() - t0) * 1000.0
        latencies.append(dt)
    lat_sorted = sorted(latencies)
    p50 = lat_sorted[int(0.5*len(lat_sorted))-1]
    p95 = lat_sorted[max(0,int(0.95*len(lat_sorted))-1)]
    st.write({'p50_ms': round(p50,1), 'p95_ms': round(p95,1), 'min_ms': round(min(latencies),1), 'max_ms': round(max(latencies),1), 'count': len(latencies)})
    # Persist history
    try:
        sig_dir = pathlib.Path('data_room/signals'); sig_dir.mkdir(parents=True, exist_ok=True)
        hist = sig_dir / 'latency.jsonl'
        import datetime as _dt
        ts = _dt.datetime.now(_dt.timezone.utc).isoformat()
        with open(hist, 'a') as f:
            f.write(json.dumps({'ts': ts, 'p50_ms': round(p50,1), 'p95_ms': round(p95,1)})+'\n')
        # Load recent history
        rows = []
        with open(hist, 'r') as f:
            for line in f.readlines()[-200:]:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
        if rows:
            st.caption("Latency history (recent)")
            dfh = pd.DataFrame(rows)
            dfh['ts'] = pd.to_datetime(dfh['ts'])
            dfh = dfh.sort_values('ts')
            st.line_chart(dfh.set_index('ts')[['p50_ms','p95_ms']])
    except Exception:
        pass

st.subheader("Next Steps")
st.markdown("""
1. Fill `.env` with GA4/Shopify/GCP settings.
2. Register Shopify webhooks and run nightly backfills.
3. Use the buttons above to verify live API endpoints.
""")
