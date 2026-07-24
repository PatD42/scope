---
name: implement
description: Deliver a refined epic sequentially from validated boundary plans through tests, runtime proof, audit remediation, and completion evidence.
args: "{epic-id}"
skills: project-documentation, scope-workflows
agents: architect, developer
---

# /implement

Implement and deliver a refined epic in a git worktree. This is a delivery
workflow, not merely a coding workflow.

**Syntax:** `/implement {epic-id}`

## Completion Contract

Report `delivery-complete` only when:

- the refinement handoff is valid;
- all stories and binding boundary-plan obligations are complete;
- required native contracts and integration touchpoints are satisfied;
- unit, integration, end-to-end, static, runtime, and operational proof required
  by the epic has passed;
- acceptance traceability and implementation evidence contain actual evidence;
- the intended user/business outcome is demonstrated;
- the real installed `/audit_epic` workflow passes after any remediation;
- `implementation-summary.md` records the delivered outcome and residual risks.

Otherwise report one of:

- `in-progress`;
- `blocked`;
- `implementation-complete, proof-pending`;
- `implementation-complete, rollout-pending`;
- `implementation-complete, audit-pending`;
- `implementation-complete, documentation-decision-pending`.

Never call an epic complete because code exists or unit tests pass.

## Installed Sources

Use only the active checkout or implementation worktree:

- command: `.claude/commands/implement.md`;
- nested audit: `.claude/commands/audit_epic.md`;
- developer role: `.claude/agents/developer.md`;
- architect role: `.claude/agents/architect.md`;
- governance: `.claude/governance/*.md`;
- policy: `.claude/config/refinement-policy.yaml`;
- validator: `.claude/scripts/validate-refinement.py`.

Do not read `plugins/scope/` or another checkout as an override. After entering the
worktree, use `.claude/` from that worktree only.

## Execution Model

Claude performs architect and developer roles sequentially in the current
session. Do not spawn sub-agents unless the user explicitly requests delegation.

Implement stories in topological `depends_on` order. Work on one story at a
time. Do not make speculative changes for later stories.

Candidate files are advisory. These boundary-plan fields are binding:

- `required_contracts`;
- `required_touchpoints`;
- `forbidden_changes`;
- `proof_obligations`.

If implementation would require a new product or architecture decision, stop
and return to refinement. Do not hide the decision in code.

---

## Step 0 — Locate and Validate the Handoff

```bash
EPIC_ID="{epic-id}"
PROJECT_ROOT="$(pwd)"
EPIC_DIR="$(find docs/epics -mindepth 1 -maxdepth 1 -type d \
  -iname "*${EPIC_ID}*" -print | sort | head -1)"

if [ -z "$EPIC_DIR" ]; then
  echo "Epic not found under docs/epics: ${EPIC_ID}"
  exit 1
fi

EPIC_SLUG="$(basename "$EPIC_DIR")"
V2_VALIDATOR=".claude/scripts/validate-refinement.py"

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

Run the v2 handoff validator:

```bash
"$PYTHON_CMD" "$V2_VALIDATOR" "$EPIC_DIR" \
  --phase handoff \
  --repo-root "$PROJECT_ROOT"
```

Read:

- `refinement-profile.yaml`;
- `refinement-manifest.yaml`;
- `refinement-findings.yaml`;
- `refinement-review.md`;
- `acceptance-traceability.yaml`;
- all `file-plan-story-*.yaml`;
- the authored sources and native contracts cited by the manifest.

Stop if validation fails. Do not repair an invalid refinement handoff inside
implementation.

### Refinement change check

Resolve the exact refinement paths:

- the epic directory;
- manifest artifact paths.

Run `git status --short -- <resolved paths>`. If refinement paths are dirty:

1. show the exact scoped list;
2. confirm they are refinement artifacts rather than unrelated work;
3. stage only those paths;
4. commit them as `refine({epic-id}): implementation handoff`;
5. leave every unrelated dirty path untouched.

Creating the worktree from stale refinement artifacts is not allowed.

---

## Step 1 — Create or Resume the Worktree

Scope compatibility requires this branch and directory convention:

```bash
BRANCH_NAME="epic/${EPIC_ID}"
WORKTREE_DIR="${PROJECT_ROOT}/wip/${EPIC_ID}"

if [ -d "$WORKTREE_DIR" ]; then
  git worktree list --porcelain | rg -F "worktree ${WORKTREE_DIR}"
else
  git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}" \
    || git branch "$BRANCH_NAME"
  git worktree add "$WORKTREE_DIR" "$BRANCH_NAME"
fi

cd "$WORKTREE_DIR"
```

Do not overwrite or regenerate `CLAUDE.md` in the worktree. It belongs to the
repository.

If the main project has `.env` and the worktree has no `.env`, create a symlink
to the explicit main-project file. Never overwrite a worktree-specific `.env`.

```bash
if [ ! -e .env ] && [ -f "${PROJECT_ROOT}/.env" ]; then
  ln -s "${PROJECT_ROOT}/.env" .env
fi
```

Read the worktree's `CLAUDE.md`, Scope role, and governance files again. All
subsequent source/test work occurs in the worktree.

### CodeGraph

CodeGraph is worktree-local during implementation:

```bash
if command -v codegraph >/dev/null 2>&1; then
  if [ ! -d .codegraph ]; then
    codegraph init .
    codegraph index .
  else
    codegraph sync-if-dirty . || codegraph sync .
  fi
  codegraph status .
fi
```

Use it for dependency discovery, then confirm decisions with direct source and
test evidence.

---

## Step 2 — Build the Story Graph

Read every `file-plan-story-*.yaml` from the epic directory in the worktree.
Parse YAML fields, not comments:

- `story_id`;
- `story_title`;
- `depends_on`;
- binding obligations;
- candidate files;
- proof obligations.

Validate:

- story IDs are unique;
- every dependency exists;
- no story depends on itself;
- the dependency graph is acyclic;
- each v2 manifest `owner_story` exists;
- every traceability row references an existing story.

Produce a topological story order. Story filename order is only a tie-breaker
between otherwise independent stories.

Create or update the Claude task list with one in-progress story at a time. Do
not use parallel writers.

Present:

- story count and order;
- Story 0 presence and actual purpose;
- dependency edges;
- capability modules involved;
- runtime/operational stories;
- high-risk proof obligations.

---

## Step 3 — Environment Readiness

Before editing code, verify the prerequisites named by the active stories:

- required environment variables are visible without printing secrets;
- local schemas and migrations are current enough to run tests;
- required services or containers are reachable;
- configured interpreters, package managers, and test tools exist;
- credentials needed for runtime proof are present;
- external provider or model limits that can block the epic are understood.

Do not defer predictable environment blockers until the audit. If a prerequisite
cannot be satisfied, identify affected stories and proof rows and report
`blocked` or `proof-pending`.

---

## Step 4 — Execute Stories Sequentially

For each story in topological order, follow this loop.

### 4.1 Load the minimum sufficient context

Read:

- the active boundary plan;
- relevant acceptance criteria;
- manifest rows whose `owner_story` is the active story;
- matching traceability rows;
- relevant architecture and ADR sections;
- relevant native contracts;
- the test-strategy sections for this story;
- applicable project lessons and governance.

Do not reload every epic artifact when stable IDs provide a smaller context.

### 4.2 Inspect before writing

Inspect:

- candidate files and actual implementation alternatives;
- immediate callers and consumers;
- shared utilities;
- current tests and fixtures;
- source/native contract definitions;
- protected surfaces from `forbidden_changes`.

State a concise implementation strategy:

- current path inspected;
- selected approach and why;
- binding contracts/touchpoints;
- accepted or skipped candidate files with evidence;
- developer-discovered files;
- proof commands;
- assumptions or blockers.

If the strategy materially changes architecture, stop and return to refinement.

### 4.3 Implement the smallest complete change

- Match existing project patterns.
- Reuse maintained libraries and existing utilities when appropriate.
- Do not add compatibility layers, abstractions, or adjacent cleanup that the
  story does not need.
- Preserve forbidden behavior and interfaces.
- Satisfy every native `required_contracts` obligation using its listed
  verification mechanism. Do not assume mypy unless the plan names it.
- Wire real entrypoints, upstream inputs, and downstream effects.
- Do not leave placeholder, mock-only, TODO, or dead production behavior.
- Keep production values in the project's configured configuration system.

### 4.4 Prove the story

Run all proof obligations from the boundary plan and traceability rows:

- focused unit tests;
- integration tests at real component boundaries;
- end-to-end tests for vertical behavior;
- native schema/static contract checks;
- live smoke or representative runtime commands;
- migrations, backfills, seeds, reindexes, syncs, or other one-time operations;
- negative and partial-state probes;
- non-zero output or threshold measurements when the promise requires them.

Unit tests do not prove an external adapter, database write, queue path, command,
worker, migration, generated artifact, or user-facing outcome by themselves.

If runtime proof is required but an external dependency is unavailable:

1. keep the row non-complete;
2. record the concrete blocker and attempted command;
3. report it immediately;
4. do not relabel it as not applicable.

### 4.5 Update evidence transactionally

After each story, update `acceptance-traceability.yaml`:

- `actual_files`;
- `actual_tests` with concrete test identifiers;
- runtime commands and evidence paths;
- status: `implemented`, `tested`, `verified`, `blocked`, or `deferred`;
- audit notes.

Create or update `implementation-evidence.yaml`:

```yaml
schema_version: 2
epic_id: "{epic-id}"
stories:
  - story_id: "story-01"
    status: "complete | implementation_complete_unverified | blocked"
    acceptance_rows: ["AC-001"]
    strategy:
      inspected_paths: []
      selected_approach: ""
      candidate_files_used: []
      candidate_files_skipped: []
      discovered_files: []
    files_changed: []
    tests_added_or_updated: []
    contract_checks: []
    commands_run:
      - command: "exact command"
        status: "pass | fail | blocked"
        evidence: "repo-relative evidence path or concise captured result"
    runtime_evidence: []
    value_proof: "Observable story outcome"
    remaining_unproven_work: []
epic_level:
  tests: {}
  coverage: {}
  operational_deliverables: []
  blocked_rows: []
audit_ready: false
```

Every completed story needs mapped acceptance rows, actual changed files,
verification evidence, and no remaining required proof. Story 0 may omit
acceptance rows only when it is pure scaffolding and its boundary plan proves
the scaffolding outcome.

### 4.6 Story checkpoint

Before advancing:

- read `.claude/governance/developer-checklist.md` from the worktree;
- run the focused checks again after the final edit;
- confirm traceability and evidence are current;
- summarize what is complete, verified, blocked, and left.

Do not continue from a state that cannot be described and reproduced.

---

## Step 5 — Epic-Wide Verification

After all planned stories are implemented:

### Source and contract checks

Run project-appropriate commands named by test strategy, boundary plans, native
contracts, and repository governance. Examples may include formatting, lint,
type checks, schema parsing, API validation, SQL validation, dead-code checks,
or frontend builds. Do not impose a language-specific tool that the project does
not use.

### Test checks

Collect tests from:

- traceability `actual_tests` and `expected_files`;
- implementation evidence;
- boundary-plan proof commands;
- changed modules and their existing regression tests.

Run focused tests first, then the appropriate broader regression suite. Report
pass/fail/error/skip counts and measured coverage. A skipped required test is a
failure unless the user approved a documented exception.

### Runtime and operational checks

For every runtime-required row:

- run the wired checker/command;
- record environment, result, and evidence;
- validate resulting state or artifact;
- measure non-zero or threshold outcomes where applicable.

Execute required migrations, backfills, seeds, reindexes, onboarding, syncs, or
rollout steps. Code for an operational task is not proof that the task ran.

### Value delivery check

Answer from evidence:

1. What user/business outcome was promised?
2. What can the real system do now that it could not do before?
3. Which concrete state, output, measurement, or interaction proves it?

If the answer is only “the code and tests exist,” delivery proof is incomplete.

### Pre-audit evidence package

Complete `implementation-evidence.yaml` and set `audit_ready: true` only when all
required/high-risk rows have appropriate proof.

Before handing off to audit, every required/high-risk traceability row must
identify:

- requirement and risk;
- actual implementation files;
- required assertions and actual tests;
- runtime requirement, command, and evidence;
- final implementation-evidence status.

Stop before audit if the package is mechanically incomplete. Missing evidence is
an implementation handoff failure, not something reviewers should discover.

Do not create `audit-verification-matrix.yaml`. The installed audit tool derives
it one-to-one from acceptance traceability so implementation cannot silently
change audit scope.

---

## Step 6 — Run the Real Scope Audit

Audit means executing the installed command workflow, not writing an informal
review or directly editing `epic_audit.md`.

1. Read `.claude/commands/audit_epic.md` from the active worktree.
2. Record the highest existing `reviews/audit-NNN` attempt.
3. Execute `/audit_epic {epic-id}` exactly as that command specifies.
4. Confirm a new attempt directory, `audit-attempt.yaml`, the attempt and
   published matrices, `audit-findings.yaml`, required reviewer-role outputs,
   and `epic_audit.md` were produced.
5. Confirm the audit completion validator passed.

If no new audit attempt exists, report `implementation-complete, audit-pending`.

Do not substitute a local summary, same-agent code review, or hand-written audit
artifact for the nested command.

---

## Step 7 — Remediate Audit Findings

Read `audit-findings.yaml` and `epic_audit.md`.

- For `PASS`, proceed to completion.
- Implement findings with disposition `remediation_required` within the approved
  implementation boundary.
- Group corrections by root cause and affected surface.
- Inspect sibling surfaces identified by the audit; do not patch only the named
  symptom.
- Add or update tests/runtime evidence that would have caught the defect.
- Update implementation evidence and actual traceability evidence mappings, but
  do not edit the audit matrix directly; the audit tool derives a fresh matrix.
- Set corrected findings to `remediated_pending_verification` only after their
  stated closure tests are ready.
- Ask the user for `user_decision` and `documentation_decision` findings and for
  product, architecture, security, destructive, credential, or scope decisions.
- Do not change approved documentation merely to make divergent code appear
  compliant.

After remediation, rerun the real `/audit_epic` command once. It must select
targeted mode for the named findings, affected acceptance rows, closure tests,
and directly coupled sibling surfaces. The audit command owns reviewer scope;
`implement` must not create extra informal review rounds or another broad audit.

If targeted verification remains `FAIL` or `BLOCKED`, report `blocked` with the
remaining finding IDs and evidence. Another full audit requires a material
approved scope/boundary change or explicit user authorization. Do not declare
delivery complete.

---

## Step 8 — Completion Artifacts

When tests, runtime proof, operational work, and audit are green, update
`implementation-summary.md` with:

- approved intent and delivered value;
- stories and actual completion states;
- acceptance-proof summary by stable row ID;
- implementation and test files;
- native contract checks;
- test counts and measured coverage;
- runtime and representative-data evidence;
- operational deliverables executed;
- audit attempts, corrections, and final status;
- residual risks and documentation decisions;
- environment or setup issues encountered.

Review documentation implications from implementation and audit. Surface each
as:

- approved update now;
- deferred to `/wrap_epic`;
- blocked on user decision.

Do not silently launder implementation drift into architecture documentation.

Write the implementation command marker under `.scope/tracking/commands/` with
the epic ID, completed time, story count, proof status, and final audit status.

Do not merge, remove, or clean the worktree. The user controls wrap/merge.

## Completion Output

Report:

- exact delivery status;
- worktree and branch;
- stories completed/blocked;
- test pass/fail/error/skip counts and coverage;
- native contract checks;
- runtime and operational evidence;
- value-delivery proof;
- audit attempt IDs, reviewer coverage, and final status;
- completion-summary path;
- residual risks or documentation decisions;
- recommended next command: `/wrap_epic {epic-id}` when delivery is complete.

## Compaction Recovery

Resume from artifacts rather than conversation memory:

1. validate the refinement handoff again;
2. inspect the worktree and branch;
3. read story graph and traceability statuses;
4. read `implementation-evidence.yaml` for story proof and blockers;
5. read the audit matrix, findings ledger, report, and latest attempt metadata;
6. continue from the first non-verified requirement or open audit finding.

Never infer story or delivery completion from changed files alone.
