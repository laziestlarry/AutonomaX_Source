# Propulse Cost Guard Kit

This kit gives you **hard guardrails** so infra never outruns revenue.

## Contents
- `ops/panic_cost_down.sh` — pause costly jobs + clamp Cloud Run (panic switch)
- `ops/restore_cost_defaults.sh` — restore safe defaults and resume essential jobs
- `ops/cleanup_cloud_artifacts.sh` — trim old revisions/images, set bucket lifecycles, logging retention (DRY-RUN by default)
- `ops/invoke_run.sh` — call private Cloud Run via Scheduler SA impersonation
- `bigquery/01_create_dataset.sql` — creates dataset `propulse-autonomax.shopify_analytics`
- `bigquery/02_create_orders_table.sql`, `03_create_products_table.sql` — partitioned+clustered skeleton tables
- `budget_panic_function/` — Pub/Sub-triggered Cloud Function to auto-apply panic on Budget alerts
- `.dockerignore.sample` — to reduce build context size

## Quick Start
```bash
# 1) Panic if needed
bash ops/panic_cost_down.sh

# 2) Restore when safe
bash ops/restore_cost_defaults.sh

# 3) Cleanup (preview, then apply)
DRY_RUN=1 bash ops/cleanup_cloud_artifacts.sh
DRY_RUN=0 bash ops/cleanup_cloud_artifacts.sh

# 4) Bootstrap BigQuery (adjust locations/dataset names if needed)
bq query --use_legacy_sql=false < bigquery/01_create_dataset.sql
bq query --use_legacy_sql=false < bigquery/02_create_orders_table.sql
bq query --use_legacy_sql=false < bigquery/03_create_products_table.sql
```

## Notes
- Adjust **locations** (US/EU) and dataset names to your standards.
- If you use **Artifact Registry** instead of GCR, tweak the cleanup script to use `gcloud artifacts` commands.
- The Cloud Function uses Cloud Run Admin & Scheduler Admin APIs to patch resources with least external deps.
