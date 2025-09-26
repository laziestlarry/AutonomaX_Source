
#!/usr/bin/env bash
set -euo pipefail
: "${GCP_PROJECT_ID:?set GCP_PROJECT_ID}"
: "${GCP_REGION:=us-central1}"
SERVICE=autonoma-x-ai
IMAGE_STABLE="gcr.io/${GCP_PROJECT_ID}/autonoma-x-ai:stable"
IMAGE_CANARY="gcr.io/${GCP_PROJECT_ID}/autonoma-x-ai:canary"
gcloud builds submit --tag "$IMAGE_STABLE"
gcloud builds submit --tag "$IMAGE_CANARY"
gcloud run deploy $SERVICE --image "$IMAGE_STABLE" --region "$GCP_REGION" --allow-unauthenticated   --set-env-vars ENV=prod   --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest,SHOPIFY_ADMIN_TOKEN=SHOPIFY_ADMIN_TOKEN:latest,SHOPIFY_API_SECRET=SHOPIFY_API_SECRET:latest,SLACK_WEBHOOK_URL=SLACK_WEBHOOK_URL:latest,GA_CREDENTIALS_JSON=GA_CREDENTIALS_JSON:latest,JIRA_API_TOKEN=JIRA_API_TOKEN:latest,JIRA_EMAIL=JIRA_EMAIL:latest,JIRA_BASE_URL=JIRA_BASE_URL:latest
gcloud run services update-traffic $SERVICE --region "$GCP_REGION" --to-revisions latest=95
gcloud run deploy $SERVICE --image "$IMAGE_CANARY" --region "$GCP_REGION" --allow-unauthenticated --no-traffic
gcloud run services update-traffic $SERVICE --region "$GCP_REGION" --to-revisions latest=5
echo "Blue/Green deployed with 95/5 traffic split."
