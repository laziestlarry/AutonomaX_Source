#!/usr/bin/env bash
set -euo pipefail

# deploy_ship_and_bootstrap.sh — One-shot push, deploy, schedule, and bootstrap ops
# - Builds and deploys Cloud Run (cost-optimized flags via Cloud Build config)
# - Ensures Scheduler OIDC SA + job upserts
# - Optionally seeds Secret Manager from local env vars
# - Runs smoke checks and triggers backfills; saves evidence under lander/delivery
# - Produces initial BI/strategy/marketing artifacts for stakeholders

PROJECT_DEFAULT="propulse-autonomax"
REGION_DEFAULT="us-central1"
SERVICE_DEFAULT="autonomax-api"
IMAGE_DEFAULT="gcr.io/${PROJECT_DEFAULT}/autonomax-api"

PROJECT="${PROJECT:-$PROJECT_DEFAULT}"
REGION="${REGION:-$REGION_DEFAULT}"
SERVICE="${SERVICE:-$SERVICE_DEFAULT}"
IMAGE="${IMAGE:-gcr.io/${PROJECT}/autonomax-api}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DELIVERY_DIR="${ROOT_DIR}/revenue_sprint_lite_payoneer/delivery"
mkdir -p "$DELIVERY_DIR"

require() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1"; exit 1; }; }
require gcloud; require jq; require curl

echo "==> Using project: $PROJECT  region: $REGION  service: $SERVICE"
gcloud config set project "$PROJECT" >/dev/null

ensure_secret() {
  local name="$1"; shift
  local value="${1:-}"
  if [[ -z "$value" ]]; then
    echo "[secrets] Skipping $name (no value in env)"; return 0
  fi
  if ! gcloud secrets describe "$name" --project="$PROJECT" >/dev/null 2>&1; then
    echo "[secrets] Creating secret $name"
    gcloud secrets create "$name" --replication-policy=automatic --project="$PROJECT" >/dev/null
  fi
  echo "[secrets] Adding new version to $name"
  printf "%s" "$value" | gcloud secrets versions add "$name" --project="$PROJECT" --data-file=- >/dev/null
}

echo "==> (Optional) Seeding Secret Manager from environment"
# Export env vars before running to seed; otherwise these are skipped safely
ensure_secret OPENAI_API_KEY "${OPENAI_API_KEY:-}"
ensure_secret SHOPIFY_ADMIN_TOKEN "${SHOPIFY_ADMIN_TOKEN:-}"
ensure_secret SHOPIFY_API_SECRET "${SHOPIFY_API_SECRET:-}"
ensure_secret SLACK_WEBHOOK_URL "${SLACK_WEBHOOK_URL:-}"
# GA_CREDENTIALS_JSON should be full JSON; base64 is also acceptable. Provide JSON in env to seed.
ensure_secret GA_CREDENTIALS_JSON "${GA_CREDENTIALS_JSON:-}"

echo "==> Building and deploying via Cloud Build (cost-optimized flags)"
gcloud builds submit \
  --project="$PROJECT" \
  --config "$ROOT_DIR/infra/gcp/cloudbuild.yaml" \
  --substitutions=_SERVICE_NAME="$SERVICE",_REGION="$REGION",_IMAGE="$IMAGE"

echo "==> Resolving Cloud Run URL"
CLOUD_RUN_URL="${CLOUD_RUN_URL:-}"
if [[ -z "$CLOUD_RUN_URL" ]]; then
  CLOUD_RUN_URL=$(gcloud run services describe "$SERVICE" --platform=managed --region="$REGION" --format='value(status.url)')
fi
if [[ -z "$CLOUD_RUN_URL" ]]; then echo "Could not resolve service URL"; exit 1; fi
echo "Service URL: $CLOUD_RUN_URL"

echo "==> Ensuring Scheduler OIDC service account and invoker permission"
SA_EMAIL="scheduler@${PROJECT}.iam.gserviceaccount.com"
gcloud iam service-accounts create scheduler --project="$PROJECT" --display-name="Scheduler OIDC" || true
gcloud run services add-iam-policy-binding "$SERVICE" \
  --project="$PROJECT" --region="$REGION" \
  --member="serviceAccount:${SA_EMAIL}" --role=roles/run.invoker || true

echo "==> Upserting Cloud Scheduler jobs from scheduling/cloud_scheduler_jobs.json"
JOBS_FILE="$ROOT_DIR/scheduling/cloud_scheduler_jobs.json"
if [[ ! -f "$JOBS_FILE" ]]; then echo "Missing $JOBS_FILE"; exit 1; fi

# Replace placeholder hosts with actual if any remain (idempotent)
TMP_JOBS=$(mktemp)
# macOS/BSD sed needs -E for extended regex; replace any prior service host with current URL
sed -E "s|https://autonomax-api-[^/]+\\.run\\.app|$CLOUD_RUN_URL|g" "$JOBS_FILE" > "$TMP_JOBS"

jq -c '.[]' "$TMP_JOBS" | while read -r job; do
  NAME=$(echo "$job" | jq -r '.name')
  CRON=$(echo "$job" | jq -r '.schedule')
  URI=$(echo "$job" | jq -r '.httpTarget.uri')
  METHOD=$(echo "$job" | jq -r '.httpTarget.httpMethod')
  SA=$(echo "$job" | jq -r '.httpTarget.oidcToken.serviceAccountEmail')
  BODY=$(echo "$job" | jq -r '.httpTarget.body // empty')
  # Build header flags without relying on Bash 4+ mapfile (macOS ships Bash 3.2)
  HDRS=$(echo "$job" | jq -r '.httpTarget.headers // {} | to_entries | map("--headers=\(.key):\(.value)") | join(" ")')
  if gcloud scheduler jobs describe "$NAME" --location="$REGION" >/dev/null 2>&1; then
    # shellcheck disable=SC2086
    gcloud scheduler jobs update http "$NAME" --location="$REGION" --schedule="$CRON" --uri="$URI" --http-method="$METHOD" --oidc-service-account-email="$SA" $HDRS ${BODY:+--message-body=$BODY}
  else
    # shellcheck disable=SC2086
    gcloud scheduler jobs create http "$NAME" --location="$REGION" --schedule="$CRON" --uri="$URI" --http-method="$METHOD" --oidc-service-account-email="$SA" $HDRS ${BODY:+--message-body=$BODY}
  fi
done
rm -f "$TMP_JOBS"

echo "==> Smoke: health & ready"
curl -fsS "$CLOUD_RUN_URL/health" | tee "$DELIVERY_DIR/health.json" >/dev/null
curl -fsS "$CLOUD_RUN_URL/ready" | tee "$DELIVERY_DIR/ready.json" >/dev/null

echo "==> Trigger backfills (orders, products) and capture evidence"
OUT="$DELIVERY_DIR/output_$(date +%Y%m%d_%H%M%S).log"
{
  echo "== HEALTH =="; curl -sS "$CLOUD_RUN_URL/health"; echo
  echo "== BACKFILL: ORDERS =="; curl -sS -X POST "$CLOUD_RUN_URL/run/backfill/orders"; echo
  echo "== BACKFILL: PRODUCTS =="; curl -sS -X POST "$CLOUD_RUN_URL/run/backfill/products"; echo
} | tee "$OUT" >/dev/null
echo "Saved evidence: $OUT"

echo "==> Generate stakeholder artifacts (BI/strategy/marketing)"
curl -fsS "$CLOUD_RUN_URL/bi/kpis" | tee "$DELIVERY_DIR/bi_kpis.json" >/dev/null || true
curl -fsS "$CLOUD_RUN_URL/strategy/objectives" | tee "$DELIVERY_DIR/strategy_objectives.json" >/dev/null || true
curl -fsS -H 'Content-Type: application/json' -d '{"audience":"returning","budget":200,"channel":"email"}' \
  "$CLOUD_RUN_URL/marketing/campaigns/suggest" | tee "$DELIVERY_DIR/marketing_suggestions.json" >/dev/null || true

echo "==> Optional local accelerators"
if [[ -x "$ROOT_DIR/local_tools/generate_images.sh" ]]; then
  echo "Running local image generation accelerator"
  "$ROOT_DIR/local_tools/generate_images.sh" "$DELIVERY_DIR" || true
fi
if [[ -x "$ROOT_DIR/local_tools/sync_partner_feed.sh" ]]; then
  echo "Syncing partner feeds"
  "$ROOT_DIR/local_tools/sync_partner_feed.sh" || true
fi

echo "==> Done. Next:"
echo "- Review $DELIVERY_DIR outputs and email client using revenue_sprint_lite_payoneer/delivery/template.md"
echo "- Monitor Cloud Run logs; adjust max-instances if demand increases"
echo "- Pause schedulers off-hours to reduce cost if needed"

echo "==> Artifacts summary"
echo "- Service URL: $CLOUD_RUN_URL"
if [[ -f "$DELIVERY_DIR/health.json" ]]; then echo "  $DELIVERY_DIR/health.json"; fi
if [[ -f "$DELIVERY_DIR/ready.json" ]]; then echo "  $DELIVERY_DIR/ready.json"; fi
latest_log=$(ls -1t "$DELIVERY_DIR"/output_*.log 2>/dev/null | head -n1 || true)
if [[ -n "${latest_log:-}" ]]; then
  echo "  Latest delivery log: $latest_log"
fi
for f in bi_kpis.json strategy_objectives.json marketing_suggestions.json; do
  if [[ -f "$DELIVERY_DIR/$f" ]]; then echo "  $DELIVERY_DIR/$f"; fi
done
