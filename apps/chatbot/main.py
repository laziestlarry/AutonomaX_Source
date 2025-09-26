import os, json, subprocess, sys
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from orchestrator.orchestrator import Orchestrator
from apps.chatbot.verify import verify_hmac
from apps.chatbot.security import ip_allowlist_middleware, api_key_middleware, request_id_middleware
from utils.otel import setup_otel
from utils.pubsub import publish_event, event_id_for, PUBSUB_ENABLED
from analytics.bq_client import ensure_events_table, write_event
from utils.slack import send as slack_send
from growth.playbooks import lifecycle_actions, referral_campaign
from growth.actions import execute_actions
from monetization.pricing import suggest_price
from monetization.subscriptions import kpis as sub_kpis
from experiments.assign import assign as exp_assign
from experiments.outcomes import record_outcome as exp_record
from portfolio.scoring import ice_score
from analytics.anomaly_detector import run_check as anomaly_check
from analytics.bi import current_kpis, top_insights
from growth.marketing import campaign_suggestions
from strategy.okrs import current_objectives
from shopify.admin.products import create_product
from mission.insights import project_plan, team_roster, portfolio_highlights

APP = FastAPI(title="AutonomaX API", version="11.1")
app = APP  # alias for runners expecting `app`
orch = Orchestrator()

@APP.get("/")
def root():
    return {"ok": True, "see": "/health"}

@APP.get("/health")
def health():
    return {"status": "ok", "env": os.getenv("ENV","dev")}

# Optional: enable OpenTelemetry and IP allowlist when configured
if os.getenv("OTEL_ENABLED", "false").lower() == "true":
    try:
        setup_otel(APP)
    except Exception:
        pass

allowlist = os.getenv("IP_ALLOWLIST", "").strip()
if allowlist:
    try:
        allowed_ips = [ip.strip() for ip in allowlist.split(",") if ip.strip()]
        APP.middleware("http")(ip_allowlist_middleware(allowed_ips))
    except Exception:
        pass

# Always set request id middleware
APP.middleware("http")(request_id_middleware())

# Optional API key enforcement (exempt health and ready)
api_key = os.getenv("API_KEY", "").strip()
# Exempt health/ready and scheduler-invoked endpoints to allow Cloud Run OIDC-only auth
_exempt_paths = {
    "/", "/health", "/ready",
    "/run/backfill/orders", "/run/backfill/products",
    "/cron/backfill/orders", "/cron/backfill/products",
    "/ops/lifecycle/batch", "/cron/anomaly-check",
}
APP.middleware("http")(api_key_middleware(api_key, exempt_paths=_exempt_paths))

@APP.get("/ready")
def ready():
    env = os.getenv("ENV","dev").lower()
    checks = {"env": env}
    try:
        if os.getenv("PUBSUB_ENABLED","false").lower()=="true":
            checks["pubsub"] = bool(os.getenv("GCP_PROJECT_ID"))
        if os.getenv("USE_OPENAI","false").lower()=="true":
            checks["openai_key"] = bool(os.getenv("OPENAI_API_KEY"))
        if os.getenv("GA4_PROPERTY_ID"):
            checks["ga4"] = True
    except Exception:
        pass
    return {"status":"ready","checks":checks}

@APP.post("/webhooks/orders/create")
async def orders_create(req: Request):
    # Require HMAC in non-dev environments; accept both WEBHOOK and API secrets
    env = os.getenv("ENV", "dev").lower()
    body = await req.body()
    sig = req.headers.get("x-shopify-hmac-sha256")
    if env != "dev":
        if not sig or not verify_hmac(body, sig):
            raise HTTPException(status_code=401, detail="Invalid HMAC")
    payload=json.loads(body.decode() or "{}")
    # Enqueue event to Pub/Sub if enabled
    evt = {"type":"orders.create","payload": payload}
    topic = "orders.create"
    msg_id = None
    try:
        msg_id = publish_event(evt, topic=topic)
    except Exception as e:
        slack_send(f"Pub/Sub publish error: {e}", level="warn")
        msg_id = None
    # Fallback to BigQuery if Pub/Sub is disabled or failed
    if not msg_id:
        try:
            ensure_events_table()
            eid = event_id_for(evt, topic)
            errs = write_event(source="shopify", topic=topic, payload=evt, event_id=eid)
            if errs and isinstance(errs, list) and errs[0].get("status") == "ok":
                msg_id = eid
            else:
                slack_send(f"BQ write_event errors: {errs}", level="warn")
        except Exception as e:
            slack_send(f"BQ fallback error: {e}", level="error")
    return {"ok": True, "got": payload.get("id"), "message_id": msg_id, "pubsub_enabled": PUBSUB_ENABLED}

@APP.post("/agent")
async def agent_endpoint(payload: dict):
    msg = payload.get("message","")
    return JSONResponse(orch.handle(msg))

# Growth & Monetization routes

@APP.post("/growth/lifecycle")
async def growth_lifecycle(user: dict):
    return {"actions": lifecycle_actions(user)}

@APP.get("/growth/referral")
async def growth_referral(seed: str, tiers: int = 3):
    return referral_campaign(seed, tiers)

@APP.post("/growth/execute")
async def growth_execute(payload: dict):
    actions = payload.get("actions", [])
    return execute_actions(actions)

@APP.post("/monetization/price_suggest")
async def price_suggest(payload: dict):
    sales = payload.get("sales", [])
    current_price = float(payload.get("current_price", 10.0))
    return suggest_price(sales, current_price)

@APP.post("/monetization/subscriptions/kpis")
async def subscriptions_kpis(payload: dict):
    events = payload.get("events", [])
    return sub_kpis(events)

# Experimentation & Portfolio

@APP.get("/experiments/assign")
async def experiments_assign(user_id: str, experiment: str, ratio_a: float = 0.5):
    return exp_assign(user_id=user_id, experiment=experiment, ratio_a=ratio_a)

@APP.post("/experiments/outcome")
async def experiments_outcome(payload: dict):
    return exp_record(user_id=payload.get("user_id",""), experiment=payload.get("experiment",""), variant=payload.get("variant",""), outcome=payload.get("outcome",{}))

@APP.post("/portfolio/score")
async def portfolio_score(items: list[dict]):
    return {"items": ice_score(items)}

# Strategy & BI & Marketing
@APP.get("/strategy/objectives")
def strategy_objectives():
    return current_objectives()

@APP.get("/bi/kpis")
def bi_kpis():
    return current_kpis()

@APP.post("/marketing/campaigns/suggest")
def marketing_campaigns_suggest(payload: dict):
    return {"suggestions": campaign_suggestions(payload or {})}


# Mission enablement endpoints
@APP.get("/mission/project")
def mission_project():
    return project_plan()


@APP.get("/mission/team")
def mission_team():
    return team_roster()


@APP.get("/mission/portfolio")
def mission_portfolio(limit: int = 5):
    return {"items": portfolio_highlights(limit=limit)}

# Admin consolidated status
@APP.get("/admin/status")
def admin_status():
    env = os.getenv("ENV", "dev")
    svc = {
        "env": env,
        "otel_enabled": os.getenv("OTEL_ENABLED", "false").lower() == "true",
        "project": os.getenv("GCP_PROJECT_ID"),
        "dataset": os.getenv("BQ_DATASET"),
        "version": os.getenv("GIT_SHA") or getattr(APP, "version", None),
    }
    # Health (quick) and readiness
    health = {"status": "ok"}
    try:
        health = {"status": "ok", "detail": "app alive"}
    except Exception:
        health = {"status": "error"}
    try:
        readiness = ready()
    except Exception:
        readiness = {"status": "unknown"}
    # KPIs + freshness (best-effort)
    try:
        kpis = current_kpis()
    except Exception:
        kpis = {"error": "kpis_unavailable"}
    # Configured scheduler jobs (static view)
    try:
        import json as _json
        from pathlib import Path as _Path
        path = _Path("scheduling/cloud_scheduler_jobs.json")
        sched = _json.loads(path.read_text()) if path.exists() else []
    except Exception:
        sched = []
    return {"service": svc, "health": health, "ready": readiness, "kpis": kpis, "scheduler_config": sched}

# E-commerce: Shopify product import
@APP.get("/ecom/shopify/status")
def shopify_status():
    domain_ok = bool(os.getenv("SHOP_DOMAIN"))
    token_ok = bool(os.getenv("SHOPIFY_ADMIN_TOKEN"))
    return {"shop_domain_configured": domain_ok, "token_configured": token_ok}

@APP.post("/ecom/shopify/import")
async def shopify_import(payload: dict):
    """Create Shopify products from provided rows.

    Body example:
    {
      "products": [
        {"title": "Zen Art #1", "body_html": "...", "tags": ["zen","printable"], "images": ["/path/to/img.png"]}
      ],
      "dry_run": false
    }
    """
    products = payload.get("products") or []
    dry = bool(payload.get("dry_run"))
    created = []
    errors = []
    for p in products:
        try:
            if dry:
                created.append({"dry_run": True, "title": p.get("title")})
            else:
                res = create_product(p)
                created.append(res)
        except Exception as e:
            errors.append({"title": p.get("title"), "error": str(e)})
    return {"created": created, "errors": errors, "dry_run": dry}

# Ops: batch lifecycle execution (for Scheduler)
@APP.post("/ops/lifecycle/batch")
async def ops_lifecycle_batch(payload: dict, request: Request):
    users = payload.get("users", [])
    executed = 0
    results = []
    for u in users:
        actions = lifecycle_actions(u)
        res = execute_actions(actions)
        executed += res.get("executed", 0)
        results.append({"user": u.get("id"), "executed": res.get("executed", 0)})
    return {"users": len(users), "actions_executed": executed, "results": results, "request_id": getattr(request.state, 'request_id', None)}

@APP.post("/run/backfill/orders")
async def run_backfill_orders(bt: BackgroundTasks):
    bt.add_task(lambda: subprocess.run([sys.executable, "analytics/backfill/orders_bulk.py"], check=False))
    return {"ok": True, "job": "orders_backfill_triggered"}

@APP.post("/run/backfill/products")
async def run_backfill_products(bt: BackgroundTasks):
    bt.add_task(lambda: subprocess.run([sys.executable, "analytics/backfill/products_bulk.py"], check=False))
    return {"ok": True, "job": "products_backfill_triggered"}

# Cron aliases (for Scheduler compatibility)
@APP.get("/cron/anomaly-check")
def cron_anomaly_check():
    return anomaly_check()

@APP.post("/cron/backfill/orders")
async def cron_backfill_orders(bt: BackgroundTasks):
    return await run_backfill_orders(bt)

@APP.post("/cron/backfill/products")
async def cron_backfill_products(bt: BackgroundTasks):
    return await run_backfill_products(bt)
