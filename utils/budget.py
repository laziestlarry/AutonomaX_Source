
import os, json, time, pathlib
from typing import Literal
STORE = pathlib.Path("/tmp/budget_caps.json")
def _load():
    if STORE.exists():
        try: return json.loads(STORE.read_text())
        except Exception: return {}
    return {}
def _save(data): STORE.write_text(json.dumps(data))
def allow(provider: Literal["openai","ollama"], spent_usd: float=0.0, spent_tokens: int=0, daily_cap_usd: float=None, daily_cap_tokens: int=None) -> bool:
    day = time.strftime("%Y-%m-%d")
    data = _load()
    cur = data.get(day, {"openai_usd":0.0,"ollama_tokens":0})
    if daily_cap_usd is None:
        try: daily_cap_usd = float(os.getenv("OPENAI_DAILY_CAP_USD","50"))
        except Exception: daily_cap_usd = 50.0
    if daily_cap_tokens is None:
        try: daily_cap_tokens = int(os.getenv("OLLAMA_DAILY_CAP_TOKENS","500000"))
        except Exception: daily_cap_tokens = 500000
    if provider == "openai":
        if cur["openai_usd"] + spent_usd > daily_cap_usd: return False
        cur["openai_usd"] += spent_usd
    else:
        if cur["ollama_tokens"] + spent_tokens > daily_cap_tokens: return False
        cur["ollama_tokens"] += spent_tokens
    data[day] = cur; _save(data); return True
