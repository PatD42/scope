# Developer Pre-Completion Checklist

**MANDATORY: Read this file from disk before marking ANY story complete.**
Do NOT rely on memory. Do NOT summarize. READ THE FILE every time.

---

## Before Marking Complete, Verify ALL Items:

### Story Completion Proof

- [ ] **Acceptance-proof summary complete** — For every affected acceptance criterion and file-plan promise, your completion summary maps the promise to concrete evidence:
  - Promise verified
  - Traceability row ID(s), when `acceptance-traceability.yaml` exists
  - Verification method
  - Real runtime path used: yes/no
  - Representative data used: yes/no
  - Observable result
  - Remaining unproven work, if any
- [ ] **Runtime path proven for integration work** — If the story adds or changes an adapter, mapper, importer, writer, parser, service call, queue/worker path, scheduled job, backfill, migration, CLI, dashboard/API integration, or any side-effecting component, unit tests alone are insufficient. Prove the intended entrypoint calls the component, upstream inputs are available there, and downstream output/state is produced.
- [ ] **Promised outputs observed** — If the story promises new output, persisted rows, generated files, extracted items, metrics, events, or side effects, provide a representative run showing the output exists. If an acceptance criterion names a threshold, measure it. If zero output is valid, the acceptance criterion or file plan must explicitly say zero is valid.
- [ ] **Precise completion status used** — Do not use `complete` unless promised value was observed through the intended path. Use a non-complete status such as `implementation_complete_unverified`, `unit_verified`, `integration_verified`, `runtime_verified`, or `blocked_missing_runtime_input` when proof is partial.

### Code Quality (see production-code-rules.md for details)

- [ ] **Intent match** — Re-read the file plan intent. Does the code do what it describes, not just what tests check?
- [ ] **All planned files touched** — Compare your `git diff --name-only` against BOTH `files_to_create` AND `files_to_modify` in the file plan. Missing a file = not done.
- [ ] **No stubs or placeholders** — No TODO, Placeholder, Stub, Mock, pass, NotImplementedError in production code.
- [ ] **I/O is real** — If intent says "calls/sends/queries", real I/O code exists (not hardcoded returns).
- [ ] **No hardcoded values** — All configurable values in `.yaml` config, not literals in code.
- [ ] **Components are wired** — Every new class/module is imported and used upstream (not just in its own tests).

### Integration

- [ ] **Live smoke test** — If this story introduces a new external service, verify it works live (not just mocked).
- [ ] **Contract compliance** — If `contracts.py` exists, `mypy --strict` passes on all files you touched.
- [ ] **Coverage threshold met** — Story-level automated test coverage is 90%+ for the code you created or modified, unless the approved test strategy documents an explicit exception.

### Consistency

- [ ] **Pattern consistency** — Does this story follow the same patterns as previous stories? (error handling, naming, logging, config access). If different, flag as `decision_candidate`.
- [ ] **No dead code** — After fix cycles, scan for unused imports, orphaned functions, commented-out code from earlier attempts.
- [ ] **No redundant tests** — New tests don't duplicate existing coverage.

### Governance

- [ ] **Lesson compliance** — Re-read `docs/lessons-learned/INDEX.md`. Any applicable lesson violated = bug.
- [ ] **Unplanned changes documented** — Every file NOT in the file plan that you modified is in your agent summary under `unplanned_modifications` with justification.
- [ ] **Scope check** — Did you add functionality not in the file plan? Stick to intent. Don't gold-plate.
- [ ] **Decision tracking** — If you made an unplanned architectural choice, flag it as `decision_candidate` in concerns.
