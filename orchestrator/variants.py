
import os, yaml, random
CFG = {"canary_percent": 5, "enable_metrics": True}
try: CFG.update(yaml.safe_load(open("config/canary.yaml")) or {})
except Exception: pass
def choose_variant() -> str:
    p = float(CFG.get("canary_percent", 5)); return "canary" if random.random() < (p/100.0) else "stable"
def record_outcome(*args, **kwargs): pass
