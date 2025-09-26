
#!/usr/bin/env bash
set -euo pipefail
: "${GCP_PROJECT_ID:?set GCP_PROJECT_ID}"
: "${PUBSUB_TOPIC:=autonx-events}"
: "${SERVICE_URL:?set SERVICE_URL (Cloud Run URL)}"
gcloud pubsub topics create "$PUBSUB_TOPIC" || true
gcloud pubsub subscriptions create autonx-events-sub   --topic="$PUBSUB_TOPIC"   --push-endpoint="${SERVICE_URL}/pubsub/push"   --push-auth-service-account="autonx-pubsub@${GCP_PROJECT_ID}.iam.gserviceaccount.com" || true
echo "Pub/Sub topic and push subscription ready."
