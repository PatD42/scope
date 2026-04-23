#!/bin/bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 docs/epics/{epic-dir}" >&2
    exit 1
fi

EPIC_DIR="${1%/}"

if [[ ! -d "$EPIC_DIR" ]]; then
    echo "Epic directory not found: $EPIC_DIR" >&2
    exit 1
fi

REQUIRED_FILES=(
    "details.md"
    "acceptance-criteria.md"
    "system-context.md"
    "architecture.md"
    "adr.md"
    "pdr.md"
    "test-strategy.md"
)

FORBIDDEN_NAMES=(
    "__pycache__"
    ".DS_Store"
)

FORBIDDEN_EXTENSIONS=(
    "*.py"
    "*.pyc"
)

fail() {
    echo "Validation failed: $1" >&2
    exit 1
}

require_file() {
    local path="$1"
    [[ -f "$path" ]] || fail "missing required file: ${path}"
}

validate_details_frontmatter() {
    local details_file="$1"
    local frontmatter_end

    [[ "$(head -n 1 "$details_file")" == "---" ]] || fail "details.md must start with YAML frontmatter"

    frontmatter_end="$(awk 'NR>1 && $0=="---" { print NR; exit }' "$details_file")"
    [[ -n "$frontmatter_end" ]] || fail "details.md frontmatter is not closed"

    local frontmatter
    frontmatter="$(sed -n "2,$((frontmatter_end - 1))p" "$details_file")"

    [[ "$frontmatter" =~ (^|[[:space:]])epic_id: ]] || fail "details.md frontmatter missing epic_id"
    [[ "$frontmatter" =~ (^|[[:space:]])title: ]] || fail "details.md frontmatter missing title"
    [[ "$frontmatter" =~ (^|[[:space:]])status: ]] || fail "details.md frontmatter missing status"
}

validate_folder_hygiene() {
    local path

    for name in "${FORBIDDEN_NAMES[@]}"; do
        path="$(find "$EPIC_DIR" -name "$name" -print -quit)"
        [[ -z "$path" ]] || fail "forbidden artifact in epic folder: ${path}"
    done

    for pattern in "${FORBIDDEN_EXTENSIONS[@]}"; do
        path="$(find "$EPIC_DIR" -type f -name "$pattern" -print -quit)"
        [[ -z "$path" ]] || fail "forbidden source/cache artifact in epic folder: ${path}"
    done

    path="$(find "$EPIC_DIR" -mindepth 1 \( -type f ! \( -name "*.md" -o -name "*.yaml" \) -o -type d \) -print -quit)"
    [[ -z "$path" ]] || fail "epic folder may contain only .md and .yaml files: ${path}"
}

collect_repo_adr_numbers() {
    local repo_root="$1"
    local adr_numbers

    adr_numbers="$(
        {
            if [[ -d "$repo_root/docs/epics" ]]; then
                rg -h -o 'ADR-[0-9]{3}' "$repo_root/docs/epics" -g 'adr.md' || true
            fi
            if [[ -d "$repo_root/docs/architecture" ]]; then
                rg -h -o 'ADR-[0-9]{3}' "$repo_root/docs/architecture" -g 'ADR-*.md' || true
            fi
        }
    )"

    printf '%s\n' "$adr_numbers"
}

validate_adr() {
    local adr_file="$1"
    local repo_root
    local adr_numbers
    local duplicate_numbers

    repo_root="$(cd "$(dirname "$EPIC_DIR")/../.." && pwd)"

    rg -q '^## ADR-[0-9]{3}: ' "$adr_file" || fail "adr.md must contain at least one ADR heading using ADR-NNN"

    for field in '**Date**:' '**Status**:' '**Scope**:' '**Epic**:'; do
        rg -F -q "$field" "$adr_file" || fail "adr.md missing required field ${field}"
    done

    for section in '### Context' '### Decision' '### Alternatives Considered' '### Consequences'; do
        rg -F -q "$section" "$adr_file" || fail "adr.md missing required section ${section}"
    done

    adr_numbers="$(rg -o 'ADR-[0-9]{3}' "$adr_file" | sort)"
    [[ -n "$adr_numbers" ]] || fail "adr.md must use ADR-NNN identifiers"

    duplicate_numbers="$(printf '%s\n' "$adr_numbers" | uniq -d)"
    [[ -z "$duplicate_numbers" ]] || fail "adr.md contains duplicate ADR numbers: ${duplicate_numbers}"

    local repo_adr_numbers
    repo_adr_numbers="$(collect_repo_adr_numbers "$repo_root")"

    while IFS= read -r adr_number; do
        [[ -n "$adr_number" ]] || continue
        if [[ "$(printf '%s\n' "$repo_adr_numbers" | grep -c "^${adr_number}$")" -gt 1 ]]; then
            fail "ADR number ${adr_number} is duplicated elsewhere in the repository"
        fi
    done <<< "$adr_numbers"
}

for file_name in "${REQUIRED_FILES[@]}"; do
    require_file "${EPIC_DIR}/${file_name}"
done

compgen -G "${EPIC_DIR}/file-plan-story-*.yaml" > /dev/null || fail "missing file-plan-story-*.yaml"

validate_folder_hygiene
validate_details_frontmatter "${EPIC_DIR}/details.md"
validate_adr "${EPIC_DIR}/adr.md"

echo "Epic documentation validation passed: ${EPIC_DIR}"
