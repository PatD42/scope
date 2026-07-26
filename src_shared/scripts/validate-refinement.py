#!/usr/bin/env python3
"""Scaffold and validate Scope Epic Refine v3 artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path
import re
import sys
from typing import Any

import yaml


PHASE_ORDER = (
    "profile",
    "product",
    "architecture",
    "reconcile",
    "review",
    "handoff",
)
STABLE_REQUIREMENT_ID_PATTERN = re.compile(r"\b(?:AC|ERR|E2E)-[A-Za-z0-9][A-Za-z0-9._-]*\b")
STABLE_DECISION_ID_PATTERN = re.compile(r"\b(?:PDR|ADR)-[A-Za-z0-9][A-Za-z0-9._-]*\b")
REQUIREMENT_HEADING_PATTERN = re.compile(
    r"(?m)^#{2,6}\s+((?:AC|ERR|E2E)-[A-Za-z0-9][A-Za-z0-9._-]*)\b"
)
DECISION_HEADING_PATTERN = re.compile(
    r"(?m)^#{3,6}\s+((?:PDR|ADR)-[A-Za-z0-9][A-Za-z0-9._-]*)\b"
)
EVIDENCE_PATTERN = re.compile(r"\[EVIDENCE:\s*([^\]]+?)\s*\]")
NORMATIVE_PATTERN = re.compile(
    r"\b(?:must|shall|always|never|required|will reject|will fail)\b",
    flags=re.IGNORECASE,
)
REVIEW_MARKER_PATTERN = re.compile(
    r"(?m)^REVIEW_(PROVIDER|MISSION):\s*([a-z][a-z0-9_]*)\s*$"
)


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


def _default_policy_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config" / "refinement-policy.yaml"


def _infer_repo_root(epic_dir: Path) -> Path:
    resolved = epic_dir.resolve()
    if resolved.parent.name == "epics" and resolved.parent.parent.name == "docs":
        return resolved.parents[2]
    return Path.cwd().resolve()


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


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _assignment_key(value: Mapping[str, Any]) -> str:
    return f"{value.get('provider', '')}:{value.get('mission', '')}"


def _canonical_requirement_ids(text: str) -> list[str]:
    return REQUIREMENT_HEADING_PATTERN.findall(text)


def _canonical_decision_ids(text: str) -> list[str]:
    return DECISION_HEADING_PATTERN.findall(text)


def _expected_assignments(
    profile: Mapping[str, Any], policy: Mapping[str, Any]
) -> list[dict[str, str]]:
    risk = profile.get("risk_level")
    author = profile.get("author_provider")
    topology = _mapping(policy.get("review_topology")).get(risk)
    if not isinstance(topology, dict) or author not in {"claude", "codex"}:
        return []

    semantic = topology.get("semantic_core")
    if semantic == "alternate_author":
        providers = ["claude" if author == "codex" else "codex"]
    else:
        providers = _string_list(semantic)

    assignments = [
        {"provider": provider, "mission": "semantic_core"} for provider in providers
    ]
    if topology.get("capability_specialist") is True:
        specialist = topology.get("specialist_provider")
        provider = author if specialist == "author_provider" else specialist
        if provider in {"claude", "codex"}:
            assignments.append(
                {"provider": str(provider), "mission": "capability_specialist"}
            )
    return assignments


class RefinementScaffolder:
    """Create mechanical v3 manifest and traceability rows without replacing judgment."""

    def __init__(self, epic_dir: Path, policy_path: Path, repo_root: Path | None) -> None:
        self.epic_dir = epic_dir.resolve()
        self.policy = _load_yaml(policy_path.resolve(), "refinement policy")
        self.repo_root = (repo_root or _infer_repo_root(self.epic_dir)).resolve()

    def run(self) -> list[Path]:
        profile = _load_yaml(
            self.epic_dir / "refinement-profile.yaml", "refinement profile"
        )
        if profile.get("schema_version") != self.policy.get("profile_version"):
            raise ValueError(
                "scaffold requires the current refinement profile schema; "
                "legacy profiles are not supported"
            )
        acceptance = (self.epic_dir / "acceptance-criteria.md").read_text(
            encoding="utf-8"
        )
        design_path = self.epic_dir / "design.md"
        design = design_path.read_text(encoding="utf-8") if design_path.is_file() else ""
        manifest_path = self.epic_dir / "refinement-manifest.yaml"
        manifest = self._manifest(profile, acceptance, design, manifest_path)
        _write_yaml(manifest_path, manifest)

        written = [manifest_path]
        traceability_path = self.epic_dir / "acceptance-traceability.yaml"
        traceability = self._traceability(profile, manifest, traceability_path)
        _write_yaml(traceability_path, traceability)
        written.append(traceability_path)
        return written

    def _manifest(
        self,
        profile: Mapping[str, Any],
        acceptance: str,
        design: str,
        path: Path,
    ) -> dict[str, Any]:
        existing: dict[str, Any] = {}
        if path.is_file():
            existing = _load_yaml(path, "refinement manifest")
            if existing.get("schema_version") != self.policy.get("manifest_version"):
                raise ValueError(
                    "scaffold will not merge a legacy refinement manifest"
                )

        existing_requirements = {
            row.get("id"): row
            for row in existing.get("requirements", [])
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        requirements: list[dict[str, Any]] = []
        for requirement_id in dict.fromkeys(_canonical_requirement_ids(acceptance)):
            row = dict(existing_requirements.get(requirement_id, {}))
            row.setdefault("id", requirement_id)
            row.setdefault(
                "source",
                {"artifact": "acceptance-criteria.md", "anchor": requirement_id},
            )
            row.setdefault(
                "summary", self._line_summary(acceptance, requirement_id)
            )
            row.setdefault("type", "behavior")
            row.setdefault("risk", profile.get("risk_level", "medium"))
            row.setdefault("implementation_required", True)
            row.setdefault("affected_surfaces", [])
            row.setdefault("proof_obligations", [])
            row.setdefault("owner_story", None)
            requirements.append(row)

        existing_decisions = {
            row.get("id"): row
            for row in existing.get("decisions", [])
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        decisions: list[dict[str, Any]] = []
        for decision_id in dict.fromkeys(_canonical_decision_ids(design)):
            row = dict(existing_decisions.get(decision_id, {}))
            row.setdefault("id", decision_id)
            row.setdefault(
                "source", {"artifact": "design.md", "anchor": decision_id}
            )
            row.setdefault("summary", self._line_summary(design, decision_id))
            row.setdefault("status", "accepted")
            decisions.append(row)
        return {
            "schema_version": self.policy.get("manifest_version"),
            "epic_id": profile.get("epic_id"),
            "requirements": requirements,
            "decisions": decisions,
            "artifacts": existing.get("artifacts", []),
            "open_items": existing.get("open_items", []),
        }

    @staticmethod
    def _line_summary(text: str, stable_id: str) -> str:
        for line in text.splitlines():
            if stable_id in line:
                summary = re.sub(r"^[#*\-\s]+", "", line)
                summary = summary.replace(stable_id, "", 1).lstrip(" :.-")
                if summary:
                    return summary
        return f"Complete judgment for {stable_id}"

    def _traceability(
        self,
        profile: Mapping[str, Any],
        manifest: Mapping[str, Any],
        path: Path,
    ) -> dict[str, Any]:
        existing: dict[str, Any] = {}
        if path.is_file():
            existing = _load_yaml(path, "acceptance traceability")
            if existing.get("schema_version") != self.policy.get(
                "traceability_version"
            ):
                raise ValueError(
                    "scaffold will not merge legacy acceptance traceability"
                )
        existing_rows = {
            row.get("id"): row
            for row in existing.get("acceptance_items", [])
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        proof_index = self._proof_index()
        rows: list[dict[str, Any]] = []
        for requirement in manifest.get("requirements", []):
            if not isinstance(requirement, dict) or not requirement.get(
                "implementation_required"
            ):
                continue
            row_id = requirement.get("id")
            if not isinstance(row_id, str):
                continue
            prior = _mapping(existing_rows.get(row_id))
            runtime = _mapping(prior.get("runtime_evidence"))
            proof_rows = proof_index.get(row_id, [])
            runtime_required = any(
                proof.get("required_evidence") in {"live_smoke", "runtime_command"}
                for _, proof in proof_rows
            )
            rows.append(
                {
                    "id": row_id,
                    "story": requirement.get("owner_story") or "",
                    "source": requirement.get("source", {}),
                    "proof_obligation_ids": [
                        str(proof.get("id"))
                        for _, proof in proof_rows
                        if isinstance(proof.get("id"), str)
                    ],
                    "implementation": {
                        "actual_files": _string_list(
                            _mapping(prior.get("implementation")).get("actual_files")
                        )
                    },
                    "tests": {
                        "actual_tests": _string_list(
                            _mapping(prior.get("tests")).get("actual_tests")
                        )
                    },
                    "runtime_evidence": {
                        "required": runtime_required,
                        "commands": _string_list(runtime.get("commands")),
                        "evidence": _string_list(runtime.get("evidence")),
                    },
                    "status": prior.get("status", "planned"),
                    "audit_notes": prior.get("audit_notes", ""),
                }
            )
        return {
            "schema_version": self.policy.get("traceability_version"),
            "epic_id": profile.get("epic_id"),
            "acceptance_items": rows,
        }

    def _proof_index(self) -> dict[str, list[tuple[str, dict[str, Any]]]]:
        result: dict[str, list[tuple[str, dict[str, Any]]]] = {}
        for path in sorted(self.epic_dir.glob("file-plan-story-*.yaml")):
            plan = _load_yaml(path, "implementation boundary plan")
            story_id = plan.get("story_id")
            if not isinstance(story_id, str):
                continue
            for proof in plan.get("proof_obligations", []):
                if not isinstance(proof, dict):
                    continue
                for requirement_id in _string_list(proof.get("acceptance_rows")):
                    result.setdefault(requirement_id, []).append((story_id, proof))
        return result


class RefinementValidator:
    """Validate one Scope Epic Refine v3 handoff phase."""

    def __init__(
        self,
        epic_dir: Path,
        phase: str,
        policy_path: Path,
        repo_root: Path | None = None,
    ) -> None:
        self.epic_dir = epic_dir.resolve()
        self.phase = phase
        self.policy_path = policy_path.resolve()
        self.repo_root = (repo_root or _infer_repo_root(self.epic_dir)).resolve()
        self.errors: list[str] = []
        self.advisories: list[str] = []
        self.policy: dict[str, Any] = {}
        self.profile: dict[str, Any] = {}
        self.manifest: dict[str, Any] = {}
        self.requirement_ids: set[str] = set()
        self.story_ids: set[str] = set()
        self.proof_index: dict[str, list[tuple[str, dict[str, Any]]]] = {}

    def validate(self) -> list[str]:
        if self.phase not in PHASE_ORDER:
            return [f"unsupported validation phase: {self.phase}"]
        if not self.epic_dir.is_dir():
            return [f"epic directory does not exist: {self.epic_dir}"]
        if not self.repo_root.is_dir():
            return [f"repository root does not exist: {self.repo_root}"]
        try:
            self.policy = _load_yaml(self.policy_path, "refinement policy")
        except ValueError as exc:
            return [str(exc)]
        self._validate_phase_artifacts()
        self._load_profile()
        self._validate_profile()
        self._collect_advisories()
        if self._phase_at_least("product"):
            self._validate_product()
        if self._phase_at_least("architecture"):
            self._load_manifest()
            self._validate_manifest()
            self._validate_design()
        if self._phase_at_least("reconcile"):
            self._validate_boundary_plans()
            self._validate_traceability()
        if self._phase_at_least("review"):
            self._validate_findings(require_closed=self.phase == "handoff")
        if self.phase == "handoff":
            self._validate_ready_status()
        return self.errors

    def _phase_at_least(self, phase: str) -> bool:
        return PHASE_ORDER.index(self.phase) >= PHASE_ORDER.index(phase)

    def _validate_phase_artifacts(self) -> None:
        requirements = self.policy.get("phase_required_artifacts")
        if not isinstance(requirements, dict):
            self.errors.append("policy phase_required_artifacts must be a mapping")
            return
        artifacts = requirements.get(self.phase)
        if not isinstance(artifacts, list):
            self.errors.append(f"policy has no artifact list for phase {self.phase}")
            return
        for name in artifacts:
            if not isinstance(name, str) or not (self.epic_dir / name).is_file():
                self.errors.append(
                    f"missing {self.phase} artifact: {self.epic_dir / str(name)}"
                )

    def _load_profile(self) -> None:
        try:
            self.profile = _load_yaml(
                self.epic_dir / "refinement-profile.yaml", "refinement profile"
            )
        except ValueError as exc:
            self.errors.append(str(exc))

    def _validate_profile(self) -> None:
        if not self.profile:
            return
        path = self.epic_dir / "refinement-profile.yaml"
        self._require_equal(
            self.profile, "schema_version", self.policy.get("profile_version"), path
        )
        self._require_string(self.profile, "epic_id", path)
        author = self.profile.get("author_provider")
        self._require_allowed(
            author,
            self.policy.get("allowed_author_providers"),
            "author_provider",
            path,
        )
        self._require_allowed(
            self.profile.get("architecture_scope"),
            self.policy.get("allowed_architecture_scopes"),
            "architecture_scope",
            path,
        )
        risk = self.profile.get("risk_level")
        self._require_allowed(
            risk, self.policy.get("allowed_risk_levels"), "risk_level", path
        )
        capabilities = self._require_string_list(
            self.profile.get("capabilities"),
            "capabilities",
            path,
            allow_empty=True,
        )
        known_capabilities = _mapping(self.policy.get("capabilities"))
        for capability in capabilities:
            if capability not in known_capabilities:
                self.errors.append(f"{path} has unknown capability: {capability}")
        if risk in {"high", "critical"} and not capabilities:
            self.errors.append(
                f"{path} high/critical risk requires at least one capability"
            )

        review = self.profile.get("review")
        if not isinstance(review, dict):
            self.errors.append(f"{path} review must be a mapping")
            return
        assignments = review.get("assignments")
        parsed = self._validate_assignments(assignments, path, "review.assignments")
        expected = _expected_assignments(self.profile, self.policy)
        if Counter(_assignment_key(row) for row in parsed) != Counter(
            _assignment_key(row) for row in expected
        ):
            self.errors.append(
                f"{path} review.assignments must match risk/provider topology: "
                f"{[_assignment_key(row) for row in expected]}"
            )
        topology = _mapping(self.policy.get("review_topology")).get(risk)
        if isinstance(topology, dict):
            for field in (
                "maximum_full_reviews",
                "maximum_targeted_verifications",
            ):
                if review.get(field) != topology.get(field):
                    self.errors.append(
                        f"{path} review.{field} must be {topology.get(field)!r}"
                    )

    def _validate_assignments(
        self, value: Any, path: Path, label: str
    ) -> list[dict[str, str]]:
        if not isinstance(value, list) or not value:
            self.errors.append(f"{path} {label} must be a non-empty list")
            return []
        providers = set(self.policy.get("allowed_author_providers", []))
        missions = set(self.policy.get("review_missions", []))
        parsed: list[dict[str, str]] = []
        for index, row in enumerate(value, start=1):
            context = f"{path} {label}[{index}]"
            if not isinstance(row, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            provider = row.get("provider")
            mission = row.get("mission")
            if provider not in providers:
                self.errors.append(f"{context} has invalid provider {provider!r}")
            if mission not in missions:
                self.errors.append(f"{context} has invalid mission {mission!r}")
            if isinstance(provider, str) and isinstance(mission, str):
                parsed.append({"provider": provider, "mission": mission})
        keys = [_assignment_key(row) for row in parsed]
        self._check_unique(keys, label, path)
        return parsed

    def _validate_product(self) -> None:
        acceptance_path = self.epic_dir / "acceptance-criteria.md"
        design_path = self.epic_dir / "design.md"
        try:
            acceptance = acceptance_path.read_text(encoding="utf-8")
            design = design_path.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"cannot read product artifact: {exc}")
            return
        ids = _canonical_requirement_ids(acceptance)
        if not ids:
            self.errors.append(
                f"{acceptance_path} must contain AC-, ERR-, or E2E- headings"
            )
        self._check_unique(ids, "stable acceptance requirement ids", acceptance_path)
        if "## Product and Architecture Decisions" not in design:
            self.errors.append(
                f"{design_path} missing heading: Product and Architecture Decisions"
            )

    def _load_manifest(self) -> None:
        try:
            self.manifest = _load_yaml(
                self.epic_dir / "refinement-manifest.yaml", "refinement manifest"
            )
        except ValueError as exc:
            self.errors.append(str(exc))

    def _validate_manifest(self) -> None:
        if not self.manifest:
            return
        path = self.epic_dir / "refinement-manifest.yaml"
        self._require_equal(
            self.manifest, "schema_version", self.policy.get("manifest_version"), path
        )
        self._match_epic_id(self.manifest, path)
        requirements = self._require_mapping_list(
            self.manifest, "requirements", path, allow_empty=False
        )
        decisions = self._require_mapping_list(
            self.manifest, "decisions", path, allow_empty=True
        )
        artifacts = self._require_mapping_list(
            self.manifest, "artifacts", path, allow_empty=True
        )
        open_items = self._require_mapping_list(
            self.manifest, "open_items", path, allow_empty=True
        )
        self._validate_requirements(requirements, path)
        self._validate_decisions(decisions, path)
        self._validate_artifacts(artifacts, path)
        self._validate_open_items(open_items, path)
        self._validate_manifest_coverage(path)

    def _validate_requirements(
        self, rows: list[dict[str, Any]], path: Path
    ) -> None:
        manifest_policy = _mapping(self.policy.get("manifest"))
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            context = f"{path} requirements[{index}]"
            row_id = self._require_string(row, "id", path, context)
            if row_id:
                ids.append(row_id)
            self._validate_source(row.get("source"), path, context)
            self._require_string(row, "summary", path, context)
            self._require_allowed(
                row.get("type"),
                manifest_policy.get("requirement_types"),
                "type",
                path,
                context,
            )
            self._require_allowed(
                row.get("risk"),
                manifest_policy.get("requirement_risks"),
                "risk",
                path,
                context,
            )
            implementation_required = row.get("implementation_required")
            if not isinstance(implementation_required, bool):
                self.errors.append(
                    f"{context} implementation_required must be boolean"
                )
                implementation_required = False
            surfaces = self._require_string_list(
                row.get("affected_surfaces"),
                "affected_surfaces",
                path,
                context=context,
                allow_empty=not implementation_required,
            )
            proof = self._require_string_list(
                row.get("proof_obligations"),
                "proof_obligations",
                path,
                context=context,
                allow_empty=not implementation_required,
            )
            if implementation_required and not surfaces:
                self.errors.append(f"{context} requires an affected surface")
            if implementation_required and not proof:
                self.errors.append(f"{context} requires a proof obligation")
            owner = row.get("owner_story")
            if self._phase_at_least("reconcile") and implementation_required:
                if not isinstance(owner, str) or not owner.strip():
                    self.errors.append(f"{context} missing owner_story at reconciliation")
        self._check_unique(ids, "requirement ids", path)
        self.requirement_ids = set(ids)

    def _validate_decisions(
        self, rows: list[dict[str, Any]], path: Path
    ) -> None:
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            context = f"{path} decisions[{index}]"
            row_id = self._require_string(row, "id", path, context)
            if row_id:
                ids.append(row_id)
            self._validate_source(row.get("source"), path, context)
            self._require_string(row, "summary", path, context)
            status = self._require_string(row, "status", path, context)
            if status and status.lower() != "accepted":
                self.errors.append(f"{context} status must be accepted")
        self._check_unique(ids, "decision ids", path)

    def _validate_artifacts(
        self, rows: list[dict[str, Any]], path: Path
    ) -> None:
        capabilities = set(_string_list(self.profile.get("capabilities")))
        policy_capabilities = _mapping(self.policy.get("capabilities"))
        authorities = _mapping(self.policy.get("manifest")).get(
            "artifact_authorities"
        )
        tagged: dict[str, list[dict[str, Any]]] = {}
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            context = f"{path} artifacts[{index}]"
            artifact_id = self._require_string(row, "id", path, context)
            artifact_path = self._require_string(row, "path", path, context)
            kind = self._require_string(row, "kind", path, context)
            if artifact_id:
                ids.append(artifact_id)
            self._require_allowed(
                row.get("authority"), authorities, "authority", path, context
            )
            row_capabilities = self._require_string_list(
                row.get("capabilities"),
                "capabilities",
                path,
                context=context,
                allow_empty=True,
            )
            for capability in row_capabilities:
                if capability not in policy_capabilities:
                    self.errors.append(
                        f"{context} references unknown capability {capability}"
                    )
                tagged.setdefault(capability, []).append(row)
            if artifact_path:
                resolved = self._resolve_repo_path(artifact_path)
                if not resolved.is_file():
                    self.errors.append(
                        f"{context} artifact path does not exist: {artifact_path}"
                    )
            if not kind:
                continue
        self._check_unique(ids, "artifact ids", path)
        for capability in capabilities:
            capability_policy = _mapping(policy_capabilities.get(capability))
            rows_for_capability = tagged.get(capability, [])
            if not rows_for_capability:
                self.errors.append(
                    f"{path} has no artifact tagged for selected capability {capability}"
                )
                continue
            if capability_policy.get("native_contract_required") is True:
                accepted = set(
                    _string_list(capability_policy.get("accepted_artifact_kinds"))
                )
                if not any(row.get("kind") in accepted for row in rows_for_capability):
                    self.errors.append(
                        f"{path} capability {capability} requires an accepted native artifact kind"
                    )

    def _validate_open_items(
        self, rows: list[dict[str, Any]], path: Path
    ) -> None:
        allowed = _mapping(self.policy.get("manifest")).get("open_item_statuses")
        for index, row in enumerate(rows, start=1):
            context = f"{path} open_items[{index}]"
            self._require_string(row, "id", path, context)
            status = row.get("status")
            self._require_allowed(status, allowed, "status", path, context)
            if self._phase_at_least("reconcile") and status in {
                "open",
                "user_question",
            }:
                self.errors.append(f"{context} remains unresolved")

    def _validate_manifest_coverage(self, path: Path) -> None:
        acceptance = (self.epic_dir / "acceptance-criteria.md").read_text(
            encoding="utf-8"
        )
        documented = set(_canonical_requirement_ids(acceptance))
        missing = sorted(documented - self.requirement_ids)
        extra = sorted(self.requirement_ids - documented)
        if missing:
            self.errors.append(
                f"{path} missing stable acceptance requirements: {', '.join(missing)}"
            )
        if extra:
            self.errors.append(
                f"{path} has requirements absent from acceptance criteria: "
                f"{', '.join(extra)}"
            )
        design = (self.epic_dir / "design.md").read_text(encoding="utf-8")
        documented_decisions = set(_canonical_decision_ids(design))
        manifest_decisions = {
            row.get("id")
            for row in self.manifest.get("decisions", [])
            if isinstance(row, dict)
        }
        missing_decisions = sorted(documented_decisions - manifest_decisions)
        extra_decisions = sorted(manifest_decisions - documented_decisions)
        if missing_decisions:
            self.errors.append(
                f"{path} missing stable decisions: {', '.join(missing_decisions)}"
            )
        if extra_decisions:
            self.errors.append(
                f"{path} has decisions absent from design: "
                f"{', '.join(extra_decisions)}"
            )

    def _validate_design(self) -> None:
        path = self.epic_dir / "design.md"
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"cannot read {path}: {exc}")
            return
        design_policy = _mapping(self.policy.get("design"))
        for heading in _string_list(design_policy.get("required_headings")):
            if not re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", text):
                self.errors.append(f"{path} missing required heading: {heading}")
        evidence = EVIDENCE_PATTERN.findall(text)
        if self.profile.get("architecture_scope") != "none" and not evidence:
            self.errors.append(f"{path} must contain at least one [EVIDENCE: path#anchor]")
        for marker in evidence:
            self._validate_evidence_marker(marker, path)

        challenges = _mapping(self.policy.get("architecture_challenges"))
        required_challenges = _string_list(challenges.get("common"))
        for capability in _string_list(self.profile.get("capabilities")):
            required_challenges.extend(_string_list(challenges.get(capability)))
        for challenge in dict.fromkeys(required_challenges):
            pattern = rf"(?m)^###\s+CHALLENGE-{re.escape(challenge)}\s*$"
            if not re.search(pattern, text):
                self.errors.append(
                    f"{path} missing architecture challenge: {challenge}"
                )

        flow_risks = set(_string_list(design_policy.get("flow_required_risks")))
        hostile_risks = set(
            _string_list(design_policy.get("hostile_case_required_risks"))
        )
        for requirement in self.manifest.get("requirements", []):
            if not isinstance(requirement, dict) or not requirement.get(
                "implementation_required"
            ):
                continue
            requirement_id = requirement.get("id")
            risk = requirement.get("risk")
            if not isinstance(requirement_id, str):
                continue
            if risk in flow_risks:
                self._validate_design_section(
                    text,
                    path,
                    f"FLOW-{requirement_id}",
                    (
                        "Authority:",
                        "Producer:",
                        "Boundary:",
                        "State owner:",
                        "Consumer:",
                        "Failure policy:",
                        "Proof:",
                    ),
                )
            if risk in hostile_risks:
                self._validate_design_section(
                    text,
                    path,
                    f"HOSTILE-{requirement_id}",
                    ("Invalid case:", "Rejection mechanism:", "Evidence:"),
                )

    def _validate_evidence_marker(self, marker: str, source_path: Path) -> None:
        value = marker.strip()
        path_text, separator, anchor = value.partition("#")
        candidate = Path(path_text)
        if candidate.is_absolute() or ".." in candidate.parts:
            self.errors.append(
                f"{source_path} evidence path must be repository-relative: {value}"
            )
            return
        resolved = self.repo_root / candidate
        if not resolved.is_file():
            self.errors.append(f"{source_path} evidence path does not exist: {value}")
            return
        if not separator or not anchor.strip():
            self.errors.append(
                f"{source_path} evidence marker must use path#anchor: {value}"
            )
            return
        try:
            content = resolved.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"cannot read evidence path {resolved}: {exc}")
            return
        if anchor.strip() not in content:
            self.errors.append(
                f"{source_path} evidence anchor not found: {value}"
            )

    def _validate_design_section(
        self,
        text: str,
        path: Path,
        heading: str,
        required_labels: tuple[str, ...],
    ) -> None:
        match = re.search(
            rf"(?ms)^###\s+{re.escape(heading)}\s*$\n(.*?)(?=^###\s+|\Z)",
            text,
        )
        if not match:
            self.errors.append(f"{path} missing design section: {heading}")
            return
        section = match.group(1)
        for label in required_labels:
            if label not in section:
                self.errors.append(f"{path} {heading} missing field {label}")

    def _validate_boundary_plans(self) -> None:
        plans = sorted(self.epic_dir.glob("file-plan-story-*.yaml"))
        if not plans:
            self.errors.append(
                f"missing implementation boundary plans in {self.epic_dir}"
            )
            return
        dependencies: dict[str, list[str]] = {}
        proof_index: dict[str, list[tuple[str, dict[str, Any]]]] = {}
        for path in plans:
            try:
                plan = _load_yaml(path, "implementation boundary plan")
            except ValueError as exc:
                self.errors.append(str(exc))
                continue
            self._match_epic_id(plan, path)
            story_id = self._require_string(plan, "story_id", path)
            self._require_string(plan, "story_title", path)
            depends_on = self._require_string_list(
                plan.get("depends_on"), "depends_on", path, allow_empty=True
            )
            if story_id:
                if story_id in dependencies:
                    self.errors.append(f"duplicate story_id {story_id!r} in {path}")
                dependencies[story_id] = depends_on
            specifications = {
                "required_contracts": (
                    "id",
                    "contract",
                    "obligation",
                    "verification",
                ),
                "required_touchpoints": (
                    "id",
                    "surface",
                    "obligation",
                    "evidence_required",
                ),
                "candidate_files": ("path", "reason"),
                "forbidden_changes": ("path_or_surface", "rule"),
                "proof_obligations": (
                    "id",
                    "required_evidence",
                    "command_hint",
                    "success_condition",
                ),
            }
            for field, required_fields in specifications.items():
                entries = self._require_mapping_list(
                    plan, field, path, allow_empty=True
                )
                entry_ids: list[str] = []
                for index, entry in enumerate(entries, start=1):
                    context = f"{path} {field}[{index}]"
                    for required_field in required_fields:
                        self._require_string(
                            entry, required_field, path, context
                        )
                    entry_id = entry.get("id")
                    if isinstance(entry_id, str):
                        entry_ids.append(entry_id)
                    if field == "candidate_files" and entry.get("advisory") is not True:
                        self.errors.append(f"{context} advisory must be true")
                    if field == "proof_obligations":
                        rows = self._require_string_list(
                            entry.get("acceptance_rows"),
                            "acceptance_rows",
                            path,
                            context=context,
                            allow_empty=False,
                        )
                        unknown = sorted(set(rows) - self.requirement_ids)
                        if unknown:
                            self.errors.append(
                                f"{context} references unknown acceptance rows: {', '.join(unknown)}"
                            )
                        if story_id:
                            for row_id in rows:
                                proof_index.setdefault(row_id, []).append(
                                    (story_id, entry)
                                )
                self._check_unique(entry_ids, f"{field} ids", path)
        self.story_ids = set(dependencies)
        self.proof_index = proof_index
        for story_id, dependencies_for_story in dependencies.items():
            for dependency in dependencies_for_story:
                if dependency == story_id:
                    self.errors.append(f"story {story_id} depends on itself")
                elif dependency not in self.story_ids:
                    self.errors.append(
                        f"story {story_id} depends on unknown story {dependency}"
                    )
        self._detect_dependency_cycles(dependencies)
        for requirement in self.manifest.get("requirements", []):
            if not isinstance(requirement, dict) or not requirement.get(
                "implementation_required"
            ):
                continue
            row_id = requirement.get("id")
            owner = requirement.get("owner_story")
            if owner not in self.story_ids:
                self.errors.append(
                    f"manifest requirement {row_id} references unknown owner_story {owner!r}"
                )
            proof_owners = {
                story_id for story_id, _ in proof_index.get(str(row_id), [])
            }
            if not proof_owners:
                self.errors.append(
                    f"manifest requirement {row_id} has no story proof obligation"
                )
            elif owner not in proof_owners:
                self.errors.append(
                    f"manifest requirement {row_id} owner_story {owner!r} "
                    "does not own a proof obligation"
                )

    def _detect_dependency_cycles(
        self, dependencies: Mapping[str, list[str]]
    ) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(story_id: str) -> None:
            if story_id in visiting:
                self.errors.append(f"story dependency cycle includes {story_id}")
                return
            if story_id in visited:
                return
            visiting.add(story_id)
            for dependency in dependencies.get(story_id, []):
                if dependency in dependencies:
                    visit(dependency)
            visiting.remove(story_id)
            visited.add(story_id)

        for story_id in dependencies:
            visit(story_id)

    def _validate_traceability(self) -> None:
        path = self.epic_dir / "acceptance-traceability.yaml"
        try:
            document = _load_yaml(path, "acceptance traceability")
        except ValueError as exc:
            self.errors.append(str(exc))
            return
        self._require_equal(
            document,
            "schema_version",
            self.policy.get("traceability_version"),
            path,
        )
        self._match_epic_id(document, path)
        rows = self._require_mapping_list(
            document, "acceptance_items", path, allow_empty=False
        )
        expected_ids = {
            row.get("id")
            for row in self.manifest.get("requirements", [])
            if isinstance(row, dict) and row.get("implementation_required") is True
        }
        ids: list[str] = []
        requirements = {
            row.get("id"): row
            for row in self.manifest.get("requirements", [])
            if isinstance(row, dict)
        }
        allowed_statuses = _mapping(self.policy.get("traceability")).get("statuses")
        for index, row in enumerate(rows, start=1):
            context = f"{path} acceptance_items[{index}]"
            row_id = self._require_string(row, "id", path, context)
            if row_id:
                ids.append(row_id)
            requirement = requirements.get(row_id, {})
            story = self._require_string(row, "story", path, context)
            if story != requirement.get("owner_story"):
                self.errors.append(
                    f"{context} story does not match manifest owner_story"
                )
            if row.get("source") != requirement.get("source"):
                self.errors.append(f"{context} source does not match manifest")
            proof_ids = self._require_string_list(
                row.get("proof_obligation_ids"),
                "proof_obligation_ids",
                path,
                context=context,
                allow_empty=False,
            )
            expected_proof_ids = [
                str(proof.get("id"))
                for _, proof in self.proof_index.get(row_id, [])
                if isinstance(proof.get("id"), str)
            ]
            if proof_ids != expected_proof_ids:
                self.errors.append(
                    f"{context} proof_obligation_ids do not match story plans"
                )
            self._validate_list_mapping(
                row.get("implementation"), ("actual_files",), context, "implementation"
            )
            self._validate_list_mapping(
                row.get("tests"), ("actual_tests",), context, "tests"
            )
            runtime = row.get("runtime_evidence")
            self._validate_list_mapping(
                runtime, ("commands", "evidence"), context, "runtime_evidence"
            )
            if not isinstance(runtime, dict) or not isinstance(
                runtime.get("required"), bool
            ):
                self.errors.append(
                    f"{context} runtime_evidence.required must be boolean"
                )
            expected_runtime = any(
                proof.get("required_evidence") in {"live_smoke", "runtime_command"}
                for _, proof in self.proof_index.get(row_id, [])
            )
            if isinstance(runtime, dict) and runtime.get("required") != expected_runtime:
                self.errors.append(
                    f"{context} runtime_evidence.required does not match story plans"
                )
            self._require_allowed(
                row.get("status"), allowed_statuses, "status", path, context
            )
            if not isinstance(row.get("audit_notes"), str):
                self.errors.append(f"{context} audit_notes must be a string")
        self._check_unique(ids, "acceptance traceability ids", path)
        if set(ids) != expected_ids:
            missing = sorted(expected_ids - set(ids))
            extra = sorted(set(ids) - expected_ids)
            if missing:
                self.errors.append(
                    f"{path} missing implementation rows: {', '.join(missing)}"
                )
            if extra:
                self.errors.append(
                    f"{path} has non-implementation rows: {', '.join(extra)}"
                )

    def _validate_findings(self, *, require_closed: bool) -> None:
        path = self.epic_dir / "refinement-findings.yaml"
        try:
            document = _load_yaml(path, "refinement findings")
        except ValueError as exc:
            self.errors.append(str(exc))
            return
        self._require_equal(
            document, "schema_version", self.policy.get("findings_version"), path
        )
        self._match_epic_id(document, path)
        review = document.get("review")
        if not isinstance(review, dict):
            self.errors.append(f"{path} review must be a mapping")
            review = {}
        full_count = review.get("full_review_count")
        targeted_count = review.get("targeted_verification_count")
        risk = self.profile.get("risk_level")
        topology = _mapping(_mapping(self.policy.get("review_topology")).get(risk))
        if full_count != 1:
            self.errors.append(f"{path} review.full_review_count must be 1")
        maximum_targeted = topology.get("maximum_targeted_verifications")
        if not isinstance(targeted_count, int) or targeted_count < 0:
            self.errors.append(
                f"{path} review.targeted_verification_count must be non-negative"
            )
        elif isinstance(maximum_targeted, int) and targeted_count > maximum_targeted:
            self.errors.append(
                f"{path} targeted verification count exceeds {maximum_targeted}"
            )

        completed = self._validate_assignments(
            review.get("completed_assignments"),
            path,
            "review.completed_assignments",
        )
        expected = _expected_assignments(self.profile, self.policy)
        if Counter(_assignment_key(row) for row in completed) != Counter(
            _assignment_key(row) for row in expected
        ):
            self.errors.append(
                f"{path} review.completed_assignments do not satisfy profile"
            )

        outputs = review.get("outputs")
        if not isinstance(outputs, list):
            self.errors.append(f"{path} review.outputs must be a list")
            outputs = []
        output_keys: list[str] = []
        output_paths: list[str] = []
        for index, output in enumerate(outputs, start=1):
            context = f"{path} review.outputs[{index}]"
            if not isinstance(output, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            assignment = self._validate_assignments(
                [output], path, f"review.outputs[{index}]"
            )
            output_path = output.get("path")
            if not isinstance(output_path, str) or not output_path:
                self.errors.append(f"{context} path must be a non-empty string")
                continue
            output_paths.append(output_path)
            resolved = self._resolve_repo_path(output_path)
            if not resolved.is_file():
                self.errors.append(f"{context} output does not exist: {output_path}")
                continue
            if assignment:
                key = _assignment_key(assignment[0])
                output_keys.append(key)
                markers = self._review_markers(resolved, path)
                if markers and markers != assignment[0]:
                    self.errors.append(
                        f"{context} provider/mission do not match review output markers"
                    )
        self._check_unique(output_paths, "review output paths", path)
        if Counter(output_keys) != Counter(_assignment_key(row) for row in expected):
            self.errors.append(f"{path} review.outputs do not cover all assignments")

        findings = self._require_mapping_list(
            document, "findings", path, allow_empty=True
        )
        findings_policy = _mapping(self.policy.get("findings"))
        ids: list[str] = []
        fingerprints: list[str] = []
        completed_keys = {_assignment_key(row) for row in completed}
        for index, finding in enumerate(findings, start=1):
            context = f"{path} findings[{index}]"
            finding_id = self._require_string(finding, "id", path, context)
            fingerprint = self._require_string(
                finding, "fingerprint", path, context
            )
            if finding_id:
                ids.append(finding_id)
            if fingerprint:
                fingerprints.append(fingerprint)
            self._require_allowed(
                finding.get("severity"),
                findings_policy.get("severities"),
                "severity",
                path,
                context,
            )
            status = finding.get("status")
            self._require_allowed(
                status,
                findings_policy.get("statuses"),
                "status",
                path,
                context,
            )
            self._require_allowed(
                finding.get("category"),
                findings_policy.get("categories"),
                "category",
                path,
                context,
            )
            self._require_string(finding, "evidence", path, context)
            self._require_string(finding, "owner", path, context)
            self._require_string(finding, "closure_test", path, context)
            if status in {"open", "corrected"}:
                self._require_string(
                    finding, "required_correction", path, context
                )
            if status == "corrected":
                self._require_string(
                    finding, "correction_evidence", path, context
                )
            if status == "verified":
                self._require_string(
                    finding, "verification_evidence", path, context
                )
            affected = self._require_string_list(
                finding.get("affected_manifest_ids"),
                "affected_manifest_ids",
                path,
                context=context,
                allow_empty=False,
            )
            unknown = sorted(set(affected) - self.requirement_ids)
            if unknown:
                self.errors.append(
                    f"{context} references unknown manifest ids: {', '.join(unknown)}"
                )
            verification = self._validate_assignments(
                finding.get("verification_assignments"),
                path,
                f"findings[{index}].verification_assignments",
            )
            unknown_assignments = sorted(
                {_assignment_key(row) for row in verification} - completed_keys
            )
            if unknown_assignments:
                self.errors.append(
                    f"{context} references incomplete assignments: {unknown_assignments}"
                )
            if not isinstance(finding.get("requires_user"), bool):
                self.errors.append(f"{context} requires_user must be boolean")
            if status == "accepted_risk" and finding.get("requires_user") is not True:
                self.errors.append(
                    f"{context} accepted_risk requires explicit user approval"
                )
            if require_closed and status in {"open", "corrected"}:
                self.errors.append(f"{context} remains {status} at handoff")
        self._check_unique(ids, "finding ids", path)
        self._check_unique(fingerprints, "finding fingerprints", path)

    def _review_markers(
        self, output_path: Path, findings_path: Path
    ) -> dict[str, str]:
        try:
            text = output_path.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(
                f"{findings_path} cannot read review output {output_path}: {exc}"
            )
            return {}
        markers = {
            key.lower(): value for key, value in REVIEW_MARKER_PATTERN.findall(text)
        }
        if set(markers) != {"provider", "mission"}:
            self.errors.append(
                f"{findings_path} review output lacks REVIEW_PROVIDER/REVIEW_MISSION: {output_path}"
            )
            return {}
        return markers

    def _validate_ready_status(self) -> None:
        details = self.epic_dir / "details.md"
        try:
            text = details.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"cannot read {details}: {exc}")
            return
        match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
        if not match:
            self.errors.append(f"{details} must start with YAML frontmatter")
            return
        try:
            frontmatter = yaml.load(match.group(1), Loader=UniqueKeyLoader)
        except (yaml.YAMLError, DuplicateKeyError, TypeError) as exc:
            self.errors.append(f"invalid frontmatter in {details}: {exc}")
            return
        if not isinstance(frontmatter, dict):
            self.errors.append(f"frontmatter in {details} must be a mapping")
        elif frontmatter.get("status") != "ready-for-implementation":
            self.errors.append(
                f"{details} status must be ready-for-implementation at handoff"
            )
        review_path = self.epic_dir / "refinement-review.md"
        try:
            review_text = review_path.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"cannot read {review_path}: {exc}")
            return
        if "Decision: Approved for implementation" not in review_text:
            self.errors.append(
                f"{review_path} must contain 'Decision: Approved for implementation'"
            )

    def _collect_advisories(self) -> None:
        details = self.epic_dir / "details.md"
        if details.is_file():
            text = details.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), start=1):
                if (
                    NORMATIVE_PATTERN.search(line)
                    and not STABLE_REQUIREMENT_ID_PATTERN.search(line)
                    and not STABLE_DECISION_ID_PATTERN.search(line)
                ):
                    self.advisories.append(
                        f"{details.relative_to(self.repo_root)}:{number}: "
                        "possible untracked normative statement"
                    )
                    if len(self.advisories) >= 25:
                        break
        budgets = _mapping(_mapping(self.policy.get("design")).get(
            "advisory_content_budgets"
        ))
        for filename, field in (
            ("details.md", "details_words"),
            ("design.md", "design_words"),
        ):
            path = self.epic_dir / filename
            maximum = budgets.get(field)
            if path.is_file() and isinstance(maximum, int):
                words = len(path.read_text(encoding="utf-8").split())
                if words > maximum:
                    self.advisories.append(
                        f"{path.relative_to(self.repo_root)} has {words} words; "
                        f"advisory budget is {maximum}"
                    )

    def metrics(self) -> dict[str, Any]:
        files = [
            path
            for path in self.epic_dir.rglob("*")
            if path.is_file() and "/tmp_debug/" not in path.as_posix()
        ]
        review_outputs = [
            path
            for path in files
            if "/reviews/refine-v3-" in path.as_posix()
            and path.name.startswith("review-")
        ]
        metadata_files = [
            path
            for path in files
            if "/reviews/refine-v3-" in path.as_posix()
            and path.name.startswith("metadata-")
        ]
        durations = 0
        retries = 0
        for path in metadata_files:
            try:
                metadata = _load_yaml(path, "review metadata")
            except ValueError:
                continue
            rows = metadata.get("reviews", [])
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                if isinstance(row.get("duration_seconds"), int):
                    durations += row["duration_seconds"]
                if isinstance(row.get("retry_count"), int):
                    retries += row["retry_count"]
        findings_by_severity: Counter[str] = Counter()
        findings_by_category: Counter[str] = Counter()
        targeted_count = 0
        findings_path = self.epic_dir / "refinement-findings.yaml"
        if findings_path.is_file():
            try:
                findings = _load_yaml(findings_path, "refinement findings")
            except ValueError:
                findings = {}
            for row in findings.get("findings", []):
                if isinstance(row, dict):
                    findings_by_severity[str(row.get("severity", "unknown"))] += 1
                    findings_by_category[str(row.get("category", "unknown"))] += 1
            review = _mapping(findings.get("review"))
            if isinstance(review.get("targeted_verification_count"), int):
                targeted_count = review["targeted_verification_count"]
        elapsed: int | None = None
        started = self.profile.get("workflow_started_at")
        completed = self.profile.get("workflow_completed_at")
        if isinstance(started, str) and isinstance(completed, str):
            try:
                elapsed = int(
                    (
                        datetime.fromisoformat(completed.replace("Z", "+00:00"))
                        - datetime.fromisoformat(started.replace("Z", "+00:00"))
                    ).total_seconds()
                )
            except ValueError:
                pass
        return {
            "schema_version": 1,
            "epic_id": self.profile.get("epic_id"),
            "phase": self.phase,
            "artifact_file_count": len(files),
            "artifact_bytes": sum(path.stat().st_size for path in files),
            "review_output_count": len(review_outputs),
            "review_output_bytes": sum(path.stat().st_size for path in review_outputs),
            "review_metadata_count": len(metadata_files),
            "review_duration_seconds": durations,
            "review_retry_count": retries,
            "targeted_verification_count": targeted_count,
            "findings_by_severity": dict(sorted(findings_by_severity.items())),
            "findings_by_category": dict(sorted(findings_by_category.items())),
            "workflow_elapsed_seconds": elapsed,
        }

    def _validate_source(self, value: Any, path: Path, context: str) -> None:
        if not isinstance(value, dict):
            self.errors.append(f"{context} source must be a mapping")
            return
        artifact = value.get("artifact")
        anchor = value.get("anchor")
        if not isinstance(artifact, str) or not artifact.strip():
            self.errors.append(f"{context} source.artifact must be non-empty")
            return
        resolved = self.epic_dir / artifact
        if artifact.startswith("docs/"):
            resolved = self.repo_root / artifact
        if Path(artifact).is_absolute() or ".." in Path(artifact).parts:
            self.errors.append(f"{context} source.artifact must be repository-relative")
            return
        if not resolved.is_file():
            self.errors.append(f"{context} source artifact does not exist: {artifact}")
            return
        if not isinstance(anchor, str) or not anchor.strip():
            self.errors.append(f"{context} source.anchor must be non-empty")
            return
        try:
            text = resolved.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"{context} cannot read source artifact: {exc}")
            return
        if anchor not in text:
            self.errors.append(f"{context} source anchor not found: {anchor}")

    def _resolve_repo_path(self, value: str) -> Path:
        candidate = Path(value)
        if candidate.is_absolute():
            return candidate
        return self.repo_root / candidate

    def _match_epic_id(self, document: Mapping[str, Any], path: Path) -> None:
        value = self._require_string(document, "epic_id", path)
        profile_id = self.profile.get("epic_id")
        if value and profile_id and value != profile_id:
            self.errors.append(
                f"{path} epic_id {value!r} does not match profile {profile_id!r}"
            )

    def _validate_list_mapping(
        self,
        value: Any,
        fields: tuple[str, ...],
        context: str,
        label: str,
    ) -> None:
        if not isinstance(value, dict):
            self.errors.append(f"{context} {label} must be a mapping")
            return
        for field in fields:
            items = value.get(field)
            if not isinstance(items, list):
                self.errors.append(f"{context} {label}.{field} must be a list")
            elif any(
                not isinstance(item, str) or not item.strip() for item in items
            ):
                self.errors.append(
                    f"{context} {label}.{field} values must be non-empty strings"
                )

    def _require_mapping_list(
        self,
        document: Mapping[str, Any],
        field: str,
        path: Path,
        *,
        allow_empty: bool,
    ) -> list[dict[str, Any]]:
        value = document.get(field)
        if not isinstance(value, list):
            self.errors.append(f"{path} {field} must be a list")
            return []
        if not value and not allow_empty:
            self.errors.append(f"{path} {field} must not be empty")
        result: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                self.errors.append(f"{path} {field}[{index}] must be a mapping")
            else:
                result.append(item)
        return result

    def _require_string_list(
        self,
        value: Any,
        field: str,
        path: Path,
        *,
        allow_empty: bool,
        context: str | None = None,
    ) -> list[str]:
        label = context or str(path)
        if not isinstance(value, list):
            self.errors.append(f"{label} {field} must be a list")
            return []
        strings = [
            item for item in value if isinstance(item, str) and item.strip()
        ]
        if len(strings) != len(value):
            self.errors.append(f"{label} {field} values must be non-empty strings")
        if not strings and not allow_empty:
            self.errors.append(f"{label} {field} must not be empty")
        self._check_unique(strings, field, path)
        return strings

    def _require_string(
        self,
        document: Mapping[str, Any],
        field: str,
        path: Path,
        context: str | None = None,
    ) -> str:
        value = document.get(field)
        label = context or str(path)
        if not isinstance(value, str) or not value.strip():
            self.errors.append(f"{label} {field} must be a non-empty string")
            return ""
        return value.strip()

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
            self.errors.append(
                f"{label} {field} must be one of {allowed!r}, got {value!r}"
            )

    def _check_unique(
        self, values: Iterable[Any], label: str, path: Path
    ) -> None:
        seen: set[Any] = set()
        for value in values:
            try:
                duplicate = value in seen
            except TypeError:
                self.errors.append(f"{path} {label} contains a non-scalar value")
                continue
            if duplicate:
                self.errors.append(f"{path} duplicate {label}: {value!r}")
            else:
                seen.add(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epic_dir", type=Path, help="Path to docs/epics/{epic-dir}")
    parser.add_argument("--phase", choices=PHASE_ORDER, required=True)
    parser.add_argument("--policy", type=Path, default=_default_policy_path())
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument(
        "--scaffold",
        action="store_true",
        help="Refresh mechanical manifest and traceability rows before validation.",
    )
    parser.add_argument(
        "--metrics-output",
        type=Path,
        help="Write point-in-time workflow metrics as YAML after validation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.scaffold:
        try:
            written = RefinementScaffolder(
                args.epic_dir, args.policy, args.repo_root
            ).run()
        except (OSError, ValueError) as exc:
            print(f"Refinement scaffold failed: {exc}", file=sys.stderr)
            return 1
        for path in written:
            print(f"Refinement scaffold updated: {path}")

    validator = RefinementValidator(
        epic_dir=args.epic_dir,
        phase=args.phase,
        policy_path=args.policy,
        repo_root=args.repo_root,
    )
    errors = validator.validate()
    for advisory in validator.advisories:
        print(f"ADVISORY: {advisory}", file=sys.stderr)
    if errors:
        print(
            f"Refinement validation failed with {len(errors)} error(s):",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.metrics_output:
        _write_yaml(args.metrics_output, validator.metrics())
        print(f"Refinement metrics written: {args.metrics_output}")
    print(f"Refinement validation passed: phase={args.phase} epic={args.epic_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
