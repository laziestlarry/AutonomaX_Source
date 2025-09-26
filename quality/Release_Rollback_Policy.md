# Release & Rollback Policy
- **Canary** at 10% traffic for 30 minutes with SLO watch.
- Auto-rollback triggers:
  - Error rate > 1% OR p95 > 2x baseline OR data freshness > SLA breach.
- Manual override allowed by Oncall SRE only.
- Keep N=3 previous images tagged for immediate rollback.
