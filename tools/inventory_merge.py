#!/usr/bin/env python3
"""
Merge one or more inventory.json files into a single catalog.

Inputs:
  --inv data_room/inventory/inventory.json  (repeatable)
  --label LABEL                               optional; applied per respective --inv in order

Output:
  data_room/inventory/inventory_merged.json

If labels are fewer than inventories, the last label is reused; if none given,
defaults to 'merged'. Duplicate items (same path+sha1) are de-duplicated.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import List, Dict, Any, Tuple

def load_inv(p: Path) -> List[Dict[str, Any]]:
    try:
        j = json.loads(p.read_text())
        return list(j.get('items', []))
    except Exception:
        return []

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--inv', action='append', default=[], help='Path to inventory.json (repeatable)')
    ap.add_argument('--label', action='append', default=[], help='Label(s) to apply per inventory (repeatable)')
    ap.add_argument('--out', default='data_room/inventory/inventory_merged.json')
    args = ap.parse_args(argv)

    if not args.inv:
        print('Provide at least one --inv path')
        return 2
    labels = (args.label or ['merged'])
    out_items: List[Dict[str, Any]] = []
    seen: set[Tuple[str,str]] = set()
    for idx, path in enumerate(args.inv):
        label = labels[min(idx, len(labels)-1)] if labels else 'merged'
        items = load_inv(Path(path))
        for it in items:
            key = (it.get('path',''), it.get('sha1',''))
            if key in seen: continue
            seen.add(key)
            it2 = dict(it)
            it2['label'] = label or it.get('label','merged')
            out_items.append(it2)
    out = {'generated_from': args.inv, 'count': len(out_items), 'items': out_items}
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f'Wrote {out_path} with {len(out_items)} items')
    return 0

if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))

