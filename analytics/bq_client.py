import json
import os
from typing import Optional

from google.cloud import bigquery


def _project_id() -> Optional[str]:
    pid = os.getenv("GCP_PROJECT_ID")
    return pid.strip() if pid else None


def client() -> Optional[bigquery.Client]:
    project = _project_id()
    if not project:
        return None
    return bigquery.Client(project=project)


def ensure_events_table() -> bool:
    client_obj = client()
    if not client_obj:
        return False
    dataset = os.getenv("BQ_DATASET", "autonomax")
    table = os.getenv("BQ_TABLE_EVENTS", "events_raw")
    ds_ref = bigquery.Dataset(f"{client_obj.project}.{dataset}")
    try:
        client_obj.get_dataset(ds_ref)
    except Exception:
        client_obj.create_dataset(ds_ref, exists_ok=True)
    schema = [
        bigquery.SchemaField("ts", "TIMESTAMP"),
        bigquery.SchemaField("event_id", "STRING"),
        bigquery.SchemaField("source", "STRING"),
        bigquery.SchemaField("topic", "STRING"),
        bigquery.SchemaField("payload", "STRING"),
    ]
    table_ref = f"{client_obj.project}.{dataset}.{table}"
    try:
        client_obj.get_table(table_ref)
    except Exception:
        client_obj.create_table(bigquery.Table(table_ref, schema=schema))
    return True


def write_event(source, topic, payload, event_id: str | None = None):
    client_obj = client()
    if not client_obj:
        return [{"status": "noop", "reason": "missing_gcp_project"}]
    dataset = os.getenv("BQ_DATASET", "autonomax")
    table = os.getenv("BQ_TABLE_EVENTS", "events_raw")
    table_ref = f"{client_obj.project}.{dataset}.{table}"
    row = {
        "ts": None,
        "event_id": event_id,
        "source": source,
        "topic": topic,
        "payload": json.dumps(payload),
    }
    errs = client_obj.insert_rows_json(table_ref, [row], row_ids=[event_id] if event_id else None)
    return errs if errs else [{"status": "ok"}]
