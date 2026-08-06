"""Small hardened Git primitives shared by Scope mutation commands."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
import os
from pathlib import Path
import re
import subprocess

from filelock import FileLock, Timeout as FileLockTimeout


COMMIT_PATTERN = re.compile(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})")
BRANCH_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")


class GitError(ValueError):
    """Raised when an exact Git mutation cannot be proved safe."""


def _environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment["GIT_TERMINAL_PROMPT"] = "0"
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_GRAFT_FILE"] = os.devnull
    return environment


def run(
    arguments: Sequence[str],
    root: Path,
    *,
    binary: bool = False,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    command = list(arguments)
    if command and command[0] == "git":
        command[1:1] = [
            "--no-replace-objects",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "core.hooksPath=",
        ]
    try:
        return subprocess.run(
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=not binary,
            env=_environment(),
        )
    except OSError as exc:
        raise GitError(f"cannot execute Git: {exc}") from exc


def git(
    root: Path,
    *arguments: str,
    binary: bool = False,
) -> str | bytes:
    result = run(["git", *arguments], root, binary=binary)
    if result.returncode != 0:
        stderr = result.stderr
        stdout = result.stdout
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        detail = (stderr or stdout or "").strip()
        raise GitError(f"git {' '.join(arguments)} failed: {detail}")
    return result.stdout if binary else str(result.stdout).strip()


def full_commit(value: str, label: str = "commit") -> str:
    if COMMIT_PATTERN.fullmatch(value) is None:
        raise GitError(f"{label} must be a full object ID")
    return value.lower()


def head(root: Path) -> str:
    return full_commit(str(git(root, "rev-parse", "HEAD")), "Git HEAD")


def tree(root: Path, revision: str = "HEAD") -> str:
    return full_commit(str(git(root, "rev-parse", f"{revision}^{{tree}}")), "Git tree")


def top_level(root: Path) -> Path:
    selected = Path(str(git(root, "rev-parse", "--show-toplevel"))).resolve(strict=True)
    if selected != root.resolve(strict=True):
        raise GitError(f"Git root mismatch: expected {root}, found {selected}")
    return selected


def require_linked_worktree(repository_root: Path, working_root: Path) -> None:
    repository = top_level(repository_root)
    worktree = top_level(working_root)
    if repository == worktree:
        raise GitError("implementation requires an isolated linked worktree")
    common = Path(
        str(git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    ).resolve(strict=True)
    git_dir = Path(
        str(git(repository, "rev-parse", "--path-format=absolute", "--git-dir"))
    ).resolve(strict=True)
    if common != git_dir:
        raise GitError("worktree does not belong to the selected repository")


def status(root: Path) -> str:
    return str(git(root, "status", "--porcelain=v1", "--untracked-files=all"))


def runtime_directory(root: Path, *children: str) -> Path:
    selected = root.resolve(strict=True)
    current = selected
    for name in ("tmp_debug", *children):
        if not name or Path(name).name != name:
            raise GitError("Scope runtime directory component is invalid")
        current = current / name
        if current.is_symlink():
            raise GitError(f"Scope runtime directory must not be a symlink: {current}")
        current.mkdir(exist_ok=True)
        if current.resolve(strict=True).parent != current.parent.resolve(strict=True):
            raise GitError(f"Scope runtime directory escapes its root: {current}")
    return current


def _fixed_mutation(arguments: Sequence[str]) -> list[str]:
    return [
        "git",
        "-c",
        "commit.gpgSign=false",
        "-c",
        "merge.autoStash=false",
        *arguments,
    ]


def merge_tree(root: Path, target: str, source: str) -> str:
    """Return the exact conflict-free tree for a two-parent merge."""
    target_commit = full_commit(target, "merge target")
    source_commit = full_commit(source, "merge source")
    preview = run(
        ["git", "merge-tree", "--write-tree", target_commit, source_commit], root
    )
    if preview.returncode != 0:
        raise GitError("exact merge preview is not conflict-free")
    first_line = str(preview.stdout).splitlines()[0].strip() if preview.stdout else ""
    return full_commit(first_line, "merge preview tree")


@contextmanager
def mutation_locks(roots: Sequence[Path]) -> Iterator[None]:
    selected = sorted(
        {root.resolve(strict=True) for root in roots}, key=lambda path: os.path.normcase(str(path))
    )
    locks: list[FileLock] = []
    try:
        for root in selected:
            lock_path = runtime_directory(root) / "scope-mutation.lock"
            if lock_path.is_symlink():
                raise GitError(f"Scope mutation lock must not be a symlink: {lock_path}")
            lock = FileLock(str(lock_path))
            try:
                lock.acquire(timeout=0)
            except FileLockTimeout as exc:
                raise GitError(f"Scope mutation root is busy: {root}") from exc
            locks.append(lock)
        yield
    finally:
        for lock in reversed(locks):
            lock.release()


def commit_index(root: Path, expected_parent: str, expected_tree: str, subject: str) -> str:
    parent = full_commit(expected_parent, "expected commit parent")
    staged_tree = full_commit(expected_tree, "expected staged tree")
    if head(root) != parent:
        raise GitError("worktree HEAD changed before closure commit")
    if str(git(root, "write-tree")).lower() != staged_tree:
        raise GitError("staged tree differs from the approved tree")
    result = run(
        _fixed_mutation(["commit", "--no-gpg-sign", "-m", subject]), root
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise GitError(f"closure commit failed: {detail}")
    commit = head(root)
    parents = str(git(root, "show", "-s", "--format=%P", commit)).lower().split()
    if parents != [parent] or tree(root, commit) != staged_tree:
        raise GitError("closure commit parent or tree differs from the approved state")
    if git(root, "show", "-s", "--format=%s", commit) != subject:
        raise GitError("closure commit subject does not match the fixed label")
    return commit


def merge_exact(root: Path, source: str, expected_head: str, subject: str) -> str:
    source_commit = full_commit(source, "merge source")
    target_head = full_commit(expected_head, "expected merge target HEAD")
    if head(root) != target_head:
        raise GitError("merge target HEAD changed after approval")
    if status(root):
        raise GitError("merge target worktree and index must be clean")
    if git(root, "cat-file", "-t", source_commit) != "commit":
        raise GitError("merge source is not a local commit object")
    expected_tree = merge_tree(root, target_head, source_commit)
    branch = str(git(root, "symbolic-ref", "--short", "HEAD"))
    if BRANCH_PATTERN.fullmatch(branch) is None:
        raise GitError("merge target branch cannot be safely configured")
    result = run(
        _fixed_mutation(
            [
                "-c",
                f"branch.{branch}.mergeOptions=",
                "merge",
                "--no-ff",
                "--no-commit",
                "--no-autostash",
                "--strategy=ort",
                source_commit,
            ]
        ),
        root,
    )
    if result.returncode != 0:
        run(["git", "merge", "--abort"], root)
        detail = (result.stderr or result.stdout or "").strip()
        raise GitError(f"exact merge failed after clean preview: {detail}")
    if head(root) != target_head:
        run(["git", "merge", "--abort"], root)
        raise GitError("merge committed before exact tree validation")
    if str(git(root, "write-tree")).lower() != expected_tree:
        run(["git", "merge", "--abort"], root)
        raise GitError("merge tree does not match the conflict-free preview")
    result = run(
        _fixed_mutation(["commit", "--no-gpg-sign", "-m", subject]), root
    )
    if result.returncode != 0:
        run(["git", "merge", "--abort"], root)
        detail = (result.stderr or result.stdout or "").strip()
        raise GitError(f"exact merge commit failed: {detail}")
    commit = head(root)
    parents = str(git(root, "show", "-s", "--format=%P", commit)).lower().split()
    if parents != [target_head, source_commit]:
        raise GitError("merge parents do not match the approved commits")
    if tree(root, commit) != expected_tree:
        raise GitError("merge tree does not match the conflict-free preview")
    if git(root, "show", "-s", "--format=%s", commit) != subject:
        raise GitError("merge subject does not match the fixed label")
    return commit
