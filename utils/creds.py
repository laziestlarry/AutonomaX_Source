
import os, json, pathlib
def ensure_ga_credentials_file()->str|None:
    raw=os.getenv("GA_CREDENTIALS_JSON")
    if not raw: return os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    try: data=json.loads(raw)
    except Exception:
        if os.path.exists(raw): os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=raw; return raw
        return None
    path=pathlib.Path("/tmp/ga_credentials.json"); path.write_text(json.dumps(data)); os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=str(path); return str(path)
