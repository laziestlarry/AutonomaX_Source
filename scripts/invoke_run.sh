#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID=${PROJECT_ID:-propulse-autonomax}
REGION=${REGION:-us-central1}
SERVICE_ACCOUNT="scheduler@$PROJECT_ID.iam.gserviceaccount.com"
CLOUD_RUN_URL=${CLOUD_RUN_URL:-"https://autonomax-api-71658389068.us-central1.run.app"}

ID_TOKEN=$(gcloud auth print-identity-token \
  --impersonate-service-account="$SERVICE_ACCOUNT" \
  --audiences="$CLOUD_RUN_URL")

curl -sS -H "Authorization: Bearer $ID_TOKEN" "$CLOUD_RUN_URL/health" | jq .
curl -sS -X POST -H "Authorization: Bearer $ID_TOKEN" "$CLOUD_RUN_URL/run/backfill/orders"   | jq .
curl -sS -X POST -H "Authorization: Bearer $ID_TOKEN" "$CLOUD_RUN_URL/run/backfill/products" | jq .