---
name: re_documentation
description: Reverse engineer product and architecture documentation from an existing codebase using code scanning and structured interviews
skills: project-documentation
---

# /re_documentation

Reverse engineer complete product and architecture documentation from an existing codebase. Uses two specialized agents that scan code autonomously, then interview you to fill gaps.

**Output:**
- Product documentation (9 files) — business view
- System architecture (15 files, Arc42 + C4) — technical view
- Component architecture (up to 6 files) — backend and/or frontend detail

---

## Overview

```
Phase 1: Product Documentation (PO Agent)
  Code scan → Interview → Generate → Review

Phase 2: Architecture Documentation (Architect Agent)
  Code scan → Interview → Generate → Review
```

Each phase has 4 steps:
1. **Code Exploration** — Agent scans the codebase autonomously (you wait)
2. **Structured Interview** — Agent asks you targeted questions
3. **Document Generation** — Agent creates documentation files (you wait)
4. **Review & Refinement** — You review, provide feedback, approve

---

## Execution

### Step 0: Validate Prerequisites

```python
# Check that documentation templates are available
templates_product = Glob("**/skills/project-documentation/templates-product-atlassian/**/*.md")
templates_arch = Glob("**/skills/project-documentation/templates-technical-arc42-c4/**/*.md")

if not templates_product or not templates_arch:
    print("ERROR: project-documentation skill not found.")
    print("Run install.sh to install SCOPE to this project.")
    exit(1)

# Check for existing docs — detect gaps
existing_product = Glob("docs/product/**/*.md")
existing_arch_system = Glob("docs/architecture/*.md")
existing_arch_crosscut = Glob("docs/architecture/08-cross-cutting/*.md")
existing_backend = Glob("docs/architecture/backend/*.md")
existing_frontend = Glob("docs/architecture/frontend/*.md")

has_product = len(existing_product) >= 5
has_system_arch = len(existing_arch_system) >= 10
has_crosscut = len(existing_arch_crosscut) >= 3
has_backend = len(existing_backend) >= 3
has_frontend = len(existing_frontend) >= 3

# Determine what needs to be done
if has_product and has_system_arch and has_crosscut and has_backend and has_frontend:
    print("All documentation already exists. Nothing to do.")
    print("Use the architect/PO agents during epic work to update docs.")
    exit(0)

# Report what exists and what's missing
print("Documentation gap analysis:")
print(f"  Product docs:        {'COMPLETE' if has_product else 'MISSING'} ({len(existing_product)} files)")
print(f"  System architecture: {'COMPLETE' if has_system_arch else 'MISSING'} ({len(existing_arch_system)} files)")
print(f"  Cross-cutting:       {'COMPLETE' if has_crosscut else 'MISSING'} ({len(existing_arch_crosscut)} files)")
print(f"  Backend component:   {'COMPLETE' if has_backend else 'MISSING'} ({len(existing_backend)} files)")
print(f"  Frontend component:  {'COMPLETE' if has_frontend else 'MISSING'} ({len(existing_frontend)} files)")
print("")

if existing_product or existing_arch_system:
    print("Options:")
    print("  1. Create only missing documentation (recommended)")
    print("  2. Overwrite all documentation")
    print("  3. Cancel")
    # Wait for user choice — default is option 1
```

### Step 1: Create Output Directories

```bash
mkdir -p docs/product/reference
mkdir -p docs/architecture/08-cross-cutting
mkdir -p docs/architecture/backend/adr
mkdir -p docs/architecture/frontend/adr
```

---

## Phase 1: Product Documentation

**Skip if**: Gap analysis shows product docs are complete and user chose option 1 (create only missing).

**Agent**: `reverse-engineer-po`
**Duration**: ~1 hour (30-45 min interview)

### 1.1 Launch PO Agent

Tell the user:

```
Starting Phase 1: Product Documentation

I'll now work as the Product Owner agent to reverse engineer your product
documentation. This has 4 steps:

  1. Code Exploration — I'll scan your codebase (you wait, ~10-15 min)
  2. Interview — I'll ask you targeted questions (~30-45 min)
  3. Document Generation — I'll create the docs (you wait, ~5-10 min)
  4. Review — You review and approve

Starting code exploration now...
```

### 1.2 Execute PO Agent Process

Follow the full process defined in the `reverse-engineer-po` agent:

1. **Phase 1 (Autonomous)**: Scan README, entry points, data models, services, user-facing elements
2. **Phase 2 (Interview)**: 5 sections — Vision, Use Cases, Features, Terminology, Decisions
3. **Phase 3 (Generate)**: Create 9 product documentation files
4. **Phase 4 (Review)**: Present to user, iterate until approved

### 1.3 Product Documentation Output

```
docs/product/
├── overview.md
├── strategy.md
├── definition.md
├── decisions.md
└── reference/
    ├── feature-catalog.md
    ├── terminology-data-model.md
    ├── use-case.md
    ├── ux-workflows.md
    └── apis-integrations.md
```

### 1.4 Approval Gate

```
Phase 1 Complete: Product Documentation

Created 9 files in docs/product/

Please review the documents above.
  - Are there corrections needed?
  - Is anything missing?
  - Ready to proceed to Phase 2 (Architecture)?

[approve / revise / stop here]
```

**Do not proceed to Phase 2 until the user approves Phase 1.**

---

## Phase 2: Architecture Documentation

**Skip if**: Gap analysis shows all architecture docs are complete (system + component).
**Partial run**: If system docs exist but backend/frontend component docs are missing, the architect agent will focus only on the missing component documentation (shorter interview, fewer documents).

**Agent**: `reverse-engineer-architect`
**Duration**: ~1-1.5 hours full, ~30 min if only component docs needed

### 2.1 Launch Architect Agent

```
Starting Phase 2: Architecture Documentation

I'll now work as the Architect agent to reverse engineer your system
architecture documentation (Arc42 + C4 diagrams). Same 4 steps:

  1. Code Analysis — I'll analyze your codebase structure (~15-20 min)
  2. Interview — I'll ask technical architecture questions (~45-60 min)
  3. Document Generation — I'll create Arc42 chapters (~10-15 min)
  4. Review — You review and approve

Starting code analysis now...
```

### 2.2 Execute Architect Agent Process

Follow the full process defined in the `reverse-engineer-architect` agent:

1. **Phase 1 (Autonomous)**: Tech stack, system structure, components, integration points, backend services & data, frontend structure, cross-cutting concerns, deployment, quality attributes
2. **Phase 2 (Interview)**: Up to 11 sections — Tech Rationale, Architecture, Components, Backend Services & Data, Frontend Architecture, Runtime, Deployment, Cross-cutting, Quality, Constraints, Decisions (sections skipped if docs already exist)
3. **Phase 3 (Generate)**: Create Arc42 12-chapter documentation + backend/frontend component docs with C4 diagrams
4. **Phase 4 (Review)**: Present to user, iterate until approved

**Important**: The Architect agent should read the product documentation from Phase 1 as input — it provides context about the product's purpose, use cases, and domain model.

### 2.3 Architecture Documentation Output

```
docs/architecture/
├── 01-intro.md
├── 02-constraints.md
├── 03-context.md
├── 04-strategy.md
├── 05-building-blocks.md
├── 06-runtime.md
├── 07-deployment.md
├── 08-cross-cutting/
│   ├── domain.md
│   ├── security.md
│   ├── operations.md
│   └── testing.md
├── 09-adr-summary.md
├── 10-quality.md
├── 11-risks.md
├── 12-glossary.md
├── backend/              ← if project has backend
│   ├── overview.md
│   ├── services.md
│   ├── data.md
│   └── adr/
└── frontend/             ← if project has frontend
    ├── overview.md
    ├── structure.md
    ├── patterns.md
    └── adr/
```

### 2.4 Approval Gate

```
Phase 2 Complete: Architecture Documentation

Created files in docs/architecture/:
  - System (arc42):  15 files (or skipped if already existed)
  - Backend:          3 files (if applicable)
  - Frontend:         3 files (if applicable)

Please review the documents and C4 diagrams.
  - Are the diagrams accurate?
  - Are there architecture decisions missing?
  - Any corrections needed?

[approve / revise]
```

---

## Completion

```
Reverse Engineering Complete

Product Documentation:  9 files in docs/product/
System Architecture:   15 files in docs/architecture/
Backend Component:      3 files in docs/architecture/backend/  (if applicable)
Frontend Component:     3 files in docs/architecture/frontend/ (if applicable)

Total: up to 30 documentation files generated from code analysis + interview.

Next steps:
  - Review docs periodically as the codebase evolves
  - Use /sync_product after product-level changes
  - Use /prd_breakdown to plan new epics from here
```

---

## Tips for Effective Interviews

**For Product Questions (Phase 1):**
- Think from the user perspective, not implementation
- Be specific about use cases — real scenarios, not abstract
- Explain value, not just features
- Define terminology as your team uses it

**For Architecture Questions (Phase 2):**
- Explain rationale, not just "what" — why you chose X over Y
- Be honest about technical debt and known issues
- Describe real runtime behavior, not ideal state
- Capture decisions with tradeoffs considered

---

## Running Only One Phase

You can run just product or just architecture documentation by telling the agent:

- "Only run Phase 1 (Product Documentation)" — stops after product docs
- "Only run Phase 2 (Architecture Documentation)" — skips product docs, goes straight to architecture
- "Only create backend docs" — creates only `docs/architecture/backend/` component docs
- "Only create frontend docs" — creates only `docs/architecture/frontend/` component docs

**Gap-aware execution**: The command automatically detects existing documentation and recommends creating only what's missing. If system-level arc42 docs already exist but `backend/` or `frontend/` docs don't, it will focus the architect agent on the missing component documentation only.

---

## Compaction Survival

If the conversation is compacted mid-execution, the agent must preserve:
- Current phase (1 or 2)
- Current step within the phase
- Files already generated
- Interview answers collected so far
- Pending approval gates
