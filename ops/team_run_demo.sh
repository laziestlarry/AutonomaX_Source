#!/usr/bin/env bash
set -euo pipefail

# team_run_demo.sh — Simple evidence of a "pro team" orchestration run
# Requires: export CLOUD_RUN_URL="https://<your-cloud-run-url>"

if [[ -z "${CLOUD_RUN_URL:-}" ]]; then
  echo "Set CLOUD_RUN_URL (e.g., https://autonomax-api-XXXX.us-central1.run.app)"; exit 1
fi

OUT_DIR="revenue_sprint_lite_payoneer/delivery"
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/team_run_$(date +%Y%m%d_%H%M%S).log"

echo "== TEAM RUN DEMO ==" | tee "$OUT"
echo "Service: $CLOUD_RUN_URL" | tee -a "$OUT"

step() { echo; echo "--- $* ---" | tee -a "$OUT"; }

step "/ready"
curl -sS "$CLOUD_RUN_URL/ready" | tee -a "$OUT"; echo | tee -a "$OUT"

step "Trigger backfills (orders/products)"
curl -sS -X POST "$CLOUD_RUN_URL/run/backfill/orders"   | tee -a "$OUT"; echo | tee -a "$OUT"
curl -sS -X POST "$CLOUD_RUN_URL/run/backfill/products" | tee -a "$OUT"; echo | tee -a "$OUT"

step "Lifecycle batch (sample users)"
PAYLOAD='{"users":[{"id":"demo-user-1","stage":"new"},{"id":"demo-user-2","stage":"churn_risk"}]}'
curl -sS -X POST -H "Content-Type: application/json" -d "$PAYLOAD" \
  "$CLOUD_RUN_URL/ops/lifecycle/batch" | tee -a "$OUT"; echo | tee -a "$OUT"

step "BI KPIs"
curl -sS "$CLOUD_RUN_URL/bi/kpis" | tee -a "$OUT"; echo | tee -a "$OUT"

step "Strategy Objectives"
curl -sS "$CLOUD_RUN_URL/strategy/objectives" | tee -a "$OUT"; echo | tee -a "$OUT"

step "Marketing Suggestions"
curl -sS -H 'Content-Type: application/json' -d '{"audience":"returning","budget":200,"channel":"email"}' \
  "$CLOUD_RUN_URL/marketing/campaigns/suggest" | tee -a "$OUT"; echo | tee -a "$OUT"

echo "== DONE. Evidence saved to $OUT =="

