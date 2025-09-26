
import os, yaml, re
from functools import lru_cache
PROMPTS_PATH=os.getenv("PROMPTS_PATH","config/prompts.yaml")
@lru_cache(maxsize=1)
def _load():
    with open(PROMPTS_PATH,"r") as f: return yaml.safe_load(f)
def get_prompt(cat:str,name:str):
    return (_load().get(cat) or {}).get(name)
def render(cat:str,name:str,**kw)->str:
    p=get_prompt(cat,name) or {}
    body=p.get("body","")
    return re.sub(r"{(.*?)}", lambda m: str(kw.get(m.group(1), "{"+m.group(1)+"}")), body)
