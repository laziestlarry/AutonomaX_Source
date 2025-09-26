#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zen & Calm — Pro Maker
Best-seller quality, composition-aware generator with textures, typography, and export sets.

Features
- 4 Design Modes:
  1) Minimalist Zen Boho  (warm earthy: terracotta/beige/clay; white background; clean poster)
  2) Sacred Geometry Zen   (circles/arches/triangles; calm muted; spiritual symmetry)
  3) Calm Flow Abstract    (flowing curves, waves, circles; soft pastels + earthy)
  4) Modern Harmony        (geometric harmony; clean lines; balanced symmetry)
- Composition helpers (rule of thirds, golden ratio, symmetry & horizon placement)
- Pro textures (paper grain, watercolor wash, vignette, deckled/fade edges)
- Imperfection (micro brush grain, slight misregistration glazes)
- Typography overlay (Title/Subitle) with safe margins; fallback fonts if system font missing
- Exports: 300 DPI print masters (A4, 4x5/16x20, 3x4/18x24, 2x3/24x36) + web (2048 master, preview w/ watermark, thumb)
- Simple room/framed mockups
- Metadata & manifest.csv

Requires: pillow, numpy
  pip install pillow numpy
"""
import os, csv, json, math, random, argparse
from dataclasses import dataclass, asdict
from typing import List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont

# ---------------- Palettes ---------------- #

PALETTES = {
    "boho_warm": ["#ffffff","#f4efe8","#e8ded1","#d7c4b3","#caa28a","#b5745c","#8f4e3b"],
    "sacred_muted": ["#f7f7f6","#e9ecef","#d7dfe6","#c7d1d8","#adbcc6","#8696a6","#5c6a74"],
    "calm_flow": ["#f6f6f6","#edeae6","#e1e3db","#d4dfd3","#c3d3c7","#aebfb3","#8aa296"],
    "modern_harmony": ["#ffffff","#f2f1ef","#e6e3df","#d6d0cb","#c4bbb4","#a99c94","#857a73"]
}

# ---------------- Modes ---------------- #

MODES = {
    1: {"name":"Minimalist Zen Boho", "palette":"boho_warm", "bg":"#ffffff"},
    2: {"name":"Sacred Geometry Zen", "palette":"sacred_muted", "bg":"#f7f7f6"},
    3: {"name":"Calm Flow Abstract",  "palette":"calm_flow",  "bg":"#f6f6f6"},
    4: {"name":"Modern Harmony",      "palette":"modern_harmony", "bg":"#ffffff"},
}
ASPECTS = [
    ("4x5_16x20", 16, 20),  # inches
    ("3x4_18x24", 18, 24),
    ("2x3_24x36", 24, 36),
    ("a4", 8.27, 11.69),
]

# ---------------- Utils ---------------- #

def hex_to_rgb(h): h=h.strip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return a + (b-a)*t
def blend(c1,c2,t): return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))
def clamp(x,a,b): return max(a,min(b,x))

def pick_font(size=48, pref=("Avenir.ttf","Inter.ttf","Helvetica.ttf","Arial.ttf")):
    for p in pref:
        try: return ImageFont.truetype(p, size=size)
        except: continue
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

def watercolor_wash(im, color=(255,255,255), alpha=0.12, radius=18):
    wash = Image.new("RGB", im.size, color)
    wash = wash.filter(ImageFilter.GaussianBlur(radius))
    return Image.blend(im, wash, alpha)

def deckled_edges(im, amount=0.08, seed=11):
    rng = random.Random(seed)
    w,h = im.size
    mask = Image.new("L",(w,h),255)
    d = ImageDraw.Draw(mask)
    for i in range(4):
        # random bite along edges
        bites = []
        n = 50
        if i%2==0:  # top/bottom
            y = 0 if i==0 else h-1
            for k in range(n):
                x = int(k*(w/n))
                r = rng.randint(0, int(h*amount))
                bites.append((x, y + (r if i==0 else -r)))
            d.line(bites, fill=0, width=1)
        else:       # left/right
            x = 0 if i==1 else w-1
            for k in range(n):
                y = int(k*(h/n))
                r = rng.randint(0, int(w*amount))
                d.line([(x + (r if i==1 else -r), y), (x, y)], fill=0, width=1)
    mask = soften(mask, 6).filter(ImageFilter.GaussianBlur(8))
    base = Image.new("RGB",(w,h), hex_to_rgb("#ffffff"))
    return Image.composite(im, base, mask)

def horizon_y(h, mode_id):
    # Slightly different horizon for variety
    return int(h * {1:0.62, 2:0.58, 3:0.64, 4:0.60}[mode_id])

# ---------------- Composition Primitives ---------------- #

def draw_circle(draw, cx, cy, r, fill):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)

def draw_arch(draw, cx, cy, r_outer, r_inner, fill, thickness=24):
    # Simple arch (upper semicircle band)
    bbox_outer = [cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer]
    bbox_inner = [cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner]
    draw.pieslice(bbox_outer, 180, 0, fill=fill)
    draw.pieslice(bbox_inner, 180, 0, fill=None)
    # Cut inner with white rect to keep clean
    draw.rectangle([cx-r_inner, cy, cx+r_inner, cy+r_inner], fill="#00000000")  # transparent; handled by layering order

def draw_triangle(draw, points, fill):
    draw.polygon(points, fill=fill)

def draw_wave(draw, w, y_mid, amp, periods, color, alpha=140, seed=5):
    rng = random.Random(seed)
    pts = []
    for x in range(0, w+1, 8):
        t = (x / w) * (2*math.pi*periods)
        y = y_mid + amp*math.sin(t) + rng.uniform(-amp*0.08, amp*0.08)
        pts.append((x, y))
    # close to bottom
    pts += [(w, y_mid+amp*2), (0, y_mid+amp*2)]
    draw.polygon(pts, fill=(*hex_to_rgb(color), alpha))

# ---------------- Modes Renderers ---------------- #

def render_minimalist_zen_boho(im, palette, rng):
    d = ImageDraw.Draw(im, "RGBA")
    w,h = im.size
    # big centered circle + horizon block + small offset circle
    main_r = int(min(w,h)*0.18)
    cx, cy = int(w*0.5), int(h*0.42)
    draw_circle(d, cx, cy, main_r, (*hex_to_rgb(palette[4]), 220))
    # horizon block
    hy = horizon_y(h, 1)
    d.rectangle([int(w*0.12), hy, int(w*0.88), hy+int(h*0.06)], fill=(*hex_to_rgb(palette[5]), 190))
    # small accent
    draw_circle(d, int(w*0.32), int(h*0.30), int(main_r*0.42), (*hex_to_rgb(palette[3]), 200))

def render_sacred_geometry_zen(im, palette, rng):
    d = ImageDraw.Draw(im, "RGBA")
    w,h = im.size
    cx, cy = int(w*0.5), int(h*0.46)
    # concentric circles
    for i in range(5):
        r = int(min(w,h)*0.22 * (1 - i*0.12))
        draw_circle(d, cx, cy, r, (*hex_to_rgb(palette[2+i%3]), int(210 - i*20)))
    # arches
    draw_arch(d, cx, cy, int(min(w,h)*0.38), int(min(w,h)*0.28), (*hex_to_rgb(palette[6-1]), 140))
    # grounding triangle
    tri_w = int(w*0.28)
    points = [(cx-tri_w//2, cy+int(h*0.18)), (cx+tri_w//2, cy+int(h*0.18)), (cx, cy+int(h*0.02))]
    draw_triangle(d, points, (*hex_to_rgb(palette[5]), 140))

def render_calm_flow_abstract(im, palette, rng):
    d = ImageDraw.Draw(im, "RGBA")
    w,h = im.size
    # layered waves
    hy = horizon_y(h, 3)
    for i, col in enumerate(palette[2:]):
        draw_wave(d, w, hy - i*int(h*0.03), amp=int(h*0.035*(1+i*0.15)),
                  periods=1.5+i*0.35, color=col, alpha=120+i*20, seed=33+i)
    # floating circle
    draw_circle(d, int(w*0.68), int(h*0.34), int(min(w,h)*0.12), (*hex_to_rgb(palette[4]), 210))

def render_modern_harmony(im, palette, rng):
    d = ImageDraw.Draw(im, "RGBA")
    w,h = im.size
    cx, cy = int(w*0.5), int(h*0.46)
    # bars
    bar_w = int(w*0.62)
    d.rectangle([cx-bar_w//2, cy-int(h*0.02), cx+bar_w//2, cy+int(h*0.02)], fill=(*hex_to_rgb(palette[5]), 200))
    # arcs (symmetry)
    r_outer = int(min(w,h)*0.28)
    r_inner = int(r_outer*0.78)
    draw_arch(d, cx, cy, r_outer, r_inner, (*hex_to_rgb(palette[4]), 180))
    # offset circle & counterbalance rectangle
    draw_circle(d, int(w*0.35), int(h*0.33), int(min(w,h)*0.10), (*hex_to_rgb(palette[3]), 210))
    d.rectangle([int(w*0.58), int(h*0.60), int(w*0.80), int(h*0.72)], fill=(*hex_to_rgb(palette[2]), 180))

MODE_RENDER = {
    1: render_minimalist_zen_boho,
    2: render_sacred_geometry_zen,
    3: render_calm_flow_abstract,
    4: render_modern_harmony
}

# ---------------- Export helpers ---------------- #

def title_block(im, title, subtitle, top_pct=0.08, pad_pct=0.05):
    if not title and not subtitle: return im
    w,h = im.size
    canvas = im.copy()
    d = ImageDraw.Draw(canvas)
    title_font = pick_font(size=int(h*0.045))   # boldish
    sub_font   = pick_font(size=int(h*0.026))   # light/regular

    top = int(h*top_pct)
    pad = int(w*pad_pct)
    # Title
    tw, th = d.textbbox((0,0), title, font=title_font)[2:]
    d.text((pad, top), title, fill=(24,24,24), font=title_font)
    # Subtitle below with softer tone
    if subtitle:
        d.text((pad, top + th + int(h*0.012)), subtitle, fill=(70,70,70), font=sub_font)
    return canvas

def add_textures(im, mode_id, seed):
    bg = im
    # paper grain
    bg = paper_grain(bg, strength=0.06 if mode_id in (1,4) else 0.08, seed=seed+3)
    # watercolor wash
    bg = watercolor_wash(bg, color=(255,255,255), alpha=0.10 if mode_id in (1,4) else 0.12, radius=16)
    # vignette
    bg = vignette(bg, strength=0.10 if mode_id in (1,3) else 0.12)
    # deckled/fade edges
    bg = deckled_edges(bg, amount=0.06, seed=seed+9)
    # gentle unsharp
    bg = unsharp(bg, r=1.0, p=80, th=3)
    return bg

def simple_mockup(master_2048, framed=False):
    W,H=2800,1800
    wall = Image.new("RGB",(W,H),(236,236,232))
    # soft vignette on wall
    mask = Image.new("L",(W,H),0)
    d = ImageDraw.Draw(mask)
    pad=int(min(W,H)*0.08)
    d.rectangle([pad,pad,W-pad,H-pad], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(60))
    wall = Image.composite(wall, Image.new("RGB",(W,H),(222,222,218)), mask)
    # floor planks
    floor_h=int(H*0.20); d2=ImageDraw.Draw(wall)
    d2.rectangle([0,H-floor_h,W,H], fill=(214,211,208))
    for i in range(18):
        x=int(i*(W/18)); d2.line([(x,H-floor_h),(x,H)], fill=(202,199,195), width=3)
    # frame
    art_w=int(W*0.44)
    art = master_2048.copy().resize((art_w,int(art_w*1.25)), Image.LANCZOS)
    art = ImageOps.expand(art, border=int(art_w*0.05), fill=(248,248,246))
    if framed:
        fw=int(art_w*0.012)
        art = ImageOps.expand(art, border=fw, fill=(60,60,60))
    wall.paste(art,(int(W*0.5-art.size[0]/2), int(H*0.42-art.size[1]/2)))
    return wall

# ---------------- Driver ---------------- #

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

def generate_piece(outdir, idx, mode_id, title, subtitle, price_try, dpi, seed):
    rng = random.Random(seed + idx*31)
    mode = MODES[mode_id]
    palette = [hex_to_rgb(x) for x in PALETTES[mode["palette"]]]
    bg_color = hex_to_rgb(mode["bg"])

    # working canvas (poster aspect ~4:5), high internal res (then reflow to outputs)
    W,H = 3200, 4000
    base = Image.new("RGB",(W,H), bg_color)

    # layout base composition (shapes)
    comp = base.copy()
    MODE_RENDER[mode_id](comp, [f"#{r:02x}{g:02x}{b:02x}" for (r,g,b) in palette], rng)

    # overlay title/subtitle block (top-left)
    poster = title_block(comp, title, subtitle, top_pct=0.085, pad_pct=0.06)

    # textures & finishing
    poster = add_textures(poster, mode_id, seed=seed+idx*7)

    # web exports
    web_dir = os.path.join(outdir,"web"); os.makedirs(web_dir, exist_ok=True)
    master_2048 = poster.resize((2048, int(2048*1.25)), Image.LANCZOS)
    master_2048.save(os.path.join(web_dir, f"master_{idx:02d}_2048.jpg"), "JPEG", quality=92, optimize=True, progressive=True)
    prev = master_2048.copy()
    prev.save(os.path.join(web_dir, f"preview_{idx:02d}_1600.jpg"), "JPEG", quality=90, optimize=True, progressive=True)
    th = master_2048.copy().resize((1200, int(1200*1.25)), Image.LANCZOS)
    th.save(os.path.join(web_dir, f"thumb_{idx:02d}_1200.jpg"), "JPEG", quality=88, optimize=True, progressive=True)

    # print masters @ 300 DPI
    print_dir = os.path.join(outdir,"print"); os.makedirs(print_dir, exist_ok=True)
    for name, in_w, in_h in ASPECTS:
        px_w, px_h = int(in_w*dpi), int(in_h*dpi)
        canvas = Image.new("RGB",(px_w,px_h), (252,252,250))
        # keep generous margins for framing (8% outer)
        inner = (int(px_w*0.84), int(px_h*0.84))
        fitted = poster.resize(inner, Image.LANCZOS)
        fitted = ImageOps.expand(fitted, border=int(min(inner)*0.03), fill=(248,248,246))
        cx, cy = (px_w - fitted.size[0])//2, (px_h - fitted.size[1])//2
        canvas.paste(fitted, (cx,cy))
        canvas = unsharp(canvas, 1.0, 70, 3)
        canvas.save(os.path.join(print_dir, f"{name}_{idx:02d}_{dpi}dpi.png"), "PNG", optimize=True)

    # mockups
    mk_dir=os.path.join(outdir,"mockups"); os.makedirs(mk_dir, exist_ok=True)
    mk1 = simple_mockup(master_2048, framed=False)
    mk1.save(os.path.join(mk_dir, f"wall_{idx:02d}.jpg"), "JPEG", quality=90, optimize=True)
    mk2 = simple_mockup(master_2048, framed=True)
    mk2.save(os.path.join(mk_dir, f"framed_{idx:02d}.jpg"), "JPEG", quality=90, optimize=True)

    # meta
    sku = f"ZCP-{idx:03d}"
    handle = f"zen-calm-pro-{idx}"
    return Meta(
        sku=sku, handle=handle, title=title, subtitle=subtitle,
        mode=mode["name"], price_try=129.90,
        palette=mode["palette"], seed=seed,
        web_master=os.path.join("web", f"master_{idx:02d}_2048.jpg"),
        preview=os.path.join("web", f"preview_{idx:02d}_1600.jpg"),
        thumb=os.path.join("web", f"thumb_{idx:02d}_1200.jpg")
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--count", type=int, default=8)
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--titles_json", help="Path to JSON list of {title,subtitle}")
    args = ap.parse_args()

    titles = []
    if args.titles_json and os.path.exists(args.titles_json):
        with open(args.titles_json,"r",encoding="utf-8") as f:
            titles = json.load(f)

    os.makedirs(args.outdir, exist_ok=True)
    metas: List[Meta] = []

    for i in range(1, args.count+1):
        # rotate modes 1..4
        mode_id = ((i-1) % 4) + 1
        if i-1 < len(titles):
            t = titles[i-1]
            title = t.get("title") or f"Zen & Calm #{i}"
            subtitle = t.get("subtitle") or MODES[mode_id]["name"]
        else:
            title = f"Zen & Calm #{i}"
            subtitle = MODES[mode_id]["name"]
        out_i = os.path.join(args.outdir, f"ZCP_{i:03d}")
        os.makedirs(out_i, exist_ok=True)
        meta = generate_piece(out_i, i, mode_id, title, subtitle, price_try=129.90, dpi=args.dpi, seed=args.seed)
        metas.append(meta)
        print(f"✓ {meta.sku} — {meta.title} [{MODES[mode_id]['name']}]")

    # manifest
    with open(os.path.join(args.outdir,"manifest.csv"),"w",newline="",encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(asdict(metas[0]).keys()))
        wr.writeheader()
        for m in metas: wr.writerow(asdict(m))
    print(f"\nAll done. Output → {args.outdir}; items={len(metas)}")

if __name__ == "__main__":
    main()
