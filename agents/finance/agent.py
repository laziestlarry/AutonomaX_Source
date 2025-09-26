from typing import Dict, Any
from llm.router import chat

class FinanceAgent:
    def __init__(self):
        pass

    def reconcile_invoices(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        _ = payload
        text = chat("finance", [{"role":"user","content":"Execute reconcile_invoices with provided payload"}])
        return {"status":"ok","note": text[:200]}

    def forecast_cashflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        _ = payload
        text = chat("finance", [{"role":"user","content":"Execute forecast_cashflow with provided payload"}])
        return {"status":"ok","note": text[:200]}
