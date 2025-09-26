# Incident Response Runbook
1. Declare severity (sev1/2/3) and page on-call.
2. Stabilize: scale up Cloud Run, enable rate-limits.
3. Triage: error dashboards + recent deploy diff.
4. Rollback if SLOs still failing after 10m.
5. Comms: status channel + customer note if sev1.
6. Postmortem within 48h; action items tracked in Jira.
