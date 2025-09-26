#!/usr/bin/env bash
set -euo pipefail

# upload_to_drive.sh — Sync local artifacts to Google Drive via rclone
# Prereq: rclone installed and a remote configured (e.g., 'drive:').
#   rclone config    # create a 'drive' remote
# Usage:
#   ./ops/upload_to_drive.sh drive:AutonomaX
#   ./ops/upload_to_drive.sh drive:AutonomaX data_room/inventory data_room/blueprints revenue_sprint_lite_payoneer/delivery

DEST=${1:?"Destination rclone remote:path required, e.g., drive:AutonomaX"}
shift || true
PATHS=("data_room/inventory" "data_room/blueprints" "revenue_sprint_lite_payoneer/delivery")
if [[ $# -gt 0 ]]; then PATHS=("$@"); fi

command -v rclone >/dev/null 2>&1 || { echo "rclone not found; install rclone"; exit 2; }

for P in "${PATHS[@]}"; do
  if [[ -d "$P" ]]; then
    echo "==> Sync $P -> $DEST/$P"
    rclone sync -P "$P" "$DEST/$P"
  else
    echo "Skip $P (not a directory)"
  fi
done

echo "==> Drive upload complete"

