# Reverse Engineering Documentation Guide

**Goal**: Create complete product and architecture documentation from an existing codebase using code scanning and structured interviews.

---

## Overview

SCOPE includes a `/re_documentation` command that reverse engineers documentation from existing code. It uses two specialized agents:

1. **Product Owner Agent** (`reverse-engineer-po`) — Creates product documentation (9 files)
2. **Architect Agent** (`reverse-engineer-architect`) — Creates system architecture documentation (15 files, Arc42 + C4)

Each agent follows the same pattern:
1. **Code Exploration** — Agent scans the codebase autonomously
2. **Structured Interview** — Agent asks you targeted questions
3. **Document Generation** — Agent creates documentation files
4. **Review & Refinement** — You review and approve

---

## Quick Start

```
cd /path/to/your-project
claude

/re_documentation
```

The command walks you through both phases with approval gates between them.

---

## What Gets Created

### Phase 1: Product Documentation

```
docs/product/
├── overview.md                      # Product summary
├── strategy.md                      # Vision, markets, problems
├── definition.md                    # Use cases, capability map
├── decisions.md                     # Product decisions (PDRs)
└── reference/
    ├── feature-catalog.md           # All features with status
    ├── terminology-data-model.md    # Domain terms and entities
    ├── use-case.md                  # Detailed use case descriptions
    ├── ux-workflows.md              # Step-by-step user workflows
    └── apis-integrations.md         # External integrations
```

### Phase 2: Architecture Documentation (Arc42)

```
docs/architecture/
├── 01-intro.md                      # Introduction & goals
├── 02-constraints.md                # Technical & organizational
├── 03-context.md                    # C4 Level 1 context diagram
├── 04-strategy.md                   # Tech stack, patterns
├── 05-building-blocks.md            # C4 Level 2 & 3 diagrams
├── 06-runtime.md                    # Sequence diagrams
├── 07-deployment.md                 # Deployment architecture
├── 08-cross-cutting/
│   ├── domain.md                    # Domain model
│   ├── security.md                  # Auth, data protection
│   ├── operations.md                # Logging, monitoring
│   └── testing.md                   # Test strategy
├── 09-adr-summary.md               # Architecture decisions
├── 10-quality.md                    # Quality requirements
├── 11-risks.md                      # Risks & technical debt
└── 12-glossary.md                   # Technical glossary
```

---

## How It Works

### Phase 1: Product Owner Agent

**Duration**: ~1 hour (30-45 min of your time answering questions)

The PO agent scans your codebase looking for:
- README and existing docs
- Entry points, CLI commands, help text
- Data models (Pydantic, dataclasses, schemas)
- Services/components and their inputs/outputs
- Configuration options

Then interviews you across 5 sections:
1. **Vision & Problem Space** — What problem does this solve? Who uses it?
2. **Use Cases & Workflows** — How do users interact with it?
3. **Features & Capabilities** — Validates what it found, asks about value
4. **Terminology & Domain Model** — Defines key terms
5. **Technical Constraints & Decisions** — Why certain choices were made

### Phase 2: Architect Agent

**Duration**: ~1-1.5 hours (45-60 min of your time)

The Architect agent scans for:
- Tech stack (package managers, imports, SDKs)
- System structure (services, entry points, shared libraries)
- Component internals (classes, modules, responsibilities)
- Integration points (external services, APIs, data flow)
- Cross-cutting concerns (security, logging, testing, config)
- Deployment (Docker, K8s, infrastructure code)

Then interviews you across 9 sections:
1. **Technology Stack Rationale** — Why each technology?
2. **System Architecture & Patterns** — Validates structure, asks about patterns
3. **Component Deep-Dive** — Drills into complex components
4. **Runtime Behavior** — Execution flow, concurrency, critical paths
5. **Deployment & Operations** — How it's deployed and monitored
6. **Cross-Cutting Concerns** — Domain model, security, testing, operations
7. **Quality Requirements** — Performance, scalability, reliability targets
8. **Constraints & Risks** — Technical debt, known issues
9. **Decisions & Rationale** — Key architectural decisions and tradeoffs

---

## Tips for Effective Interviews

### For Product Questions

- **Think from the user perspective** — not "this service does X" but "users achieve Y"
- **Be specific about use cases** — real scenarios with starting point, steps, and outcome
- **Explain value, not just features** — not "we have caching" but "users get sub-second responses"
- **Define terminology clearly** — how your team uses terms, not dictionary definitions

### For Architecture Questions

- **Explain rationale** — not "we use Redis" but "we chose Redis because X, considered Y"
- **Be honest about technical debt** — what you'd fix if you had time
- **Describe real behavior** — how the system actually runs, not the ideal state
- **Capture decisions with tradeoffs** — what alternatives were considered

---

## Running Only One Phase

You can tell the command to run just one phase:

- "Only run Phase 1" — Product documentation only
- "Only run Phase 2" — Architecture documentation only (useful if you already have product docs)

---

## After Documentation

Once you have product and architecture documentation, you can use the rest of the SCOPE workflow:

```
/re_documentation     → Reverse engineer docs from existing code
/prd_refine           → Refine the PRD for new features
/prd_breakdown        → Break PRD into epics
/epic_refine          → Refine each epic
/implement            → Implement story-by-story
```

---

## Estimated Timeline

| Phase | Duration | Your Time |
|-------|----------|-----------|
| **Phase 1: Product (PO Agent)** | ~1 hour | 30-45 min |
| - Code Exploration | 10-15 min | None |
| - Interview | 30-45 min | Active |
| - Document Generation | 5-10 min | None |
| - Review | 10-20 min | Active |
| | | |
| **Phase 2: Architecture (Architect Agent)** | ~1-1.5 hours | 45-60 min |
| - Code Analysis | 15-20 min | None |
| - Interview | 45-60 min | Active |
| - Document Generation | 10-15 min | None |
| - Review | 10-20 min | Active |
| | | |
| **Total** | 2-3 hours | ~1.5-2 hours active |

Plan for 3 hours with breaks. Don't rush the interview sections.
