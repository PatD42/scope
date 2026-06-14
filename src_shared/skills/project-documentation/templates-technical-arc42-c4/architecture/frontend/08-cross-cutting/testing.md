# Architecture - Testing

**Parent**: [Architecture - Cross-cutting Concepts](cross-cutting.md)

---

## Testing Philosophy

**Principles**:
- Test early and often
- Fast feedback loops
- Test pyramid: Many unit tests, fewer integration tests, few E2E tests
- Tests as documentation
- Fail fast on test failures

---

## Test Levels

### Unit Tests

**Purpose**: Test individual functions, methods, or classes in isolation

**Characteristics**:
- Fast execution (milliseconds)
- No external dependencies (database, network, filesystem)
- Use mocks/stubs for dependencies
- High coverage of edge cases

**Coverage Target**: 80%+ statement coverage

**Tools**: [Jest / pytest / JUnit / xUnit / etc.]

**Responsibility**: Developer

**Examples**:
- Pure function logic
- Business rule validation
- Data transformations
- Utility functions

**Best Practices**:
- One test per behavior
- Arrange-Act-Assert pattern
- Descriptive test names
- Test edge cases and error conditions

---

### Integration Tests

**Purpose**: Test interactions between components or with external systems

**Characteristics**:
- Slower than unit tests (seconds)
- May use test databases, mock services
- Test component boundaries
- Verify contracts between services

**Coverage Target**: 70%+ of integration points

**Tools**: [Integration test framework]

**Responsibility**: Developer / SDET

**Examples**:
- Database operations (with test DB)
- API endpoint testing
- Service-to-service communication
- Message queue integration

**Best Practices**:
- Use test containers for dependencies (e.g., Testcontainers)
- Isolate test data between tests
- Reset state between tests
- Test both success and failure scenarios

---

### End-to-End (E2E) Tests

**Purpose**: Test complete user workflows through the system

**Characteristics**:
- Slowest tests (minutes)
- Full system deployment
- Real or production-like environment
- User perspective testing

**Coverage Target**: Key user paths (not exhaustive)

**Tools**: [Selenium / Cypress / Playwright / Postman / etc.]

**Responsibility**: SDET

**Examples**:
- User registration and login
- Complete purchase flow
- Admin workflows
- Critical business processes

**Best Practices**:
- Focus on happy paths and critical flows
- Use page object pattern for UI tests
- Minimize flakiness (proper waits, stable selectors)
- Run in CI/CD pipeline before deployment

---

## Test Organization

### Directory Structure

```
project/
├── src/
│   └── [source code]
├── tests/
│   ├── unit/
│   │   ├── services/
│   │   ├── utils/
│   │   └── models/
│   ├── integration/
│   │   ├── api/
│   │   ├── database/
│   │   └── external/
│   └── e2e/
│       ├── user-flows/
│       └── admin-flows/
```

### Naming Conventions

**Test Files**:
- Unit: `*.test.js` or `*_test.py`
- Integration: `*.integration.test.js` or `*_integration_test.py`
- E2E: `*.e2e.test.js` or `*_e2e_test.py`

**Test Names**: Descriptive and readable
- `test_user_registration_with_valid_email_succeeds`
- `it('should return 404 when user not found')`
- `describe('OrderService') / describe('when order is valid')`

---

## Test Data Management

### Strategy

**Approaches**:
- **Fixtures**: Static test data loaded before tests
- **Factories**: Programmatic test data generation
- **Seed data**: Minimal data set for testing
- **Synthetic data**: Randomly generated realistic data

### Test Data Isolation

**Principles**:
- Each test creates its own data
- Tests don't share data
- Clean up after tests (or use transactions)
- No dependencies on data order

**Implementation**:
```
Before Each Test:
  1. Start transaction (or create isolated data)
  2. Set up required test data
  3. Run test
  4. Rollback transaction (or clean up data)
```

### Test Fixtures

**Location**: `tests/fixtures/` or `tests/data/`

**Format**: JSON, YAML, or language-specific

```yaml
# fixtures/users.yaml
admin_user:
  email: admin@example.com
  role: admin
  status: active

regular_user:
  email: user@example.com
  role: user
  status: active
```

**Usage**:
```javascript
const adminUser = loadFixture('users.yaml').admin_user;
```

---

## Test Doubles

### Types

**Mock**: Object that verifies it was called correctly
```javascript
const mockEmailService = {
  send: jest.fn()
};
// Later: expect(mockEmailService.send).toHaveBeenCalledWith(...)
```

**Stub**: Object that returns predefined responses
```javascript
const stubUserRepo = {
  findById: () => ({ id: 1, name: 'Test User' })
};
```

**Fake**: Simplified working implementation
```javascript
class FakeDatabase {
  constructor() { this.data = {}; }
  save(id, value) { this.data[id] = value; }
  get(id) { return this.data[id]; }
}
```

**Spy**: Wrapper that records interactions
```javascript
const spy = jest.spyOn(service, 'method');
```

### When to Use

- **Unit tests**: Use mocks/stubs extensively
- **Integration tests**: Use fakes or real dependencies
- **E2E tests**: Use real systems (or production-like fakes)

---

## Continuous Testing

### CI/CD Integration

**On Every Commit**:
1. Run unit tests (fast feedback)
2. Run linting and static analysis

**On Pull Request**:
1. Run unit tests
2. Run integration tests
3. Run security scans
4. Check code coverage

**Before Deployment**:
1. Run full test suite (unit + integration + E2E)
2. Run performance tests
3. Run security tests

### Test Execution

**Parallel Execution**: Run tests in parallel for speed

**Test Selection**: Run only affected tests for faster feedback

**Flaky Test Handling**:
- Quarantine flaky tests
- Investigate and fix root cause
- Retry policy: Maximum 2 retries, then fail

### Coverage Reporting

**Tools**: [Istanbul / Coverage.py / JaCoCo / etc.]

**Reports**:
- Overall coverage percentage
- Coverage by module/package
- Uncovered lines
- Coverage trends over time

**Gates**:
- Minimum coverage threshold (e.g., 80%)
- Coverage must not decrease
- Critical paths must have 100% coverage

---

## Testing Best Practices

### General

1. **Fast tests**: Optimize for speed, especially unit tests
2. **Isolated tests**: No dependencies between tests
3. **Repeatable tests**: Same input = same output
4. **Self-validating**: Tests report pass/fail clearly
5. **Timely**: Write tests as you write code (TDD)

### Avoid

- Testing implementation details (test behavior, not internals)
- Brittle tests (tightly coupled to code structure)
- Slow tests in unit test suite
- Shared mutable state between tests
- Tests that require manual setup

### Code Review

**Test Review Checklist**:
- [ ] Tests cover happy path
- [ ] Tests cover error cases
- [ ] Tests are readable and well-named
- [ ] Tests are fast (unit) or appropriately slow (E2E)
- [ ] No hardcoded test data (use fixtures/factories)
- [ ] Tests clean up after themselves

---

## Testing Tools

### Recommended Stack

**Unit Testing**:
- Framework: [Jest / pytest / JUnit]
- Assertion library: [Built-in / Chai / Hamcrest]
- Mocking: [Jest / unittest.mock / Mockito]

**Integration Testing**:
- API testing: [Supertest / RestAssured / Postman]
- Database testing: [Testcontainers / In-memory DB]

**E2E Testing**:
- Browser automation: [Playwright / Cypress / Selenium]
- API automation: [Postman / RestAssured]

**Test Data**:
- Factories: [Factory Bot / Faker.js]
- Fixtures: [YAML / JSON files]

**Coverage**:
- [Istanbul / Coverage.py / JaCoCo]

---

## Performance Testing

### Load Testing

**Tool**: [JMeter / k6 / Gatling / Locust]

**Scenarios**:
- Normal load: Expected concurrent users
- Peak load: Maximum expected concurrent users
- Stress test: Beyond maximum capacity

**Metrics**:
- Response time (p50, p95, p99)
- Throughput (requests per second)
- Error rate
- Resource utilization (CPU, memory)

### Performance Benchmarks

**Baseline**: Establish performance baseline

**Regression Testing**: Run on every major change

**Thresholds**:
- p95 response time < [X]ms
- Error rate < [Y]%
- Throughput > [Z] req/s

---

## Security Testing

### Automated Security Tests

**Static Analysis**: [SonarQube / Semgrep / Bandit]

**Dependency Scanning**: [Snyk / Dependabot / OWASP Dependency Check]

**SAST**: Static application security testing

**DAST**: Dynamic application security testing

### Manual Security Testing

**Penetration Testing**: [Frequency: Annually / Before major releases]

**Security Audit**: Code review for security vulnerabilities

**Threat Modeling**: Identify and mitigate security risks
