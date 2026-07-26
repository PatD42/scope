from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "src_shared/scripts/scope-reviewer-claude-pexpect.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "scope_reviewer_claude_pexpect", RUNNER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = _load_module()


def test_metadata_records_provider_mission_sizes_and_relative_output(
    tmp_path: Path,
) -> None:
    prompt = tmp_path / "prompt.md"
    output = tmp_path / "reviews/review.md"
    metadata = tmp_path / "reviews/metadata.yaml"
    prompt.write_text("prompt", encoding="utf-8")
    output.parent.mkdir(parents=True)
    output.write_text("review", encoding="utf-8")

    RUNNER.append_metadata(
        metadata,
        reviewer="semantic_core",
        model="Claude Opus (local alias)",
        transport="pexpect",
        session="",
        status="completed",
        started_at="2026-07-26T10:00:00Z",
        completed_at="2026-07-26T10:00:03Z",
        duration_seconds=3,
        timeout_seconds=60,
        retry_count=0,
        prompt_file=prompt,
        output_file=output,
        cwd=tmp_path,
        error="",
    )

    row = yaml.safe_load(metadata.read_text(encoding="utf-8"))["reviews"][0]
    assert row["provider"] == "claude"
    assert row["mission"] == "semantic_core"
    assert row["retry_count"] == 0
    assert row["prompt_bytes"] == 6
    assert row["output_bytes"] == 6
    assert row["output_file"] == "reviews/review.md"


def test_review_extraction_and_log_paths_are_deterministic(tmp_path: Path) -> None:
    output = tmp_path / "review.md"
    output.write_text("before\nSTART\nresult\nEND\nafter\n", encoding="utf-8")

    assert RUNNER.extract_review(output, "START", "END") == "result\n"
    assert RUNNER.extract_review(output, "MISSING", "END") is None
    assert RUNNER.extract_review(tmp_path / "missing.md", "START", "END") is None
    assert RUNNER.default_log_file(tmp_path, output).is_relative_to(
        tmp_path / "tmp_debug/scope-reviewer-logs"
    )


def test_default_claude_command_is_noninteractive_and_has_no_retry() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8")

    for flag in (
        "--safe-mode",
        "--strict-mcp-config",
        "--dangerously-skip-permissions",
        "--no-chrome",
    ):
        assert flag in source
    assert 'parser.add_argument("--retries", type=int, default=0)' in source
