#!/usr/bin/env bash
set -euo pipefail

# Panic cost-down: pause costly jobs + clamp Cloud Run scale
PROJECT_ID=${PROJECT_ID:-propulse-autonomax}
REGION=${REGION:-us-central1}
SERVICE=${SERVICE:-autonomax-api}

echo "==> Pausing high-cost scheduler jobs (if they exist)"
for j in orders-nightly-backfill products-nightly-backfill syncShopifyDaily syncShortsDaily retrainAiOpsDaily weeklyStrategyLoop; do
  if gcloud scheduler jobs describe "$j" --location="$REGION" >/dev/null 2>&1; then
    gcloud scheduler jobs pause "$j" --location="$REGION" || true
    echo "Paused: $j"
  fi
done

echo "==> Clamping Cloud Run scale"
gcloud run services update "$SERVICE"   --region="$REGION"   --max-instances=1   --concurrency=120   --memory=512Mi   --timeout=120   --cpu-throttling

echo "==> Panic cost-down applied."
