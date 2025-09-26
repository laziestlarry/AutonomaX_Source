#!/usr/bin/env bash
set -euo pipefail
if [[ -z "${CLOUD_RUN_URL:-}" ]]; then
  echo "Set CLOUD_RUN_URL (e.g., https://autonomax-api-XXXX.us-central1.run.app)"; exit 1
fi
OUT="revenue_sprint_lite_payoneer/delivery/output_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$OUT")"
echo "== HEALTH ==" | tee "$OUT"
curl -sS "$CLOUD_RUN_URL/health" | tee -a "$OUT"; echo | tee -a "$OUT"
echo "== BACKFILL: ORDERS ==" | tee -a "$OUT"
curl -sS -X POST "$CLOUD_RUN_URL/run/backfill/orders" | tee -a "$OUT"; echo | tee -a "$OUT"
echo "== BACKFILL: PRODUCTS ==" | tee -a "$OUT"
curl -sS -X POST "$CLOUD_RUN_URL/run/backfill/products" | tee -a "$OUT"; echo | tee -a "$OUT"
echo "Saved to $OUT"
