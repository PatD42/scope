#!/bin/bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 docs/epics/{epic-dir}" >&2
    exit 1
fi

EPIC_DIR="${1%/}"
[[ -d "$EPIC_DIR" ]] || {
    echo "Epic directory not found: $EPIC_DIR" >&2
    exit 1
}

fail() {
    echo "Validation failed: $1" >&2
    exit 1
}

find "$EPIC_DIR" -name ".DS_Store" -delete

for forbidden_name in __pycache__; do
    found="$(find "$EPIC_DIR" -name "$forbidden_name" -print -quit)"
    [[ -z "$found" ]] || fail "forbidden artifact in epic folder: $found"
done

for forbidden_pattern in '*.py' '*.pyc'; do
    found="$(find "$EPIC_DIR" -type f -name "$forbidden_pattern" -print -quit)"
    [[ -z "$found" ]] || fail "forbidden source/cache artifact in epic folder: $found"
done

found="$(
    find "$EPIC_DIR" -mindepth 1 -type f \
        ! \( -name '*.md' -o -name '*.yaml' -o -name '.DS_Store' \) \
        -print -quit
)"
[[ -z "$found" ]] || fail "epic folder may contain only .md and .yaml files: $found"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR="${SCRIPT_DIR}/validate-refinement.py"
POLICY="${SCRIPT_DIR}/../config/refinement-policy.yaml"

if [[ -n "${SCOPE_PYTHON:-}" ]]; then
    PYTHON_CMD="$SCOPE_PYTHON"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    fail "Scope v3 requires Python 3; install Python or set SCOPE_PYTHON"
fi

[[ -f "$VALIDATOR" ]] || fail "missing validator: $VALIDATOR"
[[ -f "$POLICY" ]] || fail "missing policy: $POLICY"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT="$(git rev-parse --show-toplevel)"
else
    REPO_ROOT="$(cd "$(dirname "$EPIC_DIR")/../.." && pwd)"
fi

"$PYTHON_CMD" "$VALIDATOR" validate "$EPIC_DIR" \
    --phase handoff \
    --policy "$POLICY" \
    --repo-root "$REPO_ROOT"

echo "Epic documentation validation passed: ${EPIC_DIR}"
