#!/usr/bin/env bash
set -euo pipefail

# generate_blueprint.sh — Wrapper to generate a blueprint from a ranked CSV
# Examples:
#   ./ops/generate_blueprint.sh repos/my_repos_ranked.csv local 12
#   ./ops/generate_blueprint.sh repos local 20  # when passing a directory of CSVs

FILE=${1:?"Path to ranked CSV or directory is required"}
LABEL=${2:-local}
TOP=${3:-12}

if [[ -d "$FILE" ]]; then
  python3 tools/blueprint.py --dir "$FILE" --label "$LABEL" --top "$TOP"
else
  python3 tools/blueprint.py --file "$FILE" --label "$LABEL" --top "$TOP"
fi

echo "==> Blueprint artifacts written under data_room/blueprints"
