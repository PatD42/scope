# Epic Implementation Summary: [Epic Title]

---

## Meta: Phase & Agent Information

**Phase**: Phase 3 - Completion
**Agent Role**: Technical Writer + Architect
**Created During**: Epic Completion - After all stories implemented
**Prerequisites**: All stories completed, Code review done, Tests passed

---

## Context Dependencies

**Required Context (must exist before this document)**:
- [{epic-id}: Epic Details](link) - Original plan to compare against
- [{epic-id}: Design](link) - Approved design to compare against actual implementation
- [{epic-id}: Implementation Boundary Plans](link) - Binding obligations and candidate files vs. actual implementation
- [{epic-id}: Design Verification Strategy](link) - Planned proof vs. actual test and runtime evidence
- Development Phase: Completed code, tests, reviews

**Provides Context For (documents that depend on this)**:
- Future Epics: Learn from implementation experience
- Architecture Documentation: Update with design changes
- Product Decisions: Inform future product choices
- Retrospectives: Continuous improvement

---

## Implementation Overview

**Status**: [Done / Partially Done / Blocked]

**Completion Date**: YYYY-MM-DD

**Target Release**: {version}

**Stories Completed**: X of Y

---

## Stories Implemented

<!-- Factual list of what was executed. -->

| Story ID | Title | Status | Escalated? | Notes |
|---------|-------|--------|------------|-------|
| | | Done/Partial | Yes/No | Brief note if issues |

---

## Divergence from Plan

<!-- What changed from the architect's design during implementation? -->

### Design Changes

<!-- Architectural decisions that changed during implementation. -->

**Changes Made**:
- [Description of change]
  - **Why**: Reason for deviation
  - **Impact**: What this affects
  - **Story**: Which story triggered this

### Unexpected Technical Challenges

<!-- Problems not anticipated in the architecture or implementation boundary plans. -->

**Challenge 1**: [Description]
- **Impact**: How this affected implementation
- **Resolution**: How it was addressed
- **Stories affected**: List

---

## Escalations

<!-- Stories that required user intervention. -->

| Story ID | Title | Reason for Escalation | Resolution | Time Impact |
|---------|-------|----------------------|------------|-------------|
| | | [Technical block / Requirements unclear / Tests failing] | | [Hours/Days] |

### Escalation Details

#### Story {story-id}: [Title]

**Why escalated**: [Specific reason - test failures after 4 retries, missing requirements, technical blocker]

**Resolution**: [How user resolved it]

**Preventable?**: [Yes/No - could better planning have avoided this?]

---

## Reviewer Concerns and Recommendations

<!-- Aggregated from implementation and audit findings. -->

### Critical Concerns

**Concern 1**: [Description]
- **Area**: [Security / Performance / Maintainability / Architecture]
- **Story**: {story-id}
- **Recommendation**: [What should be done]
- **Status**: [Addressed / Deferred / Tracked as TD-{epic-id}-###]

### High Priority Recommendations

**Recommendation 1**: [Description]
- **Area**: [Code quality / Testing / Documentation]
- **Impact**: [What happens if not addressed]
- **Action item**: [Specific next step]

### Medium Priority Observations

- [Observation with context]

---

## Residual Risks

<!-- Risks that remain after implementation. Not anticipated risks from refinement, but new/unmitigated ones. -->

| Risk ID | Description | Probability | Impact | Mitigation Status | Owner |
|---------|-------------|-------------|--------|-------------------|-------|
| RR-{epic-id}-001 | | High/Med/Low | High/Med/Low | None/Partial/Planned | |

### Risk Details

#### RR-{epic-id}-001: [Risk Title]

**Description**: [What could go wrong]

**Why it exists**: [Why we couldn't fully mitigate during implementation]

**Impact if realized**: [Consequences]

**Recommended mitigation**: [Next steps to reduce risk]

---

## Technical Debt Incurred

<!-- NEW debt created during implementation. Not planned technical decisions, but compromises made. -->

| TD ID | Description | Impact | Reason Incurred | Tracking |
|-------|-------------|--------|-----------------|----------|
| TD-{epic-id}-001 | | High/Med/Low | [Deadline / Complexity / Unknown req] | Issue link |

### Debt Details

#### TD-{epic-id}-001: [Debt Title]

**What was compromised**: [Specific technical compromise]

**Why**: [Reason - time pressure, missing info, technical limitation]

**Impact**: [Effect on maintainability, performance, etc.]

**Cost to fix**: [Estimated effort - hours/days]

**Recommended timeline**: [When this should be addressed]

**Related stories**: [Which stories created this debt]

---

## Test Results

<!-- Aggregated test execution data with analysis of anomalies. -->

### Test Execution Summary

| Test Type | Passed | Failed | Skipped | Coverage |
|-----------|--------|--------|---------|----------|
| Unit | | | | % |
| Integration | | | | % |
| E2E | | | | % |
| **Total** | | | | % |

### Test Failures

<!-- Only failed tests that required investigation or revealed issues. -->

**Story {story-id}**: [Story title]
- **Test**: `test_name`
- **Failure reason**: [Why it failed]
- **Root cause**: [Actual issue found]
- **Resolution**: [How it was fixed]
- **Attempts before success**: [Number]

### Skipped Tests

<!-- Tests that couldn't run and why. -->

**Story {story-id}**: [Story title]
- **Test**: `test_name`
- **Reason skipped**: [Missing dependency / Environment issue / Flaky test]
- **Status**: [Tracked / Will fix / Acceptable]

### Test Quality Concerns

- [Any patterns in test failures]
- [Test coverage gaps discovered]
- [Flaky tests identified]

---

## Code Quality Signals

<!-- Patterns observed by code reviewers. -->

### Positive Patterns

- [Reusable patterns that emerged]
- [Good architectural decisions validated]

### Areas for Improvement

- [Code smells or anti-patterns observed]
- [Refactoring opportunities identified]
- [Documentation gaps]

---

## Deployment Considerations

<!-- Implementation-specific deployment notes. -->

### Configuration Changes

- [New environment variables added]
- [Configuration files modified]
- [Feature flags introduced]

### Data Migration

**Required**: [Yes/No]

**Details** (if yes):
- [Migration scripts created]
- [Rollback strategy]
- [Data validation approach]

### Deployment Risks

- [Specific concerns for deploying this epic]
- [Rollback considerations]
- [Monitoring requirements]

---

## Follow-up Actions

<!-- Concrete next steps, not vague "lessons learned". -->

### Required (Before Next Epic)

- [ ] Address TD-{epic-id}-001 (technical debt item)
- [ ] Resolve RR-{epic-id}-002 (residual risk)
- [ ] Implement recommendation from security-reviewer (concern #3)

### Recommended (For Future Epics)

- [ ] [Improvement to process based on what happened]
- [ ] [Tool or automation to prevent specific issue]
- [ ] [Additional planning step to catch specific gap]

### For Architecture Update

- [ ] Update Architecture ADR Summary with design changes from "Divergence" section
- [ ] Add residual risks to Architecture Risks page
- [ ] Document new patterns in Architecture Cross-cutting (if applicable)

---

## Notes

<!-- Any other implementation-specific context. -->

**Total implementation time**: [X days/weeks]

**Agent performance**:
- Stories completed autonomously: X
- Stories requiring escalation: Y
- Average retries before test success: Z

**Most valuable boundary-plan entries**: [Which required contracts, touchpoints, candidate files, or proof obligations helped most]

**Boundary-plan gaps**: [Where boundary-plan obligations or candidate hints were insufficient]
