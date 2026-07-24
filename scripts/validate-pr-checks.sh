#!/usr/bin/env bash

set -euo pipefail

section() {
  printf '\n==> %s\n' "$1"
}

fail() {
  echo "Validation failed: $1" >&2
  exit 1
}

diff_range() {
  if [[ -n "${1:-}" ]]; then
    printf '%s\n' "$1"
  elif [[ -n "${GITHUB_BASE_REF:-}" ]]; then
    printf 'origin/%s...HEAD\n' "$GITHUB_BASE_REF"
  elif git rev-parse --verify HEAD~1 >/dev/null 2>&1; then
    printf 'HEAD~1...HEAD\n'
  fi
}

changed_files() {
  local range="$1"

  {
    if [[ -n "$range" ]]; then
      git diff --name-only "$range"
    fi
    git diff --name-only
    git diff --cached --name-only
    git ls-files --others --exclude-standard
  } | sed '/^$/d' | sort -u
}

is_text_file() {
  local file="$1"
  local mime

  mime="$(file -b --mime-type "$file" 2>/dev/null || true)"
  case "$mime" in
    text/*|application/json|application/xml|application/x-yaml|application/yaml|application/x-shellscript)
      return 0
      ;;
  esac

  case "$file" in
    *.md|*.yaml|*.yml|*.json|*.toml|*.sh|*.bat|*.cmd|*.ps1|*.py|*.txt|*.sql|*.html|*.css|*.js|*.ts|*.tsx)
      return 0
      ;;
  esac

  return 1
}

check_whitespace() {
  local range="$1"
  local failed=0
  local file
  local output

  section "Check whitespace"

  if [[ -n "$range" ]]; then
    git diff --check "$range" || failed=1
  fi

  git diff --check || failed=1
  git diff --cached --check || failed=1

  while IFS= read -r file; do
    [[ -f "$file" ]] || continue
    is_text_file "$file" || continue

    output="$(git diff --check --no-index /dev/null "$file" 2>/dev/null || true)"
    if [[ -n "$output" ]]; then
      echo "$output"
      failed=1
    fi
  done < <(git ls-files --others --exclude-standard)

  [[ "$failed" -eq 0 ]] || fail "whitespace check failed"
}

check_generated_files() {
  local failed=0
  local file

  section "Reject local/generated files"

  while IFS= read -r file; do
    case "$file" in
      .DS_Store|*/.DS_Store|*.pyc|*/__pycache__/*|*/.pytest_cache/*|.claude/*|plugins/*)
        echo "Forbidden local/generated file: $file"
        failed=1
        ;;
    esac
  done < <({
    git ls-files
    git ls-files --others --exclude-standard
  } | sort -u)

  [[ "$failed" -eq 0 ]] || fail "forbidden local/generated files found"
}

check_mirrors() {
  local range="$1"
  local missing=""
  local changed_file_list
  local file
  local counterpart

  section "Check mirrored Claude/Codex changes"

  changed_file_list="$(mktemp)"
  changed_files "$range" > "$changed_file_list"

  while IFS= read -r file; do
    [[ -n "$file" ]] || continue

    case "$file" in
      src_claude/*)
        counterpart="src_codex/${file#src_claude/}"
        ;;
      src_codex/*)
        counterpart="src_claude/${file#src_codex/}"
        ;;
      *)
        continue
        ;;
    esac

    if [[ -f "$counterpart" ]] && ! grep -F -x -q "$counterpart" "$changed_file_list"; then
      missing="${missing}\n${file} changed, but matching ${counterpart} was not changed."
    fi
  done < "$changed_file_list"

  rm -f "$changed_file_list"

  if [[ -n "$missing" ]]; then
    echo "Claude/Codex mirrored files must be updated together when a counterpart exists."
    printf '%b\n' "$missing"
    fail "mirrored file check failed"
  fi
}

check_install() {
  local tmpdir
  local obsolete

  section "Install smoke test"

  tmpdir="$(mktemp -d)"
  ./install.sh "$tmpdir" >/tmp/scope-install-smoke.log

  test -f "$tmpdir/.claude/commands/wrap_epic.md"
  test -f "$tmpdir/.claude/commands/implement.md"
  test -f "$tmpdir/.claude/commands/audit_epic.md"
  test -f "$tmpdir/.claude/commands/epic_refine/reviewer-refinement.md"
  test -f "$tmpdir/.claude/commands/audit_epic/reviewer-audit.md"
  test -f "$tmpdir/.claude/agents/developer.md"
  test -f "$tmpdir/.claude/config/refinement-policy.yaml"
  test -f "$tmpdir/.claude/config/audit-policy.yaml"
  test -f "$tmpdir/.claude/scripts/validate-refinement.py"
  test -f "$tmpdir/.claude/scripts/audit-artifacts.py"
  test -f "$tmpdir/.claude/scripts/scope-reviewer-claude-pexpect.py"
  test -f "$tmpdir/.claude/requirements.txt"

  test -f "$tmpdir/plugins/scope/commands/wrap_epic.md"
  test -f "$tmpdir/plugins/scope/commands/implement.md"
  test -f "$tmpdir/plugins/scope/commands/audit_epic.md"
  test -f "$tmpdir/plugins/scope/commands/epic_refine/reviewer-refinement.md"
  test -f "$tmpdir/plugins/scope/commands/audit_epic/reviewer-audit.md"
  test -f "$tmpdir/plugins/scope/agents/developer.md"
  test -f "$tmpdir/plugins/scope/config/refinement-policy.yaml"
  test -f "$tmpdir/plugins/scope/config/audit-policy.yaml"
  test -f "$tmpdir/plugins/scope/scripts/validate-refinement.py"
  test -f "$tmpdir/plugins/scope/scripts/audit-artifacts.py"
  test -f "$tmpdir/plugins/scope/scripts/scope-reviewer-claude-pexpect.py"
  test -f "$tmpdir/plugins/scope/requirements.txt"
  test -f "$tmpdir/plugins/scope/.codex-plugin/plugin.json"
  test -f "$tmpdir/.scope/config.yaml"

  grep -n '^  skill: local-tracking-bash' "$tmpdir/.scope/config.yaml"
  grep -n '^  project_key: PROJECT' "$tmpdir/.scope/config.yaml"
  grep -n '^  base_path: ./tracking' "$tmpdir/.scope/config.yaml"
  grep -n '^  skill: project-documentation-file' "$tmpdir/.scope/config.yaml"
  grep -n '^  docs_path: ./docs' "$tmpdir/.scope/config.yaml"
  if grep -n -E 'MYPROJ|MYSPACE|jira|confluence' "$tmpdir/.scope/config.yaml"; then
    fail "installed default config must not require Jira or Confluence setup"
  fi

  test -d "$tmpdir/.claude/commands/audit_epic"
  test -d "$tmpdir/plugins/scope/commands/audit_epic"

  test -f "$tmpdir/.claude/skills/project-documentation/SKILL.md"
  test -f "$tmpdir/plugins/scope/skills/project-documentation/SKILL.md"
  grep -n "Path selection rule" "$tmpdir/.claude/skills/project-documentation/SKILL.md"
  grep -n "docs/architecture/backend/01-intro.md" "$tmpdir/.claude/skills/project-documentation/SKILL.md"
  grep -n "Path selection rule" "$tmpdir/plugins/scope/skills/project-documentation/SKILL.md"
  grep -n "docs/architecture/backend/01-intro.md" "$tmpdir/plugins/scope/skills/project-documentation/SKILL.md"
  grep -n "do not ask for a" "$tmpdir/.claude/skills/project-documentation/SKILL.md"
  grep -n "Do not ask for a Jira project key" "$tmpdir/.claude/skills/project-tracking/SKILL.md"
  grep -n '^model: sonnet$' "$tmpdir/.claude/agents/developer.md"
  grep -n '^model: gpt-5.6-terra$' "$tmpdir/plugins/scope/agents/developer.md"
  grep -n '^model_reasoning_effort: max$' "$tmpdir/plugins/scope/agents/developer.md"

  for obsolete in \
    commands/audit_epic/reviewer-codex.md \
    commands/audit_epic/reviewer-claude.md \
    commands/audit_epic/reviewer-agy.md \
    commands/audit_epic/reviewer-glm.md \
    commands/epic_refine/reviewer-architecture-codex.md \
    commands/epic_refine/reviewer-architecture-claude.md \
    commands/epic_refine/reviewer-architecture-agy.md \
    commands/epic_refine/reviewer-architecture-glm.md; do
    test ! -e "$tmpdir/.claude/$obsolete"
    test ! -e "$tmpdir/plugins/scope/$obsolete"
  done

  rm -rf "$tmpdir"
}

check_windows_installer() {
  local batch_version
  local required_path
  local shell_version

  section "Check Windows installer parity"

  test -f install.bat
  shell_version="$(sed -n 's/^VERSION="\([^"]*\)"/\1/p' install.sh)"
  batch_version="$(sed -n 's/^set "VERSION=\([^"]*\)"/\1/p' install.bat)"
  [[ -n "$shell_version" && "$batch_version" == "$shell_version" ]] || fail "install.sh and install.bat versions differ"
  grep -n 'if /I "%~1"=="--user"' install.bat
  grep -n 'set "INSTALL_DIR=%USERPROFILE%"' install.bat
  grep -n 'set "CLAUDE_DIR=%~1\\.claude"' install.bat
  grep -n 'set "CODEX_DIR=%~1\\plugins\\scope"' install.bat

  for required_path in commands scripts skills agents governance config docs .codex-plugin; do
    grep -n "${required_path}" install.bat >/dev/null
  done

  grep -n 'config_example.yaml' install.bat
  grep -n 'requirements.txt' install.bat
  grep -n 'scope-reviewer-tmux.sh' install.bat
  grep -n 'reviewer-codex reviewer-claude reviewer-agy reviewer-glm' install.bat
  grep -n 'reviewer-architecture-codex reviewer-architecture-claude reviewer-architecture-agy reviewer-architecture-glm' install.bat
  grep -n 'install.bat --user' README.md
  grep -n 'install.bat "C:\\path\\to\\your-project"' README.md
}

check_git_hooks() {
  section "Check Git hook enforcement"

  test -x .githooks/pre-push
  test -x scripts/setup-git-hooks.sh
  bash -n .githooks/pre-push scripts/setup-git-hooks.sh
  grep -n 'validate-pr-checks.sh' .githooks/pre-push
  grep -n 'core.hooksPath .githooks' scripts/setup-git-hooks.sh
  grep -n 'setup-git-hooks.sh' AGENTS.md CONTRIBUTING.md
}

check_actions_runtime() {
  section "Check GitHub Actions runtime"

  if grep -R -n 'actions/checkout@v4' .github/workflows; then
    fail "actions/checkout@v4 uses the deprecated Node 20 runtime"
  fi

  grep -n 'actions/checkout@v6' .github/workflows/pr-checks.yml
}

check_codex_plugin_naming() {
  section "Check Codex plugin naming"

  if grep -R -n -E "scope-for-codex|scope_for_codex" src_codex src_shared install.sh install.bat README.md CONTRIBUTING.md; then
    fail "found stale Codex plugin naming; use 'scope'"
  fi

  grep -n -E '"name"[[:space:]]*:[[:space:]]*"scope"' src_codex/.codex-plugin/plugin.json
}

check_codegraph_guidance() {
  section "Check CodeGraph guidance"

  grep -n "CodeGraph" src_shared/commands/epic_refine.md
  grep -n "CodeGraph" src_claude/commands/implement.md
  grep -n "CodeGraph" src_codex/commands/implement.md
}

check_codex_override_sources() {
  section "Check Codex override sources"

  if grep -R -n -E 'prefer[^[:cntrl:]]*\.claude|fallback[^[:cntrl:]]*\.claude|\.claude[^[:cntrl:]]*project-specific|CLAUDE\.md' src_codex; then
    fail "Codex files must use plugins/scope and AGENTS.md, not .claude overrides or CLAUDE.md"
  fi

  grep -n "Do not read \`.claude/\`" src_codex/skills/scope-workflows/SKILL.md
  grep -n "Follow repository instructions in \`AGENTS.md\`" src_codex/skills/scope-workflows/SKILL.md
}

check_codex_invocation() {
  section "Check Codex invocation"

  if grep -R -n -E -- '--ask-for-approval([[:space:]]|$)' src_shared src_claude src_codex; then
    fail "Codex exec no longer supports --ask-for-approval; use supported flags only"
  fi

  if grep -R -n -F 'gpt-5.5' src_shared/commands/epic_refine.md src_shared/commands/epic_refine src_shared/commands/audit_epic.md src_shared/commands/audit_epic; then
    fail "OpenAI architecture and audit reviewer defaults must use gpt-5.6-terra"
  fi

  grep -n "codex exec" src_shared/commands/audit_epic.md
  grep -n "codex exec" src_shared/commands/epic_refine.md
  grep -n -- "--sandbox read-only" src_shared/commands/audit_epic.md
  grep -n -- "--sandbox read-only" src_shared/commands/epic_refine.md
  grep -n "fresh reviewer process" src_shared/commands/audit_epic.md
  grep -n "fresh process" src_shared/commands/epic_refine.md
  grep -n 'SCOPE_CODEX_MODEL_ID:-gpt-5.6-terra' src_shared/commands/audit_epic.md
  grep -n 'SCOPE_CODEX_MODEL_ID:-gpt-5.6-terra' src_shared/commands/epic_refine.md
  grep -n 'SCOPE_CODEX_REASONING_EFFORT:-high' src_shared/commands/audit_epic.md
  grep -n 'SCOPE_CODEX_REASONING_EFFORT:-high' src_shared/commands/epic_refine.md
  grep -n '^model: gpt-5.6-terra$' src_codex/agents/developer.md
  grep -n '^model_reasoning_effort: max$' src_codex/agents/developer.md
}

check_claude_invocation() {
  section "Check Claude invocation"

  if grep -R -n -E 'Claude Opus 4\.7|Opus 4\.7|claude-opus-4\.7' src_shared src_claude src_codex; then
    fail "Claude reviewer must use local Opus alias naming, not a stale pinned Opus version label"
  fi

  if grep -R -n -E 'permission-mode (acceptEdits|bypassPermissions)' src_shared/commands/audit_epic.md src_shared/commands/epic_refine.md; then
    fail "Claude reviewer automation must use --dangerously-skip-permissions to avoid interactive permission prompts"
  fi

  grep -n "Claude Opus (local alias)" src_shared/commands/audit_epic.md
  grep -n "Claude Opus (local alias)" src_shared/commands/epic_refine.md
  grep -n -- "--dangerously-skip-permissions" src_shared/commands/audit_epic.md
  grep -n -- "--dangerously-skip-permissions" src_shared/commands/epic_refine.md
  grep -n "Before terminating Claude, inspected PTY log" src_shared/scripts/scope-reviewer-claude-pexpect.py
  grep -n "Last PTY log lines before termination" src_shared/scripts/scope-reviewer-claude-pexpect.py
}

check_command_expectations() {
  local command

  section "Check v2 command expectations"

  for command in implement wrap_epic; do
    test -f "src_claude/commands/${command}.md"
    test -f "src_codex/commands/${command}.md"
  done

  test -f src_shared/commands/audit_epic/reviewer-audit.md
  test -f src_shared/commands/epic_refine/reviewer-refinement.md
  grep -n "Do not invoke another reviewer" src_shared/commands/audit_epic/reviewer-audit.md
  grep -n "invoke another reviewer" src_shared/commands/epic_refine/reviewer-refinement.md
  grep -n "Reviewer identity" src_shared/commands/audit_epic/reviewer-audit.md
  grep -n "Reviewer identity" src_shared/commands/epic_refine/reviewer-refinement.md

  grep -n "Nested Scope Command Execution" src_codex/skills/scope-workflows/SKILL.md
  grep -n "audit-findings.yaml" src_claude/commands/implement.md
  grep -n "audit-findings.yaml" src_codex/commands/implement.md
  grep -n "targeted_verification_count" src_shared/commands/epic_refine.md
  grep -n "targeted-verification-NNN" src_shared/commands/epic_refine.md
  grep -n "tmp_debug/scope-audit" src_shared/commands/audit_epic.md
  grep -n "tmp_debug.*scope-reviewer-logs" src_shared/scripts/scope-reviewer-claude-pexpect.py

  if grep -R -n -E 'LEGACY_VALIDATOR|legacy input mode|maximum_followups|minimum_followups|followup_count|followup-[0-9N]' \
    src_shared/commands/epic_refine.md \
    src_shared/commands/audit_epic.md \
    src_claude/commands/implement.md \
    src_codex/commands/implement.md; then
    fail "v2 commands must not contain legacy workflow fallbacks or old follow-up names"
  fi
}

check_v2_tests() {
  local python_cmd

  section "Run v2 validator tests and coverage"

  python_cmd="${SCOPE_PYTHON:-python3}"
  command -v "$python_cmd" >/dev/null 2>&1 || fail "Python is required; set SCOPE_PYTHON to a Python 3 executable"
  "$python_cmd" -c 'import coverage, pytest, yaml' >/dev/null 2>&1 ||
    fail "Missing Python dependencies; run: python3 -m pip install -r requirements-dev.txt"

  mkdir -p tmp_debug
  PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE=tmp_debug/.coverage-v2 "$python_cmd" -m coverage erase
  PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE=tmp_debug/.coverage-v2 "$python_cmd" -m coverage run -m pytest -q tests/unit
  PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE=tmp_debug/.coverage-v2 "$python_cmd" -m coverage report \
    --fail-under=90 \
    --include='*/src_shared/scripts/validate-refinement.py,*/src_shared/scripts/audit-artifacts.py'
}

main() {
  local range

  range="$(diff_range "${1:-}")"

  check_whitespace "$range"
  check_generated_files
  check_mirrors "$range"
  check_install
  check_windows_installer
  check_git_hooks
  check_actions_runtime
  check_codex_plugin_naming
  check_codegraph_guidance
  check_codex_override_sources
  check_codex_invocation
  check_claude_invocation
  check_command_expectations
  check_v2_tests

  section "All PR checks passed"
}

main "$@"
