#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID=propulse-autonomax
REGION=us-central1
SERVICE=autonomax-api

# Restore modest but safe scale
gcloud run services update "$SERVICE" \
  --region="$REGION" \
  --max-instances=2 \
  --concurrency=80 \
  --memory=512Mi \
  --timeout=300 \
  --no-cpu-throttling=false

# Resume only the essentials
for j in orders-nightly-backfill products-nightly-backfill; do
  gcloud scheduler jobs resume "$j" --location="$REGION" || true
done

echo "Restored to guarded defaults."