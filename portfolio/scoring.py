from typing import List, Dict, Any

def ice_score(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored = []
    for it in items:
        impact = float(it.get('impact', 1))
        confidence = float(it.get('confidence', 0.5))
        ease = float(it.get('ease', 0.5))
        score = impact * confidence * ease
        out = dict(it)
        out['ice'] = round(score, 3)
        scored.append(out)
    scored.sort(key=lambda x: x['ice'], reverse=True)
    return scored
