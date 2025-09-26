
#!/usr/bin/env bash
set -euo pipefail
IMAGE=gcr.io/propulse-autonomax/autonomax-ai-starter
REGION=${GCP_REGION:-us-central1}
gcloud builds submit --tag $IMAGE
gcloud run deploy autonoma-x-ai   --image $IMAGE   --region $REGION   --allow-unauthenticated   --platform managed   --set-env-vars ENV=prod   --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest,SHOPIFY_ADMIN_TOKEN=SHOPIFY_ADMIN_TOKEN:latest,SHOPIFY_API_SECRET=SHOPIFY_API_SECRET:latest,SLACK_WEBHOOK_URL=SLACK_WEBHOOK_URL:latest,GA_CREDENTIALS_JSON=GA_CREDENTIALS_JSON:latest
