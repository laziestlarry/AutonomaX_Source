#!/usr/bin/env bash
set -euo pipefail

# pipeline_local.sh — Run local-first pipeline end-to-end; no cloud required (upload optional)
# Steps:
#  1) Generate blueprint from repos/*.csv (or from config file)
#  2) Intake inventory from repos/*.csv for Agents/Commander
#  3) Prepare products locally (tagging/reordering/tuning)
#  4) Produce evidence (optional; requires CLOUD_RUN_URL if used)
#  5) Upload artifacts to GCS (optional; if configured)

CONF=${1:-config/local_pipeline.yaml}
command -v python3 >/dev/null 2>&1 || { echo "python3 not found"; exit 2; }

export CONF
LABEL=$(python3 - <<'PY'
import os,yaml
f=os.environ['CONF']
d=yaml.safe_load(open(f)) or {}
print(d.get('label',''))
PY
)
TOP=$(python3 - <<'PY'
import os,yaml
f=os.environ['CONF']
d=yaml.safe_load(open(f)) or {}
print(d.get('blueprint',{}).get('top',20))
PY
)
DIR=$(python3 - <<'PY'
import os,yaml
f=os.environ['CONF']
d=yaml.safe_load(open(f)) or {}
print(d.get('blueprint',{}).get('sources',{}).get('dir',''))
PY
)
FILES=$(python3 - <<'PY'
import os,yaml,json
f=os.environ['CONF']
d=yaml.safe_load(open(f)) or {}
print(json.dumps(d.get('blueprint',{}).get('sources',{}).get('files',[]) or []))
PY
)

echo "==> [1/4] Generate blueprint (label=$LABEL top=$TOP)"
if [[ -n "$DIR" && "$DIR" != "null" ]]; then
  ./ops/generate_blueprint.sh "$DIR" "$LABEL" "$TOP"
else
  # shellcheck disable=SC2046
  python3 tools/blueprint.py $(for f in $(echo "$FILES" | python3 -c 'import sys,json;print(" ".join(json.load(sys.stdin)))' 2>/dev/null || true); do echo --file "$f"; done) --label "$LABEL" --top "$TOP"
fi

echo "==> [2/5] Intake inventory for Agents"
FILELIST_GLOB=$(python3 - <<'PY'
import os,yaml
f=os.environ['CONF']
d=yaml.safe_load(open(f)) or {}
print(d.get('intake',{}).get('filelist_glob',''))
PY
)
ILABEL=$(python3 - <<'PY'
import os,yaml
f=os.environ['CONF']
d=yaml.safe_load(open(f)) or {}
print(d.get('intake',{}).get('label','repos'))
PY
)
if [[ -n "$FILELIST_GLOB" && "$FILELIST_GLOB" != "null" ]]; then
  ./ops/intake_inventory.sh --filelist-glob "$FILELIST_GLOB" --label "$ILABEL"
else
  echo "Skip intake: no filelist_glob configured"
fi

echo "==> [3/5] Prepare products (tagging/reordering/tuning)"
INV_PATH="data_room/inventory/inventory.json"
if [[ -f "data_room/inventory/inventory_merged.json" ]]; then
  INV_PATH="data_room/inventory/inventory_merged.json"
fi
bash ./ops/prepare_products.sh "$INV_PATH" || true

echo "==> [4/5] (Optional) Evidence run"
if [[ -n "${CLOUD_RUN_URL:-}" ]]; then
  ./ops/team_run_demo.sh || true
else
  echo "CLOUD_RUN_URL not set; skipping evidence run"
fi

echo "==> [5/5] (Optional) Upload artifacts to GCS"
GCS_PREFIX=$(python3 - <<'PY'
import os,yaml
f=os.environ['CONF']
d=yaml.safe_load(open(f)) or {}
print(d.get('upload',{}).get('gcs_prefix',''))
PY
)
if [[ -n "$GCS_PREFIX" && "$GCS_PREFIX" != "null" && "$GCS_PREFIX" != gs://YOUR_BUCKET/* ]]; then
  PATHS=$(python3 - <<'PY'
import os,yaml,json
f=os.environ['CONF']
d=yaml.safe_load(open(f)) or {}
print(json.dumps(d.get('upload',{}).get('paths',[]) or []))
PY
)
  # shellcheck disable=SC2046
  bash ./ops/upload_to_gcs.sh "$GCS_PREFIX" $(echo "$PATHS" | python3 -c 'import sys,json;print(" ".join(json.load(sys.stdin)))')
else
  echo "No gcs_prefix configured; skipping upload"
fi

echo "==> Artifacts summary"

# Helper to print latest file(s) in a directory matching a pattern
print_latest() {
  local dir="$1"; shift
  local pat="$1"; shift || true
  if [[ -d "$dir" ]]; then
    local latest
    latest=$(ls -1t "$dir"/$pat 2>/dev/null | head -n 3)
    if [[ -n "$latest" ]]; then
      echo "  $dir/$pat →"; echo "$latest" | sed 's/^/    - /'
    else
      echo "  $dir/$pat → (none)"
    fi
  else
    echo "  $dir (missing)"
  fi
}

print_path() {
  local p="$1"
  if [[ -f "$p" ]]; then echo "  $p"; fi
}

echo "- Blueprints:"
print_latest "data_room/blueprints" "blueprint_*.md"
print_latest "data_room/blueprints" "summary_*.json"
print_latest "data_room/blueprints" "project_plan_*.csv"

echo "- Inventory:"
print_path "data_room/inventory/inventory.json"
print_path "data_room/inventory/inventory_merged.json"
print_path "data_room/inventory/matrix.csv"
print_path "data_room/inventory/tags.json"

echo "- Products:"
print_path "data_room/products/catalog.csv"
print_path "data_room/products/plan.md"

echo "- Evidence:"
print_latest "revenue_sprint_lite_payoneer/delivery" "output_*.log"

echo "==> Local pipeline complete"
