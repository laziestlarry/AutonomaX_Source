#!/usr/bin/env bash
set -euo pipefail

CSV_PATH="${1:-AutonomaX_Master_Index_found.csv}"
PROJECT_ROOT="$(pwd)"

echo "▶ AutonomaX Ignite"
echo "• Project root: $PROJECT_ROOT"
echo "• CSV: $CSV_PATH"
echo

if [[ ! -f "$CSV_PATH" ]]; then
  echo "ERROR: CSV not found: $CSV_PATH"
  echo "Provide AutonomaX_Master_Index_found.csv (preferred) or AutonomaX_Master_Index.csv"
  exit 1
fi

# Ensure helper dirs
mkdir -p _autonomax _staging

# Python venv
if [[ ! -d ".venv" ]]; then
  echo "• Creating Python venv (.venv)"
  python3 -m venv .venv
fi
source .venv/bin/activate

# Minimal deps (install quietly if present)
python -m pip install --upgrade pip >/dev/null 2>&1 || true
python -m pip install pyyaml >/dev/null 2>&1 || true

echo "• Bootstrap: manifest + symlinks"
python autonomax_bootstrap.py --csv "$CSV_PATH" --project-root "$PROJECT_ROOT" ${AUTONOMAX_BOOTSTRAP_FLAGS:-}

echo "• Product update phase"
python product_update.py --project-root "$PROJECT_ROOT" || true

echo "• Self-improvement phase"
python self_improve.py --project-root "$PROJECT_ROOT" || true

echo
echo "✅ Ignite complete."
echo "Artifacts:"
echo "  - _autonomax/manifest.json"
echo "  - _autonomax/report.md"
echo "  - _staging/ (symlinks)"
