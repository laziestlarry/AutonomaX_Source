#!/usr/bin/env bash
# Printbelle pipeline: set SKUs by Title (if needed) → patch digital + collection → upload images
# Works on macOS Bash 3.2 (no readarray), relies on Python scripts we created earlier.
set -euo pipefail

PACK_DIR="Printbelle_ZenCalm_Pack"
CSV="${CSV:-$PACK_DIR/shopify_products.csv}"
IMG_MAP="${IMG_MAP:-$PACK_DIR/image_map.csv}"

# ---- Env checks ----
if [ ! -f ".env" ]; then
  echo "Missing .env (expected SHOP_DOMAIN and SHOPIFY_ADMIN_TOKEN)"; exit 1
fi
# Export only the two needed vars
export $(grep -E '^(SHOP_DOMAIN|SHOPIFY_ADMIN_TOKEN)=' .env | xargs) || true
: "${SHOP_DOMAIN:?Set SHOP_DOMAIN in .env}"
: "${SHOPIFY_ADMIN_TOKEN:?Set SHOPIFY_ADMIN_TOKEN in .env}"

# ---- Scripts presence ----
PSCRIPT="$PACK_DIR/post_sync.py"
USCRIPT="$PACK_DIR/upload_images_by_sku.py"
SSCRIPT="$PACK_DIR/set_skus_by_title.py"

missing=0
for f in "$PSCRIPT" "$USCRIPT" "$SSCRIPT"; do
  if [ ! -f "$f" ]; then echo "Missing $f"; missing=1; fi
done
if [ $missing -eq 1 ]; then
  echo "One or more helper scripts are missing. Recreate them from our last step, then retry."
  exit 1
fi

# ---- Python deps ----
if [ -d ".venv" ]; then
  . .venv/bin/activate
fi
python - <<'PYI' >/dev/null 2>&1 || pip install requests >/dev/null
import pkgutil, sys
sys.exit(0 if pkgutil.find_loader("requests") else 1)
PYI

# ---- Files checks ----
[ -f "$CSV" ] || { echo "CSV not found: $CSV"; exit 1; }
[ -f "$IMG_MAP" ] || { echo "Image map not found: $IMG_MAP"; exit 1; }

echo ">>> STEP 1/3: Ensure Variant SKUs are set by Title (only needed if SKUs are null)"
python "$SSCRIPT" "$CSV" || true

echo ">>> STEP 2/3: Patch products digital + variants no-shipping + ensure 'Zen & Calm' collection"
python "$PSCRIPT" "$CSV"

echo ">>> STEP 3/3: Upload & attach images by SKU"
python "$USCRIPT" "$IMG_MAP"

echo "✅ Printbelle pipeline complete."
