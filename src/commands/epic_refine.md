---
name: epic_refine
description: Single-session epic refinement from discovery to specs. Simplified alternative to multi-agent orchestration. Output feeds Auto Claude.
args: "{epic-id}"
skills: project-documentation, session-id-finder, agent-summary
agents: product-owner, architect
---

# /epic_refine

Single-session epic refinement with 3 approval gates. Simpler alternative to workplan/workflow/multi-agent orchestration.

**Syntax:** `/epic_refine {epic-id}`

## Why This Command

Auto Claude handles much of what multi-agent refinement was doing:
- Library verification and research
- Self-critique and validation
- Implementation planning

This command focuses on what humans + single agent do best:
- Business discovery and acceptance criteria (PO role)
- System context and architecture design (Architect role)
- Technical specs for Auto Claude consumption

**Key approach:** Instead of spawning separate agents, take the role of existing agents (`product-owner`, `architect`) which contain detailed phase-specific instructions. This keeps agent knowledge centralized while simplifying orchestration.

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
│ - Generate specs in 13-specs/ for Auto Claude           │
│ ──────────────────────────────────────────────────────  │
│ → USER APPROVAL GATE #3                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Continue as architect (story_breakdown +       │
│          file_plan)                                     │
│ - Break epic into implementable user stories            │
│ - Create file plan with intent + class/method signatures│
│ ──────────────────────────────────────────────────────  │
│ → USER APPROVAL GATE #4                                 │
│ → Mark epic "ready-for-implementation"                  │
└─────────────────────────────────────────────────────────┘
```

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
- Error scenarios (for 13-specs/errors/ generation)
- E2E test scenarios
- Written to `docs/epics/{epic-dir}/acceptance-criteria.md`

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
- ADRs for key technology decisions
- Test strategy (boundaries, test data, mocking)
- Written to:
  - `docs/epics/{epic-dir}/system-context.md`
  - `docs/epics/{epic-dir}/architecture.md`
  - `docs/epics/{epic-dir}/adr.md`
  - `docs/epics/{epic-dir}/test-strategy.md`

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

**Instruction:** Continue as `architect` agent for the `spec_generation` phase.

**Goal:** Generate technical specifications for Auto Claude consumption.

**Phase context to pass:**
```
epic_id: {epic-id}
phase: spec_generation
agent_summaries: .scope/{epic-dir}/agent_summaries.jsonl
```

**Key deliverables:**
- API contracts in `13-specs/api/` (OpenAPI 3.0.3)
- Domain schemas in `13-specs/schemas/domain/` (JSON Schema)
- Error codes in `13-specs/errors/by-domain/`
- Updated error taxonomy in `13-specs/errors/taxonomy.yaml`

### Phase 3 Checklist

Present to user:

```
Phase 3: Architect - Spec Generation

✅ API Contracts (13-specs/api/)
   Endpoints defined: [N endpoints]
   Files created: [list]

✅ Domain Schemas (13-specs/schemas/domain/)
   Entities defined: [N entities]
   Files created: [list]

✅ Error Codes (13-specs/errors/)
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

## Phase 4: Architect (story_breakdown + file_plan)

**Instruction:** Continue as `architect` agent for the `story_breakdown` and `file_plan` phases.

**Goal:** Break epic into implementable stories and document file-level intent with class/method signatures.

**Phase context to pass:**
```
epic_id: {epic-id}
phase: story_breakdown  # then file_plan
agent_summaries: .scope/{epic-dir}/agent_summaries.jsonl
```

**Key deliverables:**

**Story breakdown:**
- User stories with acceptance criteria, test requirements, dependencies
- Stories sequenced for early testing (unit → integration → e2e)
- Written to tracking system + `docs/epics/{epic-dir}/acceptance-criteria.md`

**File plan (one per story):**
- Intent documentation per file (600-1200 chars, 5-part template)
- `public_interface` for new files (class/method signatures)
- `signature_changes` for modified files (before/after with breaking_change flag)
- Written to `docs/epics/{epic-dir}/file-plan-story-NN.yaml` (pure YAML, one per story)

### Phase 4 Checklist

Present to user:

```
Phase 4: Architect - Stories & File Plan

✅ Story Breakdown
   Stories created: [N stories]
   Dependency order: [Story sequence]
   Test enablement: [When each test type becomes possible]

✅ File Plan
   New files: [N files with intent + public_interface]
   Modified files: [N files with intent + signature_changes]
   Breaking changes: [N breaking changes flagged]

✅ Coverage
   All stories mapped to files: [Yes / No]
   All acceptance criteria traceable: [Yes / No]

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

**If user wants refinement**: Address concerns, update stories/file plan, re-present checklist

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
│   ├── test-strategy.md
│   ├── file-plan-story-00.yaml
│   ├── file-plan-story-01.yaml
│   └── file-plan-story-NN.yaml
├── 13-specs/
│   ├── api/{epic-id}-*.yaml
│   ├── schemas/domain/{epic-id}-*.json
│   └── errors/by-domain/{epic-id}.yaml
└── Tracking system
    └── [N] stories created with AC and dependencies

Status: ready-for-implementation
Cost: $X.XX

Next: Run Auto Claude with this epic for implementation.
```

---

## Compaction Survival

**State is tracked in artifacts, not conversation memory.**

If session compacts mid-refinement:

1. Check `.scope/{epic-dir}/refine_summaries.jsonl` for completed phases
2. Check which epic docs exist:
   - `acceptance-criteria.md` exists → Phase 1 complete
   - `architecture.md` exists → Phase 2 complete
   - `13-specs/api/{epic-id}-*` exists → Phase 3 complete
   - `file-plan-story-*.yaml` exists → Phase 4 complete
3. Resume from appropriate phase

---

## Communication Style

**Progress indicators:**
- "Phase 1/4: Product Owner - Epic Validation"
- "Phase 2/4: Architect - System Context & Architecture"
- "Phase 3/4: Architect - Spec Generation"
- "Phase 4/4: Architect - Stories & File Plan"

**Approval gates:**
- Present checklist summary
- Ask specific question: "Ready to proceed? [yes / refine]"
- Wait for explicit approval before proceeding

**Discovery updates:**
- If Phase 2 reveals issues with Phase 1, announce and update
- "🔄 Discovery: Found missing error scenario, updating acceptance criteria"

---

## Example Session

```
User: /epic_refine EPIC-123
Assistant: Starting epic refinement for EPIC-123: User Authentication Flow

Phase 1/3: Product Owner - Epic Validation

Loading epic details... I see this epic is about adding OAuth2 authentication.

A few clarifying questions:
1. Which OAuth providers should we support initially?
2. Should we support "remember me" functionality?
3. What happens if OAuth fails - fallback to email/password?

User: Google and GitHub for now. Yes to remember me. No fallback, OAuth only.

Assistant: Got it. Writing acceptance criteria...

[... interactive refinement continues ...]

Phase 1: Product Owner - Epic Validation

✅ Epic Details
   Business value: Clear - reduce signup friction
   User stories: 3 stories defined
   Scope: Well-bounded - OAuth only, no email/password

✅ Acceptance Criteria
   Happy path scenarios: 4 scenarios
   Edge cases: 3 cases
   Error scenarios: 5 scenarios

✅ Test Scenarios
   E2E scenarios: 6 scenarios defined

Ready to proceed to architecture? [yes / refine]

User: yes

Assistant: Phase 2/4: Architect - System Context & Architecture
...
```
