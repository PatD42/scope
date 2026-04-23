---
name: epic_refine
description: Contract-first epic refinement. Produces executable Python contracts alongside file plans. Output feeds /implement or /implement_tdd.
args: "{epic-id}"
skills: project-documentation, session-id-finder, agent-summary
agents: product-owner, architect
---

# /epic_refine

Contract-first epic refinement with 4 approval gates. Produces executable Python Protocol contracts that agents verify via mypy — not just prose descriptions.

**Syntax:** `/epic_refine {epic-id}`

## Why Contract-First

The previous approach produced file plans with method signatures in YAML prose. Agents implemented against these descriptions, but nothing machine-verified that components could actually call each other. Result: 81 tests pass, 5 critical integration failures hidden by mocks.

**Contract-first** means:
- Story 0 creates `contracts.py` with Python Protocol classes
- Method signatures are executable code, not YAML descriptions
- `mypy --strict` catches interface mismatches statically after each story
- File plans reference contracts as source of truth for cross-story calls

**Key insight:** Agents need machine-verifiable contracts, not human-readable descriptions. TDD with mocks tests behavior in isolation; contracts + static analysis verifies integration mechanically.

## Epic Artifact Rules

These rules are mandatory for every refined epic:

- `contracts.py` belongs in the source package for the epic's implementation, never under `docs/epics/...`.
- The epic documentation folder may contain only `.md` and `.yaml` files.
- Required epic artifacts:
  - `details.md`
  - `acceptance-criteria.md`
  - `system-context.md`
  - `architecture.md`
  - `adr.md`
  - `pdr.md`
  - `test-strategy.md`
- `details.md` must use YAML frontmatter with at least `epic_id`, `title`, and `status`.
- `adr.md` must use the global ADR numbering sequence and include `Date`, `Status`, `Scope`, `Epic`, `Context`, `Decision`, `Alternatives Considered`, and `Consequences` for every ADR entry.

Do not pass a phase if these artifact rules are not satisfied by the work completed so far.

## Workflow Overview

```
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
│ ──────────────────────────────────────────────────────  │
│ → USER APPROVAL GATE #3                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Continue as architect (story_breakdown +       │
│          file_plan + contracts)                         │
│ - Break epic into implementable user stories            │
│ - Create contracts.py with Protocol classes             │
│ - Create file plans with cross-story call references    │
│ ──────────────────────────────────────────────────────  │
│ → USER APPROVAL GATE #4                                 │
│ → Mark epic "ready-for-implementation"                  │
└─────────────────────────────────────────────────────────┘
```

## Phase Handoff Rule

Do not pass a phase by "good enough" intuition. A phase passes only when downstream roles can execute without inventing missing decisions:
- Phase 1 is not complete until the Product Owner has specified the business behavior in enough detail that neither the Architect nor the Developer would need to make product, policy, scope, workflow, or acceptance decisions during later phases.
- If the Architect would need to choose what the business wants, or the Developer would need to choose what behavior is correct, then the business requirements are incomplete.
- In that case, the Product Owner must interview the user in a semi-structured approach to complete the business requirements in enough details before proceeding.
- Phases 2-4 are not complete until the architecture is detailed enough that the Developer would not need to make architecture decisions during implementation.
- If the Developer must decide how the system should be designed, refinement was incomplete and must return to the Architect before implementation begins.

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

# Get session ID for cost tracking
SESSION_ID=$(skill session-id-finder)

# Write baseline entry
echo '{"agent":"baseline","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' > "$SUMMARIES_FILE"
```

### Step 1: Load Epic Context

1. Read `docs/epics/{epic-dir}/details.md` to understand epic
2. Read product documentation:
   - `docs/product/strategy.md` - strategic context
   - `docs/product/definition.md` - use cases, capabilities
   - `docs/product/reference/terminology.md` - domain terms
3. Announce: "Starting epic refinement for {epic-id}: {epic-title}"

---

## Phase 1: Product Owner (epic_validation)

**Instruction:** Take the role of `product-owner` agent for the `epic_validation` phase.

**Goal:** Validate epic and define business requirements.

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

### Phase 1 Checklist

Present to user:

```
Phase 1: Product Owner - Epic Validation

✅ Epic Details
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
- Source placement rule for `contracts.py` documented in the file plans and epic architecture:
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
   Docs to create: [list new files, e.g., backend/data.md]
   ADR roll-up needed: [Yes / No]

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

**Instruction:** Continue as `architect` agent for the `spec_generation` phase. Create the `docs/architecture/13-specs/` subdirectories if they don't exist yet.

**Goal:** Generate technical specifications in `docs/architecture/13-specs/`. This is the canonical location — all specs live under `docs/architecture/13-specs/`, not in the project root.

**Phase context to pass:**
```
epic_id: {epic-id}
phase: spec_generation
agent_summaries: .scope/{epic-dir}/agent_summaries.jsonl
specs_dir: docs/architecture/13-specs
```

**Key deliverables:**
- API contracts in `docs/architecture/13-specs/api/` (OpenAPI 3.0.3)
- Domain schemas in `docs/architecture/13-specs/schemas/domain/` (JSON Schema)
- Error codes in `docs/architecture/13-specs/errors/by-domain/`
- Updated error taxonomy in `docs/architecture/13-specs/errors/taxonomy.yaml`

### Phase 3 Checklist

Present to user:

```
Phase 3: Architect - Spec Generation

✅ API Contracts (docs/architecture/13-specs/api/)
   Endpoints defined: [N endpoints]
   Files created: [list]

✅ Domain Schemas (docs/architecture/13-specs/schemas/domain/)
   Entities defined: [N entities]
   Files created: [list]

✅ Error Codes (docs/architecture/13-specs/errors/)
   Error codes defined: [N codes]
   Taxonomy updated: [Yes / No]

Ready to proceed to story breakdown? [yes / refine]
```

### Approval Gate #3

**If user approves**: Write summary entry and proceed to Phase 4

```bash
echo '{"agent":"architect","session_id":"'"$SESSION_ID"'","phase":"spec_generation","status":"success","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' >> "$SUMMARIES_FILE"
```

**If user wants refinement**: Address concerns, update specs, re-present checklist

---

## Phase 4: Architect (story_breakdown + file_plan + contracts)

**Instruction:** Continue as `architect` agent for the `story_breakdown`, `file_plan`, and `contracts` phases.

**Goal:** Break epic into implementable stories, create executable contracts, and document file-level intent.

**Story sizing constraints:** Each story should have max 7 non-trivial files, ~600 LOC of new/modified code, and the epic should have 5-8 stories. Trivial files (empty `__init__.py`, config with no logic, re-exports) don't count toward the 7-file limit. If a story exceeds these limits, split it.

**Story numbering rule:** Story 0 is reserved for epic scaffolding only. Create Story 0 only if the epic genuinely has scaffolding work such as contracts, config content, schemas with authored examples, prompts, or directory/module scaffolding that should be authored before developer implementation. If there is no scaffolding story, numbering starts at Story 1.

**Phase context to pass:**
```
epic_id: {epic-id}
phase: story_breakdown  # then file_plan, then contracts
agent_summaries: .scope/{epic-dir}/agent_summaries.jsonl
```

**Key deliverables:**

### Story breakdown

- User stories with acceptance criteria, test requirements, dependencies
- Stories sequenced for incremental delivery
- Written to tracking system + `docs/epics/{epic-dir}/acceptance-criteria.md`

### Story 0 extraction (CRITICAL — do this BEFORE writing file plans)

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

### File plan (one per story)

- Intent documentation per file (600-1200 chars, 5-part template)
- `public_interface` for new files (class/method signatures)
- `signature_changes` for modified files (before/after with breaking_change flag)
- **`calls` section for files that invoke other stories' components** ← NEW
- Written to `docs/epics/{epic-dir}/file-plan-story-NN.yaml` (pure YAML, one per story)

### File plan `calls` section (CRITICAL — new requirement)

When a file plan entry describes a file that CALLS methods from another story's components, include an explicit `calls` section. This is the machine-readable cross-reference that prevents signature mismatches.

**Example:**
```yaml
modified_files:
  - path: "src/documentation/updater.py"
    intent: |
      WHAT: Add re_render_entity() orchestration method.
      WHY: Coordinates IntelAggregator → KnowledgeSynthesizer → TemplateReRenderer per file.
      ...
    calls:
      - target: "IIntelAggregator.aggregate_for_file"
        contract: "contracts.py"
        signature: "aggregate_for_file(entity_id: str, file_config: dict) -> Dict[str, AggregatedSignals]"
      - target: "IKnowledgeSynthesizer.synthesize"
        contract: "contracts.py"
        signature: "synthesize(file_name: str, section_signals: Dict[str, AggregatedSignals], entity_id: str) -> Optional[SynthesisResult]"
      - target: "ITemplateReRenderer.render_file"
        contract: "contracts.py"
        signature: "render_file(template_name: str, context: dict, entity_slug: str, entity_config: EntityConfig) -> ReRenderResult"
```

**Rule:** If a file has a `calls` section, the developer MUST verify each call matches the exact signature listed. mypy enforces this when the implementation type-hints dependencies using Protocol types from contracts.py.

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
- no `__pycache__`, `.py`, `.pyc`, `.DS_Store`, or other non-markdown/non-YAML artifacts exist in the epic docs folder
- all required epic files exist
- `details.md` frontmatter is present and contains at least `epic_id`, `title`, and `status`
- `adr.md` uses global ADR numbering and includes the required template fields
- at least one `file-plan-story-*.yaml` exists

### Phase 4 Checklist

Present to user:

```
Phase 4: Architect - Stories, Contracts & File Plan

✅ Story Breakdown
   Stories created: [N stories]
   Dependency order: [Story sequence]

✅ Contracts (contracts.py)
   Protocol classes: [N protocols defined]
   Cross-story interfaces: [List of class names]
   All types importable: [Yes / No]

✅ File Plan
   New files: [N files with intent + public_interface]
   Modified files: [N files with intent + signature_changes]
   Cross-story calls documented: [N call references]
   Breaking changes: [N breaking changes flagged]

✅ Coverage
   All stories mapped to files: [Yes / No]
   All acceptance criteria traceable: [Yes / No]
   All cross-story calls have contracts: [Yes / No]

✅ Epic Artifact Validation
   Required epic files present: [Yes / No]
   details.md frontmatter valid: [Yes / No]
   adr.md numbering/template valid: [Yes / No]
   Epic folder hygiene valid: [Yes / No]

Ready to mark epic as ready-for-implementation? [yes / refine]
```

### Approval Gate #4

**If user approves**:

1. Write summary entry
2. Update epic status to "ready-for-implementation"
3. Calculate and output costs

```bash
# Write completion entry
echo '{"agent":"architect","session_id":"'"$SESSION_ID"'","phase":"file_plan","status":"success","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' >> "$SUMMARIES_FILE"

# Update epic status in details.md frontmatter
# status: ready-for-implementation

# Calculate costs
SCRIPT=$(find ./.claude/commands/scripts ~/.claude/commands/scripts -name "agents-tokens.sh" 2>/dev/null | head -1)
if [ -n "$SCRIPT" ]; then
    $SCRIPT --aggregate "$SUMMARIES_FILE" --storeInSummaries
fi
```

**If user wants refinement**: Address concerns, update stories/file plan/contracts, re-present checklist

---

## Completion Output

```
Epic Refinement Complete: {epic-id}

Artifacts created:
├── docs/epics/{epic-dir}/
│   ├── acceptance-criteria.md
│   ├── system-context.md
│   ├── architecture.md
│   ├── adr.md
│   ├── pdr.md
│   ├── test-strategy.md
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
Cross-story calls documented: [N] call references in file plans

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
   - `acceptance-criteria.md` exists → Phase 1 complete
   - `architecture.md` exists → Phase 2 complete
   - `docs/architecture/13-specs/api/{epic-id}-*` exists → Phase 3 complete
   - `file-plan-story-*.yaml` exists → Phase 4 complete
3. Resume from appropriate phase

---

## Communication Style

**Progress indicators:**
- "Phase 1/4: Product Owner - Epic Validation"
- "Phase 2/4: Architect - System Context & Architecture"
- "Phase 3/4: Architect - Spec Generation"
- "Phase 4/4: Architect - Stories, Contracts & File Plan"

**Approval gates:**
- Present checklist summary
- Ask specific question: "Ready to proceed? [yes / refine]"
- Wait for explicit approval before proceeding

**Discovery updates:**
- If Phase 2 reveals issues with Phase 1, announce and update
