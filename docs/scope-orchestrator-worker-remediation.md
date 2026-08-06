# Scope Orchestrator/Worker Remediation Ledger

Status: implementation complete; production dogfood pending

This ledger is the implementation checklist for closing the gaps found while
comparing the current Scope refactor with
`scope-orchestrator-worker-refactoring-plan.md` and the independent `scope-cl`
implementation. It supersedes the unverified consolidated fix list; completion
requires the acceptance checks below, not just source edits.

## P0 — workflow integrity blockers

- [x] Persist Gate 0–3 user approvals as canonical, artifact-hash-bound
  attestations. Validators must reject a phase transition when the matching
  approval is absent, stale, for a different epic, or for different artifacts.
- [x] Remove the Gate 3/finalize ordering ambiguity: the user approves a
  deterministic final-handoff candidate, then the finalize worker persists the
  approved summary/status, and handoff validation verifies the attestation.
- [x] Add a locked, content-bound attribution channel for trusted deterministic
  operations and reviewer runs. Audit preparation/gates/synthesis application,
  refinement packet/review application, proof preflight, and an authorized
  dependency-baseline merge must not require manual incident exemptions.
- [x] Assign deterministic review-packet creation to an executable helper. The
  packet must derive topology and counts from `refinement-policy.yaml` and must
  be attributed before reviewer launch.
- [x] Permit honest `user_input`, `blocked`, and `failed` results to contain only
  validations actually executed. Require every declared validation, with zero
  failures/errors/skips, only for `completed`.
- [x] Implement the promised fresh read-only diagnostic worker end to end, or
  remove the public contract. The chosen implementation must cover schema,
  policy, prompt, command invocation, provider permissions, and tests.

## P1 — durable evidence and execution safety

- [x] Add a deterministic proof-preflight executor. Execute the exact declared
  command, terminate the whole process group on timeout, parse non-negative
  counts, store content-bound logs/evidence atomically, and publish a trusted
  operation receipt. Do not copy scope-cl's `shell=True` timeout implementation.
- [x] Materialize correction attribution into canonical epic evidence; permanent
  refinement validation must not depend on prunable
  `tmp_debug/scope-runs/.../run.yaml` files.
- [x] Prevent finalize or later deterministic edits from silently invalidating
  accepted correction snapshots. Any intended post-correction transition must
  have an attributed, content-bound receipt and update canonical evidence.
- [x] Preserve the installed Scope root independently from the implementation
  worktree. A newly created Git worktree must not assume ignored `.claude/` or
  `plugins/scope/` installations were copied into it.
- [x] Enforce critical-risk user approval mechanically rather than merely
  declaring `explicit_user_residual_risk_approval` in policy.
- [ ] Complete authenticated Claude write-worker dogfood. Verify the actual
  runner's inline schema, permission model, denial behavior, usage capture,
  cancellation, timeout, partial-change evidence, and supported platforms.

## P2 — correctness and maintainability

- [x] Sample process-group state before reaping individual descendants so
  `state_at_parent_exit` is truthful. Preserve strict containment; allow only a
  bounded natural-teardown grace before forced termination.
- [x] Give unattributed-change incidents stable IDs and resolve under the run
  lock. Add a re-tampering regression; retain Scope's full HEAD/content manifest
  lineage instead of porting redundant path hashes from scope-cl.
- [x] Replace substring proof-path matching with exact command-token matching.
- [x] Remove duplicated review-topology prose after packet generation consumes
  the canonical `refinement-policy.yaml` mapping.
- [x] Filter generated artifacts (`__pycache__`, `*.pyc`, `.pytest_cache`, and
  `.DS_Store`) in both Unix and Windows installers, with install-smoke coverage.
- [x] Make evidence-anchor syntax compatible with real supported-language
  symbols while retaining repository containment and unique resolution.
- [x] Keep Claude shell permissions bounded, but support the command families
  required for iterative implementation and debugging after live dogfood proves
  the necessary surface.
- [x] Avoid rewriting the complete fsynced `run.yaml` every poll second when no
  durable state changed. Preserve a bounded heartbeat and crash-recovery data.
- [x] Update the Codex workflow skill so implementation roles run in fresh
  workers rather than the main conversational session.
- [x] Reduce the four public command bodies by at least 50 percent from the
  recorded 79,414-byte baseline without removing executable gates.

## P3 — provenance and delivery

- [x] Replace the pre-existing Claude PTY reviewer after live dogfood proved the
  authenticated headless CLI was the simpler and more reliable transport.
- [ ] Split the dirty refactor into honest, reviewable, independently green
  commits only after the user confirms the labels. Do not claim that a
  retrospective split proves characterization tests historically came first.

## Security follow-up — 2026-08-03

- [x] Require the dependency-baseline merge to exactly name the full commit
  pinned in the epic handoff, reject Git global options and moving refs, require
  a clean pre-merge tree, preview conflicts, and verify the resulting parents
  and fixed commit label.
- [x] Treat `.` consistently as repository-root write scope.
- [x] Attribute tracked, untracked, and ignored filesystem changes and reject
  writable scopes containing symlinks whose targets escape the working root.
- [x] Fail audit validation when a completed reviewer receipt is marked skipped,
  bind gate evidence by hash, disallow gate waivers, and conservatively select
  one complete finding candidate when reviewers disagree.
- [x] Restrict transport normalization to provider-introduced null placeholders;
  semantic contract violations now fail validation instead of being repaired.
- [x] Reject duplicate proof-count labels and execute proof commands with a
  non-login shell.
- [x] Allocate trusted-operation IDs under the run lock, expose status/recovery/
  cancellation, shorten the timeout, and preserve unpublished worker changes.
- [x] Validate mutable frontmatter field shape, enforce reviewer read-only tool
  permissions, and ignore Python cache/coverage artifacts in source control.

## Acceptance checks

- [x] Restart tests prove that no Gate 0–3 approval can be skipped and stale
  attestations fail after artifact changes.
- [x] End-to-end command tests cover deterministic writes followed by worker
  launch without manual incident resolution.
- [x] Proof execution, correction durability, fresh-worktree lookup, incident
  re-tampering, diagnostic jobs, installer parity, and provider-child teardown
  have regression tests.
- [x] `scripts/validate-pr-checks.sh` passes with at least 90 percent measured
  coverage, and the exact pass/fail/error/skip totals are reported.
- [ ] One real low/medium-risk epic and the primary-provider instruction
  ablation complete before the refactor is called production-ready.

## Verification record

- On 2026-08-03, `scripts/validate-pr-checks.sh` passed after the security
  follow-up, including adversarial dependency-merge, operation recovery, and
  cancellation regressions.
- Unit result: 664 passed, 0 failed, 0 errors, and 0 skipped in 204.10 seconds.
  Measured coverage: 90 percent (9,684 statements, 1,007 missed).
- On 2026-08-02, `scripts/validate-pr-checks.sh` passed all whitespace,
  generated-file, mirrored-source, install-smoke, Windows-parity, hook,
  invocation, protocol, test, and coverage checks.
- Unit result: 582 passed, 0 failed, 0 errors, and 0 skipped in 164.93 seconds.
  Measured coverage: 90 percent (8,905 statements, 924 missed).
- The measured public command set (`audit_epic`, `epic_refine`, and the Claude
  and Codex `implement` variants) is 39,478 bytes, down by 50.3 percent from the
  recorded 79,414-byte baseline, while retaining executable worker and
  validation gates.
- Claude workers and reviewers now use the authenticated headless CLI directly.
  Regression tests cover command isolation, stdin/stdout transport, timeout,
  cancellation, usage capture, and failure metadata without a PTY dependency.

## Open production-readiness work

- Authenticated Claude write-worker dogfood is blocked locally: on 2026-08-03,
  Claude CLI 2.1.220 reported `loggedIn: false` and `authMethod: none`. Fake
  provider regressions cover the runner contract, but do not substitute for a
  live authenticated write test or supported-platform dogfood.
- The real low/medium-risk epic and primary-provider instruction ablation need a
  selected epic and an authenticated primary provider.
- Commits remain intentionally uncreated. Repository policy requires the user
  to confirm each meaningful commit label before committing this dirty refactor.
