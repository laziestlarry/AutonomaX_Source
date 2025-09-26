# Data Freshness SLA
- GA4 export latency target: <= 4h
- Shopify orders backfill: incremental every 15m, full integrity check nightly
- Freshness monitors:
  - `orders` table latest timestamp < 30m (warn), < 60m (page), > 120m (sev2)
- Owner: Analytics Lead
