# Developer Pre-Completion Checklist

**MANDATORY: Read this file from disk before marking ANY story complete.**
Do NOT rely on memory. Do NOT summarize. READ THE FILE every time.

---

## Before Marking Complete, Verify ALL Items:

### Story Completion Proof

- [ ] **Acceptance-proof summary complete** — For every affected acceptance criterion and boundary-plan obligation, your completion summary maps the obligation to concrete evidence:
  - Promise verified
  - Traceability row ID(s), when `acceptance-traceability.yaml` exists
  - Verification method
  - Real runtime path used: yes/no
  - Representative data used: yes/no
  - Observable result
  - Remaining unproven work, if any
- [ ] **Runtime path proven for integration work** — If the story adds or changes an adapter, mapper, importer, writer, parser, service call, queue/worker path, scheduled job, backfill, migration, CLI, dashboard/API integration, or any side-effecting component, unit tests alone are insufficient. Prove the intended entrypoint calls the component, upstream inputs are available there, and downstream output/state is produced.
- [ ] **Promised outputs observed** — If the story promises new output, persisted rows, generated files, extracted items, metrics, events, or side effects, provide a representative run showing the output exists. If an acceptance criterion names a threshold, measure it. If zero output is valid, the acceptance criterion or boundary plan must explicitly say zero is valid.
- [ ] **Precise completion status used** — Use `verified` only when every required proof passed and promised value was observed through the intended path. Use `implementation_complete_unverified` or `blocked` when proof is partial, and record the missing proof in `remaining_unproven_work`.

### Code Quality (see production-code-rules.md for details)

- [ ] **Boundary obligations satisfied** — Re-read the implementation boundary plan. Does the code satisfy every `required_contract`, `required_touchpoint`, `forbidden_change`, and `proof_obligation`, not just what tests check?
- [ ] **Candidate/developer-discovered files documented** — Record candidate files used, relevant candidate files skipped, and developer-discovered files with source evidence. Candidate files are advisory; unexplained changed files are not allowed.
- [ ] **No stubs or placeholders** — No TODO, Placeholder, Stub, Mock, pass, NotImplementedError in production code.
- [ ] **I/O is real** — If intent says "calls/sends/queries", real I/O code exists (not hardcoded returns).
- [ ] **No hardcoded values** — All configurable values in `.yaml` config, not literals in code.
- [ ] **Components are wired** — Every new class/module is imported and used upstream (not just in its own tests).

### Integration

- [ ] **Live smoke test wired and run** — If this story introduces a new external service, local/cloud dependency, runtime-required acceptance row, migration/backfill/bootstrap/onboarding/reindex flow, or end-to-end value path, create or update the smoke checker that exercises the real path. Run it before marking the story complete and record the command, environment, result, and evidence in `acceptance-traceability.yaml`.
- [ ] **Runtime-required rows not deferred to audit** — Every affected `runtime_evidence.required: true` row must have a concrete command/checker and a passing result before implementation is considered complete. If credentials or infrastructure are missing, leave the story non-complete as `blocked_missing_runtime_input` and report the blocker; do not wait for `/audit_epic` to discover it.
- [ ] **Contract compliance** — If `contracts.py` exists, `mypy --strict` passes on all files you touched.
- [ ] **Coverage threshold met** — Story-level automated test coverage is 90%+ for the code you created or modified, unless the approved test strategy documents an explicit exception.

### Consistency

- [ ] **Pattern consistency** — Does this story follow the same patterns as previous stories? (error handling, naming, logging, config access). If different, flag as `decision_candidate`.
- [ ] **No dead code** — After fix cycles, scan for unused imports, orphaned functions, commented-out code from earlier attempts.
- [ ] **No redundant tests** — New tests don't duplicate existing coverage.

### Governance

- [ ] **Lesson compliance** — Re-read `docs/lessons-learned/INDEX.md`. Any applicable lesson violated = bug.
- [ ] **Developer-discovered files documented** — Every modified file that is not a candidate file or required touchpoint is in your agent summary under `developer_discovered_files` with evidence.
- [ ] **Scope check** — Did you add functionality outside the boundary plan? Stick to binding obligations. Don't gold-plate.
- [ ] **Decision tracking** — If you made an unplanned architectural choice, flag it as `decision_candidate` in concerns.
