#!/usr/bin/env bash
set -euo pipefail

# Cleanup cloud artifacts: revisions, GCR images, Cloud Build tarballs, lifecycles, logging retention
DRY_RUN=${DRY_RUN:-1}

PROJECT_ID=${PROJECT_ID:-propulse-autonomax}
REGION=${REGION:-us-central1}
SERVICE=${SERVICE:-autonomax-api}
IMAGE_REPO="gcr.io/${PROJECT_ID}/${SERVICE}"
CLOUD_BUILD_BUCKET="gs://${PROJECT_ID}_cloudbuild"
RAW_BUCKET=${RAW_BUCKET:-"gs://${PROJECT_ID}-raw"}
KEEP_REVISIONS=${KEEP_REVISIONS:-2}
IMAGE_AGE_DAYS=${IMAGE_AGE_DAYS:-14}
CB_AGE_DAYS=${CB_AGE_DAYS:-14}
LOG_RETENTION_DAYS=${LOG_RETENTION_DAYS:-30}

run_cmd() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[DRY-RUN] $*"
  else
    eval "$@"
  fi
}

echo "==> Ensure RAW bucket exists: ${RAW_BUCKET}"
if ! gsutil ls -b "${RAW_BUCKET}" >/dev/null 2>&1; then
  run_cmd "gsutil mb -p ${PROJECT_ID} -l ${REGION} -b on ${RAW_BUCKET}"
fi

echo "==> Set lifecycle on RAW bucket (delete after 14 days)"
cat > /tmp/lifecycle.json <<EOF
{
  "rule": [
    {"action": {"type": "Delete"}, "condition": {"age": 14}}
  ]
}
EOF
run_cmd "gsutil lifecycle set /tmp/lifecycle.json ${RAW_BUCKET}"

echo "==> Set lifecycle on Cloud Build bucket (delete sources older than ${CB_AGE_DAYS} days)"
cat > /tmp/cb_lifecycle.json <<EOF
{
  "rule": [
    {"action": {"type": "Delete"}, "condition": {"age": ${CB_AGE_DAYS}}}
  ]
}
EOF
run_cmd "gsutil lifecycle set /tmp/cb_lifecycle.json ${CLOUD_BUILD_BUCKET}"

echo "==> Trim Cloud Run revisions (keep newest ${KEEP_REVISIONS})"
REV_LIST=$(gcloud run revisions list --region="${REGION}" --service="${SERVICE}" --format="value(metadata.name)" | sort -r)
COUNT=0
for rev in $REV_LIST; do
  COUNT=$((COUNT+1))
  if [[ $COUNT -le ${KEEP_REVISIONS} ]]; then
    echo "Keeping: $rev"
  else
    TRAFFIC=$(gcloud run services describe "${SERVICE}" --region="${REGION}" --format="get(status.traffic[title(${rev})].percent)" 2>/dev/null || echo "")
    if [[ -z "$TRAFFIC" || "$TRAFFIC" == "0" ]]; then
      run_cmd "gcloud run revisions delete ${rev} --quiet --region=${REGION}"
    else
      echo "Skipping (has traffic): ${rev}"
    fi
  fi
done

echo "==> Delete untagged images older than ${IMAGE_AGE_DAYS} days in ${IMAGE_REPO}"
# List digests and filter by age
OLD_DIGESTS=$(gcloud container images list-tags "${IMAGE_REPO}"   --filter="NOT tags:* AND timestamp.datetime < -P${IMAGE_AGE_DAYS}D"   --format="get(digest)")
for d in $OLD_DIGESTS; do
  run_cmd "gcloud container images delete ${IMAGE_REPO}@${d} --quiet --force-delete-tags"
done

echo "==> Reduce Cloud Logging retention on _Default bucket to ${LOG_RETENTION_DAYS} days"
run_cmd "gcloud logging buckets update _Default --location=global --retention-days=${LOG_RETENTION_DAYS}"

echo "==> BigQuery sample: cap scan to 1GB"
echo "bq query --use_legacy_sql=false --maximum_bytes_billed=1073741824 'SELECT COUNT(*) FROM DATASET.orders_partitioned WHERE DATE(order_created_at)=DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)'"

echo "==> Cleanup complete. Re-run with DRY_RUN=0 to apply deletions/updates."
