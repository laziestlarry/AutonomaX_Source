# Pub/Sub-triggered function: on budget alert, pause schedulers and clamp Cloud Run
import os
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth import default

PROJECT_ID = os.getenv("PROJECT_ID", "propulse-autonomax")
REGION = os.getenv("REGION", "us-central1")
SERVICE = os.getenv("SERVICE", "autonomax-api")

JOBS = [
    "orders-nightly-backfill",
    "products-nightly-backfill",
    "syncShopifyDaily",
    "syncShortsDaily",
    "retrainAiOpsDaily",
    "weeklyStrategyLoop",
]

def _clients():
    creds, _ = default(scopes=[
        'https://www.googleapis.com/auth/cloud-platform'
    ])
    sch = build("cloudscheduler", "v1", credentials=creds, cache_discovery=False)
    run = build("run", "v1", credentials=creds, cache_discovery=False)  # Admin API v1 for Cloud Run (fully managed)
    return sch, run

def _pause_jobs(sch):
    for j in JOBS:
        name = f"projects/{PROJECT_ID}/locations/{REGION}/jobs/{j}"
        try:
            sch.projects().locations().jobs().pause(name=name, body={}).execute()
        except Exception as e:
            # ignore if not exists
            pass

def _clamp_cloud_run(run):
    # Patch Cloud Run service annotations for maxScale, concurrency, resources
    name = f"namespaces/{PROJECT_ID}/services/{SERVICE}"
    # Cloud Run Admin API uses Knative-style resources; patch template metadata annotations
    body = {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "autoscaling.knative.dev/maxScale": "1"
                    }
                },
                "spec": {
                    "containerConcurrency": 120,
                    "containers": [{
                        "name": SERVICE,
                        "resources": {
                            "limits": {"memory": "512Mi"}
                        }
                    }],
                    "timeoutSeconds": 120
                }
            }
        }
    }
    run.namespaces().services().patch(name=name, body=body).execute()

def entrypoint(event, context):
    # event is Pub/Sub message; we don't parse it here (budget threshold logic is handled by Budget alerts).
    sch, run = _clients()
    _pause_jobs(sch)
    _clamp_cloud_run(run)
    return "panic applied"
