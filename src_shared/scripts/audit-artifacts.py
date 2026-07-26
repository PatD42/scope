#!/usr/bin/env python3
"""Prepare and validate Scope Audit Epic artifacts from a v3 refinement handoff."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml


VALIDATION_PHASES = ("pre_review", "complete")


class DuplicateKeyError(ValueError):
    """Raised when YAML contains a duplicate mapping key."""


class UniqueKeyLoader(yaml.SafeLoader):
    """PyYAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateKeyError(
                f"duplicate key {key!r} at line {key_node.start_mark.line + 1}"
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, yaml.YAMLError, DuplicateKeyError, TypeError) as exc:
        raise ValueError(f"invalid {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain a YAML mapping: {path}")
    return value


def _write_yaml(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(dict(value), sort_keys=False), encoding="utf-8")


def _default_policy_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config" / "audit-policy.yaml"


def _infer_repo_root(epic_dir: Path) -> Path:
    resolved = epic_dir.resolve()
    if resolved.parent.name == "epics" and resolved.parent.parent.name == "docs":
        return resolved.parents[2]
    return Path.cwd().resolve()


def _run_git(repo_root: Path, *args: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _changed_files(repo_root: Path) -> list[str]:
    if not _run_git(repo_root, "rev-parse", "--is-inside-work-tree"):
        return []

    refs: list[str] = []
    origin_head = _run_git(repo_root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if origin_head:
        refs.append(origin_head[0])
    refs.extend(("origin/main", "main", "origin/master", "master", "origin/trunk", "trunk"))

    base = ""
    for ref in refs:
        if not _run_git(repo_root, "rev-parse", "--verify", "--quiet", ref):
            continue
        merge_base = _run_git(repo_root, "merge-base", "HEAD", ref)
        if merge_base:
            base = merge_base[0]
            break

    paths: set[str] = set()
    if base:
        paths.update(_run_git(repo_root, "diff", "--name-only", f"{base}...HEAD"))
    paths.update(_run_git(repo_root, "diff", "--name-only"))
    paths.update(_run_git(repo_root, "diff", "--cached", "--name-only"))
    paths.update(_run_git(repo_root, "ls-files", "--others", "--exclude-standard"))
    return sorted(path for path in paths if (repo_root / path).exists())


def _next_attempt_dir(epic_dir: Path) -> tuple[str, Path]:
    reviews = epic_dir / "reviews"
    numbers: list[int] = []
    for path in reviews.glob("audit-[0-9][0-9][0-9]"):
        match = re.fullmatch(r"audit-(\d{3})", path.name)
        if match:
            numbers.append(int(match.group(1)))
    attempt_id = f"audit-{(max(numbers, default=0) + 1):03d}"
    return attempt_id, reviews / attempt_id


def _profile(epic_dir: Path) -> dict[str, Any]:
    path = epic_dir / "refinement-profile.yaml"
    profile = _load_yaml(path, "refinement profile")
    if profile.get("schema_version") != 3:
        raise ValueError(f"refinement profile must use schema_version 3: {path}")
    return profile


def _traceability(epic_dir: Path) -> dict[str, Any]:
    path = epic_dir / "acceptance-traceability.yaml"
    traceability = _load_yaml(path, "acceptance traceability")
    if traceability.get("schema_version") != 3:
        raise ValueError(f"acceptance traceability must use schema_version 3: {path}")
    return traceability


def _manifest(epic_dir: Path) -> dict[str, Any]:
    path = epic_dir / "refinement-manifest.yaml"
    manifest = _load_yaml(path, "refinement manifest")
    if manifest.get("schema_version") != 3:
        raise ValueError(f"refinement manifest must use schema_version 3: {path}")
    return manifest


def _epic_id(
    profile: Mapping[str, Any],
    traceability: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> str:
    values = [
        value
        for value in (
            profile.get("epic_id"),
            traceability.get("epic_id"),
            manifest.get("epic_id"),
        )
        if isinstance(value, str) and value.strip()
    ]
    if not values:
        raise ValueError("cannot determine epic_id from profile, traceability, or manifest")
    if len(set(values)) != 1:
        raise ValueError(f"epic_id mismatch across audit inputs: {values}")
    return values[0]


def _risk_and_capabilities(profile: Mapping[str, Any]) -> tuple[str, list[str]]:
    risk = profile.get("risk_level")
    if not isinstance(risk, str) or risk not in {"low", "medium", "high", "critical"}:
        raise ValueError("refinement profile has invalid risk_level")
    capabilities = profile.get("capabilities", [])
    if not isinstance(capabilities, list):
        raise ValueError("refinement profile capabilities must be a list")
    if not all(isinstance(item, str) and item for item in capabilities):
        raise ValueError("refinement profile capabilities must contain non-empty strings")
    return risk, sorted({item for item in capabilities if isinstance(item, str) and item})


def _required_roles(policy: Mapping[str, Any], risk: str) -> list[str]:
    risk_policy = policy.get("risk_review_policy", {})
    if not isinstance(risk_policy, dict):
        raise ValueError("audit policy risk_review_policy must be a mapping")
    selected = risk_policy.get(risk)
    if not isinstance(selected, dict) or not isinstance(selected.get("roles"), list):
        raise ValueError(f"audit policy has no roles for risk {risk}")
    roles = selected["roles"]
    if not all(isinstance(role, str) and role for role in roles):
        raise ValueError(f"audit policy roles for {risk} must be non-empty strings")
    return list(roles)


def _requirements_by_id(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    requirements = manifest.get("requirements", [])
    if not isinstance(requirements, list):
        return {}
    return {
        str(row["id"]): row
        for row in requirements
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _derive_matrix(
    epic_dir: Path,
    attempt_id: str,
    epic_id: str,
    risk: str,
    traceability: Mapping[str, Any],
    manifest: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    items = traceability.get("acceptance_items")
    if not isinstance(items, list) or not items:
        raise ValueError("acceptance traceability must contain a non-empty acceptance_items list")
    requirements = _requirements_by_id(manifest)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"acceptance_items[{index}] must be a mapping")
        row_id = item.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise ValueError(f"acceptance_items[{index}] id must be a non-empty string")
        if row_id in seen:
            raise ValueError(f"duplicate acceptance item id: {row_id}")
        seen.add(row_id)

        implementation = _mapping(item.get("implementation"))
        tests = _mapping(item.get("tests"))
        runtime = _mapping(item.get("runtime_evidence"))
        runtime_required = runtime.get("required") is True
        requirement = requirements.get(row_id, {})
        row_risk = requirement.get("risk", risk)
        if row_risk not in {"low", "medium", "high", "critical"}:
            row_risk = risk
        priority = "runtime_required" if runtime_required else "required"
        if requirement.get("implementation_required") is False:
            priority = "documentation"

        rows.append(
            {
                "id": row_id,
                "story": str(item.get("story", "")),
                "requirement": str(requirement.get("summary", "")),
                "source": requirement.get("source", {}),
                "priority": priority,
                "risk_level": row_risk,
                "implementation": {
                    "expected_files": [],
                    "actual_files": _string_list(implementation.get("actual_files")),
                },
                "tests": {
                    "expected_files": [],
                    "required_assertions": _string_list(
                        requirement.get("proof_obligations")
                    ),
                    "actual_tests": _string_list(tests.get("actual_tests")),
                },
                "runtime_evidence": {
                    "required": runtime_required,
                    "commands": _string_list(runtime.get("commands")),
                    "evidence": _string_list(runtime.get("evidence")),
                },
                "status": "pending",
                "finding_ids": [],
                "audit_notes": "",
            }
        )

    return {
        "schema_version": policy.get("matrix_version"),
        "epic_id": epic_id,
        "attempt_id": attempt_id,
        "source_traceability": str(
            (epic_dir / "acceptance-traceability.yaml").relative_to(epic_dir.parents[2])
        ),
        "rows": rows,
    }


def _boundary_gates(epic_dir: Path, scoped_rows: set[str]) -> list[dict[str, Any]]:
    commands: list[tuple[str, str]] = []
    for path in sorted(epic_dir.glob("file-plan-story-*.yaml")):
        plan = _load_yaml(path, "implementation boundary plan")
        proofs = plan.get("proof_obligations", [])
        if not isinstance(proofs, list):
            continue
        for proof in proofs:
            if not isinstance(proof, dict):
                continue
            acceptance_rows = set(_string_list(proof.get("acceptance_rows")))
            if acceptance_rows and not acceptance_rows.intersection(scoped_rows):
                continue
            command = proof.get("command_hint")
            if isinstance(command, str) and command.strip():
                commands.append((str(proof.get("id", "boundary-proof")), command.strip()))

    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_id, command in commands:
        if command in seen:
            continue
        seen.add(command)
        unique.append(
            {
                "id": f"gate-{len(unique) + 1:03d}",
                "source": source_id,
                "command": command,
                "status": "pending",
                "evidence": [],
                "reason": "",
            }
        )
    return unique


def _existing_v2_attempts(epic_dir: Path, cycle_id: str, mode: str) -> int:
    count = 0
    for path in (epic_dir / "reviews").glob("audit-*/audit-attempt.yaml"):
        try:
            attempt = _load_yaml(path, "audit attempt")
        except ValueError:
            continue
        if (
            attempt.get("schema_version") == 2
            and attempt.get("cycle_id") == cycle_id
            and attempt.get("mode") == mode
        ):
            count += 1
    return count


def _load_findings(epic_dir: Path, epic_id: str, policy: Mapping[str, Any]) -> dict[str, Any]:
    path = epic_dir / "audit-findings.yaml"
    if not path.is_file():
        return {
            "schema_version": policy.get("findings_version"),
            "epic_id": epic_id,
            "findings": [],
        }
    return _load_yaml(path, "audit findings")


def prepare(args: argparse.Namespace) -> int:
    epic_dir = args.epic_dir.resolve()
    repo_root = (args.repo_root or _infer_repo_root(epic_dir)).resolve()
    policy = _load_yaml(args.policy.resolve(), "audit policy")
    profile = _profile(epic_dir)
    traceability = _traceability(epic_dir)
    manifest = _manifest(epic_dir)
    epic_id = _epic_id(profile, traceability, manifest)
    risk, capabilities = _risk_and_capabilities(profile)
    roles = _required_roles(policy, risk)

    allowed_modes = policy.get("allowed_modes", [])
    if args.mode not in allowed_modes:
        raise ValueError(f"unsupported audit mode {args.mode!r}")
    budget = policy.get("review_budget", {})
    budget_field = "maximum_full_attempts" if args.mode == "full" else "maximum_targeted_attempts"
    maximum = budget.get(budget_field) if isinstance(budget, dict) else None
    existing = _existing_v2_attempts(epic_dir, args.cycle_id, args.mode)
    if isinstance(maximum, int) and existing >= maximum and not args.allow_extra:
        raise ValueError(
            f"audit cycle {args.cycle_id!r} already has {existing} {args.mode} attempt(s); "
            "explicit --allow-extra and --reason are required"
        )
    if args.allow_extra and not args.reason:
        raise ValueError("--allow-extra requires --reason")

    findings = _load_findings(epic_dir, epic_id, policy)
    finding_rows = findings.get("findings", [])
    if not isinstance(finding_rows, list):
        raise ValueError("audit findings must contain a findings list")
    findings_by_id = {
        row.get("id"): row
        for row in finding_rows
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }

    attempt_id, attempt_dir = _next_attempt_dir(epic_dir)
    matrix = _derive_matrix(
        epic_dir,
        attempt_id,
        epic_id,
        risk,
        traceability,
        manifest,
        policy,
    )
    all_rows = [row["id"] for row in matrix["rows"]]
    if args.mode == "full":
        scoped_rows = all_rows
        finding_ids: list[str] = []
    else:
        finding_ids = list(dict.fromkeys(args.finding))
        if not finding_ids:
            raise ValueError("targeted preparation requires at least one --finding")
        missing = sorted(set(finding_ids) - set(findings_by_id))
        if missing:
            raise ValueError(f"unknown targeted findings: {', '.join(missing)}")
        not_ready = sorted(
            finding_id
            for finding_id in finding_ids
            if findings_by_id[finding_id].get("status")
            != "remediated_pending_verification"
        )
        if not_ready:
            raise ValueError(
                "targeted findings are not ready for verification: "
                + ", ".join(not_ready)
            )
        scoped: set[str] = set()
        for finding_id in finding_ids:
            scoped.update(_string_list(findings_by_id[finding_id].get("affected_acceptance_ids")))
        scoped_rows = [row_id for row_id in all_rows if row_id in scoped]
        if not scoped_rows:
            raise ValueError("targeted findings do not reference any current acceptance rows")

    attempt = {
        "schema_version": policy.get("attempt_version"),
        "epic_id": epic_id,
        "attempt_id": attempt_id,
        "cycle_id": args.cycle_id,
        "mode": args.mode,
        "reason": args.reason or ("complete implementation audit" if args.mode == "full" else "finding verification"),
        "risk_level": risk,
        "capabilities": capabilities,
        "specialist_focus": capabilities if "capability_specialist" in roles else [],
        "scope": {
            "acceptance_rows": scoped_rows,
            "finding_ids": finding_ids,
            "sibling_surfaces": list(dict.fromkeys(args.sibling_surface)),
        },
        "changed_files": _changed_files(repo_root),
        "gates": _boundary_gates(epic_dir, set(scoped_rows)),
        "review": {
            "required_roles": roles,
            "outputs": [],
            "skipped_reason": "",
        },
        "status": "pending",
        "decision_reason": "",
    }

    attempt_dir.mkdir(parents=True, exist_ok=False)
    _write_yaml(attempt_dir / "audit-attempt.yaml", attempt)
    _write_yaml(attempt_dir / "audit-verification-matrix.yaml", matrix)
    if not (epic_dir / "audit-findings.yaml").is_file():
        _write_yaml(epic_dir / "audit-findings.yaml", findings)
    print(attempt_dir.relative_to(repo_root))
    return 0


class AuditValidator:
    """Validate one prepared Audit Epic v2 attempt."""

    def __init__(
        self,
        epic_dir: Path,
        attempt_dir: Path,
        phase: str,
        policy_path: Path,
        repo_root: Path | None = None,
    ) -> None:
        self.epic_dir = epic_dir.resolve()
        self.attempt_dir = attempt_dir.resolve()
        self.phase = phase
        self.policy_path = policy_path.resolve()
        self.repo_root = (repo_root or _infer_repo_root(self.epic_dir)).resolve()
        self.errors: list[str] = []
        self.policy: dict[str, Any] = {}
        self.attempt: dict[str, Any] = {}
        self.matrix: dict[str, Any] = {}
        self.findings: dict[str, Any] = {}
        self.row_ids: set[str] = set()
        self.scoped_rows: set[str] = set()

    def validate(self) -> list[str]:
        if self.phase not in VALIDATION_PHASES:
            return [f"unsupported validation phase: {self.phase}"]
        for path, label in (
            (self.epic_dir, "epic directory"),
            (self.attempt_dir, "audit attempt directory"),
        ):
            if not path.is_dir():
                return [f"{label} does not exist: {path}"]
        try:
            self.policy = _load_yaml(self.policy_path, "audit policy")
            self.attempt = _load_yaml(self.attempt_dir / "audit-attempt.yaml", "audit attempt")
            self.matrix = _load_yaml(
                self.attempt_dir / "audit-verification-matrix.yaml",
                "audit verification matrix",
            )
            self.findings = _load_yaml(self.epic_dir / "audit-findings.yaml", "audit findings")
        except ValueError as exc:
            return [str(exc)]

        self._validate_all_yaml()
        self._validate_attempt()
        self._validate_matrix()
        self._validate_matrix_derivation()
        self._validate_findings()
        self._validate_finding_links()
        self._validate_scope_and_gates()
        if self.phase == "complete":
            self._validate_reviews()
            self._validate_completion()
        return self.errors

    def _validate_all_yaml(self) -> None:
        for root in (self.epic_dir, self.attempt_dir):
            for path in sorted(root.glob("*.yaml")):
                try:
                    yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
                except (OSError, yaml.YAMLError, DuplicateKeyError, TypeError) as exc:
                    self.errors.append(f"invalid YAML {path}: {exc}")

    def _validate_attempt(self) -> None:
        path = self.attempt_dir / "audit-attempt.yaml"
        self._require_equal(self.attempt, "schema_version", self.policy.get("attempt_version"), path)
        self._require_string(self.attempt, "epic_id", path)
        attempt_id = self._require_string(self.attempt, "attempt_id", path)
        if attempt_id and attempt_id != self.attempt_dir.name:
            self.errors.append(f"{path} attempt_id does not match directory name")
        self._require_string(self.attempt, "cycle_id", path)
        self._require_allowed(self.attempt.get("mode"), self.policy.get("allowed_modes"), "mode", path)
        self._require_allowed(
            self.attempt.get("risk_level"),
            list(self.policy.get("risk_review_policy", {})),
            "risk_level",
            path,
        )
        self._require_string(self.attempt, "reason", path)
        self._require_allowed(
            self.attempt.get("status"), self.policy.get("attempt_statuses"), "status", path
        )
        for field in ("capabilities", "specialist_focus", "changed_files"):
            self._require_string_list(self.attempt.get(field), field, path)
        self._require_string(self.attempt, "decision_reason", path, allow_empty=True)

    def _validate_matrix(self) -> None:
        path = self.attempt_dir / "audit-verification-matrix.yaml"
        self._require_equal(self.matrix, "schema_version", self.policy.get("matrix_version"), path)
        for field in ("epic_id", "attempt_id"):
            actual = self._require_string(self.matrix, field, path)
            expected = self.attempt.get(field)
            if actual and expected and actual != expected:
                self.errors.append(f"{path} {field} {actual!r} does not match attempt {expected!r}")
        source = self._require_string(self.matrix, "source_traceability", path)
        if source and not self._resolve_path(source).is_file():
            self.errors.append(f"{path} source_traceability does not exist: {source}")
        rows = self.matrix.get("rows")
        if not isinstance(rows, list) or not rows:
            self.errors.append(f"{path} rows must be a non-empty list")
            return
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            context = f"{path} rows[{index}]"
            if not isinstance(row, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            row_id = self._require_string(row, "id", path, context=context)
            if row_id:
                ids.append(row_id)
            self._require_string(row, "story", path, context=context)
            self._require_string(row, "requirement", path, context=context)
            if not isinstance(row.get("source"), dict):
                self.errors.append(f"{context} source must be a mapping")
            self._require_allowed(
                row.get("priority"), self.policy.get("row_priorities"), "priority", path, context
            )
            self._require_allowed(
                row.get("risk_level"),
                list(self.policy.get("risk_review_policy", {})),
                "risk_level",
                path,
                context,
            )
            self._validate_evidence_mapping(row, "implementation", ("expected_files", "actual_files"), context)
            self._validate_evidence_mapping(
                row,
                "tests",
                ("expected_files", "required_assertions", "actual_tests"),
                context,
            )
            runtime = row.get("runtime_evidence")
            self._validate_evidence_mapping(
                row,
                "runtime_evidence",
                ("commands", "evidence"),
                context,
            )
            if isinstance(runtime, dict) and not isinstance(runtime.get("required"), bool):
                self.errors.append(f"{context} runtime_evidence.required must be boolean")
            self._require_allowed(
                row.get("status"), self.policy.get("row_statuses"), "status", path, context
            )
            self._require_string_list(row.get("finding_ids"), "finding_ids", path, context)
            self._require_string(row, "audit_notes", path, context=context, allow_empty=True)
        self._check_unique(ids, "matrix row ids", path)
        self.row_ids = set(ids)

    def _validate_evidence_mapping(
        self,
        row: Mapping[str, Any],
        field: str,
        list_fields: Sequence[str],
        context: str,
    ) -> None:
        value = row.get(field)
        if not isinstance(value, dict):
            self.errors.append(f"{context} {field} must be a mapping")
            return
        for list_field in list_fields:
            self._require_string_list(value.get(list_field), f"{field}.{list_field}", Path(), context)

    def _validate_matrix_derivation(self) -> None:
        try:
            expected = _derive_matrix(
                self.epic_dir,
                str(self.attempt.get("attempt_id", "")),
                str(self.attempt.get("epic_id", "")),
                str(self.attempt.get("risk_level", "medium")),
                _traceability(self.epic_dir),
                _manifest(self.epic_dir),
                self.policy,
            )
        except ValueError as exc:
            self.errors.append(f"cannot rederive audit matrix: {exc}")
            return

        actual_rows = self.matrix.get("rows", [])
        expected_rows = expected.get("rows", [])
        if not isinstance(actual_rows, list) or not isinstance(expected_rows, list):
            return
        immutable_fields = (
            "id",
            "story",
            "requirement",
            "source",
            "priority",
            "risk_level",
            "implementation",
            "tests",
            "runtime_evidence",
        )
        if len(actual_rows) != len(expected_rows):
            self.errors.append("audit matrix row count differs from acceptance traceability")
            return
        for index, (actual, derived) in enumerate(zip(actual_rows, expected_rows, strict=True), start=1):
            if not isinstance(actual, dict) or not isinstance(derived, dict):
                continue
            for field in immutable_fields:
                if actual.get(field) != derived.get(field):
                    self.errors.append(
                        f"audit matrix rows[{index}] {field} differs from derived traceability"
                    )

    def _validate_findings(self) -> None:
        path = self.epic_dir / "audit-findings.yaml"
        self._require_equal(
            self.findings, "schema_version", self.policy.get("findings_version"), path
        )
        finding_epic = self._require_string(self.findings, "epic_id", path)
        attempt_epic = self.attempt.get("epic_id")
        if finding_epic and attempt_epic and finding_epic != attempt_epic:
            self.errors.append(f"{path} epic_id does not match audit attempt")
        rows = self.findings.get("findings")
        if not isinstance(rows, list):
            self.errors.append(f"{path} findings must be a list")
            return
        finding_policy = self.policy.get("finding", {})
        allowed_fields = {
            "severity": "severities",
            "category": "categories",
            "disposition": "dispositions",
            "status": "statuses",
        }
        ids: list[str] = []
        fingerprints: list[str] = []
        for index, finding in enumerate(rows, start=1):
            context = f"{path} findings[{index}]"
            if not isinstance(finding, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            finding_id = self._require_string(finding, "id", path, context=context)
            fingerprint = self._require_string(finding, "fingerprint", path, context=context)
            if finding_id:
                ids.append(finding_id)
            if fingerprint:
                fingerprints.append(fingerprint)
            self._require_string(finding, "first_seen_attempt", path, context=context)
            for field in ("severity", "category", "disposition", "status"):
                allowed = (
                    finding_policy.get(allowed_fields[field], [])
                    if isinstance(finding_policy, dict)
                    else []
                )
                self._require_allowed(finding.get(field), allowed, field, path, context)
            for field in ("title", "impact", "owner", "closure_test"):
                self._require_string(finding, field, path, context=context)
            for field in (
                "evidence",
                "affected_acceptance_ids",
                "affected_files",
                "reviewer_roles",
            ):
                values = self._require_string_list(finding.get(field), field, path, context)
                if field == "affected_acceptance_ids":
                    unknown = sorted(set(values) - self.row_ids)
                    if unknown:
                        self.errors.append(
                            f"{context} references unknown acceptance rows: {', '.join(unknown)}"
                        )
            if not finding.get("evidence"):
                self.errors.append(f"{context} evidence must not be empty")
        self._check_unique(ids, "finding ids", path)
        self._check_unique(fingerprints, "finding fingerprints", path)

    def _validate_finding_links(self) -> None:
        findings = {
            finding.get("id"): finding
            for finding in self.findings.get("findings", [])
            if isinstance(finding, dict) and isinstance(finding.get("id"), str)
        }
        rows = {
            row.get("id"): row
            for row in self.matrix.get("rows", [])
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        for row_id, row in rows.items():
            row_findings = set(_string_list(row.get("finding_ids")))
            unknown = sorted(row_findings - set(findings))
            if unknown:
                self.errors.append(
                    f"matrix row {row_id} references unknown findings: {', '.join(unknown)}"
                )
            for finding_id in row_findings.intersection(findings):
                affected = set(
                    _string_list(findings[finding_id].get("affected_acceptance_ids"))
                )
                if row_id not in affected:
                    self.errors.append(
                        f"matrix row {row_id} links finding {finding_id} without reciprocal scope"
                    )
        for finding_id, finding in findings.items():
            for row_id in _string_list(finding.get("affected_acceptance_ids")):
                if row_id in rows and finding_id not in set(
                    _string_list(rows[row_id].get("finding_ids"))
                ):
                    self.errors.append(
                        f"finding {finding_id} is missing from matrix row {row_id}"
                    )

    def _validate_scope_and_gates(self) -> None:
        path = self.attempt_dir / "audit-attempt.yaml"
        scope = self.attempt.get("scope")
        if not isinstance(scope, dict):
            self.errors.append(f"{path} scope must be a mapping")
            return
        acceptance_rows = self._require_string_list(
            scope.get("acceptance_rows"), "scope.acceptance_rows", path
        )
        self.scoped_rows = set(acceptance_rows)
        unknown_rows = sorted(self.scoped_rows - self.row_ids)
        if unknown_rows:
            self.errors.append(f"{path} scope references unknown rows: {', '.join(unknown_rows)}")
        finding_ids = self._require_string_list(scope.get("finding_ids"), "scope.finding_ids", path)
        self._require_string_list(scope.get("sibling_surfaces"), "scope.sibling_surfaces", path)
        mode = self.attempt.get("mode")
        if mode == "full" and self.scoped_rows != self.row_ids:
            self.errors.append(f"{path} full audit scope must include every matrix row")
        if mode == "targeted":
            if not finding_ids:
                self.errors.append(f"{path} targeted scope requires finding_ids")
            known_finding_ids = {
                row.get("id")
                for row in self.findings.get("findings", [])
                if isinstance(row, dict)
            }
            unknown_findings = sorted(set(finding_ids) - known_finding_ids)
            if unknown_findings:
                self.errors.append(
                    f"{path} targeted scope references unknown findings: {', '.join(unknown_findings)}"
                )

        matrix_rows = {
            row.get("id"): row for row in self.matrix.get("rows", []) if isinstance(row, dict)
        }
        for row_id in self.scoped_rows:
            row = matrix_rows.get(row_id, {})
            priority = row.get("priority")
            implementation = row.get("implementation", {})
            tests = row.get("tests", {})
            runtime = row.get("runtime_evidence", {})
            if priority not in {"documentation", "optional"}:
                if not isinstance(implementation, dict) or not implementation.get("actual_files"):
                    self.errors.append(f"matrix row {row_id} has no actual implementation files")
                if not isinstance(tests, dict) or not tests.get("required_assertions"):
                    self.errors.append(f"matrix row {row_id} has no required assertions")
                if not isinstance(tests, dict) or not tests.get("actual_tests"):
                    self.errors.append(f"matrix row {row_id} has no actual tests")
            if isinstance(runtime, dict) and runtime.get("required") is True:
                if not runtime.get("commands"):
                    self.errors.append(f"matrix row {row_id} has no runtime command")
                if not runtime.get("evidence"):
                    self.errors.append(f"matrix row {row_id} has no runtime evidence")
            if row.get("status") == "pending":
                self.errors.append(f"matrix row {row_id} remains pending")

        gates = self.attempt.get("gates")
        if not isinstance(gates, list):
            self.errors.append(f"{path} gates must be a list")
            return
        gate_ids: list[str] = []
        for index, gate in enumerate(gates, start=1):
            context = f"{path} gates[{index}]"
            if not isinstance(gate, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            gate_id = self._require_string(gate, "id", path, context=context)
            if gate_id:
                gate_ids.append(gate_id)
            self._require_string(gate, "source", path, context=context)
            self._require_string(gate, "command", path, context=context)
            status = gate.get("status")
            self._require_allowed(status, self.policy.get("gate_statuses"), "status", path, context)
            evidence = self._require_string_list(gate.get("evidence"), "evidence", path, context)
            reason = self._require_string(gate, "reason", path, context=context, allow_empty=True)
            if status == "pending":
                self.errors.append(f"{context} remains pending")
            elif status == "not_applicable" and not reason:
                self.errors.append(f"{context} not_applicable requires reason")
            elif status != "not_applicable" and not evidence:
                self.errors.append(f"{context} requires evidence")
        self._check_unique(gate_ids, "gate ids", path)

    def _validate_reviews(self) -> None:
        path = self.attempt_dir / "audit-attempt.yaml"
        review = self.attempt.get("review")
        if not isinstance(review, dict):
            self.errors.append(f"{path} review must be a mapping")
            return
        required_roles = self._require_string_list(
            review.get("required_roles"), "review.required_roles", path
        )
        known_roles = set(self.policy.get("roles", {}))
        unknown_roles = sorted(set(required_roles) - known_roles)
        if unknown_roles:
            self.errors.append(
                f"{path} review.required_roles contains unknown roles: {', '.join(unknown_roles)}"
            )
        risk_policy = self.policy.get("risk_review_policy", {}).get(
            self.attempt.get("risk_level"), {}
        )
        policy_roles = risk_policy.get("roles", []) if isinstance(risk_policy, dict) else []
        missing_policy_roles = sorted(set(policy_roles) - set(required_roles))
        if missing_policy_roles:
            self.errors.append(
                f"{path} review.required_roles missing policy roles: {', '.join(missing_policy_roles)}"
            )
        skipped_reason = self._require_string(
            review, "skipped_reason", path, context=str(path), allow_empty=True
        )
        outputs = review.get("outputs")
        if not isinstance(outputs, list):
            self.errors.append(f"{path} review.outputs must be a list")
            return
        if skipped_reason:
            if outputs:
                self.errors.append(f"{path} skipped review must not list outputs")
            return
        output_roles: list[str] = []
        for index, output in enumerate(outputs, start=1):
            context = f"{path} review.outputs[{index}]"
            if not isinstance(output, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            role = self._require_string(output, "role", path, context=context)
            output_path = self._require_string(output, "path", path, context=context)
            if role:
                output_roles.append(role)
            if output_path:
                resolved = self._resolve_path(output_path)
                if not resolved.is_file():
                    self.errors.append(f"{context} output file does not exist: {output_path}")
                else:
                    self._validate_review_role(resolved, role, context)
        self._check_unique(output_roles, "review output roles", path)
        missing_outputs = sorted(set(required_roles) - set(output_roles))
        if missing_outputs:
            self.errors.append(f"{path} has no output for roles: {', '.join(missing_outputs)}")

    def _validate_review_role(self, output_path: Path, expected_role: str, context: str) -> None:
        try:
            text = output_path.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"{context} cannot read review output: {exc}")
            return
        match = re.search(r"(?m)^AUDIT_ROLE:\s*([a-z][a-z0-9_]*)\s*$", text)
        if not match:
            self.errors.append(f"{context} output has no valid AUDIT_ROLE")
        elif expected_role and match.group(1) != expected_role:
            self.errors.append(
                f"{context} declares AUDIT_ROLE {match.group(1)!r}, expected {expected_role!r}"
            )
        decision = re.search(r"(?m)^DECISION:\s*([a-z][a-z0-9_]*)\s*$", text)
        allowed = self.policy.get("review_decisions", [])
        if not decision:
            self.errors.append(f"{context} output has no valid DECISION")
        elif not isinstance(allowed, list) or decision.group(1) not in allowed:
            self.errors.append(
                f"{context} declares unsupported DECISION {decision.group(1)!r}"
            )

    def _validate_completion(self) -> None:
        attempt_path = self.attempt_dir / "audit-attempt.yaml"
        status = self.attempt.get("status")
        if status == "pending":
            self.errors.append(f"{attempt_path} status remains pending")
        if not self.attempt.get("decision_reason"):
            self.errors.append(f"{attempt_path} decision_reason must not be empty")

        latest_matrix_path = self.epic_dir / "audit-verification-matrix.yaml"
        if not latest_matrix_path.is_file():
            self.errors.append(f"missing published audit matrix: {latest_matrix_path}")
        else:
            try:
                latest = _load_yaml(latest_matrix_path, "published audit matrix")
            except ValueError as exc:
                self.errors.append(str(exc))
            else:
                if latest != self.matrix:
                    self.errors.append("published audit matrix does not match attempt matrix")

        report = self.epic_dir / "epic_audit.md"
        if not report.is_file():
            self.errors.append(f"missing audit report: {report}")
        else:
            decision = f"Decision: {str(status).upper()}"
            if decision not in report.read_text(encoding="utf-8"):
                self.errors.append(f"{report} must contain {decision!r}")

        rows = {
            row.get("id"): row for row in self.matrix.get("rows", []) if isinstance(row, dict)
        }
        gates = [gate for gate in self.attempt.get("gates", []) if isinstance(gate, dict)]
        findings = [
            finding for finding in self.findings.get("findings", []) if isinstance(finding, dict)
        ]
        terminal_statuses = set(self.policy.get("terminal_finding_statuses", []))
        active = [finding for finding in findings if finding.get("status") not in terminal_statuses]
        nonpass_rows = {
            row_id
            for row_id in self.scoped_rows
            if rows.get(row_id, {}).get("status") not in {"pass", "not_applicable"}
        }
        nonpass_gates = [
            gate for gate in gates if gate.get("status") not in {"pass", "not_applicable"}
        ]
        covered_rows = {
            row_id
            for finding in active
            for row_id in _string_list(finding.get("affected_acceptance_ids"))
        }
        uncovered = sorted(nonpass_rows - covered_rows)
        if uncovered:
            self.errors.append(
                f"non-passing matrix rows have no active finding: {', '.join(uncovered)}"
            )

        if status == "pass":
            if nonpass_rows or nonpass_gates or active:
                self.errors.append("PASS requires passing scoped rows/gates and no active findings")
            if self.attempt.get("review", {}).get("skipped_reason"):
                self.errors.append("PASS cannot skip required review roles")
        elif status == "fail":
            remediation = [
                finding
                for finding in active
                if finding.get("disposition") == "remediation_required"
            ]
            if not (nonpass_rows or nonpass_gates or remediation):
                self.errors.append("FAIL requires non-passing evidence or remediation findings")
        elif status == "blocked":
            decisions = [
                finding
                for finding in active
                if finding.get("disposition")
                in {"user_decision", "documentation_decision"}
            ]
            blocked_evidence = [
                gate for gate in nonpass_gates if gate.get("status") == "blocked"
            ] or [
                row_id for row_id in nonpass_rows if rows.get(row_id, {}).get("status") == "blocked"
            ]
            if not (decisions or blocked_evidence):
                self.errors.append("BLOCKED requires decision-gated findings or blocked evidence")

        scope = self.attempt.get("scope", {})
        if self.attempt.get("mode") == "targeted" and isinstance(scope, dict):
            finding_ids = set(_string_list(scope.get("finding_ids")))
            by_id = {finding.get("id"): finding for finding in findings}
            unresolved = sorted(
                finding_id
                for finding_id in finding_ids
                if by_id.get(finding_id, {}).get("status") not in terminal_statuses
            )
            if status == "pass" and unresolved:
                self.errors.append(
                    f"targeted PASS has unresolved findings: {', '.join(unresolved)}"
                )

    def _resolve_path(self, value: str) -> Path:
        candidate = Path(value)
        return candidate if candidate.is_absolute() else self.repo_root / candidate

    def _require_equal(
        self,
        document: Mapping[str, Any],
        field: str,
        expected: Any,
        path: Path,
    ) -> None:
        if document.get(field) != expected:
            self.errors.append(
                f"{path} {field} must be {expected!r}, got {document.get(field)!r}"
            )

    def _require_string(
        self,
        document: Mapping[str, Any],
        field: str,
        path: Path,
        *,
        context: str | None = None,
        allow_empty: bool = False,
    ) -> str:
        value = document.get(field)
        label = context or str(path)
        if not isinstance(value, str) or (not allow_empty and not value.strip()):
            qualifier = "a string" if allow_empty else "a non-empty string"
            self.errors.append(f"{label} {field} must be {qualifier}")
            return ""
        return value.strip()

    def _require_string_list(
        self,
        value: Any,
        field: str,
        path: Path,
        context: str | None = None,
    ) -> list[str]:
        label = context or str(path)
        if not isinstance(value, list):
            self.errors.append(f"{label} {field} must be a list")
            return []
        strings = [item for item in value if isinstance(item, str) and item]
        if len(strings) != len(value):
            self.errors.append(f"{label} {field} values must be non-empty strings")
        return strings

    def _require_allowed(
        self,
        value: Any,
        allowed: Any,
        field: str,
        path: Path,
        context: str | None = None,
    ) -> None:
        label = context or str(path)
        if not isinstance(allowed, list):
            self.errors.append(f"policy allowed values for {field} must be a list")
        elif value not in allowed:
            self.errors.append(f"{label} {field} must be one of {allowed!r}, got {value!r}")

    def _check_unique(self, values: Iterable[str], label: str, path: Path) -> None:
        seen: set[str] = set()
        for value in values:
            if value in seen:
                self.errors.append(f"{path} duplicate {label}: {value!r}")
            seen.add(value)


def validate(args: argparse.Namespace) -> int:
    validator = AuditValidator(
        epic_dir=args.epic_dir,
        attempt_dir=args.attempt_dir,
        phase=args.phase,
        policy_path=args.policy,
        repo_root=args.repo_root,
    )
    errors = validator.validate()
    if errors:
        print(f"Audit artifact validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"Audit artifact validation passed: phase={args.phase} "
        f"attempt={args.attempt_dir}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="Prepare an audit attempt")
    prepare_parser.add_argument("epic_dir", type=Path)
    prepare_parser.add_argument("--repo-root", type=Path)
    prepare_parser.add_argument("--policy", type=Path, default=_default_policy_path())
    prepare_parser.add_argument("--mode", choices=("full", "targeted"), required=True)
    prepare_parser.add_argument("--cycle-id", default="audit-v2")
    prepare_parser.add_argument("--finding", action="append", default=[])
    prepare_parser.add_argument("--sibling-surface", action="append", default=[])
    prepare_parser.add_argument("--reason", default="")
    prepare_parser.add_argument("--allow-extra", action="store_true")
    prepare_parser.set_defaults(handler=prepare)

    validate_parser = subparsers.add_parser("validate", help="Validate an audit attempt")
    validate_parser.add_argument("epic_dir", type=Path)
    validate_parser.add_argument("attempt_dir", type=Path)
    validate_parser.add_argument("--phase", choices=VALIDATION_PHASES, required=True)
    validate_parser.add_argument("--repo-root", type=Path)
    validate_parser.add_argument("--policy", type=Path, default=_default_policy_path())
    validate_parser.set_defaults(handler=validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except ValueError as exc:
        print(f"Audit artifact operation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
