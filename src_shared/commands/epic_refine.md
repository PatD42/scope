---
name: epic_refine
description: Adaptively refine an epic into a validated product, architecture, and implementation handoff. Rigor scales with risk and applicable capabilities.
args: "{epic-id}"
skills: project-documentation, scope-workflows
agents: product-owner, architect
---

# epic_refine

Refine an epic until implementation can proceed without inventing product
behavior or architecture. The workflow is repository-grounded,
capability-aware, and bounded to one full independent review plus one targeted
verification round for low/medium risk or two for high/critical risk.

**Syntax:** `/epic_refine {epic-id}` or `scope:epic_refine {epic-id}`

## Outcome

An epic is ready only when:

- the user has approved intent, product behavior, consequential architecture
  decisions, and the final handoff;
- the current repository and materialized contracts support the design;
- every implementation requirement has an owning story and proof obligation;
- deterministic refinement validation passes;
- all risk-required reviewer roles completed;
- no blocking finding, user question, or unresolved manifest item remains;
- `details.md` has status `ready-for-implementation`.

The objective is decision closure and a reliable handoff, not a fixed document
count.

## Installed Sources

Use only the active checkout or worktree. Codex reads `plugins/scope/`; Claude
reads `.claude/`. Do not fall back to another checkout.

- command: `{scope-root}/commands/epic_refine.md`;
- product-owner role: `{scope-root}/agents/product-owner.md`;
- architect role: `{scope-root}/agents/architect.md`;
- documentation skill: `{scope-root}/skills/project-documentation/SKILL.md`;
- policy: `{scope-root}/config/refinement-policy.yaml`;
- validator: `{scope-root}/scripts/validate-refinement.py`;
- reviewer contract: `{scope-root}/commands/epic_refine/reviewer-refinement.md`.

Do not use the deprecated `webepic_refine` command.

## Core Rules

1. Product and architecture work stays in the current orchestrating session.
   Required independent reviews always run in fresh CLI processes.
2. Read repository instructions and the installed Scope skills/roles before
   changing epic artifacts.
3. Inspect existing source, callers, tests, schemas, configuration, and
   architecture before designing changes. CodeGraph is discovery support, not
   evidence by itself.
4. Ask the user only for product, policy, scope, security, destructive, or
   irreversible architecture decisions. Resolve file-backed mechanical issues
   autonomously.
5. Use technology-appropriate contracts. A Python `contracts.py` is optional
   and exists only when Python Protocols materially verify cross-story calls.
6. Materialize architecture-defining config, prompts, schemas, examples, SQL,
   APIs, and validators before the full independent review.
7. Keep narrative truth in Markdown and native specs. Use
   `refinement-manifest.yaml` as an index; do not copy whole requirements into
   several manually maintained matrices.
8. Do not create or consume deprecated refinement matrices as alternate sources
   of truth. This command supports only the v2 handoff defined below.
9. Run deterministic validation before model review. Do not spend reviewer calls
   on duplicate keys, missing files, broken references, or absent owners.
10. Run at most one full review. Use the risk-profiled targeted verification
    allowance to converge confirmed findings; correction work between reviewer
    calls is not itself a review round. Another full review requires a material
    design change or explicit user authorization.

## Artifact Model

### Authored sources

- `details.md`;
- `acceptance-criteria.md`;
- `pdr.md`;
- `system-context.md`;
- `architecture.md`;
- `adr.md`;
- `test-strategy.md`;
- applicable native architecture/spec/config/prompt artifacts;
- `file-plan-story-*.yaml`.

### Machine-readable handoff

- `refinement-profile.yaml`;
- `refinement-manifest.yaml`;
- `refinement-findings.yaml`;
- `acceptance-traceability.yaml`;
- `refinement-review.md`.

### Review evidence

- `reviews/refine-v2-001/pre-review-audit.yaml` records the bounded author-owned
  contract challenge. It is review evidence, not another source of product or
  architecture truth.

The profile selects capability modules from the installed policy. Do not invent
new capability identifiers without updating that policy and validator tests.

## Initialize

```bash
EPIC_ID="{epic-id}"
EPIC_DIR="$(find docs/epics -mindepth 1 -maxdepth 1 -type d \
  -iname "*${EPIC_ID}*" -print | sort | head -1)"

if [ -z "$EPIC_DIR" ]; then
  echo "Epic not found under docs/epics: ${EPIC_ID}"
  exit 1
fi

# Set this from the active platform. Never select another checkout:
#   Codex:  SCOPE_ROOT="plugins/scope"
#   Claude: SCOPE_ROOT=".claude"
SCOPE_ROOT="{active Scope installation root}"
POLICY_PATH="${SCOPE_ROOT}/config/refinement-policy.yaml"
VALIDATOR_PATH="${SCOPE_ROOT}/scripts/validate-refinement.py"
REVIEWER_PROMPT="${SCOPE_ROOT}/commands/epic_refine/reviewer-refinement.md"
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

for required_path in "$POLICY_PATH" "$VALIDATOR_PATH" "$REVIEWER_PROMPT"; do
  if [ ! -f "$required_path" ]; then
    echo "Missing installed Scope v2 asset: ${required_path}"
    exit 1
  fi
done

EPIC_SLUG="$(basename "$EPIC_DIR")"
STATE_DIR=".scope/${EPIC_SLUG}/refinement-v2"
mkdir -p "$STATE_DIR"
```

Read:

- `AGENTS.md` and any applicable nested instructions;
- `details.md` and existing epic artifacts;
- relevant product and architecture documentation;
- related previous epics, decisions, lessons, and audit findings;
- nearby source, configuration, schemas, and tests.

If `refinement-profile.yaml` already exists with `schema_version: 2`, resume
from the first phase whose validator does not pass. Otherwise start at Phase 0.
Do not infer a v2 handoff from older artifacts.

---

## Phase 0 — Intent and Refinement Profile

### Goal

Confirm why the epic exists and select the smallest sufficient refinement
profile before generating more artifacts.

### Repository grounding

Before classification:

1. Read the epic brief and product context.
2. Inspect the current implementation surfaces named by the epic.
3. For corrective work, inspect evidence of the defect and distinguish confirmed
   implementation defects from proposed quality improvements.
4. Use `rg`, direct file reads, and CodeGraph when available to locate callers,
   dependencies, schemas, configuration, and tests.
5. State assumptions and unknowns.

### Intent Alignment

Update `details.md` with:

- Why;
- Beneficiaries;
- Expected value;
- Observable success;
- In scope;
- Non-goals;
- Assumptions;
- Open intent questions.

`Open intent questions` must be `None` before Gate 0.

### Refinement Profile

Read `$POLICY_PATH` and create:

```yaml
schema_version: 2
epic_id: "{epic-id}"
architecture_scope: "none | system | backend | frontend | mixed"
risk_level: "low | medium | high | critical"
capabilities:
  - "one or more identifiers from policy, or an empty list"
classification_rationale: "Why this scope, risk, and capability set is sufficient"
review:
  roles:
    - "roles required by risk_review_policy"
  maximum_full_reviews: 1
  maximum_targeted_verifications: 1 # Use 2 for high/critical risk.
  specialist_focus: "Capability for specialist review, or none"
```

Risk guidance:

- `low`: local, reversible behavior with limited integration surface;
- `medium`: multiple components or contracts, but bounded and reversible;
- `high`: data integrity, external integration, async orchestration, security,
  runtime rollout, or model-evaluation risk;
- `critical`: destructive/irreversible operations, sensitive security/privacy,
  high-impact migration, or a failure that could invalidate the product outcome.

Do not raise risk merely because the documentation is long. Risk follows the
consequence and uncertainty of the change.

Run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" --phase profile --repo-root "$(pwd)"
```

### Gate 0 — Intent and Classification

Present a compact decision card:

- why this matters now;
- beneficiaries and observable outcome;
- in scope and non-goals;
- confirmed current-state evidence;
- architecture scope;
- selected capabilities and rationale;
- risk and resulting review roles;
- assumptions and remaining questions.

Ask: **“Approve this intent and refinement profile? [yes / refine]”**

Do not proceed without approval unless the user explicitly preapproved this
gate. Preapproval does not bypass validation.

---

## Phase 1 — Product Contract

Take the product-owner role. Preserve the approved intent and avoid introducing
implementation detail as product behavior.

### Required work

Create or update:

- `acceptance-criteria.md` with stable IDs;
- `pdr.md` with all product/policy decisions or an explicit “none”;
- product-level sections of `details.md` when clarification changes the brief.

Acceptance criteria must cover, where applicable:

- happy paths;
- negative and rejection behavior;
- error and recovery behavior;
- thresholds and success measures;
- user/operator-visible outcomes;
- runtime or one-time operational outcomes;
- allowed partial states;
- non-binding guidance versus binding obligations;
- explicitly deferred behavior.

Each criterion should define one observable promise. Assign stable IDs to
independently provable acceptance criteria, error scenarios, and E2E scenarios
(`AC-*`, `ERR-*`, and `E2E-*`). Do not encode proposed class names, file names,
or implementation algorithms as product requirements.

`acceptance-criteria.md` is the canonical requirement source. Product promises
summarized in `details.md`, PDRs, ADRs, architecture, or test strategy must cite
an existing stable requirement ID rather than create an untracked normative
requirement. Promote any independently provable promise discovered elsewhere
into `acceptance-criteria.md` before Gate 1.

### Product completeness test

Before Gate 1, answer:

> Would an architect or developer still need to decide what the product should
> do, which outcome is correct, or what failure policy applies?

If yes, interview the user and update the product artifacts.

Run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" --phase product --repo-root "$(pwd)"
```

### Gate 1 — Product Behavior

Present:

- behavior added or corrected;
- stable AC IDs and brief summaries;
- important negative/error cases;
- success measures;
- PDR decisions and alternatives;
- product unknowns: `None` or list.

Ask: **“Approve the product contract? [yes / refine]”**

---

## Phase 2 — Repository-Grounded Architecture

Take the architect role. Architecture must explain how approved behavior fits
the system and must be backed by inspected repository evidence.

### Current-state inspection

Inspect immediate callers, consumers, shared utilities, source schemas,
configuration, DDL/migrations, errors, tests, and runtime entrypoints.

For a corrective epic, add a current-to-target table to `system-context.md` or
`architecture.md`:

| Confirmed defect | Current evidence | Intended behavior | Smallest correction | Proof |
|---|---|---|---|---|

Do not redesign architecture merely because an existing behavior can be
described more elegantly. Separate:

- confirmed implementation defect;
- missing or contradictory contract;
- requested product change;
- optional quality experiment.

### Required artifacts

Create or update:

- `system-context.md`;
- `architecture.md`;
- `adr.md`;
- `test-strategy.md`;
- applicable native architecture/spec/config/prompt artifacts;
- `refinement-manifest.yaml`.

Follow the `architecture_scope` path rule from the installed documentation
skill. Backend specs belong under `docs/architecture/backend/13-specs/`,
frontend specs under `docs/architecture/frontend/13-specs/`, and system specs
under `docs/architecture/13-specs/`. Review inputs must be discovered from the
manifest; never assume the system-level path.

### Native contract selection

For every selected capability, read the policy entry and materialize at least
one tagged artifact. When `native_contract_required: true`, one tagged artifact
must use an accepted kind.

Examples:

- API: OpenAPI, CLI contract, event schema, or interface contract;
- persistence: SQL, database schema, migration or ownership contract;
- orchestration: state machine, event schema, orchestration or validator contract;
- security: authorization, security, threat, or privacy contract;
- LLM/ML: prompt, output schema, evaluation contract, trial plan, or routing contract;
- operations: deployment, runbook, smoke, or observability contract.

Use the project language and toolchain. Create a Python Protocol only when it is
the best executable contract for a real cross-story Python boundary.

### Refinement Manifest

Create:

```yaml
schema_version: 2
epic_id: "{epic-id}"
requirements:
  - id: "AC-001"
    source:
      artifact: "acceptance-criteria.md"
      anchor: "AC-001"
    summary: "One concise promise; canonical prose remains in the source"
    type: "behavior | quality | error | operational | migration | security | evidence"
    risk: "low | medium | high | critical"
    implementation_required: true
    affected_surfaces:
      - "Concrete API, command, module, table, artifact, workflow, or operator surface"
    proof_obligations:
      - "Observable assertion, negative probe, runtime evidence, or measurement"
    owner_story: null
decisions:
  - id: "PDR-001 | ADR-001"
    source:
      artifact: "pdr.md | adr.md"
      anchor: "stable heading or ID"
    summary: "Decision and why it constrains implementation"
    status: "accepted"
artifacts:
  - id: "ART-001"
    path: "repo-relative existing artifact path"
    kind: "kind accepted by policy or another descriptive kind"
    capabilities: ["selected capability identifiers"]
    authority: "canonical | derived | evidence"
open_items: []
```

Rules:

- one row per independently implementable or provable promise;
- every stable `AC-*`, `ERR-*`, and `E2E-*` ID in `acceptance-criteria.md` has a
  manifest row; stable error and E2E rows require implementation proof;
- source links point to canonical prose instead of duplicating it;
- `affected_surfaces` name actual boundaries, not generic layers;
- every implementation row has meaningful proof obligations;
- artifact paths must already exist;
- record non-implementation requirements with
  `implementation_required: false` rather than inventing a story;
- owner stories remain `null` until Phase 3.

### Architecture completeness test

Before Gate 2, answer:

> Would a developer still need to choose system boundaries, state ownership,
> interface shapes, persistence behavior, error policy, orchestration, rollout,
> or verification strategy?

If yes, complete the design or return to the user for an irreversible decision.

Run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" --phase architecture --repo-root "$(pwd)"
```

### Gate 2 — Architecture Decisions

Present:

- current-state evidence and confirmed defects;
- target architecture and changed boundaries;
- selected native contracts;
- ADRs and alternatives;
- high-risk proof strategy;
- expected operational or migration work;
- architecture unknowns: `None` or list.

Ask: **“Approve these architecture decisions and proof strategy? [yes / refine]”**

---

## Phase 3 — Complete Implementation Handoff

Produce the complete package that independent reviewers and `scope:implement`
will consume.

### Story design

Create the fewest independently verifiable stories that give a useful sequence.
Do not force 5–8 stories. Split only when one story would:

- mix unrelated outcomes;
- exceed a safe review/test boundary;
- require unavailable prerequisites;
- hide an independent rollout or migration;
- prevent incremental proof.

Story 0 is optional. Create it only for genuine architect-authored content or
scaffolding that must precede development, such as:

- authored configuration or prompts;
- native schemas/examples;
- a real cross-story interface contract;
- directory/module scaffolding;
- architecture documentation updates that must exist before code work.

### Implementation boundary plans

Create one `file-plan-story-NN.yaml` per story:

```yaml
epic_id: "{epic-id}"
story_id: "story-01"
story_title: "Outcome-oriented title"
depends_on: []
required_contracts:
  - id: "contract-id"
    contract: "repo path plus symbol, schema, endpoint, table, or validator"
    obligation: "Exact boundary behavior to satisfy"
    verification: "Project-appropriate static, test, schema, or runtime command"
required_touchpoints:
  - id: "touchpoint-id"
    surface: "Existing entrypoint, consumer, table, config, or integration"
    obligation: "Required integration or preservation behavior"
    evidence_required: "Source, test, runtime, or state evidence"
candidate_files:
  - path: "Likely implementation path"
    reason: "Repository evidence for considering it"
    advisory: true
forbidden_changes:
  - path_or_surface: "Protected contract, behavior, or boundary"
    rule: "Change requiring renewed refinement"
proof_obligations:
  - id: "proof-id"
    acceptance_rows: ["AC-001"]
    required_evidence: "unit | integration | e2e | live_smoke | runtime_command | inspection"
    command_hint: "Concrete project command or checker"
    success_condition: "Observable result"
```

`required_contracts`, `required_touchpoints`, `forbidden_changes`, and
`proof_obligations` are binding. `candidate_files` are investigation hints.

Use YAML `depends_on`; do not encode dependencies in comments.

### Ownership and traceability

Populate every implementation-required manifest row's `owner_story`.

Create `acceptance-traceability.yaml`:

```yaml
schema_version: 2
epic_id: "{epic-id}"
acceptance_items:
  - id: "AC-001"
    story: "story-01"
    requirement: "Concise behavior to prove"
    source:
      artifact: "acceptance-criteria.md"
      anchor: "AC-001"
    implementation:
      expected_files: []
      actual_files: []
    tests:
      expected_files: []
      required_assertions:
        - "Specific observable assertion"
      actual_tests: []
    runtime_evidence:
      required: false
      commands: []
      evidence: []
    status: planned
    audit_notes: ""
```

Every implementation-required manifest ID, including stable error and E2E
requirements, must have one traceability row. Add separate rows only when a
requirement needs independently owned or independently auditable proof.

### Pre-review contract challenge

The author must try to break the completed handoff before spending independent
review calls. This is one bounded correction pass, not another reviewer or user
gate. Create `reviews/refine-v2-001/pre-review-audit.yaml`, correct discovered
defects in one consolidated batch, and regenerate the audit fingerprint after
the corrections.

Create the review-evidence directory and calculate the current input
fingerprint without launching review:

```bash
mkdir -p "$EPIC_DIR/reviews/refine-v2-001"
INPUT_FINGERPRINT="$("$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" \
  --phase architecture --repo-root "$(pwd)" --print-input-fingerprint)"
```

Create the audit with this shape:

```yaml
schema_version: 1
epic_id: "{epic-id}"
input_fingerprint: "{INPUT_FINGERPRINT}"
canonical_requirement_source: acceptance-criteria.md
covered_requirement_ids: ["Every implementation-required manifest ID"]
untracked_normative_statements: []
unindexed_decision_ids: []
contract_flows:
  - id: FLOW-001
    requirement_ids: [AC-001]
    authority: "Canonical source of the rule or value"
    producer: "Component that creates the value or state"
    transport: "Request, event, artifact, or call boundary"
    state_or_persistence: "State owner, persistence surface, or reason none applies"
    consumer: "Component that relies on the value or state"
    proof: "Native constraint, negative probe, or exact proof obligation"
    status: passed
counterexamples:
  - id: ATTACK-001
    requirement_ids: [AC-001]
    invalid_case: "A superficially valid implementation or state that violates intent"
    rejection_mechanism: "Exact schema, constraint, ownership rule, or fail-closed behavior"
    evidence: "Artifact section plus executable or inspectable probe"
    status: passed
capability_checks:
  - capability: common
    check_id: authority-and-ownership
    evidence: "Artifact-backed result of the policy challenge"
    status: passed
validation_commands:
  - command: "Exact command that was actually run"
    result: passed
    evidence: "Pass count, parser result, or output artifact"
unresolved_items: []
```

Challenge rules:

1. Inspect all authored sources for normative promises without stable IDs.
   Promote independently provable promises to `acceptance-criteria.md` or remove
   their normative wording.
2. Trace every high/critical implementation requirement through
   `authority -> producer -> transport -> state -> consumer -> proof`.
3. Construct at least one hostile counterexample for every high/critical
   implementation requirement and identify the exact rejection mechanism.
4. Record every common and selected-capability challenge from
   `pre_review_challenges` in the policy.
5. Run applicable native schema, configuration, API, SQL, interface, fixture,
   and dry-run validation. Never claim execution that was skipped.

The author challenge is not independent closure evidence. If it finds a
decision-gated issue, return to the owning user gate. Resolve all other defects
before review.

Run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" --phase pre_review --repo-root "$(pwd)"
```

Do not launch independent review until this passes.

---

## Phase 4 — Risk-Appropriate Review and Readiness

### Review packet

Create one full-review directory:

```text
docs/epics/{epic-dir}/reviews/refine-v2-001/
```

Create `review-packet.yaml` containing:

- epic ID;
- refinement profile and risk;
- assigned reviewer roles;
- selected capabilities and specialist focus;
- the base authored handoff artifacts (`details.md`, acceptance criteria, PDR,
  system context, architecture, ADR, and test strategy);
- all canonical artifact paths from the manifest;
- boundary-plan and traceability paths;
- the pre-review audit path and its input fingerprint;
- requirement/decision IDs;
- deterministic validator command and passing result;
- prior findings, when running the targeted verification pass.

Do not copy full artifacts into the packet. Reviewers read cited files.

### Reviewer roles

Read required roles from the approved profile and policy:

- `architecture_coherence`: requirements, decisions, boundaries, native specs,
  producer/consumer compatibility, state ownership, and contradictions;
- `implementation_readiness`: story boundaries, dependencies, contract
  usability, proof obligations, negative cases, rollout, and implementer
  invention risk;
- `capability_specialist`: only the selected high-risk capability and its
  sibling surfaces.

One output cannot satisfy multiple required roles. Render each role prompt under
`tmp_debug/scope-refine/{epic-id}/`; never persist an absolute repository path
in `review-packet.yaml` or another durable epic artifact.

For Codex orchestration, every role uses a fresh process with these exact
defaults:

```bash
CODEX_MODEL_ID="${SCOPE_CODEX_MODEL_ID:-gpt-5.6-terra}"
CODEX_REASONING_EFFORT="${SCOPE_CODEX_REASONING_EFFORT:-high}"

codex exec \
  --cd "$(pwd)" \
  --model "$CODEX_MODEL_ID" \
  -c model_reasoning_effort="\"$CODEX_REASONING_EFFORT\"" \
  --sandbox read-only \
  --output-last-message "$REVIEW_OUTPUT_PATH" \
  - < "$RENDERED_REVIEW_PROMPT"
```

The model ID and reasoning effort are separate values. Never pass
`gpt-5.6-terra-high` as the model ID.

For Claude orchestration, every role uses a fresh Opus process through
`scope-reviewer-claude-pexpect.py` with
`--dangerously-skip-permissions`:

```bash
"$PYTHON_CMD" "$CLAUDE_REVIEWER_RUNNER" \
  --reviewer "$REVIEW_ROLE" \
  --model "Claude Opus (local alias)" \
  --claude-command "claude --model opus --dangerously-skip-permissions --no-chrome" \
  --prompt-file "$RENDERED_REVIEW_PROMPT" \
  --output-file "$REVIEW_OUTPUT_PATH" \
  --metadata-file "$REVIEW_METADATA_PATH" \
  --cwd "$(pwd)"
```

Store its PTY log under `tmp_debug/scope-reviewer-logs/`, not in the epic
directory.

Render `reviewer-refinement.md` with the role, packet path, runtime repository
root, reviewer identity, and output path. Reviewers are read-only and must use
file-backed evidence. If the active platform's reviewer CLI or required runtime
is unavailable, stop with the missing role; do not silently substitute the
polluted orchestrating context.

### Findings ledger

Merge and deduplicate outputs into `refinement-findings.yaml`:

```yaml
schema_version: 1
epic_id: "{epic-id}"
review:
  full_review_count: 1
  targeted_verification_count: 0
  completed_roles:
    - "roles required by the profile"
  outputs:
    - "repo-relative reviewer output paths"
findings:
  - id: "RF-001"
    fingerprint: "stable-category-and-surface-key"
    severity: "blocking | major | minor"
    category: "policy category"
    status: "open | corrected | verified | accepted_risk | rejected"
    evidence: "Current specific file/section mismatch; never overwrite with intended state"
    required_correction: "Smallest sufficient correction from the reviewer"
    affected_manifest_ids: ["AC-001"]
    owner: "product-owner | architect | user"
    verification_roles: ["architecture_coherence"]
    closure_test: "Deterministic or targeted review check"
    # correction_evidence: "Add only when status becomes corrected or verified"
    # verification_evidence: "Add only when status becomes verified"
    requires_user: false
```

Classification:

- `blocking`: implementation would need to invent product/architecture, a
  required contract is contradictory or impossible, a high-risk proof path is
  missing, or the handoff could implement the wrong outcome;
- `major`: significant readiness or testability weakness that should be fixed
  before implementation but does not invalidate the design;
- `minor`: optional clarity or polish.

Reject hypothetical findings without concrete evidence. Preserve minority
findings when evidence is valid; do not decide by provider vote.

### Bounded correction convergence

`targeted_verification_count` records independent targeted verification rounds.
Editing artifacts and running deterministic checks do not increment it.

After merging the full review, run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" --phase review --repo-root "$(pwd)"
```

The review phase validates reviewer coverage, finding structure, fingerprints,
and counters while allowing `open` and `corrected` findings. It does not permit
handoff.

While non-user findings remain and targeted verification allowance remains:

1. correct every related artifact in one consolidated batch;
2. expand each defect pattern across directly coupled sibling surfaces;
3. keep `evidence` as the observed defect and record the change in
   `correction_evidence`;
4. mark the finding `corrected`, never `verified`;
5. update affected pre-review flows, counterexamples, capability checks,
   validation evidence, and input fingerprint, then rerun
   `validate-refinement.py --phase pre_review`;
6. create `targeted-verification-NNN/` containing only changed files, non-terminal
   findings, affected manifest IDs, their `verification_roles`, and sibling
   surfaces checked;
7. rerun only the verification roles named by those findings;
8. merge results by stable fingerprint, increment
   `targeted_verification_count`, and rerun `--phase review`;
9. mark a finding `verified` only when its closure test passes and record
   `verification_evidence`.

If targeted verification leaves the same agent-owned fingerprint open and the
allowance remains, correct it and continue without asking the user. Do not run a
second full review merely because corrections occurred.

Stop only when:

- a finding requires a product, policy, security, destructive, or irreversible
  user decision;
- the architecture materially changes enough to invalidate the full review;
- targeted verification allowance is exhausted with a non-terminal finding;
- another full review would exceed policy.

When allowance is exhausted, report a bounded incomplete result with the exact
remaining fingerprints. Never mark the epic ready. Additional targeted or full
review requires explicit user authorization.

### Refinement review summary

Create `refinement-review.md` with:

```markdown
# Refinement Review: {epic-id}

## Decision
Decision: Ready for user approval

## Profile and Coverage
[risk, capabilities, completed roles, reviewer outputs]

## Deterministic Validation
[command and result]

## Findings and Corrections
[stable IDs, status, evidence, closure]

## Residual Risks
[accepted risks or None]

## Implementation Handoff
[stories, dependency order, native contracts, proof obligations]
```

### Gate 3 — Final Handoff

Present one compact decision card:

- approved intent and product outcome;
- architecture decisions and native contract authorities;
- stories and dependency order;
- high-risk proof and operational obligations;
- completed reviewer roles;
- findings corrected or residual risks accepted;
- deterministic validation result;
- remaining product/architecture questions: `None`.

Ask: **“Approve this epic for implementation? [yes / refine]”**

For critical risk, explicitly ask the user to accept or reject every residual
risk. Do not infer acceptance.

After approval:

1. set the decision line in `refinement-review.md` to exactly:
   `Decision: Approved for implementation`;
2. update `details.md` frontmatter to
   `status: ready-for-implementation`;
3. ensure `refinement-findings.yaml` has no `open` or `corrected` finding and no
   unresolved user-required finding;
4. run:

```bash
"$PYTHON_CMD" "$VALIDATOR_PATH" "$EPIC_DIR" --phase handoff --repo-root "$(pwd)"
```

If final validation fails, revoke ready status, fix the mechanical failure, and
rerun validation. Do not silently approve.

## Completion Output

Report:

- epic ID and status;
- approved profile, risk, and capabilities;
- canonical artifact paths;
- native contract authorities;
- pre-review challenge fingerprint and validation commands;
- story count and dependency order;
- review roles and correction count;
- residual risks;
- final validator command and result;
- next command: `scope:implement {epic-id}`.

Do not claim completion if any phase, reviewer role, finding closure, gate, or
validation was skipped.

## Compaction Recovery

State lives in artifacts:

- valid profile → Phase 0 complete;
- valid product phase → Phase 1 complete;
- valid architecture phase → Phase 2 complete;
- valid pre-review phase, including a current-fingerprint contract challenge →
  Phase 3 complete;
- valid review phase plus non-terminal findings → resume bounded correction
  convergence;
- valid review phase with only terminal findings → prepare Gate 3;
- handoff validator passes → ready for implementation.

On resume, rerun the validator for the latest expected phase and continue from
the first failure. Do not infer completion from file existence alone.
