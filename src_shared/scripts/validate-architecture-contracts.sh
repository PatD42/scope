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

python3 - "$EPIC_DIR" <<'PY'
from pathlib import Path
import sys

try:
    import yaml
except Exception as exc:
    raise SystemExit(f"PyYAML is required to validate architecture contracts: {exc}")

epic_dir = Path(sys.argv[1])
claims_path = epic_dir / "architecture-claims.yaml"
self_check_path = epic_dir / "architecture-contract-self-check.yaml"


def fail(message: str) -> None:
    raise SystemExit(f"Architecture contract validation failed: {message}")


def load_yaml(path: Path):
    if not path.exists():
        fail(f"missing required file: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path} does not parse as YAML: {exc}")
    if not isinstance(data, dict):
        fail(f"{path} must contain a YAML mapping")
    return data


def require_mapping(data, key: str, path: Path):
    value = data.get(key)
    if not isinstance(value, dict):
        fail(f"{path} missing mapping field: {key}")
    return value


def require_list(data, key: str, path: Path):
    value = data.get(key)
    if not isinstance(value, list) or not value:
        fail(f"{path} missing non-empty list field: {key}")
    return value


def reject_open_status(items, path: Path, context: str) -> None:
    for item in items:
        if not isinstance(item, dict):
            fail(f"{path} {context} contains a non-mapping item")
        item_id = item.get("id", "<missing id>")
        status = str(item.get("status", "")).strip().lower()
        if status in {"fail", "failed", "user_question", "open", "blocked"}:
            fail(f"{path} {context} item {item_id} has unresolved status: {status}")


claims_doc = load_yaml(claims_path)
self_check = load_yaml(self_check_path)

claims = require_list(claims_doc, "claims", claims_path)
reject_open_status(claims, claims_path, "claims")

claim_ids = set()
for claim in claims:
    claim_id = claim.get("id")
    if not claim_id:
        fail(f"{claims_path} has a claim without id")
    if claim_id in claim_ids:
        fail(f"{claims_path} has duplicate claim id: {claim_id}")
    claim_ids.add(claim_id)
    for field in ("source", "claim", "owner_phase", "enforcement_expected"):
        if field not in claim or claim.get(field) in (None, "", []):
            fail(f"{claims_path} claim {claim_id} missing {field}")

if str(self_check.get("status", "")).strip().lower() in {"fail", "failed", "user_question", "open", "blocked"}:
    fail(f"{self_check_path} has unresolved status: {self_check.get('status')}")

inventory = require_mapping(self_check, "contract_inventory", self_check_path)
for key in (
    "architecture_entities",
    "api_operations",
    "generated_schemas",
    "generated_reports_or_artifacts",
    "commands_or_scripts",
    "persistence_surfaces",
    "error_codes",
):
    if key not in inventory or not isinstance(inventory[key], list):
        fail(f"{self_check_path} contract_inventory missing list field: {key}")

compatibility = require_list(self_check, "producer_consumer_compatibility", self_check_path)
reject_open_status(compatibility, self_check_path, "producer_consumer_compatibility")
for item in compatibility:
    item_id = item.get("id", "<missing id>")
    for field in ("producer", "consumer", "required_output", "producer_can_create_required_fields", "status"):
        if field not in item or item.get(field) in (None, "", []):
            fail(f"{self_check_path} producer_consumer_compatibility {item_id} missing {field}")
    can_create = str(item.get("producer_can_create_required_fields", "")).strip().lower()
    if can_create not in {"yes", "not_applicable"}:
        fail(f"{self_check_path} producer_consumer_compatibility {item_id} producer_can_create_required_fields is {can_create}")

patterns = require_list(self_check, "cross_surface_patterns", self_check_path)
reject_open_status(patterns, self_check_path, "cross_surface_patterns")
for pattern in patterns:
    pattern_name = pattern.get("pattern", "<missing pattern>")
    if not pattern.get("surfaces_checked"):
        fail(f"{self_check_path} cross_surface_patterns {pattern_name} has no surfaces_checked")
    if pattern.get("missing_surfaces"):
        fail(f"{self_check_path} cross_surface_patterns {pattern_name} has missing_surfaces: {pattern.get('missing_surfaces')}")

self_claims = require_list(self_check, "claims", self_check_path)
reject_open_status(self_claims, self_check_path, "claims")
self_claim_ids = set()
for claim in self_claims:
    claim_id = claim.get("id")
    if not claim_id:
        fail(f"{self_check_path} has a claim without id")
    if claim_id in self_claim_ids:
        fail(f"{self_check_path} has duplicate claim id: {claim_id}")
    self_claim_ids.add(claim_id)
    for field in ("source", "claim", "contract_surfaces", "enforcement", "status"):
        if field not in claim or claim.get(field) in (None, "", []):
            fail(f"{self_check_path} claim {claim_id} missing {field}")
    enforcement = claim.get("enforcement")
    if not isinstance(enforcement, dict):
        fail(f"{self_check_path} claim {claim_id} enforcement must be a mapping")
    for field in ("type", "mechanism", "negative_case"):
        if enforcement.get(field) in (None, "", []):
            fail(f"{self_check_path} claim {claim_id} enforcement missing {field}")

missing_from_self_check = sorted(claim_ids - self_claim_ids)
if missing_from_self_check:
    fail(f"{self_check_path} missing claims from architecture-claims.yaml: {', '.join(missing_from_self_check)}")

print(f"Architecture contract validation passed: {epic_dir}")
PY
