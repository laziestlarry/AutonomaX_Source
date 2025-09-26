#!/usr/bin/env bash
set -euo pipefail

REGION="${REGION:-us-central1}"
TZ="${TZ:-Europe/Istanbul}"
SERVICE="${SERVICE:-autonomax-api}"
PROJECT="${GOOGLE_PROJECT_ID:-$(gcloud config get-value project)}"

SCHEDULER_SA="scheduler-invoker@${PROJECT}.iam.gserviceaccount.com"

# Ensure SA exists (skip if you already created it)
gcloud iam service-accounts create scheduler-invoker --display-name="Scheduler Invoker" || true

# Grant Cloud Run invoke
gcloud run services add-iam-policy-binding "$SERVICE" \
  --region "$REGION" \
  --member="serviceAccount:${SCHEDULER_SA}" \
  --role="roles/run.invoker"

CLOUD_RUN_URL="$(gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)')"

# Create jobs
gcloud scheduler jobs create http products-nightly-backfill \
  --location="$REGION" \
  --schedule="0 2 * * *" \
  --time-zone="$TZ" \
  --uri="${CLOUD_RUN_URL}/run/backfill/products" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --oidc-service-account-email="$SCHEDULER_SA" \
  --oidc-token-audience="$CLOUD_RUN_URL"

gcloud scheduler jobs create http orders-nightly-backfill \
  --location="$REGION" \
  --schedule="10 2 * * *" \
  --time-zone="$TZ" \
  --uri="${CLOUD_RUN_URL}/run/backfill/orders" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --oidc-service-account-email="$SCHEDULER_SA" \
  --oidc-token-audience="$CLOUD_RUN_URL"

echo "✅ Scheduler jobs created."