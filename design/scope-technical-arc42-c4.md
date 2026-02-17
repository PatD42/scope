# SCOPE - Arc42 + C4 Documentation Standard

Why spend so many tokens on documentation? Because Scope goes beyond prototyping and vibe coding to delivery enterprise-grade products that can evolve through hundreds of epics. To perform well in these conditions, any organizations need to have a reliable documentation.

---

## Table of Contents

- [0. Overview](#Overview)
- [1. Arc42 + C4?](#arc42--c4)
- [2. Example Documentation Structure](#example-documentation-structure)
- [3. Agent Responsibilities Summary](#agent-responsibilities-summary)
- [4. Detailed File Specifications](#4-detailed-file-specifications)
  - [4.1 Framework Overview](#41-framework-overview)
  - [4.2 Product Documentation](#42-product-documentation)
  - [4.3 Architecture Documentation](#43-architecture-documentation-arc42-based)
  - [4.4 Epic Documentation](#44-epic-documentation)
  - [4.5 Release Documentation](#45-release-documentation)
  - [4.7 Child File Guidelines](#47-child-file-guidelines)
  - [4.8 Token Budget Guidelines](#48-token-budget-guidelines)
  - [4.9 Agent-File Mapping (Critical)](#49-agent-file-mapping-critical)
  - [4.10 Update Responsibilities](#410-update-responsibilities)
  - [4.11 Versioning Strategy](#411-versioning-strategy)
  - [4.12 Search Strategy](#412-search-strategy)
  - [4.13 Lean Implementation Approach](#413-lean-implementation-approach)
  - [4.14 Template Storage](#414-template-storage)
  - [4.15 Summary](#415-summary)

---

## Overview

Scope's documentation structure and methodology can and should be tailored to the organization's needs. This document aligns to a large extent with a lean **Arc42 + C4** as this is fairly common, and adapts well to agentic teams.

### Project documentation

This is where your critical IP resides (product, architecture, epic details, release details). This is the strategic and most valuable IP for your project. It is persistent and structured to provide the right context to the right agent, with minimal extra noise to optimize Claude's attention and minimize wasted tokens.

**Two orthogonal concerns:**
1. **Documentation structure**: agents should not guess and iterate at finding the right content, and **must not** be wrong when selecting where to create new content. This is implemented using:
  - Documentation standard → `project-documentation` skill → local markdown files in `docs/`
2. **Agent responsibilities**: Each section of the documentation must have clear owners, and ideally clear triggers as to when files get updated. This is implemented using 2 levels:
  - Documentation standard → Agent responsibilities
  - Each standard defines what agents are responsible to document, and what they should read to do their tasks
  - Agents determine what docs to read based on their role

### Project tracking
This is where your active development information resides. It should be ephemeral with limited historical value. This is where the tactical/operational information resides for the duration of the task (ex.: epic implementation).

**Target audience:** Agentic teams building enterprise-scale products over 5+ years with hundreds of epics, without sacrificing nuances as documentation grows.

---

## Arc42 + C4

**Arc42** is a comprehensive, battle-tested architecture documentation template with 12 sections covering structure, decisions, quality, deployment, and risks. Widely adopted in European enterprises, growing in US adoption.

**C4 model** provides visual clarity with 4 levels of abstraction: Context (L1), Container (L2), Component (L3), Code (L4). Industry standard for architecture diagrams.

**Product sections** (Strategy, Definition, Reference, PDR) extend Arc42 with product management context that agents need during epic refinement.

### Value This Structure Provides

1. **Living documentation** - Always up-to-date with clear content ownership
2. **Long product lifespan** - Prevents yearly refactoring from agentic team mistakes or lost context
3. **Historical context** - ADR/PDR preserve decision rationale for future teams
4. **Traceability** - ADR/PDR link decisions to epics; epic summaries link to architecture/product files
5. **Quality accountability** - Quality requirements (Arc42 Section 10) and technical debt registry (Section 11) make SLAs and shortcuts explicit
6. **Deterministic access** - Tag-based file organization enables reliable file retrieval via directory structure and naming conventions

---

## Agent Responsibilities Summary

This section provides a high-level overview of which agents interact with which documentation files.

### By Agent

| Agent | Reads (Documentation) | Writes (Documentation) | Contributes To (Documentation) |
|-------|----------------------|------------------------|--------------------------------|
| **Product Owner** | Product Strategy/Definition/Reference<br>Architecture Quality Requirements | Product files (all 4)<br>Epic PDR | - |
| **Architect** | Product Strategy/Definition<br>Architecture (all sections + cross-cutting files) | Architecture (all sections + cross-cutting files)<br>Epic Details (technical)<br>Epic Architecture<br>Epic ADR<br>Epic File Plan<br>Epic Implementation Summary | - |
| **SDET** | Product Definition<br>Architecture Runtime/Quality/Testing<br>Epic Details/Architecture | - | - |
| **Developer** | Architecture Domain Model/Operations<br>Epic ADR (if story context insufficient) | `.scope/{story-id}/agent_summaries.jsonl` | - |

### By Documentation Type

| Documentation Type | Primary Owner | Secondary Contributors | Update Frequency |
|--------------------|---------------|------------------------|------------------|
| **Product Strategy** | Product Owner | - | Quarterly or strategic shift |
| **Product Definition** | Product Owner | Architect (review) | When capabilities change |
| **Product Reference** | Product Owner | Architect (review) | When data model changes |
| **Product PDR** | Product Owner | - | Per epic |
| **Architecture (all 12 sections)** | Architect | - | Varies by section (see Section 2.10) |
| **Epic Details** | Product Owner + Architect | SDET | During epic refinement |
| **Epic Architecture/ADR/File Plan** | Architect | - | During epic refinement |
| **Epic PDR** | Product Owner | - | During epic refinement |
| **Epic Implementation Summary** | Architect | - | After epic completion |

### By Phase

| Phase | Active Agents | Documentation Activities |
|-------|---------------|--------------------------|
| **Epic Refinement** | Product Owner, Architect, SDET | Write: Product files (if needed), Epic Details, Epic Architecture, Epic ADR, Epic PDR, Epic File Plan<br>Read: Product/Architecture context |
| **Implementation** | Developer, SDET | Read: Story (self-contained), Epic ADR (if confused), Architecture Cross-cutting<br>Write: Technical debt notes |

---

## Example Documentation Structure

This section provides a concrete example of how documentation is organized as local markdown files in the `docs/` directory, managed by the `project-documentation` skill.

### Documentation Structure

```
docs/
├── product/
│   ├── overview.md
│   ├── strategy.md                          (tag: product, strategy)
│   ├── definition.md                        (tag: product, definition)
│   ├── reference/
│   │   ├── feature-catalog.md               (tag: product, reference)
│   │   ├── terminology.md                   (tag: product, reference)
│   │   ├── ux-workflows.md                  (tag: product, reference)
│   │   └── apis-integrations.md             (tag: product, reference)
│   └── decisions.md                         (tag: product, pdr)
├── architecture/
│   ├── 01-intro.md                          (tag: architecture, intro)
│   ├── 02-constraints.md                    (tag: architecture, constraints)
│   ├── 03-context.md                        (tag: architecture, context)
│   ├── 04-strategy.md                       (tag: architecture, strategy)
│   ├── 05-building-blocks.md                (tag: architecture, building-blocks)
│   ├── 06-runtime.md                        (tag: architecture, runtime)
│   ├── 07-deployment.md                     (tag: architecture, deployment)
│   ├── 08-cross-cutting/
│   │   ├── domain-model.md                  (tag: architecture, cross-cutting, domain-model)
│   │   ├── security.md                      (tag: architecture, cross-cutting, security)
│   │   ├── operations.md                    (tag: architecture, cross-cutting, operations)
│   │   └── testing.md                       (tag: architecture, cross-cutting, testing)
│   ├── 09-adr.md                            (tag: architecture, adr)
│   ├── 10-quality.md                        (tag: architecture, quality)
│   ├── 11-risks.md                          (tag: architecture, risks)
│   └── 12-glossary.md                       (tag: architecture, glossary)
├── epics/{epic-id}/
│   ├── details.md                           (tag: epic, {epic-id}, epic-details)
│   ├── architecture.md                      (tag: epic, {epic-id}, architecture)
│   ├── adr.md                               (tag: epic, {epic-id}, adr)
│   ├── pdr.md                               (tag: epic, {epic-id}, pdr)
│   ├── file-plan.md                         (tag: epic, {epic-id}, file-plan)
│   └── implementation-summary.md            (tag: epic, {epic-id}, summary)
└── releases/{version}/
    ├── record.md                            (tag: release, {version}, record)
    ├── notes.md                             (tag: release, {version}, notes)
    └── postmortem.md                        (tag: release, {version}, post-mortem)
```

---

## 4. Detailed File Specifications

This section provides detailed specifications for each file type, including content, tags, update frequency, and agent usage.

### 4.1 Framework Overview

**Arc42 + C4 Hybrid Approach:**
- **Arc42** provides comprehensive architecture documentation (12 sections)
- **C4 diagrams** provide visual clarity (4 levels: Context, Container, Component, Code)
- **Product sections** extend Arc42 with strategy, use cases, and glossary
- **Living documentation** always up-to-date, component versioning (not file versioning)

**Implementation principle:** Start with all 12 Arc42 sections immediately, keep each section lean initially, evolve as product scales.

**Tag-based navigation:** Use separate tags (not composite) to enable flexible queries.
- Example: `tag: epic, epic-id, adr` enables "find all epic ADRs"
- File path conventions and grep handle content searches

### 4.2 Product Documentation

Product documentation uses markdown-based workflows with progressive disclosure. See `scope-product-atlassian.md` for comprehensive details.

Product documentation lives in the `docs/product/` directory.

#### 4.2.1 Product Strategy
**File:** `docs/product/strategy.md`
**Tags:** `product`, `strategy`
**Content:**
- Vision statement (purpose, north star, in-scope, out-of-scope)
- Target markets (segments, personas, product-market fit)
- Customer problems (pain points, intrinsic drivers)
- Links to detailed market research, go-to-market strategy

**Update frequency:** As customer insights evolve (quarterly or when strategic shift occurs)

**Agents using this file:**
- **Product Owner** (reads during epic creation, writes during quarterly updates)
- **Architect** (reads during epic creation to understand business context)

**Token budget guideline:** ~800 words (~600 tokens)

---

#### 4.2.2 Product Definition
**File:** `docs/product/definition.md`
**Tags:** `product`, `definition`
**Content:**
- Use cases & user journeys (goals, flows, links to epic details)
- Capability map & feature matrix (areas, value props, differentiation, dependencies, out-of-scope/won't-do)

**Update frequency:** When product capabilities or user intent materially change

**Agents using this file:**
- **Product Owner** (reads during epic creation, writes when capabilities change)
- **SDET** (reads to understand use cases for e2e test scenarios)
- **Architect** (reads to align architecture with product capabilities)

**Child files:** Create child file for detailed use case (>300 words)

**Token budget guideline:** ~1000 words (~750 tokens)

---

#### 4.2.3 Product Reference
**File:** `docs/product/reference/`
**Tags:** `product`, `reference`
**Content:**
- Modules overview (logical system segmentation from user perspective)
- Data dictionaries (entities, definitions, relationships)
- Glossary (source of truth for terminology and identifiers)

**Update frequency:** When product logical structure or semantics changes

**Agents using this file:**
- **Product Owner** (writes when data model changes)
- **Architect** (reads to align technical architecture with product modules)
- **SDET** (reads for entity definitions in test data)
- **Developer** (rarely, only if confused about product terminology)

**Token budget guideline:** ~1200 words (~900 tokens)

---

#### 4.2.4 Product Decisions Record (PDR)
**File:** `docs/product/decisions.md`
**Tags:** `product`, `pdr`
**Content:**
- Historical list of product decisions (summary + link to epic PDR)
- Each entry: Decision title, date, epic link, 2-sentence summary

**Update frequency:** Per epic (updated after epic completion)

**Agents using this file:**
- **Product Owner** (reads to avoid conflicting decisions, writes PDR summaries)
- **Architect** (reads to understand product evolution, writes summary when epic completes)

**Token budget guideline:** ~100 words per decision (~75 tokens)

---

### 4.3 Architecture Documentation (Arc42-based)

Architecture documentation follows Arc42 template (12 sections) with C4 diagrams. Files live in `docs/architecture/`.

#### 4.3.1 Arc42 Section 1: Introduction and Goals
**File:** `docs/architecture/01-intro.md`
**Tags:** `architecture`, `intro`
**Content:**
- Architecture purpose and motivation
- Key stakeholders (product owner, architect, developer, SDET)
- Top 3-5 quality goals (performance, scalability, security)

**Update frequency:** During epic creation or quarterly architecture review

**Agents using this file:**
- **Architect** (writes during initial setup, updates quarterly)
- **Product Owner** (reads to understand quality goals)

**Token budget guideline:** ~400 words (~300 tokens)

---

#### 4.3.2 Arc42 Section 2: Constraints
**File:** `docs/architecture/02-constraints.md`
**Tags:** `architecture`, `constraints`
**Content:**
- Technical constraints (languages, frameworks, infrastructure limitations)
- Organizational constraints (team structure, budget, timeline)
- Conventions (coding standards, naming patterns, architectural patterns)

**Update frequency:** When constraints change (rarely)

**Agents using this file:**
- **Architect** (writes during initial setup, updates when constraints change)
- **Product Owner** (reads to understand limitations)
- **Developer** (rarely, only if questioning a constraint)

**Token budget guideline:** ~600 words (~450 tokens)

---

#### 4.3.3 Arc42 Section 3: Context and Scope
**File:** `docs/architecture/03-context.md`
**Tags:** `architecture`, `context`
**Content:**
- System Context Diagram (C4 Level 1: system + users + external systems)
- External interfaces (APIs consumed, third-party services)
- Business context (business processes this system supports)
- Technical context (protocols, data formats, channels)

**Update frequency:** When external dependencies change

**Agents using this file:**
- **Architect** (writes during initial setup, updates when integrations added)
- **Product Owner** (reads to understand system boundaries)
- **SDET** (reads to understand external systems for e2e testing)

**Child files:** Detailed external system integration specifications (>300 words per integration)

**Token budget guideline:** ~800 words (~600 tokens) for main file

---

#### 4.3.4 Arc42 Section 4: Solution Strategy
**File:** `docs/architecture/04-strategy.md`
**Tags:** `architecture`, `strategy`
**Content:**
- High-level approach to meet requirements
- Key architectural patterns (microservices, event-driven, CQRS, DDD)
- Technology decisions with rationale (why React, why PostgreSQL, why Kubernetes)
- Cross-cutting strategies (security approach, scalability approach)

**Update frequency:** When architectural approach changes (rare, high-impact)

**Agents using this file:**
- **Architect** (writes during initial setup, updates for major shifts)
- **Product Owner** (reads to understand technical approach)
- **SDET** (reads to understand testing strategy)
- **Developer** (reads to understand strategic patterns before implementing)

**Token budget guideline:** ~1000 words (~750 tokens)

---

#### 4.3.5 Arc42 Section 5: Building Block View
**File:** `docs/architecture/05-building-blocks.md`
**Tags:** `architecture`, `building-blocks`
**Content:**
- Container Diagram (C4 Level 2: applications, microservices, data stores)
- Component Diagrams (C4 Level 3: internal structure of containers)
- Component responsibilities and interfaces
- Component interaction patterns

**Update frequency:** When components added/removed/restructured

**Agents using this file:**
- **Architect** (writes during initial setup, updates when components change)
- **Product Owner** (reads to understand system structure)
- **SDET** (reads to understand component boundaries for integration testing)
- **Developer** (reads to understand component interfaces before implementing)

**Child files:** Detailed component specifications (>300 words per component)

**Token budget guideline:** ~1200 words (~900 tokens) for main file

---

#### 4.3.6 Arc42 Section 6: Runtime View
**File:** `docs/architecture/06-runtime.md`
**Tags:** `architecture`, `runtime`
**Content:**
- Key scenarios (user login, payment flow, data synchronization, error recovery)
- Sequence diagrams showing component interactions
- Interaction flows with timing considerations
- Concurrency and state management

**Update frequency:** When key flows change or new critical scenarios emerge

**Agents using this file:**
- **Architect** (writes during initial setup, updates when flows change)
- **SDET** (reads extensively for e2e test scenario design)
- **Developer** (reads to understand interaction patterns)

**Child files:** Detailed scenario specifications with sequence diagrams (>300 words per scenario)

**Token budget guideline:** ~1000 words (~750 tokens) for main file

---

#### 4.3.7 Arc42 Section 7: Deployment View
**File:** `docs/architecture/07-deployment.md`
**Tags:** `architecture`, `deployment`
**Content:**
- Infrastructure overview (cloud provider, regions, availability zones)
- Deployment diagrams (C4 deployment: nodes, containers, relationships)
- Deployment strategies (blue-green, canary, rolling updates)
- Infrastructure as code approach

**Update frequency:** When infrastructure changes

**Agents using this file:**
- **Architect** (writes during initial setup, updates when infrastructure changes)

**Child files:** Detailed infrastructure specifications (Kubernetes manifests, AWS resources) (>300 words)

**Token budget guideline:** ~800 words (~600 tokens) for main file

---

#### 4.3.8 Arc42 Section 8: Cross-cutting Concepts
**Directory:** `docs/architecture/08-cross-cutting/`
**Tags:** `architecture`, `cross-cutting`
**Content:** Overview linking to 4 child files

**Child Files (Required):**
1. **Domain Model & Patterns** (`domain-model.md`)
   - **Tags:** `architecture`, `cross-cutting`, `domain-model`
   - **Content:** Domain entities, ubiquitous language, transaction management, API conventions
   - **Primary Readers:** Developer, SDET
   - **Token budget:** ~1100 tokens

2. **Security** (`security.md`)
   - **Tags:** `architecture`, `cross-cutting`, `security`
   - **Content:** Authentication, authorization, data protection, security headers, compliance
   - **Primary Readers:** Architect, Developer, SDET
   - **Token budget:** ~1300 tokens

3. **Operations** (`operations.md`)
   - **Tags:** `architecture`, `cross-cutting`, `operations`
   - **Content:** Error handling, logging, caching, configuration management
   - **Primary Readers:** Architect, Developer, SDET
   - **Token budget:** ~1400 tokens

4. **Testing** (`testing.md`)
   - **Tags:** `architecture`, `cross-cutting`, `testing`
   - **Content:** Test levels (unit/integration/E2E), coverage targets, test data management
   - **Primary Readers:** SDET, Developer
   - **Token budget:** ~1200 tokens

**Update frequency:** When cross-cutting patterns introduced or changed

**Token budget guideline:** ~200 words (~150 tokens) for main overview

---

#### 4.3.9 Arc42 Section 9: Architecture Decisions (ADR)
**File:** `docs/architecture/09-adr.md`
**Tags:** `architecture`, `adr`
**Content:**
- Historical list of architectural decisions (summary + link to epic ADR)
- High-impact decisions with brief context (why, what, consequences)
- Each entry: Decision title, date, epic link, 3-sentence summary

**Update frequency:** Per epic (updated by /audit_epic and follow up implementations)

**Agents using this file:**
- **Architect** (reads to avoid conflicting decisions, writes ADR summaries when epic completes)
- **Developer** (reads to understand why certain patterns exist)

**Token budget guideline:** ~150 words per decision (~112 tokens)

---

#### 4.3.10 Arc42 Section 10: Quality Requirements
**File:** `docs/architecture/10-quality.md`
**Tags:** `architecture`, `quality`
**Content:**
- Performance requirements (API latency <100ms, throughput >10K req/sec)
- Scalability requirements (concurrent users, data volume growth)
- Availability requirements (uptime SLA 99.9%, RTO, RPO)
- Security requirements (compliance, encryption standards, audit logging)
- Maintainability requirements (code coverage, documentation standards)

**Update frequency:** When quality targets change (annually or per major release)

**Agents using this file:**
- **Architect** (writes during initial setup, updates when targets change)
- **Product Owner** (reads to understand quality commitments)
- **SDET** (reads extensively for performance and load testing targets)
- **Developer** (reads for optimization priorities)

**Child files:** Detailed quality specifications (load testing results, performance benchmarks) (>300 words)

**Token budget guideline:** ~1000 words (~750 tokens) for main file

---

#### 4.3.11 Arc42 Section 11: Risks and Technical Debt
**File:** `docs/architecture/11-risks.md`
**Tags:** `architecture`, `risks`
**Content:**
- Known risks (performance bottlenecks, scalability limits, security vulnerabilities)
- Technical debt registry (shortcuts taken, areas needing refactoring)
- Mitigation strategies and timelines
- Risk severity and probability assessment

**Update frequency:** Continuous (risks/debt added during epics, resolved items archived)

**Agents using this file:**
- **Architect** (writes risks/debt, updates mitigation strategies)
- **Product Owner** (reads to understand technical constraints)
- **Developer** (reads to understand debt context, writes debt during implementation)

**Token budget guideline:** ~100 words per risk/debt item (~75 tokens)

---

#### 4.3.12 Arc42 Section 12: Glossary
**File:** `docs/architecture/12-glossary.md`
**Tags:** `architecture`, `glossary`
**Content:**
- Architecture-specific terminology (technical terms, acronyms, patterns)
- Component names and abbreviations
- Technology-specific jargon

**Note:** Product glossary lives in Product Reference (`docs/product/reference/terminology.md`)

**Update frequency:** As new terms introduced

**Agents using this file:**
- **Architect** (writes new terms)
- **All agents** (read for terminology clarification)

**Token budget guideline:** ~50 words per term (~37 tokens)

---

### 4.4 Epic Documentation

Epic documentation provides detailed context for implementation teams. Created during epic refinement by architect and product owner. Files live in `docs/epics/{epic-id}/`.

#### 4.4.1 Epic Details (Main File)
**File:** `docs/epics/{epic-id}/details.md`
**Tags:** `epic`, `{epic-id}`, `epic-details`
**Example:** `docs/epics/SCOPE-42/details.md` with tags `epic`, `SCOPE-42`, `epic-details`

**Content:**
- Intent and purpose (the "why")
- Requirements (functional and non-functional)
- Impact, value, capabilities to deliver
- Acceptance criteria
- Integration/e2e test scenarios overview (live services vs mocks)
- Core components and expected tech stack
- Risks and concerns
- Links: Epic ADR | Epic PDR | Epic File Plan | Epic Implementation Summary

**Agents using this file:**
- **Product Owner** (writes during epic refinement)
- **Architect** (writes during epic refinement, contributes technical sections)
- **SDET** (reads for acceptance criteria and test scenarios)
- **Developer** (rarely, usually reads story description which is self-contained)

**Token budget guideline:** ~1500 words (~1125 tokens)

---

#### 4.4.2 Epic Architecture Specification
**File:** `docs/epics/{epic-id}/architecture.md`
**Tags:** `epic`, `{epic-id}`, `architecture`

**Content:**
- Which building blocks (Arc42 Section 5) are affected
- Which runtime scenarios (Arc42 Section 6) are involved
- C4 diagrams specific to this epic (component diagrams, sequence diagrams)
- Component interfaces and contracts
- Integration points

**Agents using this file:**
- **Architect** (writes during epic refinement)
- **SDET** (reads for integration test boundaries)
- **Developer** (reads to understand component structure)

**Token budget guideline:** ~800 words (~600 tokens)

---

#### 4.4.3 Epic ADR
**File:** `docs/epics/{epic-id}/adr.md`
**Tags:** `epic`, `{epic-id}`, `adr`

**Content:**
- Detailed architectural decisions for this epic
- Each decision: Context, Options considered, Decision made, Consequences
- Maps to Arc42 Section 9 (summary added by Architect after epic completion)

**Child files:** Decision justifications (>300 words)
- Example: "JWT vs Sessions" decision with 5 options, detailed pros/cons (800 words) → child file

**Agents using this file:**
- **Architect** (writes during epic refinement, updates during implementation if developer escalates, creates ADR summary for Architecture ADR file)
- **Developer** (reads when implementation approach unclear)

**Token budget guideline:** ~2000 words (~1500 tokens) for main file, child files as needed

---

#### 4.4.4 Epic PDR
**File:** `docs/epics/{epic-id}/pdr.md`
**Tags:** `epic`, `{epic-id}`, `pdr`

**Content:**
- Detailed product decisions for this epic
- Each decision: Context, Options considered, Decision made, Impact on users/business
- If multiple options considered, list options not chosen with rationale

**Child files:** Decision justifications (>300 words)
- Example: "Pricing model selection" with 4 pricing strategies, market analysis (600 words) → child file

**Agents using this file:**
- **Product Owner** (writes during epic refinement)
- **Architect** (reads to understand product decisions, writes PDR summary to Product Decisions Record file)

**Token budget guideline:** ~1000 words (~750 tokens) for main file, child files as needed

---

#### 4.4.5 Epic File Plan
**File:** `docs/epics/{epic-id}/file-plan.md`
**Tags:** `epic`, `{epic-id}`, `file-plan`

**Content:**
- Pure YAML format (no markdown)
- File path + intent (600-1200 chars per file)
- Intent format: Purpose, Responsibilities, Key interactions, Why this file, Related modules

**Usage pattern:**
- File plan is read directly from `docs/epics/{epic-id}/file-plan.md`
- Per-story file plans stored in `.scope/{epic-id}/file_plan.json`
- Creates per-story file plan for relevant files

**Agents using this file:**
- **Architect** (writes during epic refinement)
- **Developer** (reads for implementation context)

**Token budget guideline:** ~1000 words (~750 tokens) total for all files

---

### 4.5 Release Documentation

Release documentation tracks factual releases only (not roadmap, not forward-looking). Files live in `docs/releases/{version}/`.

**Per-release directory structure:**

#### Release X.Y.Z (e.g., Release 2.4.1)
**Tags:** `release`, `{release-id}`
**Example:** `docs/releases/2.4.1/` with tags `release`, `aqua-release-2.4.1`

**Content:**
- Release Record (tag: `release`, `{release-id}`, `record`)
  - List of epics and/or stories included
  - Release date and version
  - Links to epic implementation summaries

- Release Notes (tag: `release`, `{release-id}`, `notes`)
  - Internal release notes (for team, detailed technical changes)
  - External release notes (for customers, user-facing changes)

- Post-mortem (tag: `release`, `{release-id}`, `post-mortem`)
  - What went well, what didn't
  - Lessons learned
  - Process improvements

**Update trigger:** Release planned by user

**Agents using these files:**
- **Architect** (creates release record)
- **Product Owner** (writes release notes)
- **User** (writes post-mortem after release)

**Token budget guideline:** ~500 words per release section (~375 tokens)

---

### 4.7 Child File Guidelines

**Create child file when content exceeds 300 words (~225 tokens) for a single topic within ADR or PDR.**

**Rationale:**
- Main ADR/PDR file remains scannable
- Child files provide deep context for critical decisions
- Agents read child files only when needed (progressive disclosure)
- Historical significance preserved without bloating main file

**Example scenarios for child files:**

1. **ADR Decision Justification:**
   - Main ADR: "Decision: Use JWT for authentication (see child file for full analysis)"
   - Child file: `jwt-vs-sessions.md` (5 options, detailed pros/cons, 800 words)

2. **PDR Market Analysis:**
   - Main PDR: "Decision: Usage-based pricing (see child file for analysis)"
   - Child file: `pricing-model-analysis.md` (4 strategies, market research, 600 words)

3. **Architecture Component Specification:**
   - Main Building Blocks: "Auth Service handles authentication (see child file for details)"
   - Child file: `auth-service-spec.md` (interfaces, endpoints, state machine, 1000 words)

**Agent responsibility:** Relevant agent (architect, product owner) creates child file during epic refinement when they recognize content will exceed 300 words.

**Parent file format:**
```markdown
## Decision 3: Authentication Approach

**Context:** Need stateless authentication for multi-region deployment.

**Decision:** Use JWT tokens with RS256 signing.

**Rationale:** See [JWT vs Sessions Analysis](./jwt-vs-sessions.md) for detailed comparison of 5 options.

**Consequences:**
- Stateless authentication enables horizontal scaling
- Token refresh mechanism needed
- Key rotation strategy required
```

---

### 4.8 Token Budget Guidelines

Token budgets are **guidelines, not hard limits**. As product scales to 100+ epics, some files will grow significantly. Documentation quality trumps size.

**Warning system:** When file exceeds guideline, agent should:
1. Consider if content can be split into child files (>300 words per topic)
2. Consider if content is redundant with other files (link instead of duplicate)
3. If content is essential and cannot be split, allow file to grow

**Guideline enforcement:**
- The `project-documentation` skill checks file size before update
- If file exceeds guideline by >50%, warn agent
- Agent decides whether to proceed or refactor

**Example warning:**
```
File "docs/architecture/08-cross-cutting/security.md" is 2400 words (guideline: 1500 words).
Consider creating child files for:
- Security patterns (400 words) → child file
- Event schema details (500 words) → child file
```

---

### 4.9 Agent-File Mapping (Critical)

This table defines which agents need which files. Each agent's instructions reference this mapping.

| Agent | Product Docs | Architecture Docs (Arc42) | Epic Docs | Release Docs |
|-------|--------------|---------------------------|-----------|--------------|
| **Product Owner** | Strategy (R/W)<br>Definition (R/W)<br>Reference (R/W)<br>PDR (R/W) | Intro & Goals (R)<br>Quality Requirements (R) | Epic Details (W)<br>Epic PDR (W) | Release Record (R) |
| **Architect** | Strategy (R)<br>Definition (R) | All 12 sections (R/W)<br>Primary owner | Epic Details (W)<br>Epic Architecture (W)<br>Epic ADR (W)<br>Epic File Plan (W)<br>Epic Implementation Summary (W) | Release Record (W) |
| **SDET** | Definition (R) | Runtime View (R)<br>Quality Requirements (R)<br>Cross-cutting (R) | Epic Details (R)<br>Epic Architecture (R) | - |
| **Developer** | - | Building Blocks (R, rarely)<br>Cross-cutting (R, frequently) | Epic ADR (R, if confused)<br>File Plan (R, via local cache) | - |

**Legend:**
- **R** = Read
- **W** = Write
- **R/W** = Read and Write

---

### 4.10 Update Responsibilities

Clear ownership prevents conflicting updates.

| File | Primary Owner | Update Trigger | Secondary Contributors |
|------|---------------|----------------|------------------------|
| Product Strategy | Product Owner | Quarterly review, customer insights | - |
| Product Definition | Product Owner | Capability changes | Architect (review) |
| Product Reference | Product Owner | Data model changes | Architect (review) |
| Product PDR | Product Owner | Per epic | Architect (summaries) |
| Architecture Intro & Goals | Architect | Initial setup, quarterly review | - |
| Architecture Constraints | Architect | Constraint changes (rare) | - |
| Architecture Context & Scope | Architect | External integration changes | - |
| Architecture Solution Strategy | Architect | Strategic shift (rare) | - |
| Architecture Building Blocks | Architect | Component changes | - |
| Architecture Runtime View | Architect | Flow changes | SDET (test scenarios) |
| Architecture Deployment | Architect | Infrastructure changes | - |
| Architecture Cross-cutting | Architect | Pattern changes | - |
| Architecture ADR Summary | Architect | Per epic | - |
| Architecture Quality Requirements | Architect | Annual review, quality target changes | Product Owner (business SLAs) |
| Architecture Risks & Technical Debt | Architect | Continuous | Developer (debt) |
| Architecture Glossary | Architect | As new terms introduced | All agents (contribute) |
| Epic Details | Product Owner, Architect | Epic refinement | SDET (acceptance criteria) |
| Epic Architecture | Architect | Epic refinement | - |
| Epic ADR | Architect | Epic refinement, implementation escalations | - |
| Epic PDR | Product Owner | Epic refinement | - |
| Epic File Plan | Architect | Epic refinement | - |
| Epic Implementation Summary | Architect | After epic completion | - |
| Release Record | Architect | Release planning | - |
| Release Notes | Product Owner | After release deployment | - |
| Release Post-mortem | User | After release | - |

---

### 4.11 Versioning Strategy

**Living documentation principle:** All documentation has one version, always up-to-date.

**Component versioning approach:**
- Components (microservices, APIs, tools, libraries) have versions
- When component X upgrades (v1.0 → v2.0), create epic "Upgrade Component X to v2.0"
- Epic ADR documents upgrade decisions
- Architecture files (Building Blocks, Deployment, etc.) updated to reflect v2.0
- Historical context preserved in epic ADR and Architecture ADR Summary

**Industry standard:** This is standard practice in continuous delivery environments (Netflix, Spotify, Amazon).

**Risk mitigation (stale epic):**

**Scenario:** Epic A prepared (ADR references Auth Service v1.0), Epic B upgrades to v2.0, Epic A starts implementation.

**Mitigations:**
1. **Architect validation** - Before marking "Implementation Ready", validate ADR links/references are current
2. **Agent adaptation** - Developer detects mismatch, escalates to architect, epic ADR updated
3. **Dependency tracking** - Story has "Dependencies" field, checked before starting

**User responsibility:** If epic prepared but later epic changes dependency, user assesses whether:
- Epic needs updating before implementation
- Agentic team can adapt during implementation (typical case)

---

### 4.12 Search Strategy

Clear guidance on how to find documentation files using file path conventions and standard tools.

| Query Type | Method | Example |
|------------|--------|---------|
| **Single file retrieval** | Path | `docs/epics/SCOPE-42/adr.md` → Epic ADR for SCOPE-42 |
| **All files of type** | Glob | `docs/epics/*/adr.md` → All epic ADRs |
| **Content search** | Grep | `grep -r "JWT" docs/epics/` → Find all references to JWT across epics |
| **Architecture search** | Read | `docs/architecture/10-quality.md` → Quality Requirements file |
| **Product search** | Read | `docs/product/strategy.md` → Product Strategy file |

**Agent instructions:**
- Use **direct file paths** when exact file location known (deterministic, fastest)
- Use **glob patterns** when searching across multiple files of the same type
- Use **grep** when searching for specific content across the documentation

---

### 4.13 Lean Implementation Approach

**Principle:** Implement all 12 Arc42 sections from the start, but keep each section lean initially. Evolve as product scales.

**Initial content (first epic):**

| Arc42 Section | Initial Content | Growth Trigger |
|---------------|-----------------|----------------|
| 1. Intro & Goals | Vision + 3 quality goals (300 words) | Quarterly review (add stakeholder needs) |
| 2. Constraints | 5-10 key constraints (400 words) | When new constraint discovered |
| 3. Context & Scope | C4 L1 diagram + 3 external systems (600 words) | When integration added |
| 4. Solution Strategy | 3-5 key patterns (600 words) | When pattern changes |
| 5. Building Blocks | C4 L2 diagram + 5 components (800 words) | When component added |
| 6. Runtime View | 2-3 key scenarios (600 words) | When critical flow added |
| 7. Deployment | Infrastructure diagram + deployment strategy (600 words) | When infrastructure changes |
| 8. Cross-cutting | Security + communication + persistence (1000 words) | When pattern introduced |
| 9. ADR Summary | Empty initially (grows per epic) | Per epic (ADR summary added) |
| 10. Quality Requirements | 3-5 key SLAs (600 words) | Annual review or when SLA changes |
| 11. Risks & Technical Debt | Empty initially (grows during implementation) | Continuous (risks/debt added) |
| 12. Glossary | 10-20 key terms (300 words) | As new terms introduced |

**Evolution example (after 50 epics):**
- Section 9 (ADR Summary): 50 decision summaries (~7500 words)
- Section 11 (Risks & Debt): 30 items (~3000 words)
- Section 8 (Cross-cutting): Grown to 2000 words with 5 child files
- Other sections: Modest growth (50-100% increase)

**Rationale:** Starting with all 12 sections ensures proper information architecture from day one. Prevents costly refactoring later ("where should this go?"). Each section has clear purpose, agents know where to find/write content.

---

### 4.14 Template Storage

Templates are stored in the project-documentation skill directory, separated by content type (product vs technical).

**Location pattern:**
```
.claude/skills/project-documentation/
├── SKILL.md                          # Skill definition with agent routing logic
├── product-guide-atlassian.md        # Product documentation guide
├── technical-guide-arc42-c4.md       # Technical documentation guide
├── templates-product-atlassian/
│   ├── overview.md                   # Auto-generated summary file
│   ├── strategy.md
│   ├── definition.md
│   ├── decisions.md
│   └── reference/
│       ├── parent.md                 # Auto-generated summary
│       ├── use-case.md
│       ├── feature-catalog.md
│       ├── terminology-data-model.md
│       ├── ui-workflows.md
│       └── apis-integrations.md
├── templates-technical-arc42-c4/
│   ├── architecture/
│   │   ├── intro.md
│   ├── architecture-constraints.md
│   ├── architecture-context.md
│   ├── architecture-strategy.md
│   ├── architecture-building-blocks.md
│   ├── architecture-runtime.md
│   ├── architecture-deployment.md
│   ├── architecture-cross-cutting.md
│   ├── architecture-adr.md
│   ├── architecture-quality.md
│   ├── architecture-risks.md
│   ├── architecture-glossary.md
│   ├── epic-details.md
│   ├── epic-architecture.md
│   ├── epic-adr.md
│   ├── epic-pdr.md
│   ├── epic-file-plan.json
│   └── epic-implementation-summary.md
```

**Rationale:** Templates are stored in the `project-documentation` skill directory. The skill handles both product and technical templates, writing output to the `docs/` directory.

**Skill references templates:**
```markdown
## create_epic_details Operation

Uses template: `templates-technical-arc42-c4/epic-details.md`
Writes to: `docs/epics/{epic-id}/details.md`

Populates placeholders:
- {epic_id}
- {epic_title}
- {epic_purpose}
- {requirements}
- ...
```

---

### 4.15 Summary

**Key decisions:**
- **Framework:** Arc42 (12 sections) + C4 diagrams + Product sections
- **Single skill:** The `project-documentation` skill handles both product and technical templates, writing to `docs/`
- **Template separation:** `templates-product-atlassian/` and `templates-technical-arc42-c4/` for clean organization
- **Config structure:** `technical-doc: arc42-c4` and `product-doc: atlassian` replace single `method:` field
- **Implementation:** All 12 sections from start, keep lean, evolve
- **Tags:** Separate tags (not composite) for flexible queries
- **Child files:** Created when topic exceeds 300 words
- **Token budgets:** Guidelines (not limits), quality > size
- **Versioning:** Component versioning (not file versioning), living docs
- **Story ADR:** Only epic-level ADR (not story-level)
- **Agent-file mapping:** Explicit (see Section 4.9)
- **Existing agents:** Product Owner, Architect, SDET, Developer, Reverse-Engineer-Architect, Reverse-Engineer-PM

**Config example:**
```yaml
documentation:
  skill: project-documentation
  technical-doc: arc42-c4   # → technical-guide-arc42-c4.md + templates-technical-arc42-c4/
  product-doc: atlassian    # → product-guide-atlassian.md + templates-product-atlassian/
```

**Token efficiency:**
- Product Owner: Loads product guide (2k tokens)
- Architect: Loads both guides as needed
- Developer: No guide loading (uses file paths from epic docs) - **2k tokens saved**
- SDET: No guide loading (uses direct file reads) - **2k tokens saved**

**Scalability:** Designed for 100+ epics, 5+ years continuous development, enterprise-grade systems.

**Agent efficiency:** Clear boundaries, targeted file reads, progressive disclosure via child files.
