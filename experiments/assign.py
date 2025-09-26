import hashlib, json, time
from typing import Dict, Any
from analytics.bq_client import ensure_events_table, write_event

def assign(user_id: str, experiment: str, ratio_a: float = 0.5) -> Dict[str, Any]:
    h = int(hashlib.sha256(f"{experiment}:{user_id}".encode("utf-8")).hexdigest(), 16)
    bucket = (h % 10000) / 10000.0
    variant = 'A' if bucket < ratio_a else 'B'
    ensure_events_table()
    payload = {"experiment": experiment, "user_id": user_id, "variant": variant, "ts": int(time.time())}
    write_event(source="experiments", topic="assignment", payload=payload, event_id=None)
    return payload
