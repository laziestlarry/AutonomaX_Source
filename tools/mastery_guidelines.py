#!/usr/bin/env python3
"""
Generate mastery guidelines and a runbook from a prioritized CSV index.

Reads a CSV (e.g., repos/AutonomaX_Master_Index.csv) and produces:
- docs/mastery/mastery_guidelines.md (grouped by role/tags)
- docs/mastery/runbook_master_index.md (checklist-style execution plan)

CSV columns (flexible): name, url, path, desc, tags, role, score/priority
"""
from __future__ import annotations
import argparse, csv, json, re, time
from pathlib import Path
from typing import Dict, Any, List

def load_rows(p: Path) -> List[Dict[str,str]]:
    rows = []
    with open(p, newline='') as f:
        r = csv.DictReader(f)
        cols = [c.lower() for c in (r.fieldnames or [])]
        for row in r:
            rows.append({k.lower(): (v or '').strip() for k,v in row.items()})
    # Fallback: simple CSV with no header
    if not rows:
        for line in p.read_text().splitlines():
            s = line.strip()
            if not s or s.startswith('#'): continue
            rows.append({'name': s})
    return rows

def group(rows: List[Dict[str,str]], key: str) -> Dict[str,List[Dict[str,str]]]:
    g: Dict[str,List[Dict[str,str]]] = {}
    for r in rows:
        val = r.get(key,'') or 'uncategorized'
        g.setdefault(val, []).append(r)
    return g

def normalize(rows: List[Dict[str,str]]) -> List[Dict[str,str]]:
    out = []
    for r in rows:
        name = r.get('name') or r.get('title') or r.get('filename') or r.get('path') or r.get('url') or 'item'
        # Accept alternate path/desc/tags columns
        path = r.get('path') or r.get('probable local path') or r.get('probable local path existing inventories') or r.get('file path') or r.get('local path') or r.get('filepath') or ''
        url = r.get('url','')
        desc = r.get('desc') or r.get('description') or r.get('purpose') or ''
        tags = r.get('tags') or r.get('category') or ''
        role = r.get('role') or ''
        try:
            score = float(r.get('score') or r.get('priority') or 0)
        except Exception:
            score = 0.0
        out.append({'name': name, 'url': url, 'path': path, 'desc': desc, 'tags': tags, 'role': role, 'score': score})
    out.sort(key=lambda x: (-x['score'], x['name']))
    return out

def write_mastery(rows: List[Dict[str,str]], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    md = out_dir / 'mastery_guidelines.md'
    by_role = group(rows, 'role')
    lines = [f"# Mastery Guidelines — {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"]
    for role, items in by_role.items():
        if not role: role = 'general'
        header = role.capitalize()
        lines.append(f"## {header}\n\n")
        for it in items[:200]:
            ref = it['url'] or it['path'] or it['name']
            bullet = f"- {it['name']} — {it['desc']} ({ref})"
            if it['tags']:
                bullet += f" [tags: {it['tags']}]"
            lines.append(bullet + "\n")
        lines.append("\n")
    md.write_text(''.join(lines))
    return md

def write_runbook(rows: List[Dict[str,str]], out_dir: Path) -> Path:
    md = out_dir / 'runbook_master_index.md'
    lines = [f"# Runbook — Master Index Sprint ({time.strftime('%Y-%m-%d %H:%M:%S')})\n\n"]
    sections = {
        'platform': 'Platform Readiness',
        'engineering': 'Engineering Modules',
        'data': 'Data & KPIs',
        'growth': 'Growth Ops',
        'management': 'Management & PM',
    }
    # Heuristic mapping from tags/role
    def bus_of(item: Dict[str,str]) -> str:
        role = (item.get('role') or '').lower()
        tags = (item.get('tags') or '').lower()
        if any(t in tags for t in ['gcp','cloud','run','scheduler']): return 'platform'
        if any(t in tags for t in ['bq','ga4','etl','data','kpi']): return 'data'
        if any(t in tags for t in ['campaign','dm','content','video','brand']): return 'growth'
        if role in ['pm','advisor','management','product']: return 'management'
        return 'engineering'
    buckets: Dict[str, List[Dict[str,str]]] = {k: [] for k in sections}
    for it in rows:
        buckets[bus_of(it)].append(it)
    for key, title in sections.items():
        items = buckets[key]
        if not items: continue
        lines.append(f"## {title}\n\n")
        for it in items[:100]:
            ref = it['url'] or it['path'] or it['name']
            lines.append(f"- [ ] {it['name']} — {it['desc']} ({ref})\n")
        lines.append("\n")
    md.write_text(''.join(lines))
    return md

def main(argv: List[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--file', required=True, help='CSV file')
    ap.add_argument('--outdir', default='docs/mastery')
    args = ap.parse_args(argv)
    p = Path(args.file).expanduser()
    rows = normalize(load_rows(p))
    out_dir = Path(args.outdir)
    mpath = write_mastery(rows, out_dir)
    rpath = write_runbook(rows, out_dir)
    print(json.dumps({'mastery': str(mpath), 'runbook': str(rpath), 'count': len(rows)}, indent=2))
    return 0

if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))
