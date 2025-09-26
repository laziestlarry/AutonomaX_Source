
import os, requests
from typing import List, Dict
def ollama_chat(messages: List[Dict[str,str]], model: str="llama3.1", temperature: float=0.2) -> str:
    host = os.getenv("OLLAMA_HOST","http://localhost:11434")
    url = f"{host}/api/chat"
    payload = {"model": model, "messages": messages, "options": {"temperature": temperature}}
    try:
        r = requests.post(url, json=payload, timeout=120); r.raise_for_status()
        data = r.json(); return data.get("message",{}).get("content","[ollama] no content")
    except Exception as e:
        return f"[ollama] error: {e}"
