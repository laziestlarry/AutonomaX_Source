#!/usr/bin/env bash
# replace_placeholders.sh — quick helper to set your Payoneer details
set -euo pipefail
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <PAYONEER_CHECKOUT_URL or '#'> <YOUR_PAYONEER_EMAIL>"
  exit 1
fi
PCHK="$1"
PEML="$2"
for f in   revenue_sprint_lite_payoneer/landing/index.html   revenue_sprint_lite_payoneer/landing/_redirects   revenue_sprint_lite_payoneer/social/post_and_dm.txt; do
  sed -i 's|{{PAYONEER_CHECKOUT_URL}}|'"$PCHK"'|g' "$f"
  sed -i 's|{{YOUR_PAYONEER_EMAIL}}|'"$PEML"'|g' "$f"
done
echo "Placeholders set."
