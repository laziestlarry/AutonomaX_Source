from typing import List, Dict, Any
from utils.email import send_email
from utils.slack import send as slack_send
from utils.crm import record_action

def execute_actions(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    for a in actions or []:
        t = (a.get("type") or "").lower()
        if t == "email":
            res = send_email(a.get("to") or a.get("email") or "user@example.com", a.get("subject",""), a.get("body",""))
        elif t in ("inapp","nudge","winback","cross_sell","referral","survey"):
            res = record_action(a)
        else:
            slack_send("Unknown growth action", level="warn", context=a)
            res = {"status":"unknown"}
        results.append({"action": a, "result": res})
    return {"executed": len(results), "results": results}
