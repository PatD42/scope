#!/usr/bin/env python3
"""Prepare and validate Scope Audit Epic artifacts from a v3 refinement handoff."""

from __future__ import annotations

import argparse
import hashlib
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
    return sorted(paths)


def _changed_paths(repo_root: Path) -> list[str]:
    if not _run_git(repo_root, "rev-parse", "--is-inside-work-tree"):
        return []
    paths = set(_run_git(repo_root, "diff", "--name-only", "HEAD"))
    paths.update(_run_git(repo_root, "ls-files", "--others", "--exclude-standard"))
    return sorted(paths)


def _is_evidence_output(path: str, epic_dir: Path, repo_root: Path) -> bool:
    try:
        epic_relative = epic_dir.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        epic_relative = ""
    normalized = Path(path).as_posix().lstrip("./")
    if normalized.startswith(("tmp_debug/", ".scope/")):
        return True
    if not epic_relative or not normalized.startswith(f"{epic_relative}/"):
        return False
    relative = normalized.removeprefix(f"{epic_relative}/")
    return (
        relative in {
            "acceptance-traceability.yaml",
            "implementation-evidence.yaml",
            "implementation-summary.md",
            "audit-findings.yaml",
            "audit-verification-matrix.yaml",
            "epic_audit.md",
        }
        or relative.startswith("reviews/")
    )


def repository_fingerprint(repo_root: Path, epic_dir: Path) -> str:
    """Hash the current source state while excluding self-changing evidence outputs."""
    digest = hashlib.sha256()
    head = _run_git(repo_root, "rev-parse", "HEAD")
    digest.update((head[0] if head else "no-git-head").encode())
    paths = _changed_paths(repo_root)
    if not paths:
        paths = [
            path.relative_to(repo_root).as_posix()
            for path in sorted(repo_root.rglob("*"))
            if path.is_file() and ".git" not in path.parts
        ]
    for value in paths:
        if _is_evidence_output(value, epic_dir, repo_root):
            continue
        path = repo_root / value
        digest.update(value.encode())
        digest.update(b"\0")
        if path.is_file():
            digest.update(path.read_bytes())
        else:
            digest.update(b"<deleted>")
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _file_sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


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


def _full_assignments(policy: Mapping[str, Any], risk: str) -> list[dict[str, str]]:
    risk_policy = policy.get("risk_review_policy", {})
    if not isinstance(risk_policy, dict):
        raise ValueError("audit policy risk_review_policy must be a mapping")
    selected = risk_policy.get(risk)
    if not isinstance(selected, dict) or not isinstance(selected.get("providers"), list):
        raise ValueError(f"audit policy has no providers for risk {risk}")
    providers = selected["providers"]
    known = set(_string_list(policy.get("review_providers")))
    if not all(isinstance(provider, str) and provider for provider in providers):
        raise ValueError(f"audit policy providers for {risk} must be non-empty strings")
    unknown = sorted(set(providers) - known)
    if unknown:
        raise ValueError(f"audit policy has unknown providers for {risk}: {', '.join(unknown)}")
    return [{"provider": provider, "mission": "semantic_core"} for provider in providers]


def _targeted_assignments(
    policy: Mapping[str, Any],
    findings: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    known = set(_string_list(policy.get("review_providers")))
    providers = {
        provider
        for finding in findings
        if finding.get("source") == "reviewer"
        for provider in _string_list(finding.get("detected_by"))
    }
    unknown = sorted(providers - known)
    if unknown:
        raise ValueError(f"targeted findings reference unknown providers: {', '.join(unknown)}")
    return [
        {"provider": provider, "mission": "semantic_core"}
        for provider in _string_list(policy.get("review_providers"))
        if provider in providers
    ]


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


class ImplementationEvidenceVerifier:
    """Verify implementation proof provenance without interpreting product behavior."""

    def __init__(
        self,
        epic_dir: Path,
        policy_path: Path,
        repo_root: Path | None = None,
        story_id: str = "",
    ) -> None:
        self.epic_dir = epic_dir.resolve()
        self.policy_path = policy_path.resolve()
        self.repo_root = (repo_root or _infer_repo_root(self.epic_dir)).resolve()
        self.story_id = story_id
        self.errors: list[str] = []
        self.current_fingerprint = repository_fingerprint(self.repo_root, self.epic_dir)
        self.current_head = (_run_git(self.repo_root, "rev-parse", "HEAD") or ["no-git-head"])[0]
        self.changed_files = set(_changed_files(self.repo_root))
        self.current_records: list[dict[str, Any]] = []

    def validate(self) -> list[str]:
        try:
            policy = _load_yaml(self.policy_path, "audit policy")
            profile = _profile(self.epic_dir)
            traceability = _traceability(self.epic_dir)
            manifest = _manifest(self.epic_dir)
            evidence = _load_yaml(
                self.epic_dir / "implementation-evidence.yaml",
                "implementation evidence",
            )
        except ValueError as exc:
            return [str(exc)]

        expected_version = policy.get("implementation_evidence_version")
        if evidence.get("schema_version") != expected_version:
            self.errors.append(
                "implementation-evidence.yaml schema_version must be "
                f"{expected_version!r}, got {evidence.get('schema_version')!r}"
            )
        try:
            epic_id = _epic_id(profile, traceability, manifest)
        except ValueError as exc:
            return [str(exc)]
        if evidence.get("epic_id") != epic_id:
            self.errors.append("implementation-evidence.yaml epic_id does not match refinement")

        repository = evidence.get("repository")
        if not isinstance(repository, dict):
            self.errors.append("implementation-evidence.yaml repository must be a mapping")
        else:
            if repository.get("head") != self.current_head:
                self.errors.append("implementation evidence HEAD does not match the current worktree")
            if repository.get("fingerprint") != self.current_fingerprint:
                self.errors.append(
                    "implementation evidence repository fingerprint does not match the current worktree"
                )

        evidence_policy = policy.get("implementation_evidence", {})
        stories = evidence.get("stories")
        if not isinstance(stories, list) or not stories:
            self.errors.append("implementation-evidence.yaml stories must be a non-empty list")
            stories = []
        selected_stories = [
            story
            for story in stories
            if isinstance(story, dict)
            and (not self.story_id or story.get("story_id") == self.story_id)
        ]
        if self.story_id and not selected_stories:
            self.errors.append(f"implementation evidence has no story {self.story_id!r}")

        all_records: list[dict[str, Any]] = []
        story_ids: list[str] = []
        claimed_files: set[str] = set()
        plans = {
            str(plan.get("story_id")): plan
            for path in sorted(self.epic_dir.glob("file-plan-story-*.yaml"))
            for plan in [_load_yaml(path, "implementation boundary plan")]
            if isinstance(plan.get("story_id"), str)
        }
        for index, story in enumerate(selected_stories, start=1):
            context = f"implementation-evidence.yaml stories[{index}]"
            story_id = story.get("story_id")
            if not isinstance(story_id, str) or not story_id:
                self.errors.append(f"{context} story_id must be a non-empty string")
            else:
                story_ids.append(story_id)
            status = story.get("status")
            allowed_statuses = _string_list(
                _mapping(evidence_policy).get("story_statuses")
            )
            if status not in allowed_statuses:
                self.errors.append(
                    f"{context} status must be one of {allowed_statuses!r}, got {status!r}"
                )
            acceptance_rows = self._string_list_required(
                story.get("acceptance_rows"), f"{context} acceptance_rows"
            )
            files_changed = self._string_list_required(
                story.get("files_changed"), f"{context} files_changed"
            )
            claimed_files.update(files_changed)
            strategy = story.get("strategy")
            classified: set[str] = set()
            if not isinstance(strategy, dict):
                self.errors.append(f"{context} strategy must be a mapping")
            else:
                for field in (
                    "inspected_paths",
                    "candidate_files_used",
                    "candidate_files_skipped",
                    "discovered_files",
                ):
                    values = self._string_list_required(
                        strategy.get(field), f"{context} strategy.{field}", allow_empty=True
                    )
                    if field in {"candidate_files_used", "discovered_files"}:
                        classified.update(values)
                selected_approach = strategy.get("selected_approach")
                if not isinstance(selected_approach, str) or not selected_approach.strip():
                    self.errors.append(
                        f"{context} strategy.selected_approach must be a non-empty string"
                    )
            unclassified = sorted(set(files_changed) - classified)
            if unclassified:
                self.errors.append(
                    f"{context} has unclassified changed files: {', '.join(unclassified)}"
                )
            for value in files_changed:
                self._require_changed_file(value, f"{context} files_changed")
            plan = plans.get(str(story_id), {})
            for forbidden in plan.get("forbidden_changes", []):
                if not isinstance(forbidden, dict):
                    continue
                forbidden_path = str(forbidden.get("path_or_surface", "")).split("#", 1)[0]
                if forbidden_path in files_changed:
                    self.errors.append(
                        f"{context} changes mechanically forbidden path: {forbidden_path}"
                    )

            remaining = self._string_list_required(
                story.get("remaining_unproven_work"),
                f"{context} remaining_unproven_work",
                allow_empty=True,
            )
            if status == "verified" and remaining:
                self.errors.append(f"{context} verified story has remaining unproven work")
            if status != "verified" and not remaining:
                self.errors.append(f"{context} non-verified story must describe unproven work")
            value_proof = story.get("value_proof")
            if status == "verified" and (
                not isinstance(value_proof, str) or not value_proof.strip()
            ):
                self.errors.append(f"{context} verified story requires value_proof")

            records = story.get("commands_run")
            if not isinstance(records, list):
                self.errors.append(f"{context} commands_run must be a list")
            else:
                all_records.extend(
                    self._validate_command_record(record, f"{context} commands_run[{record_index}]",
                                                  evidence_policy)
                    for record_index, record in enumerate(records, start=1)
                    if isinstance(record, dict)
                )
                if any(not isinstance(record, dict) for record in records):
                    self.errors.append(f"{context} commands_run entries must be mappings")
            if (
                status == "verified"
                and not acceptance_rows
                and story_id not in {"story-0", "story-00"}
            ):
                self.errors.append(f"{context} verified story requires acceptance_rows")

        if len(story_ids) != len(set(story_ids)):
            self.errors.append("implementation evidence has duplicate story IDs")
        if not self.story_id and _run_git(
            self.repo_root, "rev-parse", "--is-inside-work-tree"
        ):
            actual_files = {
                value
                for value in _changed_files(self.repo_root)
                if not _is_evidence_output(value, self.epic_dir, self.repo_root)
            }
            unexplained = sorted(actual_files - claimed_files)
            if unexplained:
                self.errors.append(
                    "implementation evidence does not classify changed files: "
                    + ", ".join(unexplained)
                )

        epic_level = evidence.get("epic_level")
        if not isinstance(epic_level, dict):
            self.errors.append("implementation-evidence.yaml epic_level must be a mapping")
            epic_level = {}
        epic_records = epic_level.get("commands_run")
        if not isinstance(epic_records, list):
            self.errors.append("implementation-evidence.yaml epic_level.commands_run must be a list")
            epic_records = []
        for index, record in enumerate(epic_records, start=1):
            if not isinstance(record, dict):
                self.errors.append(
                    f"implementation-evidence.yaml epic_level.commands_run[{index}] must be a mapping"
                )
                continue
            all_records.append(
                self._validate_command_record(
                    record,
                    f"implementation-evidence.yaml epic_level.commands_run[{index}]",
                    evidence_policy,
                )
            )

        self.current_records = [
            record
            for record in all_records
            if record.get("repository_fingerprint") == self.current_fingerprint
            and record.get("status") == "pass"
        ]
        self._validate_traceability(traceability, manifest, selected_stories)

        if not self.story_id:
            if evidence.get("audit_ready") is not True:
                self.errors.append("implementation-evidence.yaml audit_ready must be true")
            if any(
                isinstance(story, dict) and story.get("status") != "verified"
                for story in stories
            ):
                self.errors.append("audit_ready requires every story to be verified")
            blocked_rows = epic_level.get("blocked_rows")
            if not isinstance(blocked_rows, list) or blocked_rows:
                self.errors.append("audit_ready requires epic_level.blocked_rows to be an empty list")
        return self.errors

    def _validate_command_record(
        self,
        record: Mapping[str, Any],
        context: str,
        evidence_policy: Mapping[str, Any],
    ) -> dict[str, Any]:
        value = dict(record)
        for field in ("id", "kind", "status", "cwd", "output", "output_sha256",
                      "started_at", "completed_at", "repository_fingerprint"):
            if not isinstance(value.get(field), str) or not str(value[field]).strip():
                self.errors.append(f"{context} {field} must be a non-empty string")
        kind = value.get("kind")
        allowed_kinds = _string_list(evidence_policy.get("command_kinds"))
        if kind not in allowed_kinds:
            self.errors.append(f"{context} kind must be one of {allowed_kinds!r}")
        status = value.get("status")
        allowed_statuses = _string_list(evidence_policy.get("command_statuses"))
        if status not in allowed_statuses:
            self.errors.append(f"{context} status must be one of {allowed_statuses!r}")
        if kind == "inspection":
            if not isinstance(value.get("inspection"), str) or not value["inspection"].strip():
                self.errors.append(f"{context} inspection must be a non-empty string")
        elif not isinstance(value.get("command"), str) or not value["command"].strip():
            self.errors.append(f"{context} command must be a non-empty string")

        exit_code = value.get("exit_code")
        if kind == "inspection":
            if exit_code is not None:
                self.errors.append(f"{context} inspection exit_code must be null")
        elif not isinstance(exit_code, int):
            self.errors.append(f"{context} exit_code must be an integer")
        elif status == "pass" and exit_code != 0:
            self.errors.append(f"{context} passing command must have exit_code 0")
        elif status == "fail" and exit_code == 0:
            self.errors.append(f"{context} failing command must have non-zero exit_code")

        output = value.get("output")
        if isinstance(output, str) and output:
            output_path = self._resolve_path(output)
            if not output_path.is_file():
                self.errors.append(f"{context} output does not exist: {output}")
            elif value.get("output_sha256") != _file_sha256(output_path):
                self.errors.append(f"{context} output_sha256 does not match {output}")
        self._string_list_required(
            value.get("acceptance_rows"), f"{context} acceptance_rows", allow_empty=True
        )
        self._string_list_required(
            value.get("proof_obligation_ids"),
            f"{context} proof_obligation_ids",
            allow_empty=True,
        )
        test_ids = self._string_list_required(
            value.get("test_ids"), f"{context} test_ids", allow_empty=True
        )
        for test_id in test_ids:
            test_path = test_id.split("::", 1)[0]
            self._require_repo_file(test_path, f"{context} test_ids")
        if kind in {"test", "regression"}:
            summary = value.get("test_summary")
            if not isinstance(summary, dict):
                self.errors.append(f"{context} test_summary must be a mapping")
            else:
                for field in ("passed", "failed", "errors", "skipped"):
                    count = summary.get(field)
                    if not isinstance(count, int) or count < 0:
                        self.errors.append(
                            f"{context} test_summary.{field} must be a non-negative integer"
                        )
                if status == "pass" and (
                    summary.get("failed", 0) != 0 or summary.get("errors", 0) != 0
                ):
                    self.errors.append(
                        f"{context} passing test command reports failures or errors"
                    )
        return value

    def _validate_traceability(
        self,
        traceability: Mapping[str, Any],
        manifest: Mapping[str, Any],
        stories: Sequence[Mapping[str, Any]],
    ) -> None:
        requirements = _requirements_by_id(manifest)
        story_rows = {
            row_id
            for story in stories
            for row_id in _string_list(story.get("acceptance_rows"))
        }
        records_by_row: dict[str, list[dict[str, Any]]] = {}
        for record in self.current_records:
            for row_id in _string_list(record.get("acceptance_rows")):
                records_by_row.setdefault(row_id, []).append(record)
        rows = traceability.get("acceptance_items")
        if not isinstance(rows, list):
            self.errors.append("acceptance-traceability.yaml acceptance_items must be a list")
            return
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_id = str(row.get("id", ""))
            if self.story_id and row_id not in story_rows:
                continue
            if requirements.get(row_id, {}).get("implementation_required") is False:
                continue
            context = f"traceability row {row_id}"
            if row.get("status") != "verified":
                self.errors.append(f"{context} status must be verified")
            if row_id not in story_rows:
                self.errors.append(f"{context} is not mapped to implementation evidence")
            implementation = _mapping(row.get("implementation"))
            actual_files = _string_list(implementation.get("actual_files"))
            if not actual_files:
                self.errors.append(f"{context} has no actual implementation files")
            for value in actual_files:
                self._require_repo_file(value, f"{context} actual_files")
            tests = _mapping(row.get("tests"))
            actual_tests = _string_list(tests.get("actual_tests"))
            if not actual_tests:
                self.errors.append(f"{context} has no actual tests")
            for value in actual_tests:
                self._require_repo_file(value.split("::", 1)[0], f"{context} actual_tests")
            current = records_by_row.get(row_id, [])
            current_test_ids = {
                test_id
                for record in current
                if record.get("kind") in {"test", "regression"}
                for test_id in _string_list(record.get("test_ids"))
            }
            missing_tests = sorted(set(actual_tests) - current_test_ids)
            if missing_tests:
                self.errors.append(
                    f"{context} actual tests lack current passing proof: {', '.join(missing_tests)}"
                )
            proof_ids = set(_string_list(row.get("proof_obligation_ids")))
            current_proofs = {
                proof_id
                for record in current
                for proof_id in _string_list(record.get("proof_obligation_ids"))
            }
            missing_proofs = sorted(proof_ids - current_proofs)
            if missing_proofs:
                self.errors.append(
                    f"{context} proof obligations lack current passing evidence: "
                    + ", ".join(missing_proofs)
                )
            runtime = _mapping(row.get("runtime_evidence"))
            if runtime.get("required") is True:
                runtime_records = [
                    record for record in current if record.get("kind") == "runtime"
                ]
                commands = set(_string_list(runtime.get("commands")))
                evidence = set(_string_list(runtime.get("evidence")))
                actual_commands = {
                    str(record.get("command", "")) for record in runtime_records
                }
                actual_evidence = {
                    str(record.get("output", "")) for record in runtime_records
                }
                if not commands or not commands.issubset(actual_commands):
                    self.errors.append(f"{context} runtime commands lack current passing proof")
                if not evidence or not evidence.issubset(actual_evidence):
                    self.errors.append(f"{context} runtime evidence lacks current passing proof")

    def _string_list_required(
        self,
        value: Any,
        context: str,
        *,
        allow_empty: bool = False,
    ) -> list[str]:
        if not isinstance(value, list):
            self.errors.append(f"{context} must be a list")
            return []
        result = [item for item in value if isinstance(item, str) and item]
        if len(result) != len(value):
            self.errors.append(f"{context} values must be non-empty strings")
        if not allow_empty and not result:
            self.errors.append(f"{context} must not be empty")
        return result

    def _require_repo_file(self, value: str, context: str) -> None:
        if not self._resolve_path(value).is_file():
            self.errors.append(f"{context} path does not exist: {value}")

    def _require_changed_file(self, value: str, context: str) -> None:
        if not self._resolve_path(value).is_file() and value not in self.changed_files:
            self.errors.append(f"{context} path does not exist or identify a deletion: {value}")

    def _resolve_path(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else self.repo_root / path


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
                "status": "ready",
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


def _boundary_gates(
    epic_dir: Path,
    scoped_rows: set[str],
    manifest: Mapping[str, Any],
    current_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    requirements = _requirements_by_id(manifest)
    commands: list[tuple[str, str, list[str], bool]] = []
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
            command = proof.get("command")
            if isinstance(command, str) and command.strip():
                requires_fresh = proof.get("freshness") == "fresh" or any(
                    requirements.get(row_id, {}).get("risk") == "critical"
                    for row_id in acceptance_rows
                )
                commands.append(
                    (
                        str(proof.get("id", "boundary-proof")),
                        command.strip(),
                        sorted(acceptance_rows),
                        requires_fresh,
                    )
                )

    for record in current_records:
        if record.get("kind") != "regression":
            continue
        command = record.get("command")
        if isinstance(command, str) and command:
            commands.append(
                (
                    str(record.get("id", "epic-regression")),
                    command,
                    _string_list(record.get("acceptance_rows")),
                    False,
                )
            )

    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_id, command, acceptance_rows, requires_fresh in commands:
        if command in seen:
            continue
        seen.add(command)
        reusable = next(
            (
                record
                for record in current_records
                if record.get("command") == command and record.get("status") == "pass"
            ),
            None,
        )
        reused = reusable is not None and not requires_fresh
        unique.append(
            {
                "id": f"gate-{len(unique) + 1:03d}",
                "source": source_id,
                "command": command,
                "acceptance_rows": acceptance_rows,
                "freshness": "fresh" if requires_fresh else "reusable",
                "reused": reused,
                "status": "pass" if reused else "pending",
                "evidence": [str(reusable.get("output"))] if reused else [],
                "reason": "Reused fingerprint-matched implementation evidence."
                if reused
                else "",
            }
        )
    return unique


def _existing_attempts(
    epic_dir: Path,
    cycle_id: str,
    mode: str,
    attempt_version: int,
) -> int:
    count = 0
    for path in (epic_dir / "reviews").glob("audit-*/audit-attempt.yaml"):
        try:
            attempt = _load_yaml(path, "audit attempt")
        except ValueError:
            continue
        if (
            attempt.get("schema_version") == attempt_version
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
    evidence_verifier = ImplementationEvidenceVerifier(
        epic_dir,
        args.policy,
        repo_root,
    )
    evidence_errors = evidence_verifier.validate()
    if evidence_errors:
        raise ValueError(
            "implementation evidence is not audit-ready:\n- "
            + "\n- ".join(evidence_errors)
        )

    allowed_modes = policy.get("allowed_modes", [])
    if args.mode not in allowed_modes:
        raise ValueError(f"unsupported audit mode {args.mode!r}")
    budget = policy.get("review_budget", {})
    budget_field = "maximum_full_attempts" if args.mode == "full" else "maximum_targeted_attempts"
    maximum = budget.get(budget_field) if isinstance(budget, dict) else None
    existing = _existing_attempts(
        epic_dir,
        args.cycle_id,
        args.mode,
        int(policy.get("attempt_version", 0)),
    )
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
        assignments = _full_assignments(policy, risk)
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
        assignments = _targeted_assignments(
            policy,
            [findings_by_id[finding_id] for finding_id in finding_ids],
        )

    risk_policy = _mapping(_mapping(policy.get("risk_review_policy")).get(risk))
    capability_focus = capabilities if risk_policy.get("capability_focus") is True else []

    attempt = {
        "schema_version": policy.get("attempt_version"),
        "epic_id": epic_id,
        "attempt_id": attempt_id,
        "cycle_id": args.cycle_id,
        "mode": args.mode,
        "reason": args.reason or ("complete implementation audit" if args.mode == "full" else "finding verification"),
        "risk_level": risk,
        "capabilities": capabilities,
        "capability_focus": capability_focus,
        "repository_fingerprint": evidence_verifier.current_fingerprint,
        "scope": {
            "acceptance_rows": scoped_rows,
            "finding_ids": finding_ids,
            "sibling_surfaces": list(dict.fromkeys(args.sibling_surface)),
        },
        "changed_files": _changed_files(repo_root),
        "gates": _boundary_gates(
            epic_dir,
            set(scoped_rows),
            manifest,
            evidence_verifier.current_records,
        ),
        "review": {
            "required_assignments": assignments,
            "outputs": [],
            "skipped_reason": (
                "Targeted findings require deterministic closure only."
                if args.mode == "targeted" and not assignments
                else ""
            ),
        },
        "metrics": {},
        "status": "pending",
        "decision_reason": "",
    }

    attempt_dir.mkdir(parents=True, exist_ok=False)
    _write_yaml(attempt_dir / "audit-attempt.yaml", attempt)
    _write_yaml(attempt_dir / "audit-verification-matrix.yaml", matrix)
    packet = {
        "schema_version": 1,
        "epic_id": epic_id,
        "attempt_id": attempt_id,
        "mode": args.mode,
        "risk_level": risk,
        "capability_focus": capability_focus,
        "scope": attempt["scope"],
        "changed_files": attempt["changed_files"],
        "artifacts": [
            str(path.relative_to(repo_root))
            for path in (
                epic_dir / "refinement-profile.yaml",
                epic_dir / "refinement-manifest.yaml",
                epic_dir / "acceptance-criteria.md",
                epic_dir / "design.md",
                epic_dir / "acceptance-traceability.yaml",
                epic_dir / "implementation-evidence.yaml",
                attempt_dir / "audit-attempt.yaml",
                attempt_dir / "audit-verification-matrix.yaml",
            )
        ],
        "deterministic_guarantees": [
            "implementation evidence schema and audit readiness are valid",
            "cited implementation, test, and evidence paths exist",
            "proof output hashes and statuses are coherent",
            "traceability rows have current fingerprint-matched proof",
            "changed implementation files are classified by story",
        ],
    }
    _write_yaml(attempt_dir / "review-packet.yaml", packet)
    if not (epic_dir / "audit-findings.yaml").is_file():
        _write_yaml(epic_dir / "audit-findings.yaml", findings)
    print(attempt_dir.relative_to(repo_root))
    return 0


def _count_by(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _attempt_metrics(
    attempt: Mapping[str, Any],
    findings: Mapping[str, Any],
) -> dict[str, Any]:
    attempt_id = attempt.get("attempt_id")
    rows = [
        finding
        for finding in findings.get("findings", [])
        if isinstance(finding, dict) and finding.get("first_seen_attempt") == attempt_id
    ]
    return {
        "new_findings": {
            "total": len(rows),
            "by_severity": _count_by(
                str(finding.get("severity")) for finding in rows
            ),
            "by_category": _count_by(
                str(finding.get("category")) for finding in rows
            ),
            "by_source": _count_by(
                str(finding.get("source")) for finding in rows
            ),
            "by_provider": _count_by(
                provider
                for finding in rows
                for provider in set(_string_list(finding.get("detected_by")))
            ),
        },
        "targeted_verification_required": any(
            finding.get("disposition") == "remediation_required"
            and finding.get("status") not in {"verified", "accepted_risk", "rejected"}
            for finding in rows
        ),
    }


def record_metrics(args: argparse.Namespace) -> int:
    attempt_path = args.attempt_dir.resolve() / "audit-attempt.yaml"
    attempt = _load_yaml(attempt_path, "audit attempt")
    findings = _load_yaml(args.epic_dir.resolve() / "audit-findings.yaml", "audit findings")
    attempt["metrics"] = _attempt_metrics(attempt, findings)
    _write_yaml(attempt_path, attempt)
    print(f"Audit metrics recorded: attempt={attempt.get('attempt_id')}")
    return 0


def verify_evidence(args: argparse.Namespace) -> int:
    verifier = ImplementationEvidenceVerifier(
        args.epic_dir,
        args.policy,
        args.repo_root,
        args.story,
    )
    errors = verifier.validate()
    if errors:
        print(
            f"Implementation evidence verification failed with {len(errors)} error(s):",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    scope = f"story={args.story}" if args.story else "audit-ready handoff"
    print(
        "Implementation evidence verification passed: "
        f"{scope} fingerprint={verifier.current_fingerprint}"
    )
    return 0


def print_fingerprint(args: argparse.Namespace) -> int:
    epic_dir = args.epic_dir.resolve()
    repo_root = (args.repo_root or _infer_repo_root(epic_dir)).resolve()
    print(repository_fingerprint(repo_root, epic_dir))
    return 0


class AuditValidator:
    """Validate one prepared Audit Epic v3 attempt."""

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
        evidence_errors = ImplementationEvidenceVerifier(
            self.epic_dir,
            self.policy_path,
            self.repo_root,
        ).validate()
        self.errors.extend(
            f"implementation evidence: {error}" for error in evidence_errors
        )
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
        for field in ("capabilities", "capability_focus", "changed_files"):
            self._require_string_list(self.attempt.get(field), field, path)
        self._require_string(self.attempt, "repository_fingerprint", path)
        self._require_string(self.attempt, "decision_reason", path, allow_empty=True)
        if not isinstance(self.attempt.get("metrics"), dict):
            self.errors.append(f"{path} metrics must be a mapping")
        packet = self.attempt_dir / "review-packet.yaml"
        if not packet.is_file():
            self.errors.append(f"missing review packet: {packet}")

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
            sources = (
                finding_policy.get("sources", [])
                if isinstance(finding_policy, dict)
                else []
            )
            self._require_allowed(finding.get("source"), sources, "source", path, context)
            for field in ("title", "impact", "owner", "closure_test"):
                self._require_string(finding, field, path, context=context)
            for field in (
                "evidence",
                "affected_acceptance_ids",
                "affected_files",
                "detected_by",
            ):
                values = self._require_string_list(finding.get(field), field, path, context)
                if field == "affected_acceptance_ids":
                    unknown = sorted(set(values) - self.row_ids)
                    if unknown:
                        self.errors.append(
                            f"{context} references unknown acceptance rows: {', '.join(unknown)}"
                        )
                if field == "detected_by":
                    unknown = sorted(
                        set(values) - set(_string_list(self.policy.get("review_providers")))
                    )
                    if unknown:
                        self.errors.append(
                            f"{context} references unknown providers: {', '.join(unknown)}"
                        )
            if not finding.get("evidence"):
                self.errors.append(f"{context} evidence must not be empty")
            if finding.get("source") == "reviewer" and not finding.get("detected_by"):
                self.errors.append(f"{context} reviewer finding requires detected_by")
            if finding.get("source") == "deterministic" and finding.get("detected_by"):
                self.errors.append(f"{context} deterministic finding must not list providers")
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
            if self.phase == "complete" and row.get("status") == "ready":
                self.errors.append(f"matrix row {row_id} remains ready")

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
            self._require_string_list(
                gate.get("acceptance_rows"), "acceptance_rows", path, context
            )
            self._require_allowed(
                gate.get("freshness"),
                ["reusable", "fresh"],
                "freshness",
                path,
                context,
            )
            if not isinstance(gate.get("reused"), bool):
                self.errors.append(f"{context} reused must be boolean")
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
            if gate.get("reused") is True and status != "pass":
                self.errors.append(f"{context} reused gate must pass")
        self._check_unique(gate_ids, "gate ids", path)

    def _validate_reviews(self) -> None:
        path = self.attempt_dir / "audit-attempt.yaml"
        review = self.attempt.get("review")
        if not isinstance(review, dict):
            self.errors.append(f"{path} review must be a mapping")
            return
        required = review.get("required_assignments")
        if not isinstance(required, list):
            self.errors.append(f"{path} review.required_assignments must be a list")
            required = []
        required_keys = self._validate_assignments(required, "review.required_assignments", path)
        if self.attempt.get("mode") == "full":
            expected = _full_assignments(
                self.policy,
                str(self.attempt.get("risk_level", "")),
            )
        else:
            finding_ids = set(
                _string_list(_mapping(self.attempt.get("scope")).get("finding_ids"))
            )
            selected = [
                finding
                for finding in self.findings.get("findings", [])
                if isinstance(finding, dict) and finding.get("id") in finding_ids
            ]
            expected = _targeted_assignments(self.policy, selected)
        expected_keys = {
            (assignment["provider"], assignment["mission"]) for assignment in expected
        }
        if required_keys != expected_keys:
            self.errors.append(
                f"{path} review.required_assignments do not match policy-selected assignments"
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
        output_keys: list[tuple[str, str]] = []
        for index, output in enumerate(outputs, start=1):
            context = f"{path} review.outputs[{index}]"
            if not isinstance(output, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            provider = self._require_string(output, "provider", path, context=context)
            mission = self._require_string(output, "mission", path, context=context)
            output_path = self._require_string(output, "path", path, context=context)
            metadata_path = self._require_string(
                output, "metadata_path", path, context=context
            )
            if provider and mission:
                output_keys.append((provider, mission))
            if output_path:
                resolved = self._resolve_path(output_path)
                if not resolved.is_file():
                    self.errors.append(f"{context} output file does not exist: {output_path}")
                else:
                    self._validate_review_output(
                        resolved, provider, mission, context
                    )
            if metadata_path and not self._resolve_path(metadata_path).is_file():
                self.errors.append(
                    f"{context} metadata file does not exist: {metadata_path}"
                )
        if len(output_keys) != len(set(output_keys)):
            self.errors.append(f"{path} duplicate review output assignments")
        missing_outputs = sorted(required_keys - set(output_keys))
        if missing_outputs:
            formatted = ", ".join(f"{provider}/{mission}" for provider, mission in missing_outputs)
            self.errors.append(f"{path} has no output for assignments: {formatted}")

    def _validate_assignments(
        self,
        assignments: Sequence[Any],
        field: str,
        path: Path,
    ) -> set[tuple[str, str]]:
        providers = set(_string_list(self.policy.get("review_providers")))
        missions = set(_string_list(self.policy.get("review_missions")))
        keys: list[tuple[str, str]] = []
        for index, assignment in enumerate(assignments, start=1):
            context = f"{path} {field}[{index}]"
            if not isinstance(assignment, dict):
                self.errors.append(f"{context} must be a mapping")
                continue
            provider = assignment.get("provider")
            mission = assignment.get("mission")
            if provider not in providers:
                self.errors.append(f"{context} has unknown provider {provider!r}")
            if mission not in missions:
                self.errors.append(f"{context} has unknown mission {mission!r}")
            if isinstance(provider, str) and isinstance(mission, str):
                keys.append((provider, mission))
        if len(keys) != len(set(keys)):
            self.errors.append(f"{path} duplicate {field}")
        return set(keys)

    def _validate_review_output(
        self,
        output_path: Path,
        expected_provider: str,
        expected_mission: str,
        context: str,
    ) -> None:
        try:
            text = output_path.read_text(encoding="utf-8")
        except OSError as exc:
            self.errors.append(f"{context} cannot read review output: {exc}")
            return
        provider = re.search(r"(?m)^AUDIT_PROVIDER:\s*([a-z][a-z0-9_]*)\s*$", text)
        if not provider:
            self.errors.append(f"{context} output has no valid AUDIT_PROVIDER")
        elif expected_provider and provider.group(1) != expected_provider:
            self.errors.append(
                f"{context} declares AUDIT_PROVIDER {provider.group(1)!r}, "
                f"expected {expected_provider!r}"
            )
        mission = re.search(r"(?m)^AUDIT_MISSION:\s*([a-z][a-z0-9_]*)\s*$", text)
        if not mission:
            self.errors.append(f"{context} output has no valid AUDIT_MISSION")
        elif expected_mission and mission.group(1) != expected_mission:
            self.errors.append(
                f"{context} declares AUDIT_MISSION {mission.group(1)!r}, "
                f"expected {expected_mission!r}"
            )
        decision = re.search(r"(?m)^DECISION:\s*([a-z][a-z0-9_]*)\s*$", text)
        allowed = self.policy.get("review_decisions", [])
        if not decision:
            self.errors.append(f"{context} output has no valid DECISION")
        elif not isinstance(allowed, list) or decision.group(1) not in allowed:
            self.errors.append(
                f"{context} declares unsupported DECISION {decision.group(1)!r}"
            )
        covered = re.search(r"(?m)^COVERED_ACCEPTANCE_IDS:\s*(\[.*\])\s*$", text)
        if not covered:
            self.errors.append(f"{context} output has no COVERED_ACCEPTANCE_IDS")
        else:
            try:
                values = yaml.safe_load(covered.group(1))
            except yaml.YAMLError:
                values = None
            if not isinstance(values, list) or not all(
                isinstance(value, str) and value for value in values
            ):
                self.errors.append(f"{context} COVERED_ACCEPTANCE_IDS must be a string list")
            else:
                missing = sorted(self.scoped_rows - set(values))
                if missing:
                    self.errors.append(
                        f"{context} did not cover acceptance rows: {', '.join(missing)}"
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
        expected_metrics = _attempt_metrics(self.attempt, self.findings)
        if self.attempt.get("metrics") != expected_metrics:
            self.errors.append(
                f"{attempt_path} metrics do not match mechanically derived finding counts"
            )
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
            review = _mapping(self.attempt.get("review"))
            if review.get("skipped_reason") and review.get("required_assignments"):
                self.errors.append("PASS cannot skip required review assignments")
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
    prepare_parser.add_argument("--cycle-id", default="audit-v3")
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

    evidence_parser = subparsers.add_parser(
        "verify-evidence",
        help="Verify implementation evidence provenance",
    )
    evidence_parser.add_argument("epic_dir", type=Path)
    evidence_parser.add_argument("--repo-root", type=Path)
    evidence_parser.add_argument("--policy", type=Path, default=_default_policy_path())
    evidence_parser.add_argument("--story", default="")
    evidence_parser.set_defaults(handler=verify_evidence)

    fingerprint_parser = subparsers.add_parser(
        "fingerprint",
        help="Print the current repository-state fingerprint",
    )
    fingerprint_parser.add_argument("epic_dir", type=Path)
    fingerprint_parser.add_argument("--repo-root", type=Path)
    fingerprint_parser.set_defaults(handler=print_fingerprint)

    metrics_parser = subparsers.add_parser(
        "record-metrics",
        help="Record mechanically derived finding metrics for an attempt",
    )
    metrics_parser.add_argument("epic_dir", type=Path)
    metrics_parser.add_argument("attempt_dir", type=Path)
    metrics_parser.set_defaults(handler=record_metrics)
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
