#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zen & Calm — Pro Pipeline
Generates best-seller Zen posters (pro composition, textures, typography) and
- creates Shopify products via Admin API (draft, with 2048px image), and/or
- writes Shopify-native CSV (draft), with an attach mode to add images later.

Modes:
  --mode api     Generate & upload to Shopify (images attached)
  --mode csv     Generate & export Shopify-native CSV
  --mode attach  Attach images to products already in Shopify (after CSV import)
  --mode both    Generate & do BOTH api + csv in one pass

Requirements:
  pip install pillow numpy requests python-dotenv

Env (for API modes):
  SHOP_DOMAIN=autonomax.myshopify.com
  SHOPIFY_ADMIN_TOKEN=shpat_xxx
  SHOPIFY_API_VERSION=2024-04
"""
import os, csv, json, math, random, argparse, time, sys
from dataclasses import dataclass, asdict
from typing import List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
import base64, requests

# ---------------- Palettes & Modes ---------------- #

PALETTES = {
    "boho_warm": ["#ffffff","#f4efe8","#e8ded1","#d7c4b3","#caa28a","#b5745c","#8f4e3b"],
    "sacred_muted": ["#f7f7f6","#e9ecef","#d7dfe6","#c7d1d8","#adbcc6","#8696a6","#5c6a74"],
    "calm_flow": ["#f6f6f6","#edeae6","#e1e3db","#d4dfd3","#c3d3c7","#aebfb3","#8aa296"],
    "modern_harmony": ["#ffffff","#f2f1ef","#e6e3df","#d6d0cb","#c4bbb4","#a99c94","#857a73"]
}
MODES = {
    1: {"name":"Minimalist Zen Boho", "palette":"boho_warm", "bg":"#ffffff"},
    2: {"name":"Sacred Geometry Zen", "palette":"sacred_muted", "bg":"#f7f7f6"},
    3: {"name":"Calm Flow Abstract",  "palette":"calm_flow",  "bg":"#f6f6f6"},
    4: {"name":"Modern Harmony",      "palette":"modern_harmony", "bg":"#ffffff"},
}
ASPECTS = [
    ("4x5_16x20", 16, 20),
    ("3x4_18x24", 18, 24),
    ("2x3_24x36", 24, 36),
    ("a4", 8.27, 11.69),
]

# ---------------- Utils ---------------- #

def hex_to_rgb(h): h=h.strip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return a + (b-a)*t
def blend(c1,c2,t): return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))
def pick_font(size=48, pref=("Avenir.ttf","Inter.ttf","Helvetica.ttf","Arial.ttf")):
    for p in pref:
        try: return ImageFont.truetype(p, size=size)
        except: pass
    return ImageFont.load_default()
def soften(im, r=1.5): return im.filter(ImageFilter.GaussianBlur(r))
def unsharp(im, r=1.2, p=120, th=3): return im.filter(ImageFilter.UnsharpMask(r,p,th))

def vignette(im, strength=0.12):
    w,h = im.size
    mask = Image.new("L",(w,h),255)
    d = ImageDraw.Draw(mask)
    pad = int(min(w,h)*0.06)
    d.rectangle([pad,pad,w-pad,h-pad], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(int(min(w,h)*0.08)))
    base = Image.new("RGB",(w,h),(0,0,0))
    return Image.composite(im, Image.blend(im, base, strength), ImageOps.invert(mask))

def paper_grain(im, strength=0.06, seed=7):
    rng = np.random.default_rng(seed)
    noise = (rng.random((im.size[1], im.size[0]))*255).astype(np.uint8)
    tex = Image.fromarray(noise).filter(ImageFilter.GaussianBlur(1.2))
    tex = ImageOps.autocontrast(tex)
    tex = ImageOps.colorize(tex, black=(220,220,220), white=(255,255,255))
    return Image.blend(im.convert("RGB"), tex, strength)

def watercolor_wash(im, color=(255,255,255), alpha=0.12, radius=16):
    wash = Image.new("RGB", im.size, color).filter(ImageFilter.GaussianBlur(radius))
    return Image.blend(im, wash, alpha)

def deckled_edges(im, amount=0.06, seed=11):
    rng = random.Random(seed)
    w,h = im.size
    mask = Image.new("L",(w,h),255)
    d = ImageDraw.Draw(mask)
    for edge in range(4):
        pts = []
        N = 50
        if edge%2==0:  # top/bottom
            y = 0 if edge==0 else h-1
            for k in range(N):
                x = int(k*(w/N))
                r = rng.randint(0, int(h*amount))
                pts.append((x, y + (r if edge==0 else -r)))
        else:  # left/right
            x = 0 if edge==1 else w-1
            for k in range(N):
                y = int(k*(h/N))
                r = rng.randint(0, int(w*amount))
                pts.append((x + (r if edge==1 else -r), y))
        d.line(pts, fill=0, width=1)
    mask = soften(mask, 6).filter(ImageFilter.GaussianBlur(8))
    base = Image.new("RGB",(w,h),(255,255,255))
    return Image.composite(im, base, mask)

def horizon_y(h, mode_id): return int(h * {1:0.62, 2:0.58, 3:0.64, 4:0.60}[mode_id])

# ---------------- Composition Primitives ---------------- #

def draw_circle(d, cx, cy, r, fill): d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)
def draw_arch(d, cx, cy, r_outer, r_inner, fill):
    d.pieslice([cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer], 180, 0, fill=fill)
    d.pieslice([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], 180, 0, fill=None)
    d.rectangle([cx-r_inner, cy, cx+r_inner, cy+r_inner], fill="#00000000")
def draw_triangle(d, pts, fill): d.polygon(pts, fill=fill)

def draw_wave(d, w, y_mid, amp, periods, color, alpha=140, seed=5):
    rng = random.Random(seed); pts=[]
    for x in range(0, w+1, 8):
        t = (x / w) * (2*math.pi*periods)
        y = y_mid + amp*math.sin(t) + rng.uniform(-amp*0.08, amp*0.08)
        pts.append((x, y))
    pts += [(w, y_mid+amp*2), (0, y_mid+amp*2)]
    r,g,b = hex_to_rgb(color)
    d.polygon(pts, fill=(r,g,b,alpha))

# ---------------- Mode Renderers ---------------- #

def render_minimalist_zen_boho(im, palette, rng):
    d = ImageDraw.Draw(im, "RGBA"); w,h=im.size
    main_r = int(min(w,h)*0.18); cx,cy=int(w*0.5), int(h*0.42)
    draw_circle(d, cx, cy, main_r, (*hex_to_rgb(palette[4]), 220))
    hy = horizon_y(h, 1)
    d.rectangle([int(w*0.12), hy, int(w*0.88), hy+int(h*0.06)], fill=(*hex_to_rgb(palette[5]),190))
    draw_circle(d, int(w*0.32), int(h*0.30), int(main_r*0.42), (*hex_to_rgb(palette[3]),200))

def render_sacred_geometry_zen(im, palette, rng):
    d = ImageDraw.Draw(im, "RGBA"); w,h=im.size; cx,cy=int(w*0.5), int(h*0.46)
    for i in range(5):
        r = int(min(w,h)*0.22 * (1 - i*0.12))
        draw_circle(d, cx, cy, r, (*hex_to_rgb(palette[2+i%3]), int(210 - i*20)))
    draw_arch(d, cx, cy, int(min(w,h)*0.38), int(min(w,h)*0.28), (*hex_to_rgb(palette[5]),140))
    tri_w = int(w*0.28); pts=[(cx-tri_w//2, cy+int(h*0.18)), (cx+tri_w//2, cy+int(h*0.18)), (cx, cy+int(h*0.02))]
    draw_triangle(d, pts, (*hex_to_rgb(palette[4]), 150))

def render_calm_flow_abstract(im, palette, rng):
    d = ImageDraw.Draw(im, "RGBA"); w,h=im.size; hy=horizon_y(h,3)
    for i, col in enumerate(palette[2:]):
        draw_wave(d, w, hy - i*int(h*0.03), amp=int(h*0.035*(1+i*0.15)),
                  periods=1.5+i*0.35, color=col, alpha=120+i*20, seed=33+i)
    draw_circle(d, int(w*0.68), int(h*0.34), int(min(w,h)*0.12), (*hex_to_rgb(palette[4]), 210))

def render_modern_harmony(im, palette, rng):
    d = ImageDraw.Draw(im, "RGBA"); w,h=im.size; cx,cy=int(w*0.5), int(h*0.46)
    bar_w=int(w*0.62)
    d.rectangle([cx-bar_w//2, cy-int(h*0.02), cx+bar_w//2, cy+int(h*0.02)], fill=(*hex_to_rgb(palette[5]),200))
    r_outer=int(min(w,h)*0.28); r_inner=int(r_outer*0.78)
    draw_arch(d, cx, cy, r_outer, r_inner, (*hex_to_rgb(palette[4]),180))
    draw_circle(d, int(w*0.35), int(h*0.33), int(min(w,h)*0.10), (*hex_to_rgb(palette[3]),210))
    d.rectangle([int(w*0.58), int(h*0.60), int(w*0.80), int(h*0.72)], fill=(*hex_to_rgb(palette[2]), 180))

MODE_RENDER = {1:render_minimalist_zen_boho, 2:render_sacred_geometry_zen, 3:render_calm_flow_abstract, 4:render_modern_harmony}

# ---------------- Export helpers ---------------- #

def title_block(im, title, subtitle, top_pct=0.085, pad_pct=0.06):
    if not title and not subtitle: return im
    w,h=im.size; d=ImageDraw.Draw(im)
    title_font = pick_font(size=int(h*0.045))
    sub_font   = pick_font(size=int(h*0.026))
    top=int(h*top_pct); pad=int(w*pad_pct)
    tw,th = d.textbbox((0,0), title, font=title_font)[2:]
    d.text((pad, top), title, fill=(24,24,24), font=title_font)
    if subtitle:
        d.text((pad, top + th + int(h*0.012)), subtitle, fill=(70,70,70), font=sub_font)
    return im

def add_textures(im, mode_id, seed):
    bg = paper_grain(im, strength=0.06 if mode_id in (1,4) else 0.08, seed=seed+3)
    bg = watercolor_wash(bg, color=(255,255,255), alpha=0.10 if mode_id in (1,4) else 0.12, radius=16)
    bg = vignette(bg, strength=0.10 if mode_id in (1,3) else 0.12)
    bg = deckled_edges(bg, amount=0.06, seed=seed+9)
    return unsharp(bg, 1.0, 80, 3)

def simple_mockup(master_2048, framed=False):
    W,H=2800,1800
    wall = Image.new("RGB",(W,H),(236,236,232))
    mask=Image.new("L",(W,H),0); d=ImageDraw.Draw(mask); pad=int(min(W,H)*0.08)
    d.rectangle([pad,pad,W-pad,H-pad], fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(60))
    wall = Image.composite(wall, Image.new("RGB",(W,H),(222,222,218)), mask)
    floor_h=int(H*0.20); d2=ImageDraw.Draw(wall); d2.rectangle([0,H-floor_h,W,H], fill=(214,211,208))
    for i in range(18):
        x=int(i*(W/18)); d2.line([(x,H-floor_h),(x,H)], fill=(202,199,195), width=3)
    art_w=int(W*0.44)
    art = master_2048.copy().resize((art_w,int(art_w*1.25)), Image.LANCZOS)
    art = ImageOps.expand(art, border=int(art_w*0.05), fill=(248,248,246))
    if framed:
        fw=int(art_w*0.012)
        art = ImageOps.expand(art, border=fw, fill=(60,60,60))
    wall.paste(art,(int(W*0.5-art.size[0]/2), int(H*0.42-art.size[1]/2)))
    return wall

# ---------------- Data models ---------------- #

@dataclass
class Meta:
    sku: str
    handle: str
    title: str
    subtitle: str
    mode: str
    price_try: float
    palette: str
    seed: int
    web_master: str
    preview: str
    thumb: str

# ---------------- Shopify helpers ---------------- #

def shopify_base():
    dom = os.environ.get("SHOP_DOMAIN")
    tok = os.environ.get("SHOPIFY_ADMIN_TOKEN")
    ver = os.environ.get("SHOPIFY_API_VERSION","2024-04")
    if not dom or not tok:
        print("Set SHOP_DOMAIN and SHOPIFY_ADMIN_TOKEN for API modes.", file=sys.stderr)
        sys.exit(1)
    return f"https://{dom}/admin/api/{ver}", {"X-Shopify-Access-Token": tok, "Content-Type":"application/json"}

def shopify_create_product(base, headers, meta: Meta, image_bytes=None, filename="image.jpg"):
    payload = {
        "product": {
            "title": meta.title,
            "body_html": (
                "<p>A soothing, minimal abstract print inspired by Zen balance. "
                "Professional poster design, subtle paper texture.</p>"
                "<ul><li>High-resolution PNGs (300 DPI)</li>"
                "<li>Ratios: 4×5, 3×4, 2×3, A4, 16×20 in</li>"
                "<li>License: Personal use</li></ul>"
            ),
            "vendor": "Printbelle",
            "product_type": "Digital Art Print",
            "tags": "zen,calm,minimal,abstract,boho,poster,wall art",
            "status": "draft",
            "variants": [{
                "price": f"{meta.price_try:.2f}",
                "sku": meta.sku,
                "inventory_policy": "deny",
                "requires_shipping": False
            }],
            "images": []
        }
    }
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        payload["product"]["images"].append({"attachment": b64, "filename": filename})
    r = requests.post(f"{base}/products.json", headers=headers, json=payload, timeout=60)
    if r.status_code >= 300:
        print("ERROR create:", r.status_code, r.text)
        return None
    return r.json().get("product", {})

def shopify_find_product_by_handle(base, headers, handle_or_title: str):
    # The products endpoint doesn't filter directly by handle; try title first
    r = requests.get(f"{base}/products.json?title={handle_or_title}", headers=headers, timeout=30)
    if r.status_code == 200 and r.json().get("products"):
        return r.json()["products"][0]
    return None

def shopify_attach_image(base, headers, product_id: int, image_bytes: bytes, filename: str):
    payload = {"image": {"attachment": base64.b64encode(image_bytes).decode("utf-8"), "filename": filename}}
    r = requests.post(f"{base}/products/{product_id}/images.json", headers=headers, json=payload, timeout=60)
    if r.status_code >= 300:
        print("ERROR attach image:", r.status_code, r.text)
        return False
    return True

# ---------------- Generation ---------------- #

def render_by_mode(mode_id, base_im, palette_hex, rng):
    if mode_id==1: render_minimalist_zen_boho(base_im, palette_hex, rng)
    elif mode_id==2: render_sacred_geometry_zen(base_im, palette_hex, rng)
    elif mode_id==3: render_calm_flow_abstract(base_im, palette_hex, rng)
    else: render_modern_harmony(base_im, palette_hex, rng)

def generate_piece(outdir, idx, mode_id, title, subtitle, price_try, dpi, seed):
    rng = random.Random(seed + idx*31)
    mode = MODES[mode_id]
    palette_hex = PALETTES[mode["palette"]]
    bg_color = hex_to_rgb(mode["bg"])

    W,H = 3200, 4000
    poster = Image.new("RGB",(W,H), bg_color)
    render_by_mode(mode_id, poster, palette_hex, rng)
    poster = title_block(poster, title, subtitle, top_pct=0.085, pad_pct=0.06)
    poster = add_textures(poster, mode_id, seed=seed+idx*7)

    # web
    web_dir = os.path.join(outdir,"web"); os.makedirs(web_dir, exist_ok=True)
    master_2048 = poster.resize((2048, int(2048*1.25)), Image.LANCZOS)
    master_path = os.path.join(web_dir, f"master_{idx:02d}_2048.jpg")
    master_2048.save(master_path, "JPEG", quality=92, optimize=True, progressive=True)
    prev_path = os.path.join(web_dir, f"preview_{idx:02d}_1600.jpg")
    master_2048.copy().save(prev_path, "JPEG", quality=90, optimize=True, progressive=True)
    thumb_path = os.path.join(web_dir, f"thumb_{idx:02d}_1200.jpg")
    master_2048.copy().resize((1200,int(1200*1.25)), Image.LANCZOS).save(thumb_path, "JPEG", quality=88, optimize=True, progressive=True)

    # print masters @ DPI
    print_dir = os.path.join(outdir,"print"); os.makedirs(print_dir, exist_ok=True)
    for name, in_w, in_h in ASPECTS:
        px_w, px_h = int(in_w*dpi), int(in_h*dpi)
        canvas = Image.new("RGB",(px_w,px_h),(252,252,250))
        inner = (int(px_w*0.84), int(px_h*0.84))
        fitted = poster.resize(inner, Image.LANCZOS)
        fitted = ImageOps.expand(fitted, border=int(min(inner)*0.03), fill=(248,248,246))
        cx,cy = (px_w - fitted.size[0])//2, (px_h - fitted.size[1])//2
        canvas.paste(fitted,(cx,cy))
        unsharp(canvas, 1.0, 70, 3).save(os.path.join(print_dir, f"{name}_{idx:02d}_{dpi}dpi.png"), "PNG", optimize=True)

    # mockups
    mk_dir=os.path.join(outdir,"mockups"); os.makedirs(mk_dir, exist_ok=True)
    simple_mockup(master_2048, framed=False).save(os.path.join(mk_dir, f"wall_{idx:02d}.jpg"), "JPEG", quality=90, optimize=True)
    simple_mockup(master_2048, framed=True).save(os.path.join(mk_dir, f"framed_{idx:02d}.jpg"), "JPEG", quality=90, optimize=True)

    sku = f"ZCP-{idx:03d}"
    handle = f"zen-calm-pro-{idx}"
    return Meta(
        sku=sku, handle=handle, title=title, subtitle=subtitle,
        mode=mode["name"], price_try=price_try, palette=mode["palette"], seed=seed,
        web_master=os.path.join("web", f"master_{idx:02d}_2048.jpg"),
        preview=os.path.join("web", f"preview_{idx:02d}_1600.jpg"),
        thumb=os.path.join("web", f"thumb_{idx:02d}_1200.jpg")
    )

def run_generate(batch_outdir, count, seed, dpi, titles):
    metas=[]
    os.makedirs(batch_outdir, exist_ok=True)
    for i in range(1, count+1):
        mode_id = ((i-1) % 4) + 1
        if i-1 < len(titles):
            t = titles[i-1]; title=t.get("title") or f"Zen & Calm #{i}"; subtitle=t.get("subtitle") or MODES[mode_id]["name"]
        else:
            title=f"Zen & Calm #{i}"; subtitle=MODES[mode_id]["name"]
        item_dir = os.path.join(batch_outdir, f"ZCP_{i:03d}")
        os.makedirs(item_dir, exist_ok=True)
        meta = generate_piece(item_dir, i, mode_id, title, subtitle, price_try=129.90, dpi=dpi, seed=seed)
        metas.append(meta)
        print(f"✓ {meta.sku} — {meta.title} [{MODES[mode_id]['name']}]")
    # manifest
    with open(os.path.join(batch_outdir,"manifest.csv"),"w",newline="",encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(asdict(metas[0]).keys()))
        wr.writeheader(); [wr.writerow(asdict(m)) for m in metas]
    return metas

# ---------------- CSV & API modes ---------------- #

def write_shopify_csv(metas, out_csv):
    cols = [
        "Handle","Title","Body (HTML)","Vendor","Type","Tags","Published",
        "Option1 Name","Option1 Value",
        "Variant SKU","Variant Grams","Variant Inventory Tracker","Variant Inventory Qty",
        "Variant Inventory Policy","Variant Fulfillment Service","Variant Price","Variant Requires Shipping",
        "Variant Taxable","Status","Image Src","Image Alt Text"
    ]
    with open(out_csv,"w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for m in metas:
            w.writerow({
                "Handle": m.handle,
                "Title": m.title,
                "Body (HTML)": "<p>Minimalist Zen wall print. Professional poster design, subtle textures.</p>",
                "Vendor": "Printbelle",
                "Type": "Digital Art Print",
                "Tags": "zen,calm,minimal,abstract,boho,poster,wall art",
                "Published": "FALSE",
                "Option1 Name": "Title",
                "Option1 Value": "Default Title",
                "Variant SKU": m.sku,
                "Variant Grams": 0,
                "Variant Inventory Tracker": "",
                "Variant Inventory Qty": 0,
                "Variant Inventory Policy": "deny",
                "Variant Fulfillment Service": "manual",
                "Variant Price": f"{m.price_try:.2f}",
                "Variant Requires Shipping": "FALSE",
                "Variant Taxable": "FALSE",
                "Status": "draft",
                "Image Src": "",
                "Image Alt Text": "Zen & Calm abstract wall art"
            })
    print(f"➡ Shopify import CSV written: {out_csv}")
    print("Note: Images omitted (Shopify CSV requires public URLs). Use --mode attach after import, or host images and fill Image Src.")

def api_create_products(batch_outdir, metas):
    base, headers = shopify_base()
    for m in metas:
        img_path = os.path.join(batch_outdir, m.web_master)
        with open(img_path, "rb") as fh: img = fh.read()
        product = shopify_create_product(base, headers, m, image_bytes=img, filename=os.path.basename(img_path))
        if product:
            print(f"Created: {product.get('id')}  {m.title}")
        time.sleep(0.5)

def api_attach_images(batch_outdir, metas):
    base, headers = shopify_base()
    for m in metas:
        prod = shopify_find_product_by_handle(base, headers, m.title) or shopify_find_product_by_handle(base, headers, m.handle)
        if not prod:
            print(f"SKIP attach: not found {m.handle}")
            continue
        img_path = os.path.join(batch_outdir, m.web_master)
        with open(img_path, "rb") as fh: ok = shopify_attach_image(base, headers, prod["id"], fh.read(), os.path.basename(img_path))
        print(f"Attach to {prod['id']} -> {ok}")
        time.sleep(0.5)

# ---------------- CLI ---------------- #

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["api","csv","attach","both"], required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--count", type=int, default=8)
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--price_try", type=float, default=129.90)
    ap.add_argument("--titles_json", help="Path to JSON list of {title, subtitle}")
    ap.add_argument("--csv_path", default="shopify_import.csv")
    return ap.parse_args()

def main():
    args = parse_args()
    titles=[]
    if args.titles_json and os.path.exists(args.titles_json):
        with open(args.titles_json,"r",encoding="utf-8") as f: titles=json.load(f)

    # Generate art & metadata
    metas = run_generate(args.outdir, args.count, args.seed, args.dpi, titles)

    # update TRY price across metas (if changed via CLI)
    for m in metas: m.price_try = args.price_try

    if args.mode == "api":
        api_create_products(args.outdir, metas)
    elif args.mode == "csv":
        write_shopify_csv(metas, os.path.join(args.outdir, args.csv_path))
    elif args.mode == "attach":
        api_attach_images(args.outdir, metas)
    elif args.mode == "both":
        api_create_products(args.outdir, metas)
        write_shopify_csv(metas, os.path.join(args.outdir, args.csv_path))
        print("Both API creation and CSV export completed.")

if __name__ == "__main__":
    main()
