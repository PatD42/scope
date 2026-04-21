# {epic-id}: Test Strategy

---

## Meta: Phase & Agent Information

**Phase**: Phase 2 - Architecture
**Agent Role**: Architect + SDET (Software Development Engineer in Test)
**Created During**: Architecture Phase - After Architecture design
**Prerequisites**: Architecture, Epic Details, Acceptance Criteria

---

## Context Dependencies

**Required Context (must exist before this document)**:
- [{epic-id}: Architecture](link) - Components, integration points, data model
- [{epic-id}: Epic Details](link) - User stories implementation order, scope
- [{epic-id}: Acceptance Criteria](link) - What defines story completion
- [{epic-id}: System Context](link) - Risks to mitigate through testing

**Provides Context For (documents that depend on this)**:
- Development Phase: Developers write tests following this strategy
- QA Phase: QA Engineers execute tests per this plan
- [{epic-id}: Implementation Summary](link) - Documents which tests were created

---

## Overview

This page documents the testing strategy for this epic, including test types, boundaries, data requirements, and cross-epic test evolution.

**Epic Goal**: [Brief summary from epic details]

**Testing Principle**: Test as soon as possible - write tests at the EARLIEST point where they become possible.

**Coverage Policy**: Every story must achieve 90%+ automated test coverage for the code it creates or modifies, unless an explicit exception is documented in this strategy with rationale and approval.

---

## Test Scope by Story

<!-- For each story, define what tests are required -->

### Story: {story-id} - [Story Title]

**Test Types Required**:

**Coverage Target**: 90%+ automated coverage for story-owned code

#### Unit Tests
- [ ] [Component/function to test]
- [ ] [Component/function to test]
- [ ] Error handling and edge cases

**Rationale**: Every story includes unit tests for code it implements.

#### Integration Tests
- [ ] [Integration point to test]
- [ ] [Integration point to test]

**Rationale**: [Why integration tests are needed - e.g., "Completes OAuth integration with Google provider"]

**Defer if**: [Reason to defer to later story, if applicable]

#### E2E Tests
- [ ] [User flow to test]
- [ ] [User flow to test]

**Rationale**: [Why E2E tests are needed - e.g., "Completes vertical slice for login flow"]

**Defer if**: [Reason to defer to later story, if applicable]

---

### Story: {story-id} - [Story Title]

**Test Types Required**:

**Coverage Target**: 90%+ automated coverage for story-owned code

#### Unit Tests
- [ ] [Component/function to test]
- [ ] [Component/function to test]

#### Integration Tests
**Defer to**: Story {story-id} (integration not complete until then)

#### E2E Tests
- [ ] **EXTENDS**: [Existing test file from previous epic]
  - **Add step**: [New step to insert]
  - **Insert between**: [Existing steps]

**Rationale**: Extends existing user journey rather than duplicating flow.

---

## Test Boundaries

<!-- Define what each test level covers -->

### Unit Test Boundaries
**Scope**: Individual functions, classes, and modules in isolation

**Characteristics**:
- Fast (< 100ms per test)
- No external dependencies (mocked)
- Run everywhere (local, CI/CD)

**Coverage Target**: 90%+

### Integration Test Boundaries
**Scope**: Component interactions with external services/databases

**Test Environments**:
- Component + Database: [e.g., User model + PostgreSQL]
- Component + External Service: [e.g., OAuth provider + Google OAuth]

**Characteristics**:
- Moderate speed (< 5s per test)
- Requires test dependencies (Docker containers, test databases)
- Runs in CI/CD and staging

**Coverage Target**: Critical integration points

### E2E Test Boundaries
**Scope**: Complete user workflows through the system

**User Journeys**:
- [Journey 1]: [Brief description]
- [Journey 2]: [Brief description]

**Characteristics**:
- Slower (< 30s per test)
- Full system dependencies
- Runs in staging and production-like environments

**Coverage Target**: All critical user paths

---

## Cross-Epic Test Evolution

<!-- How tests extend across epics -->

### Tests Extending from Previous Epics

**Test File**: [test_file_name.test.ts] (from Epic: [EPIC-ID])

**Current State** (before this epic):
```
✅ User logs in
✅ User views dashboard
✅ User logs out
```

**Extensions** (this epic adds):
```
✅ User logs in
✅ User views dashboard
✅ User updates profile (NEW - Story {story-id})
✅ User changes settings (NEW - Story {story-id})
✅ User logs out
```

**Rationale**: [Why extending existing test rather than creating new one]

---

### New Test Files Created

**Test File**: [test_file_name.test.ts]

**Purpose**: [What this test file covers]

**Future Extensions** (documented for next epic):
- Epic {epic-id} will extend to add [feature]
- Epic {epic-id} will extend to add [feature]

---

## Test Architecture

<!-- Design patterns for maintainable, extensible tests -->

### Test Organization

```
tests/
├── unit/
│   ├── [module]/
│   │   ├── [component].test.ts
│   │   └── [component].test.ts
│   └── [module]/
│       └── [component].test.ts
├── integration/
│   ├── [integration-point].test.ts
│   └── [integration-point].test.ts
└── e2e/
    ├── [user_journey].test.ts  (grows across epics)
    └── [user_journey].test.ts
```

### Shared Test Utilities

**Fixtures**:
- [Fixture name]: [Purpose - e.g., "Test user data"]
- [Fixture name]: [Purpose]

**Page Objects** (for E2E):
- [Page object name]: [Encapsulates UI interactions for component]
- [Page object name]: [Encapsulates UI interactions for component]

**Test Helpers**:
- [Helper name]: [Purpose - e.g., "Database seeding"]
- [Helper name]: [Purpose]

### Extensibility Patterns

**Modular test steps** - Each step independent, can be reordered or extended

Example:
```typescript
class UserJourneyTest {
  async login() { /* ... */ }
  async viewDashboard() { /* ... */ }
  async updateProfile() { /* Epic 2 adds this */ }
  async changeSettings() { /* Epic 3 adds this */ }
  async logout() { /* ... */ }
}
```

**Extension points documented** - Clear markers for where future epics extend tests

---

## Test Data Requirements

<!-- Data needed for testing -->

### Test Datasets

| Dataset | Purpose | Size | Source |
|---------|---------|------|--------|
| [Dataset name] | [Purpose] | [# records] | [Where it comes from] |
| [Dataset name] | [Purpose] | [# records] | [Where it comes from] |

### Test Data Management

**Seeding Strategy**: [How test data is created - e.g., "Fixtures loaded before each test"]

**Data Isolation**: [How tests avoid interfering with each other]

**Cleanup Strategy**: [How test data is cleaned up]

### Sensitive Test Data

**PII/Secrets Handling**:
- [ ] No production data in tests
- [ ] Synthetic data generation for realistic scenarios
- [ ] Secrets injected via environment variables (not committed)

---

## Performance Testing

<!-- Performance benchmarks and targets -->

### Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| [Operation] | [Time/throughput] | [How measured] |
| [Operation] | [Time/throughput] | [How measured] |

### Load Testing

**Scenarios**:
- [Scenario 1]: [Expected load - e.g., "100 concurrent users"]
- [Scenario 2]: [Expected load]

**Tools**: [e.g., k6, JMeter, Locust]

**Run Frequency**: [When load tests run - e.g., "Before production deployment"]

---

## Security Testing

<!-- Security validation approach -->

### Security Test Coverage

- [ ] Input validation (SQL injection, XSS, command injection)
- [ ] Authentication/authorization checks
- [ ] Rate limiting and DoS protection
- [ ] Sensitive data handling (encryption, masking)
- [ ] Dependency vulnerability scanning

### Security Testing Tools

**SAST**: [Static analysis tools - e.g., "Semgrep, SonarQube"]

**DAST**: [Dynamic analysis tools - e.g., "OWASP ZAP"]

**Dependency Scanning**: [e.g., "Snyk, Dependabot"]

**Run Frequency**: [When security scans run - e.g., "Every PR, nightly"]

---

## Test Execution

<!-- How and when tests run -->

### CI/CD Integration

**On Pull Request**:
- [ ] Unit tests (all)
- [ ] Integration tests (affected components)
- [ ] Linting and code quality checks

**On Merge to Main**:
- [ ] Unit tests (all)
- [ ] Integration tests (all)
- [ ] E2E tests (smoke suite)
- [ ] Security scans

**Nightly**:
- [ ] E2E tests (full suite)
- [ ] Performance tests
- [ ] Extended security scans

### Test Environments

| Environment | Purpose | Test Types Run |
|-------------|---------|----------------|
| Local | Developer testing | Unit, Integration (subset) |
| CI/CD | Automated validation | Unit, Integration, E2E (smoke) |
| Staging | Pre-production validation | E2E (full), Performance, Security |
| Production | Smoke tests post-deployment | Smoke suite only |

---

## Test Quality Metrics

<!-- How we measure test effectiveness -->

### Coverage Metrics

**Targets**:
- Story-level automated coverage: 90%+ for the code each story creates or modifies
- Unit test coverage: 90%+
- Integration test coverage: Critical paths
- E2E test coverage: All user journeys

**Measurement**: [Tool - e.g., "Jest coverage, SonarQube"]

### Test Health Metrics

**Test Reliability**:
- Flaky test rate: < 1%
- Test failure rate: < 5% (excluding genuine bugs)

**Test Performance**:
- Unit test suite: < 5 minutes
- Integration test suite: < 15 minutes
- E2E test suite: < 30 minutes

**Maintenance Burden**:
- Tests updated per code change: Track ratio
- Test maintenance time: < 20% of development time

---

## Test Lineage

<!-- Document test evolution across epics -->

### Extended Tests

| Test File | Origin Epic | Extended By This Epic | Changes Made |
|-----------|-------------|----------------------|--------------|
| [test_file.test.ts] | [EPIC-ID] | Yes | Added [step] to [journey] |

### New Tests Created

| Test File | Type | Purpose | Future Extensions |
|-----------|------|---------|-------------------|
| [test_file.test.ts] | E2E | [Purpose] | Epic {epic-id} will add [feature] |

---

**Contributors**: Architect, SDET
