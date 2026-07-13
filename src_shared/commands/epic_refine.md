---
name: epic_refine
description: Contract-first epic refinement. Produces executable Python contracts alongside implementation boundary plans. Output feeds /implement or /implement_tdd.
args: "{epic-id}"
skills: project-documentation, session-id-finder, agent-summary
agents: product-owner, architect
---

# /epic_refine

Contract-first epic refinement with a gated Phase 0 intent alignment plus 4 delivery approval gates. Produces executable Python Protocol contracts that agents verify via mypy — not just prose descriptions.

**Syntax:** `/epic_refine {epic-id}`

## Why Contract-First

The previous approach produced tactical file lists with method signatures in YAML prose. Agents implemented against these descriptions, but nothing machine-verified that components could actually call each other. Result: 81 tests pass, 5 critical integration failures hidden by mocks.

**Contract-first** means:
- Story 0 creates `contracts.py` with Python Protocol classes
- Method signatures are executable code, not YAML descriptions
- `mypy --strict` catches interface mismatches statically after each story
- Implementation boundary plans reference contracts as source of truth for cross-story calls

**Key insight:** Agents need machine-verifiable contracts, not human-readable descriptions. TDD with mocks tests behavior in isolation; contracts + static analysis verifies integration mechanically.

## Epic Artifact Rules

These rules are mandatory for every refined epic:

- `contracts.py` belongs in the source package for the epic's implementation, never under `docs/epics/...`.
- The epic documentation folder may contain only `.md` and `.yaml` files.
- Required epic artifacts:
  - `details.md`
  - `acceptance-criteria.md`
  - `acceptance-traceability.yaml`
  - `system-context.md`
  - `architecture.md`
  - `adr.md`
  - `pdr.md`
  - `test-strategy.md`
  - `refinement-inconsistencies.yaml`
  - `architecture-claims.yaml`
  - `architecture-contract-self-check.yaml`
- `details.md` must use YAML frontmatter with at least `epic_id`, `title`, and `status`.
- `details.md` must include an approved `## Intent Alignment` section before Phase 1 begins.
- `adr.md` must use the global ADR numbering sequence and include `Date`, `Status`, `Scope`, `Epic`, `Context`, `Decision`, `Alternatives Considered`, and `Consequences` for every ADR entry.

Do not pass a phase if these artifact rules are not satisfied by the work completed so far.

## Artifact Generation Discipline

Refinement artifacts must be generated transactionally. Do not write a large set
of documents and defer consistency checks to Phase 3.5 reviewers.

Before writing each artifact batch, state the artifact contract:

- source inputs that must be reflected
- required sections, IDs, rows, or fields
- required cross-links to ACs, PDRs, ADRs, specs, tests, or implementation boundary plans
- validation checks that will be run immediately after writing
- known assumptions and unknowns

After writing each artifact batch, validate it before moving on:

- Markdown required sections exist and no placeholders remain
- YAML and JSON parse
- OpenAPI specs parse when created or changed
- SQL/spec files exist for persistence or migration promises
- required IDs are stable and unique
- evidence paths referenced by matrices or plans exist
- every new artifact lists what changed relative to previously approved
  artifacts and which AC/PDR/ADR rows it satisfies

Maintain `docs/epics/{epic-dir}/refinement-inconsistencies.yaml` throughout the
command. This is the working ledger for unclear issues, mismatches, and deferred
questions discovered while producing artifacts.

Required shape:

```yaml
epic_id: "{epic-id}"
items:
  - id: "RI-001"
    discovered_phase: "phase_1 | phase_2 | phase_3 | phase_3_5 | phase_4"
    owner_phase: "phase_0 | phase_1 | phase_2 | phase_3 | phase_4"
    issue: "Concrete ambiguity or inconsistency"
    affects: ["intent", "business", "architecture", "api", "schema", "sql", "tests", "implementation_boundary_plan"]
    status: "open | resolved | user_question"
    resolution: ""
```

No approval gate can pass while the ledger has `open` or `user_question` items.
If the item can be resolved from already approved context, resolve it before the
gate. If it requires user input, ask the user and update the owning phase
artifact before continuing.

## Workflow Overview

```
┌─────────────────────────────────────────────────────────┐
│ Phase 0: Intent alignment (why_understanding)           │
│ - Explain the epic's why in concrete product terms       │
│ - Interview user until intent, value, and success are    │
│   understood                                             │
│ - Record Intent Alignment in details.md                  │
│ ──────────────────────────────────────────────────────  │
│ → USER APPROVAL GATE #0                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Take role of product-owner (epic_validation)   │
│ - Load epic, ask clarifying questions                   │
│ - Write acceptance criteria + error scenarios           │
│ - Define e2e test scenarios                             │
│ ──────────────────────────────────────────────────────  │
│ → USER APPROVAL GATE #1                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 2: Take role of architect (system_context +       │
│          architecture_design)                           │
│ - Analyze system context, patterns, constraints         │
│ - Design architecture + ADRs + test strategy            │
│ ──────────────────────────────────────────────────────  │
│ → USER APPROVAL GATE #2                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 3: Continue as architect (spec_generation)        │
│ - Generate specs in docs/architecture/13-specs/          │
│ - Phase 3.5: Review architecture/spec coherence         │
│ - Fix strategic gaps before tactical story planning     │
│ ──────────────────────────────────────────────────────  │
│ → USER APPROVAL GATE #3                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Continue as architect (story_breakdown +       │
│          implementation_boundary_plan + contracts)      │
│ - Break epic into implementable user stories            │
│ - Create contracts.py with Protocol classes             │
│ - Create implementation boundary plans with proof rules │
│ ──────────────────────────────────────────────────────  │
│ → USER APPROVAL GATE #4                                 │
│ → Mark epic "ready-for-implementation"                  │
└─────────────────────────────────────────────────────────┘
```

## Phase Handoff Rule

Do not pass a phase by "good enough" intuition. A phase passes only when downstream roles can execute without inventing missing decisions:
- Phase 0 is not complete until the orchestrator can explain the epic's underlying intent, user/business value, target outcome, and non-goals in a way the user confirms is correct.
- If the orchestrator cannot explain why the epic exists, who benefits, what outcome matters, or what would make the epic successful, it must interview the user before Phase 1.
- Phase 1 is not complete until the Product Owner has specified the business behavior in enough detail that neither the Architect nor the Developer would need to make product, policy, scope, workflow, or acceptance decisions during later phases.
- If the Architect would need to choose what the business wants, or the Developer would need to choose what behavior is correct, then the business requirements are incomplete.
- In that case, the Product Owner must interview the user in a semi-structured approach to complete the business requirements in enough details before proceeding.
- Phases 2-4 are not complete until the architecture is detailed enough that the Developer would not need to make architecture decisions during implementation.
- If the Developer must decide how the system should be designed, refinement was incomplete and must return to the Architect before implementation begins.
- At every phase boundary, explicitly list unknowns or unclear issues found during that phase. If any unknown affects product intent, business behavior, architecture, acceptance, testing, security, rollout, or implementation ownership, ask the user or return to the correct prior phase before continuing.

---

## Execution

### Step 0: Initialize

```bash
# Extract epic-id from argument
EPIC_ID="{epic-id}"

# Determine epic directory (filesafe version of epic title)
EPIC_DIR=$(ls docs/epics/ | grep -i "^${EPIC_ID}" | head -1)
if [ -z "$EPIC_DIR" ]; then
  echo "Epic not found in docs/epics/. Create epic first with details.md"
  exit 1
fi

# Create .scope directory for this epic
mkdir -p ".scope/${EPIC_DIR}"
SUMMARIES_FILE=".scope/${EPIC_DIR}/refine_summaries.jsonl"
INCONSISTENCIES_FILE="docs/epics/${EPIC_DIR}/refinement-inconsistencies.yaml"

# Get session ID for cost tracking
SESSION_ID=$(skill session-id-finder)

# Write baseline entry
echo '{"agent":"baseline","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' > "$SUMMARIES_FILE"

# Create the working inconsistencies ledger if it does not already exist
if [ ! -f "$INCONSISTENCIES_FILE" ]; then
  cat > "$INCONSISTENCIES_FILE" <<EOF
epic_id: "${EPIC_ID}"
items: []
EOF
fi
```

### Step 1: Load Epic Context

1. Read `docs/epics/{epic-dir}/details.md` to understand epic
2. Read product documentation:
   - `docs/product/strategy.md` - strategic context
   - `docs/product/definition.md` - use cases, capabilities
   - `docs/product/reference/terminology.md` - domain terms
3. Announce: "Starting epic refinement for {epic-id}: {epic-title}"

---

## Phase 0: Intent Alignment (why_understanding)

**Instruction:** Before writing or refining acceptance criteria, convince the user that you understand why the epic exists.

**Goal:** Align on intent before Scope turns the epic into requirements, architecture, specs, and implementation boundary plans.

The orchestrator must not infer the "why" from implementation details alone. Read `details.md` and product context, then explain the epic in plain product terms:

- why this epic matters now
- who benefits and what job/outcome they need
- what product, operational, commercial, community, or risk-reduction value is expected
- what success looks like after implementation
- what is explicitly not the goal
- what assumptions or unknowns remain

If any of those points are weak, vague, or inferred, interview the user before Phase 1. Use a semi-structured approach: ask concise questions about motivation, users, success, non-goals, constraints, risks, and tradeoffs. Continue until there are no intent-level unknowns.

**Key deliverable:**

Update `docs/epics/{epic-dir}/details.md` with an `## Intent Alignment` section containing:

- `Why`
- `Beneficiaries`
- `Expected value`
- `Success outcome`
- `Non-goals`
- `Assumptions`
- `Open intent questions` (must be `None` before Gate #0 passes)

### Phase 0 Checklist

Present to the user in the console before asking for Gate #0 approval. Do not
only write this interpretation to `details.md`; the user must see your
interpretation in the chat/console so they can correct it before Phase 1.

```
Phase 0: Intent Alignment - Why Understanding

My interpretation of the epic intent:
- Why this matters now: [plain-language explanation]
- Who benefits: [primary users/stakeholders]
- Outcome they need: [job/outcome]
- Expected value: [product / operational / commercial / community / risk-reduction value]
- Observable success: [what will be true after implementation]
- Non-goals: [what this epic is not trying to do]
- Assumptions I am making: [list or None]

✅ Why
   My understanding: [concise explanation]
   User/business/community value: [clear / needs clarification]

✅ Beneficiaries
   Primary users or stakeholders: [list]
   Job/outcome they need: [clear / needs clarification]

✅ Success Outcome
   Observable success: [clear / needs clarification]
   Non-goals: [listed / needs clarification]

✅ Unknowns
   Intent-level unknowns: [None / list]
   Questions asked and answered: [N]
   refinement-inconsistencies.yaml open items: [0 / list]

Is this understanding of why the epic exists correct? [yes / refine]
```

Gate #0 approval is invalid if the console message says only that validation
passed, points the user to a file, or asks "is this intent alignment correct"
without first showing the interpreted intent in the console.

### Approval Gate #0

**If user approves**: Write summary entry and proceed to Phase 1

```bash
echo '{"agent":"orchestrator","session_id":"'"$SESSION_ID"'","phase":"why_understanding","status":"success","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' >> "$SUMMARIES_FILE"
```

**If user wants refinement**: Ask targeted questions, update `details.md`, and re-present the checklist.

Do not proceed to Phase 1 while `Open intent questions` is anything other than `None`.

---

## Phase 1: Product Owner (epic_validation)

**Instruction:** Take the role of `product-owner` agent for the `epic_validation` phase.

**Goal:** Validate epic and define business requirements.

Start from the approved `details.md` Intent Alignment section. Acceptance criteria must preserve the approved why; do not introduce behavior that changes the intent, beneficiaries, expected value, success outcome, or non-goals without asking the user.

**Phase context to pass:**
```
epic_id: {epic-id}
phase: epic_validation
agent_summaries: .scope/{epic-dir}/agent_summaries.jsonl
```

**Key deliverables:**
- Acceptance criteria in Given/When/Then format
- Error scenarios (for docs/architecture/13-specs/errors/ generation)
- E2E test scenarios
- Product decisions captured in `pdr.md`
- Written to:
  - `docs/epics/{epic-dir}/acceptance-criteria.md`
  - `docs/epics/{epic-dir}/pdr.md`

**Phase 1 completeness rule:** If the Architect or Developer would still need to make business, policy, scope, workflow, or acceptance decisions, Phase 1 is not complete. The Product Owner must stop and interview the user before moving to Phase 2.

If Phase 1 exposes an intent mismatch or a new unknown about why the epic exists, return to Phase 0 and ask the user before continuing.

### Phase 1 Checklist

Present to user:

```
Phase 1: Product Owner - Epic Validation

✅ Epic Details
   Intent alignment preserved: [Yes / No]
   Business value: [Clear / Needs clarification]
   User stories: [N stories defined]
   Scope: [Well-bounded / Needs refinement]

✅ Acceptance Criteria
   Happy path scenarios: [N scenarios]
   Edge cases: [N cases]
   Error scenarios: [N scenarios]

✅ Test Scenarios
   E2E scenarios: [N scenarios defined]

✅ Product Decisions
   pdr.md present: [Yes / No]
   Decisions captured or explicitly stated as none: [Yes / No]

✅ Unknowns
   Product/business unknowns: [None / list]
   User questions needed before architecture: [No / list]
   refinement-inconsistencies.yaml open items: [0 / list]

Ready to proceed to architecture? [yes / refine]
```

### Approval Gate #1

**If user approves**: Write summary entry and proceed to Phase 2

```bash
echo '{"agent":"product-owner","session_id":"'"$SESSION_ID"'","phase":"epic_validation","status":"success","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' >> "$SUMMARIES_FILE"
```

**If user wants refinement**: Address concerns, update artifacts, re-present checklist

---

## Phase 2: Architect (system_context + architecture_design)

**Instruction:** Take the role of `architect` agent for the `system_context` and `architecture_design` phases.

**Goal:** Analyze system context and design architecture.

At the start of Phase 2, restate any product or business unknowns. If any remain, return to Phase 1 before designing architecture. If architecture work reveals a new product/intent unknown, stop and ask the user rather than encoding an assumption.

**Phase context to pass:**
```
epic_id: {epic-id}
phase: system_context  # then architecture_design
agent_summaries: .scope/{epic-dir}/agent_summaries.jsonl
```

**Key deliverables:**
- System context analysis (integration points, patterns, constraints)
- Architecture design (components, data model, API contracts)
- ADRs for key technology decisions using the global ADR sequence
- Test strategy (boundaries, test data, mocking)
- **Documentation update plan** — list of product-level architecture docs that must be
  updated when this epic is implemented, with specific changes needed. This plan is
  executed in Story 0 (scaffolding) by the architect, NOT by the developer.
- Source placement rule for `contracts.py` documented in the implementation boundary plans and epic architecture:
  it must live in the source package, never in `docs/epics/...`.
- Written to:
  - `docs/epics/{epic-dir}/system-context.md`
  - `docs/epics/{epic-dir}/architecture.md`
  - `docs/epics/{epic-dir}/adr.md`
  - `docs/epics/{epic-dir}/test-strategy.md`

**Phase 2-4 completeness rule:** If the Developer would still need to choose interfaces, component boundaries, data model structure, orchestration flow, integration patterns, error strategy, or other architecture decisions, refinement is not complete and must return to the Architect before implementation.

### Phase 2 Checklist

Present to user:

```
Phase 2: Architect - System Context & Architecture

✅ System Context
   Approved why preserved: [Yes / No]
   Integration points: [N components identified]
   Patterns to follow: [N patterns documented]
   Inherited constraints: [N constraints identified]
   Feasibility: [Feasible / Feasible with constraints / Not feasible]

✅ Architecture Design
   Components: [N components designed]
   Data model: [Documented / Needs work]
   API contracts: [N endpoints outlined]

✅ ADRs
   Decisions documented: [N ADRs created]
   Key decisions: [list]

✅ Test Strategy
   Test boundaries: [Defined / Needs work]
   Test data approach: [Defined / Needs work]

✅ Documentation Update Plan (for Story 0)
   Docs to update: [list files that need changes]
   Docs to create: [list new files, e.g., backend/13-specs/database/sql/{epic-id}.sql]
   ADR roll-up needed: [Yes / No]

✅ Unknowns
   Architecture unknowns: [None / list]
   Product questions discovered during architecture: [None / list]
   refinement-inconsistencies.yaml open items: [0 / list]

Ready to proceed to spec generation? [yes / refine]
```

### Approval Gate #2

**If user approves**: Write summary entry and proceed to Phase 3

```bash
echo '{"agent":"architect","session_id":"'"$SESSION_ID"'","phase":"architecture_design","status":"success","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' >> "$SUMMARIES_FILE"
```

**If user wants refinement**: Address concerns, update artifacts, re-present checklist

---

## Phase 3: Architect (spec_generation)

**Instruction:** Continue as `architect` agent for the `spec_generation` phase. Create the applicable `13-specs/` subdirectories if they don't exist yet.

**Goal:** Generate technical specifications in `docs/architecture/13-specs/`, `docs/architecture/backend/13-specs/`, or `docs/architecture/frontend/13-specs/` depending on ownership. These are the canonical locations — all specs live under an applicable `13-specs/`, not in the project root and not in `14-schema`.

If spec generation reveals an unclear field, endpoint, status, error, persistence rule, ownership rule, or behavior, do not guess. Return to Phase 1 for product ambiguity or Phase 2 for architecture ambiguity before writing inconsistent specs.

**Phase context to pass:**
```
epic_id: {epic-id}
phase: spec_generation
agent_summaries: .scope/{epic-dir}/agent_summaries.jsonl
specs_dir: docs/architecture/{13-specs|backend/13-specs|frontend/13-specs}
```

**Key deliverables:**
- `docs/epics/{epic-dir}/architecture-claims.yaml`
- API contracts in the applicable `13-specs/api/` (OpenAPI 3.0.3)
- Domain schemas in the applicable `13-specs/schemas/domain/` (JSON Schema)
- Database specs in the applicable `13-specs/database/`
- Error codes in the applicable `13-specs/errors/by-domain/`
- Updated error taxonomy in the applicable `13-specs/errors/taxonomy.yaml`
- `docs/epics/{epic-dir}/architecture-contract-self-check.yaml`

### Phase 3 Claims Ledger

Before generating or editing specs, create
`docs/epics/{epic-dir}/architecture-claims.yaml`.

The claims ledger is the source input for contract generation. The architect
must not generate OpenAPI, JSON Schema, SQL, or error specs directly from prose
without first extracting the enforceable claims.

Required shape:

```yaml
epic_id: "{epic-id}"
generated_at: "{ISO-8601}"
status: "pass | fail"
claims:
  - id: "AC7-FIDELITY-PARTITIONS"
    source:
      artifact: "acceptance-criteria.md"
      anchor: "AC7"
    claim: "Fidelity gates must validate held-out, boundary, near-boundary, and stress rows."
    owner_phase: "phase_3"
    keywords: ["must", "all"]
    affected_surfaces:
      api: []
      json_schema: []
      sql: []
      error_contract: []
      test_strategy: []
      producer_consumer: []
      cross_surface_patterns: ["conditional_fields", "generated_report"]
    enforcement_expected:
      type: "required_field | enum | exact_cardinality | conditional | invariant | no-ddl | explicit_no_contract_needed"
      rationale: "Why this claim needs this enforcement shape"
    status: "pass | fail | user_question | not_applicable"
    notes: ""
```

Compact example row:

```yaml
claims:
  - id: "AC3-EXPORT-REJECTS-PARTIAL"
    source:
      artifact: "acceptance-criteria.md"
      anchor: "AC3"
    claim: "Export must fail closed when any required invoice line is missing."
    owner_phase: "phase_3"
    keywords: ["must", "fail closed", "required"]
    affected_surfaces:
      api: ["POST /exports"]
      json_schema: ["ExportRequest", "ExportResult"]
      sql: ["export_jobs"]
      error_contract: ["EXPORT_REQUIRED_LINE_MISSING"]
      test_strategy: ["AC3 fail-closed export test"]
      producer_consumer: ["export worker -> export result"]
      cross_surface_patterns: ["fail_closed", "generated_report"]
    enforcement_expected:
      type: "invariant"
      rationale: "A successful export with missing required lines would violate AC3."
    status: "pass"
    notes: ""
```

Create one claim row for every accepted AC/PDR/ADR rule that contains or implies
required, exact, conditional, fail-closed, ownership, idempotency, resumability,
threshold, output-completeness, split-runtime, operator-visible, or generated
artifact behavior. If the correct enforcement cannot be determined from approved
requirements, mark the row `user_question` and return to Phase 1 or Phase 2
before writing specs. Keep this ledger compact: one row per enforceable promise,
not one row per implementation detail.

### Phase 3 Contract Self-Gate

Before telling the user Phase 3 is ready for strategic architecture review, the
architect must prove that the generated contracts enforce the business and
architecture rules. Evidence links are not enough. A contract that merely
mentions a behavior but does not enforce it is incomplete.

Create `docs/epics/{epic-dir}/architecture-contract-self-check.yaml` from:

- `architecture-claims.yaml`
- every acceptance criterion
- every accepted PDR/ADR decision
- every generated API/OpenAPI path and payload
- every generated JSON/domain schema
- every generated SQL/no-DDL spec
- every generated error contract
- the test strategy

Required shape:

```yaml
epic_id: "{epic-id}"
generated_at: "{ISO-8601}"
status: "pass | fail"
contract_inventory:
  architecture_entities: []
  api_operations: []
  generated_schemas: []
  generated_reports_or_artifacts: []
  commands_or_scripts: []
  persistence_surfaces: []
  error_codes: []
producer_consumer_compatibility:
  - id: "API-COMPARE-1F"
    producer: "script, endpoint, worker, command, or service that creates the output"
    consumer: "API response, report, dashboard, operator, downstream story, or test"
    required_output: "Schema/report/artifact that must be produced"
    producer_can_create_required_fields: "yes | no | user_question"
    split_runtime_or_environment_constraint: "none | described constraint"
    status: "pass | fail | user_question | not_applicable"
cross_surface_patterns:
  - pattern: "resumability | idempotency | exact coverage | fail_closed | conditional_fields | split_runtime | generated_report"
    surfaces_checked: []
    missing_surfaces: []
    status: "pass | fail | user_question | not_applicable"
claims:
  - id: "AC7-FIDELITY-PARTITIONS"
    source:
      artifact: "acceptance-criteria.md"
      anchor: "AC7"
    claim: "Fidelity gates must validate held-out, boundary, near-boundary, and stress rows."
    keywords: ["must", "all", "fail-closed"]
    contract_surfaces:
      api: []
      json_schema: ["docs/architecture/13-specs/schemas/domain/{epic-id}-*.json#/definitions/FidelityGateResult"]
      sql: []
      error_contract: []
      test_strategy: ["docs/epics/{epic-dir}/test-strategy.md#AC7"]
    enforcement:
      type: "required_field | enum | exact_cardinality | conditional | invariant | no-ddl | explicit_no_contract_needed"
      mechanism: "Concrete OpenAPI/JSON Schema/SQL/error/test mechanism that enforces the claim"
      negative_case: "A bad payload/state that should be rejected or fail"
    status: "pass | fail | user_question | not_applicable"
    notes: ""
```

Compact example row:

```yaml
producer_consumer_compatibility:
  - id: "PC-EXPORT-RESULT"
    producer: "export worker"
    consumer: "POST /exports response and operator export report"
    required_output: "ExportResult with job_id, rejected_rows, artifact_path, and failure reasons"
    producer_can_create_required_fields: "yes"
    split_runtime_or_environment_constraint: "none"
    status: "pass"
cross_surface_patterns:
  - pattern: "fail_closed"
    surfaces_checked: ["POST /exports", "ExportResult", "export_jobs", "EXPORT_REQUIRED_LINE_MISSING", "test-strategy AC3"]
    missing_surfaces: []
    status: "pass"
claims:
  - id: "AC3-EXPORT-REJECTS-PARTIAL"
    source:
      artifact: "acceptance-criteria.md"
      anchor: "AC3"
    claim: "Export must fail closed when any required invoice line is missing."
    keywords: ["must", "fail closed", "required"]
    contract_surfaces:
      api: ["docs/architecture/backend/13-specs/api/{epic-id}-exports.openapi.yaml#/paths/~1exports/post"]
      json_schema: ["docs/architecture/backend/13-specs/schemas/domain/{epic-id}-export.schema.json#/definitions/ExportResult"]
      sql: ["docs/architecture/backend/13-specs/database/{epic-id}-exports.sql#export_jobs"]
      error_contract: ["docs/architecture/backend/13-specs/errors/by-domain/exports.yaml#EXPORT_REQUIRED_LINE_MISSING"]
      test_strategy: ["docs/epics/{epic-dir}/test-strategy.md#AC3"]
    enforcement:
      type: "invariant"
      mechanism: "OpenAPI requires failure status and reasons; SQL records rejected rows; error contract defines missing-line failure."
      negative_case: "Request with one invoice missing a required line returns EXPORT_REQUIRED_LINE_MISSING and no success artifact."
    status: "pass"
    notes: ""
```

The self-gate must include rows for every claim containing or implying:

- `must`, `only`, `never`, `all`, `every`, `exact`, `at least`, `no more than`
- thresholds, floors, row counts, component counts, timing limits, or coverage rules
- fail-closed behavior, rejection behavior, blocked states, or required reasons
- optional vs required fields
- conditional behavior such as "if X then require Y"
- idempotency, resumability, retries, supersession, overwrite, ordering, or ownership
- generated reports, manifests, metrics, artifacts, exports, or operator-visible outputs
- split runtime/environment behavior where one command cannot produce all evidence

The self-gate must also inventory and check structural consistency:

- Every data model/entity/report/artifact named in `architecture.md` has a
  generated schema or an explicit reason no schema is needed.
- Every generated schema/report/artifact has a producer and a consumer.
- Every API response schema can actually be produced by the endpoint, script,
  worker, or command named in the architecture.
- Aggregate vs per-item behavior is explicit. If an operation can cover many
  components, rows, records, files, attempts, or jobs, the request and response
  contract must say whether it returns one result, a list, or a keyed map.
- Aggregate pass/fail semantics are explicit. If a report, manifest, or response
  has a top-level `passed`, `status`, `ready`, `complete`, `approved`, or similar
  aggregate outcome, the contract must define how that outcome is derived from
  child evidence, blocking errors, skipped items, failed rows, partial outputs,
  and runtime/environment constraints.
- Split runtime/environment workflows are explicit. If one command cannot
  produce all required fields because of environment isolation, the schema must
  model partial outputs and final assembly separately.
- Every generated report or manifest has a completeness rule: required keys,
  exact counts, unique ids, keyed maps, or explicit allowed partial states.
- Every cross-cutting rule is expanded across sibling surfaces. If one surface
  needs resumability, idempotency, supersession, exact coverage, fail-closed
  reasons, conditional required fields, or output ownership, check every endpoint,
  command, report, manifest, and persistence surface touched by the same rule.

Self-gate failure rules:

- A row is `fail` if the behavior is only described in prose but not enforced by
  API/schema/SQL/error/test strategy where enforcement is applicable.
- A row is `fail` if the generated contract allows a payload/state that would
  violate the AC/PDR/ADR.
- A row is `fail` if a required output/report can omit a promised field,
  cardinality, reason, state transition, artifact path, or evidence link.
- A row is `fail` if an aggregate success/completion/pass field can contradict
  child evidence, blocking child errors, failed rows, skipped required children,
  or incomplete split-runtime outputs.
- A row is `fail` if a conditional rule is represented only as optional fields
  without a conditional enforcement mechanism or explicit implementation rule.
- A row is `fail` if an architecture-defined entity/report/artifact is missing
  from generated contracts.
- A row is `fail` if an API/command response requires fields that the documented
  producer cannot create.
- A row is `fail` if a cross-cutting rule is enforced on one surface but omitted
  on a sibling endpoint, command, report, manifest, or persistence surface.
- A row is `user_question` if the architect cannot determine the correct
  enforcement from approved requirements. Return to Phase 1 or Phase 2 before
  review.

The architect must fix all `fail` rows that can be resolved from approved
requirements before external review. Do not launch Phase 3.5 reviewers while
`architecture-contract-self-check.yaml` has any `fail` or `user_question` row.

### Phase 3 Checklist

Present to user:

```
Phase 3: Architect - Spec Generation

✅ API Contracts ({system|backend|frontend}/13-specs/api/)
   Endpoints defined: [N endpoints]
   Files created: [list]

✅ Claims Ledger
   architecture-claims.yaml exists: [Yes / No]
   Enforceable claims extracted: [N]
   Failed/user-question rows: [0 / list]

✅ Domain Schemas ({system|backend|frontend}/13-specs/schemas/domain/)
   Entities defined: [N entities]
   Files created: [list]

✅ Error Codes ({system|backend|frontend}/13-specs/errors/)
   Error codes defined: [N codes]
   Taxonomy updated: [Yes / No]

✅ Contract Self-Gate
   architecture-contract-self-check.yaml exists: [Yes / No]
   Enforceable claims checked: [N]
   Failed/user-question rows: [0 / list]
   Examples of negative cases checked: [list]

✅ Unknowns
   Spec-generation unknowns: [None / list]
   Questions requiring user or prior-phase input: [None / list]
   refinement-inconsistencies.yaml open items: [0 / list]

Ready to proceed to strategic architecture review? [yes / refine]
```

## Phase 3.5: Architecture Review (strategic)

Run this review after Phase 3 deliverables are complete and before Approval Gate #3.
This review is strategic, not tactical: it evaluates whether the business
requirements, architecture, ADRs, test strategy, and generated specs are
coherent enough to justify moving into story and implementation-boundary
breakdown.

Do not start Phase 4 until Phase 3.5 is complete.

**Goal:** prevent returning to Phase 3 after Phase 4 by catching architecture
and spec gaps before tactical planning begins.

**Inputs to review:**
- `docs/epics/{epic-dir}/details.md`
- `docs/epics/{epic-dir}/acceptance-criteria.md`
- `docs/epics/{epic-dir}/system-context.md`
- `docs/epics/{epic-dir}/architecture.md`
- `docs/epics/{epic-dir}/adr.md`
- `docs/epics/{epic-dir}/pdr.md`
- `docs/epics/{epic-dir}/test-strategy.md`
- `docs/epics/{epic-dir}/architecture-readiness-matrix.yaml`
- `docs/epics/{epic-dir}/architecture-claims.yaml`
- `docs/epics/{epic-dir}/architecture-contract-self-check.yaml`
- `docs/architecture/13-specs/api/{epic-id}-*.yaml`
- `docs/architecture/13-specs/schemas/domain/{epic-id}-*.json`
- `docs/architecture/13-specs/database/postgresql/{epic-id}-*.sql`
- `docs/architecture/13-specs/errors/by-domain/{epic-id}.yaml`
- `docs/architecture/13-specs/errors/taxonomy.yaml`

**Required reviewer set:**

Phase 3.5 review must be performed by all three reviewer perspectives: Codex,
Claude, and Antigravity. Do not choose only one reviewer and do not treat one
reviewer's approval as sufficient.

If the user preapproves all epic refinement gates, that preapproval only
removes the need to pause for user confirmation at the approval gates. It does
not skip Phase 3.5, reviewer CLI preflight, required reviewer attempts,
reviewer finding merge, or `refinement-review.md`. Preapproved gates cannot be
used as reviewer approval.

Each reviewer must be attempted for the initial full review and the final
approval review. Targeted correction reruns may use only the reviewer(s)
required by the rerun policy below, but `refinement-review.md` must document why
the rerun was targeted. If a local tool, credential, model, or CLI mode is
unavailable during a required attempt, write an explicit
`{reviewer}-unavailable.md` file in the current `refine-architecture-NNN`
directory and disclose that coverage gap in `refinement-review.md`. Do not
silently skip a required reviewer.

Unavailable reviewer tooling is not, by itself, a refinement failure. However,
Gate #3 must still include the three-reviewer coverage table and must clearly
state which of Codex, Claude, and Antigravity completed or were unavailable.

GLM through `opencode` is an optional additional reviewer. If `opencode`, the
configured GLM model, or the invocation fails, skip GLM silently: do not create
`glm-unavailable.md`, do not fail Phase 3.5, and do not classify reviewer
coverage as incomplete. If GLM completes and writes `glm-5.2.md`, import its
findings like any other reviewer output and record successful metadata.

Bad Scope-owned reviewer command syntax is not normal reviewer unavailability.
Before creating a review attempt, run the reviewer CLI preflight below. If a
reviewer would fail because Scope is passing an invalid flag, malformed
`allowedTools`, an invalid model id, or an invocation shape not supported by the
local CLI, stop with `SCOPE TOOLING ERROR`, fix the command/configuration, and
do not count or create a reviewer attempt. Examples: `codex exec` rejects a
Scope-provided flag, Claude exits with `unknown option`, or `agy` rejects the
configured model/flags.

### Phase 3.5a: Deterministic Readiness Preflight

Run this preflight before the first model review and before each full-review
rerun. The preflight is orchestrator-owned; do not ask external reviewers to
rediscover these basics.

#### Reviewer CLI Preflight

Validate reviewer command syntax before spending a review attempt:

- Codex:
  - `command -v codex`
  - `codex exec --help`
  - verify `CODEX_MODEL_ID` does not end in `-low`, `-medium`, or `-high`
  - verify Scope will call `codex exec --model "$CODEX_MODEL_ID" -c model_reasoning_effort="\"$CODEX_REASONING_EFFORT\"" --sandbox read-only`
  - verify Scope does not pass stale approval flags such as `--ask-for-approval`, which current `codex exec` rejects
  - if the local `codex exec --help` does not support a Scope-specified flag, stop as `SCOPE TOOLING ERROR`
- Claude:
  - `command -v claude`
  - `claude --help`
  - verify `scope-reviewer-claude-pexpect.py` exists
  - verify `python3 -c 'import pexpect'`
  - verify the final `--allowedTools` value is quoted as one shell argument
    because entries such as `Bash(python3 -c:*)` contain spaces
  - if Claude exits with `unknown option` before reading the prompt, stop as
    `SCOPE TOOLING ERROR`
- Antigravity:
  - `command -v agy`
  - `agy --help`
  - `agy models`
  - verify the configured primary and fallback model names appear in `agy models`
  - verify Scope will call `agy --model "$AGY_REVIEW_MODEL" --sandbox --dangerously-skip-permissions --print-timeout "$AGY_PRINT_TIMEOUT" --print "$PROMPT_TEXT"`
  - if `agy` rejects Scope-provided flags or model names, stop as `SCOPE TOOLING ERROR`
- GLM/opencode:
  - optional only
  - if `command -v opencode` succeeds, Scope may call `opencode run -m "$GLM_REVIEW_MODEL" --variant "high" --dir "$(pwd)" --dangerously-skip-permissions "$PROMPT_TEXT"`
  - if `opencode` is absent, the model is unavailable, or the call fails, skip GLM silently

Local tool absence, expired credentials, quota, or unavailable local models can
still be recorded as reviewer unavailable. Bad Scope invocation syntax cannot.

#### Architecture Readiness Matrix

Create or update `docs/epics/{epic-dir}/architecture-readiness-matrix.yaml`
before model review. This matrix is a compact checklist for reviewers; it is not
approval evidence by itself.

Required shape:

```yaml
epic_id: "{epic-id}"
generated_at: "{ISO-8601}"
status: draft
rows:
  - id: "AC1-PERSISTENCE"
    source:
      artifact: "acceptance-criteria.md"
      anchor: "AC1"
    requirement: "Concrete behavior promised by the AC/PDR/ADR"
    risk: "low | medium | high | destructive | security | data_integrity"
    requires:
      business: true
      architecture: true
      adr_or_pdr: true
      api: false
      json_schema: false
      sql: true
      error_contract: false
      test_strategy: true
      implementation_boundary_owner: true
      ownership_matrix: false
    evidence:
      business: ["docs/epics/{epic-dir}/acceptance-criteria.md#AC1"]
      architecture: []
      adr_or_pdr: []
      api: []
      json_schema: []
      sql: []
      error_contract: []
      test_strategy: []
      implementation_boundary_owner: []
      ownership_matrix: []
    status: "pass | fail | unverified | not_applicable"
    blocker_when_missing: true
    notes: ""
```

Gate semantics for `implementation_boundary_owner`:

- Before Gate #3, `requires.implementation_boundary_owner: true` is allowed
  with empty `evidence.implementation_boundary_owner` when the row otherwise has
  business, architecture, spec, and test-strategy evidence. Record it as
  `Gate #4 pending`, not as a Phase 3.5 blocker.
- Before Gate #4, every row with `requires.implementation_boundary_owner: true`
  must have `evidence.implementation_boundary_owner` populated by the
  story/boundary-plan artifacts.
- Missing implementation-boundary ownership is a Gate #4 blocker, not a Gate #3
  blocker, unless the missing owner hides an architecture decision that Phase 4
  would need to invent.

Create rows for:

- every acceptance criterion
- every accepted PDR/ADR decision that changes behavior, persistence, API,
  schema, error handling, cleanup, replay, migration, security, rollout, or
  operator workflow
- every destructive, idempotency, replay, cleanup, backfill, queue, external
  integration, or data-integrity behavior
- every generated API/schema/SQL/error contract introduced by the epic
- every implementation-boundary story owner once boundary plans exist

For cross-cutting resilience, replay, cleanup, or idempotency epics, also
require a phase/table/output ownership row for each affected data family. If the
epic includes destructive cleanup, replay, supersession, or attempt ownership,
missing ownership matrix evidence is `BLOCKING` before reviewer launch.

#### Scripted Readiness Checks

Run lightweight scripted checks and write results to
`docs/epics/{epic-dir}/reviews/refine-architecture-NNN/readiness-preflight.md`
before launching reviewers:

- required epic artifacts exist
- `refinement-inconsistencies.yaml` exists and has no `open` or
  `user_question` items
- `architecture-claims.yaml` exists, parses, has rows for every enforceable
  AC/PDR/ADR claim, and has no `fail` or `user_question` rows
- `architecture-readiness-matrix.yaml` exists and has at least one row per AC
- `architecture-contract-self-check.yaml` exists, parses, has rows for every
  enforceable AC/PDR/ADR claim, and has no `fail` or `user_question` rows
- every matrix row has a stable id, source, requirement, risk, requires,
  evidence, status, and blocker flag
- every `requires.*: true` except `requires.implementation_boundary_owner` has
  evidence or the row is `fail`/`unverified` before Gate #3
- every `requires.implementation_boundary_owner: true` row is either populated
  or explicitly marked `Gate #4 pending` before Gate #3
- API, JSON, and error specs parse
- SQL specs exist when any AC/PDR/ADR promises persistence or migrations
- every API/schema/error/SQL file expected by the matrix exists
- generated contracts enforce required/conditional/cardinality/fail-closed
  claims from `architecture-contract-self-check.yaml`
- `validate-architecture-contracts.sh docs/epics/{epic-dir}` passes when the
  script is installed
- every accepted PDR/ADR has at least one matrix row
- every high-risk row has test-strategy evidence
- every row that requires implementation has a planned implementation-boundary
  owner before Gate #4; missing implementation-boundary ownership must not block
  Gate #3 by itself
- destructive cleanup/replay/idempotency rows have ownership-matrix evidence

Do not run `validate-epic-docs.sh` as a Gate #3 blocker. That script is the
Gate #4 validator and is expected to fail before Phase 4 because
`file-plan-story-*.yaml` and boundary-plan-derived ownership evidence do not
exist yet. Gate #3 uses the architecture contract validator and the Phase 3.5
readiness preflight instead.

If scripted checks find missing artifacts, empty evidence, parse failures, stale
open questions, or obvious contract gaps that can be fixed from existing
approved requirements, fix those artifacts before running external reviewers.
Do not spend a full reviewer cycle on missing required files or mechanically
detectable omissions.

#### Pre-Review Hardening

Before launching external reviewers, create
`docs/epics/{epic-dir}/reviews/refine-architecture-NNN/pre-review-hardening.md`.
This is the orchestrator's adversarial self-check. It should be concise and
file-backed; do not turn it into another narrative architecture document.

Required checks:

- `architecture-contract-self-check.yaml` has no `fail` or `user_question` rows
- `architecture-claims.yaml` has no `fail` or `user_question` rows and every
  claims-ledger row appears in `architecture-contract-self-check.yaml`
- every acceptance criterion maps to API, schema, SQL/DDL, error contract, and
  test-strategy evidence where applicable, or has an explicit not-applicable
  rationale
- every AC/PDR/ADR claim with required, exact, conditional, fail-closed,
  resumable, idempotent, ownership, or generated-output semantics is enforced by
  a generated contract or explicitly marked not applicable with rationale
- every persistence claim has matching DDL/migration evidence or an explicit
  no-DDL decision with rationale
- every destructive, cleanup, replay, backfill, or migration action has a
  phase-owned table/key/record ownership matrix
- every "current state" or "latest state" claim has persisted ownership columns
  or deterministic derivation rules
- every endpoint or API payload promised by acceptance criteria, PDRs, or ADRs
  appears in the OpenAPI/API contract, or has an explicit no-endpoint decision
- every existing table, data family, side table, or generated output family
  named in architecture, ADRs, PDRs, boundary plans, previous audits, or reviewer
  feedback is covered by the new contract or explicitly deferred
- every observer, dashboard, monitor, report, export, or operator workflow can
  get the promised state from an API payload, database query, artifact, or
  documented derivation rule
- answer: "What would an implementer still have to invent?" If the answer is
  product behavior, architecture, persistence, API shape, error handling,
  ownership, ordering, state transition, or acceptance policy, the epic is not
  ready for external review

Recommended format:

```markdown
# Pre-Review Hardening: {epic-id}

## Result
{pass / changes required}

## Checks
| Check | Status | Evidence | Correction |
|---|---|---|---|
| Claims ledger complete | {pass/fail} | {architecture-claims.yaml rows} | {none or fix made} |
| Contract self-gate clean | {pass/fail} | {architecture-contract-self-check.yaml rows} | {none or fix made} |
| AC to contract/test coverage | {pass/fail/not applicable} | {files/sections} | {none or fix made} |
| Generated contracts enforce AC/PDR/ADR rules | {pass/fail} | {API/schema/SQL/error/test rows} | {none or fix made} |
| Persistence DDL/no-DDL decisions | {pass/fail/not applicable} | {files/sections} | {none or fix made} |
| Destructive/replay ownership matrix | {pass/fail/not applicable} | {files/sections} | {none or fix made} |
| Current-state ownership/derivation | {pass/fail/not applicable} | {files/sections} | {none or fix made} |
| Promised endpoints/API payloads | {pass/fail/not applicable} | {files/sections} | {none or fix made} |
| Existing table/data/output families | {pass/fail/not applicable} | {files/sections} | {none or fix made} |
| Observer/operator state availability | {pass/fail/not applicable} | {files/sections} | {none or fix made} |
| Implementer invention scan | {pass/fail} | {files/sections} | {none or fix made} |

## Open Hardening Failures
- {None, or concrete blocker}
```

If pre-review hardening finds a failure that can be fixed from existing approved
requirements, fix it before external review. If it requires user input, return
to the appropriate earlier phase instead of launching reviewers.

### Phase 3.5 Autonomous Review Loop

Phase 3.5 runs autonomously unless a reviewer finding requires user input.

Required loop:

1. Run deterministic readiness preflight and fix mechanical gaps.
2. Run pre-review hardening and fix self-detected gaps.
3. Run the initial Codex, Claude, and Antigravity reviews, plus GLM when
   `opencode` is available.
4. Merge reviewer findings and classify every issue as `BLOCKING`,
   `NON-BLOCKING`, or `QUESTION_FOR_USER`.
5. If there are no blocking findings, create `refinement-review.md` with
   `Approved for Gate #3`.
6. If there are blocking findings that can be fixed from existing product,
   architecture, and documentation context, fix them autonomously in the Phase
   1-3 artifacts and specs.
7. Run blocker pattern expansion before rerunning reviewers.
8. Rerun targeted scripted checks and pre-review hardening for the changed
   matrix rows, changed files, and sibling surfaces.
9. Rerun reviewers according to the rerun policy below.
10. Repeat correction batches up to `MAX_PHASE_35_CORRECTION_CYCLES=3`.

Rerun policy:

- Initial review: run all available reviewers after readiness preflight passes.
- Mechanical correction with no changed architecture decision: rerun scripted
  checks and only the reviewer(s) that found the blocker, plus any reviewer
  whose required evidence rows changed.
- New or materially changed architecture/spec artifact: rerun all available
  reviewers because new evidence can expose second-order contradictions.
- Final approval: run all available reviewers once unless the user explicitly
  instructs not to rerun.
- Do not rerun reviewers for missing required artifacts that scripted preflight
  should have caught; fix the artifact and rerun preflight first.

Blocker pattern expansion:

- Missing DDL or migration evidence means audit every persistence claim and
  every touched table/data family, not only the named table.
- Missing API field, endpoint, or payload evidence means audit every
  acceptance-facing API contract, schema, and observer/operator consumer.
- Missing ownership rule means audit every phase, side table, derived output,
  generated artifact, and cleanup/replay/backfill target.
- Missing current-state rule means audit every place that reads, writes,
  derives, caches, displays, or exports that state.
- Missing force/override/admin behavior means audit request fields, persisted
  rationale fields, authorization/policy rules, indexes, auditability, and test
  strategy together.
- Missing error behavior means audit API status, error taxonomy, retryability,
  persistence state, operator visibility, and tests together.
- Missing test-strategy evidence means audit every matrix row with the same
  risk category or runtime path.
- Record the sibling surfaces checked and fixes made in
  `pre-review-hardening.md` and `refinement-review.md`.

Cycle counting:

- The initial review does not count as a correction cycle.
- Each "fix blockers + rerun required reviewers" batch counts as one
  correction cycle.
- The default and maximum correction cycle limit is 3.

Stop and ask the user only if:

- a blocker requires a product, scope, policy, security, or credential decision
- reviewers disagree on an irreversible architecture tradeoff
- the same blocker persists after 3 correction cycles
- the correction would materially change epic scope

Do not ask the user before fixing concrete architecture/spec/doc mismatches that
are implied by existing approved requirements and architecture direction.

The final `refinement-review.md` must include review attempt directories,
blockers found per cycle, corrections applied, final reviewer decisions, and any
unresolved issues if the loop stopped.

| Reviewer | Required model | Prompt source | Output |
|----------|----------------|---------------|--------|
| Codex | `gpt-5.6-terra` with high reasoning | `commands/epic_refine/reviewer-architecture-codex.md` | `docs/epics/{epic-dir}/reviews/refine-architecture-NNN/codex-gpt-5.6-terra-high.md` |
| Claude | Opus via local `opus` alias | `commands/epic_refine/reviewer-architecture-claude.md` | `docs/epics/{epic-dir}/reviews/refine-architecture-NNN/claude-opus.md` |
| Antigravity | `Gemini 3.1 Pro (High)` with rate-limit fallback to `Gemini 3.5 Flash (High)` | `commands/epic_refine/reviewer-architecture-agy.md` | `docs/epics/{epic-dir}/reviews/refine-architecture-NNN/agy-gemini-3.1-pro-high.md` or fallback `agy-gemini-3.5-flash.md` |
| GLM | Optional `zai-coding-plan/glm-5.2` through opencode | `commands/epic_refine/reviewer-architecture-glm.md` | `docs/epics/{epic-dir}/reviews/refine-architecture-NNN/glm-5.2.md` |

Codex uses `gpt-5.6-terra` as the model id and `high` as reasoning effort. `gpt-5.6-terra-high` is only a review label/output filename and must never be passed to `codex --model`.
Claude uses the local Claude CLI `opus` alias by default. This is not pinned to a specific Claude release. To pin a specific Claude model id, set `SCOPE_CLAUDE_PEXPECT_COMMAND`.

Use the transport appropriate to each reviewer:

- Claude uses the `pexpect` one-shot file-output wrapper because Claude CLI
  headless mode can be token-only or restricted in some subscription
  environments. The wrapper gives Claude a short instruction with absolute
  paths to the reviewer prompt, repository/worktree, and output file. Claude
  writes the report file directly; the wrapper validates it with sentinels,
  strips the sentinels, and retries once on timeout.
- Before manually treating Claude as hung, unavailable, or safe to kill,
  inspect the matching PTY log under `tmp_debug/scope-reviewer-logs/`. Empty
  wrapper stdout/stderr files in the review directory are not evidence that
  Claude is idle or blocked.
- Antigravity uses the direct `agy --print "prompt"` invocation.
- GLM uses `opencode run` when available and is skipped silently otherwise.

Reviewer execution skeleton:

```bash
REVIEWS_DIR="docs/epics/${EPIC_DIR}/reviews"
mkdir -p "$REVIEWS_DIR"
MAX_PHASE_35_CORRECTION_CYCLES="${SCOPE_PHASE_35_MAX_CYCLES:-3}"

REFINE_REVIEW_NUM=$(find "$REVIEWS_DIR" -maxdepth 1 -type d -name 'refine-architecture-[0-9][0-9][0-9]' 2>/dev/null | sed 's/.*refine-architecture-//' | sort -n | tail -1)
if [ -z "$REFINE_REVIEW_NUM" ]; then
  REFINE_REVIEW_NUM=1
else
  REFINE_REVIEW_NUM=$((10#$REFINE_REVIEW_NUM + 1))
fi

REFINE_REVIEW_ID=$(printf "refine-architecture-%03d" "$REFINE_REVIEW_NUM")
REFINE_REVIEW_DIR="${REVIEWS_DIR}/${REFINE_REVIEW_ID}"
mkdir -p "$REFINE_REVIEW_DIR"
REFINE_REVIEW_METADATA_FILE="${REFINE_REVIEW_DIR}/review-metadata.yaml"

cat > "$REFINE_REVIEW_METADATA_FILE" <<EOF
epic_id: "${EPIC_ID}"
review_id: "${REFINE_REVIEW_ID}"
created_at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
reviews:
EOF

REFINE_REVIEW_PROMPT_DIR=$(find ./plugins/scope/commands/epic_refine ./.claude/commands/epic_refine ./src_shared/commands/epic_refine ~/.claude/commands/epic_refine -type d 2>/dev/null | head -1)
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
GLM_TMP_DIR="tmp_debug/scope-refine/${EPIC_ID}/${REFINE_REVIEW_ID}"
mkdir -p "$GLM_TMP_DIR"
SCOPE_REVIEW_PYTHON="${SCOPE_REVIEW_PYTHON:-python3}"
CLAUDE_REFINE_ALLOWED_TOOLS="Read,Glob,Grep,Bash(pwd),Bash(cd:*),Bash(ls:*),Bash(find:*),Bash(rg:*),Bash(grep:*),Bash(cat:*),Bash(sed:*),Bash(head:*),Bash(tail:*),Bash(wc:*),Bash(stat:*),Bash(file:*),Bash(which:*),Bash(echo:*),Bash(printf:*),Bash(for:*),Bash(python -c:*),Bash(python3 -c:*),Bash(git status:*),Bash(git rev-parse:*),Bash(git log:*),Bash(git diff:*),Bash(git show:*),Bash(git ls-files:*),Bash(git merge-base:*),Bash(git branch:*),Bash(git worktree list:*),Write"

build_refine_review_prompt_file() {
  local reviewer_file="$1"
  local output_file="$2"
  sed \
    -e "s|{{EPIC_ID}}|${EPIC_ID}|g" \
    -e "s|{{EPIC_DIR}}|${EPIC_DIR}|g" \
    -e "s|{{REPO_ROOT}}|$(pwd)|g" \
    "${REFINE_REVIEW_PROMPT_DIR}/${reviewer_file}" > "$output_file"
}

# Attempt reviewers according to the rerun policy:
# - Initial and final approval reviews use all available reviewers.
# - Mechanical correction reviews may be targeted to the reviewer(s) that found
#   the blocker plus reviewers whose required evidence rows changed.
# - Codex directly when `codex` is available, otherwise codex-unavailable.md.
#   Use --model "$CODEX_MODEL_ID" and
#   -c model_reasoning_effort="\"$CODEX_REASONING_EFFORT\"".
#   Do not pass "$CODEX_REVIEW_LABEL" as the model id.
#   If "$CODEX_MODEL_ID" ends in -low, -medium, or -high, stop and write
#   codex-unavailable.md because the reasoning suffix belongs in
#   CODEX_REASONING_EFFORT, not CODEX_MODEL_ID.
# - Claude through scope-reviewer-claude-pexpect.py when helper + `claude` +
#   Python pexpect are available, otherwise claude-unavailable.md
# - Antigravity directly with:
#     agy --model "$AGY_REVIEW_MODEL" --sandbox --dangerously-skip-permissions --print-timeout "$AGY_PRINT_TIMEOUT" --print "$PROMPT_TEXT"
#   Validate "$AGY_REVIEW_MODEL" and "$AGY_FALLBACK_MODEL" by exact line match
#   against `agy models` before running. Use the display labels from `agy models`
#   such as `Gemini 3.1 Pro (High)`, not Gemini CLI aliases such as
#   `gemini-3.1-pro-high`; agy can silently fall back to Flash Medium for the
#   normalized alias.
#   If the primary model is rate-limited, retry once with "$AGY_FALLBACK_MODEL".
#   Otherwise write agy-unavailable.md.
# - GLM through opencode when `opencode` is available. This reviewer is optional
#   and silent-fail: if opencode/model is unavailable or the command fails, skip
#   without creating glm-unavailable.md.
#
# Claude invocation shape for each refine attempt:
#   "$SCOPE_REVIEW_PYTHON" "$REVIEWER_CLAUDE_PEXPECT_SCRIPT" \
#     --reviewer "claude" \
#     --model "Claude Opus (local alias)" \
#     --claude-command "${SCOPE_CLAUDE_PEXPECT_COMMAND:-claude --model opus --dangerously-skip-permissions --allowedTools '${CLAUDE_REFINE_ALLOWED_TOOLS}' --no-chrome}" \
#     --prompt-file "${REFINE_REVIEW_DIR}/reviewer-architecture-claude-prompt.md" \
#     --output-file "${REFINE_REVIEW_DIR}/claude-opus.md" \
#     --metadata-file "$REFINE_REVIEW_METADATA_FILE" \
#     --cwd "$(pwd)" \
#     --timeout-seconds "$REVIEW_TIMEOUT_SECONDS" \
#     --retries "$REVIEW_RETRIES"
#
# Antigravity invocation shape for each refine attempt:
#   build_refine_review_prompt_file \
#     "reviewer-architecture-agy.md" \
#     "${REFINE_REVIEW_DIR}/reviewer-architecture-agy-prompt.md"
#   AGY_PROMPT_TEXT="$(cat "${REFINE_REVIEW_DIR}/reviewer-architecture-agy-prompt.md")"
#   if ! agy models 2>/dev/null | grep -Fxq "$AGY_REVIEW_MODEL"; then
#     echo "Antigravity primary model is not an exact agy model label: ${AGY_REVIEW_MODEL}" > "${REFINE_REVIEW_DIR}/agy-unavailable.md"
#     echo 'Use `Gemini 3.1 Pro (High)`, not `gemini-3.1-pro-high`.' >> "${REFINE_REVIEW_DIR}/agy-unavailable.md"
#   elif ! agy models 2>/dev/null | grep -Fxq "$AGY_FALLBACK_MODEL"; then
#     echo "Antigravity fallback model is not an exact agy model label: ${AGY_FALLBACK_MODEL}" > "${REFINE_REVIEW_DIR}/agy-unavailable.md"
#   else
#     if ! agy \
#         --model "$AGY_REVIEW_MODEL" \
#         --sandbox \
#         --dangerously-skip-permissions \
#         --print-timeout "$AGY_PRINT_TIMEOUT" \
#         --print "$AGY_PROMPT_TEXT" \
#         > "${REFINE_REVIEW_DIR}/${AGY_REVIEW_OUTPUT_ID}.md" \
#         2> "${REFINE_REVIEW_DIR}/${AGY_REVIEW_OUTPUT_ID}.stderr.txt"; then
#       if grep -Eiq 'rate.?limit|quota|429|resource.?exhausted|too many requests|try again later' \
#           "${REFINE_REVIEW_DIR}/${AGY_REVIEW_OUTPUT_ID}.stderr.txt"; then
#         agy \
#           --model "$AGY_FALLBACK_MODEL" \
#           --sandbox \
#           --dangerously-skip-permissions \
#           --print-timeout "$AGY_PRINT_TIMEOUT" \
#           --print "$AGY_PROMPT_TEXT" \
#           > "${REFINE_REVIEW_DIR}/${AGY_FALLBACK_OUTPUT_ID}.md" \
#           2> "${REFINE_REVIEW_DIR}/${AGY_FALLBACK_OUTPUT_ID}.stderr.txt" \
#           || echo "Antigravity fallback failed." > "${REFINE_REVIEW_DIR}/agy-unavailable.md"
#       else
#         echo "Antigravity failed." > "${REFINE_REVIEW_DIR}/agy-unavailable.md"
#       fi
#     fi
#   fi
#
# GLM invocation shape for each refine attempt:
#   if command -v opencode >/dev/null 2>&1; then
#     build_refine_review_prompt_file \
#       "reviewer-architecture-glm.md" \
#       "${REFINE_REVIEW_DIR}/reviewer-architecture-glm-prompt.md"
#     GLM_PROMPT_TEXT="$(cat "${REFINE_REVIEW_DIR}/reviewer-architecture-glm-prompt.md")"
#     if ! opencode run \
#         -m "$GLM_REVIEW_MODEL" \
#         --variant "high" \
#         --dir "$(pwd)" \
#         --dangerously-skip-permissions \
#         "$GLM_PROMPT_TEXT" \
#         > "${REFINE_REVIEW_DIR}/${GLM_REVIEW_OUTPUT_ID}.md" \
#         2> "${GLM_TMP_DIR}/${GLM_REVIEW_OUTPUT_ID}.stderr.txt"; then
#       rm -f "${REFINE_REVIEW_DIR}/${GLM_REVIEW_OUTPUT_ID}.md"
#     fi
#   fi
```

**Review questions:**

- Does the architecture fully satisfy the Phase 1 business behavior and acceptance criteria?
- Does the architecture force the Architect to make product, policy, scope, workflow, or acceptance decisions that should have been specified by the Product Owner?
- Are component boundaries, APIs, data models, persistence, orchestration, error handling, migration strategy, and operational behavior clear enough that Phase 4 can decompose work without redesign?
- Do generated API/schema/error specs match the architecture and ADRs?
- Does the test strategy prove the high-risk architectural behavior, including the 90%+ story coverage floor?
- Are ADRs and PDRs sufficient, globally numbered where required, and consistent with project documentation rules?
- Are there missing decisions that would cause developers to invent architecture during implementation?

**Required output:** create or update
`docs/epics/{epic-dir}/refinement-review.md` with:

```markdown
# Refinement Review: {epic-id}

## Summary
{pass / changes required}

## Reviewer Coverage
| Reviewer | Status | Findings imported |
|----------|--------|-------------------|
| Codex | {completed/unavailable/not run} | {N} |
| Claude | {completed/unavailable/not run} | {N} |
| Antigravity | {completed/unavailable/not run} | {N} |
| GLM | {completed/not run} | {N} |

## Readiness Preflight
| Check | Status | Evidence |
|---|---|---|
| Reviewer CLI preflight | {pass/fail} | {readiness-preflight.md section} |
| Architecture readiness matrix | {pass/fail} | `architecture-readiness-matrix.yaml` |
| Pre-review hardening | {pass/fail} | `pre-review-hardening.md` |
| Required artifacts | {pass/fail} | {missing/present list} |
| API/schema/error/SQL parse | {pass/fail/not applicable} | {output} |
| AC/PDR/ADR coverage | {pass/fail} | {matrix row counts} |
| High-risk test coverage | {pass/fail/not applicable} | {matrix row counts} |
| File-plan ownership status | {Gate #4 pending / pass / fail} | {rows pending or populated} |

## Review Cycle Summary
| Cycle | Review directory | Review scope | Trigger | Blockers found | Corrections applied | Result |
|-------|------------------|--------------|---------|----------------|---------------------|--------|
| Initial | reviews/refine-architecture-001 | full | readiness preflight passed | {N} | n/a | {approved / corrections needed} |
| 1 | reviews/refine-architecture-002 | {targeted/full} | {blocking findings / changed architecture artifact / final approval} | {N} | {summary} | {approved / corrections needed / stopped} |

## Strategic Findings

### BLOCKING
- {Architecture/spec/business ambiguity that must be fixed before Gate #3}

### NON-BLOCKING
- {Useful improvements that can be handled before or during Phase 4}

## Required Corrections Before Gate #3
- {Concrete docs/specs/ADRs/PDRs/test-strategy updates}

## Decision
{Approved for Gate #3 / Not approved for Gate #3}
```

**Blocking criteria:**

Gate #3 cannot be shown if any reviewer or the orchestrator finds:

- `SCOPE TOOLING ERROR` from reviewer CLI preflight
- missing or failing `architecture-claims.yaml`
- missing or failing `architecture-readiness-matrix.yaml`
- missing or failing `architecture-contract-self-check.yaml`
- missing or failing `pre-review-hardening.md`
- open `refinement-inconsistencies.yaml` items
- unresolved readiness preflight failures for required artifacts, parse checks,
  AC/PDR/ADR coverage, or high-risk test coverage
- unresolved business ambiguity that would require Architect or Developer product decisions
- unresolved unknown or unclear issue discovered during Phase 0-3 artifact generation
  that affects intent, product behavior, architecture, specs, testing, rollout, or
  implementation ownership
- missing or contradictory architecture decisions
- generated specs that do not match architecture or ADRs
- generated specs that mention but do not enforce required, exact,
  conditional, fail-closed, resumable, idempotent, ownership, or output
  cardinality rules from accepted AC/PDR/ADR claims
- missing API/schema/error contracts for behavior required by acceptance criteria
- insufficient test strategy for high-risk behavior or the 90%+ story coverage floor
- architectural gaps that would force Phase 4 to invent design while writing boundary plans

Missing `file-plan-story-*.yaml`, missing `acceptance-traceability.yaml` rows
derived from boundary plans, or empty
`evidence.implementation_boundary_owner` rows are expected before Phase 4 and
must not block Gate #3 by themselves. They become blocking before Gate #4. They
are Gate #3 blockers only when the missing owner reflects a missing architecture
decision, unclear implementation boundary, or absent test-strategy proof path.

Fix all blocking findings before Gate #3. If a blocking finding reveals product
ambiguity, return to Phase 1 and interview the user. If it reveals architecture
or spec ambiguity, update Phase 2/3 artifacts and rerun Phase 3.5 review.
Apply the autonomous review loop above before asking the user, unless one of the
explicit stop conditions applies.

### Approval Gate #3

Before presenting this gate, confirm `docs/epics/{epic-dir}/refinement-review.md`
exists and its decision is `Approved for Gate #3`. Also confirm
`docs/epics/{epic-dir}/architecture-readiness-matrix.yaml` exists and the latest
`readiness-preflight.md` and `pre-review-hardening.md` have no unresolved
blocking failures.

If the user preapproved Gate #3 or all gates, do not present the approval prompt
again, but still enforce the checks above. Gate preapproval is valid only after
Phase 3.5 reviewers were attempted and `refinement-review.md` is approved.

**If user approves**: Write summary entry and proceed to Phase 4

```bash
echo '{"agent":"architect","session_id":"'"$SESSION_ID"'","phase":"spec_generation","status":"success","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' >> "$SUMMARIES_FILE"
echo '{"agent":"architect","session_id":"'"$SESSION_ID"'","phase":"architecture_review","status":"success","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' >> "$SUMMARIES_FILE"
```

**If user wants refinement**: Address concerns, update specs, re-present checklist

---

## Phase 4: Architect (story_breakdown + implementation_boundary_plan + contracts)

**Instruction:** Continue as `architect` agent for the `story_breakdown`, `implementation_boundary_plan`, and `contracts` phases.

**Goal:** Break epic into implementable stories, create executable contracts, and document binding implementation boundaries plus proof obligations.

At the start of Phase 4, restate any remaining unknowns from Phase 3.5. Do not write stories, boundary plans, or contracts if any unresolved issue would force a developer to invent product behavior or architecture. Return to the appropriate earlier phase and ask the user when needed.

**Story sizing constraints:** Each story should have max 7 non-trivial files, ~600 LOC of new/modified code, and the epic should have 5-8 stories. Trivial files (empty `__init__.py`, config with no logic, re-exports) don't count toward the 7-file limit. If a story exceeds these limits, split it.

**Story numbering rule:** Story 0 is reserved for epic scaffolding only. Create Story 0 only if the epic genuinely has scaffolding work such as contracts, config content, schemas with authored examples, prompts, or directory/module scaffolding that should be authored before developer implementation. If there is no scaffolding story, numbering starts at Story 1.

**Phase context to pass:**
```
epic_id: {epic-id}
phase: story_breakdown  # then implementation_boundary_plan, then contracts
agent_summaries: .scope/{epic-dir}/agent_summaries.jsonl
```

**Key deliverables:**

### Story breakdown

- User stories with acceptance criteria, test requirements, dependencies
- Initial acceptance traceability matrix mapping AC/story checks to expected implementation files, expected test files, required assertions, and runtime evidence requirements
- Stories sequenced for incremental delivery
- Written to tracking system, `docs/epics/{epic-dir}/acceptance-criteria.md`, and `docs/epics/{epic-dir}/acceptance-traceability.yaml`

### Story 0 extraction (CRITICAL — do this BEFORE writing boundary plans)

Before assigning deliverables to dev stories, classify each file by work type:

| Work Type | Verifiable via mypy/tests? | Owner | Story |
|-----------|---------------------------|-------|-------|
| Config content (YAML values, semantic descriptions, prompt templates) | No — content quality is subjective | Architect | **Story 0** |
| JSON schemas with example values | No — examples are domain content | Architect | **Story 0** |
| Scaffolding (empty modules, __init__.py, directory structure) | No — no behavior to test | Architect | **Story 0** |
| **contracts.py** (Protocol classes with exact method signatures) | Yes — mypy verifies implementations match | Architect | **Story 0** |
| Pydantic models, adapters, business logic | Yes — unit tests + mypy | Developer | **Story 1+** |

**Rule:** If a file's primary value is its CONTENT (not its structure), it belongs in Story 0. The architect authors it directly.

**Important:** Do not create a placeholder Story 0 just because the number exists. If no scaffolding deliverables exist for this epic, skip Story 0 entirely and start with Story 1.

**Common Story 0 deliverables:**
- Config files with domain-specific values
- Prompt templates with carefully authored instructions
- JSON schemas with realistic example values
- Directory scaffolding for new modules
- **`contracts.py` — Python Protocol classes defining ALL cross-story interfaces**

### contracts.py (CRITICAL — new deliverable)

The architect MUST produce a `contracts.py` file in the epic's source package. This file contains Python `Protocol` classes that define every public interface that will be called across story boundaries.

`contracts.py` is implementation source code. It must never be created inside `docs/epics/{epic-dir}/`.

**What goes in contracts.py:**
- One Protocol class per component that other stories depend on
- Exact method signatures with full type annotations
- Return types using the Pydantic models from `models_*.py`
- Import statements for all referenced types

**What does NOT go in contracts.py:**
- Internal/private methods (only public interface)
- Implementation details
- Components only used within a single story

**Example contracts.py:**
```python
"""Executable contracts for Epic 015: Vector-Driven Documentation.

These Protocol classes define the cross-story interfaces. Implementations
MUST satisfy these protocols. Verified via: mypy --strict

Story 0 creates this file. Stories 1-N implement classes matching these protocols.
The orchestration story (Story 5) imports and type-hints against these protocols.
"""
from typing import Protocol, Dict, List, Optional
from pathlib import Path

from src.documentation.models_rendering import (
    AggregatedSignals, SynthesisResult, ReRenderResult, ReRenderMetrics
)
from src.config.models import SectionDescriptionConfig


class IEmbeddingCache(Protocol):
    """Story 01: Pre-computes section description embeddings."""

    def warm(self) -> int: ...

    def get_embedding(
        self, section_id: str, config_path: Path
    ) -> Optional[List[float]]: ...


class IIntelAggregator(Protocol):
    """Story 02: Queries Qdrant per section using metadata + vector similarity."""

    def aggregate_for_section(
        self, entity_id: str, section_config: SectionDescriptionConfig
    ) -> AggregatedSignals: ...

    def aggregate_for_file(
        self, entity_id: str, file_config: dict
    ) -> Dict[str, AggregatedSignals]: ...


class IKnowledgeSynthesizer(Protocol):
    """Story 03: Converts aggregated signals to structured JSON via LLM."""

    def synthesize(
        self, file_name: str,
        section_signals: Dict[str, AggregatedSignals],
        entity_id: str
    ) -> Optional[SynthesisResult]: ...
```

**Validation rule:** After Story 0, running `python -c "import src.documentation.contracts"` must succeed (all types importable).

### Implementation Boundary Plan (one per story)

The file remains named `docs/epics/{epic-dir}/file-plan-story-NN.yaml` for workflow compatibility. Its content is an implementation boundary plan, not a tactical list of files to edit.

Required shape:

```yaml
epic_id: "{epic-id}"
story_id: "story-01"
story_title: "Short story title"
depends_on: []
required_contracts:
  - id: "contract-identifier"
    contract: "contracts.py::IExample.method"
    obligation: "Exact public interface or behavior the implementation must satisfy"
    verification: "mypy --strict path/to/file.py plus targeted test"
required_touchpoints:
  - id: "touchpoint-identifier"
    surface: "API endpoint, CLI, worker, adapter, table, config, or existing module"
    obligation: "What must be integrated or preserved"
    evidence_required: "Source/test/runtime evidence expected after implementation"
candidate_files:
  - path: "src/package/module.py"
    reason: "Likely implementation area discovered during refinement"
    advisory: true
forbidden_changes:
  - path_or_surface: "public API, ADR-protected module, migration, config, or behavior"
    rule: "Change that is not allowed without returning to refinement"
proof_obligations:
  - id: "proof-identifier"
    acceptance_rows: ["AC1.1"]
    required_evidence: "unit | integration | e2e | live_smoke | runtime_command"
    command_hint: "pytest tests/... or concrete runtime checker"
    success_condition: "Observable pass condition, output, state, or threshold"
```

Binding fields:

- `required_contracts`
- `required_touchpoints`
- `forbidden_changes`
- `proof_obligations`

Advisory fields:

- `candidate_files`

The developer may skip candidate files or discover different implementation files when current source inspection shows a better path. The developer must record the strategy, files used, skipped relevant candidates, and evidence in `implementation-evidence.yaml`.

### Contract Call Boundaries

When a story must call methods from another story's components, include the obligation under `required_contracts`. This is the machine-readable cross-reference that prevents signature mismatches.

**Example:**
```yaml
required_contracts:
  - id: "re-render-aggregator-call"
    contract: "contracts.py::IIntelAggregator.aggregate_for_file"
    obligation: "Call aggregate_for_file(entity_id: str, file_config: dict) -> Dict[str, AggregatedSignals]"
    verification: "mypy --strict src/documentation/updater.py"
  - id: "re-render-synthesizer-call"
    contract: "contracts.py::IKnowledgeSynthesizer.synthesize"
    obligation: "Call synthesize(file_name: str, section_signals: Dict[str, AggregatedSignals], entity_id: str) -> Optional[SynthesisResult]"
    verification: "mypy --strict src/documentation/updater.py"
  - id: "template-renderer-call"
    contract: "contracts.py::ITemplateReRenderer.render_file"
    obligation: "Call render_file(template_name: str, context: dict, entity_slug: str, entity_config: EntityConfig) -> ReRenderResult"
    verification: "mypy --strict src/documentation/updater.py"
```

**Rule:** If a boundary plan has a `required_contracts` entry, the developer MUST verify each call matches the exact signature listed. mypy enforces this when the implementation type-hints dependencies using Protocol types from contracts.py.

### CodeGraph Context (Recommended)

Use CodeGraph during refinement when it is present to discover existing symbols, dependencies, callers, and related files before finalizing architecture and boundary plans. Prefer CodeGraph MCP when available. If MCP is unavailable or unhealthy, use the CodeGraph CLI.

During refinement, CodeGraph queries should target the main repository root. CLI fallback examples:

```bash
if [ ! -d ".codegraph" ]; then
  codegraph init .
  codegraph index .
else
  codegraph sync-if-dirty . || codegraph sync .
fi
codegraph status .

# JSON examples for architecture and boundary-plan context when using the CLI
codegraph query "ExistingServiceName" --path . --json
codegraph context "epic behavior or integration path to inspect" --path . --format json --max-nodes 80 --max-code 20
codegraph files --path . --json
```

Use CodeGraph output as discovery context only. Architecture decisions and boundary plans must still cite the actual source files, contracts, tests, and documentation that were inspected.

### Acceptance Traceability Matrix

Create `docs/epics/{epic-dir}/acceptance-traceability.yaml` during Phase 4, alongside the boundary plans. This artifact is the audit checklist. It is not proof by itself; implementation and audit must verify each row against code, tests, and runtime evidence.

The initial matrix is generated from `acceptance-criteria.md`, `architecture.md`, `adr.md`, `test-strategy.md`, and `file-plan-story-*.yaml`.

Also update `docs/epics/{epic-dir}/architecture-readiness-matrix.yaml` after
boundary plans are written:

- fill `evidence.implementation_boundary_owner` for every row with `requires.implementation_boundary_owner: true`
- mark rows `fail` if they still lack a story/boundary-plan owner
- add rows for any new implementation obligation discovered during boundary planning
- ensure every high-risk or runtime/operational row has both test-strategy and
  implementation-boundary ownership evidence before Gate #4

Required format:

```yaml
epic_id: {epic-id}
generated_at: YYYY-MM-DD
status: draft

acceptance_items:
  - id: AC1.1
    story: "Story 1"
    requirement: "Plain-language expected behavior."
    source:
      doc: docs/epics/{epic-dir}/acceptance-criteria.md
      section: "Story 1"
    implementation:
      expected_files:
        - src/package/module.py
      actual_files: []
    tests:
      expected_files:
        - tests/test_module.py
      required_assertions:
        - "Specific behavior the test must prove."
      actual_tests: []
    runtime_evidence:
      required: false
      commands: []
      evidence: []
    status: planned
    audit_notes: ""
```

Rules:
- Every acceptance criterion, story-level behavior, required edge case, and runtime/operational requirement gets a row.
- `expected_files` come from boundary-plan `candidate_files`, `required_touchpoints`, and developer strategy evidence where file paths are known.
- `required_assertions` describe what must be proven, not just which test file should exist.
- `runtime_evidence.required` is `true` for live smoke, migration, backfill, seed/bootstrap, reindex, onboarding, external sync, or other value-delivery checks.
- Initial `actual_files`, `actual_tests`, and `runtime_evidence.evidence` remain empty until implementation.
- `status` starts as `planned` and can later become `implemented`, `tested`, `verified`, `blocked`, or `deferred`.

### Final Validation (required before Gate #4)

Before presenting the final approval checklist, run the epic documentation validator and fix every failure:

```bash
VALIDATE_EPIC_SCRIPT=$(find ./plugins/scope/scripts ./.claude/commands/scripts ./src_shared/scripts ~/.claude/commands/scripts -name "validate-epic-docs.sh" 2>/dev/null | head -1)
if [ -z "$VALIDATE_EPIC_SCRIPT" ]; then
  echo "validate-epic-docs.sh not found in installed or source paths"
  exit 1
fi

"$VALIDATE_EPIC_SCRIPT" "docs/epics/${EPIC_DIR}"
```

The final approval gate cannot be shown until validation passes. Validation must confirm:
- macOS `.DS_Store` files are ignored and removed by validation
- no `__pycache__`, `.py`, `.pyc`, or other non-markdown/non-YAML artifacts exist in the epic docs folder
- all required epic files exist
- `refinement-inconsistencies.yaml` exists and has no `open` or
  `user_question` items
- `architecture-claims.yaml` exists and passes architecture contract validation
- `architecture-contract-self-check.yaml` exists and passes architecture contract validation
- `details.md` frontmatter is present and contains at least `epic_id`, `title`, and `status`
- `details.md` includes `## Intent Alignment` and has no open intent questions
- `adr.md` uses global ADR numbering and includes the required template fields
- `acceptance-traceability.yaml` exists and contains `acceptance_items`
- `architecture-readiness-matrix.yaml` exists and every row requiring
  implementation-boundary ownership has `evidence.implementation_boundary_owner`
- at least one `file-plan-story-*.yaml` exists

### Phase 4 Checklist

Present to user:

```
Phase 4: Architect - Stories, Contracts & Implementation Boundary Plan

✅ Story Breakdown
   Stories created: [N stories]
   Dependency order: [Story sequence]

✅ Contracts (contracts.py)
   Protocol classes: [N protocols defined]
   Cross-story interfaces: [List of class names]
   All types importable: [Yes / No]

✅ Implementation Boundary Plan
   Boundary plans: [N files]
   Required contracts: [N binding obligations]
   Required touchpoints: [N binding obligations]
   Candidate files: [N advisory paths]
   Forbidden changes: [N protected surfaces]
   Proof obligations: [N evidence requirements]

✅ Coverage
   All stories mapped to boundary obligations: [Yes / No]
   All acceptance criteria traceable: [Yes / No]
   All cross-story calls have contracts: [Yes / No]

✅ Acceptance Traceability
   acceptance-traceability.yaml present: [Yes / No]
   AC/story/runtime rows created: [N rows]
   Required assertions specified: [Yes / No]

✅ Epic Artifact Validation
   Required epic files present: [Yes / No]
   details.md frontmatter valid: [Yes / No]
   details.md Intent Alignment approved: [Yes / No]
   adr.md numbering/template valid: [Yes / No]
   Epic folder hygiene valid: [Yes / No]

✅ Unknowns
   Developer-facing product unknowns: [None / list]
   Developer-facing architecture unknowns: [None / list]
   User questions required before implementation: [None / list]
   refinement-inconsistencies.yaml open items: [0 / list]

Ready to mark epic as ready-for-implementation? [yes / refine]
```

### Approval Gate #4

**If user approves**:

1. Write summary entry
2. Update epic status to "ready-for-implementation"
3. Calculate and output costs

```bash
# Write completion entry
echo '{"agent":"architect","session_id":"'"$SESSION_ID"'","phase":"implementation_boundary_plan","status":"success","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' >> "$SUMMARIES_FILE"

# Update epic status in details.md frontmatter
# status: ready-for-implementation

# Calculate costs
SCRIPT=$(find ./.claude/commands/scripts ~/.claude/commands/scripts -name "agents-tokens.sh" 2>/dev/null | head -1)
if [ -n "$SCRIPT" ]; then
    $SCRIPT --aggregate "$SUMMARIES_FILE" --storeInSummaries
fi
```

**If user wants refinement**: Address concerns, update stories/boundary plans/contracts, re-present checklist

---

## Completion Output

```
Epic Refinement Complete: {epic-id}

Artifacts created:
├── docs/epics/{epic-dir}/
│   ├── details.md (with approved Intent Alignment)
│   ├── acceptance-criteria.md
│   ├── acceptance-traceability.yaml
│   ├── system-context.md
│   ├── architecture.md
│   ├── adr.md
│   ├── pdr.md
│   ├── test-strategy.md
│   ├── refinement-inconsistencies.yaml
│   ├── architecture-claims.yaml
│   ├── architecture-contract-self-check.yaml
│   ├── refinement-review.md
│   ├── file-plan-story-00.yaml   (only if scaffolding exists; may include contracts.py)
│   ├── file-plan-story-01.yaml
│   └── file-plan-story-NN.yaml
├── docs/architecture/13-specs/
│   ├── api/{epic-id}-*.yaml
│   ├── schemas/domain/{epic-id}-*.json
│   └── errors/by-domain/{epic-id}.yaml
└── Tracking system
    └── [N] stories created with AC and dependencies

Contract protocols: [N] interfaces in contracts.py
Cross-story calls documented: [N] required contract obligations in boundary plans

Status: ready-for-implementation
Cost: $X.XX

Next: Run /implement {epic-id} or /implement_tdd {epic-id}
```

---

## Compaction Survival

**State is tracked in artifacts, not conversation memory.**

If session compacts mid-refinement:

1. Check `.scope/{epic-dir}/refine_summaries.jsonl` for completed phases
2. Check which epic docs exist:
   - `details.md` contains `## Intent Alignment` with no open intent questions → Phase 0 complete
   - `refinement-inconsistencies.yaml` has no open or user-question items → no known unresolved ambiguity
   - `acceptance-criteria.md` exists → Phase 1 complete
   - `architecture.md` exists → Phase 2 complete
   - `architecture-claims.yaml`, `architecture-contract-self-check.yaml`, and `docs/architecture/13-specs/api/{epic-id}-*` exist → Phase 3 complete
   - `refinement-review.md` exists with `Approved for Gate #3` → Phase 3.5 complete
   - `file-plan-story-*.yaml` exists with implementation boundary plan schema → Phase 4 complete
3. Resume from appropriate phase

---

## Communication Style

**Progress indicators:**
- "Phase 0: Intent Alignment - Why Understanding"
- "Phase 1/4: Product Owner - Epic Validation"
- "Phase 2/4: Architect - System Context & Architecture"
- "Phase 3/4: Architect - Spec Generation"
- "Phase 3.5/4: Strategic Architecture Review"
- "Phase 4/4: Architect - Stories, Contracts & Implementation Boundary Plan"

**Approval gates:**
- Present checklist summary
- Ask specific question: "Ready to proceed? [yes / refine]"
- Wait for explicit approval before proceeding

**Discovery updates:**
- If any phase reveals new unknowns or unclear issues, state the unknown, explain
  which prior phase owns it, and ask the user before continuing when it affects
  intent, product behavior, architecture, testing, rollout, or implementation
  ownership.
- If Phase 2 reveals issues with Phase 1, announce and update
