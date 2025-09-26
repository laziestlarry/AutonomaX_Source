from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from portfolio.scoring import ice_score

BLUEPRINT_DIR = Path("data_room/blueprints")
TEAM_FILE = Path("config/team.json")


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _latest_blueprint_summary() -> Optional[Dict[str, Any]]:
    if not BLUEPRINT_DIR.exists():
        return None
    summaries = sorted(
        BLUEPRINT_DIR.glob("summary_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for summary in summaries:
        data = _load_json(summary)
        if data:
            data.setdefault("_file", str(summary))
            return data
    return None


def project_plan() -> Dict[str, Any]:
    summary = _latest_blueprint_summary()
    if not summary:
        return {
            "status": "missing",
            "generated_at": None,
            "label": None,
            "phases": [],
            "milestones": [],
            "counts": {"total": 0, "selected": 0},
        }
    return {
        "status": "ok",
        "generated_at": summary.get("generated_at"),
        "label": summary.get("label"),
        "phases": summary.get("phases", []),
        "milestones": summary.get("selected", []),
        "counts": {
            "total": summary.get("count_total", 0),
            "selected": summary.get("count_selected", 0),
        },
        "source_file": summary.get("_file"),
    }


def team_roster() -> Dict[str, Any]:
    if TEAM_FILE.exists():
        data = _load_json(TEAM_FILE) or {}
    else:
        data = {}
    members = data.get("members") or [
        {
            "name": "Eng Ops",
            "role": "Engineering",
            "focus": "Stabilize APIs & automations",
            "status": "available",
        },
        {
            "name": "Growth Lead",
            "role": "Growth",
            "focus": "Lifecycle, paid pilots, referrals",
            "status": "available",
        },
        {
            "name": "Customer Partner",
            "role": "Client Success",
            "focus": "Evidence runs, fulfillment, insights",
            "status": "available",
        },
    ]
    updated_at = data.get("updated_at")
    if not updated_at:
        updated_at = datetime.utcnow().isoformat() + "Z"
    return {"status": "ok", "updated_at": updated_at, "members": members}


def _blueprint_to_portfolio_items(summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for entry in summary.get("selected", []) or []:
        score = float(entry.get("score") or 50.0)
        impact = max(0.1, min(1.0, score / 100.0))
        confidence = 0.5 + (0.1 if entry.get("url") else 0.0)
        ease = 0.5 + (0.1 if entry.get("path") else 0.0)
        items.append(
            {
                "name": entry.get("name"),
                "impact": round(impact, 3),
                "confidence": round(confidence, 3),
                "ease": round(ease, 3),
                "tags": entry.get("tags", ""),
                "summary": entry.get("desc"),
                "path": entry.get("path"),
                "url": entry.get("url"),
            }
        )
    return items


def portfolio_highlights(limit: int = 5) -> List[Dict[str, Any]]:
    summary = _latest_blueprint_summary()
    if not summary:
        return []
    items = _blueprint_to_portfolio_items(summary)
    if not items:
        return []
    scored = ice_score(items)
    return scored[: max(0, limit)]
