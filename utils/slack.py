
import os, json, requests
from datetime import datetime
SLACK_WEBHOOK_URL=os.getenv("SLACK_WEBHOOK_URL")
def send(message:str, level:str="info", context:dict|None=None):
    if not SLACK_WEBHOOK_URL: return
    color={"info":"#7FB3D5","warn":"#F5B041","error":"#C0392B"}.get(level,"#7FB3D5")
    payload={"attachments":[{"color":color,"title":f"AutonomaX • {level.upper()}","text":message,"footer":"autonoma-x","ts":int(datetime.utcnow().timestamp())}]}
    if context: payload["attachments"][0]["fields"]=[{"title":k,"value":str(v),"short":True} for k,v in context.items()]
    try: requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type":"application/json"}, timeout=10)
    except Exception: pass
