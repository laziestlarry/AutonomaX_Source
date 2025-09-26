#!/usr/bin/env bash
set -euo pipefail

# Run the local task queue
# Usage: ./ops/local_queue_run.sh [config/local_tasks.yaml]

CONF=${1:-config/local_tasks.yaml}
python3 tools/local_queue.py --config "$CONF"

