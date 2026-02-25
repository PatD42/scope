# Epic System Context: [Epic Title]

---

## Meta: Phase & Agent Information

**Phase**: Phase 2 - Architecture
**Agent Role**: Architect
**Created During**: Architecture Phase - System Context Stage
**Prerequisites**: Epic Details, Product Definition, Product Reference

---

## Context Dependencies

**Required Context (must exist before this document)**:
- [{epic-id}: Epic Details](link) - Epic purpose, user stories, scope
- Product Definition: Use cases and capability map
- Product Reference: Existing features, terminology, APIs
- Product Strategy: Strategic goals and constraints

**Provides Context For (documents that depend on this)**:
- [{epic-id}: Architecture](link) - Component design, integration points
- [{epic-id}: ADR](link) - Technology selections with rationale
- [{epic-id}: Test Strategy](link) - Risk mitigation through testing

---

## Overview

<!-- This document captures how the epic fits within the existing system. It focuses on INTERNAL context (our codebase, patterns, constraints) rather than EXTERNAL research (library APIs, package details). -->

<!-- External dependency research (API patterns, gotchas, version details) is handled by Auto Claude during implementation planning. -->

**Phase**: System Context Analysis

**Agent**: Architect

---

## Epic Purpose (The "Why")

<!-- What problem does this epic solve? What value does it deliver? Why now? -->

**Problem Statement**:

**Business Value**:

**Target Users**:

**Expected Outcome**:

---

## Integration with Existing System

<!-- What exists today that this epic builds upon or integrates with? -->

**Current System Provides**:
-
-

**This Epic Adds**:
-
-

**Integration Points** (existing components this epic touches):
| Component | Integration Type | Notes |
|-----------|------------------|-------|
| | API / Event / Database / Shared Library | |

---

## Existing Patterns to Follow

<!-- What patterns exist in the codebase that this epic should follow? -->

**Code Patterns**:
- [ ] Error handling pattern: [describe or link]
- [ ] Logging pattern: [describe or link]
- [ ] API response format: [describe or link]
- [ ] Authentication/authorization: [describe or link]

**Architectural Patterns**:
- [ ] Service communication: [sync/async, protocol]
- [ ] Data access: [repository pattern, ORM usage]
- [ ] Configuration: [env vars, config files]

**Testing Patterns**:
- [ ] Unit test structure: [describe or link]
- [ ] Integration test approach: [describe or link]
- [ ] E2E test framework: [describe or link]

---

## System Architecture Impact

<!-- Does this epic fit within current system architecture or require updates? -->

**Current System Architecture Review**:
- [ ] Reviewed Architecture Context (Ch 3) - external interfaces
- [ ] Reviewed Architecture Building Blocks (Ch 5) - existing components
- [ ] Reviewed Architecture Solution Strategy (Ch 4) - tech stack, patterns
- [ ] Reviewed Architecture Cross-cutting (Ch 8) - security, operations, testing standards

**System Architecture Fit**:
- **Fits within current architecture**: [Yes / No / Partially]
- **Rationale**: [Why this epic does/doesn't fit current system architecture]

**Required System Architecture Updates** (if any):

| Arc42 Chapter | Update Needed | Reason |
|--------------|---------------|--------|
| Ch 3: Context & Scope | [Yes/No] | [e.g., New external integration] |
| Ch 4: Solution Strategy | [Yes/No] | [e.g., New technology adoption] |
| Ch 5: Building Blocks | [Yes/No] | [e.g., New major component] |
| Ch 8: Cross-cutting - Security | [Yes/No] | [e.g., New auth mechanism] |
| Ch 8: Cross-cutting - Operations | [Yes/No] | [e.g., New monitoring requirements] |
| Ch 8: Cross-cutting - Testing | [Yes/No] | [e.g., New test type] |

---

## Inherited Constraints

<!-- What limitations does this epic inherit from the existing system? -->

**From System Architecture**:
-

**From Technology Stack**:
-

**From Operations/Infrastructure**:
-

**From Security Requirements**:
-

---

## PoC Validation Results (if applicable)

<!-- Document any proof-of-concept work that validates feasibility -->

**PoC Conducted**: [Yes / No]

**If Yes**:
- **What was tested**:
- **Results**:
- **Implications for architecture**:

---

## Risks Identified

<!-- What could go wrong? Focus on system integration risks. -->

| Risk | Impact | Mitigation |
|------|--------|------------|
| | High/Medium/Low | |

---

## Unresolved Blockers

<!-- Only include items that genuinely block proceeding to architecture. -->

| Blocker | Why It Blocks Progress | Requires |
|---------|------------------------|----------|
| | | PO Decision / External Information / Feasibility Testing |

---

## System Context Checklist

<!-- Verify system context analysis is complete -->

**System context is complete when we can answer**:
- [ ] How does this epic integrate with existing components?
- [ ] What existing patterns should we follow?
- [ ] What constraints do we inherit from the system?
- [ ] Are there blockers that prevent us from proceeding?
- [ ] Do we have enough context to design the architecture?

---

## Outcomes

**Feasibility**: [Feasible / Not Feasible / Feasible with Constraints]

**Key Findings**:
1.
2.
3.

**Recommendation**: [Proceed / Do Not Proceed / Proceed with Changes]

**Confidence Level**: [High / Medium / Low]

---

## Next Steps

1. Proceed to technology selection and ADR creation
2. Design component architecture
3. Create architecture review checklist

---

## References

<!-- Links to relevant internal documentation consulted -->

-

---
