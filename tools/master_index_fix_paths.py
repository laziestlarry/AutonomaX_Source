#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, os
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT = Path(__file__).resolve().parent.parent

def exists(p: str) -> bool:
    try:
        return Path(p).expanduser().exists()
    except Exception:
        return False

def search_basename(name: str, max_hits: int = 10) -> List[str]:
    hits: List[str] = []
    name = name.strip()
    if not name:
        return hits
    # Search under project root only
    for p in ROOT.rglob(name):
        # Avoid matching venv/node_modules/cache dirs
        sp = str(p)
        if any(x in sp for x in ('.git', '.venv', '__pycache__', 'node_modules', 'dist', 'build')):
            continue
        hits.append(sp)
        if len(hits) >= max_hits:
            break
    return hits

def fix_paths(rows: List[Dict[str, str]], old_prefix: str, new_prefix: str) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    report = {
        'total': len(rows),
        'checked': 0,
        'ok': 0,
        'fixed_prefix': 0,
        'fixed_search': 0,
        'ambiguous': 0,
        'missing': 0,
        'details': []
    }
    out: List[Dict[str, str]] = []
    for r in rows:
        path = (r.get('path') or '').strip()
        changed = False
        detail = {'orig': path, 'status': 'ok', 'new': path, 'candidates': []}
        if not path:
            out.append(r)
            continue
        report['checked'] += 1
        if exists(path):
            report['ok'] += 1
            out.append(r)
            report['details'].append(detail)
            continue
        # Try prefix mapping
        if old_prefix and new_prefix and path.startswith(old_prefix):
            mapped = new_prefix + path[len(old_prefix):]
            if exists(mapped):
                r['path'] = mapped
                detail.update({'status': 'fixed_prefix', 'new': mapped})
                report['fixed_prefix'] += 1
                out.append(r)
                report['details'].append(detail)
                continue
        # Try basename search
        base = os.path.basename(path)
        cands = search_basename(base)
        if len(cands) == 1:
            r['path'] = cands[0]
            detail.update({'status': 'fixed_search', 'new': cands[0], 'candidates': cands})
            report['fixed_search'] += 1
        elif len(cands) > 1:
            detail.update({'status': 'ambiguous', 'candidates': cands})
            report['ambiguous'] += 1
        else:
            detail.update({'status': 'missing'})
            report['missing'] += 1
        out.append(r)
        report['details'].append(detail)
    return out, report

def load_csv(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    with open(path, newline='') as f:
        r = csv.DictReader(f)
        rows = [dict(row) for row in r]
        return rows, r.fieldnames or []

def write_csv(path: Path, rows: List[Dict[str, str]], headers: List[str]) -> None:
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for row in rows:
            w.writerow(row)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='repos/AutonomaX_Master_Index.csv')
    ap.add_argument('--old-prefix', default='')
    ap.add_argument('--new-prefix', default='')
    ap.add_argument('--out', default='repos/AutonomaX_Master_Index.corrected.csv')
    ap.add_argument('--report', default='data_room/reports/master_index_fix_report.json')
    args = ap.parse_args()

    src = Path(args.csv)
    rows, headers = load_csv(src)
    # Determine path column name (case-insensitive)
    lower_map = {h.lower(): h for h in headers}
    path_key = None
    for cand in ['path','local path','file path','filepath','probable local path','probable local path existing inventories']:
        if cand in lower_map:
            path_key = lower_map[cand]
            break
    if not path_key:
        print('No path-like column found; nothing to fix.')
        return 0
    # Normalize rows to have 'path'
    norm_rows = []
    for r in rows:
        rr = dict(r)
        rr['path'] = r.get(path_key, '')
        norm_rows.append(rr)
    fixed_rows, rep = fix_paths(norm_rows, args.old_prefix, args.new_prefix)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Write back with original headers, replacing the detected path column
    out_rows = []
    for fr in fixed_rows:
        orow = {}
        for h in headers:
            if h == path_key:
                orow[h] = fr.get('path','')
            else:
                orow[h] = fr.get(h, '')
        out_rows.append(orow)
    write_csv(out_path, out_rows, headers)

    rep_path = Path(args.report)
    rep_path.parent.mkdir(parents=True, exist_ok=True)
    rep.update({'source': str(src), 'output': str(out_path)})
    rep_path.write_text(json.dumps(rep, indent=2))
    print(json.dumps({'ok': True, 'output': str(out_path), 'report': str(rep_path), 'stats': {k: v for k, v in rep.items() if isinstance(v, int)}}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
