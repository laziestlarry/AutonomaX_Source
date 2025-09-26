#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zen & Calm Art Maker — commercial-ready abstract printables with previews & mockups.

Features
- 300 DPI print masters in common aspect ratios (A4, 4x5, 3x4, 2x3, 16x20 inches)
- Clean, minimal, calming palettes + deterministic seed
- Web images (JPG/WebP), preview watermark, Shopify-friendly 2048px master
- Simple room/framed mockups (generated locally)
- SKU + metadata (JSON + CSV manifest)

Requirements: pillow, numpy
  pip install pillow numpy

Author: AutonomaX / ProPulse
"""
import os, csv, json, math, random, argparse, time
from dataclasses import dataclass, asdict
from typing import Tuple, List, Dict
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont

# ---------------------------- Config & Palettes ---------------------------- #

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
    ("a4", None, None, 8.27, 11.69),  # A4 inches
]

DPI = 300

# ---------------------------- Helpers ---------------------------- #

def hex_to_rgb(h):  # "#aabbcc" -> (r,g,b)
    h = h.strip("#")
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def lerp(a, b, t): return a + (b - a) * t

def blend(c1, c2, alpha):
    return tuple(int(lerp(c1[i], c2[i], alpha)) for i in range(3))

def soft_noise(w, h, seed=0, octaves=3, smooth=0.8):
    rng = np.random.default_rng(seed)
    base = rng.random((h, w))
    img = base.copy()
    # multi-scale blur to get soft gradients
    for o in range(1, octaves+1):
        k = int(max(1, (min(w,h) // (8*(2**o)))))
        if k % 2 == 0: k += 1
        arr = Image.fromarray((img*255).astype(np.uint8))
        arr = arr.filter(ImageFilter.GaussianBlur(radius=k*smooth))
        img = np.array(arr)/255.0
        img = (img + base*0.15) / 1.15
    img = (img - img.min()) / (img.max() - img.min() + 1e-6)
    return img

def add_canvas_texture(im: Image.Image, strength=0.035):
    """Subtle paper/canvas texture."""
    w, h = im.size
    noise = (soft_noise(w, h, seed=42, octaves=2, smooth=0.9)*255).astype(np.uint8)
    tex = Image.fromarray(noise).convert("L").filter(ImageFilter.GaussianBlur(1.2))
    tex = ImageOps.autocontrast(tex)
    tex = ImageEnhance(im, tex, strength)
    return tex

def ImageEnhance(base: Image.Image, graymask: Image.Image, strength: float):
    """Blend grayscale texture into base luminance."""
    base = base.convert("RGB")
    g = graymask.resize(base.size, Image.BICUBIC)
    g = ImageOps.colorize(g, black=(0,0,0), white=(255,255,255))
    return Image.blend(base, g, strength)

def gamma_correct(im: Image.Image, gamma=1.0):
    if abs(gamma - 1.0) < 1e-6: return im
    lut = [min(255, int((i/255.0)**(1/gamma)*255)) for i in range(256)]
    return im.point(lut*3)

def ensure_min_border(im: Image.Image, pct=0.06, color=(250,250,247)):
    """Add white-ish border around art to be frame-friendly and text-safe."""
    w, h = im.size
    bw, bh = int(w*pct), int(h*pct)
    canvas = Image.new("RGB", (w + 2*bw, h + 2*bh), color)
    canvas.paste(im, (bw, bh))
    return canvas

def unsharp_mask(im: Image.Image, radius=1.2, percent=120, threshold=3):
    return im.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))

def save_web(im: Image.Image, path_jpg: str, path_webp: str, quality=90):
    im_jpg = im.convert("RGB")
    im_jpg.save(path_jpg, "JPEG", quality=quality, optimize=True, progressive=True)
    im_webp = im.convert("RGB")
    im_webp.save(path_webp, "WEBP", quality=quality, method=6)

# ---------------------------- Core Generator ---------------------------- #

def generate_base_art(w, h, palette: List[Tuple[int,int,int]], rng: random.Random):
    """Minimal abstract composition: soft gradients + layered shapes + mask blends."""
    # Start with gradient
    im = Image.new("RGB", (w, h), palette[0])
    draw = ImageDraw.Draw(im, "RGBA")

    # Vertical soft bands
    for i in range(6):
        c = tuple(list(palette[1 + (i % (len(palette)-1))]) + [rng.randint(35, 75)])
        x0 = int(lerp(0, w, i/6.0)) + rng.randint(-80, 80)
        x1 = x0 + rng.randint(180, 420)
        draw.rectangle([x0, 0, x1, h], fill=c)

    # Large organic circles
    for i in range(8):
        r = rng.randint(int(min(w,h)*0.18), int(min(w,h)*0.38))
        x = rng.randint(-r, w+r)
        y = rng.randint(-r, h+r)
        c = tuple(list(palette[rng.randint(2, len(palette)-1)]) + [rng.randint(60, 110)])
        draw.ellipse([x-r, y-r, x+r, y+r], fill=c)

    # Soften
    im = im.filter(ImageFilter.GaussianBlur(radius=2.2))

    # Global gentle gradient blend top→bottom
    top = palette[-1]
    bot = palette[0]
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        t = y/(h-1)
        c = blend(top, bot, t*0.25)  # subtle
        grad.putpixel((0, y), c)
    grad = grad.resize((w, h), Image.BILINEAR)
    im = Image.blend(im, grad, 0.25)

    # Add texture
    im = add_canvas_texture(im, strength=0.05)

    # Gentle contrast and sharpen
    im = gamma_correct(im, 1.05)
    im = unsharp_mask(im, radius=1.0, percent=80, threshold=2)

    return im

@dataclass
class ProductMeta:
    sku: str
    title: str
    description_html: str
    vendor: str
    product_type: str
    tags: List[str]
    price_try: float
    palette: str
    seed: int
    collection: str

# ---------------------------- Mockups ---------------------------- #

def generate_wall_mockup(master_2048: Image.Image, framed=False) -> Image.Image:
    W, H = 2800, 1800
    wall = Image.new("RGB", (W, H), (236,236,232))
    # add subtle vignette
    vign = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(vign)
    dv.rectangle([int(W*0.06), int(H*0.06), int(W*0.94), int(H*0.94)], fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(80))
    wall = Image.composite(wall, Image.new("RGB", (W,H), (222,222,218)), vign)

    # floor
    floor_h = int(H*0.18)
    draw = ImageDraw.Draw(wall)
    draw.rectangle([0, H-floor_h, W, H], fill=(214,211,208))
    for i in range(16):
        x = int(i*(W/16))
        draw.line([(x, H-floor_h), (x, H)], fill=(202,199,195), width=3)

    # frame area
    art_w = int(W*0.42)
    art = master_2048.copy().resize((art_w, int(art_w*1.25)), Image.LANCZOS)
    art = ensure_min_border(art, pct=0.05, color=(248,248,246))
    if framed:
        frame_w = 24
        framed_canvas = Image.new("RGB", (art.size[0]+2*frame_w, art.size[1]+2*frame_w), (60,60,60))
        framed_canvas.paste(art, (frame_w, frame_w))
        art = framed_canvas
    wall.paste(art, (int(W*0.5 - art.size[0]/2), int(H*0.42 - art.size[1]/2)))
    return wall

# ---------------------------- Main Pipeline ---------------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True, help="Output root folder")
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--collection", default="Zen & Calm")
    ap.add_argument("--vendor", default="Printbelle")
    ap.add_argument("--product_type", default="Digital Art Print")
    ap.add_argument("--price_try", type=float, default=129.90)
    ap.add_argument("--tags", default="zen,calm,minimal,abstract,printable,wall art")
    ap.add_argument("--palette", choices=list(PALETTES.keys()))
    ap.add_argument("--watermark", default="Zen & Calm · Printbelle")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    os.makedirs(args.outdir, exist_ok=True)
    assets_dir = os.path.join(args.outdir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    with open(os.path.join(assets_dir, "palettes.json"), "w") as f:
        json.dump(PALETTES, f, indent=2)

    manifest_rows = []
    for i in range(1, args.count+1):
        sku = f"ZC-{i:03d}"
        design_dir = os.path.join(args.outdir, "designs", sku)
        pr_dir = os.path.join(design_dir, "print")
        web_dir = os.path.join(design_dir, "web")
        mk_dir = os.path.join(design_dir, "mockups")
        os.makedirs(pr_dir, exist_ok=True)
        os.makedirs(web_dir, exist_ok=True)
        os.makedirs(mk_dir, exist_ok=True)

        pal_name = args.palette or rng.choice(list(PALETTES.keys()))
        pal = [hex_to_rgb(x) for x in PALETTES[pal_name]]

        # Make a high-res master first (for web/master & as base for prints)
        master_w = 3200  # internal working size; we’ll rescale for 2048 web master
        master_h = int(master_w * 1.25)
        art = generate_base_art(master_w, master_h, pal, rng)

        # WEB MASTER 2048
        master_2048 = art.resize((2048, int(2048*1.25)), Image.LANCZOS)
        master_2048 = unsharp_mask(master_2048, radius=0.8, percent=60, threshold=2)
        save_web(master_2048, os.path.join(web_dir, "master_2048.jpg"),
                 os.path.join(web_dir, "master_2048.webp"), quality=92)

        # Preview (watermarked)
        preview = master_2048.copy().resize((1600, int(1600*1.25)), Image.LANCZOS)
        if args.watermark:
            draw = ImageDraw.Draw(preview)
            try:
                # System font fallback; Pillow default if path not found
                font = ImageFont.truetype("Arial.ttf", size=36)
            except:
                font = ImageFont.load_default()
            text = args.watermark
            tw, th = draw.textbbox((0,0), text, font=font)[2:]
            pad = 24
            draw.rectangle([preview.width - tw - pad*2, preview.height - th - pad*2,
                            preview.width, preview.height], fill=(255,255,255,160))
            draw.text((preview.width - tw - pad, preview.height - th - pad),
                      text, fill=(30,30,30,255), font=font)
        preview.save(os.path.join(web_dir, "preview_1600_watermarked.jpg"),
                     "JPEG", quality=90, optimize=True, progressive=True)

        # Thumb
        thumb = master_2048.copy().resize((1200, int(1200*1.25)), Image.LANCZOS)
        thumb.save(os.path.join(web_dir, "thumb_1200.jpg"), "JPEG", quality=88, optimize=True, progressive=True)

        # PRINTABLES @300DPI
        for name, ax, ay, in_w, in_h in ASPECTS:
            if name == "a4":
                px_w = int(8.27 * DPI)
                px_h = int(11.69 * DPI)
            else:
                px_w = int(in_w * DPI)
                px_h = int(in_h * DPI)
            # Fit art to target with border
            canvas = Image.new("RGB", (px_w, px_h), (250,250,247))
            # keep inner margins (~6%) to be frame-friendly
            inner = (int(px_w*0.88), int(px_h*0.88))
            fitted = art.resize(inner, Image.LANCZOS)
            fitted = ensure_min_border(fitted, pct=0.03, color=(248,248,246))
            cx = (px_w - fitted.size[0])//2
            cy = (px_h - fitted.size[1])//2
            canvas.paste(fitted, (cx, cy))
            canvas = unsharp_mask(canvas, radius=1.2, percent=80, threshold=3)
            fn = f"{name}_300dpi.png"
            canvas.save(os.path.join(pr_dir, fn), "PNG", optimize=True)

        # MOCKUPS
        mk1 = generate_wall_mockup(master_2048, framed=False)
        mk1.save(os.path.join(mk_dir, "wall_mockup_1.jpg"), "JPEG", quality=90, optimize=True)
        mk2 = generate_wall_mockup(master_2048, framed=True)
        mk2.save(os.path.join(mk_dir, "framed_mockup_1.jpg"), "JPEG", quality=90, optimize=True)

        # META
        title = f"Zen & Calm Abstract #{i} — Minimal Serenity Wall Art (Digital Printable)"
        desc_html = (
            "<p>A soothing, minimal abstract printable from the Zen & Calm collection. "
            "Perfect for living rooms, bedrooms, and mindful workspaces.</p>"
            "<ul><li>High-resolution PNGs (300 DPI)</li>"
            "<li>Ratios included: 4×5, 3×4, 2×3, A4, 16×20 in</li>"
            "<li>License: Personal use</li></ul>"
        )
        meta = ProductMeta(
            sku=sku, title=title, description_html=desc_html, vendor=args.vendor,
            product_type=args.product_type, tags=[t.strip() for t in args.tags.split(",")],
            price_try=args.price_try, palette=pal_name, seed=args.seed, collection=args.collection
        )
        with open(os.path.join(design_dir, "meta.json"), "w") as f:
            json.dump(asdict(meta), f, indent=2, ensure_ascii=False)

        # Manifest row
        manifest_rows.append({
            "sku": sku,
            "title": title,
            "collection": args.collection,
            "price_try": f"{args.price_try:.2f}",
            "vendor": args.vendor,
            "product_type": args.product_type,
            "tags": args.tags,
            "palette": pal_name,
            "seed": args.seed,
            "web_master": os.path.relpath(os.path.join(web_dir, "master_2048.jpg"), args.outdir),
            "preview": os.path.relpath(os.path.join(web_dir, "preview_1600_watermarked.jpg"), args.outdir),
            "thumb": os.path.relpath(os.path.join(web_dir, "thumb_1200.jpg"), args.outdir),
            "print_4x5_16x20": os.path.relpath(os.path.join(pr_dir, "4x5_16x20_300dpi.png"), args.outdir),
            "print_3x4_18x24": os.path.relpath(os.path.join(pr_dir, "3x4_18x24_300dpi.png"), args.outdir),
            "print_2x3_24x36": os.path.relpath(os.path.join(pr_dir, "2x3_24x36_300dpi.png"), args.outdir),
            "print_a4": os.path.relpath(os.path.join(pr_dir, "a4_300dpi.png"), args.outdir),
            "mockup_wall": os.path.relpath(os.path.join(mk_dir, "wall_mockup_1.jpg"), args.outdir),
            "mockup_framed": os.path.relpath(os.path.join(mk_dir, "framed_mockup_1.jpg"), args.outdir),
        })

        print(f"✔ Generated {sku} with palette={pal_name}")

    # Write manifest CSV
    manifest_path = os.path.join(args.outdir, "manifest.csv")
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
        writer.writeheader()
        writer.writerows(manifest_rows)

    print("\nAll done.")
    print(f"Output: {args.outdir}")
    print(f"Items: {len(manifest_rows)}")

if __name__ == "__main__":
    main()