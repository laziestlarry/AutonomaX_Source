export SHOP_DOMAIN=autonoma-x.myshopify.com
export SHOPIFY_ADMIN_TOKEN=shpat_xxx
export SHOPIFY_API_VERSION=2024-04

python zen_calm_pro_pipeline.py \
  --mode api \
  --outdir ZenCalm_Pro_Collection \
  --count 8 \
  --seed 4242 \
  --dpi 300 \
  --price_try 129.90 \
  --titles_json titles.json
