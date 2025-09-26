#!/usr/bin/env bash
set -euo pipefail
# Reduce unbounded CPU by tightening timeouts (requests and idle).

PROJECT_ID="${PROJECT_ID:-propulse-autonomax}"
REGION="${REGION:-us-central1}"
SERVICES=${SERVICES:-"autonomax-api autonomax-service autonomax-ops"}

# Request/response timeouts (adjust to your workloads)
TIMEOUT="${TIMEOUT:-120}"        # seconds
# Startup/shutdown grace periods can be tuned too if needed.

gcloud config set project "$PROJECT_ID" >/dev/null

for SVC in $SERVICES; do
  echo "→ Setting request timeout=$TIMEOUT for $SVC"
  gcloud run services update "$SVC" --region="$REGION" --timeout="$TIMEOUT"
done

echo "Done. Keep timeouts tight to avoid stuck CPUs."
