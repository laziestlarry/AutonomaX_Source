# Performance Tuning Checklist
- Use uvicorn workers = CPU cores; enable uvloop.
- FastAPI response_model with orjson.
- Cache Shopify product metadata (ETag-aware) in Redis/Memory.
- Batch BigQuery inserts; prefer load jobs over per-row inserts.
- Precompute top-N recommendations; serve from cache, refresh async.
- Profile hot paths (py-spy/locust); watch p95 + tail latencies.
