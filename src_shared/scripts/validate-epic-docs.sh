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
    "acceptance-traceability.yaml"
    "architecture-readiness-matrix.yaml"
    "system-context.md"
    "architecture.md"
    "adr.md"
    "pdr.md"
    "test-strategy.md"
    "refinement-inconsistencies.yaml"
    "architecture-claims.yaml"
    "architecture-contract-self-check.yaml"
)

IGNORED_NAMES=(
    ".DS_Store"
)

FORBIDDEN_NAMES=(
    "__pycache__"
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

validate_details_intent_alignment() {
    local details_file="$1"

    rg -F -q "## Intent Alignment" "$details_file" || fail "details.md missing ## Intent Alignment section"
    rg -i -q "Open intent questions.*None" "$details_file" || fail "details.md Intent Alignment must state Open intent questions: None"
}

validate_folder_hygiene() {
    local path

    for name in "${IGNORED_NAMES[@]}"; do
        find "$EPIC_DIR" -name "$name" -delete
    done

    for name in "${FORBIDDEN_NAMES[@]}"; do
        path="$(find "$EPIC_DIR" -name "$name" -print -quit)"
        [[ -z "$path" ]] || fail "forbidden artifact in epic folder: ${path}"
    done

    for pattern in "${FORBIDDEN_EXTENSIONS[@]}"; do
        path="$(find "$EPIC_DIR" -type f -name "$pattern" -print -quit)"
        [[ -z "$path" ]] || fail "forbidden source/cache artifact in epic folder: ${path}"
    done

    path="$(find "$EPIC_DIR" -mindepth 1 -type f ! \( -name "*.md" -o -name "*.yaml" -o -name ".DS_Store" \) -print -quit)"
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

validate_acceptance_traceability() {
    local traceability_file="$1"

    rg -F -q "acceptance_items:" "$traceability_file" || fail "acceptance-traceability.yaml missing acceptance_items"
    rg -F -q "required_assertions:" "$traceability_file" || fail "acceptance-traceability.yaml missing required_assertions"
    rg -F -q "runtime_evidence:" "$traceability_file" || fail "acceptance-traceability.yaml missing runtime_evidence"
}

validate_architecture_readiness_matrix() {
    local matrix_file="$1"

    rg -F -q "rows:" "$matrix_file" || fail "architecture-readiness-matrix.yaml missing rows"
    rg -F -q "requires:" "$matrix_file" || fail "architecture-readiness-matrix.yaml missing requires"
    rg -F -q "evidence:" "$matrix_file" || fail "architecture-readiness-matrix.yaml missing evidence"
    rg -F -q "blocker_when_missing:" "$matrix_file" || fail "architecture-readiness-matrix.yaml missing blocker_when_missing"
    rg -F -q "status:" "$matrix_file" || fail "architecture-readiness-matrix.yaml missing status"

    python3 - "$matrix_file" <<'PY' || fail "architecture-readiness-matrix.yaml has rows requiring implementation-boundary ownership with empty evidence.implementation_boundary_owner"
from pathlib import Path
import re
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
rows = re.split(r"(?m)^\s*-\s+id:\s*", text)
for row in rows[1:]:
    requires_owner = re.search(r"(?m)^\s*implementation_boundary_owner:\s*true\s*$", row)
    empty_owner = re.search(r"(?m)^\s*implementation_boundary_owner:\s*\[\]\s*$", row)
    if requires_owner and empty_owner:
        raise SystemExit(1)
PY
}

validate_implementation_boundary_plans() {
    local plan_file

    for plan_file in "${EPIC_DIR}"/file-plan-story-*.yaml; do
        [[ -f "$plan_file" ]] || continue
        rg -F -q "epic_id:" "$plan_file" || fail "${plan_file} missing epic_id"
        rg -F -q "story_id:" "$plan_file" || fail "${plan_file} missing story_id"
        rg -F -q "story_title:" "$plan_file" || fail "${plan_file} missing story_title"
        rg -F -q "required_contracts:" "$plan_file" || fail "${plan_file} missing required_contracts"
        rg -F -q "required_touchpoints:" "$plan_file" || fail "${plan_file} missing required_touchpoints"
        rg -F -q "candidate_files:" "$plan_file" || fail "${plan_file} missing candidate_files"
        rg -F -q "forbidden_changes:" "$plan_file" || fail "${plan_file} missing forbidden_changes"
        rg -F -q "proof_obligations:" "$plan_file" || fail "${plan_file} missing proof_obligations"
        if rg -q "files_to_create:|files_to_modify:" "$plan_file"; then
            fail "${plan_file} uses removed legacy files_to_create/files_to_modify schema"
        fi
    done
}

validate_refinement_inconsistencies() {
    local inconsistencies_file="$1"

    rg -F -q "epic_id:" "$inconsistencies_file" || fail "refinement-inconsistencies.yaml missing epic_id"
    rg -F -q "items:" "$inconsistencies_file" || fail "refinement-inconsistencies.yaml missing items"

    if rg -q 'status:[[:space:]]*"?open"?([[:space:]]*$|[[:space:]]+#)|status:[[:space:]]*"?user_question"?([[:space:]]*$|[[:space:]]+#)' "$inconsistencies_file"; then
        fail "refinement-inconsistencies.yaml contains open or user_question items"
    fi
}

for file_name in "${REQUIRED_FILES[@]}"; do
    require_file "${EPIC_DIR}/${file_name}"
done

compgen -G "${EPIC_DIR}/file-plan-story-*.yaml" > /dev/null || fail "missing file-plan-story-*.yaml"

validate_folder_hygiene
validate_details_frontmatter "${EPIC_DIR}/details.md"
validate_details_intent_alignment "${EPIC_DIR}/details.md"
validate_adr "${EPIC_DIR}/adr.md"
validate_acceptance_traceability "${EPIC_DIR}/acceptance-traceability.yaml"
validate_architecture_readiness_matrix "${EPIC_DIR}/architecture-readiness-matrix.yaml"
validate_implementation_boundary_plans
validate_refinement_inconsistencies "${EPIC_DIR}/refinement-inconsistencies.yaml"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/validate-architecture-contracts.sh" "$EPIC_DIR"

echo "Epic documentation validation passed: ${EPIC_DIR}"
