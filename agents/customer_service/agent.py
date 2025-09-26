from __future__ import annotations

import re, json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

def _noop_enforce(text: str, policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"valid": True, "text": text, "violations": []}

try:
    from guardrails.policy_engine import enforce as _gr_enforce  # type: ignore
    _HAS_GUARDRAILS = True
except Exception:
    _gr_enforce = _noop_enforce
    _HAS_GUARDRAILS = False

try:
    import yaml
    _HAS_YAML = True
except Exception:
    yaml = None  # type: ignore
    _HAS_YAML = False

@dataclass
class Policy:
    enabled: bool = True
    use_guardrails_first: bool = True
    blocked_words: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=list)
    max_input_chars: Optional[int] = None
    mask_pii: bool = True
    pii_email: bool = True
    pii_phone: bool = True
    violation_response: str = "Üzgünüm, bu mesajda izin verilmeyen içerik tespit ettim: {violations}"

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Policy":
        return Policy(
            enabled=d.get("enabled", True),
            use_guardrails_first=d.get("use_guardrails_first", True),
            blocked_words=d.get("blocked_words", []) or [],
            blocked_patterns=d.get("blocked_patterns", []) or [],
            max_input_chars=d.get("max_input_chars"),
            mask_pii=d.get("mask_pii", True),
            pii_email=d.get("pii_email", True),
            pii_phone=d.get("pii_phone", True),
            violation_response=d.get("violation_response", "Üzgünüm, bu mesajda izin verilmeyen içerik tespit ettim: {violations}"),
        )

def load_policy(policy_path: Optional[str | Path]) -> Policy:
    if not policy_path: return Policy()
    p = Path(policy_path)
    if not p.exists() or not p.is_file() or not _HAS_YAML: return Policy()
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return Policy.from_dict(data) if isinstance(data, dict) else Policy()
    except Exception:
        return Policy()

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4})")

def _collect_local_violations(text: str, policy: Policy) -> List[str]:
    v: List[str] = []
    if policy.max_input_chars is not None and len(text) > policy.max_input_chars:
        v.append(f"max_input_chars>{policy.max_input_chars}")
    lw = text.lower()
    for w in policy.blocked_words:
        w=(w or "").strip()
        if w and w.lower() in lw: v.append(f"blocked_word:{w}")
    for pat in policy.blocked_patterns:
        try:
            if pat and re.search(pat, text, flags=re.IGNORECASE): v.append(f"blocked_pattern:{pat}")
        except re.error: continue
    return v

def _mask_pii_if_needed(text: str, policy: Policy) -> str:
    if not policy.mask_pii: return text
    t=text
    if policy.pii_email: t=_EMAIL_RE.sub("[email masked]", t)
    if policy.pii_phone: t=_PHONE_RE.sub("[phone masked]", t)
    return t

def validate_message(text: str, policy: Policy) -> Tuple[bool, List[str]]:
    allv: List[str] = []
    if policy.enabled and policy.use_guardrails_first and _HAS_GUARDRAILS:
        try:
            r=_gr_enforce(text, policy={"blocked_words": policy.blocked_words})
            if isinstance(r, dict) and not r.get("valid", True):
                v=r.get("violations") or []
                allv.extend([str(x) for x in (v if isinstance(v, list) else [v])])
        except Exception as e:
            allv.append(f"guardrails_error:{type(e).__name__}")
    allv.extend(_collect_local_violations(text, policy))
    return (len(allv)==0, allv)

def _default_llm(prompt: str, **_: Any) -> str:
    return "👋 Merhaba! Mesajınızı aldım. Mesaj özeti: " + (prompt[:400] + ("…" if len(prompt)>400 else ""))

@dataclass
class CustomerServiceAgent:
    policy_path: Optional[str | Path] = None
    llm: Callable[..., str] = _default_llm
    _policy: Policy = field(init=False, repr=False)
    def __post_init__(self): self._policy=load_policy(self.policy_path)
    def reload_policy(self): self._policy=load_policy(self.policy_path)
    @property
    def uses_guardrails(self)->bool: return _HAS_GUARDRAILS
    def handle(self, message: str, meta: Optional[Dict[str, Any]] = None, llm_kwargs: Optional[Dict[str, Any]] = None)->Dict[str, Any]:
        meta=meta or {}; llm_kwargs=llm_kwargs or {}
        ok,viol=validate_message(message, self._policy)
        if not ok:
            return {"ok":False,"reply":self._policy.violation_response.format(violations=", ".join(viol)),"violations":viol,"policy":self._policy.__dict__,"used_guardrails":self.uses_guardrails,"meta":meta}
        sanitized=_mask_pii_if_needed(message, self._policy)
        try: reply=self.llm(sanitized, **llm_kwargs)
        except Exception as e: reply=f"İşlem sırasında geçici bir hata oluştu. ({type(e).__name__})"
        return {"ok":True,"reply":reply,"violations":[],"policy":self._policy.__dict__,"used_guardrails":self.uses_guardrails,"meta":meta}

if __name__=="__main__":
    import sys
    msg=" ".join(sys.argv[1:]) or "Merhaba! Siparişim hakkında bilgi."
    agent=CustomerServiceAgent(policy_path="config/policies/customer_service.yml")
    print(json.dumps(agent.handle(msg), ensure_ascii=False, indent=2))
