from typing import Dict, Any
from llm.router import chat

class HRAgent:
    def __init__(self):
        pass

    def screen_candidates(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        _ = payload
        text = chat("hr", [{"role":"user","content":"Execute screen_candidates with provided payload"}])
        return {"status":"ok","note": text[:200]}

    def onboard_employee(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        _ = payload
        text = chat("hr", [{"role":"user","content":"Execute onboard_employee with provided payload"}])
        return {"status":"ok","note": text[:200]}
