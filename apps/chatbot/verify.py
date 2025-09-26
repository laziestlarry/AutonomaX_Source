
import os, hmac, hashlib, base64

def _get_secret_bytes() -> bytes:
    # Prefer webhook secret if present; fallback to legacy API secret var
    s = os.getenv("SHOPIFY_WEBHOOK_SECRET") or os.getenv("SHOPIFY_API_SECRET") or ""
    return s.encode("utf-8")

def verify_hmac(raw: bytes, signature: str) -> bool:
    secret = _get_secret_bytes()
    if not secret or not signature:
        return False
    digest = hmac.new(secret, raw, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(digest).decode("utf-8"), signature)
