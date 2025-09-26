#!/usr/bin/env bash
set -euo pipefail

# Build a product payload from catalog and import via Cloud Run API
# Usage:
#   CLOUD_RUN_URL=https://autonomax-api-... ./ops/shopify_import_from_catalog.sh [limit]

LIMIT=${1:-20}
OUT_JSON="data_room/products/shopify_products.json"

if [[ ! -f data_room/products/catalog.csv ]]; then
  echo "catalog.csv not found. Run: ./ops/pipeline_local.sh or ./ops/prepare_products.sh"
fi

python3 tools/catalog_to_shopify_json.py --limit "$LIMIT" --out "$OUT_JSON"

if [[ -z "${CLOUD_RUN_URL:-}" ]]; then
  echo "Set CLOUD_RUN_URL to your API URL (export CLOUD_RUN_URL=...)"; exit 2
fi

RESP=$(curl -sS -X POST -H "Content-Type: application/json" \
  -d @"$OUT_JSON" \
  "$CLOUD_RUN_URL/ecom/shopify/import")

if command -v jq >/dev/null 2>&1; then echo "$RESP" | jq .; else echo "$RESP"; fi

echo "==> Import attempted; see response above. If you see 'Not Found', redeploy the API so /ecom/shopify/import is available."
