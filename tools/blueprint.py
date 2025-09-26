#!/usr/bin/env python3
"""
Blueprint generator for ranked repositories/resources.

Reads a CSV (e.g., /Users/pq/Downloads/my_repos_ranked.csv) and produces:
- data_room/blueprints/blueprint_YYYYmmdd_HHMMSS.md (human-readable plan)
- data_room/blueprints/project_plan_YYYYmmdd_HHMMSS.csv (task matrix)
- data_room/blueprints/summary_YYYYmmdd_HHMMSS.json (machine-readable)

Usage:
  # Single file
  python tools/blueprint.py --file /path/to/my_repos_ranked.csv --label local --top 12
  # Multiple files
  python tools/blueprint.py --file repos/a.csv --file repos/b.csv --label repos --top 20
  # Directory of CSVs
  python tools/blueprint.py --dir repos --label repos --top 20

CSV expectations (flexible):
- Acceptable columns (any subset): repo,url,path,name,title,desc,tags,rank,score,priority
- If no header, first column is treated as a path/url/name in order of preference.
"""
from __future__ import annotations
import argparse, csv, json, os, sys, time
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROLES = ["research","analysis","dev","data","growth","pm","advisor"]

def load_rows(file_path: Path) -> List[Dict[str, Any]]:
    txt = file_path.read_text(errors='ignore')
    # Try CSV with header
    out: List[Dict[str, Any]] = []
    try:
        import io
        reader = csv.DictReader(io.StringIO(txt))
        if reader.fieldnames:
            for i, r in enumerate(reader):
                r['__rownum'] = i
                out.append(r)
            if out:
                return out
    except Exception:
        pass
    # Fallback: simple lines, first column only
    rows = []
    for i, line in enumerate(txt.splitlines()):
        s = line.strip()
        if not s or s.startswith('#'): continue
        if ',' in s:
            s = s.split(',')[0].strip()
        rows.append({'name': s, '__rownum': i})
    return rows

def pick_field(row: Dict[str, Any], candidates: List[str]) -> str:
    for c in candidates:
        v = row.get(c)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ''

def normalize(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for i, r in enumerate(rows):
        name = pick_field(r, ['name','title','filename','repo','path','url']) or f"item_{i+1}"
        url  = pick_field(r, ['url','repo'])
        # Accept alternate path column names from Master Index
        path = pick_field(r, ['path','probable local path','probable local path existing inventories','file path','local path','filepath'])
        # Purpose maps to desc
        desc = pick_field(r, ['desc','description','purpose'])
        # Category can map to tags
        tags = pick_field(r, ['tags','category'])
        try:
            score = float(pick_field(r, ['score','rank','priority']) or 0)
        except Exception:
            score = 0.0
        out.append({
            'name': name,
            'url': url,
            'path': path,
            'desc': desc,
            'tags': tags,
            'score': score,
            'rownum': r.get('__rownum', i)
        })
    # Order by score desc then original order
    out.sort(key=lambda x: (-x['score'], x['rownum']))
    return out

def draft_tasks(item: Dict[str, Any], phase: str, priority: int) -> List[Dict[str, Any]]:
    name = item['name']
    base = item['url'] or item['path'] or name
    tasks = []
    tasks.append({'role':'research','task': f'skim + summarize objectives for {name}', 'phase': phase, 'priority': priority, 'ref': base})
    tasks.append({'role':'analysis','task': f'outline value props and risks for {name}', 'phase': phase, 'priority': priority, 'ref': base})
    if 'shopify' in name.lower():
        tasks.append({'role':'dev','task': 'wire Shopify backfills to BQ + /bi', 'phase': phase, 'priority': priority, 'ref': base})
    if 'gcp' in name.lower() or 'cloud' in name.lower() or 'run' in name.lower():
        tasks.append({'role':'dev','task': 'harden deploy (staging/prod) + alerts', 'phase': phase, 'priority': priority, 'ref': base})
    tasks.append({'role':'data','task': 'define KPIs and freshness for BI', 'phase': phase, 'priority': priority, 'ref': base})
    tasks.append({'role':'growth','task': 'prepare 3 posts + 10 DMs plan', 'phase': phase, 'priority': priority, 'ref': base})
    tasks.append({'role':'pm','task': 'timeline + risk register', 'phase': phase, 'priority': priority, 'ref': base})
    tasks.append({'role':'advisor','task': 'review blueprint and sign-off', 'phase': phase, 'priority': priority, 'ref': base})
    return tasks

def generate_blueprint(items: List[Dict[str, Any]], label: str, top_n: int) -> Dict[str, Any]:
    selected = items[:top_n]
    # Prefer a first pipeline if any item matches laziestlarry
    first = next((x for x in selected if 'laziestlarry' in x['name'].lower()), selected[0] if selected else None)
    phases = [
        {'name':'P0 – Intake & Triage','window':'Day 0–1'},
        {'name':'P1 – MVP Integration','window':'Day 1–3'},
        {'name':'P2 – BI & Growth','window':'Day 3–5'},
    ]
    task_rows: List[Dict[str, Any]] = []
    for pri, it in enumerate(selected, start=1):
        phase = phases[0]['name'] if it is first else phases[1]['name']
        task_rows.extend(draft_tasks(it, phase, pri))
    summary = {
        'label': label,
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'count_total': len(items),
        'count_selected': len(selected),
        'first_pipeline': first,
        'phases': phases,
        'selected': selected,
        'tasks': task_rows,
    }
    return summary

def write_outputs(bp: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')
    md_path = out_dir / f'blueprint_{ts}.md'
    json_path = out_dir / f'summary_{ts}.json'
    csv_path = out_dir / f'project_plan_{ts}.csv'

    # Markdown
    first = bp.get('first_pipeline') or {}
    def line(s: str) -> str: return s + '\n'
    blocks = []
    blocks.append(line(f"# AutonomaX Blueprint — {bp['label']} ({bp['generated_at']})"))
    blocks.append(line("## Overview"))
    blocks.append(line(f"Selected: {bp['count_selected']} of {bp['count_total']} (top-ranked)"))
    if first:
        blocks.append(line(f"First pipeline candidate: {first.get('name')} (ref: {first.get('url') or first.get('path')})"))
    blocks.append(line("\n## Phases"))
    for ph in bp['phases']:
        blocks.append(line(f"- {ph['name']} ({ph['window']})"))
    blocks.append(line("\n## Candidates"))
    for it in bp['selected']:
        ref = it.get('url') or it.get('path') or it.get('name')
        blocks.append(line(f"- {it['name']} — score {it['score']} — {ref}"))
    blocks.append(line("\n## Initial Tasks (by role)"))
    by_role: Dict[str, List[Dict[str, Any]]] = {r:[] for r in ROLES}
    for t in bp['tasks']:
        by_role.setdefault(t['role'], []).append(t)
    for role in ROLES:
        rows = by_role.get(role, [])
        if not rows: continue
        blocks.append(line(f"### {role}"))
        for t in rows:
            blocks.append(line(f"- [{t['phase']}] (P{t['priority']}) {t['task']} — ref: {t['ref']}"))
    md_path.write_text(''.join(blocks))

    # JSON
    json_path.write_text(json.dumps(bp, indent=2))

    # CSV
    import csv as _csv
    with open(csv_path, 'w', newline='') as f:
        w = _csv.DictWriter(f, fieldnames=['ts','role','task','phase','priority','ref'])
        w.writeheader()
        ts_now = bp['generated_at']
        for t in bp['tasks']:
            w.writerow({'ts': ts_now, 'role': t['role'], 'task': t['task'], 'phase': t['phase'], 'priority': t['priority'], 'ref': t['ref']})

    return {'markdown': str(md_path), 'json': str(json_path), 'csv': str(csv_path)}

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--file', action='append', default=[], help='CSV file(s) with ranked resources (repeatable)')
    ap.add_argument('--dir', default='', help='Directory containing .csv files to include')
    ap.add_argument('--label', default='local', help='Label for this blueprint set')
    ap.add_argument('--top', type=int, default=12, help='How many top entries to select')
    ap.add_argument('--out', default='data_room/blueprints', help='Output directory for blueprint artifacts')
    args = ap.parse_args(argv)

    sources: List[Path] = []
    for f in args.file:
        p = Path(f).expanduser(); 
        if p.exists(): sources.append(p)
    if args.dir:
        d = Path(args.dir).expanduser()
        if d.exists():
            sources.extend(sorted(d.glob('*.csv')))
    if not sources:
        print("No CSV sources found. Use --file or --dir.", file=sys.stderr)
        return 2
    rows: List[Dict[str, Any]] = []
    for src in sources:
        rows.extend(load_rows(src))
    items = normalize(rows)
    bp = generate_blueprint(items, args.label, args.top)
    paths = write_outputs(bp, Path(args.out))
    print(json.dumps({'ok': True, 'outputs': paths}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
