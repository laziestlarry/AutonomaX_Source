#!/usr/bin/env bash
set -euo pipefail

# diagnose.sh — quick health + logs snapshot for Cloud Run service

PROJECT=${PROJECT:-propulse-autonomax}
REGION=${REGION:-us-central1}
SERVICE=${SERVICE:-autonomax-api}

echo "== Project: $PROJECT  Region: $REGION  Service: $SERVICE =="
gcloud config set project "$PROJECT" >/dev/null

echo "== Resolve service URL =="
URL=$(gcloud run services describe "$SERVICE" --platform=managed --region="$REGION" --format='value(status.url)' || true)
echo "URL: ${URL:-<unknown>}"

if [[ -n "$URL" ]]; then
  echo "== /health =="
  curl -fsS "$URL/health" || echo "Health request failed"
  echo
  echo "== /ready =="
  curl -fsS "$URL/ready" || echo "Ready request failed"
  echo
fi

echo "== Recent log severities (last 24h) =="
gcloud logging read \
  --freshness=24h \
  --limit=200 \
  --format='table(severity, timestamp, resource.labels.revision_name)' \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="'"$SERVICE"'"' | sed -n '1,40p'

echo "== Recent ERROR logs (last 24h, top 50) =="
gcloud logging read \
  --freshness=24h \
  --limit=50 \
  --format='value(timestamp, ": ", textPayload)' \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="'"$SERVICE"'" AND severity>=ERROR' | sed -n '1,200p'

echo "== Scheduler jobs in region $REGION =="
gcloud scheduler jobs list --location="$REGION" --format='table(name, schedule, httpTarget.uri)'

echo "== Done =="

