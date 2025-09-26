from typing import List, Dict, Any

def kpis(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    # events: {type:'signup|cancel|renew', amount:float}
    mrr = 0.0
    signups = cancels = renewals = 0
    for e in events:
        t = (e.get('type') or '').lower()
        if t == 'signup': signups += 1; mrr += float(e.get('amount') or 0)
        if t == 'renew': renewals += 1; mrr += float(e.get('amount') or 0)
        if t == 'cancel': cancels += 1
    churn_rate = cancels / max(1, signups + renewals)
    return {"mrr": round(mrr,2), "signups": signups, "renewals": renewals, "cancels": cancels, "churn_rate": round(churn_rate,4)}
