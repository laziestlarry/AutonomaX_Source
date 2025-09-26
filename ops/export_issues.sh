#!/usr/bin/env bash
set -euo pipefail

# export_issues.sh — Export tasks.csv to GitHub/GitLab JSON or CLI commands
# Examples:
#   ./ops/export_issues.sh json data_room/inventory/tasks.csv data_room/blueprints/exports
#   ./ops/export_issues.sh gh-cli data_room/inventory/tasks.csv . ORG/REPO | bash
#   ./ops/export_issues.sh glab-cli data_room/inventory/tasks.csv . GROUP/REPO | bash

FMT=${1:?"json|gh-cli|glab-cli"}
CSV=${2:?"Path to tasks.csv"}
OUT=${3:-.}
REPO=${4:-}

if [[ "$FMT" == "json" ]]; then
  python3 tools/issues_export.py --csv "$CSV" --out "$OUT" --format json
elif [[ "$FMT" == "gh-cli" ]]; then
  python3 tools/issues_export.py --csv "$CSV" --out "$OUT" --format gh-cli --repo "${REPO:?ORG/REPO required}" 
elif [[ "$FMT" == "glab-cli" ]]; then
  python3 tools/issues_export.py --csv "$CSV" --out "$OUT" --format glab-cli --repo "${REPO:?GROUP/REPO required}"
else
  echo "Unknown format: $FMT"; exit 2
fi

