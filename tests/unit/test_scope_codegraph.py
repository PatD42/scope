from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import subprocess

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "src_shared/config/codegraph-policy.yaml"
MODULE_PATH = REPO_ROOT / "src_shared/scripts/scope_codegraph.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("scope_codegraph_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scope_codegraph = _load_module()


FAKE_CODEGRAPH = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
version = os.environ.get("FAKE_CODEGRAPH_VERSION", "1.5.0")
if args == ["--version"]:
    print(version)
    raise SystemExit(int(os.environ.get("FAKE_CODEGRAPH_VERSION_EXIT", "0")))
if args and args[0] == "init":
    if os.environ.get("FAKE_CODEGRAPH_INIT_FAIL"):
        print("init failed", file=sys.stderr)
        raise SystemExit(7)
    root = Path(args[1])
    index = root / ".codegraph"
    index.mkdir(parents=True, exist_ok=True)
    (index / "codegraph.db").write_text("fake", encoding="utf-8")
    raise SystemExit(0)
if args and args[0] == "sync":
    if os.environ.get("FAKE_CODEGRAPH_SYNC_FAIL"):
        print("sync failed", file=sys.stderr)
        raise SystemExit(8)
    raise SystemExit(0)
if args and args[0] == "status":
    if os.environ.get("FAKE_CODEGRAPH_STATUS_FAIL"):
        print("status failed", file=sys.stderr)
        raise SystemExit(9)
    if os.environ.get("FAKE_CODEGRAPH_STATUS_INVALID"):
        print("not-json")
        raise SystemExit(0)
    root = Path(args[1]).resolve()
    pending = int(os.environ.get("FAKE_CODEGRAPH_PENDING", "0"))
    print(json.dumps({
        "initialized": True,
        "version": version,
        "projectPath": str(root),
        "indexPath": str(root / ".codegraph"),
        "pendingChanges": {"added": pending, "modified": 0, "removed": 0},
        "worktreeMismatch": None,
        "index": {"state": "complete", "reindexRecommended": False},
    }))
    raise SystemExit(0)
raise SystemExit(2)
'''


def _policy() -> dict[str, object]:
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


def _repository(tmp_path: Path, *, ignored: bool = True) -> Path:
    repository = tmp_path / "repo"
    repository.mkdir()
    (repository / ".gitignore").write_text(
        ".codegraph/\n" if ignored else "tmp_debug/\n", encoding="utf-8"
    )
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    return repository


def _fake(tmp_path: Path) -> Path:
    executable = tmp_path / "fake-codegraph"
    executable.write_text(FAKE_CODEGRAPH, encoding="utf-8")
    executable.chmod(0o755)
    return executable


def test_prepare_initializes_then_syncs_clean_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path)
    policy = _policy()
    policy["executable"] = str(_fake(tmp_path))
    monkeypatch.setenv("CODEGRAPH_DIR", ".wrong-parent-setting")

    initialized = scope_codegraph.prepare(policy, repository)
    synced = scope_codegraph.prepare(policy, repository)

    assert initialized["status"] == "ready"
    assert initialized["initialized"] is True
    assert initialized["synced"] is False
    assert synced["status"] == "ready"
    assert synced["initialized"] is False
    assert synced["synced"] is True
    assert scope_codegraph.receipt(synced)["version"] == "1.5.0"
    assert scope_codegraph.receipt(synced)["executable"] == str(policy["executable"])
    assert "explore --path" in scope_codegraph.prompt_instructions(
        scope_codegraph.receipt(synced)
    )
    assert not (repository / ".wrong-parent-setting").exists()


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ({"executable": "missing-codegraph-test-binary"}, "executable_not_found"),
        ({"minimum_version": "2.0.0"}, "unsupported_version"),
    ],
)
def test_prepare_gracefully_reports_unavailable_toolchain(
    tmp_path: Path, change: dict[str, object], expected: str
) -> None:
    repository = _repository(tmp_path)
    policy = _policy()
    policy["executable"] = str(_fake(tmp_path))
    policy.update(change)

    state = scope_codegraph.prepare(policy, repository)

    assert state["status"] == "unavailable"
    assert state["reason"] == expected


def test_prepare_refuses_unignored_index_directory(tmp_path: Path) -> None:
    repository = _repository(tmp_path, ignored=False)
    policy = _policy()
    policy["executable"] = str(_fake(tmp_path))

    state = scope_codegraph.prepare(policy, repository)

    assert state["status"] == "unavailable"
    assert state["reason"] == "index_directory_not_ignored"
    assert not (repository / ".codegraph").exists()


def test_prepare_refuses_symlinked_index_directory(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (repository / ".codegraph").symlink_to(outside, target_is_directory=True)
    policy = _policy()
    policy["executable"] = str(_fake(tmp_path))

    state = scope_codegraph.prepare(policy, repository)

    assert state["status"] == "unavailable"
    assert state["reason"] == "index_path_is_symlink"


@pytest.mark.parametrize(
    ("environment", "reason"),
    [
        ({"FAKE_CODEGRAPH_INIT_FAIL": "1"}, "initialization_failed"),
        ({"FAKE_CODEGRAPH_STATUS_FAIL": "1"}, "status_failed"),
        ({"FAKE_CODEGRAPH_STATUS_INVALID": "1"}, "invalid_status_json"),
        ({"FAKE_CODEGRAPH_PENDING": "1"}, "index_not_clean"),
    ],
)
def test_prepare_degrades_on_lifecycle_or_index_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    environment: dict[str, str],
    reason: str,
) -> None:
    repository = _repository(tmp_path)
    policy = _policy()
    policy["executable"] = str(_fake(tmp_path))
    for name, value in environment.items():
        monkeypatch.setenv(name, value)

    state = scope_codegraph.prepare(policy, repository)

    assert state["status"] == "degraded"
    assert state["reason"] == reason


def test_prepare_degrades_when_existing_index_sync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path)
    policy = _policy()
    policy["executable"] = str(_fake(tmp_path))
    assert scope_codegraph.prepare(policy, repository)["status"] == "ready"
    monkeypatch.setenv("FAKE_CODEGRAPH_SYNC_FAIL", "1")

    state = scope_codegraph.prepare(policy, repository)

    assert state["status"] == "degraded"
    assert state["reason"] == "sync_failed"


def test_incremental_sync_reuses_prepared_toolchain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path)
    policy = _policy()
    policy["executable"] = str(_fake(tmp_path))
    prepared = scope_codegraph.prepare(policy, repository)
    calls: list[list[str]] = []
    original_run = scope_codegraph._run

    def recording_run(args, **kwargs):
        calls.append(list(args))
        return original_run(args, **kwargs)

    monkeypatch.setattr(scope_codegraph, "_run", recording_run)

    refreshed = scope_codegraph.sync(policy, repository, prepared)

    assert refreshed["status"] == "ready"
    assert refreshed["synced"] is True
    assert [call[1] for call in calls] == ["sync", "status"]
    assert all("--version" not in call for call in calls)


def test_incremental_sync_does_not_retry_degraded_state(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    policy = _policy()
    degraded = scope_codegraph.disabled_state(policy, repository, "sync_failed")
    degraded["status"] = "degraded"

    assert scope_codegraph.sync(policy, repository, degraded) == degraded


def test_prompt_instructions_expose_cli_boundaries_and_fallback(tmp_path: Path) -> None:
    policy = _policy()
    ready = {
        **scope_codegraph.disabled_state(policy, tmp_path, "fixture"),
        "status": "ready",
        "reason": "ready",
        "version": "1.5.0",
        "executable": "/tools/codegraph",
    }

    instructions = scope_codegraph.prompt_instructions(ready)
    fallback = scope_codegraph.prompt_instructions(
        {**ready, "status": "unavailable", "reason": "executable_not_found"}
    )
    disabled = scope_codegraph.prompt_instructions(
        scope_codegraph.disabled_state(policy, tmp_path, "worker_role_not_enabled")
    )

    assert "explore --path" in instructions
    assert "Never run `init`, `index`, `sync`" in instructions
    assert "--filter <one-explicit-filter>" in instructions
    assert "Use direct repository reads and `rg`" in fallback
    assert "do not broaden the job's declared read scope" in disabled


@pytest.mark.parametrize(
    "mutation",
    [
        {"schema_version": 2},
        {"executable": ""},
        {"minimum_version": None},
        {"minimum_version": "not-a-version"},
        {"index_directory": "../escape"},
        {"initialize_if_missing": "yes"},
        {"timeout_seconds": 0},
        {"worker_roles": ["refinement", "refinement"]},
        {"query_commands": ["status", "sync"]},
        {"explore_max_files": 0},
        {"affected": []},
        {"affected": {"depth": 0, "test_filters": ["tests/**/*.py"]}},
        {"affected": {"depth": 3, "test_filters": []}},
    ],
)
def test_policy_validation_rejects_unsafe_or_invalid_values(
    mutation: dict[str, object]
) -> None:
    policy = deepcopy(_policy())
    policy.update(mutation)

    with pytest.raises(scope_codegraph.CodeGraphPolicyError):
        scope_codegraph.validate_policy(policy)


def test_load_policy_rejects_non_mapping(tmp_path: Path) -> None:
    invalid = tmp_path / "codegraph-policy.yaml"
    invalid.write_text("- invalid\n", encoding="utf-8")

    with pytest.raises(scope_codegraph.CodeGraphPolicyError, match="must be a mapping"):
        scope_codegraph.load_policy(invalid)


def test_load_policy_rejects_missing_and_malformed_yaml(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"
    malformed = tmp_path / "malformed.yaml"
    malformed.write_text("value: [unterminated\n", encoding="utf-8")

    with pytest.raises(scope_codegraph.CodeGraphPolicyError, match="missing"):
        scope_codegraph.load_policy(missing)
    with pytest.raises(scope_codegraph.CodeGraphPolicyError, match="invalid"):
        scope_codegraph.load_policy(malformed)
