---
name: implement
description: Implement an approved epic through bounded story workers, proof, audit, and remediation.
args: "{epic-id}"
---

# scope:implement

You are the sole user-facing orchestrator. Fresh implementation workers own
bounded source changes; independent reviewers remain read-only. Own user
decisions, worktree/Git lifecycle, worker supervision, proof, nested audit, and
the final status. Do not implement or semantically review code in this session.

Report `delivery-complete` only when the current approved handoff, every story,
strict proof evidence, epic verification, audit, and implementation summary all
pass. Otherwise report the exact partial or blocked state.

## Resolve the approved handoff

```bash
EPIC_ID="{epic-id}"
COMMAND_ROOT="$(pwd -P)"
GIT_COMMON_DIR="$(git -C "$COMMAND_ROOT" rev-parse --path-format=absolute --git-common-dir)"
REPOSITORY_ROOT="$(cd "${GIT_COMMON_DIR}/.." && pwd -P)"
EPIC_DIR="$(find "$COMMAND_ROOT/docs/epics" -mindepth 1 -maxdepth 1 -type d \
  -iname "*${EPIC_ID}*" -print | sort | head -1)"
SCOPE_ROOT="$(cd "$COMMAND_ROOT/plugins/scope" && pwd -P)"
PROVIDER="codex"
WORKER="${SCOPE_ROOT}/scripts/scope-worker.py"
REFINEMENT="${SCOPE_ROOT}/scripts/validate-refinement.py"
DEPENDENCY_MERGE="${SCOPE_ROOT}/scripts/scope-dependency-merge.py"
AUDIT_COMMAND="${SCOPE_ROOT}/commands/audit_epic.md"
WRAP_FINALIZER="${SCOPE_ROOT}/scripts/scope-wrap-finalize.py"
WRAP_POLICY="${SCOPE_ROOT}/config/wrap-policy.yaml"
AUDIT_POLICY="${SCOPE_ROOT}/config/audit-policy.yaml"
WORKER_PROFILE="default"       # budget only when the user asks
REVIEWER_PROFILE="default"     # budget only when the user asks
REVIEWER_SET="standard"        # expanded only when the user asks
```

Resolve exactly one epic and one interpreter. Require the runner, v2 schemas,
provider policy, implementation worker, validators, audit command, wrap
finalizer/policy, and canonical artifacts. Validate; implementation never
repairs refinement:

```bash
"$PYTHON_CMD" "$REFINEMENT" validate "$EPIC_DIR" \
  --phase handoff --repo-root "$COMMAND_ROOT"
```

If current approved handoff paths are dirty, invoking this command authorizes
only the exact checkpoint label below. Stage and commit only the current
hash-bound handoff paths; preserve unrelated staged and unstaged work. Stop on
ambiguity or Git failure.

```text
refine({epic-id}): implementation handoff
```

Create or verify branch `epic/{epic-id}` in
`${REPOSITORY_ROOT}/worktree/{epic-id}`. Never overwrite repository
instructions. Link the root `.env` only when the worktree has none. Re-resolve
the epic inside the worktree, but retain the absolute installed `SCOPE_ROOT`
captured above.

```bash
WORKING_ROOT="${REPOSITORY_ROOT}/worktree/${EPIC_ID}"
EPIC_DIR="$(find "$WORKING_ROOT/docs/epics" -mindepth 1 -maxdepth 1 -type d \
  -iname "*${EPIC_ID}*" -print | sort | head -1)"
RUN="${REPOSITORY_ROOT}/tmp_debug/scope-runs/${EPIC_ID}/implement/run.yaml"
"$PYTHON_CMD" "$WORKER" init \
  --repository-root "$REPOSITORY_ROOT" --working-root "$WORKING_ROOT" \
  --scope-root "$SCOPE_ROOT" --epic-id "$EPIC_ID" \
  --command implement --worker-profile "$WORKER_PROFILE"
```

`init` prepares CodeGraph once. The runner performs a cheap incremental sync
before every implementation write job; workers only query it. Degraded
CodeGraph falls back visibly to direct reads and `rg`, never reduced proof.

For resume or interruption, use only `status`, `recover`, and identity-checked
`cancel`:

```bash
"$PYTHON_CMD" "$WORKER" status --run "$RUN"
"$PYTHON_CMD" "$WORKER" recover --run "$RUN"
"$PYTHON_CMD" "$WORKER" cancel --run "$RUN" \
  --job-id "$ACTIVE_JOB_ID" --reason "$REASON"
```

Take `ACTIVE_JOB_ID` from the current `status` response; stale cancellation is
rejected.

Stop on concurrent ownership, HEAD drift, escaping symlinks, ignored or normal
out-of-scope writes, invalid results, or failed recovery. Never auto-revert
user work or create a parallel ownership ledger.

## Exact dependency baselines

Process each full commit pin in `delivery-manifest.yaml` before the first
implementation job. Never construct a Git merge command from model or user
prose. The dedicated command verifies the exact epic/pin, canonical run and
worktree, empty job history, clean tree, local commit object, ancestry,
conflict-free preview, fixed parents, and fixed subject under the same
non-blocking mutation lock:

```bash
"$PYTHON_CMD" "$DEPENDENCY_MERGE" --run "$RUN" --epic-dir "$EPIC_DIR" \
  --dependency-epic-id "$DEPENDENCY_EPIC_ID" \
  --dependency-commit "$DEPENDENCY_COMMIT"
```

This command alone owns the authorized label
`merge({epic-id}): integrate {dependency-epic-id} implementation baseline`.
It accepts no branch tip, foreign repository, extra Git option, or alternate
message. Report any resulting merge commit. This authorizes no other commit.

## Story workers

Read `delivery-manifest.yaml` and the referenced `file-plan-story-*.yaml`
documents. Require unique story/acceptance/proof IDs, one owner per item, valid
dependencies, and an acyclic story graph. Execute dependency-ready stories in
stable order, never concurrently.

For manifest v2, also require every `documentation_obligations` row to name one
existing owner story, normalized repository-relative target path, and canonical
`requirement_ref`. Treat v1 as having no documentation obligations. Add each v2
target to only its owner story's exact write scope. The worker must implement the
required durable documentation content with that story; it may not defer it to
audit or `wrap_epic`. A new product or architecture requirement returns to
refinement instead of silently widening the obligation.

For each story, create a v2 job containing only the relevant approved artifact
hashes and authority references, its bounded read/write paths, exact validation
commands, `required_proof_ids`, and `result_path`. Candidate files are advisory; binding contracts,
touchpoints, forbidden changes, and proof obligations come from the story plan.
A path outside the declared write scope requires a new job after evidence-based
reclassification—it is not silently absorbed.

Every implementation job explicitly supplies `required_proof_ids`: the exact
owned proof IDs for story, verification, and remediation work, or `[]` only
when the named phase has no proof obligation.

```bash
"$PYTHON_CMD" "$WORKER" preflight --provider "$PROVIDER" \
  --role implementation --phase story --worker-profile "$WORKER_PROFILE" \
  --scope-root "$SCOPE_ROOT"
"$PYTHON_CMD" "$WORKER" run --provider "$PROVIDER" \
  --role implementation --job "$JOB_PATH" --result "$RESULT_PATH" \
  --cwd "$WORKING_ROOT" --access workspace-write \
  --worker-profile "$WORKER_PROFILE"
```

Accept only a v2 completed result matching the actual changed paths and every
required validation. `needs_user` must batch every currently discoverable
blocking question; explain evidence and tradeoffs to the user, persist the
answer in a canonical decision, then launch a fresh job. `blocked`, `failed`,
cancellation, missing proof, or unexplained path stops sequencing.

Each story executes its exact implementation proof without `/bin/sh -lc` and
records command, exit code, pass/fail/error/skip counts, evidence path/hash, and
affected content hashes in `implementation-evidence.yaml`. A passing proof
requires exit code 0, zero failures/errors/unexplained skips, and nonzero
applicable execution. Never let a trailing summary overwrite earlier failing
counts. Evidence must be durable and must not depend on `tmp_debug`.

## Epic verification, audit, and remediation

After every story, launch one fresh `implementation/epic_verify` worker over
the complete approved boundary. It reruns acceptance, regression, native
contract, runtime/operational, and observable-value proofs and may repair only
in-boundary defects. Product or architecture changes return to refinement. It
must leave implementation evidence that passes the complete evidence validator.

Execute the installed `audit_epic.md` contract inside this orchestrator with
the same worker/reviewer profiles and set; do not create a second
conversational orchestrator and do not substitute this session for reviewers.

For audit `FAIL`, group current remediation-required findings by coupled root
cause and launch one fresh `implementation/audit_remediation` worker per
bounded batch. Require pattern-wide inspection, sibling surfaces, strict
closure proof, and updated durable implementation evidence. Mark a finding
`remediated_pending_verification` only with that evidence, then run one
authorized targeted audit. Route product/architecture defects to refinement
and genuine user/documentation/accepted-risk decisions to the user. A targeted
`FAIL` or `BLOCKED` stops delivery.

After validated audit `PASS`, launch one `implementation/delivery_summary`
worker whose only write is `implementation-summary.md`. It summarizes durable
evidence; it does not change code, contracts, findings, Git history, or the
worktree lifecycle.

Immediately seal the completed delivery with the deterministic finalizer. It
must verify the current audit and durable implementation delta, including every
v2 documentation target, before writing the seal:

```bash
"$PYTHON_CMD" "$WRAP_FINALIZER" seal "$EPIC_DIR" \
  --run "$RUN" --policy "$WRAP_POLICY" --audit-policy "$AUDIT_POLICY"
```

A failed seal leaves delivery incomplete and must be reported; never reconstruct
or hand-author it.

All deterministic artifact mutations and write workers share the same
non-blocking working-root lock. Do not launch them concurrently.

## Final response

Report exact state, branch/worktree, dependency merges, each story/job, changed
paths, proof and test counts, epic verification, audit attempt/providers/
outcome, remediation, summary, residual risk, and blockers. Do not commit
implementation/remediation, merge the epic, remove the worktree, or push.
Recommend `scope:wrap_epic {epic-id}` only for `delivery-complete`.
