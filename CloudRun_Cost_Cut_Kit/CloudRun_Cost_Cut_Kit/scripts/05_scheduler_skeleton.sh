#!/usr/bin/env bash
set -euo pipefail

# Skeleton to move heavy tasks to Cloud Run Jobs + Cloud Scheduler.
# 1) Build a Cloud Run Job image that runs your heavy task then exits.
# 2) Deploy the job once.
# 3) Schedule it with Cloud Scheduler (cron).

PROJECT_ID="${PROJECT_ID:-propulse-autonomax}"
REGION="${REGION:-us-central1}"
JOB_NAME="${JOB_NAME:-autonomax-nightly-products}"
IMAGE="${IMAGE:-us-central1-docker.pkg.dev/$PROJECT_ID/jobs/autonomax-products:latest}"
SVC_ACCOUNT="${SVC_ACCOUNT:-autonomax-jobs@$PROJECT_ID.iam.gserviceaccount.com}"
SCHEDULE="${SCHEDULE:-0 3 * * *}"  # 03:00 region time daily

echo "Create Artifact Registry repo if missing:"
echo "  gcloud artifacts repositories create jobs --repository-format=docker --location=$REGION || true"
echo
echo "Build & push image (example):"
echo "  gcloud builds submit --tag $IMAGE"
echo
echo "Deploy the Cloud Run Job:"
echo "  gcloud run jobs deploy $JOB_NAME --image=$IMAGE --region=$REGION --service-account=$SVC_ACCOUNT --max-retries=1 --tasks=1"
echo
echo "Create a Scheduler trigger:"
echo "  gcloud scheduler jobs create http $JOB_NAME \"
echo "    --schedule=\"$SCHEDULE\" \"
echo "    --http-method=POST \"
echo "    --uri=\"https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run\" \"
echo "    --oauth-service-account-email=\"$SVC_ACCOUNT\" \"
echo "    --oauth-token-scope=\"https://www.googleapis.com/auth/cloud-platform\" \"
echo "    --location=$REGION"
