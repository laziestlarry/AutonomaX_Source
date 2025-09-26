# Test Strategy
- **Unit**: agent policy pipeline, webhook HMAC, GA4 parser.
- **Contract**: JSON schemas for Shopify webhooks, stable between versions.
- **Integration**: BigQuery load jobs; idempotency and dedupe.
- **E2E**: Synthetic checkout events; verify dashboard KPIs.
- **Non-functional**: p95 latency under load, error budgets, backfill runtime.
CI gates: tests must pass + coverage >= 80% on critical modules.
