#!/usr/bin/env bash
set -euo pipefail

# intake_inventory.sh — Run local inventory intake for Commander_AutonomaX
# Example:
#   ./ops/intake_inventory.sh --root . --root ../archive --label local

python3 tools/inventory.py "$@"

echo "==> Inventory saved under data_room/inventory (inventory.json, matrix.csv)"

