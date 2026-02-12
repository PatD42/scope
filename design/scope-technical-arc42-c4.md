# SCOPE - Arc42 + C4 Documentation Standard

Why spend so many tokens on documentation? Because Scope goes beyond prototyping and vibe coding to delivery enterprise-grade products that can evolve through hundreds of epics. To perform well in these conditions, any organizations need to have a reliable documentation.

---

## Table of Contents

- [0. Overview](#Overview)
- [1. Arc42 + C4?](#arc42--c4)
- [2. Example Documentation Structure](#example-documentation-structure)
- [3. Agent Responsibilities Summary](#agent-responsibilities-summary)
- [4. Detailed Page Specifications](#4-detailed-page-specifications)
  - [4.1 Framework Overview](#41-framework-overview)
  - [4.2 Product Documentation](#42-product-documentation-confluence)
  - [4.3 Architecture Documentation](#43-architecture-documentation-confluence---arc42-based)
  - [4.4 Epic Documentation](#44-epic-documentation-confluence)
  - [4.5 Release Documentation](#45-release-documentation-confluence)
  - [4.6 Tracking Structure](#46-tracking-structure-jira)
  - [4.7 Child Page Guidelines](#47-child-page-guidelines)
  - [4.8 Token Budget Guidelines](#48-token-budget-guidelines)
  - [4.9 Agent-Page Mapping (Critical)](#49-agent-page-mapping-critical)
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
1. **Documentation structure**: agents should not guess and iterate at finding the right content, and **must not** be wrong when selecting where to create new content. This is implemented using 3 levels of files:
  - Documentation standard → Skill wrapper → Backend documentation tool (ex.: Arc42+C4 → `project-documentation` skill → confluence-sooperset-mcp backend)
  - **Dual-guide system**: Product documentation (product-guide-atlassian.md) and Technical documentation (technical-guide-arc42-c4.md) are maintained separately
2. **Agent responsibilities**: Each section of the documentation must have clear owners, and ideally clear triggers as to when pages get updated. This is implemented using 2 levels:
  - Documentation standard → Agent responsibilities
  - Each standard defines what agents are responsible to document, and what they should read to do their tasks
  - **Agent self-awareness**: Agents determine guide loading based on their role (Product Owner, Architect load guides; Developer, SDET access via URLs)

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
4. **Traceability** - ADR/PDR link decisions to epics; epic summaries link to architecture/product pages
5. **Quality accountability** - Quality requirements (Arc42 Section 10) and technical debt registry (Section 11) make SLAs and shortcuts explicit
6. **Deterministic queries** - Tag-based navigation enables reliable page retrieval (label = "epic" AND label = "SCOPE-42" AND label = "adr")

---

## Agent Responsibilities Summary

This section provides a high-level overview of which agents interact with which documentation/tracking systems.

### By Agent

| Agent | Reads (Documentation) | Writes (Documentation) | Contributes To (Documentation) | Reads (Tracking) | Writes (Tracking) | Contributes To (Tracking) |
|-------|----------------------|------------------------|--------------------------------|------------------|-------------------|---------------------------|
| **Product Owner** | Product Strategy/Definition/Reference<br>Architecture Quality Requirements | Product pages (all 4)<br>Epic PDR | - | Epic (status)<br>Story (context) | Epic (create, update status) | - |
| **Architect** | Product Strategy/Definition<br>Architecture (all sections + cross-cutting pages) | Architecture (all sections + cross-cutting pages)<br>Epic Details (technical)<br>Epic Architecture<br>Epic ADR<br>Epic File Plan | - | Epic (status/dependencies)<br>Story (context) | Story (create) | Epic (technical content) |
| **SDET** | Product Definition<br>Architecture Runtime/Quality/Testing<br>Epic Details/Architecture | - | - | Story (detailed) | - | Story (acceptance criteria) |
| **Developer** | Architecture Domain Model/Operations<br>Epic ADR (if story context insufficient) | `.scope/{story-id}/agent_summaries.jsonl`<br>(NOT documentation) | - | Story (primary source) | `.scope/{story-id}/agent_summaries.jsonl`<br>(NOT tracking) | - |
| **Security Reviewer** | Architecture Context/Strategy/Security/Quality<br>Epic Details/ADR | Epic ADR (security decisions) | Architecture Security<br>Architecture Risks | - | - | - |
| **DevOps** | Architecture Context/Deployment/Operations<br>Epic Architecture (if infra changes) | - | Architecture Deployment<br>Architecture Operations | - | - | - |
| **Epic Housekeeping** | `.scope/{epic-id}/agent_summaries.jsonl`<br>Epic ADR<br>Epic PDR | Product PDR (summaries)<br>Architecture ADR Summary<br>Epic Implementation Summary | - | Epic (status)<br>Story (all statuses) | Epic (set Done) | - |
| **Release Documentation** | Epic Implementation Summaries | Release Notes | - | Epic/Story (release scope) | - | - |
| **Release Planner** | Epic Implementation Summaries | Release Record | - | Epic/Story (release scope, status) | - | - |

### By Documentation Type

| Documentation Type | Primary Owner | Secondary Contributors | Update Frequency |
|--------------------|---------------|------------------------|------------------|
| **Product Strategy** | Product Owner | - | Quarterly or strategic shift |
| **Product Definition** | Product Owner | Architect (review) | When capabilities change |
| **Product Reference** | Product Owner | Architect (review) | When data model changes |
| **Product PDR** | Product Owner | Epic Housekeeping (summaries) | Per epic |
| **Architecture (all 12 sections)** | Architect | DevOps, Security Reviewer (contribute) | Varies by section (see Section 2.10) |
| **Epic Details** | Product Owner + Architect | SDET, Security Reviewer | During epic refinement |
| **Epic Architecture/ADR/File Plan** | Architect | Security Reviewer (ADR security) | During epic refinement |
| **Epic PDR** | Product Owner | - | During epic refinement |
| **Epic Implementation Summary** | Epic Housekeeping | - | After epic completion |
| **Release Pages** | Release Planner, Release Documentation | User (post-mortem) | Per release |
| **Jira Epic** | Product Owner | Architect, Epic Housekeeping | Throughout epic lifecycle |
| **Jira Story** | Architect | SDET, Developer | Throughout story lifecycle |

### By Phase

| Phase | Active Agents | Documentation Activities | Tracking Activities |
|-------|---------------|--------------------------|---------------------|
| **Epic Refinement** | Product Owner, Architect, SDET, Security Reviewer | Write: Product pages (if needed), Epic Details, Epic Architecture, Epic ADR, Epic PDR, Epic File Plan<br>Read: Product/Architecture context | Write: Epic (create), Stories (create)<br>Read: Dependencies |
| **Implementation** | Developer, SDET | Read: Story (self-contained), Epic ADR (if confused), Architecture Cross-cutting<br>Write: Technical debt notes | Write: Story status updates<br>Read: Story details |
| **Epic Completion** | Epic Housekeeping | Write: Product PDR summaries, Architecture ADR summaries, Epic Implementation Summary<br>Read: `.scope/` agent summaries, Epic ADR, Epic PDR | Write: Epic status to Done<br>Read: All story statuses |
| **Release Planning** | Release Planner | Read: Epic Implementation Summaries | Write: Release record<br>Read: Epic/Story scope |
| **Release Deployment** | Release Documentation | Write: Release notes<br>Read: Epic Implementation Summaries | Read: Release scope |

---

## Example Documentation Structure

This section provides concrete examples of how documentation is organized in Confluence and Jira. Similar structure will be used with different backend (ex.: file based)

### Confluence Space Structure

```
Product Documentation Space (e.g., "MyProduct Docs")
│
├── Product (parent page)
│   ├── Product Strategy                     (tag: product, strategy)
│   ├── Product Definition                   (tag: product, definition)
│   ├── Product Reference                    (tag: product, reference)
│   └── Product Decisions Record (PDR)       (tag: product, pdr)
│
├── Architecture (parent page)
│   ├── Architecture - Introduction & Goals  (tag: architecture, intro)
│   ├── Architecture - Constraints           (tag: architecture, constraints)
│   ├── Architecture - Context & Scope       (tag: architecture, context)
│   │   └── [Child] AWS S3 Integration Spec  (>300 words)
│   ├── Architecture - Solution Strategy     (tag: architecture, strategy)
│   ├── Architecture - Building Blocks       (tag: architecture, building-blocks)
│   │   └── [Child] Auth Service Spec        (>300 words)
│   ├── Architecture - Runtime View          (tag: architecture, runtime)
│   │   └── [Child] User Login Flow          (>300 words)
│   ├── Architecture - Deployment            (tag: architecture, deployment)
│   ├── Architecture - Cross-cutting (main)  (tag: architecture, cross-cutting)
│   │   ├── [Child] Domain Model & Patterns  (tag: architecture, cross-cutting, domain-model)
│   │   ├── [Child] Security                 (tag: architecture, cross-cutting, security)
│   │   ├── [Child] Operations               (tag: architecture, cross-cutting, operations)
│   │   └── [Child] Testing                  (tag: architecture, cross-cutting, testing)
│   ├── Architecture - ADR Summary           (tag: architecture, adr)
│   ├── Architecture - Quality Requirements  (tag: architecture, quality)
│   │   └── [Child] Acceptance Criteria      (tag: architecture, quality, criteria)
│   ├── Architecture - Risks & Tech Debt     (tag: architecture, risks)
│   └── Architecture - Glossary              (tag: architecture, glossary)
│
├── Releases (parent page)
│   ├── Release 2.4.1                        (tag: release, myproduct-2.4.1)
│   │   ├── Release Record
│   │   ├── Release Notes
│   │   └── Post-mortem
│   └── Release 2.5.0                        (tag: release, myproduct-2.5.0)
│
└── Epics (parent page)
    ├── SCOPE-42 - OAuth Integration         (tag: epic, SCOPE-42, epic-details)
    │   ├── [Child] Epic Architecture        (tag: epic, SCOPE-42, architecture)
    │   ├── [Child] Epic ADR                 (tag: epic, SCOPE-42, adr)
    │   │   └── [Child] JWT vs Sessions      (>300 words justification)
    │   ├── [Child] Epic PDR                 (tag: epic, SCOPE-42, pdr)
    │   ├── [Child] Epic File Plan           (tag: epic, SCOPE-42, file-plan)
    │   └── [Child] Epic Impl Summary        (tag: epic, SCOPE-42, summary)
    │
    └── SCOPE-55 - Payment Gateway           (tag: epic, SCOPE-55, epic-details)
        ├── [Child] Epic Architecture
        ├── [Child] Epic ADR
        ├── [Child] Epic PDR
        ├── [Child] Epic File Plan
        └── [Child] Epic Impl Summary
```

### Jira Project Structure

```
Jira Project (e.g., "SCOPE")
│
├── Epic: SCOPE-42 - OAuth Integration
│   ├── Description:
│   │   - Link to Confluence epic page
│   │   - 200-word summary (same as Confluence)
│   │   - Tech stack: Node.js, React, OAuth 2.0
│   │   - Customer problem summary
│   │   - Capabilities/requirements summary
│   │   - Acceptance criteria summary
│   │   - Key metrics (business value, complexity)
│   │
│   ├── Custom Fields:
│   │   - Dependencies: [SCOPE-40, SCOPE-41]
│   │
│   ├── Standard Fields:
│   │   - Fix Version: 2.5.0
│   │
│   └── Stories:
│       ├── SCOPE-43 - Implement OAuth Provider Interface
│       │   ├── Description:
│       │   │   - Story: "As a developer, I want..."
│       │   │   - Tech stack: Node.js, TypeScript
│       │   │   - Technical scope: Create src/auth/oauth_provider.ts
│       │   │   - Detailed acceptance criteria (5-10 items)
│       │   │   - Link to file plan (specific files)
│       │   │   - Technical notes
│       │   │   - Reference to Epic ADR (link to section)
│       │   │
│       │   └── Standard Fields:
│       │       - Epic Link: SCOPE-42
│       │
│       ├── SCOPE-44 - Add JWT Token Validation
│       └── SCOPE-45 - Implement Token Refresh
│
└── Epic: SCOPE-55 - Payment Gateway
    └── Stories: ...
```

---

## 4. Detailed Page Specifications

This section provides detailed specifications for each page type, including content, tags, update frequency, and agent usage.

### 4.1 Framework Overview

**Arc42 + C4 Hybrid Approach:**
- **Arc42** provides comprehensive architecture documentation (12 sections)
- **C4 diagrams** provide visual clarity (4 levels: Context, Container, Component, Code)
- **Product sections** extend Arc42 with strategy, use cases, and glossary
- **Living documentation** always up-to-date, component versioning (not page versioning)

**Implementation principle:** Start with all 12 Arc42 sections immediately, keep each section lean initially, evolve as product scales.

**Tag-based navigation:** Use separate tags (not composite) to enable flexible queries.
- Example: `tag: epic, epic-id, adr` enables "find all epic ADRs"
- Rovo Search handles complex queries (date ranges, properties)

### 4.2 Product Documentation (Confluence)

**NOTE**: Product documentation structure has been moved to a separate document: `scope-product-atlassian.md`. This section provides a brief overview for context.

Product documentation uses the Atlassian Confluence Blueprint pattern adapted for backend-agnostic, markdown-based workflows with progressive disclosure. See `scope-product-atlassian.md` for comprehensive details.

Product documentation lives in dedicated Confluence space. User manually creates space and home page.

#### 4.2.1 Product Strategy
**Page:** Product Strategy
**Tags:** `product`, `strategy`
**Content:**
- Vision statement (purpose, north star, in-scope, out-of-scope)
- Target markets (segments, personas, product-market fit)
- Customer problems (pain points, intrinsic drivers)
- Links to detailed market research, go-to-market strategy

**Update frequency:** As customer insights evolve (quarterly or when strategic shift occurs)

**Agents using this page:**
- **Product Owner** (reads during epic creation, writes during quarterly updates)
- **Architect** (reads during epic creation to understand business context)

**Token budget guideline:** ~800 words (~600 tokens)

---

#### 4.2.2 Product Definition
**Page:** Product Definition
**Tags:** `product`, `definition`
**Content:**
- Use cases & user journeys (goals, flows, links to epic details)
- Capability map & feature matrix (areas, value props, differentiation, dependencies, out-of-scope/won't-do)

**Update frequency:** When product capabilities or user intent materially change

**Agents using this page:**
- **Product Owner** (reads during epic creation, writes when capabilities change)
- **SDET** (reads to understand use cases for e2e test scenarios)
- **Architect** (reads to align architecture with product capabilities)

**Child pages:** Create child page for detailed use case (>300 words)

**Token budget guideline:** ~1000 words (~750 tokens)

---

#### 4.2.3 Product Reference
**Page:** Product Reference
**Tags:** `product`, `reference`
**Content:**
- Modules overview (logical system segmentation from user perspective)
- Data dictionaries (entities, definitions, relationships)
- Glossary (source of truth for terminology and identifiers)

**Update frequency:** When product logical structure or semantics changes

**Agents using this page:**
- **Product Owner** (writes when data model changes)
- **Architect** (reads to align technical architecture with product modules)
- **SDET** (reads for entity definitions in test data)
- **Developer** (rarely, only if confused about product terminology)

**Token budget guideline:** ~1200 words (~900 tokens)

---

#### 4.2.4 Product Decisions Record (PDR)
**Page:** Product Decisions Record
**Tags:** `product`, `pdr`
**Content:**
- Historical list of product decisions (summary + link to epic PDR)
- Each entry: Decision title, date, epic link, 2-sentence summary

**Update frequency:** Per epic (updated by epic-housekeeping agent)

**Agents using this page:**
- **Product Owner** (reads to avoid conflicting decisions, writes PDR summaries)
- **Architect** (reads to understand product evolution)
- **Epic Housekeeping** (writes summary when epic completes)

**Token budget guideline:** ~100 words per decision (~75 tokens)

---

### 4.3 Architecture Documentation (Confluence - Arc42-based)

Architecture documentation follows Arc42 template (12 sections) with C4 diagrams.

#### 4.3.1 Arc42 Section 1: Introduction and Goals
**Page:** Architecture - Introduction and Goals
**Tags:** `architecture`, `intro`
**Content:**
- Architecture purpose and motivation
- Key stakeholders (product owner, security reviewer, devops)
- Top 3-5 quality goals (performance, scalability, security)

**Update frequency:** During epic creation or quarterly architecture review

**Agents using this page:**
- **Architect** (writes during initial setup, updates quarterly)
- **Product Owner** (reads to understand quality goals)
- **Security Reviewer** (reads to understand security goals)

**Token budget guideline:** ~400 words (~300 tokens)

---

#### 4.3.2 Arc42 Section 2: Constraints
**Page:** Architecture - Constraints
**Tags:** `architecture`, `constraints`
**Content:**
- Technical constraints (languages, frameworks, infrastructure limitations)
- Organizational constraints (team structure, budget, timeline)
- Conventions (coding standards, naming patterns, architectural patterns)

**Update frequency:** When constraints change (rarely)

**Agents using this page:**
- **Architect** (writes during initial setup, updates when constraints change)
- **Product Owner** (reads to understand limitations)
- **Developer** (rarely, only if questioning a constraint)

**Token budget guideline:** ~600 words (~450 tokens)

---

#### 4.3.3 Arc42 Section 3: Context and Scope
**Page:** Architecture - Context and Scope
**Tags:** `architecture`, `context`
**Content:**
- System Context Diagram (C4 Level 1: system + users + external systems)
- External interfaces (APIs consumed, third-party services)
- Business context (business processes this system supports)
- Technical context (protocols, data formats, channels)

**Update frequency:** When external dependencies change

**Agents using this page:**
- **Architect** (writes during initial setup, updates when integrations added)
- **Product Owner** (reads to understand system boundaries)
- **SDET** (reads to understand external systems for e2e testing)
- **Security Reviewer** (reads to understand attack surface)

**Child pages:** Detailed external system integration specifications (>300 words per integration)

**Token budget guideline:** ~800 words (~600 tokens) for main page

---

#### 4.3.4 Arc42 Section 4: Solution Strategy
**Page:** Architecture - Solution Strategy
**Tags:** `architecture`, `strategy`
**Content:**
- High-level approach to meet requirements
- Key architectural patterns (microservices, event-driven, CQRS, DDD)
- Technology decisions with rationale (why React, why PostgreSQL, why Kubernetes)
- Cross-cutting strategies (security approach, scalability approach)

**Update frequency:** When architectural approach changes (rare, high-impact)

**Agents using this page:**
- **Architect** (writes during initial setup, updates for major shifts)
- **Product Owner** (reads to understand technical approach)
- **SDET** (reads to understand testing strategy)
- **Developer** (reads to understand strategic patterns before implementing)
- **Security Reviewer** (reads to understand security strategy)

**Token budget guideline:** ~1000 words (~750 tokens)

---

#### 4.3.5 Arc42 Section 5: Building Block View
**Page:** Architecture - Building Blocks
**Tags:** `architecture`, `building-blocks`
**Content:**
- Container Diagram (C4 Level 2: applications, microservices, data stores)
- Component Diagrams (C4 Level 3: internal structure of containers)
- Component responsibilities and interfaces
- Component interaction patterns

**Update frequency:** When components added/removed/restructured

**Agents using this page:**
- **Architect** (writes during initial setup, updates when components change)
- **Product Owner** (reads to understand system structure)
- **SDET** (reads to understand component boundaries for integration testing)
- **Developer** (reads to understand component interfaces before implementing)

**Child pages:** Detailed component specifications (>300 words per component)

**Token budget guideline:** ~1200 words (~900 tokens) for main page

---

#### 4.3.6 Arc42 Section 6: Runtime View
**Page:** Architecture - Runtime View
**Tags:** `architecture`, `runtime`
**Content:**
- Key scenarios (user login, payment flow, data synchronization, error recovery)
- Sequence diagrams showing component interactions
- Interaction flows with timing considerations
- Concurrency and state management

**Update frequency:** When key flows change or new critical scenarios emerge

**Agents using this page:**
- **Architect** (writes during initial setup, updates when flows change)
- **SDET** (reads extensively for e2e test scenario design)
- **Developer** (reads to understand interaction patterns)
- **Security Reviewer** (reads to understand authentication/authorization flows)

**Child pages:** Detailed scenario specifications with sequence diagrams (>300 words per scenario)

**Token budget guideline:** ~1000 words (~750 tokens) for main page

---

#### 4.3.7 Arc42 Section 7: Deployment View
**Page:** Architecture - Deployment
**Tags:** `architecture`, `deployment`
**Content:**
- Infrastructure overview (cloud provider, regions, availability zones)
- Deployment diagrams (C4 deployment: nodes, containers, relationships)
- Deployment strategies (blue-green, canary, rolling updates)
- Infrastructure as code approach

**Update frequency:** When infrastructure changes

**Agents using this page:**
- **Architect** (writes during initial setup, updates when infrastructure changes)
- **DevOps** (reads extensively, may contribute updates)
- **Security Reviewer** (reads to understand network topology and security zones)

**Child pages:** Detailed infrastructure specifications (Kubernetes manifests, AWS resources) (>300 words)

**Token budget guideline:** ~800 words (~600 tokens) for main page

---

#### 4.3.8 Arc42 Section 8: Cross-cutting Concepts
**Main Page:** Architecture - Cross-cutting (main)
**Tags:** `architecture`, `cross-cutting`
**Content:** Overview linking to 4 child pages

**Child Pages (Required):**
1. **Architecture - Domain Model & Patterns**
   - **Tags:** `architecture`, `cross-cutting`, `domain-model`
   - **Content:** Domain entities, ubiquitous language, transaction management, API conventions
   - **Primary Readers:** Developer, SDET
   - **Token budget:** ~1100 tokens

2. **Architecture - Security**
   - **Tags:** `architecture`, `cross-cutting`, `security`
   - **Content:** Authentication, authorization, data protection, security headers, compliance
   - **Primary Readers:** Security Reviewer, Developer, SDET, DevOps
   - **Contributors:** Security Reviewer
   - **Token budget:** ~1300 tokens

3. **Architecture - Operations**
   - **Tags:** `architecture`, `cross-cutting`, `operations`
   - **Content:** Error handling, logging, caching, configuration management
   - **Primary Readers:** DevOps, Developer, SDET
   - **Contributors:** DevOps
   - **Token budget:** ~1400 tokens

4. **Architecture - Testing**
   - **Tags:** `architecture`, `cross-cutting`, `testing`
   - **Content:** Test levels (unit/integration/E2E), coverage targets, test data management
   - **Primary Readers:** SDET, Developer
   - **Token budget:** ~1200 tokens

**Update frequency:** When cross-cutting patterns introduced or changed

**Token budget guideline:** ~200 words (~150 tokens) for main page (overview)

---

#### 4.3.9 Arc42 Section 9: Architecture Decisions (ADR)
**Page:** Architecture - ADR Summary
**Tags:** `architecture`, `adr`
**Content:**
- Historical list of architectural decisions (summary + link to epic ADR)
- High-impact decisions with brief context (why, what, consequences)
- Each entry: Decision title, date, epic link, 3-sentence summary

**Update frequency:** Per epic (updated by epic-housekeeping agent)

**Agents using this page:**
- **Architect** (reads to avoid conflicting decisions, writes ADR summaries)
- **Developer** (reads to understand why certain patterns exist)
- **Epic Housekeeping** (writes summary when epic completes)

**Token budget guideline:** ~150 words per decision (~112 tokens)

---

#### 4.3.10 Arc42 Section 10: Quality Requirements
**Page:** Architecture - Quality Requirements
**Tags:** `architecture`, `quality`
**Content:**
- Performance requirements (API latency <100ms, throughput >10K req/sec)
- Scalability requirements (concurrent users, data volume growth)
- Availability requirements (uptime SLA 99.9%, RTO, RPO)
- Security requirements (compliance, encryption standards, audit logging)
- Maintainability requirements (code coverage, documentation standards)

**Update frequency:** When quality targets change (annually or per major release)

**Agents using this page:**
- **Architect** (writes during initial setup, updates when targets change)
- **Product Owner** (reads to understand quality commitments)
- **SDET** (reads extensively for performance and load testing targets)
- **Developer** (reads for optimization priorities)
- **Security Reviewer** (reads for security compliance requirements)

**Child pages:** Detailed quality specifications (load testing results, performance benchmarks) (>300 words)

**Token budget guideline:** ~1000 words (~750 tokens) for main page

---

#### 4.3.11 Arc42 Section 11: Risks and Technical Debt
**Page:** Architecture - Risks and Technical Debt
**Tags:** `architecture`, `risks`
**Content:**
- Known risks (performance bottlenecks, scalability limits, security vulnerabilities)
- Technical debt registry (shortcuts taken, areas needing refactoring)
- Mitigation strategies and timelines
- Risk severity and probability assessment

**Update frequency:** Continuous (risks/debt added during epics, resolved items archived)

**Agents using this page:**
- **Architect** (writes risks/debt, updates mitigation strategies)
- **Product Owner** (reads to understand technical constraints)
- **Developer** (reads to understand debt context, writes debt during implementation)
- **Security Reviewer** (writes security risks)

**Token budget guideline:** ~100 words per risk/debt item (~75 tokens)

---

#### 4.3.12 Arc42 Section 12: Glossary
**Page:** Architecture - Glossary
**Tags:** `architecture`, `glossary`
**Content:**
- Architecture-specific terminology (technical terms, acronyms, patterns)
- Component names and abbreviations
- Technology-specific jargon

**Note:** Product glossary lives in Product Reference (Section 1.2.3)

**Update frequency:** As new terms introduced

**Agents using this page:**
- **Architect** (writes new terms)
- **All agents** (read for terminology clarification)

**Token budget guideline:** ~50 words per term (~37 tokens)

---

### 4.4 Epic Documentation (Confluence)

Epic documentation provides detailed context for implementation teams. Created during epic refinement by architect and product owner.

#### 4.4.1 Epic Details (Main Page)
**Page:** ISSUE-ID - Epic Title
**Tags:** `epic`, `{epic-id}`, `epic-details`
**Example:** `SCOPE-42 - OAuth Integration` with tags `epic`, `SCOPE-42`, `epic-details`

**Content:**
- Intent and purpose (the "why")
- Requirements (functional and non-functional)
- Impact, value, capabilities to deliver
- Acceptance criteria
- Integration/e2e test scenarios overview (live services vs mocks)
- Core components and expected tech stack
- Risks and concerns
- Links: Epic ADR | Epic PDR | Epic File Plan | Epic Implementation Summary | Jira Issue

**Agents using this page:**
- **Product Owner** (writes during epic refinement)
- **Architect** (writes during epic refinement, contributes technical sections)
- **SDET** (reads for acceptance criteria and test scenarios)
- **Test Engineer** (reads for test planning)
- **Developer** (rarely, usually reads story description which is self-contained)
- **Security Reviewer** (reads risks and security requirements)

**Token budget guideline:** ~1500 words (~1125 tokens)

---

#### 4.4.2 Epic Architecture Specification
**Page:** Epic Architecture Specification (child of epic details)
**Tags:** `epic`, `{epic-id}`, `architecture`

**Content:**
- Which building blocks (Arc42 Section 5) are affected
- Which runtime scenarios (Arc42 Section 6) are involved
- C4 diagrams specific to this epic (component diagrams, sequence diagrams)
- Component interfaces and contracts
- Integration points

**Agents using this page:**
- **Architect** (writes during epic refinement)
- **SDET** (reads for integration test boundaries)
- **Developer** (reads to understand component structure)
- **Security Reviewer** (reads to understand architectural changes)

**Token budget guideline:** ~800 words (~600 tokens)

---

#### 4.4.3 Epic ADR
**Page:** Epic ADR (child of epic details)
**Tags:** `epic`, `{epic-id}`, `adr`

**Content:**
- Detailed architectural decisions for this epic
- Each decision: Context, Options considered, Decision made, Consequences
- Maps to Arc42 Section 9 (summary link created by epic-housekeeping)

**Child pages:** Decision justifications (>300 words)
- Example: "JWT vs Sessions" decision with 5 options, detailed pros/cons (800 words) → child page

**Agents using this page:**
- **Architect** (writes during epic refinement, updates during implementation if developer escalates)
- **Developer** (reads when implementation approach unclear)
- **Epic Housekeeping** (reads to create ADR summary for Architecture - ADR Summary page)

**Token budget guideline:** ~2000 words (~1500 tokens) for main page, child pages as needed

---

#### 4.4.4 Epic PDR
**Page:** Epic PDR (child of epic details)
**Tags:** `epic`, `{epic-id}`, `pdr`

**Content:**
- Detailed product decisions for this epic
- Each decision: Context, Options considered, Decision made, Impact on users/business
- If multiple options considered, list options not chosen with rationale

**Child pages:** Decision justifications (>300 words)
- Example: "Pricing model selection" with 4 pricing strategies, market analysis (600 words) → child page

**Agents using this page:**
- **Product Owner** (writes during epic refinement)
- **Architect** (reads to understand product decisions)
- **Epic Housekeeping** (reads to create PDR summary for Product Decisions Record page)

**Token budget guideline:** ~1000 words (~750 tokens) for main page, child pages as needed

---

#### 4.4.5 Epic File Plan
**Page:** Epic File Plan (child of epic details)
**Tags:** `epic`, `{epic-id}`, `file-plan`

**Content:**
- Pure YAML format (no markdown)
- File path + intent (600-1200 chars per file)
- Intent format: Purpose, Responsibilities, Key interactions, Why this file, Related modules

**Usage pattern:**
- Implementation planner downloads file plan from Confluence
- Stores locally in `.scope/{epic-id}/file_plan.json`
- Creates per-story file plan for relevant files
- Reduces MCP calls and token count during implementation

**Agents using this page:**
- **Architect** (writes during epic refinement)
- **Implementation Planner** (reads and caches locally)
- **Story agents** (read from local cache, not from Confluence)

**Token budget guideline:** ~1000 words (~750 tokens) total for all files

---

#### 4.4.6 Epic Implementation Summary
**Page:** Epic Implementation Summary (child of epic details)
**Tags:** `epic`, `{epic-id}`, `summary`

**Content:**
- Per-story implementation summary
- Overall implementation notes
- Lessons learned
- Links to story summaries in Jira

**Created by:** Epic Housekeeping agent (after all epic stories complete)

**Agents using this page:**
- **Epic Housekeeping** (writes after epic completion, reads from `.scope/{epic-id}/agents_summaries.jsonl`)
- **Release Documentation** (reads for release notes)
- **Future agents** (read for historical context)

**Token budget guideline:** ~1500 words (~1125 tokens)

---

### 4.5 Release Documentation (Confluence)

Release documentation tracks factual releases only (not roadmap, not forward-looking).

**Page:** Releases (parent page, manually managed)
**Tags:** `releases`

**Per-release section structure:**

#### Release X.Y.Z (e.g., Release 2.4.1)
**Tags:** `release`, `{release-id}`
**Example:** Tags `release`, `aqua-release-2.4.1` (aligns with Jira version/release tag)

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

**Update trigger:** Release planned by user (via release planner agent or manual Jira)

**Agents using this page:**
- **Release Planner** (creates release record, plans release)
- **Release Documentation** (writes release notes after deployment)
- **User** (writes post-mortem after release)

**Token budget guideline:** ~500 words per release section (~375 tokens)

---

### 4.6 Tracking Structure (Jira)

Jira treats epics, stories, and tasks similarly (custom fields per type).

#### 4.6.1 Epic (Jira)
**Workflow:** Draft | Blocked | Implementation Ready | In Progress | Done

**Description:**
- Link to Confluence epic details page
- 200-word summary of epic purpose (same as epic details summary)
- Tech stack (e.g., Node.js, React, PostgreSQL)
- Summary of customer problem being addressed
- Summary of capabilities to add / requirements to address
- Summary of acceptance criteria
- Key metrics (business value, complexity estimate)

**Custom fields:**
- Dependencies (other epics, e.g., [SCOPE-40, SCOPE-41])

**Standard fields:**
- Fix Version (target release, e.g., 2.5.0)

**Agents using this:**
- **Product Owner** (creates epic during refinement, updates status)
- **Architect** (updates during refinement)
- **Orchestrator** (reads epic status, updates during implementation)
- **Epic Housekeeping** (sets status to Done after all stories complete)

---

#### 4.6.2 Story (Jira)
**Workflow:** To Do | In Progress | Blocked | Done

**Description:**
- Story description ("As a user, I want...")
- Technology stack (e.g., Node.js, TypeScript)
- Technical scope (which components affected)
- Detailed acceptance criteria
- Link to file plan (specific files for this story, stored locally in `.scope/{story-id}/file_plan.json`)
- Technical notes
- Reference to ADR (when applicable, link to epic ADR specific section)

**Design principle:** Story description is self-contained (developer doesn't need to fetch epic docs during implementation). Includes links for agents that need deeper context (SDET, Architect).

**Custom fields:**
- (none - stories are tactical units for agentic teams, no categorization needed)

**Standard fields:**
- Epic Link (connects story to parent epic)

**Agents using this:**
- **Architect** (creates story during story breakdown)
- **SDET** (reads for test planning, may contribute acceptance criteria)
- **Developer** (reads extensively, primary context source during implementation)
- **Orchestrator** (reads story status, updates during implementation)

---

#### 4.6.3 Agent Work Summary
Agent work summaries are stored in `.scope/{epic-id}/agents_summaries.jsonl` (NOT in Jira or Confluence during implementation).

After epic completion, Epic Housekeeping agent creates Epic Implementation Summary in Confluence based on these agent summaries.

**Format:** See [Section 8: Agent Summaries](scope-architecture.md#8-agent-summaries) for schema.

---

### 4.7 Child Page Guidelines

**Create child page when content exceeds 300 words (~225 tokens) for a single topic within ADR or PDR.**

**Rationale:**
- Main ADR/PDR page remains scannable
- Child pages provide deep context for critical decisions
- Agents fetch child pages only when needed (progressive disclosure)
- Historical significance preserved without bloating main page

**Example scenarios for child pages:**

1. **ADR Decision Justification:**
   - Main ADR: "Decision: Use JWT for authentication (see child page for full analysis)"
   - Child page: "JWT vs Sessions Analysis" (5 options, detailed pros/cons, 800 words)

2. **PDR Market Analysis:**
   - Main PDR: "Decision: Usage-based pricing (see child page for analysis)"
   - Child page: "Pricing Model Analysis" (4 strategies, market research, 600 words)

3. **Architecture Component Specification:**
   - Main Building Blocks: "Auth Service handles authentication (see child page for details)"
   - Child page: "Auth Service Specification" (interfaces, endpoints, state machine, 1000 words)

**Agent responsibility:** Relevant agent (architect, product owner, security reviewer, devops) creates child page during epic refinement when they recognize content will exceed 300 words.

**Parent page format:**
```markdown
## Decision 3: Authentication Approach

**Context:** Need stateless authentication for multi-region deployment.

**Decision:** Use JWT tokens with RS256 signing.

**Rationale:** See [JWT vs Sessions Analysis](link-to-child-page) for detailed comparison of 5 options.

**Consequences:**
- Stateless authentication enables horizontal scaling
- Token refresh mechanism needed
- Key rotation strategy required
```

---

### 4.8 Token Budget Guidelines

Token budgets are **guidelines, not hard limits**. As product scales to 100+ epics, some pages will grow significantly. Documentation quality trumps size.

**Warning system:** When page exceeds guideline, agent should:
1. Consider if content can be split into child pages (>300 words per topic)
2. Consider if content is redundant with other pages (link instead of duplicate)
3. If content is essential and cannot be split, allow page to grow

**Guideline enforcement:**
- Backend skill (confluence-atlassian-mcp, confluence-sooperset-mcp) checks page size before update
- If page exceeds guideline by >50%, warn agent in tool result
- Agent decides whether to proceed or refactor

**Example warning:**
```
Page "Architecture - Cross-cutting Concepts" is 2400 words (guideline: 1500 words).
Consider creating child pages for:
- Security patterns (400 words) → child page
- Event schema details (500 words) → child page
```

---

### 4.9 Agent-Page Mapping (Critical)

This table defines which agents need which pages. Each agent's instructions reference this mapping.

| Agent | Product Docs | Architecture Docs (Arc42) | Epic Docs | Release Docs | Tracking (Jira) |
|-------|--------------|---------------------------|-----------|--------------|-----------------|
| **Product Owner** | Strategy (R/W)<br>Definition (R/W)<br>Reference (R/W)<br>PDR (R/W) | Intro & Goals (R)<br>Quality Requirements (R) | Epic Details (W)<br>Epic PDR (W) | Release Record (R) | Epic (W)<br>Story (R) |
| **Architect** | Strategy (R)<br>Definition (R) | All 12 sections (R/W)<br>Primary owner | Epic Details (W)<br>Epic Architecture (W)<br>Epic ADR (W)<br>Epic File Plan (W) | - | Epic (R/W)<br>Story (W) |
| **SDET** | Definition (R) | Runtime View (R)<br>Quality Requirements (R)<br>Cross-cutting (R) | Epic Details (R)<br>Epic Architecture (R) | - | Story (R/W) |
| **Test Engineer** | Definition (R) | Runtime View (R)<br>Quality Requirements (R) | Epic Details (R) | - | Story (R) |
| **Developer** | - | Building Blocks (R, rarely)<br>Cross-cutting (R, frequently) | Epic ADR (R, if confused)<br>File Plan (R, via local cache) | - | Story (R, primary source) |
| **Security Reviewer** | - | Context & Scope (R)<br>Solution Strategy (R)<br>Cross-cutting (R)<br>Quality Requirements (R) | Epic Details (R)<br>Epic ADR (R/W, contributes security) | - | - |
| **DevOps** | - | Context & Scope (R)<br>Deployment (R/W)<br>Cross-cutting (R) | Epic Architecture (R, if infra changes) | - | - |
| **Epic Housekeeping** | PDR (W, summaries) | ADR Summary (W, summaries) | Epic Implementation Summary (W) | - | Epic (W, status to Done) |
| **Release Documentation** | - | - | Epic Implementation Summary (R) | Release Notes (W) | - |
| **Release Planner** | - | - | - | Release Record (W) | Epic (R)<br>Story (R) |

**Legend:**
- **R** = Read
- **W** = Write
- **R/W** = Read and Write

---

### 4.10 Update Responsibilities

Clear ownership prevents conflicting updates.

| Page | Primary Owner | Update Trigger | Secondary Contributors |
|------|---------------|----------------|------------------------|
| Product Strategy | Product Owner | Quarterly review, customer insights | - |
| Product Definition | Product Owner | Capability changes | Architect (review) |
| Product Reference | Product Owner | Data model changes | Architect (review) |
| Product PDR | Product Owner | Per epic | Epic Housekeeping (summaries) |
| Architecture Intro & Goals | Architect | Initial setup, quarterly review | - |
| Architecture Constraints | Architect | Constraint changes (rare) | - |
| Architecture Context & Scope | Architect | External integration changes | DevOps (infra context) |
| Architecture Solution Strategy | Architect | Strategic shift (rare) | - |
| Architecture Building Blocks | Architect | Component changes | - |
| Architecture Runtime View | Architect | Flow changes | SDET (test scenarios) |
| Architecture Deployment | Architect | Infrastructure changes | DevOps (contribute) |
| Architecture Cross-cutting | Architect | Pattern changes | Security Reviewer (security patterns) |
| Architecture ADR Summary | Architect | Per epic | Epic Housekeeping (summaries) |
| Architecture Quality Requirements | Architect | Annual review, quality target changes | Product Owner (business SLAs) |
| Architecture Risks & Technical Debt | Architect | Continuous | Developer (debt), Security Reviewer (risks) |
| Architecture Glossary | Architect | As new terms introduced | All agents (contribute) |
| Epic Details | Product Owner, Architect | Epic refinement | SDET (acceptance criteria), Security Reviewer (risks) |
| Epic Architecture | Architect | Epic refinement | - |
| Epic ADR | Architect | Epic refinement, implementation escalations | Security Reviewer (security decisions) |
| Epic PDR | Product Owner | Epic refinement | - |
| Epic File Plan | Architect | Epic refinement | - |
| Epic Implementation Summary | Epic Housekeeping | After epic completion | - |
| Release Record | Release Planner | Release planning | - |
| Release Notes | Release Documentation | After release deployment | - |
| Release Post-mortem | User | After release | - |
| Epic (Jira) | Product Owner | Epic refinement | Architect (collaborate), Epic Housekeeping (status to Done) |
| Story (Jira) | Architect | Story breakdown | SDET (acceptance criteria), Developer (technical notes) |

---

### 4.11 Versioning Strategy

**Living documentation principle:** All documentation has one version, always up-to-date.

**Component versioning approach:**
- Components (microservices, APIs, tools, libraries) have versions
- When component X upgrades (v1.0 → v2.0), create epic "Upgrade Component X to v2.0"
- Epic ADR documents upgrade decisions
- Architecture pages (Building Blocks, Deployment, etc.) updated to reflect v2.0
- Historical context preserved in epic ADR and Architecture ADR Summary

**Industry standard:** This is standard practice in continuous delivery environments (Netflix, Spotify, Amazon).

**Risk mitigation (stale epic):**

**Scenario:** Epic A prepared (ADR references Auth Service v1.0), Epic B upgrades to v2.0, Epic A starts implementation.

**Mitigations:**
1. **Epic Housekeeping validation** - Before marking "Implementation Ready", validate ADR links/references are current
2. **Agent adaptation** - Developer detects mismatch, escalates to architect, epic ADR updated
3. **Dependency tracking** - Story has "Dependencies" field, orchestrator checks before starting

**User responsibility:** If epic prepared but later epic changes dependency, user assesses whether:
- Epic needs updating before implementation
- Agentic team can adapt during implementation (typical case)

---

### 4.12 Search Strategy

Clear guidance on when to use tags, CQL, or Rovo search.

| Query Type | Method | Example |
|------------|--------|---------|
| **Single page retrieval** | Tags | `label = "epic" AND label = "SCOPE-42" AND label = "adr"` → Epic ADR for SCOPE-42 |
| **All pages of type** | Tags | `label = "epic" AND label = "adr"` → All epic ADRs |
| **Filter by properties** | CQL | `label = "epic" AND created >= "2025-01-01"` → Epics created this year |
| **Semantic search** | Rovo | "Why did we choose JWT over sessions?" → Returns relevant ADR content |
| **Date range queries** | Rovo | "All pages for epic SCOPE-42 edited between Nov 1 and Nov 8 2025" → Filtered results |
| **Natural language** | Rovo | "What are the performance requirements for the API?" → Returns Quality Requirements page |

**Agent instructions:**
- Use **tags** when exact page type and epic ID known (deterministic, single result)
- Use **CQL** when filtering by metadata (created date, updated date, status)
- Use **Rovo** when semantic understanding needed (why questions, natural language queries)

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
- Section 8 (Cross-cutting): Grown to 2000 words with 5 child pages
- Other sections: Modest growth (50-100% increase)

**Rationale:** Starting with all 12 sections ensures proper information architecture from day one. Prevents costly refactoring later ("where should this go?"). Each section has clear purpose, agents know where to find/write content.

---

### 4.14 Template Storage

Templates are stored in the project-documentation skill directory, separated by content type (product vs technical).

**Location pattern:**
```
.claude/skills/project-documentation/
├── SKILL.md                          # Wrapper skill with agent self-awareness logic
├── product-guide-atlassian.md        # Product documentation guide
├── technical-guide-arc42-c4.md       # Technical documentation guide
├── confluence-sooperset-mcp.md       # Backend implementation (example)
├── templates-product-atlassian/
│   ├── overview.md                   # Auto-generated summary page
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

.claude/skills/project-tracking/
├── jira-atlassian-mcp.md             # Backend skill
├── templates/
│   ├── epic.md
│   └── story.md
```

**Rationale:** Templates are intrinsically coupled with backend skills. Confluence templates different from file-based templates. Storing in skill extension keeps them together.

**Backend skill references templates:**
```markdown
## create_epic_page Operation

Uses template: `templates/epic-details.md`

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
- **Framework:** Arc42 (12 sections) + C4 diagrams + Product sections (Atlassian Blueprint pattern)
- **Dual-guide system:** Product guide (product-guide-atlassian.md) and Technical guide (technical-guide-arc42-c4.md) maintained separately
- **Agent self-awareness:** Agents determine guide loading based on their role from system prompt
- **Template separation:** `templates-product-atlassian/` and `templates-technical-arc42-c4/` for clean organization
- **Config structure:** `technical-doc: arc42-c4` and `product-doc: atlassian` replace single `method:` field
- **Implementation:** All 12 sections from start, keep lean, evolve
- **Tags:** Separate tags (not composite) for flexible queries
- **Child pages:** Created when topic exceeds 300 words
- **Token budgets:** Guidelines (not limits), quality > size
- **Versioning:** Component versioning (not page versioning), living docs
- **Story ADR:** Only epic-level ADR (not story-level)
- **Agent-page mapping:** Explicit (see Section 1.9)

**Config example:**
```yaml
documentation:
  skill: confluence-sooperset-mcp
  technical-doc: arc42-c4   # → technical-guide-arc42-c4.md + templates-technical-arc42-c4/
  product-doc: atlassian    # → product-guide-atlassian.md + templates-product-atlassian/
```

**Token efficiency:**
- Product Owner: Loads product guide (2k tokens)
- Architect: Loads both guides as needed
- Developer: No guide loading (uses URLs from epic docs) - **2k tokens saved**
- SDET: No guide loading (uses Rovo search) - **2k tokens saved**

**Scalability:** Designed for 100+ epics, 5+ years continuous development, enterprise-grade systems.

**Agent efficiency:** Clear boundaries, targeted fetching, progressive disclosure via child pages, agent self-awareness for guide loading.
