#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${SHOP_DOMAIN:-}" || -z "${SHOPIFY_ADMIN_TOKEN:-}" ]]; then
  echo "Set SHOP_DOMAIN and SHOPIFY_ADMIN_TOKEN in your environment (or .env)"; exit 1
fi

CSV="${1:-shopify_products.csv}"
if [[ ! -f "$CSV" ]]; then
  echo "CSV not found: $CSV"; exit 1
fi

# Read SKU and Title from CSV robustly (Python CSV)
# Outputs: SKU<TAB>Title (one per line)
readarray -t ITEMS < <(python - <<'PY'
import csv, sys
path=sys.argv[1]
with open(path, newline='', encoding='utf-8') as f:
    r=csv.DictReader(f)
    # Accept common header names for SKU and Title
    for row in r:
        sku = row.get('Variant SKU') or row.get('SKU') or row.get('Variant sku') or ''
        title = row.get('Title') or ''
        if sku.strip():
            print(f"{sku}\t{title}")
PY
"$CSV")

if [[ ${#ITEMS[@]} -eq 0 ]]; then
  echo "No rows with SKUs found in $CSV"; exit 1
fi

echo "Processing ${#ITEMS[@]} products …"

# Ensure collection "Zen & Calm" exists
ensure_collection() {
  local cid
  cid=$(curl -s -H "X-Shopify-Access-Token: ${SHOPIFY_ADMIN_TOKEN}" \
    "https://${SHOP_DOMAIN}/admin/api/2024-10/custom_collections.json?title=Zen%20%26%20Calm" | jq -r '.custom_collections[0].id // empty')
  if [[ -z "$cid" ]]; then
    cid=$(curl -s -X POST "https://${SHOP_DOMAIN}/admin/api/2024-10/custom_collections.json" \
      -H "X-Shopify-Access-Token: ${SHOPIFY_ADMIN_TOKEN}" -H "Content-Type: application/json" \
      -d '{"custom_collection":{"title":"Zen & Calm","published":true}}' | jq -r '.custom_collection.id')
    echo "Created collection Zen & Calm: $cid"
  fi
  echo -n "$cid"
}

COLLECTION_ID="$(ensure_collection)"

for line in "${ITEMS[@]}"; do
  SKU="${line%%$'\t'*}"
  TITLE="${line#*$'\t'}"
  echo "→ ${SKU} — ${TITLE}"

  # Find variant by SKU
  vdata=$(curl -s -H "X-Shopify-Access-Token: ${SHOPIFY_ADMIN_TOKEN}" \
    "https://${SHOP_DOMAIN}/admin/api/2024-10/variants.json?sku=$(python - <<PY
import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))
PY
"$SKU")")

  vid=$(echo "$vdata" | jq -r '.variants[0].id // empty')
  pid=$(echo "$vdata" | jq -r '.variants[0].product_id // empty')

  if [[ -z "$vid" || -z "$pid" ]]; then
    echo "  • Variant not found for SKU=$SKU; skip"
    continue
  fi

  # Mark product digital: type + tags
  curl -s -X PUT "https://${SHOP_DOMAIN}/admin/api/2024-10/products/${pid}.json" \
    -H "X-Shopify-Access-Token: ${SHOPIFY_ADMIN_TOKEN}" -H "Content-Type: application/json" \
    -d "{\"product\": {\"id\": ${pid}, \"product_type\": \"Digital Art\", \"tags\": \"digital,printable,abstract,zen,printbelle\"}}" \
    >/dev/null || true

  # Make variant non-shippable
  curl -s -X PUT "https://${SHOP_DOMAIN}/admin/api/2024-10/variants/${vid}.json" \
    -H "X-Shopify-Access-Token: ${SHOPIFY_ADMIN_TOKEN}" -H "Content-Type: application/json" \
    -d "{\"variant\": {\"id\": ${vid}, \"requires_shipping\": false}}" \
    >/dev/null || true

  # Ensure product is in the Zen & Calm collection
  curl -s -X POST "https://${SHOP_DOMAIN}/admin/api/2024-10/collects.json" \
    -H "X-Shopify-Access-Token: ${SHOPIFY_ADMIN_TOKEN}" -H "Content-Type: application/json" \
    -d "{\"collect\":{\"product_id\": ${pid}, \"collection_id\": ${COLLECTION_ID}}}" \
    >/dev/null || true

  echo "  • Patched SKU ${SKU} (pid=${pid}, vid=${vid})"
done

echo "Done."
