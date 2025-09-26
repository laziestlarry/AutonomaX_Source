#!/usr/bin/env bash
set -euo pipefail

# Sprint runner for AutonomaX_Master_Index.csv only

CSV="repos/AutonomaX_Master_Index.csv"
if [[ ! -f "$CSV" ]]; then
  echo "Missing $CSV. Place your prioritized index at $CSV"; exit 2
fi

echo "==> Validate & fix Master Index paths (prefix mapping optional via env OLD_PREFIX/NEW_PREFIX)"
python3 tools/master_index_fix_paths.py --csv "$CSV" ${OLD_PREFIX:+--old-prefix "$OLD_PREFIX"} ${NEW_PREFIX:+--new-prefix "$NEW_PREFIX"} || true
FIXED="repos/AutonomaX_Master_Index.corrected.csv"
USE_CSV="$CSV"
if [[ -f "$FIXED" ]]; then USE_CSV="$FIXED"; fi

echo "==> Generate blueprint (master index)"
python3 tools/blueprint.py --file "$USE_CSV" --label master --top 100

echo "==> Reset batch checkpoint"
rm -f data_room/blueprints/batch_checkpoint.json || true

echo "==> Append all tasks in batches of 20"
bash ./ops/batch_blueprint_all.sh 20

echo "==> Intake inventory for Agents"
./ops/intake_inventory.sh --filelist "$USE_CSV" --label master

echo "==> Prepare products (broad include)"
bash ./ops/prepare_products.sh data_room/inventory/inventory.json product printable content media

echo "==> Generate mastery guidelines"
python3 tools/mastery_guidelines.py --file "$USE_CSV" --outdir docs/mastery

echo "==> Sprint summary"
ls -1 data_room/blueprints/blueprint_*.md | tail -n 1 | sed 's/^/  - /'
echo "  - data_room/inventory/tasks.csv"
echo "  - docs/mastery/mastery_guidelines.md"
echo "  - docs/mastery/runbook_master_index.md"
