---
name: audit_epic
description: Audit epic implementation against original architecture and ADRs. Detects divergence and creates fix plan.
args: "{epic-id}"
skills: project-documentation
---

# /audit_epic

Audit an epic's implementation to detect divergence from original architecture, ADRs, and requirements. Produces a comprehensive audit report with prioritized fix plan.

**Syntax:** `/audit_epic {epic-id}`

**Output:** `docs/epics/{epic-dir}/epic_audit.md`

## Definition of Done

`/audit_epic` is not complete when `epic_audit.md` is written.

The command is complete only when one of these conditions is true:

1. The latest audit attempt has no open `CRITICAL` findings, no open `MAJOR` findings, and no easy/local `MINOR` auto-fix findings.
2. All remaining findings are classified as `ASK USER`, `DEFERRED DOC DECISION`, or `DO NOT FIX` with evidence.
3. The audit has reached 3 total attempts and remaining `CRITICAL` or `MAJOR` findings are documented as an unresolved audit failure.
4. Remediation is blocked by an external dependency, credential, destructive migration decision, product/architecture/security decision, or repeated tool failure, and the blocker is documented in `epic_audit.md`.

If any `AUTO-FIX` finding exists, the responsible implementation agent must immediately remediate it, run the relevant focused tests, and run `/audit_epic {epic-id}` again. Do not stop after producing a failing audit report.

`AUTO-FIX` means:

- all `CRITICAL` findings
- all `MAJOR` findings
- `MINOR` findings that are easy, local, mechanical, and low-risk

Maximum audit attempts: 3 total.
Maximum remediation cycles: 2.

### Audit Attempt Accounting

The 3-attempt cap is a hard execution ceiling, not guidance.

Count a run as an audit attempt when it performs any full audit decision step, including deterministic matrix review, external reviewer collection, same-agent exploratory residual review, or final finding classification.

Do not bypass the cap by creating "local evidence", "focused verification", "partial review", or "rerun" directories. Local evidence collection is part of remediation inside the current attempt; it may add command output files to the active attempt directory, but it does not reset the attempt count and must not be followed by a fourth full/reviewer audit.

Before launching reviewers or starting final classification, count the full/reviewer audit attempts already performed in the current audit cycle. If 3 attempts have already run, stop. Update `epic_audit.md` with `FAIL`, unresolved findings, evidence collected, and the reason no further audit pass was allowed.

The audit loop is:

1. Run deterministic matrix review, external reviewers, and same-agent exploratory residual review.
2. Classify findings and update `epic_audit.md`, `audit-verification-matrix.yaml`, and `audit-issue-ledger.yaml`.
3. If `AUTO-FIX` findings exist and fewer than 3 total audit attempts have run, remediate immediately, run focused tests, and start the next audit attempt.
4. If attempt 3 still has open `CRITICAL` or `MAJOR` findings, stop and mark the audit as failed with unresolved issues.

The final response to the user must report the latest audit status after remediation, not the first failing audit status.

### Audit Boundary and Artifact Policy

`/audit_epic` may remediate `AUTO-FIX` findings only through the controlled loop above. Do not turn one audit attempt into repeated ad hoc reviewer passes.

One audit attempt has one deterministic review, one external reviewer collection, one same-agent residual review, one merged classification, and one report update. If remediation changes code or tests and another full review is needed, create the next `reviews/audit-NNN/` attempt. Do not create `pre-final`, `rerun`, `focused-review`, or similar reviewer outputs inside the same attempt directory.

Never delete, rename, compact, or rewrite an existing `reviews/audit-NNN/` directory. Superseded attempts remain audit evidence. If an attempt was noisy or failed, keep it and explain its status in `review-metadata.yaml`, `audit-issue-ledger.yaml`, and the next `epic_audit.md` update.

Commit-worthy audit artifacts are concise evidence and decisions:

- reviewer prompt files
- final reviewer markdown files
- reviewer unavailable/failure markdown summaries
- `review-metadata.yaml`
- `exploratory-residual-review.md`
- concise scripted gate outputs that prove pass/fail status
- `audit-manifest.yaml`
- `audit-verification-matrix.yaml`
- `audit-issue-ledger.yaml`
- `epic_audit.md`

Bulky runtime logs, PTY transcripts, CLI debug streams, repeated stderr dumps, and full console transcripts are not audit artifacts. Store them under `tmp_debug/scope-audit/{epic-id}/{audit-NNN}/` or `tmp_debug/scope-reviewer-logs/`, summarize the relevant lines in a markdown artifact, and do not commit the bulky raw files unless the user explicitly asks.

If an audit attempt directory grows beyond 1 MB, inspect the largest files before committing. Move non-essential raw logs to `tmp_debug/`, replace them with concise summaries, and keep only evidence needed to explain pass/fail decisions.

## Preferred Multi-Model Review

Every audit should gather independent reviewer feedback before the final audit report is classified when the relevant tools are available:

| Reviewer | Required model | Prompt source | Output |
|----------|----------------|---------------|--------|
| Codex | `gpt-5.6-terra` with high reasoning | `commands/audit_epic/reviewer-codex.md` | `docs/epics/{epic-dir}/reviews/audit-NNN/codex-gpt-5.6-terra-high.md` |
| Claude | Opus via local `opus` alias | `commands/audit_epic/reviewer-claude.md` | `docs/epics/{epic-dir}/reviews/audit-NNN/claude-opus.md` |
| Antigravity | `Gemini 3.1 Pro (High)` with rate-limit fallback to `Gemini 3.5 Flash (High)` | `commands/audit_epic/reviewer-agy.md` | `docs/epics/{epic-dir}/reviews/audit-NNN/agy-gemini-3.1-pro-high.md` or fallback `agy-gemini-3.5-flash.md` |
| GLM | Optional `zai-coding-plan/glm-5.2` through opencode | `commands/audit_epic/reviewer-glm.md` | `docs/epics/{epic-dir}/reviews/audit-NNN/glm-5.2.md` |

Codex uses `gpt-5.6-terra` as the model id and `high` as reasoning effort. `gpt-5.6-terra-high` is only a review label/output filename and must never be passed to `codex --model`.

These reviewers are read-only auditors. They do not edit files and do not decide what to fix. The orchestrating audit command merges their findings, removes duplicates, assigns severities, and produces the fix plan for the responsible implementation agent.

Reviewer tools are optional. If Codex, Claude, Antigravity, or a required model is unavailable or not configured in the user's environment, record the failure in the current audit attempt directory as `{reviewer}-unavailable.md` and continue with the reviewers that are available. Do not mark the audit as `FAIL` solely because an external reviewer tool is missing. The audit report must disclose which reviewers completed and which were unavailable.

GLM through `opencode` is an optional additional reviewer. If `opencode`, the configured GLM model, or the invocation fails, skip GLM silently: do not create `glm-unavailable.md`, do not fail the audit, and do not classify reviewer coverage as incomplete. If GLM completes and writes `glm-5.2.md`, import its findings like any other reviewer output and record successful metadata.

Model reviews are never overwritten. Each audit run writes to a new `reviews/audit-NNN/` directory.

Each audit attempt also writes `reviews/audit-NNN/review-metadata.yaml` with reviewer transport, session, start/end timestamps, duration, timeout, retry count, status, and output file.

Reviewer markdown files are stable audit artifacts. Raw reviewer process logs are debugging artifacts and must stay outside the epic docs folder unless explicitly summarized.

## Remediation Policy

The responsible implementation agent must fix these findings without asking the user:

- all `CRITICAL` findings
- all `MAJOR` findings
- `MINOR` findings that are easy, local, mechanical, and low-risk

Ask the user only for findings that require a product decision, architecture decision, security tradeoff, destructive migration, external credential, or scope change. Documentation sync recommendations remain decision-gated as described in Phase 8.

## When to Run

| Trigger | Use Case |
|---------|----------|
| After Auto Claude completes | Verify implementation matches design |
| Before merging to main | Gate check for architectural compliance |
| After discovering bugs | Determine if root cause is architectural drift |
| Periodic review | Quarterly audit of implemented epics |

---

## What Gets Audited

```
/audit_epic {epic-id}

SOURCES:
├── Our architecture: docs/epics/{epic-id}/architecture.md
├── Our ADRs: docs/epics/{epic-id}/adr.md
├── Acceptance criteria: docs/epics/{epic-id}/acceptance-criteria.md
├── Acceptance traceability: docs/epics/{epic-id}/acceptance-traceability.yaml
├── Lint findings: docs/epics/{epic-id}/lint_findings.yaml (if exists)
├── Audit manifest: docs/epics/{epic-id}/audit-manifest.yaml
├── Audit verification matrix: docs/epics/{epic-id}/audit-verification-matrix.yaml
├── Issue ledger: docs/epics/{epic-id}/audit-issue-ledger.yaml
├── Codex review if available: docs/epics/{epic-id}/reviews/audit-NNN/codex-gpt-5.6-terra-high.md
├── Claude review if available: docs/epics/{epic-id}/reviews/audit-NNN/claude-opus.md
├── Antigravity review if available: docs/epics/{epic-id}/reviews/audit-NNN/agy-gemini-3.1-pro-high.md
├── GLM review if opencode is available: docs/epics/{epic-id}/reviews/audit-NNN/glm-5.2.md
├── Reviewer metadata: docs/epics/{epic-id}/reviews/audit-NNN/review-metadata.yaml
├── Auto Claude spec: .auto-claude/specs/*/spec.md
└── Implemented code: .auto-claude/worktrees/tasks # The auto-claude ID is the same as the folder that has the relevant spec.md

AUDIT CHECKS:
├── 1. Architecture Compliance
│   ├── Components match design
│   ├── APIs match contracts
│   └── Data models match schemas
│
├── 2. ADR Compliance
│   ├── Technology decisions followed
│   ├── Patterns applied correctly
│   └── Constraints respected
│
├── 3. Acceptance Criteria
│   ├── All scenarios implemented
│   ├── Edge cases handled
│   ├── Error scenarios covered
│   └── Each story meets the 90%+ automated coverage floor (or has an approved exception)
│
├── 4. Auto Claude Spec Alignment
│   ├── Spec matches our architecture
│   ├── Implementation matches spec
│   └── Test coverage as specified
│
├── 5. Code Quality
│   ├── Follows project patterns
│   ├── Error handling consistent
│   └── Documentation complete
│
├── 6. Stub/Placeholder Detection
│   ├── No placeholder/TODO/stub markers in production code
│   ├── Intent I/O verbs matched by real I/O in implementation
│   └── No functions returning literals without performing stated action
│
├── 7. Lint & Contract Compliance
│   ├── Ingest lint_findings.yaml (ruff + vulture + mypy from epic-wide check)
│   ├── Remaining ruff violations → MAJOR severity
│   ├── Dead code (vulture) → MAJOR severity
│   └── mypy --strict errors → CRITICAL severity (contract violations)
│
└── 8. Documentation Sync (Reverse Audit)
    ├── Do architecture docs reflect what was actually built?
    ├── Read legacy backend/frontend docs as context if present, but do not
    │   treat them as satisfying the new documentation format
    ├── Check: backend/13-specs/database/ and schemas match implemented schema
    ├── Check: backend/05-building-blocks.md and backend/06-runtime.md match implemented services
    ├── Check: 05-building-blocks.md includes new components
    ├── Check: 03-context.md reflects new external dependencies
    ├── Check: 08-cross-cutting/domain.md includes new domain entities
    ├── Check: 12-glossary.md includes new technical terms
    ├── Check: product/reference/terminology-data-model.md includes new terms
    ├── Check: product/decisions.md includes epic PDRs
    └── Check: 09-adr-summary.md includes epic ADRs

OUTPUT:
└── docs/epics/{epic-dir}/epic_audit.md
    ├── Executive summary
    ├── Findings by severity
    ├── Root cause analysis
    └── Prioritized fix plan
```

---

## Execution

### Step 0: Initialize

```bash
EPIC_ID="{epic-id}"
EPIC_DIR=$(ls docs/epics/ | grep -i "^${EPIC_ID}" | head -1)

if [ -z "$EPIC_DIR" ]; then
  echo "Epic not found in docs/epics/"
  exit 1
fi

AUDIT_FILE="docs/epics/${EPIC_DIR}/epic_audit.md"
REVIEWS_DIR="docs/epics/${EPIC_DIR}/reviews"
mkdir -p "$REVIEWS_DIR"

ATTEMPT_NUM=$(find "$REVIEWS_DIR" -maxdepth 1 -type d -name 'audit-[0-9][0-9][0-9]' 2>/dev/null | sed 's/.*audit-//' | sort -n | tail -1)
if [ -z "$ATTEMPT_NUM" ]; then
  ATTEMPT_NUM=1
else
  ATTEMPT_NUM=$((10#$ATTEMPT_NUM + 1))
fi

ATTEMPT_ID=$(printf "audit-%03d" "$ATTEMPT_NUM")
ATTEMPT_DIR="${REVIEWS_DIR}/${ATTEMPT_ID}"
mkdir -p "$ATTEMPT_DIR"

MANIFEST_FILE="docs/epics/${EPIC_DIR}/audit-manifest.yaml"
VERIFICATION_MATRIX_FILE="docs/epics/${EPIC_DIR}/audit-verification-matrix.yaml"
ISSUE_LEDGER_FILE="docs/epics/${EPIC_DIR}/audit-issue-ledger.yaml"
CHANGED_FILES_FILE="docs/epics/${EPIC_DIR}/changed-files.txt"
REVIEW_METADATA_FILE="${ATTEMPT_DIR}/review-metadata.yaml"
AUDIT_TMP_DIR="tmp_debug/scope-audit/${EPIC_ID}/${ATTEMPT_ID}"
mkdir -p "$AUDIT_TMP_DIR"

cat > "$REVIEW_METADATA_FILE" <<EOF
epic_id: "${EPIC_ID}"
attempt_id: "${ATTEMPT_ID}"
created_at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
reviews:
EOF

# Generate the changed-file manifest once, before CodeGraph sync and reviewer
# launch. Reviewers may use this as input to read-only impact queries.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  DEFAULT_BRANCH=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
  if [ -z "$DEFAULT_BRANCH" ]; then
    for candidate in main master trunk; do
      if git rev-parse --verify --quiet "$candidate" >/dev/null || git rev-parse --verify --quiet "origin/$candidate" >/dev/null; then
        DEFAULT_BRANCH="$candidate"
        break
      fi
    done
  fi

  BASE_REF=""
  if [ -n "$DEFAULT_BRANCH" ]; then
    if git rev-parse --verify --quiet "origin/$DEFAULT_BRANCH" >/dev/null; then
      BASE_REF=$(git merge-base HEAD "origin/$DEFAULT_BRANCH" 2>/dev/null || true)
    elif git rev-parse --verify --quiet "$DEFAULT_BRANCH" >/dev/null; then
      BASE_REF=$(git merge-base HEAD "$DEFAULT_BRANCH" 2>/dev/null || true)
    fi
  fi

  {
    if [ -n "$BASE_REF" ]; then
      git diff --name-only "$BASE_REF"...HEAD
    fi
    git diff --name-only
    git diff --cached --name-only
    git ls-files --others --exclude-standard
  } | sort -u | grep -F -x -v "$CHANGED_FILES_FILE" | while IFS= read -r path; do
    if [ -n "$path" ] && [ -e "$path" ]; then
      printf '%s\n' "$path"
    fi
  done > "$CHANGED_FILES_FILE"
else
  : > "$CHANGED_FILES_FILE"
fi

# CodeGraph is owned by the audit orchestrator, not by external reviewers.
# Always initialize/index or sync the active repo/worktree when audit_epic
# starts so reviewers can use read-only query commands against current code
# without taking write locks. External reviewers must never run CodeGraph
# maintenance/write commands.
if command -v codegraph >/dev/null 2>&1; then
  if [ ! -d ".codegraph" ]; then
    codegraph init . && codegraph index . || {
      echo "CodeGraph initial index failed. Continue the audit, but record CodeGraph as unavailable for reviewer query context." > "${ATTEMPT_DIR}/codegraph-unavailable.md"
    }
  else
    codegraph sync-if-dirty . || codegraph sync . || {
      echo "CodeGraph sync failed. Continue the audit, but record CodeGraph as unavailable for reviewer query context." > "${ATTEMPT_DIR}/codegraph-unavailable.md"
    }
  fi
  codegraph status . > "${ATTEMPT_DIR}/codegraph-status.txt" 2>&1 || true
else
  echo "CodeGraph CLI not found. Reviewers may still use read-only CodeGraph MCP if it is available and healthy; otherwise continue without CodeGraph query context." > "${ATTEMPT_DIR}/codegraph-unavailable.md"
fi
```

### Step 1: Load Sources

```python
# Our design documents
architecture = Read(f"docs/epics/{epic_dir}/architecture.md")
adrs = Read(f"docs/epics/{epic_dir}/adr.md")
acceptance_criteria = Read(f"docs/epics/{epic_dir}/acceptance-criteria.md")
acceptance_traceability = read_yaml(f"docs/epics/{epic_dir}/acceptance-traceability.yaml")

# Auto Claude spec
ac_spec = find_auto_claude_spec(epic_id)  # grep -l epic-id in .auto-claude/specs/*/spec.md

# Implementation
implemented_files = scan_implementation(epic_id)
```

---

## Step 2: Generate Deterministic Audit Manifest

Before model review, generate `docs/epics/{epic-dir}/audit-manifest.yaml`. The manifest is the deterministic scope of the audit and must not depend on what any reviewer happens to notice.

Include:

- binding obligations and candidate file hints from every `file-plan-story-*.yaml`
- all implementation and test files from `acceptance-traceability.yaml`
- all implementation proof from `implementation-evidence.yaml` when present
- all files changed in git for the epic branch/worktree, generated in `docs/epics/{epic-dir}/changed-files.txt`
- API, schema, migration, worker, queue, dashboard, and storage files touched indirectly by changed imports or routes
- tests touching those modules
- missing or stale boundary-plan referenced paths
- required runtime evidence commands from `acceptance-traceability.yaml`

Required format:

```yaml
epic_id: {epic-id}
attempt_id: audit-001
generated_at: YYYY-MM-DDTHH:MM:SSZ
changed_files_path: docs/epics/{epic-dir}/changed-files.txt
files:
  from_boundary_plans: []
  from_traceability: []
  changed_in_git: []
  indirectly_touched: []
  tests: []
missing_paths: []
runtime_evidence_required: []
scripted_gates:
  boundary_plan_path_validation: pending
  acceptance_traceability_validation: pending
  contract_parity: pending
  schema_openapi_enum_parity: pending
  ruff_mypy_vulture: pending
  real_pg_queue: pending
  live_smoke_status_matrix: pending
```

If `missing_paths` is non-empty, create a `MAJOR` finding before model review when the path is required by a binding contract, required touchpoint, proof obligation, or traceability row. Missing candidate-file paths are advisory context issues, not findings by themselves.

## Step 3: Generate Audit Verification Matrix

Before model review, generate `docs/epics/{epic-dir}/audit-verification-matrix.yaml` from `acceptance-traceability.yaml`, `audit-manifest.yaml`, boundary plans, changed files, implementation evidence, previous issue ledger rows, and known recurring risk dimensions.

This matrix is the primary audit contract. The audit is no longer a broad "find what you notice" review. Every required row must be evaluated as `pass`, `fail`, `unverified`, `blocked`, or `not_applicable`.

Required matrix shape:

```yaml
epic_id: {epic-id}
attempt_id: audit-001
generated_at: YYYY-MM-DDTHH:MM:SSZ
source_traceability: docs/epics/{epic-dir}/acceptance-traceability.yaml
source_manifest: docs/epics/{epic-dir}/audit-manifest.yaml
source_implementation_evidence: docs/epics/{epic-dir}/implementation-evidence.yaml
rows:
  - id: AC2.2-P10-REPROCESS-SERVICE
    source_acceptance_id: AC2.2
    story: "Story 6"
    category: behavior
    requirement: "Service focused pass 10 in reprocess mode requires current pass 9 before projection."
    priority: required
    risk_level: high
    dimensions:
      execution_surface: service
      pass_mode: reprocess
      pass_number: 10
      prior_state: missing_or_stale_dependency
    implementation:
      expected_files: []
      actual_files: []
    tests:
      expected_files: []
      required_assertions: []
      actual_tests: []
    runtime_evidence:
      required: false
      commands: []
      evidence: []
    reviewer_status:
      codex: pending
      claude: pending
      agy: pending
    final_status: pending
    audit_notes: ""
```

Required row fields:

- `id`: stable, unique row id. Use acceptance ids plus risk dimensions, not vague prose names.
- `requirement`: one concrete behavior or evidence obligation.
- `priority`: `required`, `runtime_required`, `high_risk`, `optional`, or `documentation`.
- `risk_level`: `critical`, `high`, `medium`, or `low`.
- `implementation.expected_files` and `tests.expected_files`: copied from traceability, implementation evidence, and binding boundary-plan touchpoints/proof obligations where paths are known. Candidate files are advisory hints only.
- `tests.required_assertions`: behavior that must be proven, not just test file names.
- `runtime_evidence.required`: true for smoke, migration, backfill, queue, service, or external integration requirements.
- `dimensions`: include relevant mode/state dimensions for orchestration-heavy epics.

For high-risk orchestration, queue, migration, storage, security, data integrity, or local/service parity work, expand broad acceptance items into matrix rows that cover the relevant state space. Examples:

- `execution_surface`: `service`, `local`, `worker`, `api`, `dashboard`
- `mode`: `idempotency`, `reprocess`, `only-pass`, `retry`, `resume`
- `prior_state`: `missing`, `stale`, `current`, `partial`, `duplicate`
- `data_shape`: `empty`, `single`, `multi`, `invalid`, `large`
- `failure_path`: `timeout`, `429`, `503`, `validation_error`, `permission_denied`

Do not let the matrix explode mechanically. Generate rows only for dimensions that are relevant to the epic, named in the acceptance criteria, implied by the architecture/ADRs, or historically risky in the touched code path.

### Matrix Status and Severity Rules

Use deterministic severity mapping:

| Matrix result | Row priority/risk | Finding severity |
|---------------|-------------------|------------------|
| `fail` | `runtime_required`, `required` with core behavior, data integrity, security, or destructive side effect | `CRITICAL` |
| `fail` | `required`, `high_risk` implementation/test coverage, architecture contract, or operational evidence | `MAJOR` |
| `unverified` | `runtime_required` or `required` row | `MAJOR` unless runtime evidence is the only acceptance proof, then `CRITICAL` |
| `unverified` | `high_risk` row | `MAJOR` |
| `unverified` | `optional` or `documentation` row | `MINOR` or documentation follow-up |
| `blocked` | needs user/product/security/credential/destructive migration decision | `ASK USER` |
| `not_applicable` | cited evidence shows the row is out of scope | no finding |

Missing proof is not automatically the same as a broken behavior. Label it `unverified` and map severity by row priority. Do not classify unverified optional/documentation rows as `CRITICAL`.

Unit tests passing must never downgrade a missing promised outcome. If a central promised benefit has no real-path evidence, or expected output is absent/zero without an explicit acceptance/boundary-plan statement that zero is valid, classify the row as `MAJOR` at minimum. Classify it as `CRITICAL` when the missing outcome is core acceptance behavior, the only proof path is runtime evidence, or the absence would make the epic's delivered value false.

### Follow-Up Audit Scope

On audit attempts after the first one, prioritize:

- all previously failed, blocked, or unverified matrix rows
- sibling rows with the same risk pattern or dimensions
- rows touched by the remediation diff
- required runtime evidence rows

Run a bounded fresh scan for new high-impact issues, but do not let follow-up audits repeatedly rediscover unrelated low-priority risks before failed matrix rows are resolved.

## Step 4: Run Scripted Pre-Audit Gates

Run or explicitly mark blocked for each gate in `audit-manifest.yaml` before model review:

- boundary-plan path validation
- acceptance traceability validation: every row has implementation files, required assertions, expected tests, and status
- implementation evidence validation: `implementation-evidence.yaml` exists when `/implement` produced code, `audit_ready` is true, and completed stories map to proof
- contract parity test
- schema/OpenAPI enum parity
- ruff, mypy, and vulture
- real Postgres queue test when the epic touches queue/database behavior
- live smoke status matrix when `runtime_evidence.required` is true

Scripted gates produce findings before LLM review. Do not let model reviewers be the only check for machine-verifiable issues.

Also validate `audit-verification-matrix.yaml` before model review:

- every `required`, `runtime_required`, and `high_risk` row has implementation files or an explicit reason why implementation is not applicable
- every `required`, `runtime_required`, and `high_risk` row has expected test files and required assertions, unless it is explicitly runtime-only
- every runtime-required row has a command and evidence field
- every row id is stable and unique
- every expected file path exists or is listed as a manifest missing path

### Fast-Fail Before External Review

Do not spend external reviewer time on an audit attempt whose deterministic
evidence package is mechanically incomplete.

Before launching Codex, Claude, Antigravity, or GLM, inspect the scripted gates
and matrix validation results. If any of these conditions exist, stop this
attempt before external reviewer launch:

- missing or stale paths for binding required/high-risk work
- `implementation-evidence.yaml` is missing after implementation has changed code
- `implementation-evidence.yaml` has `audit_ready: false`
- a completed story lacks mapped acceptance rows, changed files, tests, runtime
  evidence, or an explicit not-applicable reason
- a required/high-risk matrix row lacks implementation evidence
- a required/high-risk matrix row lacks test evidence and is not explicitly
  runtime-only
- a runtime-required row lacks a wired command, passing result, or evidence path

When fast-failing:
- write concise gate evidence into the current `reviews/audit-NNN/` directory
- update `audit-verification-matrix.yaml` with `fail`, `unverified`, or `blocked`
  statuses
- update `audit-issue-ledger.yaml`
- write `epic_audit.md` with `FAIL` or `BLOCKED`
- do not create reviewer prompt files
- do not launch external reviewers

This still counts as an audit attempt because it reaches final finding
classification. It should be rare when `/implement` followed its pre-audit
handoff rules; if it happens, the remediation target is the implementation
evidence/matrix gap, not reviewer disagreement.

## Step 5: Fix-Verification Audit

If this is not the first audit attempt, first verify previous findings from `audit-issue-ledger.yaml`:

- Did each previous `AUTO-FIX` item get fixed?
- Did the fix include an assertion or runtime evidence proving the issue stays fixed?
- Did the fix introduce a regression in the same call path?

Only after fix verification is complete should the command run a fresh audit for latent issues.

## Step 6: Gather Independent Reviewer Feedback

Before producing the final audit report, try to run all three preferred reviewers. Use the prompt files installed with this command and pass the epic id, epic directory, audit scope, repository root, changed-files path, and audit verification matrix path.

Reviewer execution is best-effort. Missing local tools, missing credentials, unavailable models, or local CLI incompatibilities must be recorded, not treated as a blocking audit failure. The audit should still proceed with scripted gates, local inspection, and any reviewer outputs that were successfully produced.

CodeGraph must already be initialized, indexed, and synced by this command before reviewers are launched when CLI CodeGraph is available. Reviewers must not run `codegraph init`, `codegraph sync`, `codegraph sync-if-dirty`, `codegraph mark-dirty`, `codegraph unlock`, `codegraph index`, or other write/maintenance commands. They are in read-only query mode only. Reviewers should use CodeGraph if present. Prefer read-only CodeGraph MCP when available and healthy because it can provide relationship context directly to the reviewer. If MCP is unavailable, unhealthy, or appears to hold a database lock, use read-only CLI commands instead: `codegraph status`, `codegraph query`, `codegraph context`, `codegraph files`, and `codegraph affected`. CodeGraph helps discover relationships, but findings and pass decisions still require direct source/test evidence.

Claude should be run through the `pexpect` one-shot file-output wrapper when
available because Claude CLI headless mode can be token-only or restricted in
some subscription environments. Do not use tmux pane scraping for Claude review
output.
Antigravity should use the direct `agy --print "prompt"` invocation.

- Claude receives a short one-shot instruction that points to the reviewer
  prompt file, repository/worktree path, and required output file.
- Claude writes the review report to `claude-opus.md` with wrapper-managed
  sentinels; the wrapper strips the sentinels before the file is consumed.
- Claude's allowed tools include common read-only shell inspection commands used
  during audits, while still excluding mutating commands.
- Claude requests are blocking until the output file is valid or the timeout
  expires.
- On Claude timeout, the wrapper inspects the live PTY log under
  `tmp_debug/scope-reviewer-logs/` before terminating the process and retrying
  once.
- Before manually treating Claude as hung, unavailable, or safe to kill,
  inspect the matching PTY log under `tmp_debug/scope-reviewer-logs/`. Empty
  wrapper stdout/stderr files in the audit attempt directory are not evidence
  that Claude is idle or blocked.
- If `pexpect`, `python3`, `claude`, or the wrapper is unavailable, record
  `claude-unavailable.md` and continue.
- Antigravity runs headless with `agy --model "Gemini 3.1 Pro (High)" --sandbox --dangerously-skip-permissions --print-timeout "$SCOPE_AGY_PRINT_TIMEOUT" --print "$PROMPT_TEXT"`. If the primary model is rate-limited, retry once with `Gemini 3.5 Flash (High)`.
- GLM runs only when `opencode` is available: `opencode run -m "zai-coding-plan/glm-5.2" --variant "high" --dir "$(pwd)" --dangerously-skip-permissions "$PROMPT_TEXT"`. If it is unavailable or fails, skip it silently.
- For follow-up attempts after `audit-001`, generate `reviews/audit-NNN/reviewer-packet.yaml` before launching reviewers. The packet narrows reviewer attention without hiding evidence:
  - previous failed, blocked, or unverified matrix rows
  - previous critical/major findings and closure evidence
  - remediation diff since the prior attempt
  - rows sharing the same risk pattern or dimensions as prior findings
  - runtime evidence added or changed since the prior attempt
  - changed files and sibling surfaces affected by the fix
- Required reviewer packet shape:

```yaml
epic_id: {epic-id}
attempt_id: audit-002
previous_attempt: audit-001
generated_at: YYYY-MM-DDTHH:MM:SSZ
review_mode: follow_up_delta
previous_findings:
  critical: []
  major: []
  minor_easy: []
rows_to_prioritize: []
sibling_risk_patterns: []
remediation_diff:
  base_ref: ""
  files_changed_since_previous_attempt: []
runtime_evidence_changed: []
bounded_fresh_scan:
  required: true
  focus: "new high-impact issues only"
```

- Reviewers must read `reviewer-packet.yaml` when present, prioritize it first,
  and then run a bounded fresh scan for new high-impact issues.
- Run independent reviewers in parallel by default after CodeGraph sync and
  prompt generation. Set `SCOPE_AUDIT_PARALLEL_REVIEWERS=0` to force sequential
  execution for troubleshooting.
- Parallel reviewers must not append concurrently to the same metadata file.
  Each reviewer writes to a reviewer-specific metadata file and the orchestrator
  merges them into `review-metadata.yaml` after all reviewer processes exit.
- Write timing/status data for every reviewer into `review-metadata.yaml`.

```bash
REVIEWER_PROMPT_DIR=$(find ./plugins/scope/commands/audit_epic ./.claude/commands/audit_epic ./src_shared/commands/audit_epic ~/.claude/commands/audit_epic -type d 2>/dev/null | head -1)
REVIEWER_CLAUDE_PEXPECT_SCRIPT=$(find ./plugins/scope/scripts ./.claude/commands/scripts ./src_shared/scripts ~/.claude/commands/scripts -name "scope-reviewer-claude-pexpect.py" 2>/dev/null | head -1)
REVIEW_TIMEOUT_SECONDS="${SCOPE_REVIEW_TIMEOUT_SECONDS:-3600}"
REVIEW_RETRIES="${SCOPE_REVIEW_RETRIES:-1}"
CODEX_MODEL_ID="${SCOPE_CODEX_MODEL_ID:-gpt-5.6-terra}"
CODEX_REASONING_EFFORT="${SCOPE_CODEX_REASONING_EFFORT:-high}"
CODEX_REVIEW_LABEL="${SCOPE_CODEX_REVIEW_LABEL:-${CODEX_MODEL_ID}-${CODEX_REASONING_EFFORT}}"
AGY_REVIEW_MODEL="${SCOPE_AGY_MODEL:-Gemini 3.1 Pro (High)}"
AGY_FALLBACK_MODEL="${SCOPE_AGY_FALLBACK_MODEL:-Gemini 3.5 Flash (High)}"
AGY_REVIEW_OUTPUT_ID="${SCOPE_AGY_OUTPUT_ID:-agy-gemini-3.1-pro-high}"
AGY_FALLBACK_OUTPUT_ID="${SCOPE_AGY_FALLBACK_OUTPUT_ID:-agy-gemini-3.5-flash}"
AGY_PRINT_TIMEOUT="${SCOPE_AGY_PRINT_TIMEOUT:-60m}"
GLM_REVIEW_MODEL="${SCOPE_GLM_MODEL:-zai-coding-plan/glm-5.2}"
GLM_REVIEW_OUTPUT_ID="${SCOPE_GLM_OUTPUT_ID:-glm-5.2}"
SCOPE_REVIEW_PYTHON="${SCOPE_REVIEW_PYTHON:-python3}"
SCOPE_AUDIT_PARALLEL_REVIEWERS="${SCOPE_AUDIT_PARALLEL_REVIEWERS:-1}"
CLAUDE_AUDIT_ALLOWED_TOOLS="Read,Glob,Grep,Bash(pwd),Bash(cd:*),Bash(ls:*),Bash(find:*),Bash(rg:*),Bash(grep:*),Bash(cat:*),Bash(sed:*),Bash(head:*),Bash(tail:*),Bash(wc:*),Bash(stat:*),Bash(file:*),Bash(which:*),Bash(echo:*),Bash(printf:*),Bash(for:*),Bash(python -c:*),Bash(python3 -c:*),Bash(git status:*),Bash(git rev-parse:*),Bash(git log:*),Bash(git diff:*),Bash(git show:*),Bash(git ls-files:*),Bash(git merge-base:*),Bash(git branch:*),Bash(git worktree list:*),Bash(codegraph status:*),Bash(codegraph query:*),Bash(codegraph context:*),Bash(codegraph files:*),Bash(codegraph affected:*),Write"

if [ -z "$REVIEWER_PROMPT_DIR" ]; then
  echo "Audit reviewer prompts not found"
  exit 1
fi

json_quote() {
  python3 -c 'import json, sys; print(json.dumps(sys.argv[1]))' "$1"
}

append_review_metadata() {
  local reviewer="$1"
  local model="$2"
  local transport="$3"
  local session="$4"
  local status="$5"
  local started_at="$6"
  local completed_at="$7"
  local duration_seconds="$8"
  local timeout_seconds="$9"
  local retry_count="${10}"
  local output_file="${11}"
  local error_message="${12:-}"
  local reasoning_effort="${13:-}"
  local review_label="${14:-}"

  {
    printf '  - reviewer: %s\n' "$(json_quote "$reviewer")"
    printf '    model: %s\n' "$(json_quote "$model")"
    printf '    model_id: %s\n' "$(json_quote "$model")"
    printf '    reasoning_effort: %s\n' "$(json_quote "$reasoning_effort")"
    printf '    review_label: %s\n' "$(json_quote "$review_label")"
    printf '    transport: %s\n' "$(json_quote "$transport")"
    printf '    session: %s\n' "$(json_quote "$session")"
    printf '    status: %s\n' "$(json_quote "$status")"
    printf '    started_at: %s\n' "$(json_quote "$started_at")"
    printf '    completed_at: %s\n' "$(json_quote "$completed_at")"
    printf '    duration_seconds: %s\n' "$duration_seconds"
    printf '    timeout_seconds: %s\n' "$timeout_seconds"
    printf '    retry_count: %s\n' "$retry_count"
    printf '    output_file: %s\n' "$(json_quote "$output_file")"
    printf '    error: %s\n' "$(json_quote "$error_message")"
  } >> "$REVIEW_METADATA_FILE"
}

build_review_prompt_file() {
  local reviewer_file="$1"
  local output_file="$2"
  sed \
    -e "s|{{EPIC_ID}}|${EPIC_ID}|g" \
    -e "s|{{EPIC_DIR}}|${EPIC_DIR}|g" \
    -e "s|{{ATTEMPT_DIR}}|${ATTEMPT_DIR}|g" \
    -e "s|{{CHANGED_FILES_PATH}}|${CHANGED_FILES_FILE}|g" \
    -e "s|{{AUDIT_MATRIX_PATH}}|${VERIFICATION_MATRIX_FILE}|g" \
    -e "s|{{REVIEWER_PACKET_PATH}}|${REVIEWER_PACKET_FILE:-not-applicable}|g" \
    -e "s|{{REPO_ROOT}}|$(pwd)|g" \
    "${REVIEWER_PROMPT_DIR}/${reviewer_file}" > "$output_file"
}

run_with_metadata_file() {
  local reviewer="$1"
  shift
  local reviewer_metadata="${ATTEMPT_DIR}/review-metadata-${reviewer}.yaml"
  (
    REVIEW_METADATA_FILE="$reviewer_metadata"
    printf 'reviews:\n' > "$REVIEW_METADATA_FILE"
    "$@"
  )
}

merge_reviewer_metadata() {
  {
    printf 'epic_id: %s\n' "$(json_quote "$EPIC_ID")"
    printf 'attempt_id: %s\n' "$(json_quote "$ATTEMPT_ID")"
    printf 'generated_at: %s\n' "$(json_quote "$(date -u +"%Y-%m-%dT%H:%M:%SZ")")"
    printf 'reviews:\n'
    for reviewer_metadata in "${ATTEMPT_DIR}"/review-metadata-*.yaml; do
      [ -f "$reviewer_metadata" ] || continue
      sed -n '/^reviews:/,$p' "$reviewer_metadata" | sed '1d'
    done
  } > "${ATTEMPT_DIR}/review-metadata.yaml"
}

run_codex_review() {
  local prompt_file="${ATTEMPT_DIR}/reviewer-codex-prompt.md"
  local output_file="${ATTEMPT_DIR}/codex-${CODEX_REVIEW_LABEL}.md"
  local started_epoch started_at completed_at duration_seconds

  if [[ "$CODEX_MODEL_ID" =~ -(low|medium|high)$ ]]; then
    echo "Codex model id appears to include a reasoning suffix: ${CODEX_MODEL_ID}" > "${ATTEMPT_DIR}/codex-unavailable.md"
    echo "Use CODEX_MODEL_ID=gpt-5.6-terra and CODEX_REASONING_EFFORT=high." >> "${ATTEMPT_DIR}/codex-unavailable.md"
    append_review_metadata "codex" "$CODEX_MODEL_ID" "exec" "" "failed" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" 0 "$REVIEW_TIMEOUT_SECONDS" 0 "${ATTEMPT_DIR}/codex-unavailable.md" "Codex model id includes reasoning suffix; use separate model id and reasoning effort" "$CODEX_REASONING_EFFORT" "$CODEX_REVIEW_LABEL"
    return 1
  fi

  if ! command -v codex >/dev/null 2>&1; then
    echo "Codex CLI not found. Skipped Codex external review." > "${ATTEMPT_DIR}/codex-unavailable.md"
    append_review_metadata "codex" "$CODEX_MODEL_ID" "exec" "" "unavailable" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" 0 "$REVIEW_TIMEOUT_SECONDS" 0 "${ATTEMPT_DIR}/codex-unavailable.md" "Codex CLI not found" "$CODEX_REASONING_EFFORT" "$CODEX_REVIEW_LABEL"
    return 0
  fi

  build_review_prompt_file "reviewer-codex.md" "$prompt_file"
  started_epoch="$(date +%s)"
  started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  if codex exec \
      --cd "$(pwd)" \
      --model "$CODEX_MODEL_ID" \
      -c model_reasoning_effort="\"$CODEX_REASONING_EFFORT\"" \
      --sandbox read-only \
      --output-last-message "$output_file" \
      - < "$prompt_file"; then
    completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    duration_seconds="$(( $(date +%s) - started_epoch ))"
    append_review_metadata "codex" "$CODEX_MODEL_ID" "exec" "" "completed" "$started_at" "$completed_at" "$duration_seconds" "$REVIEW_TIMEOUT_SECONDS" 0 "$output_file" "" "$CODEX_REASONING_EFFORT" "$CODEX_REVIEW_LABEL"
  else
    completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    duration_seconds="$(( $(date +%s) - started_epoch ))"
    append_review_metadata "codex" "$CODEX_MODEL_ID" "exec" "" "failed" "$started_at" "$completed_at" "$duration_seconds" "$REVIEW_TIMEOUT_SECONDS" 0 "$output_file" "Codex reviewer command failed" "$CODEX_REASONING_EFFORT" "$CODEX_REVIEW_LABEL"
    return 1
  fi
}

run_claude_review() {
  local prompt_file="${ATTEMPT_DIR}/reviewer-claude-prompt.md"
  local output_file="${ATTEMPT_DIR}/claude-opus.md"

  if [ -z "$REVIEWER_CLAUDE_PEXPECT_SCRIPT" ]; then
    echo "scope-reviewer-claude-pexpect.py not found. Skipped Claude external review." > "${ATTEMPT_DIR}/claude-unavailable.md"
    append_review_metadata "claude" "Claude Opus (local alias)" "pexpect" "" "unavailable" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" 0 "$REVIEW_TIMEOUT_SECONDS" 0 "${ATTEMPT_DIR}/claude-unavailable.md" "scope-reviewer-claude-pexpect.py not found"
    return 0
  fi

  if ! command -v claude >/dev/null 2>&1; then
    echo "Claude CLI not found. Skipped Claude external review." > "${ATTEMPT_DIR}/claude-unavailable.md"
    append_review_metadata "claude" "Claude Opus (local alias)" "pexpect" "" "unavailable" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" 0 "$REVIEW_TIMEOUT_SECONDS" 0 "${ATTEMPT_DIR}/claude-unavailable.md" "Claude CLI not found"
    return 0
  fi

  if ! command -v "$SCOPE_REVIEW_PYTHON" >/dev/null 2>&1; then
    echo "Python not found: ${SCOPE_REVIEW_PYTHON}. Skipped Claude external review." > "${ATTEMPT_DIR}/claude-unavailable.md"
    append_review_metadata "claude" "Claude Opus (local alias)" "pexpect" "" "unavailable" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" 0 "$REVIEW_TIMEOUT_SECONDS" 0 "${ATTEMPT_DIR}/claude-unavailable.md" "Python not found: ${SCOPE_REVIEW_PYTHON}"
    return 0
  fi

  if ! "$SCOPE_REVIEW_PYTHON" -c 'import pexpect' >/dev/null 2>&1; then
    echo "Python pexpect module not found. Skipped Claude external review." > "${ATTEMPT_DIR}/claude-unavailable.md"
    append_review_metadata "claude" "Claude Opus (local alias)" "pexpect" "" "unavailable" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" 0 "$REVIEW_TIMEOUT_SECONDS" 0 "${ATTEMPT_DIR}/claude-unavailable.md" "Python pexpect module not found"
    return 0
  fi

  build_review_prompt_file "reviewer-claude.md" "$prompt_file"
  local claude_command="${SCOPE_CLAUDE_PEXPECT_COMMAND:-claude --model opus --dangerously-skip-permissions --allowedTools '${CLAUDE_AUDIT_ALLOWED_TOOLS}' --no-chrome}"
  "$SCOPE_REVIEW_PYTHON" "$REVIEWER_CLAUDE_PEXPECT_SCRIPT" \
    --reviewer "claude" \
    --model "Claude Opus (local alias)" \
    --claude-command "$claude_command" \
    --prompt-file "$prompt_file" \
    --output-file "$output_file" \
    --metadata-file "$REVIEW_METADATA_FILE" \
    --cwd "$(pwd)" \
    --timeout-seconds "$REVIEW_TIMEOUT_SECONDS" \
    --retries "$REVIEW_RETRIES" || {
      return 1
    }
}

is_agy_rate_limit_error() {
  local error_file="$1"
  grep -Eiq 'rate.?limit|quota|429|resource.?exhausted|too many requests|try again later' "$error_file"
}

agy_model_available() {
  local model="$1"
  agy models 2>/dev/null | grep -Fxq "$model"
}

validate_agy_model_or_fail() {
  local model="$1"
  local output_file="$2"
  local model_role="$3"

  if agy_model_available "$model"; then
    return 0
  fi

  {
    printf 'Antigravity %s model is not an exact agy model label: %s\n' "$model_role" "$model"
    printf '\nUse one of the exact labels from `agy models`, for example:\n'
    printf '%s\n' '- Gemini 3.1 Pro (High)'
    printf '%s\n' '- Gemini 3.5 Flash (High)'
    printf '\nDo not use Gemini CLI aliases such as `gemini-3.1-pro-high`; agy may silently fall back to Flash Medium.\n'
  } > "$output_file"
  return 1
}

run_agy_model_review() {
  local model="$1"
  local output_id="$2"
  local prompt_file="$3"
  local output_file="${ATTEMPT_DIR}/${output_id}.md"
  local error_file="${AUDIT_TMP_DIR}/${output_id}.stderr.txt"
  local prompt_text

  prompt_text="$(cat "$prompt_file")"

  agy \
    --model "$model" \
    --sandbox \
    --dangerously-skip-permissions \
    --print-timeout "$AGY_PRINT_TIMEOUT" \
    --print "$prompt_text" \
    > "$output_file" \
    2> "$error_file"
}

run_agy_review() {
  local prompt_file="${ATTEMPT_DIR}/reviewer-agy-prompt.md"
  local output_file="${ATTEMPT_DIR}/${AGY_REVIEW_OUTPUT_ID}.md"
  local fallback_output_file="${ATTEMPT_DIR}/${AGY_FALLBACK_OUTPUT_ID}.md"
  local error_file="${AUDIT_TMP_DIR}/${AGY_REVIEW_OUTPUT_ID}.stderr.txt"
  local started_epoch started_at completed_at duration_seconds
  local final_model final_output_file final_transport

  if ! command -v agy >/dev/null 2>&1; then
    echo "Antigravity agy CLI not found. Skipped Antigravity external review." > "${ATTEMPT_DIR}/agy-unavailable.md"
    append_review_metadata "agy" "$AGY_REVIEW_MODEL" "agy-print" "" "unavailable" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" 0 "$REVIEW_TIMEOUT_SECONDS" 0 "${ATTEMPT_DIR}/agy-unavailable.md" "agy CLI not found"
    return 0
  fi

  if ! validate_agy_model_or_fail "$AGY_REVIEW_MODEL" "${ATTEMPT_DIR}/agy-unavailable.md" "primary"; then
    append_review_metadata "agy" "$AGY_REVIEW_MODEL" "agy-print" "" "failed" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" 0 "$REVIEW_TIMEOUT_SECONDS" 0 "${ATTEMPT_DIR}/agy-unavailable.md" "Antigravity primary model is not an exact agy model label"
    return 1
  fi

  if ! validate_agy_model_or_fail "$AGY_FALLBACK_MODEL" "${ATTEMPT_DIR}/agy-unavailable.md" "fallback"; then
    append_review_metadata "agy" "$AGY_FALLBACK_MODEL" "agy-print-fallback" "" "failed" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" 0 "$REVIEW_TIMEOUT_SECONDS" 0 "${ATTEMPT_DIR}/agy-unavailable.md" "Antigravity fallback model is not an exact agy model label"
    return 1
  fi

  build_review_prompt_file "reviewer-agy.md" "$prompt_file"
  started_epoch="$(date +%s)"
  started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  if run_agy_model_review "$AGY_REVIEW_MODEL" "$AGY_REVIEW_OUTPUT_ID" "$prompt_file"; then
    final_model="$AGY_REVIEW_MODEL"
    final_output_file="$output_file"
    final_transport="agy-print"
  elif is_agy_rate_limit_error "$error_file"; then
    echo "Primary Antigravity model rate-limited; retrying with ${AGY_FALLBACK_MODEL}." > "${ATTEMPT_DIR}/agy-fallback-used.txt"
    if run_agy_model_review "$AGY_FALLBACK_MODEL" "$AGY_FALLBACK_OUTPUT_ID" "$prompt_file"; then
      final_model="$AGY_FALLBACK_MODEL"
      final_output_file="$fallback_output_file"
      final_transport="agy-print-fallback"
    else
      completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
      duration_seconds="$(( $(date +%s) - started_epoch ))"
      append_review_metadata "agy" "$AGY_FALLBACK_MODEL" "agy-print-fallback" "" "failed" "$started_at" "$completed_at" "$duration_seconds" "$REVIEW_TIMEOUT_SECONDS" 0 "${AUDIT_TMP_DIR}/${AGY_FALLBACK_OUTPUT_ID}.stderr.txt" "Antigravity fallback reviewer command failed"
      rm -f "$fallback_output_file"
      return 1
    fi
  else
    completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    duration_seconds="$(( $(date +%s) - started_epoch ))"
    append_review_metadata "agy" "$AGY_REVIEW_MODEL" "agy-print" "" "failed" "$started_at" "$completed_at" "$duration_seconds" "$REVIEW_TIMEOUT_SECONDS" 0 "$error_file" "Antigravity reviewer command failed"
    rm -f "$output_file"
    return 1
  fi

  if [ ! -s "$final_output_file" ]; then
    completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    duration_seconds="$(( $(date +%s) - started_epoch ))"
    append_review_metadata "agy" "$final_model" "$final_transport" "" "failed" "$started_at" "$completed_at" "$duration_seconds" "$REVIEW_TIMEOUT_SECONDS" 0 "$final_output_file" "Antigravity reviewer produced empty output"
    rm -f "$final_output_file"
    return 1
  fi

  completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  duration_seconds="$(( $(date +%s) - started_epoch ))"
  append_review_metadata "agy" "$final_model" "$final_transport" "" "completed" "$started_at" "$completed_at" "$duration_seconds" "$REVIEW_TIMEOUT_SECONDS" 0 "$final_output_file" ""
}

run_glm_review() {
  local prompt_file="${ATTEMPT_DIR}/reviewer-glm-prompt.md"
  local output_file="${ATTEMPT_DIR}/${GLM_REVIEW_OUTPUT_ID}.md"
  local error_file="${AUDIT_TMP_DIR}/${GLM_REVIEW_OUTPUT_ID}.stderr.txt"
  local prompt_text started_epoch started_at completed_at duration_seconds

  if ! command -v opencode >/dev/null 2>&1; then
    return 0
  fi

  build_review_prompt_file "reviewer-glm.md" "$prompt_file" || return 0
  prompt_text="$(cat "$prompt_file")"
  started_epoch="$(date +%s)"
  started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  if opencode run \
      -m "$GLM_REVIEW_MODEL" \
      --variant "high" \
      --dir "$(pwd)" \
      --dangerously-skip-permissions \
      "$prompt_text" \
      > "$output_file" \
      2> "$error_file"; then
    if [ -s "$output_file" ]; then
      completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
      duration_seconds="$(( $(date +%s) - started_epoch ))"
      append_review_metadata "glm" "$GLM_REVIEW_MODEL" "opencode-run" "" "completed" "$started_at" "$completed_at" "$duration_seconds" "$REVIEW_TIMEOUT_SECONDS" 0 "$output_file" ""
      return 0
    fi
  fi

  rm -f "$output_file"
  return 0
}

if [ "$SCOPE_AUDIT_PARALLEL_REVIEWERS" = "1" ]; then
  pids=()
  (
    run_with_metadata_file "codex" run_codex_review ||
      echo "Codex reviewer failed or model unavailable. Continuing audit with remaining evidence." > "${ATTEMPT_DIR}/codex-unavailable.md"
  ) &
  pids+=("$!")
  (
    run_with_metadata_file "claude" run_claude_review ||
      echo "Claude reviewer failed or model unavailable. Continuing audit with remaining evidence." > "${ATTEMPT_DIR}/claude-unavailable.md"
  ) &
  pids+=("$!")
  (
    run_with_metadata_file "agy" run_agy_review ||
      echo "Antigravity reviewer failed or model unavailable. Continuing audit with remaining evidence." > "${ATTEMPT_DIR}/agy-unavailable.md"
  ) &
  pids+=("$!")
  (
    run_with_metadata_file "glm" run_glm_review || true
  ) &
  pids+=("$!")

  for pid in "${pids[@]}"; do
    wait "$pid" || true
  done
  merge_reviewer_metadata
else
  run_codex_review || echo "Codex reviewer failed or model unavailable. Continuing audit with remaining evidence." > "${ATTEMPT_DIR}/codex-unavailable.md"
  run_claude_review || echo "Claude reviewer failed or model unavailable. Continuing audit with remaining evidence." > "${ATTEMPT_DIR}/claude-unavailable.md"
  run_agy_review || echo "Antigravity reviewer failed or model unavailable. Continuing audit with remaining evidence." > "${ATTEMPT_DIR}/agy-unavailable.md"
  run_glm_review || true
fi
```

Claude CLI model aliases vary by installation. By default Scope calls
`claude --model opus`, which uses the local current Opus alias and is not pinned
to a specific Claude release. To pin a specific Claude model id, set
`SCOPE_CLAUDE_PEXPECT_COMMAND`. The Claude wrapper requires Python with the
`pexpect` module available; set `SCOPE_REVIEW_PYTHON` to a Python executable
that can import `pexpect` if needed.

### Reviewer Output Contract

Each reviewer must return markdown using this structure:

```markdown
# External Audit Review: {reviewer} / {model}

## Summary
{brief assessment}

## Files Inspected
- {path}

## Unread Required Files
- {path}: {error}

## Required Checks Performed
| Matrix Row ID | Requirement | Implementation Evidence | Test Evidence | Runtime Evidence | Result |
|---------------|-------------|-------------------------|---------------|------------------|--------|
| {row id} | {requirement} | {file:line or missing} | {test assertion or missing} | {command/evidence/n/a} | {pass/fail/blocked/unverified/not_applicable with evidence} |

## Findings

### CRITICAL
- **Title**:
  **Evidence**:
  **Impact**:
  **Fix**:

### MAJOR
- **Title**:
  **Evidence**:
  **Impact**:
  **Fix**:

### MINOR
- **Title**:
  **Evidence**:
  **Impact**:
  **Fix**:
  **Easy fix**: yes/no

## Questions For Human
- {only product, architecture, security, destructive migration, credential, or scope decisions}
```

## Step 7: Same-Agent Exploratory Residual Review

After the traceability/matrix-driven review is complete, the orchestrating agent running this command performs a bounded exploratory residual review:

- If `/audit_epic` is running in Codex, Codex performs this residual review locally.
- If `/audit_epic` is running in Claude, Claude performs this residual review locally.
- Do not launch another external model for this step.
- Do not repeat the full matrix audit.
- Spend the review budget on undocumented high-impact risks that a traceability matrix is likely to miss.

Write the result to `docs/epics/{epic-dir}/reviews/{audit-NNN}/exploratory-residual-review.md`.

Residual review focus:

- undocumented negative-space behavior: things the implementation must not do but the ACs did not say explicitly
- emergent interactions between changed modules and adjacent unchanged modules
- operational/concurrency/lock/timeout/retry risks not covered by the matrix
- security, privacy, auth, secret handling, and unsafe logging risks
- data-loss, duplicate-write, stale-state, or rollback risks outside named AC rows
- bad or incomplete requirements that the matrix would verify too narrowly

Residual review output:

```markdown
# Exploratory Residual Review

## Scope
{brief statement of what was intentionally inspected outside the matrix}

## Findings

### CRITICAL
...

### MAJOR
...

### MINOR
...

## No-Finding Rationale
{if clean, explain which high-risk areas were sampled and why no issue was found}
```

Residual findings must still be evidence-backed. Do not use the residual review to relabel matrix `unverified` rows as bugs without proof.

## Step 8: Merge Reviewer Findings

After reviewer execution finishes:

1. Read every completed review in the current attempt directory. Expected filenames are `reviews/audit-NNN/codex-gpt-5.6-terra-high.md`, `reviews/audit-NNN/claude-opus.md`, `reviews/audit-NNN/agy-gemini-3.1-pro-high.md` or fallback `reviews/audit-NNN/agy-gemini-3.5-flash.md`, and optional `reviews/audit-NNN/glm-5.2.md` when opencode is available. Any required reviewer may be absent when the local tool is unavailable; GLM may be absent silently. For legacy attempts, also read any additional `reviews/audit-NNN/claude-opus*.md` review file if present.
2. Read `reviews/audit-NNN/review-metadata.yaml` and use it to report reviewer duration, timeout, retry count, transport, and status.
3. Read `reviews/audit-NNN/exploratory-residual-review.md` if it exists.
4. Merge reviewer row statuses into `audit-verification-matrix.yaml` under `reviewer_status`.
5. Assign `final_status` for every matrix row using source/test/runtime evidence and reviewer consensus.
6. Convert failed or unverified matrix rows into findings using the deterministic severity table.
7. Deduplicate findings by matrix row id, root cause, affected file, and required fix.
8. Preserve the highest severity assigned by any reviewer only when it matches the deterministic severity table or the reviewer provides concrete evidence that raises impact.
9. Add reviewer attribution to each merged finding.
10. Include a dedicated "External Reviewer Findings" section in `epic_audit.md`.
11. Include a dedicated "Exploratory Residual Review" section in `epic_audit.md`.
12. If any `*-unavailable.md` file exists in the current attempt, disclose it in `epic_audit.md` under reviewer coverage. Do not fail the audit solely for unavailable reviewers.
13. Update `audit-issue-ledger.yaml` with every major and critical finding.

---

## Audit Phase 1: Architecture Compliance

### 1.1 Component Verification

**Check:** Do implemented components match architecture design?

```python
# From architecture.md
designed_components = extract_components(architecture)
# Example: FileMapper, HierarchyBuilder, ConfigLoader

# From implementation
implemented_components = scan_src_structure()
# Example: file_mapper/, hierarchy/, config_manager/

# Compare
missing = designed_components - implemented_components
extra = implemented_components - designed_components
renamed = detect_renames(designed_components, implemented_components)
```

**Report:**
```markdown
### Component Compliance

✅ MATCHES (N components):
- FileMapper → src/file_mapper/ ✓
- HierarchyBuilder → src/hierarchy/ ✓

⚠️  DEVIATIONS (N issues):
- ConfigLoader → src/config_manager/ (renamed without ADR)
- Missing: FrontmatterHandler (designed but not implemented)
- Extra: src/utils/retry.py (implemented but not in design)
```

### 1.2 API Contract Verification

**Check:** Do APIs match architecture design?

```python
# From architecture.md API section
designed_apis = extract_api_endpoints(architecture)

# From implementation
implemented_apis = scan_api_routes(src_dir)

# From 13-specs
spec_apis = parse_openapi(f"docs/architecture/13-specs/api/")

# Three-way comparison
api_audit = compare_apis(designed_apis, spec_apis, implemented_apis)
```

**Report:**
```markdown
### API Contract Compliance

✅ MATCHES:
- GET /api/sync-status (design → spec → implementation) ✓

⚠️  DEVIATIONS:
- POST /api/force-sync: Missing required field "direction" (spec has it, code doesn't)
- GET /api/config: Returns 200 instead of designed 201 for new configs
```

### 1.3 Data Model Verification

**Check:** Do data models match schemas?

```python
# From architecture.md
designed_models = extract_data_models(architecture)

# From implementation
implemented_models = scan_dataclasses_and_models(src_dir)

# From docs/architecture/13-specs/schemas
spec_schemas = parse_json_schemas(f"docs/architecture/13-specs/schemas/domain/")

# Compare
model_audit = compare_models(designed_models, spec_schemas, implemented_models)
```

**Report:**
```markdown
### Data Model Compliance

✅ MATCHES:
- PageNode: All fields match schema ✓

⚠️  DEVIATIONS:
- SyncConfig: Added field "retry_count" (not in schema or design)
- LocalPage: Missing field "last_modified" (in schema, not in code)
```

---

## Audit Phase 2: ADR Compliance

### 2.1 Technology Decisions

**Check:** Were ADR technology selections followed?

```python
adrs_list = parse_adrs(adrs)

for adr in adrs_list:
    decision = adr['decision']
    # Check if decision was implemented correctly
    compliance = verify_adr_implementation(adr, src_dir)
```

**Report:**
```markdown
### ADR Compliance

✅ ADR-008: CQL-based page discovery
   Implementation: Using CQL queries ✓
   Limit: 100 pages enforced ✓

❌ ADR-010: Filesafe conversion with case preservation
   VIOLATION: Implementation converts to lowercase only
   Location: src/file_mapper/filesafe_converter.py:15
   Impact: CRITICAL - Data loss for case-sensitive titles

⚠️  ADR-011: Atomic file operations (two-phase commit)
   PARTIAL: Two-phase commit implemented, but no rollback on failure
   Location: src/file_mapper/file_mapper.py:45-60
   Impact: MAJOR - Could leave partial state on error
```

### 2.2 Pattern Compliance

**Check:** Were architectural patterns applied correctly?

```python
# From ADRs and cross-cutting docs
required_patterns = extract_patterns(adrs)
# Example: Exception hierarchy, dataclass pattern, module organization

# From implementation
implemented_patterns = analyze_code_patterns(src_dir)

# Compare
pattern_audit = verify_patterns(required_patterns, implemented_patterns)
```

**Report:**
```markdown
### Pattern Compliance

✅ Exception Hierarchy Pattern:
   All exceptions inherit from ConfluenceError ✓
   Typed exception parameters ✓

⚠️  Dataclass Pattern:
   DEVIATION: SyncConfig uses dict instead of @dataclass
   Location: src/file_mapper/models.py:25
   Impact: MINOR - Inconsistent with project pattern
```

---

## Audit Phase 3: Acceptance Criteria

### 3.1 Scenario Coverage

**Check:** Are all acceptance criteria scenarios implemented and tested?

```python
acceptance_scenarios = parse_acceptance_criteria(acceptance_criteria)

for scenario in acceptance_scenarios:
    # Check implementation
    implemented = find_implementation(scenario, src_dir)
    # Check tests
    tested = find_tests(scenario, tests_dir)

    scenario_audit.append({
        'scenario': scenario,
        'implemented': implemented,
        'tested': tested
    })
```

**Report:**
```markdown
### Acceptance Criteria Coverage

✅ AC-1: Filesafe Filename Conversion
   Implemented: ✓
   Tested: ✓
   Coverage: 95%

❌ AC-6: Initial Sync Direction
   Implemented: ✗ (forcePull/forcePush flags missing)
   Tested: ✗
   Impact: CRITICAL - Core requirement not implemented

⚠️  AC-8: Exclusion Patterns
   Implemented: ✓
   Tested: Partial (only unit tests, no E2E)
   Impact: MINOR - Missing E2E test coverage
```

### 3.2 Story Coverage Threshold

**Check:** Does each story reach the required 90%+ automated coverage for the code it created or modified?

Use the epic test strategy, coverage reports, and changed-file ownership to verify per-story coverage. If a story is below 90%, it fails the quality gate unless the test strategy explicitly documents an approved exception and compensating controls.

**Report:**
```markdown
### Story Coverage Threshold

✅ Story 01: 93% automated coverage on story-owned code

❌ Story 03: 82% automated coverage on story-owned code
   Expected: 90%+
   Exception: None documented
   Impact: MAJOR - Story does not meet minimum coverage floor

⚠️  Story 04: 87% automated coverage on story-owned code
   Exception: Approved in test strategy due to uninstrumentable vendor callback path
   Compensating controls: Integration test + live smoke test
   Impact: MINOR - Below threshold but exception documented
```

### 3.3 Edge Case Handling

**Report:**
```markdown
### Edge Case Coverage

✅ Malformed frontmatter: Error handling implemented ✓
✅ Network failure: APIUnreachableError raised ✓
❌ 100 page limit: No error message, silent truncation
   Impact: MAJOR - Users won't know why pages missing
```

---

## Audit Phase 4: Auto Claude Spec Alignment

### 4.1 Spec vs Architecture

**Check:** Does Auto Claude's spec align with our architecture?

```python
ac_spec_components = extract_components_from_spec(ac_spec)
our_components = extract_components(architecture)

spec_alignment = compare_components(ac_spec_components, our_components)
```

**Report:**
```markdown
### Auto Claude Spec Alignment

✅ Auto Claude spec references our architecture ✓
✅ ADR references match (ADR-008 through ADR-015) ✓

⚠️  SPEC DEVIATION:
   Auto Claude spec added: DirectoryScanner
   Not in our architecture.md
   Reason: Auto Claude optimization for performance
   Impact: MINOR - Enhancement not breaking change
```

### 4.2 Spec vs Implementation

**Check:** Did implementation follow Auto Claude's spec?

```python
spec_requirements = extract_requirements(ac_spec)
implementation_features = scan_implementation_features(src_dir)

spec_compliance = verify_spec_implementation(spec_requirements, implementation_features)
```

**Report:**
```markdown
### Spec Implementation Compliance

✅ All "Files to Modify" created ✓
✅ All "Patterns to Follow" applied ✓

❌ SUCCESS CRITERIA NOT MET:
   Spec requires: Unit test coverage >90%
   Actual: 75% coverage
   Impact: MAJOR - Quality gate not met
```

---

## Audit Phase 5: Code Quality

### 5.1 Pattern Consistency

**Report:**
```markdown
### Code Quality

✅ Follows project structure ✓
✅ Error handling consistent ✓

⚠️  DEVIATIONS:
- Missing docstrings: 15 functions
- Hardcoded config values: 3 instances (should be in YAML)
  Impact: MINOR - Maintainability issue
```

---

## Audit Phase 6: Stub/Placeholder Detection

**Check:** Does every implementation file satisfy the binding boundary-plan obligations and evidence claims that justify it?

```python
for story_plan in boundary_plans:
    for obligation in story_plan["required_contracts"] + story_plan["required_touchpoints"] + story_plan["proof_obligations"]:
        path = obligation.get("path") or find_path_from_implementation_evidence(obligation["id"])
        if not path:
            continue
        intent = obligation.get("obligation") or obligation.get("required_evidence") or obligation.get("success_condition")
        code = Read(path)

        # 1. Search for stub markers in production code
        stub_markers = ["# Placeholder", "# TODO", "# Stub", "# Mock",
                        "NotImplementedError", "pass  #", "hardcoded"]
        for marker in stub_markers:
            if marker.lower() in code.lower():
                report_finding(severity="CRITICAL", file=path, marker=marker)

        # 2. Check intent vs implementation for I/O verbs
        io_verbs = ["sends", "calls", "queries", "uploads", "downloads",
                    "writes to", "reads from", "posts", "fetches", "connects"]
        intent_has_io = any(verb in intent.lower() for verb in io_verbs)

        if intent_has_io:
            # Verify code contains actual I/O (HTTP client, DB driver, file ops)
            has_real_io = contains_io_operations(code)  # requests, httpx, aiohttp, fetch, db.execute, etc.
            if not has_real_io:
                report_finding(
                    severity="CRITICAL",
                    file=path,
                    issue=f"Intent says '{extract_io_verb(intent)}' but implementation contains no I/O code",
                    expected="Production code with real API/DB/network calls",
                    actual="Function returns hardcoded/literal values or delegates to mocks"
                )

        # 3. Check for functions that return literals without performing their stated purpose
        for func in extract_functions(code):
            if func.returns_literal and func.name_implies_action:
                report_finding(
                    severity="MAJOR",
                    file=path,
                    issue=f"Function {func.name}() returns literal value without performing action",
                    impact="Tests pass via mocks but production code does nothing"
                )
```

**Report:**
```markdown
### Stub/Placeholder Detection

❌ CRITICAL: src/classification/llm_classifier.py
   Intent: "Sends first excerpt_chars of markdown to configured LLM model"
   Issue: No HTTP/API client call found in _call_llm()
   Actual: Returns hardcoded ClassificationResult
   Impact: CRITICAL - Core functionality is a stub

❌ CRITICAL: src/ingestion/feed_fetcher.py
   Issue: Contains "# TODO: implement retry logic"
   Impact: CRITICAL - Incomplete implementation

✅ src/models/document.py - No stubs detected
✅ src/utils/parser.py - No stubs detected
```

**Key rule:** A stub found in production code is ALWAYS severity CRITICAL, never minor. If a binding boundary-plan obligation says the code should do something and it doesn't, that's a failed implementation.

---

## Audit Phase 7: Lint & Contract Compliance

**Check:** Ingest epic-wide lint and contract findings and include them in the audit report.

```python
lint_findings_path = f"docs/epics/{epic_dir}/lint_findings.yaml"
if file_exists(lint_findings_path):
    lint_report = read_yaml(lint_findings_path)

    # Ruff violations that couldn't be auto-fixed
    for violation in lint_report.get("ruff_violations", []):
        report_finding(
            severity="MAJOR",
            file=violation["file"],
            issue=f"ruff: {violation['code']} - {violation['message']} (line {violation['line']})",
            impact="Code quality violation that couldn't be auto-fixed"
        )

    # Vulture dead code findings
    for finding in lint_report.get("vulture_dead_code", []):
        report_finding(
            severity="MAJOR",
            file=finding["file"],
            issue=f"vulture: unused {finding['type']} '{finding['name']}' (line {finding['line']})",
            impact="Dead code increases maintenance burden and may indicate incomplete refactoring"
        )

    # mypy contract violations
    for error in lint_report.get("mypy_errors", []):
        report_finding(
            severity="CRITICAL",
            file=error["file"],
            issue=f"mypy: {error['message']} (line {error['line']})",
            impact="Contract violation — implementation does not match Protocol interface. Cross-story calls will fail at runtime."
        )
```

**Report:**
```markdown
### Lint & Contract Compliance

❌ CRITICAL: src/documentation/intel_aggregator.py:23
   mypy: Argument 1 to "aggregate_for_section" has incompatible type "int"; expected "str"
   Impact: Contract violation — cross-story calls will fail at runtime

❌ MAJOR: src/classification/classifier.py:45
   ruff: F841 - Local variable 'result' is assigned but never used
   Impact: Code quality violation

❌ MAJOR: src/ingestion/feed_parser.py:12
   vulture: unused function 'parse_legacy_format' (line 12)
   Impact: Dead code from incomplete refactoring

✅ No lint/contract findings (lint_findings.yaml not present or empty)
```

**Note:** If `lint_findings.yaml` does not exist, the epic-wide checks passed cleanly — skip this phase. mypy errors are CRITICAL because they indicate implementations that don't match the Protocol contracts — these will cause runtime failures when stories integrate.

---

## Audit Phase 8: Documentation Sync (Reverse Audit)

**Purpose:** Phases 1-7 check "does code match docs?" (code ← docs). Phase 8 checks the reverse: **"do docs match code?"** (docs ← code). This catches stale documentation — docs that were accurate before implementation but are now outdated because implementation changed things.

**CRITICAL GOVERNANCE RULE:** Phase 8 produces **recommendations only**. It does NOT auto-fix documentation and does NOT create fix stories for doc updates. The user must review each recommendation and approve before any documentation is changed.

**Why human-in-the-loop:** If implementation diverged from the design, auto-updating docs to match the code would launder the divergence — the docs would now say "we planned this" when actually the implementation drifted. Only the user can decide whether:
- The code is correct and docs should be updated to reflect reality
- The code drifted and should be fixed to match the original design
- The divergence is intentional and should be recorded as a new ADR

### 8.1 What to Check

For each category, compare what the code actually does against what the docs say:

Read both new-format and legacy docs when present. Legacy docs are context, not
the target format. If implementation matches only legacy docs, report a
documentation-sync finding to migrate or summarize the legacy content into the
new component `01-intro.md` through `13-specs/` tree.

| Category | Document | Compare Against |
|----------|----------|----------------|
| Database schema | `backend/13-specs/database/`, `backend/13-specs/schemas/` | Migration files, CREATE TABLE, schema.sql, Pydantic DB models |
| Services | `backend/05-building-blocks.md`, `backend/06-runtime.md` | FastAPI apps, CLI entry points, new routers, workers |
| Building blocks | `05-building-blocks.md` | New components from boundary plans and implementation evidence vs. what's documented |
| External dependencies | `03-context.md` | New cloud SDKs, API clients, DB drivers, Docker services |
| Domain entities | `08-cross-cutting/domain.md` | New Pydantic models, dataclasses, named domain concepts |
| Terminology | `12-glossary.md`, `terminology-data-model.md` | New terms in code not in glossary |
| ADR roll-up | `09-adr-summary.md` | Epic ADRs not yet in system summary |
| PDR roll-up | `product/decisions.md` | Epic PDRs not yet in product decisions |

### 8.2 Classify Each Finding

For each divergence found, classify:

```python
for finding in doc_sync_findings:
    finding.category = classify_divergence(finding)
    # Categories:
    # "planned_not_documented" — architect designed it, Story 0 should have updated docs but didn't
    # "implementation_drift"  — code diverged from design, unclear if intentional
    # "missing_doc"           — doc file doesn't exist at all (e.g., backend/13-specs/database/ never created)
    # "rollup_pending"        — epic ADRs/PDRs not yet rolled up to system level
```

### 8.3 Present Recommendations to User

**Do NOT auto-fix. Present each finding as a recommendation for user approval.**

```markdown
### Documentation Sync — Recommendations for User Approval

Phase 8 found {N} documentation gaps. Each requires your decision.

┌────┬──────────┬──────────────────────────────────────────────────────────┐
│ #  │ Severity │ Finding                                                  │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 1  │ MAJOR    │ backend/13-specs/database/ does not exist                 │
│    │          │ Code has 5 new tables (organizations, persons, etc.)     │
│    │          │ Was this planned? Should docs be created to match code?  │
│    │          │ Action: [create docs / code should be fixed / defer]     │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 2  │ MAJOR    │ 05-building-blocks.md missing PostgresClient             │
│    │          │ Component exists in code but not in architecture diagram │
│    │          │ Was this an intentional addition?                        │
│    │          │ Action: [update docs / code should be fixed / defer]     │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 3  │ MEDIUM   │ 03-context.md still shows SQLite only                    │
│    │          │ Code now uses PostgreSQL as primary database              │
│    │          │ This appears intentional (per epic architecture.md)      │
│    │          │ Action: [update docs / defer]                            │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 4  │ MEDIUM   │ 09-adr-summary.md missing 4 epic ADRs                   │
│    │          │ Epic adr.md has ADRs not yet in system summary           │
│    │          │ Action: [roll up now / defer to /wrap_epic]              │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 5  │ MINOR    │ 12-glossary.md missing 11 new terms                     │
│    │          │ New terms: RLS, sagara, heartbeat, ...                   │
│    │          │ Action: [update glossary / defer]                        │
└────┴──────────┴──────────────────────────────────────────────────────────┘

For each finding, choose:
  [update docs]      — Docs should reflect the code (implementation is correct)
  [code should fix]  — Code diverged and should be fixed to match design
  [new ADR needed]   — Divergence is intentional, record as a new decision
  [defer]            — Handle later (in /wrap_epic or next epic)
```

### 8.4 Record User Decisions

For each finding the user approves:
- **"update docs"** → Record in audit report as approved doc update. The user (or `/wrap_epic`) will execute it. Do NOT have the developer agent update docs — that bypasses the architect's design authority.
- **"code should fix"** → Create a fix story (same as Phases 1-7 findings). This IS a code problem, not a doc problem.
- **"new ADR needed"** → Flag for `/decision` or `/wrap_epic` to record formally.
- **"defer"** → Record as deferred in audit report. Will be caught again by next audit or `/wrap_epic`.

**Key rule:** Documentation sync findings are MAJOR severity (not CRITICAL) because they don't break functionality, but they degrade the project's ability to make informed decisions in future epics. Stale docs are a compounding problem — each unfixed gap makes the next epic's architecture design less accurate.

---

## Issue Classification

All findings are classified by severity:

| Severity | Definition | Examples |
|----------|------------|----------|
| **CRITICAL** | Failed required/runtime matrix row that breaks core behavior, risks data loss/security, violates a hard contract, or leaves required runtime evidence as the only proof and absent | Core acceptance behavior broken, destructive side effect, security exposure, production stub/fake, runtime-required smoke absent when no other proof exists |
| **MAJOR** | Failed or unverified required/high-risk matrix row, significant design drift, or stale documentation | Partial ADR implementation, missing important edge case, required row lacks test evidence, any story below 90% coverage without an approved exception, backend/13-specs database/schema docs missing or stale |
| **MEDIUM** | Documentation or tracking gaps | ADRs/PDRs not rolled up, context diagram outdated, missing external dependencies in docs |
| **MINOR** | Optional/documentation row unverified, cosmetic issue, or low-risk consistency issue | Naming inconsistencies, missing glossary terms, small pattern deviations |
| **ENHANCEMENT** | Improvements not in original design | Performance optimizations, additional features |

### Automatic Fix Classification

Classify every finding into one remediation action:

| Action | Applies To | User Approval |
|--------|------------|---------------|
| **AUTO-FIX** | All critical findings, all major findings, and easy low-risk minor findings | Not required |
| **ASK USER** | Product decisions, architecture decisions, security tradeoffs, destructive migrations, external credentials, or scope changes | Required |
| **DEFERRED DOC DECISION** | Documentation sync recommendations that may launder implementation drift | Required |
| **DO NOT FIX** | False positives with evidence | Not required, but explain in audit report |

Easy minor findings include local naming consistency, small docstring/comment cleanup, obvious formatting, missing low-risk test assertions, or mechanical cleanup in files already being edited. Do not ask the user before fixing those.

### Cumulative Issue Ledger

Maintain `docs/epics/{epic-dir}/audit-issue-ledger.yaml` across audit attempts. Every new `CRITICAL` or `MAJOR` finding must be classified:

| RCA Class | Meaning |
|-----------|---------|
| `introduced_by_fix` | The issue was created by a remediation change after a previous audit |
| `missed_previous_audit` | The issue existed earlier but the audit process did not catch it |
| `new_requirement` | The issue comes from a requirement clarified after earlier audits |
| `false_positive` | The issue is not valid, with evidence |

For `missed_previous_audit`, include why it was missed: unchecked acceptance row, unread file, no runtime evidence, stale boundary plan, missing scripted gate, reviewer overtrusted docs, or other concrete reason.

Required ledger shape:

```yaml
epic_id: {epic-id}
issues:
  - id: AUD-001
    first_seen_attempt: audit-003
    severity: CRITICAL
    title: "Issue title"
    rca_class: missed_previous_audit
    missed_reason: "Acceptance row AC4.2 had no code/test evidence in previous audit"
    affected_files: []
    reviewer_sources: []
    status: open
```

---

## Audit Report Output

Write to: `docs/epics/{epic-dir}/epic_audit.md`

### Report Template

```markdown
# Epic Audit Report: {epic-id}

**Date**: {date}
**Auditor**: Scope audit command
**Audit Attempt**: {audit-NNN}
**External Reviewers**: Codex `gpt-5.6-terra` with high reasoning, Claude Opus via local `opus` alias, Antigravity `Gemini 3.1 Pro (High)` or fallback `Gemini 3.5 Flash (High)`, optional GLM `zai-coding-plan/glm-5.2` when opencode is available
**Status**: {PASS / FAIL / PASS WITH CONDITIONS}

---

## Executive Summary

{2-3 sentence summary of audit outcome}

**Overall Compliance**: {percentage}%

**Critical Issues**: {N}
**Major Issues**: {N}
**Minor Issues**: {N}
**Enhancements**: {N}

**Recommendation**: {APPROVE / FIX CRITICAL / FIX ALL}

---

## Deterministic Audit Inputs

| Artifact | Path | Status |
|----------|------|--------|
| Acceptance traceability | `docs/epics/{epic-dir}/acceptance-traceability.yaml` | {valid/invalid} |
| Audit manifest | `docs/epics/{epic-dir}/audit-manifest.yaml` | {valid/invalid} |
| Audit verification matrix | `docs/epics/{epic-dir}/audit-verification-matrix.yaml` | {valid/invalid} |
| Issue ledger | `docs/epics/{epic-dir}/audit-issue-ledger.yaml` | {updated/not updated} |
| Attempt reviews | `docs/epics/{epic-dir}/reviews/{audit-NNN}/` | {complete/incomplete} |

### Acceptance Traceability Matrix Result

| Row | Requirement | Implementation Evidence | Test Evidence | Runtime Evidence | Status |
|-----|-------------|-------------------------|---------------|------------------|--------|
| AC1.1 | {requirement} | {file:line or missing} | {test assertion or missing} | {command/result or n/a} | {verified/blocked/fail} |

Rows without implementation evidence, test evidence, or required runtime evidence are findings. Do not mark acceptance criteria passed by relying on summaries.

### Verification Matrix Result

| Row ID | Priority | Risk | Final Status | Reviewer Status | Finding |
|--------|----------|------|--------------|-----------------|---------|
| AC2.2-P10-REPROCESS-SERVICE | required | high | {pass/fail/unverified/blocked/not_applicable} | Codex: {status}; Claude: {status}; Antigravity: {status}; GLM: {status if present} | {none/finding id} |

Rows marked `fail`, required rows marked `unverified`, and blocked rows must appear in the finding list or human-question list. Rows marked `pass` require cited implementation, test, or runtime evidence.

### Scripted Gate Results

| Gate | Status | Evidence |
|------|--------|----------|
| File-plan path validation | {pass/fail/blocked} | {path/output} |
| Acceptance traceability validation | {pass/fail/blocked} | {path/output} |
| Contract parity | {pass/fail/blocked} | {command/output} |
| Schema/OpenAPI enum parity | {pass/fail/blocked} | {command/output} |
| ruff/mypy/vulture | {pass/fail/blocked} | {command/output} |
| Real PG queue | {pass/fail/blocked/not applicable} | {command/output} |
| Live smoke status matrix | {pass/fail/blocked/not applicable} | {command/output} |

---

## Findings

### External Reviewer Findings

| Reviewer | Model | Transport | Session | Status | Duration | Retries | Findings Imported |
|----------|-------|-----------|---------|--------|----------|---------|-------------------|
| Codex | gpt-5.6-terra / high reasoning | exec | n/a | {completed/unavailable} | {from review-metadata.yaml} | {N} | {N} |
| Claude | Opus via local alias | pexpect | n/a | {completed/unavailable} | {from review-metadata.yaml} | {N} | {N} |
| Antigravity | {Gemini 3.1 Pro (High) / Gemini 3.5 Flash (High)} | agy-print | n/a | {completed/unavailable} | {from review-metadata.yaml} | {N} | {N} |
| GLM | zai-coding-plan/glm-5.2 | opencode-run | n/a | {completed/not run} | {from review-metadata.yaml if present} | {N} | {N} |

### Exploratory Residual Review

| Reviewer | Output | Critical | Major | Minor |
|----------|--------|----------|-------|-------|
| {Codex or Claude orchestrator} | `reviews/{audit-NNN}/exploratory-residual-review.md` | {N} | {N} | {N} |

### Critical Issues (Blocking)

#### 1. {Issue Title}
- **Category**: {Architecture / ADR / Acceptance Criteria}
- **Location**: {file:line}
- **Description**: {what's wrong}
- **Impact**: {why it matters}
- **Expected**: {what should be}
- **Actual**: {what was implemented}

### Major Issues (Should Fix)

{...}

### Minor Issues (Nice to Fix)

{...}

### Enhancements (Unexpected Improvements)

{...}

---

## Root Cause Analysis

**Why did divergence occur?**

1. {Root cause 1 - e.g., Auto Claude misinterpreted ADR}
2. {Root cause 2 - e.g., Architecture ambiguous on edge case}
3. {Root cause 3 - e.g., Implementation added feature not in design}

### New Major/Critical Findings Since Previous Audit

Every new major or critical finding must include:
- `introduced_by_fix`, `missed_previous_audit`, `new_requirement`, or `false_positive`
- reason it was not caught previously
- audit gate or reviewer prompt change that would have caught it

---

## Fix Plan

The responsible implementation agent must automatically fix all `AUTO-FIX` items. Do not ask the user before fixing critical issues, major issues, or easy low-risk minor issues.

### Priority 1: Critical Fixes (BLOCKING)

| # | Issue | Fix | Effort | Files |
|---|-------|-----|--------|-------|
| 1 | AC-6 not implemented | Add forcePull/forcePush flags | 4h | file_mapper.py, config_loader.py |
| 2 | ADR-010 violated | Fix case preservation in filesafe converter | 2h | filesafe_converter.py |

**Total Effort**: 6 hours

### Priority 2: Major Fixes (Should Address)

| # | Issue | Fix | Effort | Files |
|---|-------|-----|--------|-------|
| 3 | ADR-011 partial | Add rollback on failure | 3h | file_mapper.py |
| 4 | Test coverage gap | Add E2E tests for AC-8 | 4h | tests/e2e/ |

**Total Effort**: 7 hours

### Priority 3: Minor Fixes (Optional)

| # | Issue | Fix | Effort | Files |
|---|-------|-----|--------|-------|
| 5 | Missing docstrings | Add docstrings to 15 functions | 2h | Various |
| 6 | Hardcoded config | Move to YAML files | 1h | config_loader.py |

**Total Effort**: 3 hours

---

## Compliance Scorecard

| Area | Score | Status |
|------|-------|--------|
| Architecture Compliance | 85% | ⚠️  Issues found |
| ADR Compliance | 70% | ❌ Critical violations |
| Acceptance Criteria | 75% | ❌ Missing scenarios |
| Auto Claude Spec | 95% | ✅ Mostly aligned |
| Code Quality | 90% | ✅ Good |
| **OVERALL** | **83%** | ⚠️  **PASS WITH CONDITIONS** |

---

## Recommendations

1. **IMMEDIATE**: Fix all Critical issues (Priority 1) before merging
2. **IMMEDIATE**: Fix all Major issues (Priority 2) before merging
3. **IMMEDIATE**: Fix easy low-risk Minor issues before merging
4. **ASK USER**: Escalate only product, architecture, security, destructive migration, credential, or scope decisions
5. **DOCUMENT**: Record deferred documentation decisions for `/wrap_epic`

---

## Next Steps

After reviewing this audit:

1. Implement all AUTO-FIX findings immediately.
2. Run focused tests that prove the remediated matrix rows and sibling-risk rows.
3. If fewer than 3 total audit attempts have run, run `/audit_epic {epic-id}` again after fixes to verify.
4. Ask the user only for findings marked ASK USER or DEFERRED DOC DECISION.
5. Mark epic as "audit-passed" only when the latest audit satisfies the Definition of Done.

---

## Appendix: Detailed Findings

{Full detailed findings with code snippets, comparisons, etc.}
```

---

## Completion Flow

After generating audit report:

```
Audit Complete: {epic-id}

Report saved to: docs/epics/{epic-dir}/epic_audit.md

Summary:
├── Status: {PASS / FAIL / PASS WITH CONDITIONS}
├── Overall Compliance: {percentage}%
├── Critical Issues: {N}
├── Major Issues: {N}
└── Minor Issues: {N}

{If CRITICAL issues exist:}
⚠️  CRITICAL ISSUES FOUND - Blocking issues must be fixed

Fix Plan Summary:
├── Priority 1 (Critical): {N} issues, {X} hours estimated
├── Priority 2 (Major): {N} issues, {X} hours estimated
└── Priority 3 (Minor): {N} issues, {X} hours estimated

Proceeding with automatic remediation for all critical, major, and easy minor findings.
```

Do not ask whether to implement critical or major fixes. Start remediation immediately unless the fix requires a user decision as defined in Automatic Fix Classification. Do not stop after writing a failing audit report.

---

## Re-Audit After Fixes

After implementing fixes:

```bash
/audit_epic {epic-id}
```

The audit writes a new `reviews/audit-NNN/` directory, updates `audit-manifest.yaml`, updates `audit-verification-matrix.yaml`, updates `audit-issue-ledger.yaml`, writes `exploratory-residual-review.md`, and updates the existing `epic_audit.md` with new findings and progress:

```markdown
## Audit History

### Audit #2 - {date}
Status: PASS ✅
Critical: 0 (was 2)
Major: 1 (was 4)
Minor: 2 (was 6)
New major/critical issues: 0

### Audit #1 - {date}
Status: FAIL ❌
Critical: 2
Major: 4
Minor: 6
```

The command may run at most 3 total full/reviewer audit attempts for one audit cycle: the initial audit plus up to 2 remediation cycles. If attempt 3 still has open critical or major findings, stop, mark the audit failed, and document the unresolved findings and blockers in `epic_audit.md`. Focused local evidence gathered during remediation does not reset or extend this ceiling.

For large epics, require two clean consecutive audits before merge when feasible within the 3-attempt cap. A large epic is one with 8 or more implementation stories, more than 30 changed implementation/test files, runtime evidence requirements, or prior audits that found new major/critical issues. A clean audit means zero critical findings, zero major findings, and zero new major/critical findings in the issue ledger. If two clean audits are not reached within the 3-attempt cap, the final status is determined by the latest attempt and unresolved issue list.

---

## Example Session

```
User: /audit_epic {epic-id}
