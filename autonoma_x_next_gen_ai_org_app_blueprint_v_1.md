# AutonomaX Next‑Gen AI Org & App Blueprint (v1.0)

> Goal: Stand up a self‑improving, multi‑agent AI organization and an enterprise‑grade application codebase that ships the **first commercial transaction** fast, then compounds via continuous delivery.

---

## 0) Executive Snapshot
- **North Star:** Generate, list, and sell digital products/services with autonomous agents; expand via integrations sourced from AI tool directories and OSS ecosystems.
- **MVP Scope (T+7 days):**
  1) **Catalog Brain** (RAG + Agents) → create product briefs, assets, listings.
  2) **Commerce Pipe** (API + Jobs) → publish to Shopify/Etsy.
  3) **Funnel Frontend** → landing + checkout + status page.
  4) **Telemetry** → events, dashboards, and on‑call playbooks.
- **Critical Path:** Data → Model → Orchestrator → API → Frontend → Payments → Delivery.

---

## 1) Org & Roles (Self‑Improving)
**Director Agents (C‑level):**
- **Chief Product Agent (CPA):** Owns product roadmap, validates demand, defines SKU specs.
- **Chief Commerce Agent (CCA):** Owns listings, pricing, promotions, multi‑market sync.
- **Chief Operations Agent (COA):** Owns CI/CD, environments, reliability, costs.
- **Chief Data Agent (CDA):** Owns datasets, embeddings, evals, model registry.
- **Chief Customer Agent (CCA2):** Owns CS flows, macros, SLAs, NPS, retention.

**Department Executors:**
- **Sourcing Bots:** Scrape/ingest trends & tools → structured opportunities.
- **Content Fabricators:** Generate titles, bullets, SEO, thumbnails, A/B variants.
- **Listing Runners:** Push to channels (Shopify/Etsy/Amazon/eBay) & verify.
- **Support Copilots:** Omni‑channel FAQ, triage, resolution, and refunds.
- **Revenue Analysts:** Run cohorts, CAC/LTV, experiment matrices.

**Self‑Improvement Loop:**
1) Daily job collects outcomes →
2) Evals compare vs. goals →
3) Proposals drafted →
4) Director vote/guardrails →
5) Merge via change controls →
6) Rollout behind flags.

---

## 2) System Architecture (High Level)
- **Frontend (Next.js/React)**: Marketing site, product pages, checkout links, agent console.
- **Edge/API (FastAPI/Cloud Run)**: REST/GraphQL endpoints, webhooks, auth, rate limits.
- **Orchestration (LangGraph / Celery)**: DAGs for generation → review → publish.
- **Data Layer (PostgreSQL + Redis + Object Storage)**: Products, runs, events, assets.
- **RAG/Search (Vector DB)**: Chroma/pgvector for embeddings; S3/GCS for documents.
- **Model Layer**: Hosted APIs (OpenAI/Anthropic/etc.) + Local fallbacks (llama.cpp/gguf).
- **Observability**: OpenTelemetry + Prometheus/Grafana + LangSmith (optional).
- **CI/CD**: GitHub Actions → Docker → Cloud Run; IaC via Terraform.

---

## 3) Codebase Layout (Monorepo)
```
autonomaX/
  apps/
    web/                # Next.js 15 (app router) - landing, console, status
    api/                # FastAPI service (REST + webhooks)
    workers/            # Celery/Worker jobs for async DAGs
  libs/
    agents/             # director & executor agents (LangGraph nodes)
    rag/                # loaders, splitters, retrievers, evaluators
    models/             # provider adapters, prompts, safety, output schemas
    common/             # logging, config, feature flags, errors, types
  data/
    seeds/              # bootstrap CSV/JSON/YAML for demo SKUs
    datasets/           # training & eval curated sets
  deploy/
    docker/             # Dockerfiles
    terraform/          # cloud infra
    github/             # workflows
    scripts/            # one‑liners, smoke tests, importers
  ops/
    runbooks/           # on‑call, incidents, SLOs
    playbooks/          # releases, rollbacks, migrations
  docs/
    adr/                # architecture decision records
    api/                # OpenAPI & GraphQL schemas
    org/                # RACI, processes, policies
  .env.example
  pyproject.toml / package.json
  Makefile
```

---

## 4) Minimal Contracts (APIs & Schemas)
**OpenAPI (excerpt):**
```yaml
openapi: 3.1.0
info: { title: AutonomaX API, version: 1.0.0 }
paths:
  /v1/products/draft:
    post:
      summary: Generate product draft from brief
      requestBody: { content: { application/json: { schema: { $ref: '#/components/schemas/ProductBrief' } } } }
      responses:
        '200': { description: OK, content: { application/json: { schema: { $ref: '#/components/schemas/ProductDraft' } } } }
  /v1/products/publish:
    post:
      summary: Publish product to channels
      requestBody: { content: { application/json: { schema: { $ref: '#/components/schemas/PublishRequest' } } } }
      responses:
        '200': { description: OK }
components:
  schemas:
    ProductBrief: { type: object, required: [category, audience], properties: { category: {type: string}, audience: {type: string}, keywords: {type: array, items: {type: string}}, refs: {type: array, items: {type: string}} } }
    ProductDraft: { type: object, properties: { title: {type: string}, description: {type: string}, tags: {type: array, items: {type: string}}, assets: {type: array, items: {type: string}}, price: {type: number} } }
    PublishRequest: { type: object, properties: { channel: {type: string, enum: [shopify, etsy]}, draft_id: {type: string}, pricing: {type: object} } }
```

**Events (analytics):** `product.generated`, `asset.created`, `listing.published`, `order.paid`, `refund.issued`, `agent.proposal`.

---

## 5) Pipelines (LangGraph‑style)
**Pipeline: Product→Revenue**
1) **Ingest & Discover**: trend sources, directories, prior sales, keyword gaps.
2) **Brief Synthesis**: structured `ProductBrief` + success criteria.
3) **Asset Forge**: titles, bullets, SEO, thumbnails (gen + safety + dedupe).
4) **Human/Agent Gate**: rubric scoring; A/B variant selection.
5) **Publish**: Shopify/Etsy API; verify and fetch live URL.
6) **Promote**: auto‑post to socials; optional ads budget gate.
7) **Measure**: UTM, cohorts, dashboard in Grafana/Looker.
8) **Improve**: nightly evals → proposals → change requests.

---

## 6) Data & RAG
- **Stores:**
  - `postgres.products(id, brief, draft, listing, metrics)`
  - `postgres.jobs(id, dag, status, artifacts)`
  - `vector.product_ideas(embedding, meta)`
- **Embeddings:** text‑embedding‑3‑large (hosted) or E5/Instructor (local) + pgvector.
- **Curation:** `data/datasets/{train,eval}` with YAML manifests; mdx notes as sources.

---

## 7) Model Registry (YAML)
```yaml
providers:
  openai: { models: [gpt-4.1, gpt-4o-mini], use_for: [drafting, planning, tools] }
  anthropic: { models: [claude-3.7-sonnet], use_for: [analysis, long-context] }
  local: { models: [llama3.1-8b-instruct-gguf], use_for: [offline, cost‑save] }

defaults:
  chat: openai:gpt-4o-mini
  embed: openai:text-embedding-3-small
  vision: openai:gpt-4o

policies:
  max_cost_usd_per_day: 15
  safe_modes: [profanity_filter, pii_redact]
```

---

## 8) CI/CD (GitHub Actions)
`.github/workflows/ci.yml`
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -e apps/api[all] apps/workers libs/agents libs/rag
      - run: pytest -q
  build_docker:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t gcr.io/$PROJECT/autonomax-api:$(git rev-parse --short HEAD) -f deploy/docker/api.Dockerfile .
      - uses: google-github-actions/auth@v2
        with: { workload_identity_provider: ${{ secrets.WIP }}, service_account: ${{ secrets.SA }} }
      - uses: google-github-actions/push-artifact-registry@v2
        with: { location: us, repository: docker, image: autonomax-api }
  deploy:
    needs: build_docker
    runs-on: ubuntu-latest
    steps:
      - uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: autonomax-api
          image: us-docker-pkg.dev/$PROJECT/docker/autonomax-api:$(git rev-parse --short HEAD)
          region: us-central1
          allow_unauthenticated: true
```

---

## 9) Infrastructure as Code (Terraform excerpt)
```hcl
resource "google_artifact_registry_repository" "docker" {
  location = var.region
  repository_id = "docker"
  format = "DOCKER"
}

resource "google_cloud_run_service" "api" {
  name     = "autonomax-api"
  location = var.region
  template { containers { image = var.image } }
  traffic { percent = 100, latest_revision = true }
}
```

---

## 10) Worker Jobs & Schedules
- **Nightly:** trend‑ingest, price check, listing health, evals.
- **Hourly:** abandoned carts, support queue triage, asset render retries.
- **On‑Demand:** `products/draft`, `products/publish`, `sync/shopify`.

Cron examples (Cloud Scheduler → Pub/Sub → worker):
```
0 1 * * *  trend-ingest
*/30 * * * * listing-health
```

---

## 11) Security & Compliance
- API keys in Secret Manager; short‑lived tokens for workers.
- PII redaction at ingress; audit logs to BigQuery.
- Feature flags for risky rollouts.
- Backup/restore runbooks; error budgets and SLOs.

---

## 12) Testing & Evals
- **Unit**: prompts, tools, reducers.
- **Contract**: OpenAPI responses via Schemathesis.
- **Load**: k6 on `/v1/products/publish`.
- **Eval**: rubric JSON for product quality; Golden sets for RAG grounding.

---

## 13) Kick‑Off Agenda (90 mins)
1) Mission & KPIs (10)
2) Roles & RACI (10)
3) Architecture & Risks (20)
4) Sprint‑1 Plan & Critical Path (25)
5) Change Management & SLAs (10)
6) Decision Log (ADR‑001) (5)
7) Q&A / Parking Lot (10)

**RACI Snapshot:**
- CPA: A for briefs; C for pricing; I for ops.
- CCA: A for listings; R for channel sync.
- COA: A for CI/CD & costs.
- CDA: A for datasets/evals.
- CCA2: A for CS macros.

---

## 14) Sprint‑1 (to First Revenue)
**Critical Path:** Data → Draft → Gate → Publish → Pay → Deliver → Review.

**Backlog → Sequenced:**
1) Seed datasets & embeddings (CDA)
2) Draft generator endpoint (API)
3) Asset forge worker (Workers)
4) Shopify publish adapter (Workers)
5) Landing page + checkout link (Web)
6) Telemetry & dashboards (Ops)
7) Support macros + autoresponder (CCA2)
8) Promo hooks (social/email) (CCA)

**Definition of Done (MVP):**
- 5 products live, checkout working, 1 paid order processed.

---

## 15) Shell & Make Targets
```makefile
setup:
	pip install -e apps/api apps/workers libs/*
	cp .env.example .env

run-api:
	uvicorn apps.api.main:app --reload --port 8080

run-worker:
	celery -A apps.workers.app worker -l info

draft:
	curl -X POST $API/v1/products/draft -d @examples/brief.json -H 'Content-Type: application/json'

publish:
	curl -X POST $API/v1/products/publish -d @examples/publish.json -H 'Content-Type: application/json'
```

---

## 16) Example Prompts & Rubrics
**Title Prompt (system):** "You are a senior e‑commerce copywriter. Return JSON strictly matching schema with title ≤ 70 chars, primary keyword first, avoid stop‑words."

**Rubric (JSON):** `readability, intent‑match, uniqueness, SEO‑score, brand‑fit (0‑5)`; threshold `≥ 4.0`.

---

## 17) Customer Service Flows
- **Tier‑0:** semantic FAQ + macros; instant ETA for orders.
- **Tier‑1:** returns/refunds automation; coupon recovery.
- **Tier‑2:** escalation to human with full context.

SLA: First response < 2m; Resolution < 24h.

---

## 18) Risk Controls & Upgrades
- **Model Drift:** weekly eval gates.
- **Cost Overruns:** per‑job budget caps; auto‑switch to local models.
- **Listing Policy Changes:** adapters behind feature flags; contract tests.
- **Data Loss:** daily backups; restore drills.

**Upgrade Hooks:**
- Plug‑in providers from directories (YesChat, ThereIsAnAIForThat, Awesome lists) via adapter pattern.

---

## 19) Integration Sources (curated)
- LangChain model & chat integrations (providers & tool calling) – use as the adapter layer.
- AI tool directories (YesChat / ThereIsAnAIForThat) to discover partners and features.
- Awesome lists (LLM, apps, safety, efficiency) for patterns, evals, and guardrails.

---

## 20) Next Steps (Today)
1) Clone scaffold & push repo.
2) Provision Cloud Run + Artifact Registry via Terraform.
3) Configure secrets and environment.
4) Run `draft` → `publish` happy path on 1 SKU.
5) Light promo & support ready.

> When the MVP order lands, freeze a tag `v1.0` and start Experiment Queue A/B‑001.

