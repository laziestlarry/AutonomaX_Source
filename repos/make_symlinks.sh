#!/usr/bin/env bash
set -euo pipefail
DRY_RUN=${DRY_RUN:-1}
echo "Creating symlinks from old_path -> new_path (only when new exists and old missing)..."
while IFS=, read -r old new; do
  # Skip header line
  if [[ "$old" == "old_path" ]]; then continue; fi
  # Trim quotes
  old_clean=${old//\"/}
  new_clean=${new//\"/}
  if [[ -z "$old_clean" || -z "$new_clean" ]]; then continue; fi
  if [[ -e "$new_clean" && ! -e "$old_clean" ]]; then
    echo "[LINK] $old_clean -> $new_clean"
    if [[ "$DRY_RUN" -eq 0 ]]; then
      mkdir -p "$(dirname "$old_clean")"
      ln -s "$new_clean" "$old_clean" || true
    fi
  fi
done < <(tail -n +2 /mnt/data/repo_path_mapping.csv)
echo "Done. Set DRY_RUN=0 to actually create links."