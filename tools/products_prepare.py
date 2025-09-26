#!/usr/bin/env python3
"""
Prepare product artifacts locally from inventory and tags.

Steps:
- Load inventory.json (merged or standard) and tags.json (if any)
- Suggest tags (rule-based) for each item and merge with existing tags
- Select items matching include_tags (e.g., product, printable, content)
- Score and order items (simple heuristic: recency + tag weights)
- Emit:
  - data_room/products/catalog.csv
  - data_room/inventory/tags.json (updated)
  - data_room/products/plan.md (summary)

Usage:
  python tools/products_prepare.py \
    --inventory data_room/inventory/inventory.json \
    --tags data_room/inventory/tags.json \
    --include product printable content \
    --out data_room/products
"""
from __future__ import annotations
import argparse, json, time, csv, os, sys
from pathlib import Path
from typing import Dict, Any, List, Set

# Ensure project root is on sys.path when invoked as a script from tools/
THIS_DIR = Path(__file__).resolve().parent
ROOT_DIR = THIS_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.agents import suggest_tags_for_path

def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--inventory', default='data_room/inventory/inventory.json')
    ap.add_argument('--tags', default='data_room/inventory/tags.json')
    ap.add_argument('--out', default='data_room/products')
    ap.add_argument('--include', nargs='*', default=['product','printable','content'])
    args = ap.parse_args(argv)

    inv = load_json(Path(args.inventory))
    items = inv.get('items') or []
    tag_file = Path(args.tags)
    tags = load_json(tag_file) if tag_file.exists() else {}

    include: Set[str] = set(t.lower() for t in (args.include or []))

    enriched: List[Dict[str, Any]] = []
    for it in items:
        path = it.get('path','')
        kind = it.get('kind','other')
        sug = suggest_tags_for_path(path, kind)
        curr = tags.get(path, [])
        merged = sorted(set(curr) | set(sug))
        tags[path] = merged
        # selection
        sel = any(t in (tt.lower() for tt in merged) for t in include)
        if not sel:
            continue
        # score: favor include tags + recency
        w = 0
        low = [t for t in merged if t.lower() in include]
        w += 10 * len(low)
        mtime = int(it.get('mtime') or 0)
        w += min(10, (mtime // (24*3600)))  # rough day bucket
        enriched.append({
            'path': path,
            'relpath': it.get('relpath',''),
            'kind': kind,
            'tags': ','.join(merged),
            'score': w,
        })

    # order by score desc
    enriched.sort(key=lambda r: (-r['score'], r['path']))

    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    # write catalog.csv
    cat = out_dir / 'catalog.csv'
    with open(cat, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['path','relpath','kind','tags','score'])
        w.writeheader()
        for r in enriched:
            w.writerow(r)
    # write plan.md
    plan = out_dir / 'plan.md'
    lines = [f"# Products Plan — {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"]
    for r in enriched[:100]:
        lines.append(f"- [{r['score']:02d}] {r['relpath'] or r['path']} — {r['tags']}\n")
    plan.write_text(''.join(lines))
    # persist tags
    tag_file.parent.mkdir(parents=True, exist_ok=True)
    tag_file.write_text(json.dumps(tags, indent=2))

    print(json.dumps({'catalog': str(cat), 'plan': str(plan), 'tags': str(tag_file)}, indent=2))
    return 0

if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))
