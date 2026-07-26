---
name: audit_epic
description: Perform a read-only, evidence-based audit of an implemented epic and return PASS, FAIL, BLOCKED, or NOT_READY.
args: "{epic-id}"
skills: project-documentation, scope-workflows
---

# audit_epic

Audit an implemented epic against its approved requirements, architecture,
native contracts, implementation evidence, and real system behavior.

**Syntax:** `/audit_epic {epic-id}` or `scope:audit_epic {epic-id}`

## Outcome Contract

Return exactly one outcome:

- `PASS` — all scoped acceptance rows and required gates pass, required review
  roles completed, and no active findings remain;
- `FAIL` — implementation or evidence has one or more findings that can be
  remediated within approved scope;
- `BLOCKED` — required evidence cannot be obtained or a product, architecture,
  security, destructive, credential, or scope decision is required;
- `NOT_READY` — the implementation handoff is mechanically incomplete, so no
  audit attempt was started.

Audit is read-only. It may write only the audit artifacts listed below and raw
debug output under `tmp_debug/scope-audit/`. It must not edit implementation,
tests, approved requirements, architecture, native contracts, refinement
artifacts, or implementation evidence. The implementation workflow owns all
remediation.

Do not report percentages, provider consensus, or fix-hour estimates. Report
what evidence proves, what failed, and what remains unresolved.

## Installed Sources

Use only the active checkout or worktree. Codex reads `plugins/scope/`; Claude
reads `.claude/`. Do not fall back to another checkout.

- command: `{scope-root}/commands/audit_epic.md`;
- reviewer contract: `{scope-root}/commands/audit_epic/reviewer-audit.md`;
- policy: `{scope-root}/config/audit-policy.yaml`;
- audit tool: `{scope-root}/scripts/audit-artifacts.py`;
- refinement validator: `{scope-root}/scripts/validate-refinement.py`.

Never use another checkout or a provider-specific reviewer prompt as an
override.

## Authoritative Evidence Chain

Read the project documentation skill first. Then use, in order:

1. `refinement-profile.yaml` and `refinement-manifest.yaml`;
2. acceptance criteria, epic `design.md`, native contracts, and the applicable
   architecture tree;
3. `acceptance-traceability.yaml`;
4. `file-plan-story-*.yaml` boundary plans;
5. native contracts cited by the manifest and boundary plans;
6. `implementation-evidence.yaml`;
7. actual changed source, tests, migrations, configuration, and operational
   artifacts;
8. raw results from project-native test, static, runtime, and operational
   commands.

The audit matrix is a status view of traceability. It is not a second
requirements model. Do not invent rows, reinterpret approved intent, or infer
success from an implementation summary.

## Artifact Contract

Canonical outputs are:

```text
docs/epics/{epic-dir}/
├── audit-findings.yaml
├── audit-verification-matrix.yaml
├── epic_audit.md
└── reviews/audit-NNN/
    ├── audit-attempt.yaml
    ├── audit-verification-matrix.yaml
    └── review-{role}.md
```

Do not consume deprecated audit manifests, issue ledgers, or provider-specific
review files as v2 handoff inputs.

Store bulky logs and transcripts under:

```text
tmp_debug/scope-audit/{epic-id}/{audit-NNN}/
```

Keep only concise, durable evidence in the epic directory.

## Review Budget

The default audit cycle is `audit-v2` and permits:

- one full audit;
- one targeted verification after remediation.

Do not start another full audit because a review was noisy or remediation was
performed. Another full attempt requires a material change to approved product
scope, architecture, native contracts, or implementation boundary, or explicit
user authorization. Record the reason and use a new cycle ID when the change
creates a genuinely new audit cycle. `--allow-extra` is only for explicit user
authorization and must include `--reason`.

## Phase 0 — Locate and Validate the Handoff

Locate exactly one epic directory under `docs/epics/`. If the identifier is
missing or ambiguous, stop with `NOT_READY` and do not create an attempt.

Set:

```bash
EPIC_ID="{epic-id}"
REPO_ROOT="$(pwd)"
EPIC_DIR="docs/epics/{resolved-epic-directory}"
# Set this from the active platform. Never select another checkout:
#   Codex:  SCOPE_ROOT="plugins/scope"
#   Claude: SCOPE_ROOT=".claude"
SCOPE_ROOT="{active Scope installation root}"
AUDIT_TOOL="${SCOPE_ROOT}/scripts/audit-artifacts.py"
REFINEMENT_VALIDATOR="${SCOPE_ROOT}/scripts/validate-refinement.py"
AUDIT_POLICY="${SCOPE_ROOT}/config/audit-policy.yaml"
REVIEWER_PROMPT="${SCOPE_ROOT}/commands/audit_epic/reviewer-audit.md"
CLAUDE_REVIEWER_RUNNER="${SCOPE_ROOT}/scripts/scope-reviewer-claude-pexpect.py"

if [ -n "${SCOPE_PYTHON:-}" ]; then
  PYTHON_CMD="$SCOPE_PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Scope v2 requires Python 3. Install Python and set SCOPE_PYTHON."
  exit 1
fi

if ! "$PYTHON_CMD" -c "import yaml" >/dev/null 2>&1; then
  echo "Scope v2 requires PyYAML. Run: $PYTHON_CMD -m pip install 'PyYAML>=6,<7'"
  exit 1
fi
```

Run the installed refinement validator's handoff phase. Require:

- a valid refinement handoff;
- `implementation-evidence.yaml` with `audit_ready: true`;
- traceability mappings to actual files, tests, assertions, and required
  runtime evidence;
- no unresolved implementation or rollout blocker hidden behind ready status.

Any missing handoff requirement returns `NOT_READY`. Explain the exact missing
file, field, or proof and stop before `prepare`.

## Phase 1 — Select and Prepare the Attempt

Use `full` unless there are findings with status
`remediated_pending_verification`. When those exist, use `targeted` and include
their IDs. A targeted attempt may also name directly coupled sibling surfaces
that share the defect pattern.

Full preparation:

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" prepare "$EPIC_DIR" \
  --repo-root "$REPO_ROOT" \
  --policy "$AUDIT_POLICY" \
  --mode full \
  --cycle-id audit-v2
```

Targeted preparation:

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" prepare "$EPIC_DIR" \
  --repo-root "$REPO_ROOT" \
  --policy "$AUDIT_POLICY" \
  --mode targeted \
  --cycle-id audit-v2 \
  --finding AUDIT-FINDING-ID \
  --sibling-surface path-or-contract
```

The command prints the new attempt directory. Record it as `ATTEMPT_DIR`.
Preparation mechanically:

- selects roles from risk;
- derives exactly one matrix row per traceability item;
- copies evidence mappings without inventing new requirements;
- records full or targeted scope;
- discovers boundary-plan proof commands;
- records changed files;
- enforces the review budget.

If preparation fails, report its exact error. Do not hand-create an attempt or
matrix to bypass it.

## Phase 2 — Establish Mechanical Evidence

Work only in the prepared attempt and raw debug directory.

### 2.1 Run project-native gates

Start with commands recorded in `audit-attempt.yaml`. Add only commands required
by:

- repository instructions;
- the project test strategy;
- implementation evidence;
- native contracts or boundary-plan proof obligations;
- the selected targeted finding closure tests.

Do not impose Python, mypy, Vulture, PostgreSQL, container, or cloud checks
unless the project evidence requires them.

Run focused tests first, then the applicable broader regression suite. For each
command record:

- exact command;
- status: `pass`, `fail`, `blocked`, or `not_applicable`;
- concise evidence path;
- a reason for `blocked` or `not_applicable`.

Never claim tests passed if any required tests were skipped. Report pass, fail,
error, and skip counts and measured coverage when the project produces it.

Do not run paid, destructive, credentialed, production, migration, backfill, or
external-state-changing operations without existing authorization. If required
proof needs new authority, mark the gate and affected rows `blocked`.

### 2.2 Verify every scoped matrix row

Inspect actual implementation paths and real call paths. Update the attempt
matrix status for each scoped row:

- `pass` — direct code/test/runtime evidence proves the approved outcome;
- `fail` — evidence proves a mismatch or defect;
- `unverified` — the required evidence is absent or inconclusive;
- `blocked` — obtaining required evidence needs authority or an unavailable
  dependency;
- `not_applicable` — the approved row truly does not apply, with a reason.

For required implementation rows, identify actual implementation files,
required assertions, and actual tests. For runtime-required rows, retain exact
commands and evidence. A prose summary, mocked-only test, or file existence is
not runtime proof.

### 2.3 Validate before review

Run:

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" validate "$EPIC_DIR" "$ATTEMPT_DIR" \
  --repo-root "$REPO_ROOT" \
  --policy "$AUDIT_POLICY" \
  --phase pre_review
```

Fix audit-artifact mechanics only: malformed YAML, wrong paths, incomplete
status recording, or missing evidence references. Never edit product artifacts
to make validation pass.

If required evidence remains failed, unverified, or blocked, reviewer judgment
cannot replace it. Record findings, set `review.skipped_reason`, classify the
attempt as `FAIL` or `BLOCKED`, and continue to Phase 4.

## Phase 3 — Run Risk-Directed Reviews

Read `review.required_roles` from `audit-attempt.yaml`. Default policy is:

| Risk | Roles |
|---|---|
| low | `implementation_integrity` |
| medium | `implementation_integrity`, `contract_and_evidence` |
| high/critical | both core roles plus `capability_specialist` |

Perform every role in a fresh reviewer process. One output cannot satisfy
multiple roles. Render prompts under `tmp_debug/scope-audit/{epic-id}/{attempt}/`
so absolute runtime paths never enter durable audit artifacts.

For Codex orchestration, every role uses these exact defaults:

```bash
CODEX_MODEL_ID="${SCOPE_CODEX_MODEL_ID:-gpt-5.6-terra}"
CODEX_REASONING_EFFORT="${SCOPE_CODEX_REASONING_EFFORT:-high}"

codex exec \
  --cd "$REPO_ROOT" \
  --model "$CODEX_MODEL_ID" \
  -c model_reasoning_effort="\"$CODEX_REASONING_EFFORT\"" \
  --sandbox read-only \
  --output-last-message "$OUTPUT_PATH" \
  - < "$RENDERED_REVIEW_PROMPT"
```

For Claude orchestration, every role uses a fresh Opus process through
`scope-reviewer-claude-pexpect.py` with
`--dangerously-skip-permissions`:

```bash
"$PYTHON_CMD" "$CLAUDE_REVIEWER_RUNNER" \
  --reviewer "$AUDIT_ROLE" \
  --model "Claude Opus (local alias)" \
  --claude-command "claude --model opus --dangerously-skip-permissions --no-chrome" \
  --prompt-file "$RENDERED_REVIEW_PROMPT" \
  --output-file "$OUTPUT_PATH" \
  --metadata-file "$REVIEW_METADATA_PATH" \
  --cwd "$REPO_ROOT"
```

Store PTY logs under `tmp_debug/scope-reviewer-logs/`.

For each role:

1. read `reviewer-audit.md` in full;
2. substitute the epic ID, role, runtime repository root, reviewer identity,
   attempt path, matrix path, output path, and specialist focus;
3. inspect the cited repository evidence directly;
4. write `reviews/audit-NNN/review-{role}.md`;
5. add `{role, path}` to `review.outputs`.

Do not run the same role through several providers and vote on the result.
Reviewer identity is metadata and never changes the acceptance standard. If the
active platform's reviewer CLI or required runtime is unavailable, leave the
role incomplete and return `BLOCKED`; do not use the orchestrating context as a
substitute.

Reviewer conclusions cannot override a failing deterministic gate. Do not ask
one role to repeat another role's mission.

## Phase 4 — Merge Findings and Decide

Merge mechanical and reviewer findings into `audit-findings.yaml`. Reuse an
existing finding with the same fingerprint. Allocate a new stable ID only for a
new root cause.

Each finding must contain:

```yaml
- id: AUDIT-001
  fingerprint: stable-category-surface-root-cause
  first_seen_attempt: audit-NNN
  severity: blocking | major | minor
  category: implementation | architecture_contract | native_contract | testability | runtime_evidence | operations | security | data_integrity | documentation | mechanical | specialist
  disposition: remediation_required | user_decision | documentation_decision | accepted_risk | false_positive
  status: open | remediated_pending_verification | verified | accepted_risk | rejected
  title: concise root cause
  evidence:
    - path-or-command-result
  affected_acceptance_ids:
    - AC-001
  affected_files:
    - path
  impact: concrete consequence
  owner: implementation | user | documentation
  closure_test: exact evidence that closes the finding
  reviewer_roles:
    - implementation_integrity
```

Severity and disposition are independent. Missing proof is `unverified`; do not
assert a runtime defect without evidence. Do not combine unrelated root causes
or create duplicates for reviewer agreement.

Set the attempt status:

- `pass` only when all scoped rows and gates pass or are justified
  `not_applicable`, required roles completed, and no active finding remains;
- `fail` for remediation findings or failed/unverified evidence;
- `blocked` for decision-gated findings or blocked required evidence.

Write a non-empty `decision_reason` and `epic_audit.md` with this minimum shape:

```markdown
# Epic Audit: {epic-id}

Decision: PASS | FAIL | BLOCKED

## Scope and Profile
## Evidence Gates
## Acceptance Results
## Findings
## Reviewer Roles
## Test and Coverage Results
## Residual Risk and Next Action
```

For targeted verification, update each named finding to `verified`,
`accepted_risk`, or `rejected` only when its closure test and affected/sibling
surfaces support that result. Do not silently close findings.

Publish the attempt matrix as the latest top-level matrix:

```bash
cp "$ATTEMPT_DIR/audit-verification-matrix.yaml" \
  "$EPIC_DIR/audit-verification-matrix.yaml"
```

This copy is an audit artifact write, not implementation remediation.

## Phase 5 — Validate Completion

Run:

```bash
"$PYTHON_CMD" "$AUDIT_TOOL" validate "$EPIC_DIR" "$ATTEMPT_DIR" \
  --repo-root "$REPO_ROOT" \
  --policy "$AUDIT_POLICY" \
  --phase complete
```

Completion validation checks identity, scope, matrix coverage, evidence fields,
gate states, reviewer roles, finding references, published matrix equality,
report decision, and PASS/FAIL/BLOCKED consistency.

If validation fails, correct audit artifacts only and rerun it. If a correction
would require implementation or approved-document changes, keep the attempt
failed or blocked and return it to `scope:implement` or the user.

## Remediation and Follow-up Contract

Audit never remediates.

- `PASS`: implementation may proceed to completion/wrap.
- `FAIL` with `remediation_required`: implementation fixes the root cause,
  updates tests/runtime proof and implementation evidence, marks the finding
  `remediated_pending_verification`, then requests the one targeted audit.
- `BLOCKED` or decision-gated finding: ask the user.
- targeted `FAIL`/`BLOCKED`: stop with the remaining finding IDs. Do not start
  another broad audit automatically.

Another full audit is appropriate only after a material scope/boundary change
or explicit user authorization.

## Completion Output

Report:

- outcome: `PASS`, `FAIL`, `BLOCKED`, or `NOT_READY`;
- attempt ID and mode, or why no attempt was created;
- evidence-gate and acceptance-row results;
- test pass/fail/error/skip counts and coverage;
- reviewer roles completed or skipped with reason;
- finding IDs grouped by disposition and status;
- residual risk;
- exact next action and owner.

Do not claim completion if the deterministic completion validator failed.
