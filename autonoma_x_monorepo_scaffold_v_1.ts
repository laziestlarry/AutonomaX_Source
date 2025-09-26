# 📦 AutonomaX Monorepo Scaffold v1.0

Below is a ready‑to‑run scaffold with a minimal FastAPI API, Celery workers, LangGraph‑style agent orchestration, CI/CD to Cloud Run, and Terraform IaC. Copy these files into a folder named `autonomaX/`.

> Notes
> - Python 3.11 recommended.  
> - Replace placeholders: `YOUR_GCP_PROJECT`, `YOUR_REGION`, secrets.  
> - Shopify creds (Admin token + shop domain) required for publish adapter.

---

## 🗂 Folder Tree
```
autonomaX/
  apps/
    api/
      main.py
      routers/
        products.py
      core/
        config.py
        deps.py
    workers/
      app.py
      tasks/
        assets.py
        publish.py
  libs/
    agents/
      graph.py
      prompts.py
    models/
      providers.py
      schemas.py
    rag/
      retriever.py
    common/
      logging.py
      events.py
  data/
    seeds/
      example_brief.json
    datasets/
      README.md
  deploy/
    docker/
      api.Dockerfile
      worker.Dockerfile
    github/
      ci.yml
    terraform/
      main.tf
      variables.tf
      outputs.tf
  ops/
    runbooks/incident.md
    playbooks/release.md
  docs/
    adr/ADR-001-initial-architecture.md
  .env.example
  requirements.txt
  Makefile
  pyproject.toml
  README.md
```

---

## 📘 README.md
```md
# AutonomaX

Monorepo bootstrapped for AI-driven product generation → channel publishing → telemetry.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make run-api   # localhost:8080
make run-worker
make draft     # sample brief → product draft
make publish   # publish draft to Shopify (needs creds)
```

## Environments
- Local dev via uvicorn & Celery
- CI via GitHub Actions → Docker → Cloud Run
- IaC via Terraform (Artifact Registry + Cloud Run)
```
```

---

## 🔐 .env.example
```dotenv
# Core
APP_ENV=local
LOG_LEVEL=INFO

# DBs
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/autonomax
REDIS_URL=redis://localhost:6379/0
VECTOR_DB_URL=postgresql+psycopg://user:pass@localhost:5432/autonomax

# Providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Channels
SHOPIFY_ADMIN_TOKEN=
SHOPIFY_SHOP_DOMAIN=autonomax.myshopify.com

# Telemetry
OTEL_EXPORTER_OTLP_ENDPOINT=

# Cloud
GCP_PROJECT=YOUR_GCP_PROJECT
GCP_REGION=us-central1
```

---

## 🧰 requirements.txt
```txt
fastapi==0.112.2
uvicorn[standard]==0.30.6
pydantic==2.9.2
pydantic-settings==2.6.1
httpx==0.27.2
celery==5.4.0
redis==5.0.8
python-dotenv==1.0.1
loguru==0.7.2
sqlalchemy==2.0.36
psycopg[binary]==3.2.2
langchain==0.2.16
langgraph==0.2.35
numpy==1.26.4
openai==1.50.2
```

---

## 🧪 pyproject.toml
```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "autonomaX"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []
```

---

## 🧱 Makefile
```makefile
.PHONY: setup run-api run-worker draft publish fmt lint test

setup:
	pip install -r requirements.txt

run-api:
	uvicorn apps.api.main:app --reload --port 8080

run-worker:
	celery -A apps.workers.app.celery worker -l info

draft:
	curl -s -X POST http://localhost:8080/v1/products/draft \
	  -H 'Content-Type: application/json' \
	  -d @data/seeds/example_brief.json | jq

publish:
	curl -s -X POST http://localhost:8080/v1/products/publish \
	  -H 'Content-Type: application/json' \
	  -d '{"channel":"shopify","draft_id":"demo-1"}' | jq
```

---

## 🧩 apps/api/core/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str
    REDIS_URL: str
    VECTOR_DB_URL: str

    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    SHOPIFY_ADMIN_TOKEN: str | None = None
    SHOPIFY_SHOP_DOMAIN: str | None = None

    GCP_PROJECT: str | None = None
    GCP_REGION: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🚦 apps/api/main.py
```python
from fastapi import FastAPI
from loguru import logger
from apps.api.core.config import settings
from apps.api.routers import products

app = FastAPI(title="AutonomaX API", version="1.0.0")
app.include_router(products.router, prefix="/v1/products", tags=["products"])

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV}

@app.on_event("startup")
def on_startup():
    logger.info("AutonomaX API starting in {}", settings.APP_ENV)
```

---

## 🗺 apps/api/routers/products.py
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from libs.agents.graph import generate_product_draft
from libs.common.events import emit
from apps.workers.tasks.publish import publish_shopify

router = APIRouter()

class ProductBrief(BaseModel):
    category: str
    audience: str
    keywords: list[str] = []
    refs: list[str] = []

class ProductDraft(BaseModel):
    id: str
    title: str
    description: str
    tags: list[str]
    assets: list[str] = []
    price: float
    score: float

@router.post("/draft", response_model=ProductDraft)
def draft(brief: ProductBrief):
    draft = generate_product_draft(brief.model_dump())
    emit("product.generated", {"draft_id": draft["id"], "score": draft["score"]})
    return ProductDraft(**draft)

class PublishRequest(BaseModel):
    channel: str
    draft_id: str

@router.post("/publish")
def publish(req: PublishRequest):
    if req.channel != "shopify":
        raise HTTPException(400, "only shopify adapter wired in scaffold")
    result = publish_shopify.delay(req.draft_id)
    return {"status": "queued", "task_id": result.id}
```

---

## 🧠 libs/agents/prompts.py
```python
BRIEF_TO_DRAFT_SYSTEM = (
    "You are a senior e-commerce copywriter. Return strict JSON with keys: "
    "id,title,description,tags,assets,price,score. Title ≤ 70 chars; score in [0,5]."
)
```

---

## 🧠 libs/agents/graph.py
```python
import json, os, uuid
from libs.models.providers import llm_chat
from libs.agents.prompts import BRIEF_TO_DRAFT_SYSTEM

# Minimal synchronous node to keep scaffold simple.

def generate_product_draft(brief: dict) -> dict:
    sys = BRIEF_TO_DRAFT_SYSTEM
    user = (
        f"Category: {brief['category']}\nAudience: {brief['audience']}\n"
        f"Keywords: {', '.join(brief.get('keywords', []))}\n"
        "Return JSON only."
    )
    raw = llm_chat(system=sys, user=user)
    try:
        data = json.loads(raw)
    except Exception:
        # Simple fallback if model returns text: wrap into schema
        data = {
            "id": f"demo-{uuid.uuid4().hex[:8]}",
            "title": raw[:64],
            "description": raw,
            "tags": brief.get("keywords", []),
            "assets": [],
            "price": 7.0,
            "score": 4.0,
        }
    data.setdefault("id", f"demo-{uuid.uuid4().hex[:8]}")
    return data
```

---

## 🤝 libs/models/providers.py
```python
import os
from typing import Optional
from openai import OpenAI

_client: Optional[OpenAI] = None

def _client_openai() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client

# Minimal wrapper so we can swap providers later

def llm_chat(system: str, user: str) -> str:
    client = _client_openai()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.7,
    )
    return resp.choices[0].message.content
```

---

## 📚 libs/models/schemas.py
```python
from pydantic import BaseModel

class DraftSchema(BaseModel):
    id: str
    title: str
    description: str
    tags: list[str]
    assets: list[str]
    price: float
    score: float
```

---

## 🔎 libs/rag/retriever.py
```python
# Placeholder for pgvector/Chroma integration.
# Expose: embed(text) → upsert; query(text) → passages.

def query_ideas(keyword: str) -> list[str]:
    return [f"Idea: {keyword} minimal abstract printable", f"Idea: {keyword} bundle"]
```

---

## 📣 libs/common/logging.py
```python
from loguru import logger

logger.add("logs/app.log", rotation="10 MB")
```

---

## 📡 libs/common/events.py
```python
from loguru import logger

def emit(event: str, payload: dict):
    logger.bind(event=event).info(payload)
```

---

## 🧵 apps/workers/app.py
```python
import os
from celery import Celery

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
celery = Celery("autonomax", broker=redis_url, backend=redis_url)
celery.conf.task_routes = {
    "apps.workers.tasks.assets.*": {"queue": "assets"},
    "apps.workers.tasks.publish.*": {"queue": "publish"},
}
```

---

## 🛠 apps/workers/tasks/assets.py
```python
from apps.workers.app import celery

@celery.task
def render_thumbnail(draft_id: str) -> str:
    # TODO: call your image gen; return URL/path
    return f"s3://artifacts/{draft_id}/thumb.jpg"
```

---

## 🛒 apps/workers/tasks/publish.py
```python
import os, httpx
from apps.workers.app import celery
from loguru import logger

SHOP = os.environ.get("SHOPIFY_SHOP_DOMAIN")
TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")

@celery.task
def publish_shopify(draft_id: str) -> dict:
    if not (SHOP and TOKEN):
        return {"status": "error", "reason": "missing_shopify_creds"}
    # Minimal demo payload
    product = {
        "product": {
            "title": f"AutonomaX Draft {draft_id}",
            "body_html": "Generated by AutonomaX",
            "vendor": "AutonomaX",
            "product_type": "Digital",
            "variants": [{"price": "7.00"}],
        }
    }
    url = f"https://{SHOP}/admin/api/2024-07/products.json"
    headers = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
    with httpx.Client(timeout=30) as client:
        r = client.post(url, json=product, headers=headers)
    logger.info("publish_shopify {} => {}", draft_id, r.status_code)
    if r.status_code >= 300:
        return {"status": "error", "code": r.status_code, "body": r.text}
    pid = r.json()["product"]["id"]
    return {"status": "ok", "product_id": pid}
```

---

## 🐳 deploy/docker/api.Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PORT=8080
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## 🐳 deploy/docker/worker.Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["celery", "-A", "apps.workers.app.celery", "worker", "-l", "info"]
```

---

## 🛠 deploy/github/ci.yml
```yaml
name: CI-CD
on: [push]
jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: python -m compileall apps libs

  build-and-deploy-api:
    needs: build-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIP }}
          service_account: ${{ secrets.SA_EMAIL }}
      - uses: google-github-actions/setup-gcloud@v2
      - run: |
          gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
          docker build -f deploy/docker/api.Dockerfile -t ${REGION}-docker.pkg.dev/${{ secrets.GCP_PROJECT }}/docker/autonomax-api:${{ github.sha }} .
          docker push ${REGION}-docker.pkg.dev/${{ secrets.GCP_PROJECT }}/docker/autonomax-api:${{ github.sha }}
          gcloud run deploy autonomax-api \
            --image ${REGION}-docker.pkg.dev/${{ secrets.GCP_PROJECT }}/docker/autonomax-api:${{ github.sha }} \
            --region ${{ secrets.GCP_REGION }} --allow-unauthenticated
    env:
      REGION: ${{ secrets.GCP_REGION }}
```

---

## 🌍 deploy/terraform/variables.tf
```hcl
variable "project" { type = string }
variable "region"  { type = string  default = "us-central1" }
```

## 🌍 deploy/terraform/main.tf
```hcl
terraform {
  required_providers { google = { source = "hashicorp/google", version = ">= 5.0" } }
}
provider "google" { project = var.project, region = var.region }

resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "docker"
  format        = "DOCKER"
}

resource "google_cloud_run_service" "api" {
  name     = "autonomax-api"
  location = var.region
  template {
    spec {
      containers { image = "${var.region}-docker.pkg.dev/${var.project}/docker/autonomax-api:latest" }
    }
  }
  traffic { percent = 100, latest_revision = true }
}
```

## 🌍 deploy/terraform/outputs.tf
```hcl
output "api_url" {
  value = google_cloud_run_service.api.status[0].url
}
```

---

## 🧯 ops/runbooks/incident.md
```md
# Incident Runbook
- Collect: logs, last deploy SHA, recent changes.
- Mitigate: rollback one revision in Cloud Run if 5xx > 5% for 10m.
- Create postmortem within 48h with action items + owners.
```

---

## 📜 docs/adr/ADR-001-initial-architecture.md
```md
# ADR-001 Initial Architecture
Decision: FastAPI + Celery + LangChain adapters + Cloud Run + Terraform.
Status: Accepted.
Consequences: Simple path to first revenue; can evolve into microservices.
```

---

## 🧪 data/seeds/example_brief.json
```json
{
  "category": "Zen & Calm Abstract Print",
  "audience": "Home decor buyers",
  "keywords": ["minimal", "serene", "printable"],
  "refs": []
}
