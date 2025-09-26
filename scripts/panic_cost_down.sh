#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID=propulse-autonomax
REGION=us-central1
SERVICE=autonomax-api

# 1) Pause all cost-driving schedulers
for j in orders-nightly-backfill products-nightly-backfill syncShopifyDaily syncShortsDaily retrainAiOpsDaily; do
  gcloud scheduler jobs pause "$j" --location="$REGION" || true
done

# 2) Clamp Cloud Run to 0-1 instances and high concurrency
gcloud run services update "$SERVICE" \
  --region="$REGION" \
  --max-instances=1 \
  --concurrency=120 \
  --memory=512Mi \
  --timeout=120 \
  --no-cpu-throttling=false

echo "Panic cost-down applied."