# BMAD Phase Quick Reference

Quick lookup for what documents to create in each phase and their context dependencies.

---

## Phase Overview

| Phase | BMAD Name | Agent | Purpose | Documents Created |
|-------|-----------|-------|---------|-------------------|
| **Phase 0** | Product Foundation | Product Owner | Define product vision | Product docs (9 files) |
| **Phase 0.5** | **System Architecture** ⚠️ | Architect | **Define technical system foundation** | **Arc42 12 chapters** |
| **Phase 1** | Agentic Planning | Product Owner | Define WHAT to build | Epic Details, Acceptance Criteria |
| **Phase 2A** | Context-Engineered Development (Epic Architecture) | Architect | Design HOW to build epic | System Context, Epic Architecture, ADR, Test Strategy, File Plan, PDR |
| **Phase 2B** | Context-Engineered Development (Build) | Developer | Implement stories | Code, Tests |
| **Phase 2C** | Context-Engineered Development (QA) | QA Engineer | Validate implementation | Test Results, Validation |
| **Phase 3** | Completion | Technical Writer + Architect | Document lessons learned | Implementation Summary |

---

## Phase 0: Product Foundation

**Agent**: Product Owner

**When**: Before any epics start

**Prerequisites**: None (this is the foundation)

**Documents to Create** (in order):

| # | Document | Purpose | Creates Child Pages? |
|---|----------|---------|---------------------|
| 1 | `product/overview.md` | Product summary, navigation to child pages | Yes (root page) |
| 2 | `product/strategy.md` | Vision, markets, problems, competitive landscape | No (child of overview) |
| 3 | `product/definition.md` | Use cases and capability map | No (child of overview) |
| 4 | `product/reference/feature-catalog.md` | Existing features | No (child of overview → reference) |
| 5 | `product/reference/terminology-data-model.md` | Domain terminology | No (child of overview → reference) |
| 6 | `product/reference/apis-integrations.md` | API contracts | No (child of overview → reference) |
| 7 | `product/reference/use-case.md` | Detailed use cases | No (child of overview → reference) |
| 8 | `product/reference/ux-workflows.md` | UI structure and workflows | No (child of overview → reference) |
| 9 | `product/decisions.md` | Product-level PDRs | No (child of overview) |

**Deliverable**: Complete product documentation foundation

**Context Provided**: Strategic goals, use cases, existing features, terminology → feeds all epics

**Transition to Phase 0.5**: Product documentation complete, ready for system architecture

---

## Phase 0.5: System Architecture ⚠️ **CRITICAL FOUNDATION**

**Agent**: Architect

**When**: After Phase 0, before any feature epics

⚠️ **YOU CANNOT DESIGN EPIC ARCHITECTURE WITHOUT SYSTEM ARCHITECTURE**

**Why This Phase Exists**: BMAD v4's public documentation does not explicitly distinguish between system-level and feature/epic-level architecture. However, **you cannot design epics without a system architecture foundation**.

**Prerequisites**:
- ✅ Product documentation complete (Phase 0)

**Documents to Create** (Arc42 12 Chapters in order):

### Foundation (Create First)

| # | Document | Purpose | Context Required |
|---|----------|---------|------------------|
| 1 | `architecture/01-intro.md` | Requirements, quality goals, stakeholders | Product Strategy, Product Definition |
| 2 | `architecture/02-constraints.md` | Technical, organizational, conventions | Product Strategy (timeline, budget) |
| 3 | `architecture/03-context.md` | C4 Level 1, external interfaces | Product Reference (integrations) |
| 4 | `architecture/04-strategy.md` | Tech stack, patterns, principles | Intro, Constraints, Context |

### Structure (Create Second)

| # | Document | Purpose | Context Required |
|---|----------|---------|------------------|
| 5 | `architecture/05-building-blocks.md` | C4 Level 2 & 3, major components | Solution Strategy |
| 6 | `architecture/06-runtime.md` | Sequence diagrams for key scenarios | Building Blocks |
| 7 | `architecture/07-deployment.md` | Infrastructure, environments | Building Blocks, Solution Strategy |

### Standards (Create Third)

| # | Document | Purpose | Context Required |
|---|----------|---------|------------------|
| 8a | `architecture/08-cross-cutting/domain.md` | Domain model, API conventions, transactions | Product Reference: Terminology |
| 8b | `architecture/08-cross-cutting/security.md` | Auth, authorization, data protection | Solution Strategy |
| 8c | `architecture/08-cross-cutting/operations.md` | Logging, monitoring, error handling | Deployment |
| 8d | `architecture/08-cross-cutting/testing.md` | Test types, standards, CI/CD | Solution Strategy |

### Meta (Create Last)

| # | Document | Purpose | Context Required |
|---|----------|---------|------------------|
| 9 | `architecture/09-adr-summary.md` | Aggregated decisions from all epics | Initially empty, populated during epics |
| 10 | `architecture/10-quality.md` | Quality scenarios | Intro, Solution Strategy |
| 11 | `architecture/11-risks.md` | System risks, technical debt | Solution Strategy, Constraints |
| 12 | `architecture/12-glossary.md` | Technical terminology | Product Reference: Terminology, Domain model |

**Two Approaches**:

**Option A: First Epic as "System Foundation"**
- Track as EPIC-001: System Foundation
- Product Owner defines system capabilities needed
- Architect designs and documents system architecture
- Developer implements skeleton/infrastructure
- Result: Working system + Arc42 documentation

**Option B: Pre-Epic Architecture Work**
- Architect creates Arc42 documentation before epics
- For existing systems: Document current architecture
- For new systems: Design initial architecture
- Not tracked as epic (foundational work)

**Recommendation**: Option A for new products, Option B for existing products

**Phase 0.5 Deliverables**:
- ✅ All 12 Arc42 chapters created
- ✅ Technology stack defined
- ✅ System constraints documented
- ✅ C4 Level 1, 2, 3 diagrams created
- ✅ Cross-cutting standards defined

**Phase 0.5 → Phase 1 Handoff Checklist**:
- [ ] All 12 Arc42 chapters created
- [ ] Technology stack defined (Solution Strategy)
- [ ] System constraints documented
- [ ] C4 Level 1, 2, 3 diagrams created
- [ ] Cross-cutting standards defined (domain, security, operations, testing)
- [ ] (If implemented) Project structure and dev environment setup

**Context Provided**: System architecture → All epic documents

**Transition to Phase 1**: System architecture foundation ready, can now define feature epics

**See**: [SYSTEM-ARCHITECTURE-PHASE.md](SYSTEM-ARCHITECTURE-PHASE.md) for detailed guide

---

## Phase 1: Agentic Planning

**Agent**: Product Owner

**When**: Starting a new epic

**Prerequisites**:
- ✅ Product documentation complete (Phase 0)

**Documents to Create**:

### 1. Epic Details (`epic/details.md`)

**Context Required**:
- Product Strategy (for Strategic Alignment section)
- Product Definition (for user stories context)
- Product Reference (for feature catalog - what exists)

**Key Sections**:
- Meta: Phase & Agent Information
- Strategic Alignment (links to product/strategy.md)
- Context Dependencies
- Epic Summary (Goal, User Value, Technical Approach)
- User Stories **in implementation order**
- Dependencies, Success Criteria, Risks
- Agent Ownership by Phase

**Creates Child Pages**: Yes (this is the epic root page)

---

### 2. Acceptance Criteria (`epic/acceptance-criteria.md`)

**Context Required**:
- Epic Details (user stories)
- Product Definition (use cases)
- Product Reference: Feature Catalog (existing features)

**Key Sections**:
- Meta: Phase & Agent Information
- Context Dependencies
- Story Acceptance Criteria (for each story)
- Epic-Level Acceptance Criteria
- Validation Checklist

**Creates Child Pages**: No (child of Epic Details)

---

**Phase 1 Deliverables**:
- ✅ Epic Details with strategic alignment and story sequence
- ✅ Acceptance Criteria for all stories

**Phase 1 → Phase 2A Handoff Checklist**:
- [ ] Epic Details complete with strategic alignment
- [ ] User stories defined in implementation order
- [ ] Acceptance Criteria defined for all stories
- [ ] Epic-level success criteria clear

**Transition to Phase 2A**: Product Owner hands off to Architect

---

## Phase 2A: Architecture

**Agent**: Architect

**When**: After Phase 1 handoff approved

**Prerequisites**:
- ✅ Epic Details complete
- ✅ Acceptance Criteria complete
- ✅ Product Reference documentation exists
- ✅ **System Architecture complete (Arc42 12 chapters)** ⚠️

**Documents to Create** (in order):

### 1. System Context (`epic/system-context.md`)

**Context Required**:
- Epic Details (epic purpose, user stories, scope)
- Product Definition (use cases and capability map)
- Product Reference (existing features, terminology, APIs)
- Product Strategy (strategic goals and constraints)

**Key Sections**:
- Meta: Phase & Agent Information
- Context Dependencies
- Epic Purpose
- Integration with Existing System
- Technology Stack recommendations
- Constraints
- Risks Identified
- Unresolved Blockers
- Discovery Outcomes (Feasibility assessment)

**Decision Point**: If "Do Not Proceed", escalate. If "Proceed with Changes", update Epic Details.

---

### 2. Architecture (`epic/architecture.md`)

**Context Required**:
- System Context (tech stack, constraints, risks, feasibility)
- Epic Details (user stories, scope, success criteria)
- Product Reference (existing system architecture, APIs, data models)
- Product Reference: UI & Workflows (for frontend architecture)

**Key Sections**:
- Meta: Phase & Agent Information
- Context Dependencies
- Architectural Overview
- Component Diagrams (C4 Level 3/4, Mermaid)
- Data Model
- API Design
- Integration Points
- Sequence Diagrams
- Security Considerations
- Performance Considerations
- Infrastructure Changes

---

### 3. ADR (`epic/adr.md`)

**Context Required**:
- System Context (alternatives evaluated)
- Architecture (design decisions made)
- Product Reference (existing architecture patterns and standards)

**Key Sections**:
- Meta: Phase & Agent Information
- Context Dependencies
- ADR-{epic-id}-001 through ADR-{epic-id}-NNN
  - Date, Status, Deciders
  - Context, Decision, Alternatives, Consequences
  - Implementation Notes

**Format**: Most recent ADRs at top

---

### 4. Test Strategy (`epic/test-strategy.md`)

**Context Required**:
- Architecture (components, integration points, data model)
- Epic Details (user stories implementation order, scope)
- Acceptance Criteria (what defines story completion)
- System Context (risks to mitigate through testing)

**Key Sections**:
- Meta: Phase & Agent Information
- Context Dependencies
- Test Scope by Story (unit, integration, E2E per story)
- Test Boundaries (unit/integration/E2E definitions)
- Cross-Epic Test Evolution
- Test Architecture
- Test Data Requirements
- CI/CD Integration

---

### 5. File Plan (`epic/file-plan.md`)

**Context Required**:
- Architecture (components map to files)
- ADR (technology decisions determine file patterns)
- System Context (technology stack determines file types)
- Product Reference (existing codebase structure and conventions)

**Key Sections**:
- Meta: Phase & Agent Information
- Context Dependencies
- New Files (path, purpose, owner story)
- Modified Files (current state, planned changes, impact)
- Deleted Files (reason, migration)
- Directory Structure
- Configuration Files
- Database Migrations
- Test Files
- Documentation Files

---

### 6. PDR (`epic/pdr.md`) - Optional

**Context Required**:
- Epic Details (epic context for decisions)
- Product Strategy (strategic goals informing decisions)
- Product Decisions (product-level PDRs that may influence epic-specific ones)

**Key Sections**:
- Meta: Phase & Agent Information
- Context Dependencies
- PDR-{epic-id}-001 through PDR-{epic-id}-NNN
  - Date, Status, Related Epics
  - Context, Decision, Alternatives, Consequences
  - Success Criteria

**When to Create**: If product decisions arise during architecture (UX choices, feature scope, etc.)

---

**Phase 2A Deliverables**:
- ✅ System Context with feasibility confirmed
- ✅ Architecture designed with diagrams
- ✅ ADRs documented for all significant decisions
- ✅ Test Strategy defined per story
- ✅ File Plan complete with all files mapped
- ✅ PDRs documented (if applicable)

**Phase 2A → Phase 2B Handoff Checklist**:
- [ ] System Context complete with feasibility confirmed
- [ ] Architecture designed with diagrams
- [ ] ADRs documented for all significant decisions
- [ ] Test Strategy defined per story
- [ ] File Plan complete with all files mapped

**Context Package for Developer**:
- Epic Details (what to build)
- Acceptance Criteria (definition of done)
- Architecture (how it's designed)
- ADR (technical decisions with rationale)
- File Plan (what files to create/modify)
- Test Strategy (what tests to write per story)

**Transition to Phase 2B**: Architect hands off to Developer

---

## Phase 2B: Development

**Agent**: Developer

**When**: After Phase 2A handoff approved

**Prerequisites**:
- ✅ All Phase 2A documents complete
- ✅ Context package reviewed

**Documents to Create**: None (implements based on existing documentation)

**What Developer Does**:

**For each story (in order from Epic Details)**:
1. Read Epic Details for story context
2. Read Acceptance Criteria for this story
3. Read Architecture for relevant components
4. Read ADR for technical decision context
5. Read File Plan for files to create/modify
6. Read Test Strategy for tests required for this story
7. Implement story:
   - Write code per File Plan and Architecture
   - Follow ADR decisions
   - Write unit tests (always)
   - Write integration tests (if indicated by Test Strategy)
   - Write E2E tests (if indicated by Test Strategy)
8. Run tests (escalate after 4 failures)
9. Request code review
10. Address review feedback
11. Mark story complete

**Escalation Triggers**:
- Tests fail after 4 retries → escalate to user
- Requirements unclear → escalate to Product Owner
- Technical blocker not in ADR → escalate to Architect
- Design needs to change → escalate to Architect

**Phase 2B Deliverables**:
- ✅ All stories implemented
- ✅ All tests passing
- ✅ Code reviews approved

**Phase 2B → Phase 2C Handoff Checklist**:
- [ ] All stories implemented per Epic Details sequence
- [ ] All Acceptance Criteria met
- [ ] All tests passing per Test Strategy
- [ ] Code reviews completed
- [ ] No critical or high-severity bugs

**Transition to Phase 2C**: Developer hands off to QA Engineer

---

## Phase 2C: QA

**Agent**: QA Engineer

**When**: After Phase 2B handoff approved

**Prerequisites**:
- ✅ All stories implemented
- ✅ All tests passing
- ✅ Code reviews complete

**Documents to Create**: None (validates based on existing documentation)

**What QA Does**:

1. Review Test Strategy for test execution plan
2. Review Acceptance Criteria for validation checklist
3. Execute tests per Test Strategy:
   - Run full unit test suite
   - Run full integration test suite
   - Run full E2E test suite
4. Validate Acceptance Criteria:
   - Functional validation per story
   - Epic-level validation
   - Non-functional validation (performance, security, accessibility)
5. Document test results
6. If validation fails → log bugs, return to Developer
7. If validation passes → sign off

**Phase 2C Deliverables**:
- ✅ All tests executed
- ✅ All Acceptance Criteria validated
- ✅ Test results documented
- ✅ No blocking bugs

**Phase 2C → Phase 3 Handoff Checklist**:
- [ ] All tests executed per Test Strategy
- [ ] All Acceptance Criteria validated
- [ ] Test results documented
- [ ] No blocking bugs

**Transition to Phase 3**: QA Engineer hands off to Technical Writer + Architect

---

## Phase 3: Completion

**Agent**: Technical Writer + Architect

**When**: After Phase 2C sign-off

**Prerequisites**:
- ✅ All stories implemented
- ✅ All tests passing
- ✅ QA validation complete

**Documents to Create**:

### 1. Implementation Summary (`epic/implementation-summary.md`)

**Context Required**:
- Epic Details (original plan to compare against)
- Architecture (design to compare against actual implementation)
- File Plan (planned files vs. actual files created)
- Test Strategy (planned tests vs. actual test results)
- Development Phase (completed code, tests, reviews)

**Key Sections**:
- Meta: Phase & Agent Information
- Context Dependencies
- Implementation Overview (status, completion date, stories completed)
- Stories Implemented (with escalations)
- Divergence from Plan (design changes, unexpected challenges)
- Escalations (what required intervention, was it preventable)
- Reviewer Concerns and Recommendations
- Residual Risks
- Technical Debt Incurred
- Test Results (execution summary, failures, quality concerns)
- Code Quality Signals
- Deployment Considerations
- Follow-up Actions (required, recommended, architecture updates)

---

**Phase 3 Deliverables**:
- ✅ Implementation Summary complete
- ✅ Follow-up actions documented
- ✅ Epic marked complete in tracking system

**Epic Complete** ✅

---

## Context Dependency Matrix

| Document | Requires Context From | Provides Context To |
|----------|----------------------|---------------------|
| **Product/Strategy** | None (foundation) | System Architecture, Epic Details (strategic alignment) |
| **Product/Definition** | None (foundation) | System Architecture, Epic Details (user stories), System Context |
| **Product/Reference** | None (foundation) | System Architecture, All epic documents |
| **System Architecture** | Product docs (all) | **ALL epic documents** (tech stack, patterns, standards, components) |
| **Epic Details** | Product Strategy, Definition, System Architecture | All other epic documents |
| **Acceptance Criteria** | Epic Details, Product Definition | Test Strategy, Development, QA, Implementation Summary |
| **System Context** | Epic Details, Product Definition, Product Reference, **System Architecture** | Epic Architecture, ADR, Test Strategy, File Plan |
| **Epic Architecture** | System Context, Epic Details, Product Reference, **System Architecture** | ADR, File Plan, Test Strategy, Development |
| **ADR** | System Context, Epic Architecture, Product Reference, System Architecture | File Plan, Development, Implementation Summary, System Architecture (ADR Summary) |
| **Test Strategy** | Epic Architecture, Epic Details, Acceptance Criteria, System Context, **System Architecture (testing standards)** | Development, QA, Implementation Summary |
| **File Plan** | Epic Architecture, ADR, System Context, Product Reference, **System Architecture (conventions)** | Development, Implementation Summary |
| **PDR** | Epic Details, Product Strategy, Product Decisions | Epic Architecture, Acceptance Criteria, Development |
| **Implementation Summary** | All epic documents, Development results | Future epics, **System Architecture updates (Ch 9, 11, 12)** |

---

## Document Creation Order

**Strict Order** (must follow):
1. Product documentation (Phase 0) - 9 files
2. **System Architecture (Phase 0.5) - Arc42 12 chapters** ⚠️ **CRITICAL**
3. Epic Details (Phase 1, step 1)
4. Acceptance Criteria (Phase 1, step 2)
5. System Context (Phase 2A, step 1)
6. Epic Architecture (Phase 2A, step 2)
7. ADR (Phase 2A, step 3)
8. Test Strategy (Phase 2A, step 4)
9. File Plan (Phase 2A, step 5)
10. PDR (Phase 2A, step 6 - if needed)
11. Development (Phase 2B)
12. QA (Phase 2C)
13. Implementation Summary (Phase 3)
14. **Update System Architecture** (Phase 3 - Ch 9, 11, 12)

**Why Strict Order**: Each document depends on context from previous documents. Creating out of order results in missing/invalid context.

**Critical**: System Architecture (step 2) must exist before any epic work begins. You cannot design epic architecture without system architecture foundation.

---

## Phase Transition Checklist Template

Use this checklist when transitioning between phases:

### Phase 0 → Phase 0.5
- [ ] Product/Strategy complete with vision and markets
- [ ] Product/Definition complete with use cases
- [ ] Product/Reference complete (all 5 child pages)
- [ ] Product/Decisions created (may be empty initially)

### Phase 0.5 → Phase 1 ⚠️ **CRITICAL CHECKPOINT**
- [ ] All 12 Arc42 chapters created
- [ ] Technology stack defined (Ch 4: Solution Strategy)
- [ ] System constraints documented (Ch 2: Constraints)
- [ ] C4 Level 1, 2, 3 diagrams created (Ch 3, 5)
- [ ] Cross-cutting standards defined (Ch 8: domain, security, operations, testing)
- [ ] (If implemented) Project structure and dev environment setup

### Phase 1 → Phase 2A
- [ ] Epic Details complete with strategic alignment
- [ ] Epic Details has user stories in implementation order
- [ ] Acceptance Criteria defined for all stories
- [ ] Epic-level success criteria clear

### Phase 2A → Phase 2B
- [ ] System Context complete with feasibility confirmed
- [ ] System Context assessed system architecture impact
- [ ] System Architecture updated (if needed)
- [ ] Epic Architecture designed with diagrams (extends system architecture)
- [ ] ADRs documented for all significant decisions
- [ ] Test Strategy defined per story
- [ ] File Plan complete with all files mapped

### Phase 2B → Phase 2C
- [ ] All stories implemented per Epic Details sequence
- [ ] All Acceptance Criteria met
- [ ] All tests passing per Test Strategy
- [ ] Code reviews completed
- [ ] No critical or high-severity bugs

### Phase 2C → Phase 3
- [ ] All tests executed per Test Strategy
- [ ] All Acceptance Criteria validated
- [ ] Test results documented
- [ ] No blocking bugs

### Phase 3 Complete
- [ ] Implementation Summary complete
- [ ] Follow-up actions documented
- [ ] **System Architecture updated**:
  - [ ] ADR Summary (Ch 9) updated with epic's ADRs
  - [ ] Risks (Ch 11) updated if new risks emerged
  - [ ] Glossary (Ch 12) updated if new terms introduced
- [ ] Epic marked complete in tracking system

---
