export SHOP_DOMAIN=autonomax.myshopify.com
export SHOPIFY_ADMIN_TOKEN=shpat_xxx

python zen_calm_pro_pipeline.py \
  --mode both \
  --outdir ZenCalm_Pro_Collection \
  --count 8 \
  --seed 4242 \
  --dpi 300 \
  --price_try 129.90 \
  --titles_json titles.json \
  --csv_path shopify_import.csv
