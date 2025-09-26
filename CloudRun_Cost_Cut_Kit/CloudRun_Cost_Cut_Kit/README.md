# Cloud Run Cost-Cut Kit (TRY-first)

This kit helps immediately reduce **Google Cloud Run** CPU spend in **us-central1** for your AutonomaX / ProPulse services. 
Currency context: your billing shows **Turkish Lira (TRY)** totals. Targets below optimize usage, not exchange rates.

## What this kit does
1) Caps scaling (`--max-instances`) and raises per-instance concurrency.
2) Ensures no idle cost (`--min-instances=0`).
3) Enforces CPU to be used **only when handling requests** (throttled) where applicable.
4) Adds Monitoring alerts for CPU spikes and daily cost anomalies (template JSON).
5) Moves expensive recurring jobs to Cloud Scheduler (skeleton).

> Safe to run multiple times. Edit env vars at the top of each script as needed.

## Quick Start
```bash
# 0) Auth & Project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 1) Apply safe instance & concurrency caps
bash scripts/01_apply_scaling_guards.sh

# 2) Enforce throttled CPU (no idle CPU billing)
bash scripts/02_enforce_cpu_throttling.sh

# 3) OPTIONAL: Move long jobs to scheduler skeleton (edit first)
bash scripts/05_scheduler_skeleton.sh

# 4) Create Monitoring alerts (edit notification channels first)
gcloud monitoring policies create --policy-from-file=monitoring/policy_cpu_spike.json
gcloud monitoring policies create --policy-from-file=monitoring/policy_daily_cost_anomaly.json
```

## Notes (TRY-specific)
- Your sample line item shows **TRY 2,827.22** for ~6.51M vCPU-seconds. This kit reduces waste regardless of currency.
- If workloads are bursty, throttled CPU + zero min instances usually yields the largest savings.
- If you have long **background** tasks, prefer **Cloud Run Jobs** triggered by **Cloud Scheduler**, not always-on services.

## Files
- `scripts/01_apply_scaling_guards.sh` — set `max-instances`, `min-instances`, `concurrency`, `cpu/mem`
- `scripts/02_enforce_cpu_throttling.sh` — ensure CPU is not allocated while idle (where supported)
- `scripts/03_show_live_cost_and_cpu.sh` — quick CLI to inspect CPU/cost (Aggregation via Cloud Monitoring / Billing export if available)
- `scripts/04_set_egress_timeout_and_timeouts.sh` — tighten timeouts to avoid stuck CPUs
- `scripts/05_scheduler_skeleton.sh` — example to move heavy tasks to Cloud Scheduler + Cloud Run Jobs
- `monitoring/policy_cpu_spike.json` — alert if CPU time spikes above baseline
- `monitoring/policy_daily_cost_anomaly.json` — (template) daily cost anomaly alert (requires Billing Export to BigQuery or FinOps tool)
- `dashboards/README.md` — hints to build a CPU & Cost dashboard

## Rollback
Re-run `01_apply_scaling_guards.sh` with previous values (or increase limits) if throughput suffers.

