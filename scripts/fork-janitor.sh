#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI ('gh') is required but not installed." >&2
  exit 1
fi

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "Error: GH_TOKEN is not set. Export GH_TOKEN with a PAT before running." >&2
  exit 1
fi

OWNER="${OWNER:-}"
if [[ -z "$OWNER" ]]; then
  OWNER="$(gh api user --jq .login 2>/dev/null || true)"
fi

if [[ -z "$OWNER" ]]; then
  echo "Error: Could not determine repository owner. Set OWNER explicitly." >&2
  exit 1
fi

EXECUTE_VALUE="${EXECUTE:-0}"
SHOULD_EXECUTE=0
if [[ "$EXECUTE_VALUE" == "1" || "$EXECUTE_VALUE" == "true" ]]; then
  SHOULD_EXECUTE=1
fi

if ! mapfile -t FORKS < <(gh repo list "$OWNER" --limit 1000 --fork --json nameWithOwner,name,isFork --jq '.[] | select(.isFork == true) | .nameWithOwner'); then
  echo "Error: Failed to list fork repositories for owner '$OWNER'." >&2
  exit 1
fi

TOTAL="${#FORKS[@]}"
DISABLED=0
SKIPPED=0
ERRORS=0

for FORK in "${FORKS[@]}"; do
  if [[ "$SHOULD_EXECUTE" -eq 1 ]]; then
    echo "[EXECUTE] Disabling Actions on ${FORK}"
    if gh api -X PUT "repos/${FORK}/actions/permissions" -f enabled=false >/dev/null; then
      DISABLED=$((DISABLED + 1))
    else
      echo "[ERROR] Failed to disable Actions on ${FORK}" >&2
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo "[DRY-RUN] Would disable Actions on ${FORK}"
    SKIPPED=$((SKIPPED + 1))
  fi
done

if [[ "$SHOULD_EXECUTE" -eq 1 ]]; then
  SKIPPED=$((TOTAL - DISABLED - ERRORS))
fi

echo "Total forks: ${TOTAL} | Disabled: ${DISABLED} | Skipped: ${SKIPPED} | Errors: ${ERRORS}"
