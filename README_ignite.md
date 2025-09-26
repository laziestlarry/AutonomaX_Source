# AutonomaX Ignition Kit

This kit helps you **brief Codex (or any LLM)** using your `AutonomaX_Master_Index.csv`
and **ignite** a local run of AutonomaX in:
`/Users/pq/AutonomaX_AI_Integration_Starter_v11_full`

## What it does
1. **Bootstrap**: reads your CSV, verifies files, builds `manifest.json`, and (optionally) creates `_staging/` symlinks.
2. **Product Update**: locates `shopify_sync.py` or `scripts/make_products_from_yaml.py` and prepares/runs updates.
3. **Self-Improve**: runs a light diagnostic pass (env, deps, folder sanity), and emits prioritized TODOs.
4. **Ignite**: one-liner to execute all the above.

---

## Quick Start

```bash
# 1) Copy this kit into your repo
cd /Users/pq/AutonomaX_AI_Integration_Starter_v11_full
unzip ~/Downloads/AutonomaX_Ignition_Kit.zip -d .

# 2) Provide the CSV
#    Use the found-file CSV if you ran my search script:
#    AutonomaX_Master_Index_found.csv
#    Otherwise, use AutonomaX_Master_Index.csv
cp ~/Downloads/AutonomaX_Master_Index*.csv . || true

# 3) Ignite (auto-creates .venv if missing)
bash ignite.sh AutonomaX_Master_Index_found.csv
# or
bash ignite.sh AutonomaX_Master_Index.csv
```

### After running, check:
- `./_autonomax/manifest.json` → canonical paths for important files
- `./_autonomax/report.md` → status and next actions
- `./_staging/` → quick symlinks to critical files (optional)

---

## Files in this kit
- `ignite.sh` — orchestrates everything
- `autonomax_bootstrap.py` — reads CSV, builds manifest, creates symlinks
- `product_update.py` — prepares/runs product update flow
- `self_improve.py` — sanity checks and prioritized TODOs
- `config/defaults.yaml` — settings for the above
- `.env.example` — template for environment variables
- `Makefile` — convenient targets

---

## Notes
- **No secrets included.** Fill `.env` based on `.env.example`.
- Scripts are safe-by-default: they simulate if required inputs are missing.
- You can re-run ignition as needed; artifacts live under `./_autonomax/` and `./_staging/`.
