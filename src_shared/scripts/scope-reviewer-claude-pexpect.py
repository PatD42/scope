#!/usr/bin/env python3
"""Run a Scope Claude reviewer through an interactive PTY.

This wrapper is for subscription-backed Claude CLI usage where `claude -p`
is undesirable. It avoids fragile TUI scraping by:

1. passing Claude a short one-shot instruction as the initial prompt;
2. asking Claude to read the real reviewer prompt from a file;
3. asking Claude to write the review to a file with sentinels;
4. watching the output file until it is valid or the timeout expires.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import time
from typing import Any


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def append_metadata(
    metadata_file: Path,
    *,
    reviewer: str,
    model: str,
    transport: str,
    session: str,
    status: str,
    started_at: str,
    completed_at: str,
    duration_seconds: int,
    timeout_seconds: int,
    retry_count: int,
    output_file: Path,
    error: str,
) -> None:
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    if not metadata_file.exists():
        metadata_file.write_text("reviews:\n")

    def q(value: Any) -> str:
        return json.dumps(str(value))

    with metadata_file.open("a", encoding="utf-8") as handle:
        handle.write(f"  - reviewer: {q(reviewer)}\n")
        handle.write(f"    model: {q(model)}\n")
        handle.write(f"    transport: {q(transport)}\n")
        handle.write(f"    session: {q(session)}\n")
        handle.write(f"    status: {q(status)}\n")
        handle.write(f"    started_at: {q(started_at)}\n")
        handle.write(f"    completed_at: {q(completed_at)}\n")
        handle.write(f"    duration_seconds: {duration_seconds}\n")
        handle.write(f"    timeout_seconds: {timeout_seconds}\n")
        handle.write(f"    retry_count: {retry_count}\n")
        handle.write(f"    output_file: {q(output_file)}\n")
        handle.write(f"    error: {q(error)}\n")


def extract_review(output_file: Path, start_marker: str, end_marker: str) -> str | None:
    if not output_file.exists():
        return None

    text = output_file.read_text(encoding="utf-8", errors="ignore")
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker) if start != -1 else 0)
    if start == -1 or end == -1:
        return None

    return text[start + len(start_marker) : end].strip() + "\n"


def terminate_child(child: Any) -> None:
    try:
        child.sendcontrol("c")
        time.sleep(0.3)
        child.sendline("/exit")
        time.sleep(0.3)
    except Exception:
        pass

    try:
        child.terminate(force=True)
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer", default="claude")
    parser.add_argument("--model", required=True)
    parser.add_argument("--claude-command", default="claude --model opus")
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--output-file", required=True, type=Path)
    parser.add_argument("--metadata-file", required=True, type=Path)
    parser.add_argument("--cwd", required=True, type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--log-file", type=Path)
    args = parser.parse_args()

    started_epoch = int(time.time())
    started_at = utc_now()
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    log_file = args.log_file or args.output_file.with_suffix(args.output_file.suffix + ".pty.log")

    try:
        import pexpect  # type: ignore[import-not-found]
    except Exception as exc:
        completed_at = utc_now()
        duration_seconds = int(time.time()) - started_epoch
        error = f"Python pexpect module not available: {exc}"
        args.output_file.write_text(f"Claude external review unavailable.\n{error}\n")
        append_metadata(
            args.metadata_file,
            reviewer=args.reviewer,
            model=args.model,
            transport="pexpect",
            session="",
            status="unavailable",
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
            timeout_seconds=args.timeout_seconds,
            retry_count=0,
            output_file=args.output_file,
            error=error,
        )
        return 127

    command_parts = shlex.split(args.claude_command)
    if not command_parts:
        print("--claude-command must not be empty", file=sys.stderr)
        return 2

    claude_binary = command_parts[0]
    if shutil.which(claude_binary) is None:
        completed_at = utc_now()
        duration_seconds = int(time.time()) - started_epoch
        error = f"Claude CLI not found: {claude_binary}"
        args.output_file.write_text(f"Claude external review unavailable.\n{error}\n")
        append_metadata(
            args.metadata_file,
            reviewer=args.reviewer,
            model=args.model,
            transport="pexpect",
            session="",
            status="unavailable",
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
            timeout_seconds=args.timeout_seconds,
            retry_count=0,
            output_file=args.output_file,
            error=error,
        )
        return 127

    cwd = args.cwd.resolve()
    prompt_file = args.prompt_file.resolve()
    output_file = args.output_file.resolve()
    nonce = f"{int(time.time())}-{os.getpid()}"
    safe_reviewer = "".join(ch if ch.isalnum() else "_" for ch in args.reviewer)
    start_marker = f"SCOPE_REVIEW_START_{safe_reviewer}_{nonce}"
    end_marker = f"SCOPE_REVIEW_END_{safe_reviewer}_{nonce}"

    instruction = f"""Read the reviewer prompt at {prompt_file}.
Apply it to the repository/worktree at {cwd}.
Write the final review report to {output_file}.
The output file must begin with exactly this line: {start_marker}
The output file must end with exactly this line: {end_marker}
Do not edit files except {output_file}.
Do not create commits.
Use read-only inspection of the repository/worktree except for writing the output file.
Return the complete requested review report in the output file, not in the console."""

    env = os.environ.copy()
    env.setdefault("TERM", "xterm-256color")
    env["NO_COLOR"] = "1"

    status = "failed"
    error = ""
    retry_count = 0

    for attempt in range(args.retries + 1):
        retry_count = attempt
        try:
            output_file.unlink()
        except FileNotFoundError:
            pass

        child = None
        try:
            child = pexpect.spawn(
                command_parts[0],
                command_parts[1:] + [instruction],
                cwd=str(cwd),
                env=env,
                encoding="utf-8",
                timeout=10,
                dimensions=(60, 220),
            )
            with log_file.open("a", encoding="utf-8", errors="ignore") as log:
                log.write(f"\n--- attempt {attempt + 1} started {utc_now()} ---\n")
                child.logfile_read = log

                deadline = time.time() + args.timeout_seconds
                while time.time() < deadline:
                    review = extract_review(output_file, start_marker, end_marker)
                    if review is not None:
                        output_file.write_text(review, encoding="utf-8")
                        status = "completed"
                        error = ""
                        terminate_child(child)
                        child = None
                        break

                    try:
                        child.read_nonblocking(8192, timeout=1)
                    except pexpect.TIMEOUT:
                        pass
                    except pexpect.EOF:
                        error = "Claude process exited before a valid sentinel-bounded output file was observed"
                        break

            if status == "completed":
                break

            if not error:
                error = f"Timed out waiting for Claude output file after {args.timeout_seconds}s"
            if child is not None:
                terminate_child(child)

        except Exception as exc:
            error = str(exc)
            if child is not None:
                terminate_child(child)

    completed_at = utc_now()
    duration_seconds = int(time.time()) - started_epoch

    if status != "completed":
        output_file.write_text(f"Claude external review failed.\n{error}\n", encoding="utf-8")

    append_metadata(
        args.metadata_file,
        reviewer=args.reviewer,
        model=args.model,
        transport="pexpect",
        session="",
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=duration_seconds,
        timeout_seconds=args.timeout_seconds,
        retry_count=retry_count,
        output_file=output_file,
        error=error,
    )

    return 0 if status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
