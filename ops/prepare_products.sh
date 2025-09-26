#!/usr/bin/env bash
set -euo pipefail

# Prepare product artifacts using inventory and agents' tag suggestions
# Usage:
#   ./ops/prepare_products.sh [inventory.json] [include-tags...]

INV=${1:-data_room/inventory/inventory.json}
shift || true
INCLUDE=("$@")
if [[ ${#INCLUDE[@]} -eq 0 ]]; then INCLUDE=(product printable content); fi

python3 tools/products_prepare.py --inventory "$INV" --include "${INCLUDE[@]}" --out data_room/products

echo "==> Products catalog and plan under data_room/products"

