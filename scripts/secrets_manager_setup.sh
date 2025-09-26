
#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID="${GCP_PROJECT_ID:-propulse-autonomax}"
create_secret(){ local n="$1"; local v="$2"; echo -n "$v" | gcloud secrets create "$n" --replication-policy="automatic" --data-file=- || echo -n "$v" | gcloud secrets versions add "$n" --data-file=- ; }
for k in OPENAI_API_KEY SHOPIFY_ADMIN_TOKEN SHOPIFY_API_SECRET SLACK_WEBHOOK_URL GA_CREDENTIALS_JSON JIRA_API_TOKEN JIRA_EMAIL JIRA_BASE_URL; do
  if [[ -n "${!k:-}" ]]; then create_secret "$k" "${!k}"; fi
done
echo "Secrets ensured in project: $PROJECT_ID"
