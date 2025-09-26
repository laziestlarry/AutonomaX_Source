#!/usr/bin/env python3
"""
Archive Upgrade Helper
======================

This helper script upgrades the AutonomaX codebase using a master index CSV.
It scans the extracted `Archive` directory for each entry in the
`AutonomaX_Master_Index.csv` file and attempts to locate matching files
or directories.  For each entry it records whether a match was found,
along with a list of candidate paths.  The script writes a new CSV
(`AutonomaX_Master_Index_resolved.csv`) with the resolved paths and
summary information.

Usage:
    python archive_upgrade.py --index /path/to/AutonomaX_Master_Index.csv --root /path/to/Archive --out /path/to/output.csv

If `--index` is omitted, it defaults to `AutonomaX_Master_Index.csv` in
the current working directory.  If `--root` is omitted, it defaults to
`Archive` in the current working directory.  If `--out` is omitted, it
will write `AutonomaX_Master_Index_resolved.csv` next to the index.

This script does not modify any source files; it merely inspects the
filesystem.  It can be extended to perform additional upgrade tasks
such as copying data from the dataroom, but those are not included by
default.
"""

import argparse
import csv
import fnmatch
import os
from pathlib import Path
from typing import List


def parse_arguments() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Resolve paths in AutonomaX master index")
    ap.add_argument("--index", dest="index", default="AutonomaX_Master_Index.csv",
                    help="Path to the master index CSV (default: AutonomaX_Master_Index.csv)")
    ap.add_argument("--root", dest="root", default="Archive",
                    help="Root directory to search (default: Archive)")
    ap.add_argument("--out", dest="out", default=None,
                    help="Output CSV path (default: <index>_resolved.csv)")
    return ap.parse_args()


def find_candidates(root: Path, pattern: str) -> List[str]:
    """
    Search for files or directories matching the given pattern under root.

    The pattern may contain wildcards (e.g. "autosync/*.py") or end with a
    slash to indicate a directory.  The search is case-sensitive.
    Returns a list of absolute paths as strings.
    """
    candidates: List[str] = []
    # If pattern is empty, return empty list
    if not pattern:
        return candidates
    # Handle directory patterns ending with a slash
    if pattern.endswith('/'):
        dir_name = pattern.rstrip('/')
        for dirpath, dirnames, filenames in os.walk(root):
            for d in dirnames:
                if d == Path(dir_name).name:
                    candidates.append(str(Path(dirpath) / d))
        return candidates

    # Handle wildcard patterns (e.g. autosync/*.py)
    if '*' in pattern or '?' in pattern:
        dir_part, file_part = os.path.split(pattern)
        search_dir = root / dir_part if dir_part else root
        if not search_dir.exists():
            return candidates
        for dirpath, dirnames, filenames in os.walk(search_dir):
            for filename in filenames:
                if fnmatch.fnmatch(filename, file_part):
                    candidates.append(str(Path(dirpath) / filename))
        return candidates

    # Otherwise treat as exact file name
    filename = pattern
    for dirpath, dirnames, filenames in os.walk(root):
        if filename in filenames:
            candidates.append(str(Path(dirpath) / filename))
    return candidates


def resolve_index(index_path: Path, root: Path) -> List[dict]:
    """
    Read the master index CSV and attempt to resolve each entry to
    candidate paths under root.  Returns a list of dictionaries
    representing the rows with additional fields.
    """
    rows = []
    with open(index_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = (row.get('Filename') or row.get('Filename / Folder') or
                        row.get('file') or row.get('name') or row.get('Filename / folder') or
                        row.get('filename') or '').strip()
            category = (row.get('Category') or row.get('category') or '').strip()
            purpose = (row.get('Purpose') or row.get('purpose') or '').strip()
            probable = (row.get('Probable Local Path') or row.get('probable local path') or
                        row.get('Probable Path') or '').strip()
            # Search for candidates only if filename is non-empty
            candidates: List[str] = []
            if filename:
                candidates = find_candidates(root, filename)
            resolved = {
                'Category': category,
                'Filename': filename,
                'Purpose': purpose,
                'Probable Local Path': probable,
                'Found': 'yes' if candidates else 'no',
                'Candidate Paths': "|".join(candidates),
                'Chosen Path': candidates[0] if candidates else ''
            }
            rows.append(resolved)
    return rows


def write_output(rows: List[dict], out_path: Path) -> None:
    fieldnames = [
        'Category', 'Filename', 'Purpose', 'Probable Local Path',
        'Found', 'Candidate Paths', 'Chosen Path'
    ]
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    args = parse_arguments()
    index_path = Path(args.index)
    root = Path(args.root)
    if not index_path.exists():
        print(f"Index file not found: {index_path}", file=sys.stderr)
        return
    if not root.exists():
        print(f"Search root not found: {root}", file=sys.stderr)
        return
    rows = resolve_index(index_path, root)
    out_path = Path(args.out) if args.out else index_path.with_name(index_path.stem + '_resolved.csv')
    write_output(rows, out_path)
    print(f"Resolved index written to {out_path} ({len(rows)} entries)")


if __name__ == '__main__':
    import sys
    main()