from typing import Dict, Any
from utils.slack import send as slack_send

def upsert_contact(contact: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder CRM upsert; send to Slack for visibility
    slack_send("CRM upsert", level="info", context=contact)
    return {"status":"ok","id":contact.get("email") or contact.get("id")}

def record_action(action: Dict[str, Any]) -> Dict[str, Any]:
    slack_send("CRM action", level="info", context=action)
    return {"status":"ok"}
