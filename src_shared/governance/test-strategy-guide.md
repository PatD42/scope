# Test Strategy Guide

Used by the architect when creating test strategies during epic refinement.
READ this file during architecture_design phase.

---

## Core Principle: Test as Soon as Possible

Write tests at the EARLIEST point where the test becomes possible, not a moment later.
Fixing issues in closed stories is expensive (context lost after completion).

## Coverage Floor: Every Story Reaches 90%+

Every story must reach 90%+ automated test coverage for the code it creates or modifies.

Use this as a planning and sequencing constraint:
- break stories so their code can be tested to 90%+ within the story
- do not defer essential testability to later stories without an explicit, documented exception
- if a story cannot realistically reach 90%+, the architect must document why and what compensating tests or controls replace the missing coverage

## Test Types by Story Scope

### Unit Tests: Always in Each Story
Every story includes unit tests for code it implements. Fast, isolated, no external dependencies.

### Integration Tests: When Component Integration Exists
**Include in story if:**
- Component integrates with external service (OAuth + Google)
- Component integrates with database (model + PostgreSQL)
- Story completes self-contained component with dependencies

**Defer to later story if:**
- Integration requires multiple stories (auth + session + API)
- Component is partial (model exists but service incomplete)

### E2E Tests: When User Flow Completes
**Include in story if:**
- Story delivers vertical slice (complete API endpoint)
- Story completes user-facing feature

**Defer to later story if:**
- User flow requires multiple stories
- Feature incomplete (login exists but no protected resources)

## Cross-Epic Test Evolution

Tests are living artifacts that evolve across epics.

### Progressive E2E Pattern

Don't wait for final epic. Build tests progressively:

**Epic 1: User Authentication**
```
user_lifecycle_journey.test:
  [done] User logs in with Google OAuth
  [done] User sees dashboard
  [future] User updates profile (Epic 2)
  [future] User changes settings (Epic 3)
  [done] User logs out
```

**Epic 2: Profile Management** — EXTENDS the same test file:
```
user_lifecycle_journey.test:
  [done] User logs in
  [done] User sees dashboard
  [NEW]  User updates profile  ← added in Epic 2
  [future] User changes settings (Epic 3)
  [done] User logs out
```

**Benefits:** Catch integration issues early, each epic tests current system state, no "big bang" integration at the end.

### Test Organization

Organize by user journey, not by epic:

**Good:**
```
tests/e2e/
  user_lifecycle_journey.test    # Grows across epics
  admin_management_journey.test
  payment_flow_journey.test
```

**Bad:**
```
tests/e2e/
  epic1_auth.test       # Duplicates user flow
  epic2_profile.test    # Duplicates user flow
```

## Story Sequencing for Testability

When breaking epic into stories, sequence for early testing:

**Good** (enables testing early):
```
1. User model + database → Unit tests
2. OAuth provider → Unit + Integration (OAuth + Google)
3. Login endpoint → Unit + Integration + E2E (FIRST USER FLOW)
4. Protected endpoint → Extends E2E
5. Logout → Completes E2E
```

**Bad** (testing delayed):
```
1. User model → No tests beyond unit
2. Session management → Still waiting
3. Auth middleware → Still waiting
4. OAuth provider → Still waiting
5. Login endpoint → Finally can test (too late)
```

## Test Architecture for Extensibility

1. **Page Object Model**: Encapsulate UI interactions for reusability
2. **Modular test steps**: Each step independent, can be reordered
3. **Shared fixtures**: Test data reused across tests
4. **Clear extension points**: Document where future epics will extend

## Cross-Epic Test Planning

When analyzing an epic, identify:

```yaml
Cross-Epic Test Planning:
  Existing tests to extend:
    - user_lifecycle_journey.test (from Epic 1)
      Current: login → dashboard → logout
      Extend: login → dashboard → update profile → logout

  New tests to create:
    - profile_validation_journey.test (profile-specific)

  Future extensions (documented for next epic):
    - Epic 3 will extend user_lifecycle to add settings
```

## Test Requirements in Story Definition

For each story, specify:

```yaml
Test Requirements:
  coverage_target: "90%+ automated coverage for story-owned code"
  unit:
    - Profile validation logic
    - Database update operations
  integration:
    - Profile endpoint + database
    - Auth middleware + profile access
  e2e:
    - EXTEND: user_lifecycle_journey.test
      Add step: User updates profile
      Insert between: dashboard → logout
  Cross-Epic Context:
    - Extends Epic 1 authentication test
    - Epic 3 will further extend with settings
```
