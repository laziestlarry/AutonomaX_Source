import hashlib
import json
import os
from typing import Any, Dict, Optional

from google.cloud import pubsub_v1

PUBSUB_ENABLED = os.getenv("PUBSUB_ENABLED", "false").lower() == "true"
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "autonx-events")


def _project_id() -> Optional[str]:
    pid = os.getenv("GCP_PROJECT_ID")
    return pid.strip() if pid else None


def event_id_for(payload: Dict[str, Any], topic: str) -> str:
    raw = json.dumps({"topic": topic, "payload": payload}, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def publish_event(payload: Dict[str, Any], topic: str) -> str | None:
    if not PUBSUB_ENABLED:
        return None
    project = _project_id()
    if not project:
        return None
    publisher = pubsub_v1.PublisherClient()
    path = publisher.topic_path(project, PUBSUB_TOPIC)
    eid = event_id_for(payload, topic)
    future = publisher.publish(
        path,
        data=json.dumps(payload).encode("utf-8"),
        event_id=eid,
        topic=topic,
        source="shopify",
    )
    return future.result(timeout=30)
