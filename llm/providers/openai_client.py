
import os
from typing import List, Dict
from openai import OpenAI

def openai_chat(messages: List[Dict[str,str]], model: str="gpt-4o-mini", temperature: float=0.2) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[openai] missing OPENAI_API_KEY"
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
        return resp.choices[0].message.content
    except Exception as e:
        return f"[openai] error: {e}"
