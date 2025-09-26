#!/usr/bin/env bash
set -euo pipefail

# Restore guarded defaults
PROJECT_ID=${PROJECT_ID:-propulse-autonomax}
REGION=${REGION:-us-central1}
SERVICE=${SERVICE:-autonomax-api}

echo "==> Restoring Cloud Run guarded defaults"
gcloud run services update "$SERVICE"   --region="$REGION"   --max-instances=2   --concurrency=80   --memory=512Mi   --timeout=300   --cpu-throttling

echo "==> Resuming essential scheduler jobs"
for j in orders-nightly-backfill products-nightly-backfill; do
  if gcloud scheduler jobs describe "$j" --location="$REGION" >/dev/null 2>&1; then
    gcloud scheduler jobs resume "$j" --location="$REGION" || true
    echo "Resumed: $j"
  fi
done

echo "==> Restore complete."
