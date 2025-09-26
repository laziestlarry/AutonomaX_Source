#!/usr/bin/env bash
set -euo pipefail
# Lightweight views (best effort) for CPU and (if billing export exists) cost.
# For full cost, enable Billing Export to BigQuery and use a SQL, or FinOps tool.

PROJECT_ID="${PROJECT_ID:-propulse-autonomax}"
REGION="${REGION:-us-central1}"
SVC="${1:-autonomax-api}"
WINDOW="${WINDOW:-1h}"

echo "CPU usage (approx) for service=$SVC window=$WINDOW"
gcloud monitoring time-series list   --project="$PROJECT_ID"   --filter='metric.type="run.googleapis.com/container/cpu/usage_time" AND resource.label."service_name"="'$SVC'"'   --align=ALIGN_SUM   --alignment_period="$WINDOW"   --format="table(points[0].value.doubleValue, metric.labels.instance_id, resource.labels.revision_name)"   --limit=10 || echo "Metric fetch may need permissions or correct metric names."

echo
echo "Tip: Enable Billing Export to BigQuery for precise TRY cost queries."
