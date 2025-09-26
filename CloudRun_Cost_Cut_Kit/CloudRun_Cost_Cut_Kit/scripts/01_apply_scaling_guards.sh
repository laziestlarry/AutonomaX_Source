#!/usr/bin/env bash
set -euo pipefail

# === EDIT ME ===
PROJECT_ID="${PROJECT_ID:-propulse-autonomax}"
REGION="${REGION:-us-central1}"
# List your Cloud Run services here (space-separated)
SERVICES=${SERVICES:-"autonomax-api autonomax-service autonomax-ops"}

# Safe caps (adjust as needed)
MAX_INSTANCES="${MAX_INSTANCES:-5}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
CONCURRENCY="${CONCURRENCY:-80}"   # higher concurrency -> fewer instances
CPU="${CPU:-1}"                    # vCPU per instance
MEMORY="${MEMORY:-512Mi}"          # memory per instance

gcloud config set project "$PROJECT_ID" >/dev/null

echo "Applying scaling guards in project=$PROJECT_ID region=$REGION"
for SVC in $SERVICES; do
  echo "→ Updating $SVC"
  gcloud run services update "$SVC"     --region="$REGION"     --max-instances="$MAX_INSTANCES"     --min-instances="$MIN_INSTANCES"     --concurrency="$CONCURRENCY"     --cpu="$CPU"     --memory="$MEMORY"
done

echo "Done. Verify with: gcloud run services describe <service> --region=$REGION | sed -n '1,120p'"
