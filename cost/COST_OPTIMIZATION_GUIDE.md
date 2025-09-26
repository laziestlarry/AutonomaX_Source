# Cost Optimization Guide (GCP)
- Prefer BigQuery load jobs + partitioned tables; avoid unbounded on-demand scans.
- Compact small files in GCS (parquet/ndjson) before load.
- Turn off min instances in Cloud Run outside trading hours if acceptable.
- Pub/Sub Lite for high-volume telemetry if > 1TB/mo.
- Looker Studio: use BI Engine cache for dashboards.
