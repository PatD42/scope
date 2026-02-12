# Reverse Engineering Documentation Guide

**Project**: AquaForge (~/dev/aquaforge-reqs)
**Goal**: Create complete BMAD-aligned documentation from existing code
**Agents**: reverse-engineer-pm + reverse-engineer-architect

---

## Overview

This guide explains how to use two specialized AI agents to reverse engineer your product and system architecture documentation from the existing AquaForge codebase.

**What you'll create**:
- **Phase 0**: Product Documentation (9 files) - Business view
- **Phase 0.5**: System Architecture (Arc42 12 chapters) - Technical view

**Time estimate**: 2-3 hours total (1-1.5 hours per agent)

---

## Prerequisites

1. **Product Documentation Skill Installed**:
   - Templates at: `~/aquaforge/scope/src/skills/project-documentation/`
   - Includes: product templates + architecture templates

2. **Output Directory**:
   - Create: `~/dev/aquaforge-reqs/.scope/docs/`
   - Or use existing `~/dev/aquaforge-reqs/docs/` (will reorganize)

---

## Workflow

### Step 1: Run PM Agent (Product Documentation)

**Duration**: 1-1.5 hours

**Launch Agent**:
```
cd ~/dev/aquaforge-reqs
claude chat

*agent reverse-engineer-pm
```

**What Happens**:

**Phase 1: Autonomous Code Exploration** (Agent works independently)
- Agent reads README, docs, code structure
- Agent maps out services, data models, CLI commands
- Agent creates preliminary understanding document
- **You do nothing during this phase** (10-15 minutes)

**Phase 2: Structured Interview** (You answer questions)
- Agent asks targeted questions in 5 sections:
  1. Vision & Problem Space (5-10 min)
  2. Use Cases & Workflows (10-15 min)
  3. Features & Capabilities (10-15 min)
  4. Terminology & Domain Model (5-10 min)
  5. Technical Constraints & Decisions (5 min)
- **You answer conversationally** - agent guides you through questions

**Phase 3: Document Generation** (Agent works independently)
- Agent creates 9 product documentation files
- **You do nothing during this phase** (5-10 minutes)

**Phase 4: Review & Refinement** (You review)
- Agent presents documents for review
- You provide feedback
- Agent iterates until approved

**Output**: Complete product documentation (9 files):
```
.scope/docs/product/
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

---

### Step 2: Run Architect Agent (System Architecture)

**Duration**: 1-1.5 hours

**Prerequisites**: Product documentation from Step 1 complete

**Launch Agent**:
```
*agent reverse-engineer-architect
```

**What Happens**:

**Phase 1: Autonomous Code Analysis** (Agent works independently)
- Agent analyzes tech stack, system structure, components
- Agent creates C4 diagrams (Context, Container, Component)
- Agent identifies integration points, cross-cutting concerns
- Agent creates preliminary architecture understanding document
- **You do nothing during this phase** (15-20 minutes)

**Phase 2: Structured Interview** (You answer questions)
- Agent asks technical questions in 9 sections:
  1. Technology Stack Rationale (10 min)
  2. System Architecture & Patterns (15 min)
  3. Component Deep-Dive (15-20 min)
  4. Runtime Behavior (10 min)
  5. Deployment & Operations (10 min)
  6. Cross-Cutting Concerns (10 min)
  7. Quality & Non-Functional Requirements (10 min)
  8. Constraints & Risks (10 min)
  9. Decisions & Rationale (5 min)
- **You answer conversationally** - agent guides you through questions

**Phase 3: Document Generation** (Agent works independently)
- Agent creates Arc42 12-chapter architecture documentation
- Agent creates C4 diagrams in Mermaid format
- **You do nothing during this phase** (10-15 minutes)

**Phase 4: Review & Refinement** (You review)
- Agent presents architecture documentation and diagrams
- You provide feedback
- Agent iterates until approved

**Output**: Complete system architecture (15 files):
```
.scope/docs/architecture/
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
└── 12-glossary.md
```

---

## Tips for Effective Interviews

### For PM Agent (Product Questions):

1. **Think from user perspective**:
   - Not "this service does X"
   - But "users achieve Y by doing X"

2. **Be specific about use cases**:
   - Real scenarios, not abstract descriptions
   - Include starting point, steps, and outcome

3. **Explain value, not just features**:
   - Not "we have multilingual embeddings"
   - But "users can search regulations in any language"

4. **Define terminology clearly**:
   - How you use terms, not dictionary definitions
   - Relationships between concepts

### For Architect Agent (Technical Questions):

1. **Explain rationale, not just what**:
   - Not "we use Qdrant"
   - But "we chose Qdrant because X, considered Y, decided against Z because..."

2. **Be honest about technical debt**:
   - What you'd fix if you had time
   - Known issues and workarounds

3. **Describe real behavior**:
   - How system actually runs, not ideal state
   - Real performance, not theoretical

4. **Capture decisions with tradeoffs**:
   - What alternatives were considered
   - Why you chose one over another
   - What you gave up

---

## Output Directory Structure

After both agents complete, you'll have:

```
~/dev/aquaforge-reqs/.scope/docs/
├── product/                          # Phase 0 (PM Agent)
│   ├── overview.md
│   ├── strategy.md
│   ├── definition.md
│   ├── decisions.md
│   └── reference/
│       ├── feature-catalog.md
│       ├── terminology-data-model.md
│       ├── use-case.md
│       ├── ux-workflows.md
│       └── apis-integrations.md
│
└── architecture/                     # Phase 0.5 (Architect Agent)
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
    └── 12-glossary.md
```

---

## Assessment: Single Product vs. Multiple Products

### ✅ Recommendation: Single Product Documentation

**Why**:
- AquaForge is **one product** (regulatory document processing platform)
- 6 services form a **single pipeline** (not separate products)
- Shared library (`aquaforge`) indicates **single codebase**
- Services are **not independently deployable products** (they're components)

**Structure**:
- **Product Documentation**: One set (AquaForge.ai)
- **System Architecture**: One architecture showing all 6 services as **containers** (C4 Level 2)
- **No separate product docs per service** - they're components, not products

**Each service appears in**:
- **C4 Container Diagram** (Level 2) - As a container in the system
- **C4 Component Diagrams** (Level 3) - Internal structure of each container
- **Building Blocks** (Arc42 Ch 5) - Detailed component view

**NOT as separate products** with their own product/strategy/definition docs.

---

## Next Steps After Documentation

Once you have complete product + architecture documentation:

### Optional: Epic Documentation

You may want to document major features/initiatives as "epics":

**Example Epics** (based on your existing docs):
- **Epic**: Enhanced Chunking Strategy (already has docs/misc/chunking-strategy.md)
- **Epic**: Multilingual Processing (multilingual embeddings, cross-lingual search)
- **Epic**: Multi-Agent Pipeline Integration (docs/multi-agent-pipeline/)
- **Epic**: Document Reconstruction & Validation

**For each epic**, create:
- Epic Details
- Architecture (how this epic extends system architecture)
- ADR (decisions made for this epic)
- Test Strategy
- Implementation Summary

**But**: Start with product + system architecture first. Epics are optional.

---

## Troubleshooting

### Agent gets stuck or confused

**Solution**: Restart with clearer context
```
*agent reverse-engineer-pm

"Start fresh. I have an existing Python project at ~/dev/aquaforge-reqs
with 6 pipeline services. Begin Phase 1: Code Exploration."
```

### Agent asks questions you can't answer

**Solution**: Tell agent to infer or skip
```
"I don't know the answer to that. Can you infer from the code,
or mark as 'TODO' and move on?"
```

### Generated documents have errors

**Solution**: Provide corrections in review phase
```
"In product/strategy.md, change target market from X to Y.
In section 3, add this use case..."
```

### Agent output doesn't follow template format

**Solution**: Remind agent of templates
```
"Please use the exact template format from
~/aquaforge/scope/src/skills/project-documentation/templates-product-atlassian/strategy.md"
```

---

## Success Criteria

After completing both agents:

- [ ] Product documentation exists (9 files)
- [ ] System architecture exists (15 files)
- [ ] All questions answered (no "TODO" or "Unknown")
- [ ] C4 diagrams created (Context, Container, Component)
- [ ] You've reviewed and approved all documents
- [ ] Documentation is accurate (reflects current state)
- [ ] Rationale captured (why decisions were made)

**You now have BMAD Phase 0 + Phase 0.5 complete** and can proceed to epic planning if needed.

---

## Estimated Timeline

| Phase | Duration | Your Involvement |
|-------|----------|------------------|
| **Step 1: PM Agent** | 1-1.5 hours | 30-45 min (interview) |
| - Code Exploration | 10-15 min | None (agent works) |
| - Interview | 30-45 min | Answer questions |
| - Document Generation | 5-10 min | None (agent works) |
| - Review & Refinement | 10-20 min | Review & feedback |
| | | |
| **Step 2: Architect Agent** | 1-1.5 hours | 45-60 min (interview) |
| - Code Analysis | 15-20 min | None (agent works) |
| - Interview | 45-60 min | Answer questions |
| - Document Generation | 10-15 min | None (agent works) |
| - Review & Refinement | 10-20 min | Review & feedback |
| | | |
| **TOTAL** | 2-3 hours | 1.5-2 hours active |

**Plan for 3 hours with breaks** - don't rush the interview sections.

---

## Ready to Start?

```bash
cd ~/dev/aquaforge-reqs
claude chat

# Start with PM Agent
*agent reverse-engineer-pm
```

**Good luck!** The agents will guide you through the process.
