#!/usr/bin/env python3
"""Merge one exact dependency commit authorized by a lean Scope handoff."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path
import re
import sys
from typing import Any

import yaml

SCRIPT_DIRECTORY = str(Path(__file__).resolve().parent)
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)
import scope_git  # noqa: E402


ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
COMMIT_PATTERN = re.compile(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})")


class MergeError(ValueError):
    """Raised when the requested dependency merge is not exactly authorized."""


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    value: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in value:
            raise MergeError(f"duplicate YAML key: {key!r}")
        value[key] = loader.construct_object(value_node, deep=deep)
    return value


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise MergeError(f"missing or symlinked {label}: {path}")
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise MergeError(f"invalid {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MergeError(f"{label} must be a YAML mapping: {path}")
    return value


def _authorized_commit(
    manifest: Mapping[str, Any], dependency_epic_id: str
) -> str:
    dependencies = manifest.get("dependencies", [])
    if not isinstance(dependencies, list):
        raise MergeError("delivery-manifest.yaml dependencies must be a list")
    matches = [
        row
        for row in dependencies
        if isinstance(row, Mapping)
        and isinstance(row.get("epic_id"), str)
        and row["epic_id"].casefold() == dependency_epic_id.casefold()
    ]
    if len(matches) != 1:
        raise MergeError(
            f"delivery manifest must contain exactly one pin for {dependency_epic_id}"
        )
    commit = matches[0].get("commit")
    if not isinstance(commit, str) or COMMIT_PATTERN.fullmatch(commit) is None:
        raise MergeError("delivery manifest dependency commit must be a full object ID")
    return commit.lower()


def merge_dependency(
    run_path: Path,
    epic_dir: Path,
    dependency_epic_id: str,
    dependency_commit: str,
) -> str:
    if ID_PATTERN.fullmatch(dependency_epic_id) is None:
        raise MergeError("dependency epic ID is invalid")
    if COMMIT_PATTERN.fullmatch(dependency_commit) is None:
        raise MergeError("dependency commit must be a full object ID")

    if run_path.is_symlink():
        raise MergeError("Scope run must not be a symlink")
    resolved_run = run_path.resolve(strict=True)
    run = _load_yaml(resolved_run, "Scope run")
    if run.get("schema_version") != 2 or run.get("command") != "implement":
        raise MergeError("dependency merge requires a lean implement run")
    if run.get("active_job") is not None:
        raise MergeError("dependency merge refused while a worker is active")
    completed_jobs = run.get("completed_jobs")
    if not isinstance(completed_jobs, list) or completed_jobs:
        raise MergeError("dependency merge must precede implementation worker jobs")

    working_value = run.get("working_root")
    repository_value = run.get("repository_root")
    if not isinstance(working_value, str) or not isinstance(repository_value, str):
        raise MergeError("Scope run roots are invalid")
    working_root = Path(working_value).resolve(strict=True)
    repository_root = Path(repository_value).resolve(strict=True)
    expected_run = (
        repository_root
        / "tmp_debug"
        / "scope-runs"
        / str(run.get("epic_id"))
        / "implement"
        / "run.yaml"
    )
    if resolved_run != expected_run:
        raise MergeError("Scope run path is not canonical for this implement run")
    try:
        scope_git.require_linked_worktree(repository_root, working_root)
    except scope_git.GitError as exc:
        raise MergeError(str(exc)) from exc

    selected_epic = epic_dir.resolve(strict=True)
    if selected_epic.parent != working_root / "docs" / "epics":
        raise MergeError("epic directory is not a direct child of docs/epics")
    epic_id = run.get("epic_id")
    if not isinstance(epic_id, str) or ID_PATTERN.fullmatch(epic_id) is None:
        raise MergeError("Scope run epic_id is invalid")
    expected_branch = f"epic/{epic_id}"
    if scope_git.git(working_root, "symbolic-ref", "--short", "HEAD") != expected_branch:
        raise MergeError(f"implement worktree must be on branch {expected_branch}")
    manifest = _load_yaml(selected_epic / "delivery-manifest.yaml", "delivery manifest")
    if not isinstance(manifest.get("epic_id"), str) or manifest["epic_id"].casefold() != epic_id.casefold():
        raise MergeError("delivery manifest epic_id does not match the Scope run")
    pinned = _authorized_commit(manifest, dependency_epic_id)
    if pinned != dependency_commit.lower():
        raise MergeError("dependency commit does not match the delivery manifest pin")

    try:
        with scope_git.mutation_locks([working_root]):
            if scope_git.status(working_root):
                raise MergeError("dependency merge requires a clean worktree and index")
            if scope_git.git(working_root, "cat-file", "-t", dependency_commit) != "commit":
                raise MergeError("dependency pin is not a local commit object")
            ancestry = scope_git.run(
                ["git", "merge-base", "--is-ancestor", dependency_commit, "HEAD"],
                working_root,
            )
            if ancestry.returncode == 0:
                return "already_integrated"
            if ancestry.returncode != 1:
                raise MergeError("cannot determine dependency ancestry")
            label = (
                f"merge({epic_id}): integrate {dependency_epic_id} implementation baseline"
            )
            return scope_git.merge_exact(
                working_root,
                dependency_commit,
                scope_git.head(working_root),
                label,
            )
    except scope_git.GitError as exc:
        if "busy" in str(exc):
            raise MergeError("working root is busy with another Scope mutation") from exc
        if "clean" in str(exc):
            raise MergeError("dependency merge requires a clean worktree and index")
        raise MergeError(str(exc)) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--epic-dir", type=Path, required=True)
    parser.add_argument("--dependency-epic-id", required=True)
    parser.add_argument("--dependency-commit", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = merge_dependency(
            args.run,
            args.epic_dir,
            args.dependency_epic_id,
            args.dependency_commit,
        )
    except (MergeError, OSError, scope_git.GitError) as exc:
        print(f"Scope dependency merge failed: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
