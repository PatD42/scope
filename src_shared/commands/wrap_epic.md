---
name: wrap_epic
description: Finalize one delivery-complete epic through a sealed, approved, exact commit and merge.
args: "{epic-id}"
---

# wrap_epic

Invocation is `scope:wrap_epic {epic-id}` in Codex and `/wrap_epic {epic-id}`
in Claude.

This command only closes an already completed delivery. It does not implement,
audit, remediate, rewrite documentation, generate summaries, discover decisions
or lessons, or infer which dirty files belong to the epic. The deterministic
finalizer owns archival, exact staging, commit, merge, recovery, and the
post-merge CodeGraph refresh.

## Resolve the sealed delivery

Resolve exactly one repository root, epic worktree, active epic directory, and
Scope installation. Reject an empty or ambiguous epic/worktree match, a foreign
branch, or roots that do not describe the same Git repository.

```bash
EPIC_ID="{epic-id}"
REPOSITORY_ROOT="<main repository root>"
WORKING_ROOT="<epic worktree root>"
EPIC_DIR="<active epic directory in the worktree>"
IMPLEMENT_RUN="${REPOSITORY_ROOT}/tmp_debug/scope-runs/${EPIC_ID}/implement/run.yaml"

# Codex:
SCOPE_ROOT="${REPOSITORY_ROOT}/plugins/scope"
# Claude instead uses:
# SCOPE_ROOT="${REPOSITORY_ROOT}/.claude"

FINALIZER="${SCOPE_ROOT}/scripts/scope-wrap-finalize.py"
WRAP_POLICY="${SCOPE_ROOT}/config/wrap-policy.yaml"
AUDIT_POLICY="${SCOPE_ROOT}/config/audit-policy.yaml"
CODEGRAPH_POLICY="${SCOPE_ROOT}/config/codegraph-policy.yaml"
```

Require the finalizer and policies. Use one Python interpreter throughout.

`implement` is the sole owner of the durable `seal` operation and creates it
immediately after the delivery summary. Never reconstruct or create a seal in
this command. A missing seal means delivery is incomplete: return read-only
`NOT_READY` and instruct the user to resume `scope:implement {epic-id}` in
Codex or `/implement {epic-id}` in Claude so it can finish delivery and retry
its crash-idempotent seal operation.

## Verify readiness

Verification is read-only and survives deletion of `tmp_debug`:

```bash
"$PYTHON_CMD" "$FINALIZER" verify "$EPIC_DIR" \
  --repo-root "$WORKING_ROOT" --policy "$WRAP_POLICY" \
  --audit-policy "$AUDIT_POLICY"
```

Proceed only for `status: verified`. This requires the current approved handoff,
delivery evidence and summary, terminal audit PASS, current seal, exact sealed
delta, clean ownership state, and every manifest documentation obligation
implemented before audit.

On any readiness failure, return `NOT_READY` with the finalizer's exact errors.
Do not archive, stage, commit, merge, update tracking, or synchronize CodeGraph.
Recommend resuming `implement` when repair is possible. If the user wants to
abandon the epic, return `ABANDONMENT_DEFERRED`; abandonment has no automated
mutation path in this command.

## Prepare exact closure

Prepare only after verification:

```bash
"$PYTHON_CMD" "$FINALIZER" prepare "$EPIC_DIR" \
  --run "$IMPLEMENT_RUN" --main-root "$REPOSITORY_ROOT" \
  --policy "$WRAP_POLICY" --audit-policy "$AUDIT_POLICY"
```

Accept only `prepared` or `already_prepared`. The result must provide the
archived epic directory, staged tree, current main HEAD, worktree HEAD, fixed
closure label, fixed merge label, and seal hash. The prepared state is the exact
sealed implementation delta plus archival. Do not add files, broaden staging,
rewrite links or documentation, or create a separate tracking marker.

Present one approval request containing:

- the exact staged tree;
- the current main HEAD and main branch;
- the fixed closure label and merge label;
- the archived epic path and seal hash; and
- the explicit intent to create the closure commit and immediately merge that
  exact commit into the displayed main HEAD.

Approval is valid only for those displayed values. Cancellation leaves the
prepared state resumable and creates no commit or merge.

## Commit and merge the approved state

After explicit approval, pass back exactly the approved identities:

```bash
"$PYTHON_CMD" "$FINALIZER" commit-merge "$ARCHIVED_EPIC_DIR" \
  --run "$IMPLEMENT_RUN" --main-root "$REPOSITORY_ROOT" \
  --approved-staged-tree "$APPROVED_STAGED_TREE" \
  --approved-main-head "$APPROVED_MAIN_HEAD" \
  --approved-main-branch "$APPROVED_MAIN_BRANCH" \
  --policy "$WRAP_POLICY" --codegraph-policy "$CODEGRAPH_POLICY"
```

Do not run Git or CodeGraph separately. The finalizer rechecks the approved
tree, main HEAD, locks, roots, labels, and seal; commits the fixed closure;
merges that exact commit; verifies the result; and refreshes CodeGraph at the
main root. Drift stops before mutation and requires a new prepare result and
approval. `already_prepared` and `already_merged` are resumable/idempotent
states, not permission to weaken checks.

## Final response

Report the exact outcome (`NOT_READY`, `PREPARED_NOT_APPROVED`, `MERGED`,
`ALREADY_MERGED`, or `ABANDONMENT_DEFERRED`), seal hash, staged tree, approved
main HEAD and branch, closure and merge commits when present, archived epic
path, and CodeGraph status. Report any pending optional external synchronization
without claiming it completed. Never claim wrap completion unless the finalizer
returns `merged` or `already_merged`.
