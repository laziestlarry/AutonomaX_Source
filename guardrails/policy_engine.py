from typing import Any, Dict, List

DEFAULT_POLICY: Dict[str, Any] = {"blocked_words": []}

def enforce(text: str, policy: Dict[str, Any] | None = None) -> Dict[str, Any]:
    p = policy or DEFAULT_POLICY
    blocked: List[str] = []
    for w in p.get("blocked_words", []):
        if w and w.lower() in text.lower():
            blocked.append(w)
    return {"valid": len(blocked) == 0, "text": text, "violations": blocked}
