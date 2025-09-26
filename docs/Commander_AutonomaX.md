# Commander_AutonomaX — Team Control Center

This adds a simple, agent-ready intake → review → plan loop.

Quick start
- Intake inventory (local only):
  - `./ops/intake_inventory.sh --root . --label local`
- Open control center:
  - `streamlit run apps/commander/app.py`
- Evidence team run:
  - `export CLOUD_RUN_URL="https://<your-run-url>"`
  - `./ops/team_run_demo.sh`

What it does
- Scans folders, builds an inventory and matrix for quick sorting.
- Lets you tag items and assemble a tasks.csv for teams (research, analysis, dev, PM, advisor).
- Keeps artifacts under `data_room/inventory/` for sharing.

Where to scale next
- Add ingestion of external drives or GDrive by mounting paths and re-running intake.
- Hook BI KPIs to BigQuery; add scoring to prioritize high-value assets.
- Add “agents” to auto-suggest tags and tasks (LLM or heuristics).

