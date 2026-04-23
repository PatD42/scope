---
epic_id: {epic-id}
title: [Epic Title]
status: draft
---

# {epic-id}: [Epic Title]

---

## Meta: Phase & Agent Information

**Phase**: Phase 1 - Planning
**Agent Role**: Product Owner
**Created During**: Epic Planning
**Prerequisites**: Product Strategy, Product Definition completed

---

## Strategic Alignment

**Related Product Strategy**: [Link to product/strategy.md section - e.g., "Target Market: Enterprise Users"]

**Strategic Goals Addressed**:
- [Goal 1 from product strategy - e.g., "Improve enterprise user onboarding"]
- [Goal 2 from product strategy - e.g., "Reduce time-to-value for new customers"]

**Product Decisions Applied**: [Link to relevant PDRs from product/decisions.md]

---

## Context Dependencies

**Required Context (must exist before this document)**:
- Product Strategy: Vision, target markets, customer problems
- Product Definition: Use cases and capability map
- Product Reference: Feature catalog, terminology

**Provides Context For (documents that depend on this)**:
- [{epic-id}: System Context](link) - Problem statement, expected outcome
- [{epic-id}: Acceptance Criteria](link) - Success criteria, user stories
- [{epic-id}: Test Strategy](link) - Scope boundaries, quality requirements

---

## Epic Documentation

**Child Pages**:
- [{epic-id}: System Context](link) - Integration points, inherited constraints, patterns to follow
- [{epic-id}: Acceptance Criteria](link) - Story-level acceptance criteria and validation checklist
- [{epic-id}: Test Strategy](link) - Test types, boundaries, and cross-epic test evolution
- [{epic-id}: Architecture](link) - Component diagrams, data models, and integration points
- [{epic-id}: ADR](link) - Architecture Decision Records for this epic
- [{epic-id}: PDR](link) - Product Decision Records for this epic
- [{epic-id}: File Plan](link) - Intent documentation for all files
- [{epic-id}: Implementation Summary](link) - Created after epic completion

---

## Epic Summary

<!-- 400-word summary of what this epic achieves. -->

**Goal**:

**User Value**:

**Technical Approach**:

## Tech Stack

<!-- Specific technologies used in this epic. -->

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Backend | | | |
| Frontend | | | |
| Database | | | |
| Infrastructure | | | |

## Scope

<!-- What is included and excluded from this epic. -->

### In Scope

-
-

### Out of Scope

-
-

## User Stories

<!-- High-level user stories addressed by this epic. Order defines implementation sequence. -->

1. **As a** [user type], **I want** [capability], **so that** [benefit]
2.
3.

**Implementation Order**: Stories are listed in recommended implementation sequence. Each story maps to one or more tasks in the development phase.

## Dependencies

<!-- What must be completed before this epic can begin? -->

### Epic Dependencies

| Epic ID | Title | Relationship | Status |
|---------|-------|-------------|--------|
| | | Blocks/Depends on | |

### External Dependencies

-

## Success Criteria

<!-- High-level epic success criteria. Detailed story-level acceptance criteria are in the child page. -->

**See**: [{epic-id}: Acceptance Criteria](link-to-child-page) for detailed story-level AC

### Epic-Level Criteria

- [ ] All stories complete with AC verified
- [ ] Cross-story integration validated
- [ ] Performance targets met (see Test Strategy)
- [ ] Security requirements validated
- [ ] Documentation complete

## Key Metrics

<!-- What metrics will we track? -->

| Metric | Target | How Measured |
|--------|--------|--------------|
| | | |

## Risks

<!-- What could go wrong? -->

| Risk | Impact | Mitigation |
|------|--------|------------|
| | | |

## Timeline

<!-- Target release and key milestones. -->

**Target Release**: {version} (e.g., 2.5.0)

**Key Milestones**:
- [ ] Architecture complete
- [ ] Stories created
- [ ] Implementation complete
- [ ] Testing complete

---

## Agent Ownership by Phase

| Phase | Agent Role | Responsibilities | Deliverables |
|-------|-----------|------------------|--------------|
| **Planning** | Product Owner | Define epic scope, user stories, strategic alignment | This document, Acceptance Criteria |
| **Architecture** | Architect | Evaluate feasibility, design system, document decisions | System Context, Architecture, ADR, Test Strategy, File Plan |
| **Development** | Developer | Implement stories in sequence, follow file plan | Code, unit tests |
| **QA** | QA Engineer | Execute test strategy, validate acceptance criteria | Test results, bug reports |
| **Completion** | Technical Writer + Architect | Document what was built and decisions made | Implementation Summary, updated ADRs |

---
