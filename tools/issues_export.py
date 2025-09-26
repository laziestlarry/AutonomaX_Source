#!/usr/bin/env python3
"""
issues_export.py — Convert tasks CSV into GitHub/GitLab issue payloads or CLI commands.

Usage:
  python tools/issues_export.py --csv data_room/inventory/tasks.csv --out data_room/blueprints/exports --format json
  python tools/issues_export.py --csv data_room/inventory/tasks.csv --out . --format gh-cli --repo ORG/REPO

Formats:
  - json: writes issues_github_*.json (title,body,labels,assignees) and issues_gitlab_*.json
  - gh-cli: prints gh issue create commands (requires gh auth)
  - glab-cli: prints glab issue create commands (requires glab auth)
"""
from __future__ import annotations
import argparse, csv, json, sys, time
from pathlib import Path
from typing import List, Dict

def load_tasks(csv_path: Path) -> List[Dict[str,str]]:
    rows: List[Dict[str,str]] = []
    with open(csv_path, newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

def to_issues(rows: List[Dict[str,str]]) -> List[Dict[str, str]]:
    issues = []
    for r in rows:
        title = f"[{r.get('role','task')}] {r.get('desc','')}".strip()
        body = f"Ref: {r.get('path','')}\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        labels = [r.get('role','task')]
        issues.append({'title': title, 'body': body, 'labels': labels, 'assignees': []})
    return issues

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--format', choices=['json','gh-cli','glab-cli'], default='json')
    ap.add_argument('--repo', default='')
    args = ap.parse_args(argv)

    rows = load_tasks(Path(args.csv))
    issues = to_issues(rows)
    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')

    if args.format == 'json':
        gh = out_dir / f'issues_github_{ts}.json'
        gl = out_dir / f'issues_gitlab_{ts}.json'
        gh.write_text(json.dumps(issues, indent=2))
        gl.write_text(json.dumps([{'title': i['title'], 'description': i['body'], 'labels': ','.join(i['labels'])} for i in issues], indent=2))
        print(json.dumps({'github_json': str(gh), 'gitlab_json': str(gl)}, indent=2))
    elif args.format == 'gh-cli':
        if not args.repo:
            print('--repo ORG/REPO required for gh-cli format', file=sys.stderr); return 2
        for i in issues:
            labels = ','.join(i['labels'])
            print(f"gh issue create -R {args.repo} -t {json.dumps(i['title'])} -b {json.dumps(i['body'])} -l {json.dumps(labels)}")
    elif args.format == 'glab-cli':
        if not args.repo:
            print('--repo GROUP/REPO required for glab-cli format', file=sys.stderr); return 2
        for i in issues:
            labels = ','.join(i['labels'])
            print(f"glab issue create --repo {args.repo} --title {json.dumps(i['title'])} --description {json.dumps(i['body'])} --label {json.dumps(labels)}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

