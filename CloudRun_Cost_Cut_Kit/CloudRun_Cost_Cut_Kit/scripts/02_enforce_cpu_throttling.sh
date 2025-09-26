#!/usr/bin/env bash
set -euo pipefail

# Ensures CPU is not allocated while idle (aka "throttled CPU").
# Note: In Cloud Run, the default is throttled CPU. If you previously enabled always-on CPU,
# this will revert to throttled mode.

PROJECT_ID="${PROJECT_ID:-propulse-autonomax}"
REGION="${REGION:-us-central1}"
SERVICES=${SERVICES:-"autonomax-api autonomax-service autonomax-ops"}

gcloud config set project "$PROJECT_ID" >/dev/null

for SVC in $SERVICES; do
  echo "→ Enforcing throttled CPU for $SVC"
  # The flag below is a no-op on some configs where throttling is default; kept for clarity.
  gcloud run services update "$SVC" --region="$REGION" --cpu-throttling || true
done

echo "CPU throttling enforced where supported."
