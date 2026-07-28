---
name: audit_epic
description: Perform a read-only, evidence-based audit of an implemented epic and return PASS, FAIL, BLOCKED, or NOT_READY.
args: "{epic-id}"
skills: project-documentation, scope-workflows
---

# audit_epic

Audit an implemented epic against approved requirements, architecture, native
contracts, current implementation evidence, and real system behavior.

**Syntax:** `/audit_epic {epic-id}` or `scope:audit_epic {epic-id}`

## Outcome Contract

Return exactly one outcome:

- `PASS` — all scoped acceptance rows and required gates pass, every required
  provider completed, and no active findings remain;
- `FAIL` — implementation or evidence has a finding remediable within approved
  scope;
- `BLOCKED` — required evidence or a required provider is unavailable, or a
  product, architecture, security, destructive, credential, or scope decision
  is required;
- `NOT_READY` — the implementation evidence verifier rejected the handoff, so
  no attempt was created.

Audit is read-only. It may write audit artifacts and raw output under
`tmp_debug/scope-audit/`; it must not edit implementation, tests, approved
requirements, native contracts, refinement artifacts, or implementation
evidence. Implementation owns remediation.

Do not vote by provider, report consensus percentages, or discard a
well-evidenced minority finding.

## Installed Sources

Use only the active checkout or worktree. Codex reads `plugins/scope/`; Claude
reads `.claude/`.

- command: `{scope-root}/commands/audit_epic.md`;
- reviewer contract: `{scope-root}/commands/audit_epic/reviewer-audit.md`;
- policy: `{scope-root}/config/audit-policy.yaml`;
- audit tool: `{scope-root}/scripts/audit-artifacts.py`;
- Claude runner: `{scope-root}/scripts/scope-reviewer-claude-pexpect.py`.

## Artifact Contract

```text
docs/epics/{epic-dir}/
├── audit-findings.yaml
├── audit-verification-matrix.yaml
├── epic_audit.md
└── reviews/audit-NNN/
    ├── audit-attempt.yaml
    ├── audit-verification-matrix.yaml
    ├── review-packet.yaml
    ├── review-{provider}-semantic-core.md
    └── metadata-{provider}-semantic-core.yaml
```

Bulky command output, rendered prompts, transcripts, and stderr belong under:

```text
tmp_debug/scope-audit/{epic-id}/{audit-NNN}/
```

The default `audit-v3` cycle permits one full audit and one targeted
verification. Another full audit requires a material approved boundary change
or explicit user authorization with a recorded reason.

## Phase 0 — Verify the Handoff

Locate exactly one epic directory under `docs/epics/`. Set:

```bash
EPIC_ID="{epic-id}"
REPO_ROOT="$(pwd)"
EPIC_DIR="docs/epics/{resolved-epic-directory}"
SCOPE_ROOT="{plugins/scope for Codex, or .claude for Claude}"
AUDIT_TOOL="${SCOPE_ROOT}/scripts/audit-artifacts.py"
AUDIT_POLICY="${SCOPE_ROOT}/config/audit-policy.yaml"
REVIEWER_PROMPT="${SCOPE_ROOT}/commands/audit_epic/reviewer-audit.md"
CLAUDE_RUNNER="${SCOPE_ROOT}/scripts/scope-reviewer-claude-pexpect.py"

if [ -n "${SCOPE_PYTHON:-}" ]; then
  PYTHON_CMD="$SCOPE_PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Scope audit requires Python 3."
  exit 1
fi
```

Run the exact verifier used by implementation:

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" verify-evidence "$EPIC_DIR" \
  --repo-root "$REPO_ROOT" \
  --policy "$AUDIT_POLICY"
```

The verifier checks schema v3, `audit_ready`, repository fingerprint, story
statuses, changed-file classification, cited paths, raw-output hashes, command
results, traceability parity, current proof-obligation coverage, test mappings,
and required runtime evidence. Any failure returns `NOT_READY`; do not create an
attempt or repair implementation evidence inside audit.

## Phase 1 — Prepare the Attempt

Use full mode unless one or more findings are
`remediated_pending_verification`.

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" prepare "$EPIC_DIR" \
  --repo-root "$REPO_ROOT" \
  --policy "$AUDIT_POLICY" \
  --mode full \
  --cycle-id audit-v3
```

Targeted mode names findings and directly coupled sibling surfaces:

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" prepare "$EPIC_DIR" \
  --repo-root "$REPO_ROOT" \
  --policy "$AUDIT_POLICY" \
  --mode targeted \
  --cycle-id audit-v3 \
  --finding AUDIT-FINDING-ID \
  --sibling-surface path-or-contract
```

Record the printed attempt directory as `ATTEMPT_DIR`. Preparation:

- re-verifies implementation evidence;
- derives one matrix row per traceability row with mechanical status `ready`;
- selects Claude, Codex, and AGY for every full semantic review;
- selects only the originating provider(s) for targeted semantic verification;
- creates a compact, diff-centric `review-packet.yaml`;
- reuses passing broad or focused evidence only when command and repository
  fingerprint match;
- leaves critical, explicitly fresh, and finding-closure gates pending;
- enforces the attempt budget.

## Phase 2 — Establish Mechanical Gates

Read `gates` from `audit-attempt.yaml`.

- Do not rerun a gate already marked `pass` with `reused: true`.
- Run every pending critical, freshness-required, or targeted closure gate.
- Add only project-native gates required by repository governance or the
  approved proof strategy.
- Capture exact command, exit status, pass/fail/error/skip counts when
  applicable, and raw output under the attempt debug directory.
- A required skipped test is a failure.
- Never execute paid, destructive, credentialed, production, migration,
  backfill, or external-state-changing operations without existing authority.

Update each gate to `pass`, `fail`, `blocked`, or `not_applicable`, with evidence
and a reason where required. Do not semantically classify matrix rows in this
phase; the evidence verifier already established mechanical readiness.

Run:

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" validate "$EPIC_DIR" "$ATTEMPT_DIR" \
  --repo-root "$REPO_ROOT" \
  --policy "$AUDIT_POLICY" \
  --phase pre_review
```

If a deterministic gate fails or is blocked, create a deterministic finding
with `source: deterministic` and `detected_by: []`. Reviewer judgment cannot
override it. Skip reviewers only when the attempt cannot meaningfully proceed,
then continue to the decision phase.

## Phase 3 — Concurrent Three-Provider Semantic Review

Read `review.required_assignments` and `review-packet.yaml`.

Every full attempt contains these assignments, regardless of risk:

```yaml
- provider: claude
  mission: semantic_core
- provider: codex
  mission: semantic_core
- provider: agy
  mission: semantic_core
```

High/critical capability focus is embedded in each semantic review. Do not add a
fourth specialist process. Targeted attempts contain only providers listed in
the original reviewer finding's `detected_by`; deterministic-only closure may
skip semantic review.

Render the shared `reviewer-audit.md` once per assignment with provider, mission,
review packet, repository root, output path, and Reviewer identity. Each process
is a fresh reviewer process and owns distinct prompt, output, metadata, and log
paths.

### Codex

```bash
CODEX_MODEL_ID="${SCOPE_CODEX_MODEL_ID:-gpt-5.6-terra}"
CODEX_REASONING_EFFORT="${SCOPE_CODEX_REASONING_EFFORT:-high}"

codex exec \
  --ephemeral \
  --ignore-user-config \
  --cd "$REPO_ROOT" \
  --model "$CODEX_MODEL_ID" \
  -c model_reasoning_effort="\"$CODEX_REASONING_EFFORT\"" \
  --sandbox read-only \
  --output-last-message "$REVIEW_OUTPUT_PATH" \
  - < "$RENDERED_REVIEW_PROMPT"
```

### Claude

```bash
"$PYTHON_CMD" "$CLAUDE_RUNNER" \
  --reviewer "semantic_core" \
  --model "Claude Opus (local alias)" \
  --claude-command "claude --model opus --safe-mode --strict-mcp-config --mcp-config '{}' --dangerously-skip-permissions --no-chrome" \
  --prompt-file "$RENDERED_REVIEW_PROMPT" \
  --output-file "$REVIEW_OUTPUT_PATH" \
  --metadata-file "$REVIEW_METADATA_PATH" \
  --cwd "$REPO_ROOT" \
  --retries 0
```

### Antigravity

Use exact model IDs reported by `agy models`:

```bash
AGY_MODEL="${SCOPE_AGY_MODEL:-gemini-3.1-pro-high}"
AGY_FALLBACK_MODEL="${SCOPE_AGY_FALLBACK_MODEL:-gemini-3.5-flash-high}"
AGY_TIMEOUT="${SCOPE_AGY_PRINT_TIMEOUT:-60m}"

agy --model "$AGY_MODEL" \
  --sandbox \
  --dangerously-skip-permissions \
  --print-timeout "$AGY_TIMEOUT" \
  --print "$(cat "$RENDERED_REVIEW_PROMPT")" \
  > "$REVIEW_OUTPUT_PATH"
```

Validate the configured model against `agy models` before launch. Retry once
with the fallback only when stderr proves rate limiting or quota exhaustion; do
not retry other failures.

### Concurrency and Failure

Launch all required assignment commands before waiting for any result. Capture
one PID per process, then wait for all. Record provider, model, mission, status,
start/end time, duration, retry count, prompt bytes, output bytes, transport,
and repo-relative output path in each metadata file.

A missing or failed required provider makes the attempt `BLOCKED`. Do not
substitute another provider or the orchestrating context.

## Phase 4 — Merge Findings and Decide

Preserve every evidence-backed finding. Deduplicate only the same root cause,
surface, and closure condition. A finding first discovered in this attempt is:

```yaml
- id: AUDIT-001
  fingerprint: stable-category-surface-root-cause
  first_seen_attempt: audit-NNN
  severity: blocking | major | minor
  category: implementation | architecture_contract | native_contract | testability | runtime_evidence | operations | security | data_integrity | documentation | mechanical | specialist
  source: deterministic | reviewer
  detected_by: [claude, codex, agy]
  disposition: remediation_required | user_decision | documentation_decision | accepted_risk | false_positive
  status: open | remediated_pending_verification | verified | accepted_risk | rejected
  title: concise root cause
  evidence: [path-or-command-result]
  affected_acceptance_ids: [AC-001]
  affected_files: [path]
  impact: concrete consequence
  owner: implementation | user | documentation
  closure_test: exact runnable command or concrete semantic predicate
```

For deterministic findings, use `detected_by: []`. For reviewer findings,
include every provider that independently reported the same root cause; this is
provenance, not voting.

After merging:

- change each scoped `ready` matrix row to `pass`, `fail`, `blocked`,
  `unverified`, or justified `not_applicable`;
- attach finding IDs reciprocally;
- set attempt status and a non-empty decision reason;
- publish the attempt matrix to the epic root;
- write `epic_audit.md` with scope, gates, acceptance results, findings,
  provider coverage, test results, and residual risk.

Run mechanically generated metrics:

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" record-metrics "$EPIC_DIR" "$ATTEMPT_DIR"
```

Metrics count only findings whose `first_seen_attempt` is this attempt, grouped
by severity, category, deterministic/reviewer source, and detecting provider.
Agents never transcribe these counters.

## Phase 5 — Validate Completion

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" validate "$EPIC_DIR" "$ATTEMPT_DIR" \
  --repo-root "$REPO_ROOT" \
  --policy "$AUDIT_POLICY" \
  --phase complete
```

Completion validation checks evidence freshness, scope, matrix coverage, gates,
provider assignments and outputs, finding links, metrics, published artifacts,
and PASS/FAIL/BLOCKED consistency.

Audit never remediates:

- `PASS`: implementation may complete.
- `FAIL`: implementation fixes root causes, adds regression proof, refreshes
  implementation evidence, and requests the one targeted verification.
- `BLOCKED`: ask the user or restore the missing provider/evidence.
- targeted `FAIL` or `BLOCKED`: stop. Do not start another broad audit.

Do not claim completion when deterministic validation fails.
