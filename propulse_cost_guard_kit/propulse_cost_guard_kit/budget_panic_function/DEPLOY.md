# Budget Panic Function (Gen1 HTTP or Gen2 Pub/Sub)

## Purpose
When a Billing Budget alert fires (Pub/Sub), this function:
- Pauses costly Cloud Scheduler jobs
- Clamps Cloud Run max scale and resources

## Deploy (Gen2, Pub/Sub)
```bash
PROJECT_ID=propulse-autonomax
REGION=us-central1
TOPIC=budget-alerts  # Use the Pub/Sub topic configured in your Budget

gcloud functions deploy budget-panic   --gen2   --region=$REGION   --runtime=python311   --entry-point=entrypoint   --source=.   --trigger-topic=$TOPIC   --set-env-vars=PROJECT_ID=$PROJECT_ID,REGION=$REGION,SERVICE=autonomax-api   --no-allow-unauthenticated
```

### Required IAM
Grant the function's service account:
- Cloud Scheduler Admin (to pause jobs)
- Cloud Run Admin (to patch service)
- Service Account Token Creator (if impersonation is used; not required in this sample)

Adjust least-privilege as desired (Jobs Pause + Run Services Update).
