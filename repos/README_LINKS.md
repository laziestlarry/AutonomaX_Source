
# Symlink Generator (old → new)

This helper builds a mapping from your ORIGINAL list (with old paths) and your RESOLVED list (with updated paths), then emits a symlink script.

## Usage

```bash
python3 make_symlinks_from_resolved.py   --original "/path/to/my_repos_ranked.xlsx"   --resolved "/path/to/my_repos_ranked_resolved.xlsx"   --out-dir "/path/to/output_dir"
```

Outputs in `--out-dir`:
- `repo_path_mapping.csv` — `old_path,new_path`
- `make_symlinks.sh` — DRY_RUN by default. To actually create links:
  ```bash
  cd /path/to/output_dir
  DRY_RUN=0 ./make_symlinks.sh
  ```

You can also override the mapping file path:
```bash
MAP_FILE=/custom/path/mapping.csv DRY_RUN=0 ./make_symlinks.sh
```
