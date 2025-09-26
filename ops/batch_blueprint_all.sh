#!/usr/bin/env bash
set -euo pipefail

# Process all blueprint tasks in batches until completion.
# Usage: ./ops/batch_blueprint_all.sh [batch_size]

BATCH=${1:-20}
while true; do
  out=$(python3 tools/batch_blueprint.py --batch "$BATCH" || true)
  echo "$out"
  appended=$(echo "$out" | python3 -c 'import sys,json,re; import sys
import json
try:
    d=json.loads(sys.stdin.read())
    print(d.get("appended",0))
except Exception:
    print(0)
')
  if [[ "$appended" -eq 0 ]]; then
    echo "==> All tasks appended."
    break
  fi
  sleep 1
done

