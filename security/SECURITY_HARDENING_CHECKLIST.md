# Security Hardening Checklist
- [ ] Least privilege for service accounts (BQ read/write, Storage limited to bucket prefixes).
- [ ] Secrets in Secret Manager; no plaintext in .env for prod.
- [ ] Webhook HMAC verify (Shopify) + 401 on fail.
- [ ] Rate limiting on /agent and webhooks (per IP / key).
- [ ] Dependency pinning & weekly CVE scan (GitHub Dependabot / pip-audit).
- [ ] OTEL traces with sampling; exclude PII fields from logs.
- [ ] Egress allowlist for API calls; deny-all default in Cloud Run.
- [ ] Production-only domains over HTTPS; HSTS enabled.
