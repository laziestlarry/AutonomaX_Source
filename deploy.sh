#!/usr/bin/env bash
set -euo pipefail

# Unified deploy helper.
# 1. Builds container images with Cloud Build (if configured).
# 2. Deploys API and dashboard services to Cloud Run.
# 3. Runs post-deploy bootstrap scripts.

PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
SERVICE_API="${SERVICE_API:-autonomax-api}"
SERVICE_DASH="${SERVICE_DASH:-autonomax-dashboard}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Set GCP_PROJECT_ID before running deploy.sh" >&2
  exit 1
fi

echo "Building containers via Cloud Build..."
gcloud builds submit --config cloudbuild.yaml .

echo "Deploying API to Cloud Run..."
gcloud run deploy "$SERVICE_API" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --image "gcr.io/$PROJECT_ID/$SERVICE_API:latest" \
  --platform managed \
  --allow-unauthenticated

echo "Deploying Dashboard to Cloud Run..."
gcloud run deploy "$SERVICE_DASH" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --image "gcr.io/$PROJECT_ID/$SERVICE_DASH:latest" \
  --platform managed \
  --allow-unauthenticated

echo "Running post-deploy bootstrap..."
bash ops/deploy_ship_and_bootstrap.sh

echo "Deploy complete."
