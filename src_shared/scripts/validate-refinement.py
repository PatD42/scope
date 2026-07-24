#!/usr/bin/env python3
"""Validate Scope Epic Refine v2 artifacts.

The validator checks structure, references, artifact existence, capability
coverage, story ownership, and review closure. It deliberately does not claim to
prove semantic correctness; that remains the responsibility of user decisions
and role-based review.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import yaml


PHASE_ORDER = (
    "profile",
    "product",
    "architecture",
    "pre_review",
    "review",
    "handoff",
)

STABLE_REQUIREMENT_ID_PATTERN = re.compile(
    r"(?m)^(?:#{2,6}\s+|\|\s*)((?:AC|ERR|E2E)-[A-Za-z0-9._-]+)\b"
)
STABLE_DECISION_ID_PATTERN = re.compile(
    r"(?m)^#{2,6}\s+((?:ADR|PDR)-[A-Za-z0-9._-]+)\b"
)


class DuplicateKeyError(ValueError):
    """Raised when a YAML mapping contains a duplicate key."""


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


class RefinementValidator:
    """Phase-aware validator for one epic refinement directory."""

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
        self.repo_root = (repo_root or self._infer_repo_root()).resolve()
        self.errors: list[str] = []
        self.policy: dict[str, Any] = {}
        self.profile: dict[str, Any] = {}
        self.manifest: dict[str, Any] = {}
        self.story_ids: set[str] = set()
        self.requirement_ids: set[str] = set()
        self.proof_owners: dict[str, set[str]] = {}

    def _infer_repo_root(self) -> Path:
        if (
            self.epic_dir.parent.name == "epics"
            and self.epic_dir.parent.parent.name == "docs"
        ):
            return self.epic_dir.parents[2]
        return Path.cwd()

    def validate(self) -> list[str]:
        if self.phase not in PHASE_ORDER:
            return [f"unsupported validation phase: {self.phase}"]
        if not self.epic_dir.is_dir():
            return [f"epic directory does not exist: {self.epic_dir}"]

        self.policy = self._load_mapping(self.policy_path, "refinement policy")
        if not self.policy:
            return self.errors

        self._validate_all_epic_yaml()
        self._validate_phase_artifacts()
        self._validate_profile()

        if self._phase_at_least("architecture"):
            self._validate_manifest()
        if self._phase_at_least("pre_review"):
            self._validate_boundary_plans()
            self._validate_traceability()
            self._validate_pre_review_audit()
        if self._phase_at_least("review"):
            self._validate_findings(require_closed=self._phase_at_least("handoff"))
        if self._phase_at_least("handoff"):
            self._validate_ready_status()

        return self.errors

    def _phase_at_least(self, phase: str) -> bool:
        return PHASE_ORDER.index(self.phase) >= PHASE_ORDER.index(phase)

    def _load_mapping(self, path: Path, label: str) -> dict[str, Any]:
        if not path.is_file():
            self.errors.append(f"missing {label}: {path}")
            return {}
        try:
            value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
        except (OSError, yaml.YAMLError, DuplicateKeyError, TypeError) as exc:
            self.errors.append(f"invalid {label} {path}: {exc}")
            return {}
        if not isinstance(value, dict):
            self.errors.append(f"{label} must contain a YAML mapping: {path}")
            return {}
        return value

    def _validate_all_epic_yaml(self) -> None:
        for path in sorted(self.epic_dir.rglob("*.yaml")):
            try:
                yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
            except (OSError, yaml.YAMLError, DuplicateKeyError, TypeError) as exc:
                self.errors.append(f"invalid YAML {path}: {exc}")

    def _validate_phase_artifacts(self) -> None:
        requirements = self.policy.get("phase_required_artifacts", {})
        if not isinstance(requirements, dict):
            self.errors.append("policy phase_required_artifacts must be a mapping")
            return
        required = requirements.get(self.phase)
        if not isinstance(required, list):
            self.errors.append(f"policy has no artifact list for phase {self.phase}")
            return
        for name in required:
            if not isinstance(name, str) or not (self.epic_dir / name).is_file():
                self.errors.append(
                    f"missing {self.phase} artifact: {self.epic_dir / str(name)}"
                )

    def _validate_profile(self) -> None:
        path = self.epic_dir / "refinement-profile.yaml"
        self.profile = self._load_mapping(path, "refinement profile")
        if not self.profile:
            return

        self._require_equal(
            self.profile,
            "schema_version",
            self.policy.get("profile_version"),
            path,
        )
        epic_id = self._require_string(self.profile, "epic_id", path)
        self._require_string(self.profile, "classification_rationale", path)

        scope = self._require_string(self.profile, "architecture_scope", path)
        self._require_allowed(
            scope,
            self.policy.get("allowed_architecture_scopes"),
            "architecture_scope",
            path,
        )
        risk = self._require_string(self.profile, "risk_level", path)
        self._require_allowed(
            risk,
            self.policy.get("allowed_risk_levels"),
            "risk_level",
            path,
        )

        capabilities = self.profile.get("capabilities")
        if not isinstance(capabilities, list):
            self.errors.append(f"{path} capabilities must be a list")
            capabilities = []
        self._check_unique_scalars(capabilities, "capabilities", path)
        known_capabilities = self.policy.get("capabilities", {})
        if not isinstance(known_capabilities, dict):
            self.errors.append("policy capabilities must be a mapping")
            known_capabilities = {}
        for capability in capabilities:
            if not isinstance(capability, str):
                self.errors.append(f"{path} capability values must be strings")
                continue
            if capability not in known_capabilities:
                self.errors.append(f"{path} has unknown capability: {capability}")

        review = self.profile.get("review")
        if not isinstance(review, dict):
            self.errors.append(f"{path} review must be a mapping")
            return
        roles = review.get("roles")
        if not isinstance(roles, list) or not roles:
            self.errors.append(f"{path} review.roles must be a non-empty list")
            roles = []
        self._check_unique_scalars(roles, "review.roles", path)
        valid_roles = {role for role in roles if isinstance(role, str)}
        if len(valid_roles) != len(roles):
            self.errors.append(f"{path} review.roles values must be strings")

        risk_policy = self._risk_policy(risk)
        required_roles = risk_policy.get("roles", [])
        if isinstance(required_roles, list):
            missing_roles = sorted(set(required_roles) - valid_roles)
            if missing_roles:
                self.errors.append(
                    f"{path} review.roles missing policy roles for {risk}: {', '.join(missing_roles)}"
                )
        self._validate_budget(review, risk_policy, "maximum_full_reviews", path)
        self._validate_budget(
            review,
            risk_policy,
            "maximum_targeted_verifications",
            path,
            minimum_policy_field="minimum_targeted_verifications",
        )
        minimum_full_reviews = risk_policy.get("minimum_full_reviews")
        maximum_full_reviews = review.get("maximum_full_reviews")
        if (
            isinstance(minimum_full_reviews, int)
            and isinstance(maximum_full_reviews, int)
            and maximum_full_reviews < minimum_full_reviews
        ):
            self.errors.append(
                f"{path} review.maximum_full_reviews={maximum_full_reviews} "
                f"is below policy minimum {minimum_full_reviews}"
            )

        if not epic_id:
            return

    def _validate_budget(
        self,
        review: Mapping[str, Any],
        risk_policy: Mapping[str, Any],
        field: str,
        path: Path,
        minimum_policy_field: str | None = None,
    ) -> None:
        actual = review.get(field)
        expected = risk_policy.get(field)
        minimum = (
            risk_policy.get(minimum_policy_field) if minimum_policy_field else None
        )
        if not isinstance(actual, int) or actual < 0:
            self.errors.append(f"{path} review.{field} must be a non-negative integer")
        elif isinstance(minimum, int) and actual < minimum:
            self.errors.append(
                f"{path} review.{field}={actual} is below policy minimum {minimum}"
            )
        elif isinstance(expected, int) and actual > expected:
            self.errors.append(
                f"{path} review.{field}={actual} exceeds policy maximum {expected}"
            )

    def _risk_policy(self, risk: str) -> dict[str, Any]:
        policies = self.policy.get("risk_review_policy", {})
        if not isinstance(policies, dict):
            self.errors.append("policy risk_review_policy must be a mapping")
            return {}
        value = policies.get(risk, {})
        if not isinstance(value, dict):
            self.errors.append(f"policy has no review mapping for risk {risk}")
            return {}
        return value

    def _validate_manifest(self) -> None:
        path = self.epic_dir / "refinement-manifest.yaml"
        self.manifest = self._load_mapping(path, "refinement manifest")
        if not self.manifest:
            return

        self._require_equal(
            self.manifest,
            "schema_version",
            self.policy.get("manifest_version"),
            path,
        )
        manifest_epic_id = self._require_string(self.manifest, "epic_id", path)
        profile_epic_id = self.profile.get("epic_id")
        if manifest_epic_id and profile_epic_id and manifest_epic_id != profile_epic_id:
            self.errors.append(
                f"{path} epic_id {manifest_epic_id!r} does not match profile {profile_epic_id!r}"
            )

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
        self._validate_documented_requirement_coverage(path)
        self._validate_decisions(decisions, path)
        self._validate_documented_decision_coverage(path)
        self._validate_artifacts(artifacts, path)
        self._validate_open_items(open_items, path)
        self._validate_capability_coverage(artifacts, path)

    def _validate_requirements(self, rows: list[dict[str, Any]], path: Path) -> None:
        allowed_risks = self.policy.get("manifest", {}).get("requirement_risks", [])
        allowed_types = self.policy.get("manifest", {}).get("requirement_types", [])
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            context = f"{path} requirements[{index}]"
            row_id = self._require_string(row, "id", path, context)
            if row_id:
                ids.append(row_id)
            self._validate_source(row.get("source"), path, context)
            self._require_string(row, "summary", path, context)
            self._require_allowed(row.get("type"), allowed_types, "type", path, context)
            self._require_allowed(row.get("risk"), allowed_risks, "risk", path, context)

            implementation_required = row.get("implementation_required")
            if not isinstance(implementation_required, bool):
                self.errors.append(f"{context} implementation_required must be boolean")
                implementation_required = False
            if (
                row_id
                and row_id.startswith(("ERR-", "E2E-"))
                and implementation_required is not True
            ):
                self.errors.append(
                    f"{context} stable error and E2E requirements must require implementation proof"
                )
            surfaces = row.get("affected_surfaces")
            if not isinstance(surfaces, list):
                self.errors.append(f"{context} affected_surfaces must be a list")
                surfaces = []
            else:
                self._validate_non_empty_string_values(
                    surfaces, "affected_surfaces", context
                )
            proof = row.get("proof_obligations")
            if not isinstance(proof, list):
                self.errors.append(f"{context} proof_obligations must be a list")
                proof = []
            else:
                self._validate_non_empty_string_values(
                    proof, "proof_obligations", context
                )
            if implementation_required and not surfaces:
                self.errors.append(f"{context} requires at least one affected surface")
            if implementation_required and not proof:
                self.errors.append(f"{context} requires at least one proof obligation")
            owner = row.get("owner_story")
            if self._phase_at_least("pre_review") and implementation_required:
                if not isinstance(owner, str) or not owner.strip():
                    self.errors.append(f"{context} missing owner_story at handoff")
        self._check_unique_scalars(ids, "requirement ids", path)
        self.requirement_ids = set(ids)

    def _validate_documented_requirement_coverage(self, path: Path) -> None:
        acceptance_path = self.epic_dir / "acceptance-criteria.md"
        try:
            text = acceptance_path.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"cannot read {acceptance_path}: {exc}")
            return
        documented_ids = set(STABLE_REQUIREMENT_ID_PATTERN.findall(text))
        missing = sorted(documented_ids - self.requirement_ids)
        if missing:
            self.errors.append(
                f"{path} missing stable acceptance requirements: {', '.join(missing)}"
            )

    def _validate_decisions(self, rows: list[dict[str, Any]], path: Path) -> None:
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            context = f"{path} decisions[{index}]"
            row_id = self._require_string(row, "id", path, context)
            if row_id:
                ids.append(row_id)
            self._validate_source(row.get("source"), path, context)
            self._require_string(row, "summary", path, context)
            status = self._require_string(row, "status", path, context)
            if self._phase_at_least("pre_review") and status.lower() != "accepted":
                self.errors.append(f"{context} status must be accepted before review")
        self._check_unique_scalars(ids, "decision ids", path)

    def _validate_documented_decision_coverage(self, path: Path) -> None:
        documented_ids: set[str] = set()
        for name in ("pdr.md", "adr.md"):
            decision_path = self.epic_dir / name
            try:
                text = decision_path.read_text(encoding="utf-8")
            except OSError as exc:
                self.errors.append(f"cannot read {decision_path}: {exc}")
                continue
            documented_ids.update(STABLE_DECISION_ID_PATTERN.findall(text))
        manifest_ids = {
            row.get("id")
            for row in self.manifest.get("decisions", [])
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        missing = sorted(documented_ids - manifest_ids)
        if missing:
            self.errors.append(f"{path} missing stable decisions: {', '.join(missing)}")

    def _validate_artifacts(self, rows: list[dict[str, Any]], path: Path) -> None:
        authorities = self.policy.get("manifest", {}).get("artifact_authorities", [])
        known_capabilities = self.policy.get("capabilities", {})
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            context = f"{path} artifacts[{index}]"
            row_id = self._require_string(row, "id", path, context)
            if row_id:
                ids.append(row_id)
            artifact_path = self._require_string(row, "path", path, context)
            self._require_string(row, "kind", path, context)
            self._require_allowed(
                row.get("authority"), authorities, "authority", path, context
            )
            capabilities = row.get("capabilities")
            if not isinstance(capabilities, list):
                self.errors.append(f"{context} capabilities must be a list")
                capabilities = []
            for capability in capabilities:
                if not isinstance(capability, str):
                    self.errors.append(f"{context} capability values must be strings")
                    continue
                if capability not in known_capabilities:
                    self.errors.append(
                        f"{context} references unknown capability {capability!r}"
                    )
            if artifact_path:
                resolved = self._resolve_repo_path(artifact_path)
                if not resolved.exists():
                    self.errors.append(
                        f"{context} artifact path does not exist: {artifact_path}"
                    )
                self._validate_architecture_scope_path(artifact_path, context)
        self._check_unique_scalars(ids, "artifact ids", path)

    def _validate_architecture_scope_path(
        self, artifact_path: str, context: str
    ) -> None:
        normalized = artifact_path.replace("\\", "/")
        if not normalized.startswith("docs/architecture/"):
            return
        scope = self.profile.get("architecture_scope")
        if scope == "backend" and not normalized.startswith(
            "docs/architecture/backend/"
        ):
            self.errors.append(f"{context} must use the backend architecture tree")
        elif scope == "frontend" and not normalized.startswith(
            "docs/architecture/frontend/"
        ):
            self.errors.append(f"{context} must use the frontend architecture tree")
        elif scope == "system" and normalized.startswith(
            ("docs/architecture/backend/", "docs/architecture/frontend/")
        ):
            self.errors.append(f"{context} must use the system architecture tree")

    def _validate_open_items(self, rows: list[dict[str, Any]], path: Path) -> None:
        allowed = self.policy.get("manifest", {}).get("open_item_statuses", [])
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            context = f"{path} open_items[{index}]"
            row_id = self._require_string(row, "id", path, context)
            if row_id:
                ids.append(row_id)
            self._require_string(row, "issue", path, context)
            status = row.get("status")
            self._require_allowed(status, allowed, "status", path, context)
            if self._phase_at_least("pre_review") and status in {
                "open",
                "user_question",
            }:
                self.errors.append(f"{context} remains unresolved at handoff")
        self._check_unique_scalars(ids, "open item ids", path)

    def _validate_capability_coverage(
        self,
        artifacts: list[dict[str, Any]],
        path: Path,
    ) -> None:
        selected = self.profile.get("capabilities", [])
        capability_policy = self.policy.get("capabilities", {})
        if not isinstance(selected, list) or not isinstance(capability_policy, dict):
            return
        for capability in selected:
            policy = capability_policy.get(capability, {})
            tagged = [
                row
                for row in artifacts
                if isinstance(row.get("capabilities"), list)
                and capability in row["capabilities"]
            ]
            if not tagged:
                self.errors.append(
                    f"{path} has no artifact tagged for selected capability {capability}"
                )
                continue
            if not isinstance(policy, dict) or not policy.get(
                "native_contract_required"
            ):
                continue
            accepted = policy.get("accepted_artifact_kinds", [])
            if not any(row.get("kind") in accepted for row in tagged):
                self.errors.append(
                    f"{path} capability {capability} requires one artifact kind from: "
                    f"{', '.join(str(item) for item in accepted)}"
                )

    def _validate_boundary_plans(self) -> None:
        plans = sorted(self.epic_dir.glob("file-plan-story-*.yaml"))
        if not plans:
            self.errors.append(
                f"missing implementation boundary plans in {self.epic_dir}"
            )
            return

        dependencies: dict[str, list[str]] = {}
        for path in plans:
            plan = self._load_mapping(path, "implementation boundary plan")
            if not plan:
                continue
            story_id = self._require_string(plan, "story_id", path)
            plan_epic_id = self._require_string(plan, "epic_id", path)
            profile_epic_id = self.profile.get("epic_id")
            if plan_epic_id and profile_epic_id and plan_epic_id != profile_epic_id:
                self.errors.append(
                    f"{path} epic_id {plan_epic_id!r} does not match profile "
                    f"{profile_epic_id!r}"
                )
            self._require_string(plan, "story_title", path)
            depends_on = plan.get("depends_on")
            if not isinstance(depends_on, list):
                self.errors.append(f"{path} depends_on must be a list")
                depends_on = []
            for field in (
                "required_contracts",
                "required_touchpoints",
                "candidate_files",
                "forbidden_changes",
                "proof_obligations",
            ):
                if not isinstance(plan.get(field), list):
                    self.errors.append(f"{path} {field} must be a list")
            self._validate_boundary_entries(plan, path)
            if story_id:
                if story_id in dependencies:
                    self.errors.append(f"duplicate story_id {story_id!r} in {path}")
                dependencies[story_id] = [str(item) for item in depends_on]

        self.story_ids = set(dependencies)
        for story_id, depends_on in dependencies.items():
            for dependency in depends_on:
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
            owner = requirement.get("owner_story")
            requirement_id = str(requirement.get("id", "<missing>"))
            if owner not in self.story_ids:
                self.errors.append(
                    f"manifest requirement {requirement_id} "
                    f"references unknown owner_story {owner!r}"
                )
            proof_stories = self.proof_owners.get(requirement_id, set())
            if not proof_stories:
                self.errors.append(
                    f"manifest requirement {requirement_id} has no story proof obligation"
                )
            elif owner not in proof_stories:
                self.errors.append(
                    f"manifest requirement {requirement_id} owner_story {owner!r} "
                    "does not own a proof obligation"
                )

    def _validate_boundary_entries(self, plan: Mapping[str, Any], path: Path) -> None:
        specifications = {
            "required_contracts": ("id", "contract", "obligation", "verification"),
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
            entries = plan.get(field)
            if not isinstance(entries, list):
                continue
            entry_ids: list[str] = []
            for index, entry in enumerate(entries, start=1):
                context = f"{path} {field}[{index}]"
                if not isinstance(entry, dict):
                    self.errors.append(f"{context} must be a mapping")
                    continue
                for required_field in required_fields:
                    value = entry.get(required_field)
                    if not isinstance(value, str) or not value.strip():
                        self.errors.append(
                            f"{context} {required_field} must be a non-empty string"
                        )
                entry_id = entry.get("id")
                if isinstance(entry_id, str) and entry_id:
                    entry_ids.append(entry_id)
                if field == "candidate_files" and entry.get("advisory") is not True:
                    self.errors.append(f"{context} advisory must be true")
                if field == "proof_obligations":
                    acceptance_rows = entry.get("acceptance_rows")
                    if not isinstance(acceptance_rows, list) or not acceptance_rows:
                        self.errors.append(
                            f"{context} acceptance_rows must be a non-empty list"
                        )
                    else:
                        valid_rows = {
                            item for item in acceptance_rows if isinstance(item, str)
                        }
                        if len(valid_rows) != len(acceptance_rows):
                            self.errors.append(
                                f"{context} acceptance_rows values must be strings"
                            )
                        unknown = sorted(valid_rows - self.requirement_ids)
                        if unknown:
                            self.errors.append(
                                f"{context} references unknown acceptance rows: {', '.join(unknown)}"
                            )
                        story_id = plan.get("story_id")
                        if isinstance(story_id, str) and story_id:
                            for requirement_id in valid_rows:
                                self.proof_owners.setdefault(requirement_id, set()).add(
                                    story_id
                                )
            if entry_ids:
                self._check_unique_scalars(entry_ids, f"{field} ids", path)

    def _detect_dependency_cycles(self, dependencies: Mapping[str, list[str]]) -> None:
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
        traceability = self._load_mapping(path, "acceptance traceability")
        if not traceability:
            return
        self._require_equal(
            traceability,
            "schema_version",
            self.policy.get("traceability_version"),
            path,
        )
        traceability_epic_id = self._require_string(traceability, "epic_id", path)
        profile_epic_id = self.profile.get("epic_id")
        if (
            traceability_epic_id
            and profile_epic_id
            and traceability_epic_id != profile_epic_id
        ):
            self.errors.append(
                f"{path} epic_id {traceability_epic_id!r} does not match profile "
                f"{profile_epic_id!r}"
            )
        rows = self._require_mapping_list(
            traceability, "acceptance_items", path, allow_empty=False
        )
        allowed_statuses = self.policy.get("traceability", {}).get("statuses", [])
        manifest_by_id = {
            row.get("id"): row
            for row in self.manifest.get("requirements", [])
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            context = f"{path} acceptance_items[{index}]"
            row_id = self._require_string(row, "id", path, context)
            if row_id:
                ids.append(row_id)
                if row_id not in self.requirement_ids:
                    self.errors.append(
                        f"{context} references unknown manifest requirement {row_id!r}"
                    )
            story = self._require_string(row, "story", path, context)
            self._require_string(row, "requirement", path, context)
            if story and story not in self.story_ids:
                self.errors.append(f"{context} references unknown story {story!r}")
            self._validate_source(row.get("source"), path, context)
            manifest_requirement = manifest_by_id.get(row_id)
            if isinstance(manifest_requirement, dict):
                owner_story = manifest_requirement.get("owner_story")
                if story and owner_story != story:
                    self.errors.append(
                        f"{context} story {story!r} does not match manifest owner_story "
                        f"{owner_story!r}"
                    )
                if row.get("source") != manifest_requirement.get("source"):
                    self.errors.append(
                        f"{context} source does not match manifest requirement source"
                    )
            implementation = row.get("implementation")
            tests = row.get("tests")
            runtime = row.get("runtime_evidence")
            self._validate_list_mapping_fields(
                implementation,
                ("expected_files", "actual_files"),
                "implementation",
                context,
            )
            self._validate_list_mapping_fields(
                tests,
                ("expected_files", "required_assertions", "actual_tests"),
                "tests",
                context,
            )
            if isinstance(tests, dict):
                assertions = tests.get("required_assertions")
                if isinstance(assertions, list):
                    self._validate_non_empty_string_values(
                        assertions,
                        "tests.required_assertions",
                        context,
                    )
                    if not assertions:
                        self.errors.append(
                            f"{context} tests.required_assertions must not be empty"
                        )
            self._validate_list_mapping_fields(
                runtime,
                ("commands", "evidence"),
                "runtime_evidence",
                context,
            )
            if isinstance(runtime, dict) and not isinstance(
                runtime.get("required"), bool
            ):
                self.errors.append(
                    f"{context} runtime_evidence.required must be boolean"
                )
            if isinstance(runtime, dict) and runtime.get("required") is True:
                commands = runtime.get("commands")
                if isinstance(commands, list) and not commands:
                    self.errors.append(
                        f"{context} runtime_evidence.commands must not be empty when required"
                    )
            self._require_allowed(
                row.get("status"), allowed_statuses, "status", path, context
            )
        self._check_unique_scalars(ids, "acceptance traceability ids", path)

        required = {
            row.get("id")
            for row in self.manifest.get("requirements", [])
            if isinstance(row, dict) and row.get("implementation_required") is True
        }
        missing = sorted(item for item in required if item and item not in set(ids))
        if missing:
            self.errors.append(
                f"{path} missing implementation requirements: {', '.join(missing)}"
            )

    def _validate_pre_review_audit(self) -> None:
        path = self.epic_dir / "reviews/refine-v2-001/pre-review-audit.yaml"
        audit = self._load_mapping(path, "pre-review audit")
        if not audit:
            return

        self._require_equal(
            audit,
            "schema_version",
            self.policy.get("pre_review_audit_version"),
            path,
        )
        audit_epic_id = self._require_string(audit, "epic_id", path)
        profile_epic_id = self.profile.get("epic_id")
        if audit_epic_id and profile_epic_id and audit_epic_id != profile_epic_id:
            self.errors.append(
                f"{path} epic_id {audit_epic_id!r} does not match profile "
                f"{profile_epic_id!r}"
            )
        input_fingerprint = self._require_string(audit, "input_fingerprint", path)
        expected_fingerprint = self.pre_review_input_fingerprint()
        if input_fingerprint and input_fingerprint != expected_fingerprint:
            self.errors.append(
                f"{path} input_fingerprint is stale; expected {expected_fingerprint}"
            )

        audit_policy = self.policy.get("pre_review_audit", {})
        if not isinstance(audit_policy, dict):
            self.errors.append("policy pre_review_audit must be a mapping")
            audit_policy = {}
        expected_source = audit_policy.get(
            "canonical_requirement_source", "acceptance-criteria.md"
        )
        canonical_source = self._require_string(
            audit, "canonical_requirement_source", path
        )
        if canonical_source and canonical_source != expected_source:
            self.errors.append(
                f"{path} canonical_requirement_source must be {expected_source!r}"
            )

        covered = self._require_string_list(
            audit.get("covered_requirement_ids"),
            "covered_requirement_ids",
            path,
            allow_empty=False,
        )
        required = {
            row.get("id")
            for row in self.manifest.get("requirements", [])
            if isinstance(row, dict) and row.get("implementation_required") is True
        }
        covered_set = set(covered)
        missing = sorted(item for item in required if item and item not in covered_set)
        unknown = sorted(covered_set - self.requirement_ids)
        if missing:
            self.errors.append(
                f"{path} missing covered implementation requirements: {', '.join(missing)}"
            )
        if unknown:
            self.errors.append(
                f"{path} covers unknown requirements: {', '.join(unknown)}"
            )

        for field in (
            "untracked_normative_statements",
            "unindexed_decision_ids",
            "unresolved_items",
        ):
            values = audit.get(field)
            if not isinstance(values, list):
                self.errors.append(f"{path} {field} must be a list")
            elif values:
                self.errors.append(f"{path} {field} must be empty before review")

        flow_coverage = self._validate_challenge_rows(
            audit.get("contract_flows"),
            path,
            "contract_flows",
            (
                "id",
                "authority",
                "producer",
                "transport",
                "state_or_persistence",
                "consumer",
                "proof",
            ),
        )
        counterexample_coverage = self._validate_challenge_rows(
            audit.get("counterexamples"),
            path,
            "counterexamples",
            ("id", "invalid_case", "rejection_mechanism", "evidence"),
        )

        flow_risks = set(audit_policy.get("flow_required_risks", []))
        counterexample_risks = set(
            audit_policy.get("counterexample_required_risks", [])
        )
        flow_required = {
            row.get("id")
            for row in self.manifest.get("requirements", [])
            if isinstance(row, dict)
            and row.get("implementation_required") is True
            and row.get("risk") in flow_risks
        }
        counterexample_required = {
            row.get("id")
            for row in self.manifest.get("requirements", [])
            if isinstance(row, dict)
            and row.get("implementation_required") is True
            and row.get("risk") in counterexample_risks
        }
        missing_flows = sorted(
            item for item in flow_required if item and item not in flow_coverage
        )
        missing_counterexamples = sorted(
            item
            for item in counterexample_required
            if item and item not in counterexample_coverage
        )
        if missing_flows:
            self.errors.append(
                f"{path} high-risk requirements missing contract flows: "
                f"{', '.join(missing_flows)}"
            )
        if missing_counterexamples:
            self.errors.append(
                f"{path} high-risk requirements missing counterexamples: "
                f"{', '.join(missing_counterexamples)}"
            )

        self._validate_capability_challenges(audit, path)
        self._validate_pre_review_commands(audit, path)

    def _validate_challenge_rows(
        self,
        value: Any,
        path: Path,
        field: str,
        required_fields: tuple[str, ...],
    ) -> set[str]:
        if not isinstance(value, list):
            self.errors.append(f"{path} {field} must be a list")
            return set()
        row_ids: list[str] = []
        covered: set[str] = set()
        for index, row in enumerate(value, start=1):
            context = f"{path} {field}[{index}]"
            if not isinstance(row, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            for required_field in required_fields:
                self._require_string(row, required_field, path, context)
            row_id = row.get("id")
            if isinstance(row_id, str) and row_id:
                row_ids.append(row_id)
            requirement_ids = self._require_string_list(
                row.get("requirement_ids"),
                "requirement_ids",
                path,
                context=context,
                allow_empty=False,
            )
            unknown = sorted(set(requirement_ids) - self.requirement_ids)
            if unknown:
                self.errors.append(
                    f"{context} references unknown requirements: {', '.join(unknown)}"
                )
            covered.update(set(requirement_ids) & self.requirement_ids)
            if row.get("status") != "passed":
                self.errors.append(f"{context} status must be passed")
        self._check_unique_scalars(row_ids, f"{field} ids", path)
        return covered

    def _validate_capability_challenges(
        self, audit: Mapping[str, Any], path: Path
    ) -> None:
        rows = audit.get("capability_checks")
        if not isinstance(rows, list):
            self.errors.append(f"{path} capability_checks must be a list")
            return
        completed: set[tuple[str, str]] = set()
        for index, row in enumerate(rows, start=1):
            context = f"{path} capability_checks[{index}]"
            if not isinstance(row, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            capability = self._require_string(row, "capability", path, context)
            check_id = self._require_string(row, "check_id", path, context)
            self._require_string(row, "evidence", path, context)
            if row.get("status") != "passed":
                self.errors.append(f"{context} status must be passed")
            if capability and check_id:
                key = (capability, check_id)
                if key in completed:
                    self.errors.append(
                        f"{path} duplicate capability check: {capability}/{check_id}"
                    )
                completed.add(key)

        challenge_policy = self.policy.get("pre_review_challenges", {})
        if not isinstance(challenge_policy, dict):
            self.errors.append("policy pre_review_challenges must be a mapping")
            return
        applicable = ["common"]
        capabilities = self.profile.get("capabilities", [])
        if isinstance(capabilities, list):
            applicable.extend(item for item in capabilities if isinstance(item, str))
        required_checks: set[tuple[str, str]] = set()
        for capability in applicable:
            challenge_ids = challenge_policy.get(capability, [])
            if not isinstance(challenge_ids, list):
                self.errors.append(
                    f"policy pre_review_challenges.{capability} must be a list"
                )
                continue
            required_checks.update(
                (capability, check_id)
                for check_id in challenge_ids
                if isinstance(check_id, str)
            )
        missing = sorted(required_checks - completed)
        if missing:
            rendered = ", ".join(
                f"{capability}/{check_id}" for capability, check_id in missing
            )
            self.errors.append(f"{path} missing capability checks: {rendered}")

    def _validate_pre_review_commands(
        self, audit: Mapping[str, Any], path: Path
    ) -> None:
        rows = audit.get("validation_commands")
        if not isinstance(rows, list) or not rows:
            self.errors.append(f"{path} validation_commands must be a non-empty list")
            return
        for index, row in enumerate(rows, start=1):
            context = f"{path} validation_commands[{index}]"
            if not isinstance(row, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            self._require_string(row, "command", path, context)
            self._require_string(row, "evidence", path, context)
            if row.get("result") != "passed":
                self.errors.append(f"{context} result must be passed")

    def pre_review_input_fingerprint(self) -> str:
        paths = {
            self.epic_dir / name
            for name in (
                "details.md",
                "acceptance-criteria.md",
                "pdr.md",
                "system-context.md",
                "architecture.md",
                "adr.md",
                "test-strategy.md",
                "refinement-profile.yaml",
                "refinement-manifest.yaml",
                "acceptance-traceability.yaml",
            )
        }
        paths.update(self.epic_dir.glob("file-plan-story-*.yaml"))
        for artifact in self.manifest.get("artifacts", []):
            if not isinstance(artifact, dict):
                continue
            artifact_path = artifact.get("path")
            if isinstance(artifact_path, str) and artifact_path:
                paths.add(self._resolve_repo_path(artifact_path))

        digest = hashlib.sha256()
        for path in sorted(paths, key=lambda item: str(item)):
            try:
                content = path.read_bytes()
            except OSError:
                content = b"<missing>"
            try:
                label = path.resolve().relative_to(self.repo_root).as_posix()
            except ValueError:
                label = str(path.resolve())
            digest.update(label.encode("utf-8"))
            digest.update(b"\0")
            digest.update(content)
            digest.update(b"\0")
        return digest.hexdigest()

    def _validate_list_mapping_fields(
        self,
        value: Any,
        fields: tuple[str, ...],
        label: str,
        context: str,
    ) -> None:
        if not isinstance(value, dict):
            self.errors.append(f"{context} {label} must be a mapping")
            return
        for field in fields:
            if not isinstance(value.get(field), list):
                self.errors.append(f"{context} {label}.{field} must be a list")

    def _require_string_list(
        self,
        value: Any,
        field: str,
        path: Path,
        *,
        context: str | None = None,
        allow_empty: bool,
    ) -> list[str]:
        label = context or str(path)
        if not isinstance(value, list):
            self.errors.append(f"{label} {field} must be a list")
            return []
        if not value and not allow_empty:
            self.errors.append(f"{label} {field} must not be empty")
        strings = [item for item in value if isinstance(item, str) and item.strip()]
        if len(strings) != len(value):
            self.errors.append(f"{label} {field} values must be non-empty strings")
        self._check_unique_scalars(strings, field, path)
        return strings

    def _validate_non_empty_string_values(
        self, values: list[Any], field: str, context: str
    ) -> None:
        if any(not isinstance(value, str) or not value.strip() for value in values):
            self.errors.append(f"{context} {field} values must be non-empty strings")

    def _validate_findings(self, *, require_closed: bool) -> None:
        path = self.epic_dir / "refinement-findings.yaml"
        document = self._load_mapping(path, "refinement findings")
        if not document:
            return
        self._require_equal(
            document,
            "schema_version",
            self.policy.get("findings_version"),
            path,
        )
        findings_epic_id = self._require_string(document, "epic_id", path)
        profile_epic_id = self.profile.get("epic_id")
        if findings_epic_id and profile_epic_id and findings_epic_id != profile_epic_id:
            self.errors.append(
                f"{path} epic_id {findings_epic_id!r} does not match profile {profile_epic_id!r}"
            )
        review = document.get("review")
        if not isinstance(review, dict):
            self.errors.append(f"{path} review must be a mapping")
            review = {}

        risk = str(self.profile.get("risk_level", ""))
        risk_policy = self._risk_policy(risk)
        completed_roles = review.get("completed_roles")
        if not isinstance(completed_roles, list):
            self.errors.append(f"{path} review.completed_roles must be a list")
            completed_roles = []
        valid_completed_roles = {
            role for role in completed_roles if isinstance(role, str) and role.strip()
        }
        if len(valid_completed_roles) != len(completed_roles):
            self.errors.append(
                f"{path} review.completed_roles values must be non-empty strings"
            )
        required_roles = risk_policy.get("roles", [])
        if isinstance(required_roles, list):
            missing_roles = sorted(set(required_roles) - valid_completed_roles)
            if missing_roles:
                self.errors.append(
                    f"{path} missing completed review roles: {', '.join(missing_roles)}"
                )
        self._validate_review_count(
            review,
            risk_policy,
            "full_review_count",
            "minimum_full_reviews",
            "maximum_full_reviews",
            path,
        )
        self._validate_review_count(
            review,
            risk_policy,
            "targeted_verification_count",
            None,
            "maximum_targeted_verifications",
            path,
        )

        outputs = review.get("outputs")
        if not isinstance(outputs, list):
            self.errors.append(f"{path} review.outputs must be a list")
            outputs = []
        valid_outputs = [output for output in outputs if isinstance(output, str)]
        self._check_unique_scalars(valid_outputs, "review outputs", path)
        output_roles: set[str] = set()
        for output in outputs:
            if not isinstance(output, str):
                self.errors.append(f"{path} review output does not exist: {output!r}")
                continue
            output_path = self._resolve_repo_path(output)
            if not output_path.is_file():
                self.errors.append(f"{path} review output does not exist: {output!r}")
                continue
            role = self._read_review_role(output_path, path)
            if role:
                output_roles.add(role)
                if role not in valid_completed_roles:
                    self.errors.append(
                        f"{path} review output role {role!r} is not in completed_roles"
                    )
        if isinstance(required_roles, list):
            missing_output_roles = sorted(set(required_roles) - output_roles)
            if missing_output_roles:
                self.errors.append(
                    f"{path} has no review output for roles: {', '.join(missing_output_roles)}"
                )
        minimum_roles = risk_policy.get("minimum_completed_roles")
        if isinstance(minimum_roles, int) and len(output_roles) < minimum_roles:
            self.errors.append(
                f"{path} review.outputs covers {len(output_roles)} roles; "
                f"{minimum_roles} required"
            )

        findings = self._require_mapping_list(
            document, "findings", path, allow_empty=True
        )
        policy = self.policy.get("findings", {})
        severities = policy.get("severities", []) if isinstance(policy, dict) else []
        statuses = policy.get("statuses", []) if isinstance(policy, dict) else []
        categories = policy.get("categories", []) if isinstance(policy, dict) else []
        ids: list[str] = []
        fingerprints: list[str] = []
        for index, finding in enumerate(findings, start=1):
            context = f"{path} findings[{index}]"
            finding_id = self._require_string(finding, "id", path, context)
            fingerprint = self._require_string(finding, "fingerprint", path, context)
            if finding_id:
                ids.append(finding_id)
            if fingerprint:
                fingerprints.append(fingerprint)
            severity = finding.get("severity")
            status = finding.get("status")
            self._require_allowed(severity, severities, "severity", path, context)
            self._require_allowed(status, statuses, "status", path, context)
            self._require_allowed(
                finding.get("category"), categories, "category", path, context
            )
            self._require_string(finding, "evidence", path, context)
            if status in {"open", "corrected"}:
                self._require_string(finding, "required_correction", path, context)
            self._require_string(finding, "owner", path, context)
            self._require_string(finding, "closure_test", path, context)
            verification_roles = finding.get("verification_roles")
            if status in {"open", "corrected"} and (
                not isinstance(verification_roles, list) or not verification_roles
            ):
                self.errors.append(
                    f"{context} verification_roles must be a non-empty list"
                )
            if not isinstance(verification_roles, list):
                verification_roles = []
            valid_verification_roles = {
                role
                for role in verification_roles
                if isinstance(role, str) and role.strip()
            }
            if len(valid_verification_roles) != len(verification_roles):
                self.errors.append(
                    f"{context} verification_roles values must be non-empty strings"
                )
            unknown_roles = sorted(valid_verification_roles - valid_completed_roles)
            if unknown_roles:
                self.errors.append(
                    f"{context} verification_roles are not completed review roles: "
                    f"{', '.join(unknown_roles)}"
                )
            if status == "corrected":
                self._require_string(finding, "correction_evidence", path, context)
            affected = finding.get("affected_manifest_ids")
            if not isinstance(affected, list):
                self.errors.append(f"{context} affected_manifest_ids must be a list")
                affected = []
            valid_affected = {item for item in affected if isinstance(item, str)}
            if len(valid_affected) != len(affected):
                self.errors.append(
                    f"{context} affected_manifest_ids values must be strings"
                )
            unknown = sorted(valid_affected - self.requirement_ids)
            if unknown:
                self.errors.append(
                    f"{context} references unknown manifest ids: {', '.join(unknown)}"
                )
            requires_user = finding.get("requires_user")
            if not isinstance(requires_user, bool):
                self.errors.append(f"{context} requires_user must be boolean")
            if require_closed and status in {"open", "corrected"}:
                self.errors.append(f"{context} remains {status} at handoff")
        self._check_unique_scalars(ids, "finding ids", path)
        self._check_unique_scalars(fingerprints, "finding fingerprints", path)

    def _read_review_role(self, output_path: Path, findings_path: Path) -> str:
        try:
            text = output_path.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(
                f"{findings_path} cannot read review output {output_path}: {exc}"
            )
            return ""
        match = re.search(r"(?m)^REVIEW_ROLE:\s*([a-z][a-z0-9_]*)\s*$", text)
        if not match:
            self.errors.append(
                f"{findings_path} review output has no valid REVIEW_ROLE: {output_path}"
            )
            return ""
        return match.group(1)

    def _validate_review_count(
        self,
        review: Mapping[str, Any],
        policy: Mapping[str, Any],
        actual_field: str,
        minimum_field: str | None,
        maximum_field: str,
        path: Path,
    ) -> None:
        actual = review.get(actual_field)
        minimum = policy.get(minimum_field) if minimum_field else None
        maximum = policy.get(maximum_field)
        if not isinstance(actual, int) or actual < 0:
            self.errors.append(
                f"{path} review.{actual_field} must be a non-negative integer"
            )
        elif isinstance(minimum, int) and actual < minimum:
            self.errors.append(
                f"{path} review.{actual_field}={actual} is below policy minimum {minimum}"
            )
        elif isinstance(maximum, int) and actual > maximum:
            self.errors.append(
                f"{path} review.{actual_field}={actual} exceeds policy maximum {maximum}"
            )

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

    def _validate_source(self, source: Any, path: Path, context: str) -> None:
        if not isinstance(source, dict):
            self.errors.append(f"{context} source must be a mapping")
            return
        artifact = source.get("artifact")
        anchor = source.get("anchor")
        if not isinstance(artifact, str) or not artifact.strip():
            self.errors.append(f"{context} source.artifact must be a non-empty string")
        elif not self._resolve_source_path(artifact).is_file():
            self.errors.append(f"{context} source artifact does not exist: {artifact}")
        if not isinstance(anchor, str) or not anchor.strip():
            self.errors.append(f"{context} source.anchor must be a non-empty string")
        elif (
            isinstance(artifact, str) and self._resolve_source_path(artifact).is_file()
        ):
            try:
                source_text = self._resolve_source_path(artifact).read_text(
                    encoding="utf-8"
                )
            except OSError as exc:
                self.errors.append(
                    f"{context} cannot read source artifact {artifact}: {exc}"
                )
            else:
                if anchor not in source_text:
                    self.errors.append(
                        f"{context} source anchor {anchor!r} not found in {artifact}"
                    )

    def _resolve_source_path(self, value: str) -> Path:
        candidate = Path(value)
        if candidate.is_absolute():
            return candidate
        if value.startswith("docs/"):
            return self.repo_root / candidate
        return self.epic_dir / candidate

    def _resolve_repo_path(self, value: str) -> Path:
        candidate = Path(value)
        return candidate if candidate.is_absolute() else self.repo_root / candidate

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

    def _check_unique_scalars(
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


def _default_policy_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config" / "refinement-policy.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epic_dir", type=Path, help="Path to docs/epics/{epic-dir}")
    parser.add_argument("--phase", choices=PHASE_ORDER, required=True)
    parser.add_argument("--policy", type=Path, default=_default_policy_path())
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument(
        "--print-input-fingerprint",
        action="store_true",
        help="Print the current aggregate pre-review input fingerprint on success.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validator = RefinementValidator(
        epic_dir=args.epic_dir,
        phase=args.phase,
        policy_path=args.policy,
        repo_root=args.repo_root,
    )
    errors = validator.validate()
    if errors:
        print(
            f"Refinement validation failed with {len(errors)} error(s):",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.print_input_fingerprint:
        print(validator.pre_review_input_fingerprint())
        return 0
    print(f"Refinement validation passed: phase={args.phase} epic={args.epic_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
