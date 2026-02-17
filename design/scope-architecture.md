# SCOPE - Simple Claude Orchestrator & Persistence Engine

**Version:** 3.0
**Date:** February 2026
**Status:** Implementation

## Version History

- **3.0** (February 2026) - Major simplification: removed orchestrator, planners, plan schemas, state management, install scripts. Claude Code 2.1.16+ is the orchestrator via slash commands and built-in task management. Contract-first development with executable Python Protocol contracts. Two implementation modes: TDD (SDET + developer) and non-TDD (developer only). Documentation always local files. Max 2 audit cycles with escalation.
- **2.6** (January 2026) - TDD workflow refinement, developer autonomous test execution, file plan intent documentation
- **2.5** (December 2025) - Wrapper skill pattern, minimal agent prompts, Atlassian MCP backends
- **2.4** (December 2025) - Removed test-engineer agent, architect-led story breakdown
- **2.0-2.3** - Initial SCOPE architecture through Rovo MCP integration

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

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Commands                             │
│                                                                   │
│   /prd_refine [product]    Refine product requirements           │
│   /prd_breakdown           Break PRD into epics                  │
│   /epic_refine {epic-id}   Refine epic (contract-first)          │
│   /implement {epic-id}     Implement (developer writes tests)    │
│   /implement_tdd {epic-id} Implement (SDET writes tests first)   │
│   /audit_epic {epic-id}    Audit implementation                  │
│   /create {type} {desc}    Create epic/story/task/bug            │
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
│                                                                   │
│   Does NOT require:                                               │
│   - Custom orchestrator agent                                    │
│   - Plan schemas or state files                                  │
│   - Install scripts                                              │
│   - External MCP servers for documentation                       │
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

**Key design change from v2.x:** Claude Code itself is the orchestrator. Commands contain the workflow logic (phases, approval gates, agent sequencing). No separate orchestrator agent, planner routing, or plan execution engine exists.

---

## 2. File Structure

### 2.1 This Project (SCOPE Repository)

```
scope/                                      # This repo
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
│   ├── commands/                           # Slash commands (8 files)
│   │   ├── prd_refine.md
│   │   ├── prd_breakdown.md
│   │   ├── epic_refine.md
│   │   ├── implement.md
│   │   ├── implement_tdd.md
│   │   ├── audit_epic.md
│   │   ├── create.md
│   │   └── sync_product.md
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
└── design/                                 # This directory
    ├── scope-architecture.md               # This document
    ├── scope-product-atlassian.md          # Product documentation standard
    ├── scope-technical-arc42-c4.md         # Technical documentation standard
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
│   │   ├── create.md
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
Create PRD draft
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
- `/create {type} {desc}` - Create epic/story/task/bug via product-owner agent
- `/sync_product [epic-id]` - Sync product docs when implementation changes product scope

---

## 4. Commands

Each command is a self-contained workflow definition in markdown with YAML frontmatter.

| Command | Description | Agents Used | Skills Used |
|---------|-------------|-------------|-------------|
| `/prd_refine` | Interactive PRD refinement with checklist | (inline) | project-documentation |
| `/prd_breakdown` | Convert PRD into implementable epics | (inline) | project-documentation, project-tracking |
| `/epic_refine` | Contract-first epic refinement, 4 gates | product-owner, architect | project-documentation |
| `/implement` | Developer implements + writes tests | architect, developer | project-documentation |
| `/implement_tdd` | TDD: SDET tests first, developer implements | architect, sdet, developer | project-documentation |
| `/audit_epic` | Audit implementation against design | (inline) | project-documentation |
| `/create` | Create epic/story/task/bug interactively | product-owner | project-documentation, project-tracking |
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

Introduced in v3.0 via `/epic_refine`.

**Problem:** File plans with method signatures in YAML prose led to integration failures hidden by mocks. 81 tests pass, 5 critical integration failures.

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

Claude Code 2.1.16+ provides TaskCreate, TaskUpdate, TaskList tools that replace the need for custom plan schemas and state management.

**Implementation commands use tasks like:**
```
TaskCreate(subject: "architect-story-0", description: "Scaffold shared modules...")
TaskCreate(subject: "dev-story-1", description: "Implement authentication...")
TaskUpdate(taskId: "1", addBlockedBy: ["0"])  # story-1 blocked by story-0
```

This eliminates:
- Plan JSON schemas (`refine-plan.json`, `impl-plan.json`)
- State files (`current_state.json`)
- Custom execution loops
- Agent summary JSONL files

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

`/audit_epic` runs at most 2 cycles (initial audit + one fix cycle). If issues remain after 2 cycles, the command escalates to the user rather than looping.

### 7.10 Context Window Optimization

- Agent files loaded at session start are in high-attention area
- Commands keep agent prompts minimal (epic_id + phase + task description)
- Agents fetch documentation on demand via direct file paths
- Progressive disclosure: parent pages link to details, agents load only what's needed

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

Phase 3: Technical specifications (conditional)
  → API contracts, schemas in docs/architecture/13-specs/ (if used)
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
1. Architect creates fix stories from audit findings
2. Developer implements fixes
3. Final audit (max 2 cycles total, then escalate)

### 8.4 Supporting Operations

- **`/sync_product`** - When implementation reveals product-level changes (new capabilities, terminology changes, scope shifts), updates `docs/product/` accordingly
- **`/create`** - Product-owner agent interactively creates work items with appropriate questions per type

---

## 9. Documentation Structure

Documentation uses two complementary standards:

### Product Documentation (Atlassian Blueprint Pattern)

See `design/scope-product-atlassian.md` for full specification.

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

See `design/scope-technical-arc42-c4.md` for full specification.

```
docs/architecture/
├── 01-intro.md               # Purpose, stakeholders, quality goals
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
└── 13-specs/                 # API contracts, schemas, database specs
```

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

### 10.1 Claude Code as Orchestrator (v3.0)

**Decision:** Remove custom orchestrator agent. Use Claude Code's built-in capabilities.

**Rationale:**
- Claude Code 2.1.16 introduced TaskCreate/TaskUpdate/TaskList, eliminating need for plan schemas
- Slash commands already contain workflow logic; separate orchestrator was redundant
- Removes plan execution engine, state files, agent-summary protocol
- Simpler system with fewer moving parts

**Impact:** Commands are self-contained workflows. No orchestrator.md, no planners, no plan JSON.

### 10.2 Contract-First over Prose Descriptions (v3.0)

**Decision:** Epic refinement produces executable `contracts.py` with Python Protocol classes.

**Rationale:**
- YAML prose descriptions led to hidden integration failures
- `mypy --strict` catches interface mismatches statically
- Agents implement against machine-verifiable contracts

**Impact:** Story 0 in every epic creates contracts.py. All subsequent stories must pass `mypy --strict`.

### 10.3 Local Files for Documentation (v3.0)

**Decision:** Documentation is always local markdown files. Removed multi-backend support.

**Rationale:**
- Simplifies the system (no MCP dependencies, no backend dispatch)
- Files are in git alongside code
- Agents read/write files directly (fast, no API calls)
- Still follows Arc42+C4 and Atlassian Blueprint patterns for structure

**Impact:** project-documentation skill always writes to `docs/`. Template-based, no backend selection.

### 10.4 Two Implementation Modes (v3.0)

**Decision:** Provide both TDD (`/implement_tdd`) and non-TDD (`/implement`) modes.

**Rationale:**
- TDD (SDET writes tests first) is ideal for complex integration scenarios
- Non-TDD (developer writes code + tests) is faster for straightforward features
- User chooses per epic; one mode will eventually be deprecated

### 10.5 One Agent Per Story (v2.5)

**Decision:** A single agent must implement the complete story.

**Rationale:**
- Splitting across agents creates context coordination complexity
- Agent loads technology skills dynamically as needed
- Story boundaries align with technical component boundaries

### 10.6 Test-as-Soon-as-Possible (v2.4)

**Decision:** Write tests at the earliest possible point, not deferred to epic end.

**Rationale:**
- Fixing issues in closed stories is expensive (context lost)
- Early testing catches issues while context is fresh
- Prevents "big bang" integration risk at epic end

### 10.7 Architect-Led Story Breakdown (v2.4)

**Decision:** Architect leads story breakdown; Product Owner validates business alignment.

**Rationale:**
- Technical boundaries drive story structure (component alignment, dependencies)
- Architect has full context of architecture decisions for story sequencing
- PO ensures stories deliver coherent user value

### 10.8 File Plan Intent Documentation (v2.6)

**Decision:** Each file in the plan has a 600-1200 character intent with 5-part structure.

**Parts:**
1. **WHAT** (~100 chars): Core functionality
2. **WHY** (~150-250 chars): Architectural purpose
3. **RESPONSIBILITIES** (~150-250 chars): Key functions (3-5)
4. **DEPENDENCIES** (~100-150 chars): Module dependencies
5. **RELATED MODULES** (~100-150 chars): Positive delegation

**Key insight:** Use positive delegation ("session encryption via SessionStore") instead of negation ("Does NOT handle encryption") to avoid confusing semantic search routing.
