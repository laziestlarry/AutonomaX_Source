#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, os
from pathlib import Path
from typing import List, Dict, Any

IMG_EXT = {'.png','.jpg','.jpeg','.webp','.gif'}

def guess_title(relpath: str, path: str) -> str:
    base = os.path.basename(relpath or path or "")
    name, _ = os.path.splitext(base)
    return name.replace('_',' ').replace('-',' ').strip() or base

def build_products(catalog: Path, limit: int | None = None) -> List[Dict[str, Any]]:
    rows = []
    with open(catalog, newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    out: List[Dict[str, Any]] = []
    for row in rows[:limit or len(rows)]:
        path = row.get('path','')
        rel = row.get('relpath','')
        tags = row.get('tags','')
        title = guess_title(rel, path)
        images: List[str] = []
        ext = os.path.splitext(path)[1].lower()
        if ext in IMG_EXT:
            images.append(path)
        prod = {
            'title': title,
            'body_html': '',
            'tags': tags,
            'vendor': 'AutonomaX',
            'product_type': 'digital',
            'images': images,
        }
        out.append(prod)
    return out

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', default='data_room/products/catalog.csv')
    ap.add_argument('--limit', type=int, default=20)
    ap.add_argument('--out', default='data_room/products/shopify_products.json')
    args = ap.parse_args(argv)
    prods = build_products(Path(args.catalog), args.limit)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({'products': prods}, indent=2))
    print(json.dumps({'ok': True, 'count': len(prods), 'output': str(out_path)}, indent=2))
    return 0

if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))

