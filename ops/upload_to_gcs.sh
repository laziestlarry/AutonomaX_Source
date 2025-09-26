#!/usr/bin/env bash
set -euo pipefail

# upload_to_gcs.sh — Sync local artifacts to a GCS bucket/prefix for faster cloud initiation
# Usage:
#   ./ops/upload_to_gcs.sh gs://YOUR_BUCKET/autonomax
#   ./ops/upload_to_gcs.sh gs://YOUR_BUCKET/autonomax data_room/inventory data_room/blueprints revenue_sprint_lite_payoneer/delivery

DEST=${1:?"Destination GCS prefix required, e.g., gs://my-bucket/autonomax"}
shift || true
PATHS=("data_room/inventory" "data_room/blueprints" "revenue_sprint_lite_payoneer/delivery")
if [[ $# -gt 0 ]]; then PATHS=("$@"); fi

command -v gsutil >/dev/null 2>&1 || { echo "gsutil not found; install gcloud SDK"; exit 2; }

for P in "${PATHS[@]}"; do
  if [[ -d "$P" ]]; then
    echo "==> Sync $P -> $DEST/$P"
    gsutil -m rsync -r "$P" "$DEST/$P"
  else
    echo "Skip $P (not a directory)"
  fi
done

echo "==> Upload complete"

