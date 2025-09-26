from typing import Dict, Any, List

def current_objectives() -> Dict[str, Any]:
    return {
        "company": "AutonomaX",
        "quarter": "Q3",
        "objectives": [
            {
                "name": "Stabilize data pipelines & SLA",
                "key_results": [
                    {"name": "<1% failed jobs/week", "target": 0.99},
                    {"name": "P95 < 400ms /health", "target": 0.4},
                ],
            },
            {
                "name": "Grow recurring revenue",
                "key_results": [
                    {"name": "+20% 28d revenue", "target": 1.2},
                    {"name": "+10% retention D30", "target": 1.1},
                ],
            },
        ],
    }

