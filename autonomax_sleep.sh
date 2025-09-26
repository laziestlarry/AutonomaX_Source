#!/usr/bin/env bash
set -euo pipefail

PROJECT="propulse-autonomax"
REGION="us-central1"
SERVICE="autonomax-api"

echo "== SLEEP MODE for $PROJECT / $SERVICE =="

gcloud config set project "$PROJECT" >/dev/null

echo "[1/4] Pause Cloud Scheduler jobs (stop daily invocations)"
for job in orders-nightly-backfill products-nightly-backfill retrainAiOpsDaily syncShopifyDaily syncShortsDaily weeklyStrategyLoop; do
  echo " - Pausing $job"
  gcloud scheduler jobs pause "$job" --location="$REGION" || echo "   (warn) couldn't pause $job"
done

echo "[2/4] Minimize Cloud Run (idle=0 cost; prevent bursts)"
# High concurrency, tiny CPU/RAM, single instance cap, shorter timeout, min-instances 0
gcloud run services update "$SERVICE" \
  --region="$REGION" \
  --platform=managed \
  --cpu=100m \
  --memory=128Mi \
  --concurrency=250 \
  --max-instances=1 \
  --timeout=30 \
  --min-instances=0 || echo "   (warn) update flags not fully supported on this gcloud - continue"

echo "[3/4] Require auth (block accidental public traffic)"
gcloud run services update "$SERVICE" \
  --region="$REGION" \
  --platform=managed \
  --no-allow-unauthenticated || echo "   (warn) couldn't flip auth; check IAM/permissions"

echo "[4/4] (Optional) Disable Vision API to avoid surprise charges"
if gcloud services list --enabled --project="$PROJECT" | grep -q "vision.googleapis.com"; then
  gcloud services disable vision.googleapis.com --project="$PROJECT" || echo "   (warn) couldn't disable vision"
fi

echo
echo "== Sleep completed. Verifying... =="
gcloud scheduler jobs list --location="$REGION"
gcloud run services describe "$SERVICE" --region="$REGION" --platform=managed | sed -n '1,140p'
echo "OK: Jobs paused, Cloud Run minimized & auth-gated."