from typing import Dict, Any, List

def campaign_suggestions(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    audience = context.get("audience", "returning")
    budget = float(context.get("budget", 100.0))
    channel = context.get("channel", "email")
    return [
        {
            "name": f"{channel.capitalize()} upsell to {audience}",
            "budget": budget,
            "kpi": "revenue",
            "cta": "Bundle & save",
            "copy_hint": "Limited-time bundle offer ends Sunday",
        },
        {
            "name": "UGC push",
            "budget": budget * 0.5,
            "kpi": "engagement",
            "cta": "Share your setup",
            "copy_hint": "Feature customers weekly on IG/TikTok",
        },
    ]

