
# Repo Path Resolver (Local)

This toolkit updates the **first column** of your repo list (e.g. `Link to Local Folder`) by checking if the original path exists and, if not, searching your external drives for the correct location.

**Your request implemented**:
- If path exists at `/Users/pq/...` → leave as-is and move to next row.
- If missing at old address → search **/Volumes/psiqo** first, then **/Volumes/PQuattro** for a matching folder name.
- If found → replace first column with the best match and annotate resolution method.
- If not found anywhere → leave as missing but clearly flagged.

## Files

- `resolve_repo_paths.py` — main resolver script.
- `resolver_config.json` — example config with search roots and depth.
- (From earlier steps) You may use `my_repos_ranked.xlsx` as input.

## Quick Start (Mac)

1. Open Terminal in the folder containing your Excel file (e.g. `my_repos_ranked.xlsx`).  
2. Download `resolve_repo_paths.py` and `resolver_config.json` to that folder or point to them with full paths.

3. Run:

```bash
python3 "/mnt/data/repo_path_resolver/resolve_repo_paths.py" --in "/path/to/my_repos_ranked.xlsx" --out "/path/to/my_repos_ranked_resolved.xlsx"
```

By default it searches roots:
- `/Volumes/psiqo`
- `/Volumes/PQuattro`

To override roots:

```bash
python3 "/mnt/data/repo_path_resolver/resolve_repo_paths.py" --in "/path/to/my_repos_ranked.xlsx" --out "/path/to/my_repos_ranked_resolved.xlsx" --roots "/Volumes/psiqo" "/Volumes/PQuattro"
```

Limit deep scans if you want to speed it up:

```bash
python3 "/mnt/data/repo_path_resolver/resolve_repo_paths.py" --in "/path/to/my_repos_ranked.xlsx" --out "/path/to/my_repos_ranked_resolved.xlsx" --max-depth 10
```

## Output

The resolver **replaces the first column** with the best-found path and adds these audit columns at the end:

- `__resolution_method` — one of:
  - `unchanged` → original path exists
  - `found_psiqo_or_pquattro` → located on one of the drives
  - `not_found` → searched but couldn’t locate
  - `missing_non_pq` → original path missing and wasn’t under `/Users/pq`
  - `found_non_dir` → matched a path that wasn’t a directory (rare)

- `__examined_dirs` — number of directories walked while searching
- `__notes` — quick notes like the basename that was searched

## Tips

- The search uses the **folder name** of the original path (e.g., if original is `/Users/pq/code/myapp`, it searches for `myapp`). If you have multiple repos with the same name, it will prefer candidates that **look like repos** (contain `.git` or typical dev files) and pick the **shortest** path.
- If you want to keep the original sheet untouched: duplicate it first and run the resolver on the duplicate.

## Example

```bash
python3 "/mnt/data/repo_path_resolver/resolve_repo_paths.py" --in "/Users/pq/Documents/my_repos_ranked.xlsx" --out "/Users/pq/Documents/my_repos_ranked_resolved.xlsx"
```

You'll see a summary printed at the end, e.g.:

```
Summary: {'unchanged': 120, 'found_psiqo_or_pquattro': 90, 'not_found': 8}
```

---

If you’d like, I can also generate a **post-check symlink script** based on the resolved file to keep old tool configs working while you migrate.
