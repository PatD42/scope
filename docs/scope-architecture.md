# SCOPE - Simple Claude Orchestrator for Product Engineering

**Status:** Implementation

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. File Structure](#2-file-structure)
- [3. User Workflow](#3-user-workflow)
- [4. Commands](#4-commands)
- [5. Agents](#5-agents)
- [6. Skills](#6-skills)
- [7. Core Concepts](#7-core-concepts)
- [8. Epic Lifecycle](#8-epic-lifecycle)
- [9. Documentation Structure](#9-documentation-structure)
- [10. Architectural Decisions](#10-architectural-decisions)

---

## 1. Overview

SCOPE is a Claude Code skill-based framework for epic lifecycle management. It provides slash commands, agent definitions, and documentation skills that turn Claude Code into a structured product engineering environment.

Claude Code is the orchestrator. Commands contain the workflow logic (phases, approval gates, agent sequencing). Tasks are managed via Claude Code's built-in TaskCreate/TaskUpdate/TaskList.

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Commands                             │
│                                                                   │
│   /prd_create [product]    Create first-pass PRD from interview  │
│   /prd_refine [product]    Refine product requirements           │
│   /prd_breakdown           Break PRD into epics                  │
│   /epic_refine {epic-id}   Refine epic (contract-first)          │
│   /implement {epic-id}     Implement (developer writes tests)    │
│   /implement_tdd {epic-id} Implement (SDET writes tests first)   │
│   /audit_epic {epic-id}    Audit implementation                  │
│   /sync_product [epic-id]  Sync product documentation            │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Claude Code (Orchestrator)                      │
│                                                                   │
│   - Executes command workflows step-by-step                      │
│   - Manages tasks via TaskCreate / TaskUpdate / TaskList          │
│   - Spawns agents via Task tool (subagent_type)                  │
│   - Manages git worktrees for implementation                     │
│   - Handles user approval gates                                  │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                   │
              ▼                  ▼                   ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Agent Files     │  │   Skills          │  │   Documentation   │
│                   │  │                   │  │                   │
│   architect       │  │   project-        │  │   docs/product/   │
│   developer       │  │    documentation  │  │   docs/arch/      │
│   sdet            │  │   project-        │  │   docs/epics/     │
│   product-owner   │  │    tracking       │  │   docs/releases/  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 2. File Structure

### 2.1 This Project (SCOPE Repository)

```
scope/
├── src/
│   ├── agents/                             # Agent definitions (7 files)
│   │   ├── architect.md
│   │   ├── developer.md
│   │   ├── sdet.md
│   │   ├── product-owner.md
│   │   ├── reverse-engineer-architect.md
│   │   ├── reverse-engineer-pm.md
│   │   └── REVERSE-ENGINEERING-GUIDE.md
│   │
│   ├── commands/                           # Slash commands
│   │   ├── prd_refine.md
│   │   ├── prd_refine/                    # Supporting resources
│   │   ├── prd_breakdown.md
│   │   ├── prd_breakdown/                 # Supporting resources
│   │   ├── epic_refine.md
│   │   ├── implement.md
│   │   ├── implement_tdd.md
│   │   ├── audit_epic.md
│   │   ├── sync_product.md
│   │   └── config_example.yaml
│   │
│   └── skills/                             # Skills
│       ├── project-documentation/
│       │   ├── SKILL.md                    # Local file-based documentation
│       │   ├── templates-product-atlassian/
│       │   └── templates-technical-arc42-c4/
│       └── project-tracking/
│           ├── SKILL.md                    # Wrapper (dispatches to backend)
│           └── {backend}.md                # Backend implementations
│
└── docs/                                   # Documentation
    ├── scope-architecture.md               # This document
    ├── epic-workflow.md                    # Epic phase-by-phase workflow
    ├── reverse-engineering-guide.md        # Guide for /re_documentation
    └── artifact-structure.md               # Project file structure guidelines
```

### 2.2 Target Project Structure

After installing SCOPE skills into a target project:

```
user-project/
├── .claude/
│   ├── commands/                           # Slash commands (copied from src/commands/)
│   │   ├── prd_refine.md
│   │   ├── prd_breakdown.md
│   │   ├── epic_refine.md
│   │   ├── implement.md
│   │   ├── implement_tdd.md
│   │   ├── audit_epic.md
│   │   └── sync_product.md
│   │
│   ├── agents/                             # Agent definitions (copied from src/agents/)
│   │   ├── architect.md
│   │   ├── developer.md
│   │   ├── sdet.md
│   │   └── product-owner.md
│   │
│   └── skills/                             # Skills (copied from src/skills/)
│       ├── project-documentation/
│       │   ├── SKILL.md
│       │   ├── templates-product-atlassian/
│       │   └── templates-technical-arc42-c4/
│       └── project-tracking/
│           ├── SKILL.md
│           └── {backend}.md
│
├── .scope/
│   └── config.yaml                         # Project configuration
│
├── docs/                                   # Documentation (local files)
│   ├── product/                            # Product documentation
│   ├── architecture/                       # Arc42 technical documentation
│   ├── epics/{epic-id}/                    # Per-epic documentation
│   └── releases/{version}/                 # Release documentation
│
├── wip/                                    # Worktrees for implementation
│   └── {epic-id}/                          # Worktree per epic
│       ├── .git                            # Worktree link
│       └── src/                            # Code changes
│
└── src/                                    # Application source code
```

**Key points:**
- Documentation is always local markdown files in `docs/`
- Implementation happens in git worktrees under `wip/`
- Main branch holds refinement artifacts; worktrees hold implementation
- No `.scope/` runtime state beyond `config.yaml`

---

## 3. User Workflow

The complete product development pipeline:

```
Create PRD draft or run /prd_create
       │
       ▼
/prd_refine [product]          Interactive PRD refinement
       │                       (checklist-driven, discovery updates)
       ▼
/prd_breakdown                 Convert PRD → epics
       │                       (architecture, dependency analysis)
       ▼
/epic_refine {epic-id}         Contract-first epic refinement
       │                       (4 approval gates, contracts.py)
       ▼
┌──────┴──────┐
│             │
▼             ▼
/implement    /implement_tdd   Story-by-story implementation
│             │                (choose one per epic)
└──────┬──────┘
       │
       ▼
/audit_epic {epic-id}          Audit implementation
       │                       (max 2 cycles, then escalate)
       ▼
User merges worktree           Manual merge when satisfied
```

**Supporting commands:**
- `/sync_product [epic-id]` - Sync product docs when implementation changes product scope

---

## 4. Commands

Each command is a self-contained workflow definition in markdown with YAML frontmatter.

| Command | Description | Agents Used | Skills Used |
|---------|-------------|-------------|-------------|
| `/prd_create` | Lightweight interview to create a first-pass PRD | (inline) | project-documentation |
| `/prd_refine` | Interactive PRD refinement with checklist | (inline) | project-documentation |
| `/prd_breakdown` | Convert PRD into implementable epics | (inline) | project-documentation, project-tracking |
| `/epic_refine` | Contract-first epic refinement, 4 gates | product-owner, architect | project-documentation |
| `/implement` | Developer implements + writes tests | architect, developer | project-documentation |
| `/implement_tdd` | TDD: SDET tests first, developer implements | architect, sdet, developer | project-documentation |
| `/audit_epic` | Audit implementation against design | (inline) | project-documentation |
| `/sync_product` | Sync product docs after implementation | (inline) | project-documentation |

### Command Frontmatter

```yaml
---
name: implement
description: Implement an epic story-by-story. Developer implements and writes tests.
args: "{epic-id}"
skills: project-documentation
agents: architect, developer
---
```

- `name` - Slash command name
- `description` - What the command does
- `args` - Expected arguments
- `skills` - Skills the command uses (loaded by agents)
- `agents` - Agent definitions spawned during execution

---

## 5. Agents

Agents are markdown files that define persona, responsibilities, and constraints for Claude Code subagents.

| Agent | File | Role |
|-------|------|------|
| **Architect** | `architect.md` | System design, story breakdown, file plans, ADRs, contracts |
| **Developer** | `developer.md` | Implements stories, writes tests, follows file plan intent |
| **SDET** | `sdet.md` | Writes tests first (TDD mode), test strategy |
| **Product Owner** | `product-owner.md` | Business requirements, acceptance criteria, PDRs |
| **RE Architect** | `reverse-engineer-architect.md` | Reverse-engineer architecture from existing code |
| **RE PM** | `reverse-engineer-pm.md` | Reverse-engineer product requirements from existing code |

### Agent Spawning

Claude Code spawns agents via the Task tool:

```
Task(
  prompt: "Implement story 3 for epic SCOPE-42. File plan: ...",
  subagent_type: "general-purpose"
)
```

The command workflow controls sequencing:
- **Story 0:** Architect scaffolds (contracts.py, shared modules)
- **Stories 1-N:** Developer implements (or SDET → Developer in TDD mode)
- **Fix stories:** Architect creates fix stories after audit, developer implements

### Agent Constraints

- **One agent per story** - No splitting implementation across agents
- **Single developer agent** - Prevents concurrent worktree write conflicts
- **Sequential SDET** (TDD mode) - SDET tasks are sequential to prevent test conflicts
- **Agents read, not write, documentation** - Developer reads docs but doesn't write to docs/ (writes code only)

---

## 6. Skills

### 6.1 Project Documentation

**File:** `src/skills/project-documentation/SKILL.md`

Local markdown files in `docs/`. The skill defines:
- Folder structure (`docs/product/`, `docs/architecture/`, `docs/epics/`, `docs/releases/`)
- Operations: `read(path)`, `write(path, content)`, `search(pattern)`, `list(path)`
- Templates for product docs (Atlassian Blueprint pattern) and technical docs (Arc42+C4)

**Configuration:**
```yaml
# .scope/config.yaml
documentation:
  root: ./docs
```

### 6.2 Project Tracking

**File:** `src/skills/project-tracking/SKILL.md`

Wrapper skill that dispatches to a configured backend. Supports:
- Local file-based tracking
- Jira (Atlassian MCP or Sooperset MCP)
- GitHub issues

**Configuration:**
```yaml
# .scope/config.yaml
tracking:
  skill: project-tracking-file   # or jira-atlassian-mcp, jira-sooperset-mcp
```

**Note:** Project tracking is optional. Many commands work without it. The documentation skill is the primary requirement.

---

## 7. Core Concepts

### 7.1 Contract-First Development

**Problem:** File plans with method signatures in YAML prose lead to integration failures hidden by mocks.

**Solution:**
- Story 0 creates `contracts.py` with Python Protocol classes
- Method signatures are executable code, not YAML descriptions
- `mypy --strict` catches interface mismatches statically after each story
- File plans reference contracts as source of truth for cross-story calls

**Flow:**
```
/epic_refine → Story 0 (architect creates contracts.py)
                  → Story 1 (developer implements against contracts)
                  → mypy --strict (verifies interface compliance)
                  → Story 2 ...
```

### 7.2 Git Worktrees

Implementation happens in git worktrees, not on the main branch.

```
/implement {epic-id}
  → Creates worktree at wip/{epic-id} on branch epic/{epic-id}
  → All stories implemented in the worktree
  → User merges when satisfied with quality
  → Worktree NOT cleaned up automatically (user decides when to merge/remove)
```

### 7.3 Built-In Task Management

Claude Code provides TaskCreate, TaskUpdate, TaskList tools that replace the need for custom plan schemas and state management.

**Implementation commands use tasks like:**
```
TaskCreate(subject: "architect-story-0", description: "Scaffold shared modules...")
TaskCreate(subject: "dev-story-1", description: "Implement authentication...")
TaskUpdate(taskId: "1", addBlockedBy: ["0"])  # story-1 blocked by story-0
```

### 7.4 Story Sizing

| Constraint | Value |
|-----------|-------|
| Max non-trivial files per story | 7 |
| Target LOC per story | ~600 |
| Stories per epic | 5-8 |
| File plan intent length | 600-1200 chars (5-part template) |

### 7.5 Inter-Story Dependencies

Parsed from `# Dependencies:` comments in file plan headers. Commands read these and set up TaskUpdate `addBlockedBy` relationships.

### 7.6 Test-as-Soon-as-Possible

Write tests at the earliest point where the test becomes possible:
- **Unit tests:** Always in each story
- **Integration tests:** When component integration exists in that story
- **E2E tests:** When user flow completes in that story

### 7.7 Cross-Epic Test Evolution

Tests evolve progressively across epics rather than being written all at once:
```
Epic 1: user_lifecycle_journey.test.ts
  ✅ User logs in → ✅ User sees dashboard → 🔵 Future → ✅ User logs out

Epic 2 (extends):
  ✅ User logs in → ✅ User sees dashboard → ✅ User updates profile → ✅ User logs out
```

Tests organized by user journey, not by epic.

### 7.8 Production-Ready Code Rules

- File plan intent is the source of truth for what a file does
- No stubs, placeholders, or TODO implementations
- No mock-only code that passes tests but fails integration
- Fail-fast: no fallbacks or hardcoded values masking bugs

### 7.9 Audit Loop Guard

`/audit_epic` runs at most 2 cycles (initial audit + one fix cycle). If issues remain after 2 cycles, the command escalates to the user rather than looping. Fix stories are created for ALL findings (critical, major, and minor).

### 7.10 Context Window Optimization

- Agent files loaded at session start are in high-attention area
- Commands keep agent prompts minimal (epic_id + phase + task description)
- Agents fetch documentation on demand via direct file paths
- Progressive disclosure: parent files link to details, agents load only what's needed

---

## 8. Epic Lifecycle

### 8.1 Refinement (`/epic_refine`)

Contract-first epic refinement with 4 approval gates:

```
Phase 1: Product Owner validates epic
  → Acceptance criteria, error scenarios, e2e test scenarios
  → USER APPROVAL GATE #1

Phase 2: Architect analyzes system context
  → Technical risks, affected components, ADRs
  → USER APPROVAL GATE #2

Phase 3: Architect generates technical specifications
  → API contracts, schemas in docs/architecture/13-specs/
  → USER APPROVAL GATE #3

Phase 4: Story breakdown
  → File plans per story with intent documentation
  → contracts.py with Protocol classes (Story 0)
  → Story sizing constraints enforced
  → USER APPROVAL GATE #4
```

**Output:** Per-story file plans (`file-plan-story-*.yaml`), `contracts.py`, acceptance criteria, architecture docs, ADRs

### 8.2 Implementation (`/implement` or `/implement_tdd`)

**`/implement` (non-TDD):**
```
Story 0: Architect scaffolds (contracts.py, shared modules)
Story 1-N: Developer implements + writes tests
  → Each story: read file plan → implement → run tests → mypy --strict
After all stories: Epic-wide lint (ruff + vulture + mypy)
```

**`/implement_tdd`:**
```
Story 0: Architect scaffolds (contracts.py, shared modules)
Story 1-N:
  SDET writes tests first (from file plan + acceptance criteria)
    → Developer implements to make tests pass
  → Each story: mypy --strict verification
After all stories: Epic-wide lint (ruff + vulture + mypy)
```

**Orchestration:** Claude Code uses TaskCreate to create tasks for each story with proper `addBlockedBy` dependencies, then processes them in order.

### 8.3 Audit (`/audit_epic`)

7 audit phases:
1. Architecture compliance
2. ADR compliance
3. Acceptance criteria coverage
4. Auto Claude spec alignment
5. Code quality
6. Stub/placeholder detection
7. Lint & contract compliance (mypy --strict)

**Output:** `docs/epics/{epic-dir}/epic_audit.md`

**Post-audit loop:**
1. Architect creates fix stories from ALL audit findings (critical, major, minor)
2. Developer implements fixes
3. Final audit (max 2 cycles total, then escalate)

### 8.4 Supporting Operations

- **`/sync_product`** - When implementation reveals product-level changes (new capabilities, terminology changes, scope shifts), updates `docs/product/` accordingly

---

## 9. Documentation Structure

Documentation uses two complementary standards:

### Product Documentation (Atlassian Blueprint Pattern)

```
docs/product/
├── overview.md               # Auto-generated parent with links
├── strategy.md               # Vision, markets, problems, scope
├── definition.md             # Use cases, capability map
├── reference/
│   ├── feature-catalog.md    # Features with status, priority, release
│   ├── terminology.md        # Domain terms, key entities
│   ├── ux-workflows.md       # Navigation, screens, workflows
│   └── apis-integrations.md  # External integrations
└── decisions.md              # Product Decision Records (PDR)
```

### Technical Documentation (Arc42 + C4)

```
docs/architecture/
├── 01-intro.md               # System purpose, stakeholders, quality goals
├── 02-constraints.md         # Technical, organizational constraints
├── 03-context.md             # C4 L1 context diagram
├── 04-strategy.md            # Solution approach, technology decisions
├── 05-building-blocks.md     # C4 L2/L3 component diagrams
├── 06-runtime.md             # Key scenarios, sequence diagrams
├── 07-deployment.md          # Infrastructure, deployment
├── 08-cross-cutting/         # Domain, security, operations, testing
├── 09-adr-summary.md         # Architecture Decision Records
├── 10-quality.md             # Quality requirements
├── 11-risks.md               # Risks, technical debt
├── 12-glossary.md            # Architecture terms
├── 13-specs/                 # System API contracts, schemas, database specs
│   ├── api/
│   ├── schemas/              # Schemas live here; do not create 14-schema
│   ├── database/
│   └── errors/
├── backend/                  # Backend-specific Arc42 01-13 tree
│   ├── 01-intro.md
│   ├── 02-constraints.md
│   ├── 03-context.md
│   ├── 04-strategy.md
│   ├── 05-building-blocks.md
│   ├── 06-runtime.md
│   ├── 07-deployment.md
│   ├── 08-cross-cutting/
│   ├── 09-adr-summary.md
│   ├── 10-quality.md
│   ├── 11-risks.md
│   ├── 12-glossary.md
│   ├── 13-specs/
│   └── adr/
└── frontend/                 # Frontend-specific Arc42 01-13 tree
    ├── 01-intro.md
    ├── 02-constraints.md
    ├── 03-context.md
    ├── 04-strategy.md
    ├── 05-building-blocks.md
    ├── 06-runtime.md
    ├── 07-deployment.md
    ├── 08-cross-cutting/
    ├── 09-adr-summary.md
    ├── 10-quality.md
    ├── 11-risks.md
    ├── 12-glossary.md
    ├── 13-specs/
    └── adr/
```

`13-specs/` is the canonical location for machine-readable contracts: OpenAPI,
JSON/YAML schemas, database specs, queue/message specs, and error contracts.
Do not create a separate `14-schema`; schemas belong in `13-specs/schemas/`.

Legacy component docs may exist in older projects:
`backend/overview.md`, `backend/services.md`, `backend/data.md`,
`frontend/overview.md`, `frontend/structure.md`, and `frontend/patterns.md`.
Read them as context when present, but do not create or extend them. New or
updated backend/frontend documentation uses the component `01-intro.md` through
`13-specs/` tree.

### Epic Documentation

```
docs/epics/{epic-id}/
├── details.md                # Overview, capabilities, acceptance criteria
├── system-context.md         # Technical analysis, risks
├── acceptance-criteria.md    # Given/When/Then testable criteria
├── test-strategy.md          # Test approach, levels, mocking
├── architecture.md           # Affected components, C4 diagrams
├── adr.md                    # Architectural decisions for this epic
├── pdr.md                    # Product decisions for this epic
├── file-plan.yaml            # Story breakdown with intent
└── implementation-summary.md # Post-implementation outcomes
```

### Agent Documentation Responsibilities

| Agent | Writes | Reads |
|-------|--------|-------|
| **Product Owner** | product/*, epics/*/details, acceptance-criteria, pdr | architecture/10-quality |
| **Architect** | architecture/*, epics/*/system-context, test-strategy, architecture, adr, file-plan | product/strategy, product/definition |
| **SDET** | (none) | product/definition, architecture/06-runtime, 10-quality, 08-cross-cutting/testing, epics/* |
| **Developer** | (code only, not docs) | architecture/08-cross-cutting/*, epics/*/adr (if unclear) |

---

## 10. Architectural Decisions

### 10.1 Claude Code as Orchestrator

Commands are self-contained workflows. Claude Code executes them step-by-step, manages tasks via TaskCreate/TaskUpdate/TaskList, and spawns agents via the Task tool. No separate orchestrator agent, planner, or execution engine.

### 10.2 Contract-First over Prose Descriptions

Epic refinement produces executable `contracts.py` with Python Protocol classes. `mypy --strict` catches interface mismatches statically. Agents implement against machine-verifiable contracts, not YAML prose.

### 10.3 Local Files for Documentation

Documentation is always local markdown files in `docs/`. Files are in git alongside code. Agents read/write directly. Follows Arc42+C4 and Atlassian Blueprint patterns for structure.

### 10.4 Two Implementation Modes

`/implement` (developer writes code + tests) for straightforward features. `/implement_tdd` (SDET writes tests first, developer implements) for complex integration scenarios. User chooses per epic.

### 10.5 One Agent Per Story

A single agent implements the complete story. Splitting across agents creates context coordination complexity. Story boundaries align with technical component boundaries.

### 10.6 Test-as-Soon-as-Possible

Tests are written at the earliest possible point, not deferred to epic end. Fixing issues in closed stories is expensive (context lost). Early testing catches issues while context is fresh.

### 10.7 Architect-Led Story Breakdown

Architect leads story breakdown; Product Owner validates business alignment. Technical boundaries drive story structure (component alignment, dependencies).

### 10.8 File Plan Intent Documentation

Each file in the plan has a 600-1200 character intent with 5-part structure:

1. **WHAT** (~100 chars): Core functionality
2. **WHY** (~150-250 chars): Architectural purpose
3. **RESPONSIBILITIES** (~150-250 chars): Key functions (3-5)
4. **DEPENDENCIES** (~100-150 chars): Module dependencies
5. **RELATED MODULES** (~100-150 chars): Positive delegation

Use positive delegation ("session encryption via SessionStore") instead of negation ("Does NOT handle encryption") to avoid confusing semantic search routing.
