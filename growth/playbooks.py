import hashlib, time
from typing import Dict, Any, List

def _hash(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)

def lifecycle_actions(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    stage = user.get("stage","unknown").lower()
    plan: List[Dict[str, Any]] = []
    uid = str(user.get("id","anon"))
    now = int(time.time())
    if stage in ("new","onboarding"):
        plan.append({"type":"email","template":"welcome_series","user_id":uid,"send_at":now})
        plan.append({"type":"inapp","message":"First-purchase incentive","user_id":uid})
    if stage in ("active","engaged"):
        plan.append({"type":"cross_sell","offer":"related_products","user_id":uid})
        plan.append({"type":"referral","incentive":"10% credit","user_id":uid})
    if stage in ("churn_risk","inactive"):
        plan.append({"type":"winback","offer":"reactivation_discount","user_id":uid})
        plan.append({"type":"survey","template":"churn_reasons","user_id":uid})
    if not plan:
        plan.append({"type":"nudge","message":"Check-in","user_id":uid})
    return plan

def referral_campaign(seed: str, tiers: int = 3) -> Dict[str, Any]:
    base = _hash(seed) % 1000
    rewards = [5, 10, 25]
    return {"code": f"REF-{base:03d}", "rewards": rewards[:max(1, min(tiers, len(rewards)))]}
