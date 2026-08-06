"""Shared CodeGraph 1.5 lifecycle and prompt support for Scope agents."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
from typing import Any, Mapping, Sequence

import yaml


KNOWN_QUERY_COMMANDS = {
    "status",
    "query",
    "explore",
    "node",
    "files",
    "callers",
    "callees",
    "impact",
    "affected",
}
VERSION_PATTERN = re.compile(r"(?<!\d)(\d+)\.(\d+)\.(\d+)(?!\d)")


class CodeGraphPolicyError(ValueError):
    """Raised when Scope's installed CodeGraph policy is invalid."""


def load_policy(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CodeGraphPolicyError(f"missing CodeGraph policy: {path}")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise CodeGraphPolicyError(f"invalid CodeGraph policy {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CodeGraphPolicyError("CodeGraph policy must be a mapping")
    validate_policy(value)
    return value


def _non_empty_strings(value: Any, field: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise CodeGraphPolicyError(f"CodeGraph {field} must be non-empty strings")
    return list(value)


def _version(value: Any, field: str) -> tuple[int, int, int]:
    if not isinstance(value, str):
        raise CodeGraphPolicyError(f"CodeGraph {field} must be a semantic version")
    match = VERSION_PATTERN.search(value)
    if match is None:
        raise CodeGraphPolicyError(f"CodeGraph {field} must be a semantic version")
    return tuple(int(part) for part in match.groups())


def validate_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("schema_version") != 1:
        raise CodeGraphPolicyError("CodeGraph policy schema_version must be 1")
    if not isinstance(policy.get("executable"), str) or not policy["executable"]:
        raise CodeGraphPolicyError("CodeGraph executable must be non-empty")
    _version(policy.get("minimum_version"), "minimum_version")
    index_directory = policy.get("index_directory")
    if (
        not isinstance(index_directory, str)
        or not index_directory
        or Path(index_directory).is_absolute()
        or len(Path(index_directory).parts) != 1
        or index_directory in {".", ".."}
    ):
        raise CodeGraphPolicyError("CodeGraph index_directory must be one relative path component")
    for field in ("initialize_if_missing", "sync_on_prepare"):
        if not isinstance(policy.get(field), bool):
            raise CodeGraphPolicyError(f"CodeGraph {field} must be boolean")
    timeout = policy.get("timeout_seconds")
    if not isinstance(timeout, int) or timeout <= 0:
        raise CodeGraphPolicyError("CodeGraph timeout_seconds must be a positive integer")
    roles = _non_empty_strings(policy.get("worker_roles"), "worker_roles")
    if len(set(roles)) != len(roles):
        raise CodeGraphPolicyError("CodeGraph worker_roles must be unique")
    commands = _non_empty_strings(policy.get("query_commands"), "query_commands")
    if len(set(commands)) != len(commands) or not set(commands) <= KNOWN_QUERY_COMMANDS:
        raise CodeGraphPolicyError("CodeGraph query_commands contain duplicates or mutating commands")
    max_files = policy.get("explore_max_files")
    if not isinstance(max_files, int) or max_files <= 0:
        raise CodeGraphPolicyError("CodeGraph explore_max_files must be a positive integer")
    affected = policy.get("affected")
    if not isinstance(affected, dict):
        raise CodeGraphPolicyError("CodeGraph affected must be a mapping")
    depth = affected.get("depth")
    if not isinstance(depth, int) or depth <= 0:
        raise CodeGraphPolicyError("CodeGraph affected.depth must be a positive integer")
    _non_empty_strings(affected.get("test_filters"), "affected.test_filters")


def _run(
    args: Sequence[str],
    *,
    cwd: Path,
    timeout: int,
    environment: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=None if environment is None else {**os.environ, **environment},
    )


def _detail(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr or result.stdout).strip()[-1200:]


def _state(
    policy: Mapping[str, Any],
    root: Path,
    status: str,
    reason: str,
    **values: Any,
) -> dict[str, Any]:
    return {
        "status": status,
        "reason": reason,
        "project_root": str(root),
        "index_path": str(root / str(policy["index_directory"])),
        "minimum_version": str(policy["minimum_version"]),
        "query_commands": list(policy["query_commands"]),
        "explore_max_files": int(policy["explore_max_files"]),
        "affected_depth": int(policy["affected"]["depth"]),
        "affected_test_filters": list(policy["affected"]["test_filters"]),
        **values,
    }


def disabled_state(policy: Mapping[str, Any], root: Path, reason: str) -> dict[str, Any]:
    return _state(policy, root.resolve(), "disabled", reason)


def _status_state(
    policy: Mapping[str, Any],
    root: Path,
    *,
    executable: str,
    version: str,
    initialized: bool,
    synced: bool,
    result: subprocess.CompletedProcess[str],
) -> dict[str, Any]:
    if result.returncode != 0:
        return _state(
            policy,
            root,
            "degraded",
            "status_failed",
            executable=executable,
            version=version,
            initialized=initialized,
            synced=synced,
            error=_detail(result),
        )
    try:
        snapshot = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return _state(
            policy,
            root,
            "degraded",
            "invalid_status_json",
            executable=executable,
            version=version,
            initialized=initialized,
            synced=synced,
            error=str(exc),
        )
    if not isinstance(snapshot, dict):
        return _state(
            policy,
            root,
            "degraded",
            "invalid_status_json",
            executable=executable,
            version=version,
            initialized=initialized,
            synced=synced,
        )
    pending = snapshot.get("pendingChanges")
    index = snapshot.get("index")
    pending_values = (
        [pending.get(name) for name in ("added", "modified", "removed")]
        if isinstance(pending, dict)
        else []
    )
    complete = (
        snapshot.get("initialized") is True
        and len(pending_values) == 3
        and all(value == 0 for value in pending_values)
        and snapshot.get("worktreeMismatch") is None
        and isinstance(index, dict)
        and index.get("state") == "complete"
        and index.get("reindexRecommended") is False
    )
    return _state(
        policy,
        root,
        "ready" if complete else "degraded",
        "ready" if complete else "index_not_clean",
        executable=executable,
        version=version,
        initialized=initialized,
        synced=synced,
        status_snapshot=snapshot,
    )


def prepare(policy: Mapping[str, Any], project_root: Path) -> dict[str, Any]:
    """Initialize/sync a safely ignored project index and return durable state.

    Runtime failures deliberately degrade to ordinary repository inspection. An
    invalid installed policy remains a hard configuration error.
    """

    validate_policy(policy)
    root = project_root.resolve(strict=True)
    timeout = int(policy["timeout_seconds"])
    environment = {"CODEGRAPH_DIR": str(policy["index_directory"])}
    executable = str(policy["executable"])
    binary = shutil.which(executable)
    if binary is None and Path(executable).is_file():
        binary = str(Path(executable).resolve())
    if binary is None:
        return _state(policy, root, "unavailable", "executable_not_found")

    try:
        version_result = _run(
            [binary, "--version"],
            cwd=root,
            timeout=timeout,
            environment=environment,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return _state(
            policy,
            root,
            "unavailable",
            "version_check_failed",
            executable=binary,
            error=str(exc),
        )
    version_text = (version_result.stdout or version_result.stderr).strip().splitlines()
    if version_result.returncode != 0 or not version_text:
        return _state(
            policy,
            root,
            "unavailable",
            "version_check_failed",
            executable=binary,
            error=_detail(version_result),
        )
    match = VERSION_PATTERN.search(version_text[0])
    if match is None:
        return _state(
            policy,
            root,
            "unavailable",
            "unparseable_version",
            executable=binary,
            version=version_text[0],
        )
    installed_version = tuple(int(part) for part in match.groups())
    if installed_version < _version(policy["minimum_version"], "minimum_version"):
        return _state(
            policy,
            root,
            "unavailable",
            "unsupported_version",
            executable=binary,
            version=version_text[0],
        )

    index_directory = str(policy["index_directory"])
    index_path = root / index_directory
    database_path = index_path / "codegraph.db"
    if index_path.is_symlink() or database_path.is_symlink():
        return _state(
            policy,
            root,
            "unavailable",
            "index_path_is_symlink",
            executable=binary,
            version=version_text[0],
        )
    ignore_probe = f"{index_directory}/codegraph.db"
    try:
        ignored = _run(
            ["git", "check-ignore", "--quiet", "--no-index", "--", ignore_probe],
            cwd=root,
            timeout=timeout,
            environment=environment,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return _state(
            policy,
            root,
            "unavailable",
            "ignore_check_failed",
            executable=binary,
            version=version_text[0],
            error=str(exc),
        )
    if ignored.returncode != 0:
        return _state(
            policy,
            root,
            "unavailable",
            "index_directory_not_ignored",
            executable=binary,
            version=version_text[0],
        )

    initialized = False
    synced = False
    try:
        if not database_path.is_file():
            if not policy["initialize_if_missing"]:
                return _state(
                    policy,
                    root,
                    "unavailable",
                    "index_not_initialized",
                    executable=binary,
                    version=version_text[0],
                )
            init = _run(
                [binary, "init", str(root)],
                cwd=root,
                timeout=timeout,
                environment=environment,
            )
            if init.returncode != 0:
                return _state(
                    policy,
                    root,
                    "degraded",
                    "initialization_failed",
                    executable=binary,
                    version=version_text[0],
                    error=_detail(init),
                )
            initialized = True
        elif policy["sync_on_prepare"]:
            sync = _run(
                [binary, "sync", str(root)],
                cwd=root,
                timeout=timeout,
                environment=environment,
            )
            if sync.returncode != 0:
                return _state(
                    policy,
                    root,
                    "degraded",
                    "sync_failed",
                    executable=binary,
                    version=version_text[0],
                    error=_detail(sync),
                )
            synced = True
        status_result = _run(
            [binary, "status", str(root), "--json"],
            cwd=root,
            timeout=timeout,
            environment=environment,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return _state(
            policy,
            root,
            "degraded",
            "lifecycle_command_failed",
            executable=binary,
            version=version_text[0],
            initialized=initialized,
            synced=synced,
            error=str(exc),
        )
    return _status_state(
        policy,
        root,
        executable=binary,
        version=version_text[0],
        initialized=initialized,
        synced=synced,
        result=status_result,
    )


def sync(
    policy: Mapping[str, Any],
    project_root: Path,
    prior_state: Mapping[str, Any],
) -> dict[str, Any]:
    """Incrementally refresh a previously prepared index without re-preflighting it."""

    validate_policy(policy)
    root = project_root.resolve(strict=True)
    if prior_state.get("status") != "ready":
        return dict(prior_state)
    if prior_state.get("project_root") != str(root):
        return _state(policy, root, "degraded", "project_root_changed")
    executable = prior_state.get("executable")
    version = prior_state.get("version")
    if not isinstance(executable, str) or not executable or not isinstance(version, str):
        return _state(policy, root, "degraded", "prepared_state_invalid")

    index_path = root / str(policy["index_directory"])
    if index_path.is_symlink() or (index_path / "codegraph.db").is_symlink():
        return _state(
            policy,
            root,
            "degraded",
            "index_path_is_symlink",
            executable=executable,
            version=version,
        )

    timeout = int(policy["timeout_seconds"])
    environment = {"CODEGRAPH_DIR": str(policy["index_directory"])}
    try:
        refreshed = _run(
            [executable, "sync", str(root)],
            cwd=root,
            timeout=timeout,
            environment=environment,
        )
        if refreshed.returncode != 0:
            return _state(
                policy,
                root,
                "degraded",
                "sync_failed",
                executable=executable,
                version=version,
                error=_detail(refreshed),
            )
        status = _run(
            [executable, "status", str(root), "--json"],
            cwd=root,
            timeout=timeout,
            environment=environment,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return _state(
            policy,
            root,
            "degraded",
            "sync_failed",
            executable=executable,
            version=version,
            error=str(exc),
        )
    return _status_state(
        policy,
        root,
        executable=executable,
        version=version,
        initialized=False,
        synced=True,
        result=status,
    )


def prompt_instructions(state: Mapping[str, Any]) -> str:
    status = str(state.get("status", "unavailable"))
    root = str(state.get("project_root", ""))
    if status == "disabled":
        reason = str(state.get("reason", "policy"))
        return (
            "## CodeGraph\n\n"
            f"CodeGraph is deliberately disabled for this assignment ({reason}). Do not "
            "query or mutate it, and do not broaden the job's declared read scope. Use "
            "direct reads only for the packet-authorized inputs.\n"
        )
    if status != "ready":
        reason = str(state.get("reason", "unknown"))
        return (
            "## CodeGraph\n\n"
            f"CodeGraph is {status} for this assignment ({reason}). Do not attempt to "
            "initialize, repair, or synchronize it. Use direct repository reads and `rg` "
            "instead.\n"
        )
    executable = shlex.quote(str(state["executable"]))
    quoted_root = shlex.quote(root)
    max_files = int(state["explore_max_files"])
    depth = int(state["affected_depth"])
    filters = ", ".join(f"`{value}`" for value in state["affected_test_filters"])
    commands = ", ".join(f"`{value}`" for value in state["query_commands"])
    return (
        "## CodeGraph\n\n"
        f"Scope prepared a CodeGraph {state.get('version', '')} index for "
        f"`{root}`. Use its CLI before broad grep/read exploration of indexed code. "
        f"Start with `{executable} explore --path {quoted_root} --max-files {max_files} "
        '"<specific symbols, files, or question>"`; use `node` for exact symbol/file '
        "source and its trail, then focused `query`, `callers`, `callees`, or `impact` "
        f"as needed. Allowed query subcommands are: {commands}.\n\n"
        "CodeGraph is navigation and blast-radius evidence, not correctness proof. Source "
        "returned for indexed symbols is direct, while cross-file relationships are derived; "
        "verify ambiguous or safety-critical relationships against source and tests. After "
        "you edit a source file, read that changed file directly when freshness matters; do "
        "not synchronize or mutate the index. Never run `init`, `index`, `sync`, `uninit`, "
        "`daemon`, `unlock`, `install`, `uninstall`, `telemetry`, or `upgrade`.\n\n"
        f"For affected-test discovery, run `affected --path {quoted_root} --depth {depth} "
        "--filter <one-explicit-filter> <changed-source-files>` separately with applicable "
        f"filters ({filters}). Treat those results as additions to required validation, never "
        "as permission to omit planned or contract-required tests.\n"
    )


def receipt(state: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "status",
        "reason",
        "project_root",
        "index_path",
        "executable",
        "version",
        "minimum_version",
        "initialized",
        "synced",
        "query_commands",
        "explore_max_files",
        "affected_depth",
        "affected_test_filters",
    )
    return {key: state[key] for key in keys if key in state}
