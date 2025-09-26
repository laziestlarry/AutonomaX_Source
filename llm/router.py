
from typing import List, Dict, Optional
import os, yaml
from llm.providers.openai_client import openai_chat
from llm.providers.ollama_client import ollama_chat
from utils.budget import allow

MODELS_CFG_PATH = os.getenv("MODELS_CONFIG_PATH", "config/models.yaml")
_DEFAULTS = {"provider":"openai","model":"gpt-4o-mini","temperature":0.3}

def _load_rules():
    try:
        with open(MODELS_CFG_PATH, "r") as f:
            data = yaml.safe_load(f) or {}
        defaults = data.get("defaults") or {}
        rules = data.get("rules") or []
        return defaults, rules
    except Exception:
        return _DEFAULTS, [
            {"match":["finance","executive","customer_service"],"provider":"openai","model":"gpt-4o-mini","temperature":0.2},
            {"match":["draft","brainstorm","bulk"],"provider":"ollama","model":"llama3.1","temperature":0.5},
        ]

def choose_backend(task_type: str) -> Dict[str, str | float]:
    defaults, rules = _load_rules()
    t = (task_type or "").lower()
    for rule in rules:
        if any(k in t for k in rule.get("match", [])):
            return {"provider": rule.get("provider", defaults.get("provider","openai")),
                    "model": rule.get("model", defaults.get("model","gpt-4o-mini")),
                    "temperature": rule.get("temperature", defaults.get("temperature",0.3))}
    return {"provider": defaults.get("provider","openai"),
            "model": defaults.get("model","gpt-4o-mini"),
            "temperature": defaults.get("temperature",0.3)}

def chat(task_type: str, messages: List[Dict[str, str]], model: Optional[str]=None, temperature: Optional[float]=None) -> str:
    if model:
        provider = "openai" if "gpt" in model else "ollama"; model_name = model
        temp = temperature if temperature is not None else 0.3
    else:
        choice = choose_backend(task_type); provider, model_name = choice["provider"], str(choice["model"]) ; temp = float(choice.get("temperature", 0.3))
    if provider == "openai":
        if not allow("openai", spent_usd=0.002): return "[budget] openai daily cap reached"
        return openai_chat(messages, model=model_name, temperature=temp)
    else:
        if not allow("ollama", spent_tokens=1000): return "[budget] ollama daily cap reached"
        return ollama_chat(messages, model=model_name, temperature=temp)
