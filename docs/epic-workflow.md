# Epic Workflow

This guide describes the complete workflow for creating and executing an epic.

---

## Overview

The workflow follows a two-phase approach with **human-in-the-loop collaboration**:
1. **Phase 1: Planning** - Product and strategic planning
2. **Phase 2: Development** - Architecture, implementation, and QA

Context preservation and clear agent responsibilities ensure efficient handoffs between phases.

---

## Prerequisites: Product and System Architecture

**Before starting any epics**, create product and system architecture documentation:

### Phase 0: Product Foundation (PRD Creation)

**Collaboration Model**: PM Agent drafts, user reviews and approves iteratively

**Agent**: PM Agent (drafts) + Product Owner (reviews/approves)

**Process**:
1. User provides Project Brief (vision, requirements, constraints)
2. PM Agent drafts PRD (9 documents)
3. Multiple rounds of scope refinement (user + PM Agent)
4. **Approval Gate**: User approves PRD before proceeding

**Documents to Create** (in order):
1. `product/overview.md` - Product summary and navigation
2. `product/strategy.md` - Vision, markets, problems, competitive landscape
3. `product/definition.md` - Use cases and capability map
4. `product/reference/feature-catalog.md` - Existing features
5. `product/reference/terminology-data-model.md` - Domain terminology
6. `product/reference/apis-integrations.md` - API contracts
7. `product/reference/use-case.md` - Detailed use cases
8. `product/reference/ux-workflows.md` - UI structure and workflows
9. `product/decisions.md` - Product-level PDRs

**Why**: Epics link to product strategy. Strategy must exist first.

**Context Flow**: Product documentation → System Architecture, Epic Details

---

### Phase 0.5: System Architecture ⚠️ **CRITICAL FOUNDATION**

**Collaboration Model**: Architect Agent drafts, technical lead reviews and approves, specialized agents review

**Agent**: Architect Agent (drafts) + Technical Lead (reviews/approves) + Specialized Agents (QA, Security, DevOps review)

**Process**:
1. Architect Agent drafts system architecture (Arc42 12 chapters)
2. Multiple rounds of review (tech stack, patterns, structure, standards)
3. Specialized agent reviews (QA, Security, DevOps agents)
4. **Approval Gate**: Technical Lead approves before proceeding

**When**: After product documentation, before any feature epics

⚠️ **YOU CANNOT DESIGN EPIC ARCHITECTURE WITHOUT SYSTEM ARCHITECTURE**

**Why This Phase Exists**: You cannot design epics without a system architecture foundation.

**What is System Architecture**: The Arc42 12-chapter documentation of the **overall technical system**:
- Technology stack (Node.js, React, PostgreSQL, etc.)
- System structure (containers, layers, components)
- Architectural patterns (layered, event-driven, etc.)
- External interfaces and integrations
- Cross-cutting standards (security, operations, testing, domain)
- System-wide constraints and decisions

**Two Approaches**:

#### Approach A: First Epic as "System Foundation"
- Track as EPIC-001: System Foundation
- Product Owner defines required system capabilities
- Architect designs system architecture (12 chapters)
- Developer implements skeleton/infrastructure
- **Result**: Working system + complete Arc42 documentation

#### Approach B: Pre-Epic System Architecture Work
- Architect creates Arc42 documentation before epics
- For existing systems: Document current architecture
- For new systems: Design initial architecture
- Not tracked as epic (foundational work)

**Documents to Create** (in order):

**Foundation (create first)**:
1. `architecture/01-intro.md` - Requirements, quality goals, stakeholders
2. `architecture/02-constraints.md` - Technical, organizational, conventions
3. `architecture/03-context.md` - C4 Level 1, external interfaces
4. `architecture/04-strategy.md` - Tech stack, patterns, principles

**Structure (create second)**:
5. `architecture/05-building-blocks.md` - C4 Level 2 (containers), Level 3 (components)
6. `architecture/06-runtime.md` - Sequence diagrams
7. `architecture/07-deployment.md` - Infrastructure, environments

**Standards (create third)**:
8. `architecture/08-cross-cutting/domain.md` - Domain model, API conventions
9. `architecture/08-cross-cutting/security.md` - Auth, authorization, data protection
10. `architecture/08-cross-cutting/operations.md` - Logging, monitoring, error handling
11. `architecture/08-cross-cutting/testing.md` - Test types, standards, CI/CD

**Meta (create last)**:
12. `architecture/09-adr-summary.md` - Aggregated decisions (initially empty)
13. `architecture/10-quality.md` - Quality scenarios
14. `architecture/11-risks.md` - System risks
15. `architecture/12-glossary.md` - Technical terms

**Context Required**:
- Product Strategy (quality needs, scale needs)
- Product Definition (capabilities, use cases)
- Product Reference (terminology, features to build)

**Deliverable**: Complete Arc42 system architecture documentation

**Context Provided**: System architecture → All epic documents (epic architecture extends system architecture)

**Handoff Checklist**:
- [ ] All 12 Arc42 chapters created
- [ ] Technology stack defined
- [ ] System constraints documented
- [ ] C4 Level 1, 2, 3 diagrams created
- [ ] Cross-cutting standards defined
- [ ] (If implemented) Project structure and dev environment setup

**Transition to Phase 1**: System architecture foundation ready, can now define feature epics

---

## Phase 1: Planning

**Collaboration Model**: PM Agent drafts, Product Owner reviews and approves

**Goal**: Define WHAT to build and WHY

**Agent**: PM Agent (drafts) + Product Owner (reviews/approves)

**Process**:
1. User identifies feature/epic to implement
2. PM Agent drafts Epic Details and Acceptance Criteria
3. Review and refinement
4. **Approval Gate**: Product Owner approves before proceeding

### Step 1.1: Create Epic Details

**Document**: `epic/details.md`

**Actions**:
1. Create epic page with title: `{EPIC-ID}: [Epic Title]`
2. Fill out Strategic Alignment section:
   - Link to relevant product/strategy.md sections
   - List strategic goals this epic addresses
   - Reference applicable product/decisions.md PDRs
3. Complete Epic Summary:
   - Goal, User Value, Technical Approach
   - Tech Stack (high-level)
   - Scope (In/Out)
4. Define User Stories **in implementation order**:
   - Stories sequence defines development workflow
   - Each story should build on previous ones
5. Document dependencies, success criteria, risks

**Output**: Epic Details page with clear strategic context

**Context Provided**: Epic purpose, user stories, scope → feeds into all other documents

---

### Step 1.2: Create Acceptance Criteria

**Document**: `epic/acceptance-criteria.md`

**Actions**:
1. For each user story from Epic Details, define:
   - Specific, testable acceptance criteria
   - Definition of Done checklist
   - Dependencies between stories
2. Define epic-level acceptance criteria
3. Create validation checklist (functional, non-functional, quality)

**Output**: Clear definition of "done" for each story and the epic

**Context Provided**: What defines completion → feeds Test Strategy and QA phase

---

### Phase 1 Handoff

**Handoff Checklist**:
- [ ] Epic Details complete with strategic alignment
- [ ] User stories defined in implementation order
- [ ] Acceptance Criteria defined for all stories
- [ ] Epic-level success criteria clear

**Next Agent**: Architect (Phase 2 begins)

---

## Phase 2: Development

**Goal**: Design HOW to build it, IMPLEMENT, and VALIDATE

### Sub-phase 2A: Architecture (Discovery)

**Agent**: Architect

#### Step 2A.1: System Context

**Document**: `epic/system-context.md`

**Actions**:
1. Review Epic Details (purpose, user stories, scope)
2. Review Product Reference (existing system, APIs, data model)
3. **Review System Architecture (critical context)**:
   - Architecture Context (Ch 3) - external interfaces
   - Architecture Building Blocks (Ch 5) - existing components
   - Architecture Solution Strategy (Ch 4) - tech stack, patterns
   - Architecture Cross-cutting (Ch 8) - security, operations, testing standards
3. Explore problem space:
   - Review System Architecture (Building Blocks, Context) for existing system
   - What exists today that this builds upon?
   - What does this epic add?
   - Integration points with existing system
4. **Evaluate system architecture impact**:
   - Does this epic fit within current system architecture?
   - Does this epic require updating system architecture?
   - Which Arc42 chapters need updating?
   - If major changes needed, may require system architecture epic first
5. Evaluate technology options **within system architecture**:
   - Use system tech stack where possible (from Architecture Solution Strategy)
   - If new technology needed, document why and propose system architecture update
   - Recommend tech stack per epic component/layer
   - Document rationale for each choice
6. Identify constraints:
   - Inherited from existing system
   - Specific to this epic
   - Non-functional requirements
6. Identify risks and potential blockers
7. Complete discovery outcomes:
   - Is this feasible?
   - Recommendation: Proceed / Do Not Proceed / Proceed with Changes
   - Confidence level

**Output**: System Context page with feasibility assessment

**Decision Point**: If "Do Not Proceed", escalate to Product Owner. If "Proceed with Changes", update Epic Details.

**Context Provided**: Technology choices, constraints, risks → feeds Architecture and ADR

---

#### Step 2A.2: Architecture Design

**Document**: `epic/architecture.md`

**Actions**:
1. Review System Context (tech stack, constraints, risks, system architecture impact)
2. Review Epic Details (user stories to understand what to design)
3. **Review System Architecture (critical - epic architecture extends this)**:
   - Architecture Building Blocks (Ch 5) - where do new components fit?
   - Architecture Cross-cutting Domain (Ch 8) - follow API conventions, domain patterns
   - Architecture Cross-cutting Security (Ch 8) - follow auth/authz standards
4. Review Product Reference: UI & Workflows (for frontend architecture)
5. Create architectural design **that extends system architecture**:
   - Component diagrams (C4 Level 3/4) showing **how epic components fit into system**
   - Data model (new entities, modified entities, schema following system conventions)
   - API design (endpoints following system API conventions from Ch 8)
   - Integration points (with external systems AND existing system components)
   - Sequence diagrams (key flows showing interaction with existing system)
6. **If system architecture update needed**:
   - Update affected Arc42 chapters
   - Document in Epic ADR why system changed
   - Note update in System Context
7. Document considerations:
   - Security (authentication, authorization, data protection)
   - Performance (targets, optimization strategies)
   - Infrastructure (new services, configuration, resources)

**Output**: Detailed architecture design with diagrams

**Context Provided**: Component structure, APIs, data model → feeds ADR, Implementation Boundary Plan, Test Strategy

---

#### Step 2A.3: Architecture Decision Records

**Document**: `epic/adr.md`

**Actions**:
1. Review System Context (alternatives evaluated)
2. Review Architecture (design decisions made)
3. For each significant technical decision:
   - Document context (what problem/challenge)
   - State decision (specific technical choice)
   - List alternatives considered with pros/cons
   - Document consequences (positive, negative, risks)
   - Add implementation notes (code changes, configuration, migration)
4. Number ADRs sequentially: ADR-{epic-id}-001, ADR-{epic-id}-002, etc.
5. Most recent ADRs at top

**Output**: ADR page with all architectural decisions documented

**Context Provided**: Technical rationale → feeds Implementation Boundary Plan, guides Development

---

#### Step 2A.4: Test Strategy

**Document**: `epic/test-strategy.md`

**Actions**:
1. Review Architecture (components, integration points)
2. Review Epic Details (user stories implementation order)
3. Review Acceptance Criteria (what to validate)
4. Review System Context (risks to mitigate)
5. For each user story, define test types required:
   - Unit tests (always required)
   - Integration tests (when integration complete)
   - E2E tests (when vertical slice complete)
   - Rationale for each test type
   - Note deferrals (if integration/E2E deferred to later story)
6. Define test boundaries (unit, integration, E2E scope)
7. Document cross-epic test evolution:
   - Which existing tests extend?
   - Which new tests create?
8. Document test architecture (organization, fixtures, extensibility)
9. Define test data requirements
10. Define CI/CD integration (when tests run)

**Output**: Test Strategy page with clear testing approach per story

**Context Provided**: What to test, when to test → guides Development and QA phases

---

#### Step 2A.5: Implementation Boundary Plan

**Document**: `epic/file-plan.md`

**Actions**:
1. Review Architecture (components map to files)
2. Review ADR (technology decisions inform file patterns)
3. Review System Context (tech stack determines file types)
4. Review Product Reference (existing codebase structure)
5. Map out all files:
   - New files (path, purpose, owner story)
   - Modified files (current state, planned changes, impact)
   - Deleted files (reason, migration)
   - Directory structure
   - Configuration files
   - Database migrations
   - Test files (align with Test Strategy)
   - Documentation files
6. For key files, add detail:
   - Purpose
   - Key components
   - Dependencies
   - Associated tests

**Output**: Implementation Boundary Plan page with complete file inventory

**Context Provided**: What binding obligations and candidate file hints → guides Development phase

---

#### Step 2A.6: Product Decision Records (if needed)

**Document**: `epic/pdr.md`

**Actions**:
1. If product decisions arise during architecture (UX choices, feature scope, etc.):
   - Document as PDR with context, decision, alternatives, consequences
   - Link to related epics
   - Add success metrics
2. Number PDRs: PDR-{epic-id}-001, etc.

**Output**: PDR page (may be minimal if no product decisions needed)

**Context Provided**: Product constraints → influences Architecture and Acceptance Criteria

---

### Sub-phase 2A Handoff

**Handoff Checklist**:
- [ ] System Context complete with feasibility confirmed
- [ ] Architecture designed with diagrams
- [ ] ADRs documented for all significant decisions
- [ ] Test Strategy defined per story
- [ ] Implementation Boundary Plan complete with all files mapped
- [ ] PDRs documented (if applicable)

**Context Package for Developer**:
- Epic Details (what to build)
- Acceptance Criteria (definition of done)
- Architecture (how it's designed)
- ADR (technical decisions with rationale)
- Implementation Boundary Plan (what binding obligations and candidate file hints)
- Test Strategy (what tests to write per story)

**Next Agent**: Developer (Sub-phase 2B begins)

---

### Sub-phase 2B: Development

**Agent**: Developer

**No new documentation page created in this phase** - Developer implements following existing documentation.

#### Step 2B.1: Story Implementation Loop

For each user story (in order from Epic Details):

**Actions**:
1. Read Epic Details for story context
2. Read Acceptance Criteria for this story
3. Read Architecture for relevant components
4. Read ADR for technical decision context
5. Read Implementation Boundary Plan for binding obligations and candidate file hints
6. Read Test Strategy for tests required for this story
7. Implement story:
   - Write code per Implementation Boundary Plan and Architecture
   - Follow ADR decisions
   - Write unit tests (always)
   - Write integration tests (if indicated by Test Strategy)
   - Write E2E tests (if indicated by Test Strategy)
8. Run tests:
   - Unit tests must pass
   - Integration tests must pass (if written)
   - E2E tests must pass (if written)
9. If tests fail:
   - Debug and fix (up to 4 attempts)
   - If still failing after 4 attempts, escalate to user
10. Request code review
11. Address review feedback
12. Mark story complete when:
    - All AC met
    - All tests passing
    - Code review approved

**Escalation Triggers**:
- Tests fail after 4 retries → escalate to user
- Requirements unclear → escalate to Product Owner
- Technical blocker not in ADR → escalate to Architect
- Design needs to change → escalate to Architect

**Story Completion**: Move to next story in sequence

---

### Sub-phase 2B Handoff

**Handoff Checklist**:
- [ ] All stories implemented per Epic Details sequence
- [ ] All Acceptance Criteria met
- [ ] All tests passing per Test Strategy
- [ ] Code reviews completed
- [ ] No critical or high-severity bugs

**Next Agent**: QA Engineer (Sub-phase 2C begins)

---

### Sub-phase 2C: QA

**Agent**: QA Engineer

**No new documentation page created in this phase** - QA validates following Test Strategy and Acceptance Criteria.

#### Step 2C.1: Test Execution

**Actions**:
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
5. Document test results:
   - Pass/fail counts per test type
   - Coverage metrics
   - Failed tests with root cause
   - Skipped tests with reason
6. If validation fails:
   - Log bugs
   - Return to Developer for fixes
7. If validation passes:
   - Sign off on epic completion

**Output**: Test results, bug reports (if any), validation sign-off

---

### Sub-phase 2C Handoff

**Handoff Checklist**:
- [ ] All tests executed per Test Strategy
- [ ] All Acceptance Criteria validated
- [ ] Test results documented
- [ ] No blocking bugs

**Next Agent**: Technical Writer + Architect (Phase 3 begins)

---

## Phase 3: Completion (Post-Implementation)

**Goal**: Document WHAT WAS BUILT and LEARN

**Agent**: Technical Writer + Architect

### Step 3.1: Implementation Summary

**Document**: `epic/implementation-summary.md`

**Actions**:
1. Review all epic documentation to compare plan vs. actual
2. Document stories implemented:
   - List all stories with status
   - Note escalations and resolutions
3. Document divergence from plan:
   - Design changes made during implementation
   - Unexpected technical challenges
4. Document escalations:
   - What required user intervention?
   - How was it resolved?
   - Was it preventable?
5. Aggregate reviewer concerns:
   - Critical concerns from code reviews
   - High priority recommendations
6. Document residual risks:
   - Risks that remain after implementation
   - Why they couldn't be mitigated
7. Document technical debt incurred:
   - NEW debt created during implementation
   - Why it was created
   - Cost to fix
8. Compile test results:
   - Execution summary (pass/fail/skip counts)
   - Test failures analysis
   - Test quality concerns
9. Document deployment considerations:
   - Configuration changes
   - Data migrations
   - Deployment risks
10. Define follow-up actions:
    - Required actions before next epic
    - Recommended improvements for future
    - Architecture documentation to update

**Output**: Implementation Summary page with complete retrospective

**Context Provided**: Lessons learned, debt, risks → feeds future epics and architecture updates

---

### Phase 3 Handoff

**Handoff Checklist**:
- [ ] Implementation Summary complete
- [ ] Follow-up actions documented
- [ ] Epic marked complete in tracking system

**Epic Complete** ✅

---

## Context Preservation

### Context Flow Between Documents

```
LAYER 1: PRODUCT (Business View)
Product Strategy → System Architecture (quality goals, scale needs)
Product Definition → System Architecture (capabilities, use cases)
Product Reference → System Architecture (domain terminology, integrations)

LAYER 2: SYSTEM ARCHITECTURE (Technical System View)
System Architecture → All Epic Documents (tech stack, patterns, standards, existing components)

LAYER 3: EPIC (Feature Implementation)
Product Strategy → Epic Details (Strategic Alignment)
Product Definition → Epic Details (User Stories)
Product Reference → Epic System Context (Integration with Existing System)
System Architecture → Epic System Context (Tech stack, constraints, patterns)

Epic Details → System Context (Epic Purpose)
Epic Details → Acceptance Criteria (User Stories)
Epic Details → Test Strategy (Scope)

System Context → Epic Architecture (Technology Stack, Constraints, System Impact)
System Context → ADR (Alternatives Evaluated)
System Context → Test Strategy (Risks)

Epic Architecture → ADR (Design Decisions)
Epic Architecture → Implementation Boundary Plan (Components Map to Files)
Epic Architecture → Test Strategy (Test Boundaries)

ADR → Implementation Boundary Plan (Technology Decisions)

Epic Details + Epic Architecture + ADR + Implementation Boundary Plan + System Architecture → Development
Acceptance Criteria + Test Strategy → Development + QA

Development + QA → Implementation Summary
Implementation Summary → System Architecture (update ADR Summary, Risks, Glossary)
```

### Context Dependency Matrix

| Document | Requires Context From | Provides Context To |
|----------|----------------------|---------------------|
| **Product/Strategy** | None (foundation) | System Architecture, Epic Details (strategic alignment) |
| **Product/Definition** | None (foundation) | System Architecture, Epic Details (user stories), System Context |
| **Product/Reference** | None (foundation) | System Architecture, All epic documents |
| **System Architecture** | Product docs (all) | **ALL epic documents** (tech stack, patterns, standards, components) |
| **Epic Details** | Product Strategy, Definition, System Architecture | All other epic documents |
| **Acceptance Criteria** | Epic Details, Product Definition | Test Strategy, Development, QA, Implementation Summary |
| **System Context** | Epic Details, Product Definition, Product Reference, **System Architecture** | Epic Architecture, ADR, Test Strategy, Implementation Boundary Plan |
| **Epic Architecture** | System Context, Epic Details, Product Reference, **System Architecture** | ADR, Implementation Boundary Plan, Test Strategy, Development |
| **ADR** | System Context, Epic Architecture, Product Reference, System Architecture | Implementation Boundary Plan, Development, Implementation Summary, System Architecture (ADR Summary) |
| **Test Strategy** | Epic Architecture, Epic Details, Acceptance Criteria, System Context, **System Architecture (testing standards)** | Development, QA, Implementation Summary |
| **Implementation Boundary Plan** | Epic Architecture, ADR, System Context, Product Reference, **System Architecture (conventions)** | Development, Implementation Summary |
| **PDR** | Epic Details, Product Strategy, Product Decisions | Epic Architecture, Acceptance Criteria, Development |
| **Implementation Summary** | All epic documents, Development results | Future epics, **System Architecture updates (Ch 9, 11, 12)** |

### Document Creation Order

**Strict Order** (must follow):
1. Product documentation (Phase 0) - 9 files
2. **System Architecture (Phase 0.5) - Arc42 12 chapters**
3. Epic Details (Phase 1, step 1)
4. Acceptance Criteria (Phase 1, step 2)
5. System Context (Phase 2A, step 1)
6. Epic Architecture (Phase 2A, step 2)
7. ADR (Phase 2A, step 3)
8. Test Strategy (Phase 2A, step 4)
9. Implementation Boundary Plan (Phase 2A, step 5)
10. PDR (Phase 2A, step 6 - if needed)
11. Development (Phase 2B)
12. QA (Phase 2C)
13. Implementation Summary (Phase 3)
14. **Update System Architecture** (Phase 3 - Ch 9, 11, 12)

Each document depends on context from previous documents. Creating out of order results in missing or invalid context.

---

## Agent Roles & Responsibilities

| Agent | Phases | Documents Created | Key Responsibilities |
|-------|--------|-------------------|---------------------|
| **Product Owner** | Phase 0, Phase 1 | Product docs, Epic Details, Acceptance Criteria, PDR | Define product vision and what to build, strategic alignment, product decisions |
| **Architect** | Phase 0.5, Phase 2A | System Architecture (12 chapters), Epic System Context, Epic Architecture, ADR, Test Strategy, Implementation Boundary Plan | Design system and epics, evaluate feasibility, document decisions, maintain system architecture |
| **Developer** | Phase 2B | Code, Tests | Implement stories per system and epic architecture and implementation boundary plan |
| **QA Engineer** | Phase 2C | Test Results, Bug Reports | Validate acceptance criteria, execute test strategy |
| **Technical Writer** | Phase 3 | Implementation Summary | Document what was built, capture lessons learned |

---

## SCOPE Commands

These slash commands orchestrate the workflow:

```bash
# Product Documentation
/prd_create                     # Create a first-pass PRD from an interview
/prd_refine                     # Refine product requirements document
/prd_breakdown                  # Break PRD into implementable epics

# Reverse Engineering (existing codebases)
/re_documentation               # Reverse engineer product + architecture docs

# Epic Workflow
/epic_refine {EPIC-ID}          # Refine epic (planning + architecture + specs + stories)
/implement {EPIC-ID}            # Implement stories in a git worktree
/implement_tdd {EPIC-ID}        # Implement with test-driven development
/audit_epic {EPIC-ID}           # Audit implementation against specs

# Sync
/sync_product                   # Update product docs after implementation changes
```

---

## Workflow Summary

**Phase 0: Product Foundation** (Product Owner)
- Product Owner creates product documentation (strategy, definition, reference, use cases, UX workflows)
- **Output**: Business view of product

**Phase 0.5: System Architecture** ⚠️ **CRITICAL** (Architect)
- Architect creates system architecture (Arc42 12 chapters)
- OR first epic establishes system architecture
- **Output**: Technical view of overall system
- **See**: Phase 0.5 section above

**Phase 1: Planning** (Product Owner)
1. Create Epic Details with strategic alignment to product strategy
2. Create Acceptance Criteria for all stories

**Phase 2A: Epic Architecture** (Architect)
3. Create System Context (feasibility, system architecture impact)
4. Create Epic Architecture (design that extends system architecture)
5. Create ADR (decisions specific to this epic)
6. Create Test Strategy (testing approach per story)
7. Create Implementation Boundary Plan (file inventory)
8. Create PDR (if product decisions arise during epic)
9. **Update System Architecture if needed** (affected Arc42 chapters)

**Phase 2B: Development** (Developer)
10. Implement stories in sequence
11. Write tests per Test Strategy
12. Pass code reviews

**Phase 2C: QA** (QA Engineer)
13. Execute Test Strategy
14. Validate Acceptance Criteria

**Phase 3: Completion** (Technical Writer + Architect)
15. Create Implementation Summary
16. **Update System Architecture**:
    - Update ADR Summary (Ch 9) with epic's ADRs
    - Update Risks (Ch 11) if new risks emerged
    - Update Glossary (Ch 12) if new terms introduced

**Epic Complete** ✅

---

## Best Practices

1. **Create documentation in correct order** - Product → System Architecture → Epics
2. **System architecture is fundamental** - Cannot design epics without system architecture foundation
2. **Follow document order** - Context dependencies prevent starting documents without prerequisites
3. **Use implementation order for stories** - Epic Details story sequence defines development workflow
4. **Document decisions when made** - Don't wait until end to write ADRs/PDRs
5. **Update documents during implementation** - If design changes, update Architecture and ADR immediately
6. **Write tests early** - Per Test Strategy, write tests at earliest point they become possible
7. **Escalate blockers quickly** - Don't retry indefinitely, escalate after 4 attempts
8. **Complete Implementation Summary** - Critical for learning and continuous improvement

---
