---
name: epic_refine
description: Refine an epic into a repository-grounded, adversarially designed, independently reviewed implementation handoff.
args: "{epic-id}"
---

# epic_refine

Refine an epic until implementation can proceed without inventing product
behavior or architecture.

**Syntax:** `/epic_refine {epic-id}` or `scope:epic_refine {epic-id}`

## Outcome

The epic is ready only when:

- the user approved intent, product behavior, consequential architecture, and
  final handoff;
- current-state claims cite repository evidence;
- architecture answers all applicable capability challenges before approval;
- high/critical requirements have explicit flows and hostile cases;
- native contracts were actually validated;
- every implementation requirement has one story owner and proof obligation;
- deterministic reconciliation passes;
- every risk-required Claude/Codex assignment completed in a fresh process;
- no blocking finding, user question, or unresolved item remains;
- `details.md` has status `ready-for-implementation`.

## Fixed Contract

Authored truth:

- `details.md`: intent, scope, outcome, and status;
- `acceptance-criteria.md`: canonical product behavior with stable `AC-*`,
  `ERR-*`, and `E2E-*` IDs;
- `design.md`: current-state evidence, decisions, architecture, ownership,
  failures, capability challenges, hostile cases, and verification strategy;
- applicable native contracts;
- `file-plan-story-*.yaml`: implementation boundaries and proof.

Generated or review-owned indexes:

- `refinement-profile.yaml`;
- `refinement-manifest.yaml`;
- `acceptance-traceability.yaml`;
- `refinement-findings.yaml`;
- `refinement-review.md`.

Do not create the removed split epic files or `pre-review-audit.yaml`. This is a
v3-only workflow; do not add compatibility behavior.

## Core Rules

1. Product and architecture authoring stays in the current session. Independent
   reviews run in fresh CLI processes.
2. Use only the active checkout/worktree and its installed Scope files:
   Codex uses `plugins/scope/`; Claude uses `.claude/`.
3. Read repository instructions and inspect source, callers, consumers, tests,
   schemas, configuration, migrations, and runtime entrypoints before design.
4. Ask the user only for product, policy, scope, security, destructive, or
   irreversible decisions. Resolve mechanical issues autonomously.
5. Put each normative fact in one canonical artifact and cite its stable ID
   elsewhere.
6. Apply capability challenges while constructing architecture, not after it.
7. Run native validators before independent review. Never claim skipped
   execution.
8. Use the validator to generate mechanical rows. The author supplies semantic
   judgment.
9. Run one full review concurrently across the approved provider assignments.
   Low risk uses the provider opposite the author. Medium+ uses overlapping
   Claude and Codex semantic-core review. High/critical adds one specialist.
10. Preserve every evidence-backed minority finding. Never vote by provider.
11. Run only targeted verification after corrections. A second full review
    requires material redesign or explicit user approval.

## Initialize

Resolve the epic and active installation:

```bash
EPIC_ID="{epic-id}"
EPIC_DIR="$(find docs/epics -mindepth 1 -maxdepth 1 -type d \
  -iname "*${EPIC_ID}*" -print | sort | head -1)"

if [ -z "$EPIC_DIR" ]; then
  echo "Epic not found under docs/epics: ${EPIC_ID}"
  exit 1
fi

# Set these from the active platform:
#   Codex:  AUTHOR_PROVIDER="codex";  SCOPE_ROOT="plugins/scope"
#   Claude: AUTHOR_PROVIDER="claude"; SCOPE_ROOT=".claude"
AUTHOR_PROVIDER="{claude-or-codex}"
SCOPE_ROOT="{active Scope installation root}"

POLICY_PATH="${SCOPE_ROOT}/config/refinement-policy.yaml"
VALIDATOR_PATH="${SCOPE_ROOT}/scripts/validate-refinement.py"
REVIEWER_PROMPT="${SCOPE_ROOT}/commands/epic_refine/reviewer-refinement.md"
CLAUDE_RUNNER="${SCOPE_ROOT}/scripts/scope-reviewer-claude-pexpect.py"

if [ -n "${SCOPE_PYTHON:-}" ]; then
  PYTHON_CMD="$SCOPE_PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Scope v3 requires Python 3. Install Python and set SCOPE_PYTHON."
  exit 1
fi

if ! "$PYTHON_CMD" -c "import yaml" >/dev/null 2>&1; then
  echo "Scope v3 requires PyYAML. Run: $PYTHON_CMD -m pip install 'PyYAML>=6,<7'"
  exit 1
fi

for required in "$POLICY_PATH" "$VALIDATOR_PATH" "$REVIEWER_PROMPT"; do
  test -f "$required" || { echo "Missing Scope asset: $required"; exit 1; }
done

EPIC_SLUG="$(basename "$EPIC_DIR")"
RUNTIME_DIR="tmp_debug/scope-refine/${EPIC_SLUG}"
mkdir -p "$RUNTIME_DIR"
```

If a valid v3 profile exists, run each validator phase and resume at the first
failure. Do not infer or migrate old schemas.

---

## Phase 0: Intent and Profile

### Repository Grounding

Read:

- repository instructions;
- `details.md`;
- relevant product and architecture documentation;
- immediate source/test surfaces suggested by the epic;
- `refinement-policy.yaml`.

When CodeGraph is installed, sync the current checkout and use it to identify
callers, consumers, and affected boundaries. Treat its output as a navigation
aid and verify consequential claims in source.

Confirm the requested outcome, scope, non-goals, architecture scope, risk, and
applicable capabilities.

### Profile

Create `refinement-profile.yaml`:

```yaml
schema_version: 3
epic_id: "{epic-id}"
author_provider: "claude | codex"
architecture_scope: "none | system | backend | frontend | mixed"
risk_level: "low | medium | high | critical"
capabilities: []
workflow_started_at: "ISO-8601 UTC timestamp"
review:
  assignments:
    - provider: "provider required by the topology below"
      mission: "semantic_core | capability_specialist"
  maximum_full_reviews: 1
  maximum_targeted_verifications: 1
```

Assignments:

| Risk | Required assignments |
|---|---|
| low | one `semantic_core` assignment using the provider opposite `author_provider` |
| medium | Claude and Codex `semantic_core` |
| high/critical | Claude and Codex `semantic_core`, plus `capability_specialist` using `author_provider` |

High/critical risk requires at least one selected capability. Use maximum
targeted verifications `1` for low/medium and `2` for high/critical.

Run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" \
  --phase profile \
  --repo-root "$(pwd)" \
  --metrics-output "$RUNTIME_DIR/metrics-start.yaml"
```

### Gate 0

Present intent, scope, risk, capabilities, assignments, and user decisions.

Ask: **“Approve this refinement profile? [yes / refine]”**

---

## Phase 1: Product Contract

Create or update:

- `acceptance-criteria.md`;
- the `Product and Architecture Decisions` section of `design.md`;
- product-level content in `details.md`.

Requirements:

- one observable promise per canonical `## AC-*`, `## ERR-*`, or `## E2E-*`
  heading; references to an existing ID do not redeclare it;
- happy, rejection, error, recovery, partial-state, and operational outcomes
  where applicable;
- thresholds and success measures;
- explicit deferred/non-binding behavior;
- accepted product decisions as `PDR-*` sections in `design.md`;
- no class names, file names, or algorithms encoded as product behavior.

`acceptance-criteria.md` is the only product-behavior authority. Other prose
cites stable IDs.

Run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" \
  --phase product --repo-root "$(pwd)"
```

### Gate 1

Present behavior, negative cases, success measures, accepted PDRs, and remaining
product unknowns.

Ask: **“Approve the product contract? [yes / refine]”**

---

## Phase 2: Evidence-Backed Adversarial Design

Complete every stable section in `design.md`:

1. `Current State and Evidence`
2. `Product and Architecture Decisions`
3. `Architecture and Ownership`
4. `Failure and Partial States`
5. `Capability Challenges`
6. `Hostile Cases`
7. `Verification Strategy`

### Current-State Evidence

Support material claims with repository-relative markers:

```text
[EVIDENCE: src/path/file.py#symbol_name]
```

Use symbols, test names, schema/table/config keys, endpoints, or command names.
Do not use absolute paths. Line numbers alone are not stable anchors.

Inspect immediate producers, consumers, shared utilities, persistence,
configuration, errors, tests, runtime entrypoints, and existing contracts.

### Decisions and Native Contracts

Record accepted technical decisions as `ADR-*` sections in `design.md`.
Materialize technology-appropriate native artifacts for selected capabilities:
OpenAPI, schemas, SQL, state machines, authorization models, prompt/output
contracts, deployment/runbook contracts, or equivalent project-native forms.

Run applicable parsers and validators. Store raw output under `$RUNTIME_DIR`;
record exact commands and concise results in `Verification Strategy`.

### Capability Challenges

Read `architecture_challenges` from the policy. Create one
`### CHALLENGE-{challenge-id}` section for every common and selected-capability
challenge. Each section records the resolution and repository/native-contract
evidence. Do not write `passed` without explaining the mechanism.

### Material Flows and Hostile Cases

For every high/critical implementation requirement, create:

```markdown
### FLOW-AC-NNN
Authority:
Producer:
Boundary:
State owner:
Consumer:
Failure policy:
Proof:

### HOSTILE-AC-NNN
Invalid case:
Rejection mechanism:
Evidence: [EVIDENCE: repo/path#anchor]
```

These sections shape architecture before approval. They are not a later
self-audit.

### Manifest Scaffold

Run scaffold generation:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" \
  --phase architecture \
  --repo-root "$(pwd)" \
  --scaffold
```

The scaffold creates stable requirement/decision rows and preserves populated
v3 judgment. Fill:

- requirement type and risk;
- implementation requirement flag;
- affected surfaces;
- meaningful proof obligations;
- native artifact index and capability tags;
- accepted decisions and unresolved items.

Rerun architecture validation until it passes. Advisory normative-language and
content-budget hits are prompts for inspection, never validation failures.

### Gate 2

Present:

- consequential PDRs/ADRs and rejected alternatives;
- current-state evidence;
- authority, ownership, and changed boundaries;
- failure/partial-state behavior;
- capability challenge resolutions;
- hostile cases and rejection mechanisms;
- native validation commands/results;
- proof strategy and unresolved questions.

Ask: **“Approve these design invariants and proof strategy? [yes / refine]”**

---

## Phase 3: Implementation Handoff and Reconciliation

Create the fewest independently verifiable stories that produce a useful
sequence. Story 0 is optional and only for genuine prerequisite contracts,
configuration, prompts, schemas, or scaffolding.

Create one `file-plan-story-NN.yaml` per story:

```yaml
epic_id: "{epic-id}"
story_id: "story-01"
story_title: "Outcome-oriented title"
depends_on: []
required_contracts:
  - id: "contract-id"
    contract: "repo path plus symbol/schema/endpoint/table/validator"
    obligation: "Exact boundary behavior"
    verification: "Executable project command"
required_touchpoints:
  - id: "touchpoint-id"
    surface: "Existing entrypoint, consumer, table, config, or integration"
    obligation: "Required integration or preservation behavior"
    evidence_required: "Source, test, runtime, or state evidence"
candidate_files:
  - path: "Likely implementation path"
    reason: "Repository evidence"
    advisory: true
forbidden_changes:
  - path_or_surface: "Protected behavior or boundary"
    rule: "Change requiring renewed refinement"
proof_obligations:
  - id: "proof-id"
    acceptance_rows: ["AC-001"]
    required_evidence: "unit | integration | e2e | live_smoke | runtime_command | inspection"
    command_hint: "Concrete checker"
    success_condition: "Observable result"
```

Populate each implementation-required manifest row's `owner_story`, then
regenerate the mechanical traceability view:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" \
  --phase reconcile \
  --repo-root "$(pwd)" \
  --scaffold
```

`acceptance-traceability.yaml` derives requirement source, owner story, proof
IDs, and runtime requirement from the manifest and story plans. Do not hand-copy
those fields. Implementation later fills actual files, tests, commands,
evidence, status, and audit notes.

Reconciliation must prove:

- stable-ID, decision, source-anchor, owner, and proof coverage;
- exact review topology and budgets;
- all challenge/flow/hostile-case sections required by risk/capability;
- valid evidence paths and anchors;
- acyclic story dependencies;
- generated traceability matches canonical sources;
- no unresolved item is presented as accepted.

There is no `pre-review-audit.yaml`.

---

## Phase 4: Concurrent Cross-Provider Review

### Review Packet

Create `reviews/refine-v3-001/review-packet.yaml` with repository-relative paths:

- epic ID, profile, risk, capabilities, and assignments;
- `details.md`, acceptance criteria, `design.md`, manifest, generated
  traceability, story plans, and native contracts;
- specialist focus when assigned;
- deterministic validator command and passing result;
- deterministic guarantees listed by name;
- advisory normative-language/content-budget hits;
- native validation commands and results;
- targeted fingerprints and changed files only during targeted verification.

Do not copy full artifacts into the packet or persist absolute paths.

### Render Prompts

For every profile assignment, render `reviewer-refinement.md` under
`$RUNTIME_DIR` with provider, mission, packet path, runtime repository root,
and unique output path.

Use distinct durable output and metadata files:

```text
reviews/refine-v3-001/review-{provider}-{mission}.md
reviews/refine-v3-001/metadata-{provider}-{mission}.yaml
```

### Codex Reviewer

```bash
CODEX_MODEL_ID="${SCOPE_CODEX_MODEL_ID:-gpt-5.6-terra}"
CODEX_REASONING_EFFORT="${SCOPE_CODEX_REASONING_EFFORT:-high}"

codex exec \
  --ephemeral \
  --ignore-user-config \
  --cd "$(pwd)" \
  --model "$CODEX_MODEL_ID" \
  -c model_reasoning_effort="\"$CODEX_REASONING_EFFORT\"" \
  --sandbox read-only \
  --output-last-message "$REVIEW_OUTPUT_PATH" \
  - < "$RENDERED_REVIEW_PROMPT"
```

Record provider, model, mission, status, start/end time, duration, retry count
`0`, prompt bytes, output bytes, and repo-relative output path in the unique
metadata file.

### Claude Reviewer

```bash
"$PYTHON_CMD" "$CLAUDE_RUNNER" \
  --reviewer "$REVIEW_MISSION" \
  --model "Claude Opus (local alias)" \
  --claude-command "claude --model opus --safe-mode --strict-mcp-config --mcp-config '{}' --dangerously-skip-permissions --no-chrome" \
  --prompt-file "$RENDERED_REVIEW_PROMPT" \
  --output-file "$REVIEW_OUTPUT_PATH" \
  --metadata-file "$REVIEW_METADATA_PATH" \
  --cwd "$(pwd)" \
  --retries 0
```

### Concurrency and Failure

Launch all required assignment commands before waiting for any one result.
Capture one PID per process and wait for all. Each process owns separate prompt,
output, metadata, and log paths.

If a required provider is missing or fails, stop with that exact assignment.
Do not substitute another provider or the orchestrating context. Do not
automatically rerun a timed-out model review.

### Findings

Merge outputs into `refinement-findings.yaml`:

```yaml
schema_version: 2
epic_id: "{epic-id}"
review:
  full_review_count: 1
  targeted_verification_count: 0
  completed_assignments:
    - provider: claude
      mission: semantic_core
  outputs:
    - provider: claude
      mission: semantic_core
      path: "docs/epics/.../reviews/refine-v3-001/review-claude-semantic_core.md"
findings:
  - id: RF-001
    fingerprint: "stable-category-and-surface-key"
    severity: "blocking | major | minor"
    category: "product_decision | architecture | contract | implementation_readiness | testability | mechanical | missing_evidence | specialist"
    status: "open | corrected | verified | accepted_risk | rejected"
    evidence: "Observed defect; never overwrite with intended state"
    required_correction: "Smallest sufficient correction"
    affected_manifest_ids: ["AC-001"]
    owner: "product-owner | architect | user"
    verification_assignments:
      - provider: claude
        mission: semantic_core
    closure_test: "Independent evidence that closes the finding"
    # verification_evidence: "Required when status is verified"
    requires_user: false
```

Preserve valid findings from either provider. Deduplicate only identical root
causes with the same affected surface and closure test.

Run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" \
  --phase review --repo-root "$(pwd)"
```

### Targeted Convergence

While non-user findings remain and allowance remains:

1. correct all related canonical artifacts in one batch;
2. inspect the defect pattern across directly coupled sibling surfaces;
3. keep original finding evidence and add correction evidence;
4. mark findings `corrected`, never `verified`;
5. rerun scaffold and `--phase reconcile`;
6. create a targeted packet with changed files, fingerprints, affected IDs,
   closure tests, and `verification_assignments`;
7. rerun only those provider/mission assignments concurrently;
8. merge by fingerprint, increment `targeted_verification_count`, and validate
   `--phase review`;
9. mark `verified` only from fresh independent closure evidence.

Stop for a user decision, material redesign, provider failure, or exhausted
budget. Never silently run another full review.

---

## Final Handoff

Create `refinement-review.md`:

```markdown
# Refinement Review: {epic-id}

Decision: Approved for implementation | Incomplete

## Design and Evidence
[decisions, evidence-backed boundaries, challenges, hostile cases]

## Deterministic Reconciliation
[command, result, advisories]

## Independent Review
[assignments, outputs, findings, targeted verification]

## Residual Risks
[accepted risks or None]

## Implementation Handoff
[story order, native contracts, proof/runtime obligations]
```

### Gate 3

Present design invariants, story sequence, proof strategy, reviewer assignments,
findings/corrections, residual risks, reconciliation result, and metrics path.
For critical risk, enumerate every `accepted_risk` finding and require an
explicit decision.

Ask: **“Approve this implementation handoff? [yes / revise / hold]”**

After approval:

1. set `details.md` status to `ready-for-implementation`;
2. set `workflow_completed_at` in the profile;
3. run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" \
  --phase handoff \
  --repo-root "$(pwd)" \
  --metrics-output "$RUNTIME_DIR/metrics-final.yaml"
```

Do not claim completion if any required assignment, finding closure, native
validation, user gate, or deterministic phase was skipped.
