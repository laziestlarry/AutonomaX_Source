#!/usr/bin/env python3
"""
Generate symlink script (old -> new) from ORIGINAL and RESOLVED repo lists.

- ORIGINAL: Excel/CSV with first column = old paths (e.g., "/Users/pq/...")
- RESOLVED: Excel/CSV with first column replaced by final paths ("/Volumes/...")
- Output:
    - repo_path_mapping.csv (old_path,new_path)
    - make_symlinks.sh      (DRY_RUN by default; set DRY_RUN=0 to actually create)

Usage:
  python3 make_symlinks_from_resolved.py \
    --original /path/to/my_repos_ranked.xlsx \
    --resolved /path/to/my_repos_ranked_resolved.xlsx \
    --out-dir /path/to/outdir
"""
import argparse, os, sys, pandas as pd
from pathlib import Path

def read_table(p: str) -> pd.DataFrame:
    if p.lower().endswith(".xlsx"):
        return pd.read_excel(p)
    elif p.lower().endswith(".csv"):
        return pd.read_csv(p)
    else:
        raise SystemExit("ERROR: only .xlsx or .csv supported")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", required=True, help="Original file with old paths")
    ap.add_argument("--resolved", required=True, help="Resolved file with updated paths")
    ap.add_argument("--out-dir", default=".", help="Output directory (default: current)")
    args = ap.parse_args()

    df_orig = read_table(args.original)
    df_res  = read_table(args.resolved)

    if df_orig.shape[1] == 0 or df_res.shape[1] == 0:
        raise SystemExit("ERROR: One of the files appears to have no columns.")

    col0_orig = df_orig.columns[0]
    col0_res  = df_res.columns[0]

    old_paths = df_orig[col0_orig].astype(str)
    new_paths = df_res[col0_res].astype(str)

    if len(old_paths) != len(new_paths):
        raise SystemExit(f"ERROR: Row counts differ (original={len(old_paths)} resolved={len(new_paths)}). Align inputs.")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build mapping
    map_csv = out_dir / "repo_path_mapping.csv"
    mapping = pd.DataFrame({"old_path": old_paths, "new_path": new_paths})
    mapping.to_csv(map_csv, index=False)

    # Build symlink script
    sh = out_dir / "make_symlinks.sh"
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        'DRY_RUN=${DRY_RUN:-1}',
        'MAP_FILE="${MAP_FILE:-repo_path_mapping.csv}"',
        'echo "Symlinking old -> new (only if new exists and old missing). DRY_RUN=$DRY_RUN"',
        'if [[ ! -f "$MAP_FILE" ]]; then echo "Mapping file not found: $MAP_FILE" >&2; exit 2; fi',
        'tail -n +2 "$MAP_FILE" | while IFS=, read -r old new; do',
        '  old=${old//\\"/}',
        '  new=${new//\\"/}',
        '  if [[ -z "$old" || -z "$new" ]]; then continue; fi',
        '  if [[ -e "$new" && ! -e "$old" ]]; then',
        '    echo "[LINK] $old -> $new"',
        '    if [[ "$DRY_RUN" -eq 0 ]]; then',
        '      mkdir -p "$(dirname "$old")"',
        '      ln -s "$new" "$old" || true',
        '    fi',
        '  else',
        '    if [[ ! -e "$new" ]]; then echo "[SKIP new-missing] $new"; fi',
        '    if [[ -e "$old" ]]; then echo "[SKIP old-exists] $old"; fi',
        '  fi',
        'done',
        'echo "Done. Set DRY_RUN=0 to actually create links. To use a different mapping file, set MAP_FILE=/path/to/repo_path_mapping.csv"'
    ]
    sh.write_text("\n".join(lines))
    os.chmod(sh, 0o755)

    print("Generated:", map_csv, "and", sh)

if __name__ == "__main__":
    main()
