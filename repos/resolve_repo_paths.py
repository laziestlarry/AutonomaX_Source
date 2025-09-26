#!/usr/bin/env python3
"""
Resolve repo paths:
- Input Excel/CSV with the first column = "Link to Local Folder"
- If path exists as-is, keep it (proceed to next row).
- If missing and starts with /Users/pq, try to locate the repo on /Volumes/psiqo, then /Volumes/PQuattro.
  Matching strategy:
    1) Exact folder name match (basename) preferred.
    2) If multiple candidates, prefer ones containing ".git" or well-known repo markers.
    3) If still multiple, prefer shortest path (closest to root).
- Writes an updated file with the first column replaced by the best resolved path.
- Also writes a detailed report with resolution method and candidates examined.

Usage:
  python3 resolve_repo_paths.py --in my_repos_ranked.xlsx --out my_repos_ranked_resolved.xlsx
Options:
  --sheet SHEETNAME   (for Excel; default = first sheet)
  --roots /Volumes/psiqo /Volumes/PQuattro  (override default search roots)
  --max-depth N       (limit deep scanning; default=12)
  --ext csv|xlsx      (output format; default inferred from --out)
"""
import argparse, os, sys, re, time, hashlib
from pathlib import Path
import pandas as pd

DEFAULT_ROOTS = ["/Volumes/psiqo", "/Volumes/PQuattro"]
REPO_HINTS = {".git", "pyproject.toml", "package.json", "go.mod", "Pipfile", "requirements.txt", ".github"}

def path_exists(p: str) -> bool:
    try:
        return os.path.exists(p)
    except Exception:
        return False

def iter_dirs(root: Path, max_depth: int = 12):
    # BFS directory walk with depth control
    from collections import deque
    q = deque([(root, 0)])
    while q:
        cur, depth = q.popleft()
        # Yield only directories (files aren't candidate repo roots)
        try:
            with os.scandir(cur) as it:
                for entry in it:
                    if not entry.is_dir(follow_symlinks=False):
                        continue
                    yield Path(entry.path), depth + 1
                    if depth + 1 < max_depth:
                        q.append((Path(entry.path), depth + 1))
        except PermissionError:
            continue
        except FileNotFoundError:
            continue

def looks_like_repo(dirpath: Path) -> bool:
    try:
        names = set(os.listdir(dirpath))
    except Exception:
        return False
    # simple heuristic: any repo hint present
    return any(h in names for h in REPO_HINTS)

def score_candidate(candidate: Path, target_name: str) -> tuple:
    """
    Higher score is better.
    - Exact name match: +100
    - Repo-looking: +20
    - Shortness (fewer parts): + up to 10 (shorter is better)
    """
    score = 0
    if candidate.name == target_name:
        score += 100
    if looks_like_repo(candidate):
        score += 20
    # shorter path is better
    parts = len(candidate.parts)
    score += max(0, 10 - parts)
    return (score, -parts)  # tie-breaker: fewer parts

def find_best_match(target_name: str, roots, max_depth: int):
    best = None
    best_score = None
    examined = 0
    for root in roots:
        rpath = Path(root)
        if not rpath.exists():
            continue
        for d, depth in iter_dirs(rpath, max_depth=max_depth):
            examined += 1
            # quick filter: name match first
            if d.name != target_name:
                continue
            sc = score_candidate(d, target_name)
            if best_score is None or sc > best_score:
                best, best_score = d, sc
    return best, examined

def resolve_paths(df: pd.DataFrame, col0: str, roots, max_depth: int):
    rows = []
    for idx, row in df.iterrows():
        original = str(row[col0])
        resolved = original
        method = "unchanged"
        examined = 0
        note = ""

        # If path exists, keep
        if path_exists(original):
            rows.append((resolved, method, examined, note))
            continue

        # Only redirect if it looks like an old /Users/pq path
        if original.startswith("/Users/pq"):
            target_name = Path(original).name
            best, examined = find_best_match(target_name, roots, max_depth)
            if best and path_exists(str(best)):
                resolved = str(best)
                # final safety: ensure it's a directory
                if not os.path.isdir(resolved):
                    method = "found_non_dir"
                else:
                    method = "found_psiqo_or_pquattro"
            else:
                method = "not_found"
                note = f"searched_by_name={target_name}"
        else:
            method = "missing_non_pq"
            note = "original path missing and not under /Users/pq"

        rows.append((resolved, method, examined, note))

    # Build result columns
    df_out = df.copy()
    df_out[col0] = [r[0] for r in rows]
    df_out["__resolution_method"] = [r[1] for r in rows]
    df_out["__examined_dirs"] = [r[2] for r in rows]
    df_out["__notes"] = [r[3] for r in rows]
    return df_out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input Excel/CSV file")
    ap.add_argument("--out", dest="out", required=True, help="Output file (xlsx or csv)")
    ap.add_argument("--sheet", dest="sheet", default=None, help="Excel sheet name (default: first)")
    ap.add_argument("--roots", nargs="*", default=DEFAULT_ROOTS, help="Search roots (default: %(default)s)")
    ap.add_argument("--max-depth", dest="max_depth", type=int, default=12, help="Max search depth (default: 12)")
    args = ap.parse_args()

    inp = args.inp
    outp = args.out
    sheet = args.sheet
    roots = args.roots
    max_depth = args.max_depth

    # Read input
    if inp.lower().endswith(".xlsx"):
        df = pd.read_excel(inp, sheet_name=sheet)
    elif inp.lower().endswith(".csv"):
        df = pd.read_csv(inp)
    else:
        print("ERROR: Input must be .xlsx or .csv", file=sys.stderr)
        sys.exit(2)

    if df.shape[1] == 0:
        print("ERROR: No columns in input file", file=sys.stderr)
        sys.exit(2)

    col0 = df.columns[0]

    df_res = resolve_paths(df, col0, roots, max_depth)

    # Write output
    if outp.lower().endswith(".xlsx"):
        df_res.to_excel(outp, index=False)
    elif outp.lower().endswith(".csv"):
        df_res.to_csv(outp, index=False)
    else:
        print("ERROR: Output must be .xlsx or .csv", file=sys.stderr)
        sys.exit(2)

    # Also emit a small summary to stdout
    counts = df_res["__resolution_method"].value_counts().to_dict()
    print("Summary:", counts)

if __name__ == "__main__":
    main()
