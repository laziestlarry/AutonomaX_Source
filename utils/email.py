import os, json
import requests
from typing import Optional

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM = os.getenv("SENDGRID_FROM", "noreply@example.com")
EMAIL_WEBHOOK_URL = os.getenv("EMAIL_WEBHOOK_URL")

def send_email(to: str, subject: str, body: str) -> dict:
    """Minimal email sender.
    Priority: webhook → SendGrid → no-op.
    """
    if EMAIL_WEBHOOK_URL:
        try:
            r = requests.post(EMAIL_WEBHOOK_URL, json={"to": to, "subject": subject, "body": body}, timeout=10)
            r.raise_for_status()
            return {"status":"queued","provider":"webhook"}
        except Exception as e:
            return {"status":"error","provider":"webhook","error":str(e)}
    if SENDGRID_API_KEY:
        try:
            r = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"},
                data=json.dumps({
                    "from": {"email": SENDGRID_FROM},
                    "personalizations": [{"to": [{"email": to}], "subject": subject}],
                    "content": [{"type": "text/plain", "value": body}]
                }), timeout=10)
            if r.status_code in (200, 202):
                return {"status":"queued","provider":"sendgrid"}
            return {"status":"error","provider":"sendgrid","error":r.text}
        except Exception as e:
            return {"status":"error","provider":"sendgrid","error":str(e)}
    return {"status":"noop","provider":"none"}
