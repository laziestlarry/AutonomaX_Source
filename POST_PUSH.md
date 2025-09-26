
git remote -v          # should show origin → https://github.com/laziestlarry/AutonomaX_AI_Integration_Starter.git
git status             # on branch main, nothing to commit
git log --oneline -1   # shows last commit

2. GitHub Repo Settings

 Add Actions secrets for CI/CD:

GCP_PROJECT_ID → e.g. propulse-autonomax

GCP_REGION → e.g. us-central1

GOOGLE_CREDENTIALS → full JSON of a service account with Cloud Run, Artifact Registry, and BQ perms

 Optional: SHOPIFY_API_KEY, SHOPIFY_API_SECRET, OPENAI_API_KEY for test runs in CI.

3. Cloud Scheduler Jobs

The upgrade pack included scheduling/cloud_scheduler_jobs.json.

Deploy them:

jq -c '.[]' scheduling/cloud_scheduler_jobs.json | while read -r job; do
  NAME=$(echo "$job" | jq -r '.name')
  URI=$(echo "$job" | jq -r '.httpTarget.uri')
  CRON=$(echo "$job" | jq -r '.schedule')
  SA=$(echo "$job" | jq -r '.httpTarget.oidcToken.serviceAccountEmail')
  gcloud scheduler jobs create http "$NAME" \
    --schedule="$CRON" \
    --uri="$URI" \
    --http-method=POST \
    --oidc-service-account-email="$SA" \
    --location="$GCP_REGION" || true
done

4. Looker Studio

Import looker/theme.json as a custom theme.

Connect BQ dataset (autonomax_analytics) with tables orders, products, events.

Apply theme for consistent branding.

5. Release Policy

Canary deploy: shift 5% traffic → bake 30 min → promote 100% if SLOs green.

Rollback: bash scripts/deploy_blue_green.sh --rollback.

6. Operations

SLOs defined in monitoring/SLOs.yaml.

Alerts in monitoring/ALERT_POLICIES.md.

Incident runbook: ops/INCIDENT_RESPONSE_RUNBOOK.md.