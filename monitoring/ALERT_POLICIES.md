# Alert Policies
- Sev1: API 5xx > 5% for 5m
- Sev2: p95 > 1000ms for 10m OR orders freshness > 120m
- Sev3: webhook failures > 1% over 30m
Channels: PagerDuty (Sev1/2), Slack #autonomax-ops (all)
