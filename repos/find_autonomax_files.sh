#!/usr/bin/env bash
# find_autonomax_files.sh
# Search for AutonomaX "status-impactful" files across local drives.
# Usage:
#   bash find_autonomax_files.sh                      # default roots
#   bash find_autonomax_files.sh /Users/pq /Volumes/psiqo /Volumes/PQuattro   # custom roots
#   bash find_autonomax_files.sh --open "main.py"     # reveal in Finder the first match for a specific filename
#
# Output: AutonomaX_Master_Index_found.csv (in current directory)

set -euo pipefail

# ---------- Config: filenames to search ----------
# Patterns support exact names and simple wildcards (*). Directories end with '/'.

FILENAMES=(
  "main.py"
  "commander.py"
  "server.js"
  "analytics_dashboard_fixed.py"
  ".env"
  "deploy.sh"
  ".github/workflows/deploy.yml"
  "cloudbuild.yaml"
  "firebase.json"
  "firebase.config.js"
  "requirements.txt"
  "package.json"
  "shopify_sync.py"
  "shopify/products.csv"
  "etsy_commander_bundle.zip"
  "commander_import_samples.zip"
  "autosync/*.py"
  "flows/*.flow"
  "videos/"
  "fiverr/gig.md"
  "fiverr/thumbnail.png"
  "LeadMagnet_LazyLarry.pdf"
  "landing/index.html"
  "205_strategies.json"
  "commander_knowledge_base/"
  "analytics/looker_template.json"
  "scripts/make_products_from_yaml.py"
  "scripts/scheduler_setup.sh"
  "commander_intelligence_server.zip"
  "commander_knowledge_base.zip"
  "Brain_modules.zip"
  "knowldg.zip"
  "Cognosystemized.txt"
)

# ---------- Helper: CSV escaping ----------
csv_escape() {
  local s="$1"
  s="${s//\"/\"\"}"
  printf "\"%s\"" "$s"
}

# ---------- Roots ----------
if [[ "${1:-}" == "--open" ]]; then
  TARGET="${2:-}"
  if [[ -z "$TARGET" ]]; then
    echo "Provide a filename after --open"; exit 1
  fi
  # Try Spotlight first, then find
  # Spotlight: exact name match first
  if command -v mdfind >/dev/null 2>&1; then
    MATCHES=$(mdfind -name "$TARGET" | head -n 1 || true)
  fi
  if [[ -z "${MATCHES:-}" ]]; then
    MATCHES=$(find /Users /Volumes -type f -iname "$(basename "$TARGET")" 2>/dev/null | head -n 1 || true)
  fi
  if [[ -n "${MATCHES:-}" ]]; then
    echo "Opening: $MATCHES"
    open -R "$MATCHES"
    exit 0
  else
    echo "No match found for $TARGET"; exit 2
  fi
fi

if [[ "$#" -ge 1 ]]; then
  ROOTS=("$@")
else
  ROOTS=(/Users/pq /Volumes/psiqo /Volumes/PQuattro)
fi

# Only keep existing roots
EXISTING_ROOTS=()
for r in "${ROOTS[@]}"; do
  if [[ -d "$r" ]]; then
    EXISTING_ROOTS+=("$r")
  fi
done

if [[ "${#EXISTING_ROOTS[@]}" -eq 0 ]]; then
  echo "No valid search roots found. Provide at least one existing directory."
  exit 1
fi

OUT_CSV="AutonomaX_Master_Index_found.csv"
echo "\"Filename\",\"Found\",\"Paths\"" > "$OUT_CSV"

# ---------- Search loop ----------
for NAME in "${FILENAMES[@]}"; do
  MATCHED_PATHS=()

  IS_DIR_PATTERN=0
  if [[ "$NAME" == */ ]]; then
    IS_DIR_PATTERN=1
    BASE="$(basename "$NAME")"
  else
    BASE="$(basename "$NAME")"
  fi

  # 1) Spotlight (mdfind) – fast, macOS only
  if command -v mdfind >/dev/null 2>&1; then
    if [[ "$IS_DIR_PATTERN" -eq 1 ]]; then
      CANDIDATES=$(mdfind "kMDItemFSName == '$BASE'" 2>/dev/null || true)
    else
      # If wildcard present, do a broader name search
      if [[ "$NAME" == *"*"* ]]; then
        CANDIDATES=$(mdfind "kMDItemFSName == '*${BASE#\*}*'" 2>/dev/null || true)
      else
        CANDIDATES=$(mdfind "kMDItemFSName == '$BASE'" 2>/dev/null || true)
      fi
    fi
    # Filter candidates by roots
    if [[ -n "${CANDIDATES:-}" ]]; then
      while IFS= read -r p; do
        for r in "${EXISTING_ROOTS[@]}"; do
          if [[ "$p" == "$r"* ]]; then
            if [[ "$IS_DIR_PATTERN" -eq 1 && -d "$p" ]]; then
              MATCHED_PATHS+=("$p")
            elif [[ "$IS_DIR_PATTERN" -eq 0 && -f "$p" ]]; then
              # For patterns like autosync/*.py ensure parent folder matches
              if [[ "$NAME" == *"*"*"/"* ]]; then
                PARENT="$(dirname "$p")"
                if [[ "$PARENT" == *"/${NAME%%/*}" ]]; then
                  MATCHED_PATHS+=("$p")
                else
                  MATCHED_PATHS+=("$p")
                fi
              else
                MATCHED_PATHS+=("$p")
              fi
            fi
          fi
        done
      done <<< "$CANDIDATES"
    fi
  fi

  # 2) POSIX find fallback and pattern matching
  if [[ "${#MATCHED_PATHS[@]}" -eq 0 ]]; then
    for r in "${EXISTING_ROOTS[@]}"; do
      if [[ "$IS_DIR_PATTERN" -eq 1 ]]; then
        while IFS= read -r p; do MATCHED_PATHS+=("$p"); done < <(find "$r" -type d -iname "$BASE" 2>/dev/null || true)
      else
        if [[ "$NAME" == *"*"* ]]; then
          # Split "dir/*.ext" into dir and pattern if applicable
          if [[ "$NAME" == */* ]]; then
            PARENT_DIR="${NAME%%/*}"
            CHILD_PATTERN="${NAME#*/}"
            while IFS= read -r p; do MATCHED_PATHS+=("$p"); done < <(find "$r" -type f -path "*/$PARENT_DIR/*" -name "$CHILD_PATTERN" 2>/dev/null || true)
          else
            while IFS= read -r p; do MATCHED_PATHS+=("$p"); done < <(find "$r" -type f -name "$NAME" 2>/dev/null || true)
          fi
        else
          while IFS= read -r p; do MATCHED_PATHS+=("$p"); done < <(find "$r" -type f -iname "$BASE" 2>/dev/null || true)
        fi
      fi
    done
  fi

  # Deduplicate
  if [[ "${#MATCHED_PATHS[@]}" -gt 0 ]]; then
    IFS=$'\n' read -rd '' -a MATCHED_PATHS <<< "$(printf "%s\n" "${MATCHED_PATHS[@]}" | awk 'NF' | sort -u)"
    FOUND="yes"
    PATHS_JOINED=$(printf "%s" "${MATCHED_PATHS[0]}")
    for ((i=1; i<${#MATCHED_PATHS[@]}; i++)); do
      PATHS_JOINED="${PATHS_JOINED} | ${MATCHED_PATHS[$i]}"
    done
  else
    FOUND="no"
    PATHS_JOINED=""
  fi

  # Write CSV row
  echo "$(csv_escape "$NAME"),$(csv_escape "$FOUND"),$(csv_escape "$PATHS_JOINED")" >> "$OUT_CSV"
  printf "• Searched: %-35s -> %s\n" "$NAME" "$FOUND"
done

echo
echo "✅ Done. Results saved to: $OUT_CSV"
echo "Tip: open -a Numbers \"$OUT_CSV\"   # or Excel"
