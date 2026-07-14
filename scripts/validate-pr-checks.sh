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

  section "Install smoke test"

  tmpdir="$(mktemp -d)"
  ./install.sh "$tmpdir" >/tmp/scope-install-smoke.log

  test -f "$tmpdir/.claude/commands/wrap_epic.md"
  test -f "$tmpdir/.claude/commands/implement.md"
  test -f "$tmpdir/.claude/commands/audit_epic.md"
  test -f "$tmpdir/.claude/agents/developer.md"

  test -f "$tmpdir/plugins/scope/commands/wrap_epic.md"
  test -f "$tmpdir/plugins/scope/commands/implement.md"
  test -f "$tmpdir/plugins/scope/commands/audit_epic.md"
  test -f "$tmpdir/plugins/scope/agents/developer.md"
  test -f "$tmpdir/plugins/scope/.codex-plugin/plugin.json"

  test -d "$tmpdir/.claude/commands/audit_epic"
  test -d "$tmpdir/plugins/scope/commands/audit_epic"

  test -f "$tmpdir/.claude/skills/project-documentation/SKILL.md"
  test -f "$tmpdir/plugins/scope/skills/project-documentation/SKILL.md"
  grep -n "Path selection rule" "$tmpdir/.claude/skills/project-documentation/SKILL.md"
  grep -n "docs/architecture/backend/01-intro.md" "$tmpdir/.claude/skills/project-documentation/SKILL.md"
  grep -n "Path selection rule" "$tmpdir/plugins/scope/skills/project-documentation/SKILL.md"
  grep -n "docs/architecture/backend/01-intro.md" "$tmpdir/plugins/scope/skills/project-documentation/SKILL.md"
  grep -n '^model: sonnet$' "$tmpdir/.claude/agents/developer.md"
  grep -n '^model: gpt-5.6-terra$' "$tmpdir/plugins/scope/agents/developer.md"
  grep -n '^model_reasoning_effort: max$' "$tmpdir/plugins/scope/agents/developer.md"
  grep -n 'Model requirement: `gpt-5.6-terra` with high reasoning.' "$tmpdir/.claude/commands/epic_refine/reviewer-architecture-codex.md"
  grep -n 'Model requirement: `gpt-5.6-terra` with high reasoning.' "$tmpdir/.claude/commands/audit_epic/reviewer-codex.md"
  grep -n 'Model requirement: `gpt-5.6-terra` with high reasoning.' "$tmpdir/plugins/scope/commands/epic_refine/reviewer-architecture-codex.md"
  grep -n 'Model requirement: `gpt-5.6-terra` with high reasoning.' "$tmpdir/plugins/scope/commands/audit_epic/reviewer-codex.md"

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

  for required_path in commands scripts skills agents governance docs .codex-plugin; do
    grep -n "${required_path}" install.bat >/dev/null
  done

  grep -n 'config_example.yaml' install.bat
  grep -n 'scope-reviewer-tmux.sh' install.bat
  grep -n 'reviewer-gemini.md' install.bat
  grep -n 'reviewer-architecture-gemini.md' install.bat
  grep -n 'install.bat --user' README.md
  grep -n 'install.bat "C:\\path\\to\\your-project"' README.md
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

  if grep -R -n -E 'Do not use CodeGraph MCP|CodeGraph MCP is intentionally disabled|not MCP' src_shared/commands src_claude/commands src_codex/commands src_codex/skills; then
    fail "found stale CodeGraph MCP prohibition"
  fi

  grep -n "Prefer CodeGraph MCP" src_shared/commands/epic_refine.md
  grep -n "Prefer CodeGraph MCP" src_claude/commands/implement.md
  grep -n "Prefer CodeGraph MCP" src_codex/commands/implement.md
}

check_codex_override_sources() {
  section "Check Codex override sources"

  if grep -R -n -E 'prefer[^[:cntrl:]]*\.claude|fallback[^[:cntrl:]]*\.claude|\.claude[^[:cntrl:]]*project-specific|CLAUDE\.md' src_codex; then
    fail "Codex files must use plugins/scope and AGENTS.md, not .claude overrides or CLAUDE.md"
  fi

  grep -n "Do not read \`.claude/\`" src_codex/skills/scope-workflows/SKILL.md
  grep -n "Follow repository instructions in \`AGENTS.md\`" src_codex/skills/scope-workflows/SKILL.md
}

check_agy_invocation() {
  section "Check Antigravity invocation"

  if grep -R -n -E 'SCOPE_AGY_MODEL:-gemini-|SCOPE_AGY_FALLBACK_MODEL:-gemini-|AGY_REVIEW_MODEL=.*gemini-|AGY_FALLBACK_MODEL=.*gemini-' src_shared src_claude src_codex; then
    fail "Antigravity model defaults must use exact display labels from agy models"
  fi

  if grep -R -n -E 'agy[[:space:]]+--print[[:space:]]+--' src_shared src_claude src_codex; then
    fail "Antigravity --print must receive prompt text, not another flag"
  fi

  grep -n 'Gemini 3.1 Pro (High)' src_shared/commands/audit_epic.md
  grep -n 'Gemini 3.1 Pro (High)' src_shared/commands/epic_refine.md
  grep -n -- '--print "$prompt_text"' src_shared/commands/audit_epic.md
  grep -n -- '--print "$AGY_PROMPT_TEXT"' src_shared/commands/epic_refine.md
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
  grep -n -- "--sandbox read-only" src_shared/commands/audit_epic.md
  grep -n -- "--sandbox read-only" src_shared/commands/epic_refine.md
  grep -n "stale approval flags" src_shared/commands/epic_refine.md
  grep -n 'SCOPE_CODEX_MODEL_ID:-gpt-5.6-terra' src_shared/commands/audit_epic.md
  grep -n 'SCOPE_CODEX_MODEL_ID:-gpt-5.6-terra' src_shared/commands/epic_refine.md
  grep -n 'SCOPE_CODEX_REASONING_EFFORT:-high' src_shared/commands/audit_epic.md
  grep -n 'SCOPE_CODEX_REASONING_EFFORT:-high' src_shared/commands/epic_refine.md
  grep -n 'Model requirement: `gpt-5.6-terra` with high reasoning.' src_shared/commands/audit_epic/reviewer-codex.md
  grep -n 'Model requirement: `gpt-5.6-terra` with high reasoning.' src_shared/commands/epic_refine/reviewer-architecture-codex.md
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

  grep -n "claude-opus.md" src_shared/commands/audit_epic.md
  grep -n "claude-opus.md" src_shared/commands/epic_refine.md
  grep -n "Claude Opus (local alias)" src_shared/commands/audit_epic.md
  grep -n "Claude Opus (local alias)" src_shared/commands/epic_refine.md
  grep -n -- "--dangerously-skip-permissions" src_shared/commands/audit_epic.md
  grep -n -- "--dangerously-skip-permissions" src_shared/commands/epic_refine.md
  grep -n "Before manually treating Claude as hung" src_shared/commands/audit_epic.md
  grep -n "Before manually treating Claude as hung" src_shared/commands/epic_refine.md
  grep -n "Before terminating Claude, inspected PTY log" src_shared/scripts/scope-reviewer-claude-pexpect.py
  grep -n "Last PTY log lines before termination" src_shared/scripts/scope-reviewer-claude-pexpect.py
  grep -n "Bash(grep:\\*)" src_shared/commands/audit_epic.md
  grep -n "Bash(grep:\\*)" src_shared/commands/epic_refine.md
  grep -n "Bash(echo:\\*)" src_shared/commands/audit_epic.md
  grep -n "Bash(echo:\\*)" src_shared/commands/epic_refine.md
  grep -n "Bash(printf:\\*)" src_shared/commands/audit_epic.md
  grep -n "Bash(printf:\\*)" src_shared/commands/epic_refine.md
  grep -n "Bash(for:\\*)" src_shared/commands/audit_epic.md
  grep -n "Bash(for:\\*)" src_shared/commands/epic_refine.md
  grep -n "Bash(which:\\*)" src_shared/commands/audit_epic.md
  grep -n "Bash(which:\\*)" src_shared/commands/epic_refine.md
  grep -n "Bash(python -c:\\*)" src_shared/commands/audit_epic.md
  grep -n "Bash(python -c:\\*)" src_shared/commands/epic_refine.md
}

check_command_expectations() {
  local command
  local reviewer

  section "Check mirrored command expectations"

  for command in implement wrap_epic; do
    test -f "src_claude/commands/${command}.md"
    test -f "src_codex/commands/${command}.md"
  done

  for reviewer in reviewer-codex reviewer-claude reviewer-agy reviewer-glm; do
    test -f "src_shared/commands/audit_epic/${reviewer}.md"
    grep -n "not the Scope orchestrator" "src_shared/commands/audit_epic/${reviewer}.md"
    grep -n "any other reviewer" "src_shared/commands/audit_epic/${reviewer}.md"
  done

  for reviewer in reviewer-architecture-codex reviewer-architecture-claude reviewer-architecture-agy reviewer-architecture-glm; do
    test -f "src_shared/commands/epic_refine/${reviewer}.md"
    grep -n "not the Scope orchestrator" "src_shared/commands/epic_refine/${reviewer}.md"
    grep -n "any other reviewer" "src_shared/commands/epic_refine/${reviewer}.md"
  done

  grep -n "Nested Scope Command Execution" src_codex/skills/scope-workflows/SKILL.md
  grep -n "zai-coding-plan/glm-5.2" src_shared/commands/audit_epic.md
  grep -n "zai-coding-plan/glm-5.2" src_shared/commands/epic_refine.md
  grep -n -- '--variant "high"' src_shared/commands/audit_epic.md
  grep -n -- '--variant "high"' src_shared/commands/epic_refine.md
  grep -n "glm-5.2.md" src_shared/commands/audit_epic.md
  grep -n "glm-5.2.md" src_shared/commands/epic_refine.md
  grep -n "skip GLM silently" src_shared/commands/audit_epic.md
  grep -n "skip GLM silently" src_shared/commands/epic_refine.md
  grep -n "not an informal audit" src_claude/commands/implement.md
  grep -n "not an informal audit" src_codex/commands/implement.md
  grep -n "review-metadata.yaml" src_claude/commands/implement.md
  grep -n "review-metadata.yaml" src_codex/commands/implement.md
  grep -n "runtime_evidence.required: true" src_claude/commands/implement.md
  grep -n "runtime_evidence.required: true" src_codex/commands/implement.md
  grep -n "Missing live smoke wiring is an implementation gap" src_claude/commands/implement.md
  grep -n "Missing live smoke wiring is an implementation gap" src_codex/commands/implement.md
  grep -n "Runtime-required rows not deferred to audit" src_shared/governance/developer-checklist.md
  grep -n "Audit Boundary and Artifact Policy" src_shared/commands/audit_epic.md
  grep -n "Never delete, rename, compact, or rewrite" src_shared/commands/audit_epic.md
  grep -n "tmp_debug/scope-audit" src_shared/commands/audit_epic.md
  grep -n "tmp_debug.*scope-reviewer-logs" src_shared/scripts/scope-reviewer-claude-pexpect.py
}

main() {
  local range

  range="$(diff_range "${1:-}")"

  check_whitespace "$range"
  check_generated_files
  check_mirrors "$range"
  check_install
  check_windows_installer
  check_codex_plugin_naming
  check_codegraph_guidance
  check_codex_override_sources
  check_agy_invocation
  check_codex_invocation
  check_claude_invocation
  check_command_expectations

  section "All PR checks passed"
}

main "$@"
