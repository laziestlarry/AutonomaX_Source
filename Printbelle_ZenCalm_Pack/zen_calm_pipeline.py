#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zen & Calm Pipeline — generate commercial art + upload to Shopify OR emit Shopify-native CSV.

Modes:
  --mode api        Generate artworks & create draft products via Admin API (images embedded as base64)
  --mode csv        Generate artworks & write Shopify-native CSV (no image URLs) for Admin → Products → Import
  --mode attach     Attach images (base64) to products already created/imported (match by handle or title)

Requirements:
  pip install pillow numpy requests python-dotenv

Env (for API modes):
  SHOP_DOMAIN=autonomax.myshopify.com
  SHOPIFY_ADMIN_TOKEN=shpat_xxx
  SHOPIFY_API_VERSION=2024-04
"""
import os, csv, json, math, random, argparse, time, sys
from dataclasses import dataclass, asdict
from typing import Tuple, List, Dict
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
import base64, requests

# --------------------- Palettes & constants --------------------- #

PALETTES = {
    "dunes":  ["#f5efe6", "#efe8de", "#e0d7c9", "#cbbfb1", "#a9a093", "#7a7167"],
    "mist":   ["#f7f8fa", "#e8edf1", "#d4dde6", "#bfc9d3", "#a2aebc", "#8794a3"],
    "sage":   ["#f3f6f2", "#e3ece1", "#cfdecf", "#bbcfbc", "#9fb5a2", "#7c9480"],
    "latte":  ["#fbf7f1", "#f1e7d8", "#e3d2b9", "#cdb492", "#b39377", "#8e6e54"],
    "greige": ["#f8f7f6", "#eceae8", "#dfdcd9", "#cfcac6", "#b9b2ac", "#9a9189"],
}
ASPECTS = [
    ("4x5_16x20", 4, 5, 16, 20),
    ("3x4_18x24", 3, 4, 18, 24),
    ("2x3_24x36", 2, 3, 24, 36),
    ("a4", None, None, 8.27, 11.69),
]
DPI = 300

# --------------------- Small helpers --------------------- #

def hex_to_rgb(h): h=h.strip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return a + (b-a)*t
def blend(c1,c2,a): return tuple(int(lerp(c1[i], c2[i], a)) for i in range(3))
def unsharp(im, r=1.0, p=80, th=2): return im.filter(ImageFilter.UnsharpMask(radius=r, percent=p, threshold=th))

def add_canvas_texture(im, strength=0.05):
    w,h = im.size
    rng = np.random.default_rng(42)
    base = (rng.random((h,w))*255).astype(np.uint8)
    tex = Image.fromarray(base).convert("L").filter(ImageFilter.GaussianBlur(1.2))
    tex = ImageOps.autocontrast(tex)
    tex_rgb = ImageOps.colorize(tex, black=(0,0,0), white=(255,255,255))
    return Image.blend(im.convert("RGB"), tex_rgb, strength)

def ensure_border(im, pct=0.06, color=(250,250,247)):
    w,h = im.size; bw,bh = int(w*pct), int(h*pct)
    canvas = Image.new("RGB", (w+2*bw, h+2*bh), color); canvas.paste(im,(bw,bh)); return canvas

# --------------------- Art generator --------------------- #

def generate_base_art(w, h, palette, rng):
    im = Image.new("RGB",(w,h), hex_to_rgb(palette[0]))
    draw = ImageDraw.Draw(im,"RGBA")
    # soft vertical bands
    for i in range(6):
        col = hex_to_rgb(palette[1 + (i % (len(palette)-1))]) + (rng.randint(35,75),)
        x0 = int(lerp(0, w, i/6.0)) + rng.randint(-80,80); x1 = x0 + rng.randint(180,420)
        draw.rectangle([x0,0,x1,h], fill=col)
    # organic circles
    for i in range(8):
        r = rng.randint(int(min(w,h)*0.18), int(min(w,h)*0.38))
        x = rng.randint(-r, w+r); y = rng.randint(-r, h+r)
        col = hex_to_rgb(palette[rng.randint(2, len(palette)-1)]) + (rng.randint(60,110),)
        draw.ellipse([x-r,y-r,x+r,y+r], fill=col)
    im = im.filter(ImageFilter.GaussianBlur(2.2))
    # global gentle gradient
    top = hex_to_rgb(palette[-1]); bot = hex_to_rgb(palette[0])
    grad = Image.new("RGB",(1,h))
    for yy in range(h):
        t = yy/(h-1); c = blend(top, bot, t*0.25); grad.putpixel((0,yy), c)
    grad = grad.resize((w,h), Image.BILINEAR)
    im = Image.blend(im, grad, 0.25)
    im = add_canvas_texture(im, 0.05)
    im = unsharp(im, 1.0, 80, 2)
    return im

def save_web_variants(art, web_dir, watermark="Zen & Calm · Printbelle"):
    os.makedirs(web_dir, exist_ok=True)
    master_2048 = art.resize((2048, int(2048*1.25)), Image.LANCZOS)
    master_2048 = unsharp(master_2048, 0.8, 60, 2)
    master_2048.convert("RGB").save(os.path.join(web_dir,"master_2048.jpg"), "JPEG", quality=92, optimize=True, progressive=True)
    master_2048.convert("RGB").save(os.path.join(web_dir,"master_2048.webp"), "WEBP", quality=92, method=6)
    # preview
    prev = master_2048.copy().resize((1600, int(1600*1.25)), Image.LANCZOS)
    if watermark:
        d = ImageDraw.Draw(prev); 
        try: font = ImageFont.truetype("Arial.ttf", 36)
        except: font = ImageFont.load_default()
        text = watermark; bbox = d.textbbox((0,0), text, font=font); tw,th=bbox[2]-bbox[0],bbox[3]-bbox[1]
        pad=24
        d.rectangle([prev.width - tw - pad*2, prev.height - th - pad*2, prev.width, prev.height], fill=(255,255,255,160))
        d.text((prev.width - tw - pad, prev.height - th - pad), text, fill=(30,30,30,255), font=font)
    prev.save(os.path.join(web_dir,"preview_1600_watermarked.jpg"), "JPEG", quality=90, optimize=True, progressive=True)
    # thumb
    th = master_2048.copy().resize((1200, int(1200*1.25)), Image.LANCZOS)
    th.save(os.path.join(web_dir,"thumb_1200.jpg"), "JPEG", quality=88, optimize=True, progressive=True)
    return master_2048

def save_prints(art, pr_dir):
    os.makedirs(pr_dir, exist_ok=True)
    for name, ax, ay, in_w, in_h in ASPECTS:
        if name=="a4":
            px_w = int(8.27*DPI); px_h = int(11.69*DPI)
        else:
            px_w = int(in_w*DPI); px_h = int(in_h*DPI)
        canvas = Image.new("RGB",(px_w,px_h),(250,250,247))
        inner = (int(px_w*0.88), int(px_h*0.88))
        fitted = art.resize(inner, Image.LANCZOS)
        fitted = ensure_border(fitted, pct=0.03, color=(248,248,246))
        cx=(px_w-fitted.size[0])//2; cy=(px_h-fitted.size[1])//2
        canvas.paste(fitted,(cx,cy))
        canvas = unsharp(canvas, 1.2, 80, 3)
        canvas.save(os.path.join(pr_dir, f"{name}_300dpi.png"), "PNG", optimize=True)

def generate_wall_mockup(master_2048, framed=False):
    W,H=2800,1800
    wall = Image.new("RGB",(W,H),(236,236,232))
    vign = Image.new("L",(W,H),0); dv=ImageDraw.Draw(vign)
    dv.rectangle([int(W*0.06), int(H*0.06), int(W*0.94), int(H*0.94)], fill=255)
    vign=vign.filter(ImageFilter.GaussianBlur(80))
    wall = Image.composite(wall, Image.new("RGB",(W,H),(222,222,218)), vign)
    # floor
    floor_h=int(H*0.18); dr=ImageDraw.Draw(wall)
    dr.rectangle([0,H-floor_h,W,H], fill=(214,211,208))
    for i in range(16):
        x=int(i*(W/16)); dr.line([(x,H-floor_h),(x,H)], fill=(202,199,195), width=3)
    art_w=int(W*0.42)
    art = master_2048.copy().resize((art_w,int(art_w*1.25)), Image.LANCZOS)
    art = ensure_border(art, pct=0.05, color=(248,248,246))
    if framed:
        fw=24
        frame = Image.new("RGB",(art.size[0]+2*fw, art.size[1]+2*fw),(60,60,60))
        frame.paste(art,(fw,fw)); art=frame
    wall.paste(art,(int(W*0.5-art.size[0]/2), int(H*0.42-art.size[1]/2)))
    return wall

@dataclass
class ProductMeta:
    handle: str
    sku: str
    title: str
    description_html: str
    vendor: str
    product_type: str
    tags: str
    price_try: float
    palette: str
    seed: int
    collection: str
    web_master_path: str
    preview_path: str
    thumb_path: str

# --------------------- Shopify helpers (API) --------------------- #

def shopify_base():
    dom = os.environ.get("SHOP_DOMAIN")
    tok = os.environ.get("SHOPIFY_ADMIN_TOKEN")
    ver = os.environ.get("SHOPIFY_API_VERSION","2024-04")
    if not dom or not tok: 
        print("Set SHOP_DOMAIN and SHOPIFY_ADMIN_TOKEN for API modes.", file=sys.stderr)
        sys.exit(1)
    return f"https://{dom}/admin/api/{ver}", {"X-Shopify-Access-Token": tok, "Content-Type":"application/json"}

def shopify_create_product(base, headers, meta: ProductMeta, image_bytes=None, filename="image.png"):
    payload = {
        "product": {
            "title": meta.title,
            "body_html": meta.description_html,
            "vendor": meta.vendor,
            "product_type": meta.product_type,
            "tags": meta.tags,
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

def shopify_find_product_by_handle(base, headers, handle: str):
    r = requests.get(f"{base}/products.json?handle={handle}", headers=headers, timeout=30)
    if r.status_code == 200 and r.json().get("products"):
        return r.json()["products"][0]
    # Fallback: search by title (less reliable)
    r = requests.get(f"{base}/products.json?title={handle}", headers=headers, timeout=30)
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

# --------------------- Main pipeline --------------------- #

def run_generate(outdir, count, seed, collection, vendor, product_type, price_try, tags, palette, watermark):
    rng = random.Random(seed)
    manifest = []
    for i in range(1, count+1):
        sku = f"ZC-{i:03d}"
        handle = f"zen-calm-abstract-{i}"
        design_dir = os.path.join(outdir, "designs", sku)
        pr_dir = os.path.join(design_dir, "print")
        web_dir = os.path.join(design_dir, "web")
        mk_dir = os.path.join(design_dir, "mockups")
        os.makedirs(pr_dir, exist_ok=True); os.makedirs(web_dir, exist_ok=True); os.makedirs(mk_dir, exist_ok=True)

        pal_name = palette or rng.choice(list(PALETTES.keys()))
        pal = PALETTES[pal_name]
        # base art (work size)
        w = 3200; h = int(w*1.25)
        art = generate_base_art(w, h, pal, rng)
        # web
        master_2048 = save_web_variants(art, web_dir, watermark)
        # prints
        save_prints(art, pr_dir)
        # mockups
        mk1 = generate_wall_mockup(master_2048, framed=False); mk1.save(os.path.join(mk_dir,"wall_mockup_1.jpg"), "JPEG", quality=90, optimize=True)
        mk2 = generate_wall_mockup(master_2048, framed=True); mk2.save(os.path.join(mk_dir,"framed_mockup_1.jpg"), "JPEG", quality=90, optimize=True)

        title = f"Zen & Calm Abstract #{i} — Minimal Serenity Wall Art (Digital Printable)"
        desc_html = (
            "<p>A soothing, minimal abstract printable from the Zen & Calm collection. "
            "Perfect for living rooms, bedrooms, and mindful workspaces.</p>"
            "<ul><li>High-resolution PNGs (300 DPI)</li>"
            "<li>Ratios included: 4×5, 3×4, 2×3, A4, 16×20 in</li>"
            "<li>License: Personal use</li></ul>"
        )

        meta = ProductMeta(
            handle=handle, sku=sku, title=title, description_html=desc_html,
            vendor=vendor, product_type=product_type, tags=tags, price_try=price_try,
            palette=pal_name, seed=seed, collection=collection,
            web_master_path=os.path.join(web_dir,"master_2048.jpg"),
            preview_path=os.path.join(web_dir,"preview_1600_watermarked.jpg"),
            thumb_path=os.path.join(web_dir,"thumb_1200.jpg"),
        )
        with open(os.path.join(design_dir,"meta.json"),"w",encoding="utf-8") as f: json.dump(asdict(meta), f, indent=2, ensure_ascii=False)
        manifest.append(meta)
        print(f"✔ Generated {sku} ({pal_name})")
    # collection-level manifest
    with open(os.path.join(outdir,"manifest.csv"),"w",newline="",encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(asdict(manifest[0]).keys()))
        wr.writeheader(); [wr.writerow(asdict(m)) for m in manifest]
    return manifest

def mode_api(manifest):
    base, headers = shopify_base()
    for m in manifest:
        with open(m.web_master_path,"rb") as fh:
            img = fh.read()
        product = shopify_create_product(base, headers, m, image_bytes=img, filename=os.path.basename(m.web_master_path))
        if product:
            print(f"Created: {product.get('id')}  {m.title}")
        time.sleep(0.5)

def mode_attach(manifest):
    base, headers = shopify_base()
    for m in manifest:
        prod = shopify_find_product_by_handle(base, headers, m.handle) or shopify_find_product_by_handle(base, headers, m.title)
        if not prod:
            print(f"SKIP attach: not found {m.handle}")
            continue
        with open(m.web_master_path,"rb") as fh:
            ok = shopify_attach_image(base, headers, prod["id"], fh.read(), os.path.basename(m.web_master_path))
        print(f"Attach to {prod['id']} -> {ok}")
        time.sleep(0.5)

def mode_csv(manifest, out_csv):
    """
    Shopify-native CSV (minimal set). Image Src left blank (Shopify requires public URLs).
    After import, optionally run --mode attach to add images via API.
    """
    cols = [
        "Handle","Title","Body (HTML)","Vendor","Type","Tags","Published",
        "Option1 Name","Option1 Value",
        "Variant SKU","Variant Grams","Variant Inventory Tracker","Variant Inventory Qty",
        "Variant Inventory Policy","Variant Fulfillment Service","Variant Price","Variant Requires Shipping",
        "Variant Taxable","Status","Image Src","Image Alt Text"
    ]
    with open(out_csv,"w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for m in manifest:
            w.writerow({
                "Handle": m.handle,
                "Title": m.title,
                "Body (HTML)": m.description_html,
                "Vendor": m.vendor,
                "Type": m.product_type,
                "Tags": m.tags,
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
    print(f"➡ Wrote Shopify import CSV: {out_csv}")
    print("Note: Images not included (Shopify import requires public URLs). After import, run:")
    print("  python zen_calm_pipeline.py --mode attach --outdir <same>")

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["api","csv","attach"], required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--collection", default="Zen & Calm")
    ap.add_argument("--vendor", default="Printbelle")
    ap.add_argument("--product_type", default="Digital Art Print")
    ap.add_argument("--price_try", type=float, default=129.90)
    ap.add_argument("--tags", default="zen,calm,minimal,abstract,printable,wall art")
    ap.add_argument("--palette", choices=list(PALETTES.keys()))
    ap.add_argument("--watermark", default="Zen & Calm · Printbelle")
    ap.add_argument("--csv_path", default="shopify_import.csv")
    return ap.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    manifest = run_generate(args.outdir, args.count, args.seed, args.collection,
                            args.vendor, args.product_type, args.price_try, args.tags,
                            args.palette, args.watermark)
    if args.mode == "api":
        mode_api(manifest)
    elif args.mode == "csv":
        mode_csv(manifest, os.path.join(args.outdir, args.csv_path))
    elif args.mode == "attach":
        mode_attach(manifest)

if __name__ == "__main__":
    main()