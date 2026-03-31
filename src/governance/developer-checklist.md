# Developer Pre-Completion Checklist

**MANDATORY: Read this file before marking ANY story complete.**

This file exists as a standalone reference so it survives context summarization.
Re-read it from disk — do not rely on memory of its contents.

---

## Before Marking a Story Complete, Verify ALL 10 Items:

1. **Intent match** — Re-read the file plan intent. Does the code do what it describes, not just what the tests check? Tests can pass while intent is unfulfilled (e.g., tests mock the API call, but the real HTTP call is missing).

2. **No dead code** — After fix cycles, unused imports, orphaned functions, or commented-out code from earlier attempts often remain. Scan your changes for artifacts of failed approaches. Clean them up.

3. **Pattern consistency** — Does this story follow the same patterns as previous stories in this epic? (error handling, naming, logging, config access, test structure). If you chose a different pattern, flag as `decision_candidate` in your agent summary concerns.

4. **Lesson compliance** — Re-read `docs/lessons-learned/INDEX.md`. Does any lesson apply to what you just wrote? A lesson violation is a bug, not a suggestion.

5. **Unplanned changes documented** — Every file you modified that's NOT in the file plan must be recorded in your agent summary under `unplanned_modifications` with a justification. If you can't justify it, revert it.

6. **Contract compliance** — If `contracts.py` exists, run `mypy --strict` on all files you touched. Fix violations before completing. Don't defer type errors to the next story.

7. **Scope check** — Did you add functionality not in the file plan? Gold-plating compounds — the next story may depend on the planned interface, not your enhanced version. Stick to intent.

8. **No hardcoded values** — Unless the user specifically approved it in the spec, all configurable values must come from `.yaml` config files — not literals in code. Hardcoded URLs, ports, thresholds, model names, bucket names, API keys, timeouts, retry counts in production code are a FAILURE. If the config file doesn't have the value yet, add it there and read from config.

9. **Live smoke test for new external services** — If this story integrates with a new external service (API, database, cloud service, Docker container, cloud platform) for the first time, run a smoke test against the live service. Confirm the connection, auth, and a basic request/response work. Mock-only validation of external services is insufficient — it hides auth failures, serialization mismatches, network issues, and configuration errors. This includes: new Docker images (build and run them), new database tables (verify they exist), new cloud APIs (verify auth works), new infrastructure (verify it deploys).

10. **No redundant tests** — Before writing new tests, check what existing tests already cover. Do not duplicate test coverage across unit/integration/e2e layers. If an existing test already verifies a behavior, don't re-test the same path.

---

## How to Use This File

- **In `/implement`**: The orchestrator includes a reference to this file in every developer task description. The developer agent MUST read this file before marking any task complete.
- **In ad-hoc work**: When implementing outside of `/implement`, read this file before considering your work done.
- **After compaction**: If your context has been summarized and you're unsure whether you followed these rules, re-read this file from disk and verify each item.
- **When spawning subagents**: Include this instruction in the agent prompt: `"Before marking any task complete, read and verify all items in src/governance/developer-checklist.md (or .claude/governance/developer-checklist.md)."`
