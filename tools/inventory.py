#!/usr/bin/env python3
"""
Inventory intake tool for Commander_AutonomaX.

Scans one or more filesystem roots and/or a file list and produces:
- data_room/inventory/inventory.json (structured catalog)
- data_room/inventory/matrix.csv (flat matrix view)

Usage examples:
  python tools/inventory.py --root . --root ../some_folder --label local
  python tools/inventory.py --filelist repos/my_repos.csv --label local
  python tools/inventory.py --filelist-glob 'repos/*.csv' --label repos
  # CSV with a path column (auto-detects common names or specify):
  python tools/inventory.py --filelist repos/AutonomaX_Master_Index.csv --filelist-path-col "Probable Local Path" --label master

Notes:
- Pure local scan; no network calls (URLs are recorded as link items).
- For --filelist, each line may be a local dir/file path or a URL.
- File type heuristics by extension; size and mtime recorded.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time, csv
from pathlib import Path
from typing import Dict, Any, List

CODE_EXT = {'.py','.js','.ts','.tsx','.jsx','.go','.rs','.java','.kt','.cs','.rb','.php','.sh','.ipynb','.sql','.scala'}
DOC_EXT  = {'.md','.txt','.rst','.pdf','.doc','.docx','.ppt','.pptx','.xls','.xlsx','.csv','.yaml','.yml'}
DATA_EXT = {'.parquet','.feather','.orc','.json','.ndjson','.avro','.db','.sqlite'}
MEDIA_EXT= {'.png','.jpg','.jpeg','.gif','.webp','.svg','.mp3','.wav','.aac','.m4a','.mp4','.mov','.mkv'}

def guess_kind(p: Path) -> str:
    ext = p.suffix.lower()
    if ext in CODE_EXT: return 'code'
    if ext in DOC_EXT: return 'doc'
    if ext in DATA_EXT: return 'data'
    if ext in MEDIA_EXT: return 'media'
    return 'other'

def sha1_of(path: Path, max_bytes: int = 1024*1024) -> str:
    h = hashlib.sha1()
    try:
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(65536)
                if not chunk: break
                h.update(chunk)
                if f.tell() >= max_bytes: break
        return h.hexdigest()
    except Exception:
        return ''

def scan_root(root: Path, base_label: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for dirpath, _, filenames in os.walk(root):
        # Skip virtualenvs and caches
        if any(skip in dirpath for skip in ('.git', '.venv', '__pycache__', 'node_modules', 'dist', 'build')):
            continue
        for name in filenames:
            p = Path(dirpath) / name
            try:
                stat = p.stat()
            except Exception:
                continue
            kind = guess_kind(p)
            items.append({
                'path': str(p.resolve()),
                'relpath': str(p.relative_to(root)),
                'root': str(root.resolve()),
                'label': base_label,
                'kind': kind,
                'size': stat.st_size,
                'mtime': int(stat.st_mtime),
                'sha1': sha1_of(p),
            })
    return items

def record_file(path: Path, base_label: str) -> Dict[str, Any]:
    try:
        stat = path.stat()
    except Exception:
        stat = type('S', (), {'st_size':0,'st_mtime':0})()
    return {
        'path': str(path.resolve()),
        'relpath': path.name,
        'root': str(path.parent.resolve()),
        'label': base_label,
        'kind': guess_kind(path),
        'size': getattr(stat, 'st_size', 0),
        'mtime': int(getattr(stat, 'st_mtime', 0)),
        'sha1': sha1_of(path) if path.exists() and path.is_file() else ''
    }

def load_filelist(path: Path) -> List[str]:
    lines: List[str] = []
    try:
        txt = path.read_text()
        for raw in txt.splitlines():
            s = raw.strip()
            if not s or s.startswith('#'): continue
            # CSV: take first column
            if ',' in s:
                s = s.split(',')[0].strip()
            lines.append(s)
    except Exception:
        pass
    return lines

def write_outputs(records: List[Dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')
    inv_path = out_dir / f'inventory_{ts}.json'
    mat_path = out_dir / f'matrix_{ts}.csv'
    latest_json = out_dir / 'inventory.json'
    latest_csv = out_dir / 'matrix.csv'

    with open(inv_path, 'w') as f:
        json.dump({'generated_at': ts, 'count': len(records), 'items': records}, f, indent=2)
    with open(mat_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['label','kind','size','mtime','path'])
        w.writeheader()
        for r in records:
            w.writerow({'label': r['label'], 'kind': r['kind'], 'size': r['size'], 'mtime': r['mtime'], 'path': r['path']})
    # Update latest pointers
    latest_json.write_text(inv_path.read_text())
    latest_csv.write_text(mat_path.read_text())

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', action='append', default=[], help='Root directory to scan (repeatable)')
    ap.add_argument('--label', default='local', help='Label for these roots')
    ap.add_argument('--filelist', default='', help='Path to CSV/TXT with local paths or URLs (one per line, or CSV with a path column)')
    ap.add_argument('--filelist-glob', default='', help='Glob pattern for multiple CSV/TXT lists (e.g., repos/*.csv)')
    ap.add_argument('--filelist-path-col', default='', help='If --filelist is a CSV with headers, use this column for local paths')
    ap.add_argument('--out', default='data_room/inventory', help='Output directory')
    args = ap.parse_args(argv)

    all_items: List[Dict[str, Any]] = []

    roots = [Path(r).resolve() for r in (args.root or [])]
    for r in roots:
        if not r.exists():
            print(f"Skip missing root: {r}")
            continue
        all_items.extend(scan_root(r, args.label))

    lists: List[str] = []
    if args.filelist: lists.append(args.filelist)
    if args.filelist_glob:
        import glob
        lists.extend(glob.glob(args.filelist_glob))
    for lf in lists:
        p = Path(lf)
        # If CSV with a header, attempt to extract a path column
        if p.suffix.lower() == '.csv' and p.exists():
            import csv
            with open(p, newline='') as f:
                rd = csv.DictReader(f)
                headers = [h.lower() for h in (rd.fieldnames or [])]
                path_col = args.filelist_path_col.strip().lower() if args.filelist_path_col else ''
                if not path_col:
                    # Auto-detect common path column names
                    candidates = [
                        'path','local path','file path','filepath','probable local path','probable local path existing inventories'
                    ]
                    for c in candidates:
                        if c in headers:
                            path_col = c; break
                if path_col:
                    for row in rd:
                        entry = (row.get(path_col) or '').strip()
                        if not entry: continue
                        if entry.startswith(('http://','https://','git@','git://')):
                            # Record as link
                            all_items.append({
                                'path': entry,'relpath': entry,'root': '<link>','label': args.label,
                                'kind':'link','size':0,'mtime':0,'sha1':''
                            })
                        else:
                            pp = Path(entry).expanduser().resolve()
                            if pp.is_dir():
                                all_items.extend(scan_root(pp, args.label))
                            elif pp.exists():
                                all_items.append(record_file(pp, args.label))
                            else:
                                all_items.append({'path': str(pp), 'relpath': pp.name, 'root': str(pp.parent), 'label': args.label, 'kind': 'missing', 'size': 0, 'mtime': 0, 'sha1': ''})
                    continue  # handled CSV
        lst = load_filelist(Path(lf))
        for entry in lst:
            if entry.startswith('http://') or entry.startswith('https://') or entry.startswith('git@') or entry.startswith('git://'):
                # Record as link item
                all_items.append({
                    'path': entry,
                    'relpath': entry,
                    'root': '<link>',
                    'label': args.label,
                    'kind': 'link',
                    'size': 0,
                    'mtime': 0,
                    'sha1': ''
                })
                continue
            p = Path(entry).expanduser().resolve()
            if p.is_dir():
                all_items.extend(scan_root(p, args.label))
            elif p.exists():
                all_items.append(record_file(p, args.label))
            else:
                # Record missing reference for later triage
                all_items.append({
                    'path': str(p), 'relpath': p.name, 'root': str(p.parent), 'label': args.label,
                    'kind': 'missing', 'size': 0, 'mtime': 0, 'sha1': ''
                })

    write_outputs(all_items, Path(args.out))
    print(f"Inventory written to {args.out}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
