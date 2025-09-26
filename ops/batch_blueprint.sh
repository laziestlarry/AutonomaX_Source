#!/usr/bin/env bash
set -euo pipefail

# Append next batch of tasks from latest blueprint summary into tasks.csv
# Usage: ./ops/batch_blueprint.sh [batch_size]

BATCH=${1:-20}
python3 tools/batch_blueprint.py --batch "$BATCH"

echo "==> Batch appended. Check data_room/inventory/tasks.csv and data_room/blueprints/batch_checkpoint.json"

