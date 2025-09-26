#!/usr/bin/env python3
"""
Append next batch of tasks from the latest blueprint summary into tasks.csv.

Keeps a checkpoint at data_room/blueprints/batch_checkpoint.json with index of
next task to process. Re-run to append the next batch.

Usage:
  python tools/batch_blueprint.py --batch 20
  python tools/batch_blueprint.py --summary data_room/blueprints/summary_XXXX.json --batch 50
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
from typing import List, Dict, Any

BP_DIR = Path('data_room/blueprints')
CKPT = BP_DIR / 'batch_checkpoint.json'
TASKS_CSV = Path('data_room/inventory/tasks.csv')

def latest_summary() -> Path | None:
    if not BP_DIR.exists():
        return None
    sums = sorted(BP_DIR.glob('summary_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    return sums[0] if sums else None

def load_checkpoint() -> Dict[str, Any]:
    if CKPT.exists():
        try: return json.loads(CKPT.read_text())
        except Exception: return {}
    return {}

def save_checkpoint(ck: Dict[str, Any]) -> None:
    CKPT.parent.mkdir(parents=True, exist_ok=True)
    CKPT.write_text(json.dumps(ck, indent=2))

def append_tasks(rows: List[Dict[str, Any]]):
    TASKS_CSV.parent.mkdir(parents=True, exist_ok=True)
    import csv
    exists = TASKS_CSV.exists()
    with open(TASKS_CSV, 'a' if exists else 'w', newline='') as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["ts","role","desc","path"])  # header
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        for r in rows:
            w.writerow([ts, r.get('role',''), r.get('task',''), r.get('ref','')])

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--summary', default='')
    ap.add_argument('--batch', type=int, default=20)
    args = ap.parse_args(argv)

    summ_path = Path(args.summary) if args.summary else latest_summary()
    if not summ_path or not summ_path.exists():
        print('No blueprint summary found. Generate one first.')
        return 2
    bp = json.loads(summ_path.read_text())
    tasks = bp.get('tasks') or []
    ck = load_checkpoint()
    idx = int(ck.get('next_index', 0))
    end = min(idx + args.batch, len(tasks))
    batch = tasks[idx:end]
    if not batch:
        print('No more tasks to append. All done.')
        return 0
    append_tasks(batch)
    ck.update({'summary': str(summ_path), 'next_index': end, 'appended': len(batch), 'total': len(tasks)})
    save_checkpoint(ck)
    print(json.dumps({'appended': len(batch), 'next_index': end, 'total': len(tasks)}, indent=2))
    return 0

if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))

