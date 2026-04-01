# Production Code Rules

Rules that apply to ALL production code written by any agent. READ this file — do not duplicate its contents.

---

## Rule 1: File Plan Intent Is Source of Truth

The file plan intent defines what the code must do. Tests validate behavior but do NOT define the full scope. If all tests pass but the code doesn't do what the intent says, that is a FAILURE.

When tests and intent conflict, intent wins.

## Rule 2: No Stubs or Placeholders

The following in production code are FAILURES:
- `# TODO`, `# Placeholder`, `# Stub`, `# Mock`
- `pass` in a function that should have logic
- `NotImplementedError` in code that should be implemented
- Hardcoded return values where real computation is expected
- `raise NotImplementedError("coming soon")`

## Rule 3: I/O Must Be Real

If the file plan says the function sends, calls, queries, uploads, fetches, connects, writes to, or reads from something — the implementation MUST contain real I/O code (HTTP client, DB driver, file system operations). Tests may mock the I/O boundary for speed, but the production code path must be real.

## Rule 4: No Hardcoded Values

Unless the user specifically approved it in the spec, all configurable values must come from `.yaml` config files — not literals in code. This includes: URLs, ports, thresholds, model names, bucket names, API keys, timeouts, retry counts.

If the config file doesn't have the value yet, add it there and read from config.

## Rule 5: All Planned Files Must Be Touched

Both `files_to_create` AND `files_to_modify` in the file plan are equally mandatory. Skipping a file from `files_to_modify` is as much a failure as skipping a file from `files_to_create`.

**Self-check before completing:** Compare files you changed (git diff --name-only) against ALL files listed in the file plan. If any planned file is missing from your changes, you are not done.

## Rule 6: Live Smoke Test for New External Services

If this story integrates with a new external service (API, database, cloud service, Docker container, cloud platform) for the first time, run a smoke test against the live service. Confirm:
- Connection works
- Authentication works
- A basic request/response round-trip works

Mock-only validation of external services is insufficient — it hides auth failures, serialization mismatches, network issues, and configuration errors.

**This includes:** new Docker images (build and run them), new database tables (verify they exist), new cloud APIs (verify auth works), new infrastructure (verify it deploys).

## Rule 7: No Redundant Tests

Before writing new tests, check what existing tests already cover. Do not duplicate test coverage across unit/integration/e2e layers.

## Rule 8: Components Must Be Wired

Creating a component is not enough — it must be imported and used by the system it's designed to serve. A class that exists but is never called from anywhere is an incomplete implementation.

**Self-check:** For each new class/module you created, verify it is imported and used somewhere upstream (not just in its own tests).

## Rule 9: Security by Default

- Validate input at system boundaries (API endpoints, config loading, external data)
- Trust internal function calls (don't re-validate within the same service)
- No hardcoded credentials or secrets in code
- Use environment variables or config files for sensitive configuration

## Rule 10: Error Handling

- Fail fast with clear error messages
- Don't catch errors you can't handle meaningfully
- No silent failures or empty catch blocks
- Log errors with context (what operation, what input, what went wrong)
