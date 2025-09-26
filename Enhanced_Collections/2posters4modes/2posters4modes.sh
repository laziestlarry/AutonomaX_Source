python3 -m venv .venv && source .venv/bin/activate
pip install pillow numpy

# Generate 8 pro posters using your titles, mapped across 4 modes (2 each)
python zen_calm_pro_maker.py \
  --outdir ZenCalm_Pro_Collection \
  --seed 4242 \
  --dpi 300 \
  --titles_json titles.json \
  --count 8
