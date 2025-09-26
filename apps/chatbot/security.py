
from fastapi import Request, HTTPException
from typing import List, Optional, Set
import uuid


def _extract_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        first_hop = forwarded.split(",")[0].strip()
        if first_hop:
            return first_hop
    client = request.client
    return client.host if client else None


def ip_allowlist_middleware(allowed: List[str]):
    allowed_set = set(allowed or [])

    async def middleware(request: Request, call_next):
        if not allowed_set:
            return await call_next(request)
        client_ip = _extract_client_ip(request)
        if client_ip not in allowed_set:
            raise HTTPException(status_code=403, detail="IP not allowed")
        return await call_next(request)

    return middleware

def api_key_middleware(required_key: Optional[str], exempt_paths: Optional[Set[str]] = None):
    required = (required_key or "").strip()
    exempt = set(exempt_paths or set())
    async def middleware(request: Request, call_next):
        if not required:
            return await call_next(request)
        if request.url.path in exempt:
            return await call_next(request)
        key = request.headers.get("x-api-key") or request.query_params.get("api_key")
        if key != required:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return await call_next(request)
    return middleware

def request_id_middleware():
    async def middleware(request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["x-request-id"] = rid
        return response
    return middleware
