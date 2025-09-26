# Printbelle: Zen & Calm Pack (v20250917)

This pack contains 10 digital wall-art products for **Shopify**.

## Contents
- `shopify_products.csv` — importable CSV (no image URLs yet)
- `images/` — 10 high-res PNGs (1600x2000)
- `image_map.csv` — SKU → local image path mapping
- `post_sync.sh` — patches products to be digital + assigns **Zen & Calm** collection after import

## Quick Start
1. Import CSV: Shopify Admin → Products → Import → upload `shopify_products.csv`.
2. Ensure `.env` has `SHOP_DOMAIN` and `SHOPIFY_ADMIN_TOKEN`, then export them in your shell.
3. Run post-patch:
   ```bash
   cd /Users/pq/AutonomaX_AI_Integration_Starter_v11_full
   export $(grep -E '^(SHOP_DOMAIN|SHOPIFY_ADMIN_TOKEN)=' .env | xargs)
   bash /path/to/post_sync.sh shopify_products.csv
   ```

### Images
Shopify CSV requires public URLs for `Image Src`. We included local PNGs instead.
Options:
- Manually upload each image on the product page.
- Host images (GitHub/GCS) + place URLs into CSV and re-import as update.
- Ask me to generate a script to upload to Shopify Files and attach automatically.

