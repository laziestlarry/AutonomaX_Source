# Zen & Calm — Shopify Launch Kit

This bundle creates **5 draft products** in your Shopify store (`autonomax.myshopify.com`) with high-res images generated locally.
Images are attached via base64 (no external hosting needed). **Prices are set in TRY**.

## Files
- `products.csv` — product manifest
- `images/ZenCalm_*.png` — 5 minimal abstract printables (4000x5000 px)
- `shopify_push.py` — Python script to create products via Shopify Admin API
- `.env.example` — scaffold for secrets

## Quick Start
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install requests python-dotenv

cp .env.example .env
# edit .env → paste your SHOPIFY_ADMIN_TOKEN and confirm SHOP_DOMAIN
export $(grep -v '^#' .env | xargs)

# Dry run (no API calls)
export DRY_RUN=true
python shopify_push.py

# Real run
export DRY_RUN=false
python shopify_push.py