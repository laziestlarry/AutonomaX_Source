import time
from typing import Dict, Any
from analytics.bq_client import ensure_events_table, write_event

def record_outcome(user_id: str, experiment: str, variant: str, outcome: Dict[str, Any]) -> Dict[str, Any]:
    ensure_events_table()
    payload = {"experiment": experiment, "user_id": user_id, "variant": variant, "outcome": outcome, "ts": int(time.time())}
    errs = write_event(source="experiments", topic="outcome", payload=payload, event_id=None)
    return {"status": "ok" if errs and errs[0].get("status") == "ok" else "error", "errors": errs}
