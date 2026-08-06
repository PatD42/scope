# Scope Orchestrator and Worker Refactoring Plan

Status: implementation brief for a separate session
Prepared: 2026-08-02
Repository: `/Users/patrick/aquaforge/scope`

## 1. Purpose

Refactor `epic_refine`, `implement`, and `audit_epic` so the command running in
the user's session is a thin conversational orchestrator. Fresh, bounded
workers perform repository inspection, artifact authoring, implementation,
verification, finding synthesis, and remediation.

The user must continue talking only to the orchestrator. Workers must never ask
the user questions directly or require the user to switch into a worker thread.

This refactor must also implement the still-relevant GPT-5.6 reliability
improvements:

1. reduce active prompt size and repetition;
2. put authorization and stopping boundaries in one compact place;
3. move important compliance from prose into executable validators;
4. use fresh context for bounded work;
5. derive review accounting from durable evidence;
6. require structured proof and correction evidence before review;
7. keep existing independent reviewers without adding review rounds;
8. measure the result with representative Scope workflow regressions.

This is not a cosmetic prompt split. Success requires a real separation of
responsibilities and validator-enforced handoffs.

### 1.1 How to use this brief

This is a durable implementation reference, not a runtime prompt and not a
single-session checklist. Start with Sections 1-7 and 24-28, select one delivery
unit, then read only its detailed sections:

| Delivery | Detailed sections |
|---|---|
| A: mechanical baseline | 15, 21-23 |
| B: worker foundation | 8-10, 17-22 |
| C: `epic_refine` | 11-12, 15-16, 22-23 |
| D: `audit_epic` | 11, 14-15, 22-23 |
| E: `implement` | 11, 13, 15, 22-23 |
| F: consolidation | 19-21, 25 |

Do not paste this document into a command, worker prompt, or job packet. Return
to the relevant section when an implementation decision requires it.

## 2. Baseline Warning

At the time this brief was written, `main` was at `02b9e99` and the worktree had
pending changes in:

- `README.md`
- `scripts/validate-pr-checks.sh`
- `src_claude/commands/implement.md`
- `src_codex/commands/implement.md`
- `src_shared/commands/audit_epic.md`
- `src_shared/commands/epic_refine.md`
- `src_shared/scripts/scope-reviewer-claude-pexpect.py`
- `tests/unit/test_scope_reviewer_claude_pexpect.py`
- `tests/unit/test_validate_refinement.py`

Those changes automate the refinement handoff/dependency baseline and harden
Claude reviewer launch preflight. They are prerequisites, not disposable
experiments.

Before beginning this refactor:

1. inspect current Git status and HEAD again;
2. confirm the prerequisite changes were committed or deliberately included;
3. do not overwrite or revert user changes;
4. rerun `./scripts/validate-pr-checks.sh` on the actual starting baseline.

Do not implement this refactor in a dirty tree whose ownership cannot be
explained.

## 3. Current Weaknesses

### 3.1 Monolithic active prompts

Current command sizes are approximately:

- `src_shared/commands/epic_refine.md`: 624 lines;
- `src_shared/commands/audit_epic.md`: 358 lines;
- `src_codex/commands/implement.md`: 680 lines.

The main session receives workflow rules, examples, schemas, shell launchers,
reviewer topology, remediation logic, and completion output at once. This makes
the orchestrating context carry both user decisions and noisy execution detail.

### 3.2 The author session performs too many roles

The current main session may act as:

- user interlocutor;
- product owner;
- architect;
- repository explorer;
- artifact author;
- implementation coordinator;
- developer;
- test runner;
- review launcher;
- finding merger;
- remediation author;
- completion reporter.

Independent reviewers are fresh, but the author and remediator remain in the
long-running session. Context compaction does not eliminate accumulated bias,
stale goals, or repeated instruction content.

### 3.3 Important controls remain prose-only

Examples include:

- inspect the complete defect pattern, not just reviewer-named files;
- execute exact proof commands before presenting them as viable;
- update all sibling contract and traceability surfaces;
- run only one full review;
- do not create new issues while correcting old ones.

The SAG-112 artifacts demonstrate that an agent can violate these expectations
while producing superficially valid bookkeeping.

### 3.4 Refinement review accounting trusts self-report

`validate-refinement.py` currently validates the declared
`full_review_count`/`targeted_verification_count`, but does not derive the count
from all `reviews/refine-v3-*/review-packet.yaml` artifacts.

By contrast, `audit-artifacts.py::_existing_attempts` already counts durable
`audit-attempt.yaml` artifacts by cycle and mode. Refinement should use the same
principle.

### 3.5 More reasoning effort is not an enforcement mechanism

Increasing model effort may improve difficult judgment, but it does not make
procedural boundaries deterministic. The refactor must not depend on a model
remembering or voluntarily applying every instruction.

### 3.6 Historical instructions may reduce current-model quality

Scope's commands accumulated detailed instructions while compensating for
earlier model weaknesses. Those instructions are not automatically assets for
newer models. A capable model can perform worse when it must reconcile a large,
prescriptive checklist with repository evidence, especially when rules overlap,
encode obsolete workarounds, or dictate reasoning steps that the model could
handle more directly.

Do not assume every current instruction must survive somewhere in the new
architecture. Splitting the same prose between an orchestrator and workers would
preserve this weakness while adding orchestration complexity.

Classify existing instructions before migrating them:

| Class | Treatment |
|---|---|
| Authorization, safety, user approval, or write boundary | Keep once in the controller or worker boundary, and enforce mechanically where possible. |
| Artifact/schema invariant | Move to schema or validator; remove explanatory duplicates from prompts. |
| Workflow transition or retry budget | Move to orchestrator logic and durable-state validation. |
| Domain context required for the task | Reference the authoritative artifact; load it only for the relevant worker. |
| Model workaround supported by a current regression | Keep the smallest instruction that fixes the measured failure. |
| Checklist, example, preferred reasoning sequence, or historical warning without current evidence | Remove initially; restore only if an evaluation demonstrates material regression. |

The default migration decision for nonessential prose is deletion, not
relocation.

## 4. Goals

### 4.1 User experience

The user talks only to the public command's orchestrator.

The user can, at any time:

- ask what is happening and why;
- ask questions about current decisions or evidence;
- raise a concern;
- report an issue;
- request a change;
- approve, reject, or refine a proposed decision;
- stop the workflow.

The orchestrator answers or routes the request without directing the user to a
worker.

### 4.2 Context isolation

Workers receive a fresh, bounded job. They do not inherit the entire user
conversation. They read durable artifacts and only the relevant role/phase
instructions.

### 4.3 Deterministic workflow state

Existing epic and audit artifacts remain the durable state. The orchestrator
must infer the next incomplete phase through validators and artifact status,
not through memory or a second permanent workflow ledger.

### 4.4 Controlled execution

Only one write-capable worker may run at a time. Independent read-only reviewer
assignments remain the only intentional concurrency over the same checkout.

### 4.5 Cross-platform behavior

Claude and Codex installations must expose behaviorally equivalent workflows.
Shared behavior belongs under `src_shared/`; platform-specific launch syntax
belongs under the platform source only when unavoidable.

### 4.6 Evidence-based instruction set

Start each orchestrator and worker role from the smallest instruction set that
defines its authority, inputs, output contract, and stopping condition. Measure
current-model performance with that minimal prompt before adding procedural
guidance. Add an instruction only when a repeatable evaluation shows that it
prevents a material failure and a deterministic control cannot replace it.

Prompt quality is determined by task outcomes, not by how completely the new
files reproduce the old prose.

## 5. Non-Goals

Do not add:

- a general-purpose multi-agent framework;
- a queue service, daemon, database, or server;
- a new user-facing command for each worker;
- a new durable orchestration artifact beside existing epic/audit state;
- parallel code-writing workers;
- workers that recursively spawn workers;
- an additional semantic reviewer before audit;
- legacy compatibility with the monolithic command path;
- a feature flag preserving both old and new execution models;
- automatic commits beyond Scope's already fixed and authorized internal labels;
- worker-authored recommendations for the workflow's next action.

The user previously stated that legacy support is not needed. Replace the old
path cleanly after tests cover the new path.

## 6. Architectural Decision

Use one conversational orchestrator plus fresh Scope-managed worker processes.

Do not make correctness depend on native subagent model inheritance. Current
Codex releases support native subagents, but recent GPT-5.6 multi-agent routing
has had model/role inheritance defects. Scope already uses controlled fresh CLI
processes for independent reviewers. Extend that deterministic pattern to
workers.

The process is still a subagent in the architectural sense:

- it has isolated context;
- it receives a bounded role and job;
- it performs tool work independently;
- it returns a structured result to the orchestrator;
- it never owns the user conversation.

### 6.1 High-level flow

```text
User
  |
  v
Conversational orchestrator
  |  owns decisions, gates, status, questions, and worker lifecycle
  |
  +--> fresh bounded worker (one writer)
  |      reads durable artifacts
  |      performs one phase/story/remediation batch
  |      returns structured result
  |
  +--> deterministic validators
  |
  +--> existing independent reviewers (parallel, read-only)
  |
  v
User-visible decision/status
```

### 6.2 Why not one worker per command

One worker running all of `epic_refine` or `implement` would accumulate the
same repository noise and correction history as the current main session. Use
fresh workers at meaningful boundaries:

- one refinement phase;
- one implementation story;
- one review-finding correction batch;
- one audit synthesis pass.

Do not create a worker for every shell command. The boundary should remove
context pollution without adding coordination overhead.

## 7. Responsibility Contract

### 7.1 Orchestrator responsibilities

The orchestrator may:

- resolve the active Scope installation and epic/worktree;
- read concise durable status artifacts and validator output;
- maintain a short phase checklist;
- create bounded worker job packets;
- launch, poll, terminate, and relaunch workers;
- launch existing independent reviewers;
- run deterministic validators and fixed orchestration scripts;
- explain evidence, questions, concerns, and tradeoffs to the user;
- ask the user only for product, policy, scope, security, destructive,
  irreversible, or material-boundary decisions;
- persist confirmed decisions in the canonical artifact through a worker;
- perform fixed Scope-internal Git operations already authorized by the public
  command;
- report completion or a concrete blocker.

The orchestrator must not:

- broadly inspect implementation source itself;
- author or repair epic artifacts itself;
- implement or remediate production code;
- perform semantic review;
- silently answer a worker's user question;
- merge reviewer findings through free-form judgment in the root context;
- run extra reviews because a worker correction was incomplete;
- infer the next step from worker prose.

### 7.2 Worker responsibilities

A worker must:

- execute exactly one declared role and phase;
- read repository instructions and only the relevant Scope worker prompt;
- read referenced artifacts from the active checkout/worktree;
- obey explicit read and write scopes;
- inspect enough source to complete its bounded task;
- run required focused validation;
- return a schema-valid result;
- stop with `user_input` when a real user decision is required;
- stop with `blocked` when the outcome cannot be reached within the job;
- report every path it changed;
- report exact validation commands and counts;
- leave decisions outside its authority unresolved.

A worker must not:

- communicate with the user;
- create commits;
- launch Scope commands;
- launch reviewers or nested workers;
- continue into the next phase/story;
- broaden scope because related work looks useful;
- modify paths outside its write contract without reporting and justifying them;
- return a `next_action` or workflow recommendation;
- declare completion from intent alone.

### 7.3 Reviewer responsibilities

Existing reviewer prompts remain independent and read-only. Reviewers:

- receive review packets, not the user's full conversation;
- may identify evidence-backed findings in their assigned mission;
- do not edit implementation or canonical artifacts;
- do not invoke other reviewers;
- do not become the remediation worker.

An audit-synthesis worker is not an additional reviewer. It only normalizes,
deduplicates, and maps existing reviewer/deterministic findings. Its prompt must
forbid creating new semantic findings not present in an input source.

### 7.4 Mechanical authorship attribution

The repository cannot completely prevent the conversational model from calling
an edit tool without platform-specific host hooks. Do not claim a security
boundary that Scope cannot provide consistently across Claude and Codex.

Instead, make direct orchestrator authoring unable to satisfy a phase gate:

1. At command start, record a baseline manifest of existing Git status, changed
   paths, and content hashes for already-dirty files.
2. Before each write job, record the current manifest and acquire the runner's
   exclusive write-worker lock.
3. The runner records the worker process identity, job ID, start/end manifests,
   and schema-valid result.
4. Phase validation compares all post-baseline changes with valid worker
   receipts and their declared `changed_paths`.
5. Any unattributed change stops the workflow. The orchestrator asks whether it
   came from the user or another process; it never silently assigns ownership.

Record each detection in the command's `run.yaml` under one field:

```yaml
unattributed_change_incidents:
  - detected_at: "2026-08-02T15:00:00Z"
    job_id: "SAG-112-epic-refine-design-001"
    paths: ["docs/epics/.../design.md"]
    resolution: "orchestrator | user | other_process | unresolved"
```

The list length is the incident count; `resolution` distinguishes actual
orchestrator drift from legitimate concurrent user work. Do not add a second
counter that can disagree with the list.

This is compliance enforcement, not protection from a malicious parent
process. Do not add signatures, hidden tokens, or other mechanisms that pretend
the orchestrator cannot forge data it can read and write.

Do not install a global or project-wide `PreToolUse` edit-denial hook in the
initial refactor. Such a hook is platform-specific, can affect unrelated user
work, and needs a reliable way to distinguish the conversational orchestrator
from a write worker. Reconsider a narrowly scoped hook only as a separate
improvement if retained run records show recurring incidents resolved as
`orchestrator`, not from anecdotal reports alone.

## 8. Shared Worker Protocol

### 8.1 Ephemeral runtime location

Use existing ignored runtime storage:

```text
tmp_debug/scope-runs/
  locks/{working-root-hash}.lock  # exclusive runner-owned write-worker lock
  {epic-id}/{command}/
    run.yaml                     # command baseline and current job identity
    jobs/{job-id}/
      job.yaml
      rendered-prompt.md
      result.json
      metadata.yaml
      before-manifest.json
      after-manifest.json
      stdout.log
      stderr.log
```

These files are operational evidence and debugging material. They are not Git
artifacts and must not be referenced as permanent proof after the workflow
finishes.

`run.yaml` is an ephemeral recovery record, not a second canonical workflow
ledger. Validators still derive semantic phase state from existing epic/audit
artifacts. The run record contains only process/job identity, baseline
attribution data, incident observations, and lifecycle status.

Resolve the runtime directory exclusively from the job packet's canonical
`repository_root`:

```text
runtime_root = {repository_root}/tmp_debug/scope-runs
```

`working_root` is the checkout or epic worktree where the worker reads, writes,
and runs validation. It selects the lock key and manifest scope, but it never
selects the location of run records. A runner launched with its current
directory inside a worktree must still read and write lifecycle state under
`repository_root`. Do not rediscover the runtime root from process CWD during
`run`, `status`, or `recover`.

Canonical documents, implementation evidence, review packets, reviewer output,
and audit findings remain in their existing durable locations.

### 8.2 Job packet

Add one versioned shared job schema. Recommended shape:

```yaml
schema_version: 1
job_id: "SAG-112-epic-refine-design-001"
command: "epic_refine | implement | audit_epic"
role: "refinement | implementation | audit | diagnostic"
phase: "profile | product | design | handoff | correction | finalize_candidate | materialize_handoff | story | epic_verify | audit_remediation | debugging | delivery_summary | merge_findings | investigate"
epic_id: "SAG-112"
repository_root: "/absolute/runtime/path"
working_root: "/absolute/runtime/path-or-worktree"
scope_root: "/absolute/installed-scope-root"
read_scope:
  - "repository-relative path or directory"
write_scope:
  - "repository-relative canonical path or boundary"
artifacts:
  - kind: "design"
    path: "docs/epics/.../design.md"
confirmed_decisions:
  - id: "PDR-001"
    source: "docs/epics/.../design.md#PDR-001"
constraints:
  - "No Signal-v1 migration"
required_validations:
  - command: "exact command"
    purpose: "gate it proves"
stop_conditions:
  - "Product behavior is ambiguous"
  - "Required external input is unavailable"
result_path: "/absolute/tmp_debug/.../result.json"
```

Rules:

- Absolute paths are allowed only in ephemeral job packets.
- `repository_root` is the canonical project/control root selected by the
  orchestrator before worktree execution; `working_root` may equal it or name a
  linked epic worktree.
- Both roots must be normalized and validated once when the job is accepted.
- Do not copy full artifact contents into the packet.
- `confirmed_decisions` must cite durable sources, not conversation memory.
- `write_scope` is exact for refinement and audit. Implementation may permit
  developer-discovered paths only through the existing boundary classification
  and post-run gate.
- The packet must not tell the worker what workflow phase comes next.

### 8.3 Worker result

Add one JSON Schema with `additionalProperties: false`.

Required shape:

```json
{
  "schema_version": 1,
  "job_id": "SAG-112-epic-refine-design-001",
  "status": "completed",
  "phase": "design",
  "summary": "Completed bounded design work.",
  "changed_paths": [
    {
      "path": "docs/epics/.../design.md",
      "classification": "authorized",
      "reason": "Updated approved architecture contract"
    }
  ],
  "validation_results": [
    {
      "command": "python3 ... --phase architecture",
      "exit_code": 0,
      "passed": 1,
      "failed": 0,
      "errors": 0,
      "skipped": 0,
      "summary": "Architecture validation passed"
    }
  ],
  "questions": [],
  "question_discovery": null,
  "concerns": [],
  "error": null
}
```

Allowed statuses:

- `completed`: bounded job and required validation succeeded;
- `user_input`: worker stopped before making an unauthorized decision;
- `blocked`: required outcome cannot be reached with current inputs;
- `failed`: execution failed and evidence is included.

Question shape:

```json
{
  "id": "Q-001",
  "question": "Which behavior is authoritative?",
  "why_user_decision_required": "Both behaviors are externally observable.",
  "options": [
    {"id": "A", "description": "Preserve current API behavior", "tradeoff": "..."},
    {"id": "B", "description": "Adopt the new contract", "tradeoff": "..."}
  ],
  "evidence": ["src/path.py#symbol"]
}
```

The worker does not include a recommended option. The orchestrator evaluates
the evidence, explains a recommendation to the user when appropriate, and
records only the user's confirmed decision.

For `status: user_input`, require a question-discovery record:

```json
{
  "scope_examined": ["approved product contract", "all declared acceptance rows"],
  "all_current_blockers_reported": true,
  "further_discovery_blocked_by": []
}
```

The worker must batch all blocking questions discoverable from the scope it has
already examined. A single question is valid when it is genuinely the only
current blocker or when it prevents further inspection; in the latter case,
`further_discovery_blocked_by` names it. Do not require the worker to predict
questions hidden behind an unresolved decision.

Concern shape:

```json
{
  "id": "C-001",
  "severity": "blocking | major | minor",
  "category": "scope | architecture | implementation | validation | environment",
  "description": "Concrete concern",
  "evidence": ["repo-relative path#anchor"]
}
```

Explicitly reject a `next_action` property.

### 8.4 Result validation

Add `src_shared/scripts/validate-worker-result.py` or equivalent logic in the
worker runner. It must validate:

- schema and job ID match;
- status-specific required fields;
- changed paths are repository-relative and do not escape the working root;
- every validation command has an exit code and counts;
- `completed` has no unresolved questions or blocking concerns;
- `user_input` has at least one question and a valid question-discovery record;
- the question-discovery record attests that all currently discoverable
  blockers were batched;
- no `next_action` field exists;
- no absolute durable artifact path is returned.

Do not let the orchestrator interpret malformed free-form output.

## 9. Worker Roles

Use three primary shared worker prompts. Do not create one prompt per minor
phase.

### 9.1 `refinement-worker`

Supported phases:

- `profile`
- `product`
- `design`
- `handoff`
- `correction`
- `finalize`

Responsibilities:

- repository grounding;
- product/architecture artifact authoring;
- native contract authoring and validation;
- story boundary/proof planning;
- related-surface correction sweeps;
- final refinement summary artifact.

The worker must not launch reviewers or ask the user directly.

### 9.2 `implementation-worker`

Replace command reliance on the current long `developer.md` body with a slimmer
worker prompt that references existing governance files instead of repeating
them.

Supported phases:

- `story`
- `epic_verify`
- `audit_remediation`
- `debugging`

Retain existing production-code, test-integrity, evidence, and unplanned-file
requirements. Preserve the current Codex default `gpt-5.6-terra` with max
reasoning unless representative evaluation justifies a change. Preserve the
Claude implementation model behavior unless deliberately changed and tested.

### 9.3 `audit-worker`

Supported phase:

- `merge_findings`
- optionally `prepare_packet` only if preparation cannot remain mechanical.

Responsibilities:

- consume deterministic and reviewer outputs;
- normalize finding schema;
- deduplicate only identical root cause/surface/closure requirements;
- preserve evidence-backed minority findings;
- produce audit decision artifacts.

It is read-only with respect to implementation and approved epic contracts.
It must not add a finding based solely on its own repository interpretation.

## 10. Worker Launching

### 10.1 Shared runner

Add a focused shared Python entry point, tentatively:

```text
src_shared/scripts/scope-worker.py
```

Recommended CLI:

```text
scope-worker.py preflight --provider codex|claude

scope-worker.py status --run /absolute/path/run.yaml

scope-worker.py recover --run /absolute/path/run.yaml

scope-worker.py run \
  --provider codex|claude \
  --role refinement|implementation|audit \
  --job /absolute/path/job.yaml \
  --result /absolute/path/result.json \
  --metadata /absolute/path/metadata.yaml \
  --cwd /absolute/path \
  --access read-only|workspace-write
```

The runner should:

1. load and validate the job packet;
2. load the role prompt from the active Scope installation;
3. render a short instruction that references the job file and result schema;
4. record the exact provider/model/effort/command;
5. atomically acquire the working root's write-worker lock when access is
   `workspace-write`;
6. record the pre-job manifest and worker process identity;
7. run the provider process while recording lifecycle events;
8. validate the structured result and post-job manifest;
9. record toolchain, duration, resource-usage, and termination metadata;
10. release the lock on every clean exit;
11. exit non-zero for malformed output or failed infrastructure.

The lock must be cross-platform and owned by the runner process, not merely a
prose convention. Key it by the canonical working-root path so two Scope write
workers cannot modify the same checkout, while independent epic worktrees are
not unnecessarily serialized. A stale lock is never silently deleted; `status`
and `recover` inspect its process identity and run metadata first.

Use a maintained cross-platform file-locking library instead of hand-rolling
separate `fcntl` and Windows implementations. Evaluate `filelock` first and add
an explicit compatible dependency range if selected. The runner remains the
supervisor holding the lock for the worker's lifetime. Before acquiring a free
lock, it must also reject an active provider process recorded for the same
working root, covering the case where the supervisor died but its child did
not.

Do not implement generic retries. Infrastructure failure before semantic work
may be corrected and rerun in the same job directory. Semantic failure requires
orchestrator judgment.

### 10.2 Codex backend

Use controlled non-interactive execution:

```bash
codex exec \
  --ephemeral \
  --ignore-user-config \
  --cd "$WORKING_ROOT" \
  --model "$MODEL" \
  -c model_reasoning_effort="\"$EFFORT\"" \
  --sandbox "$SANDBOX" \
  --output-schema "$RESULT_SCHEMA" \
  --output-last-message "$RESULT_PATH" \
  - < "$RENDERED_PROMPT"
```

Use:

- `read-only` for audit synthesis that only writes the result outside the
  repository through the runner's controlled path;
- `workspace-write` for refinement and implementation workers;
- never `danger-full-access` as a default worker mode.

Pin model and effort through worker policy rather than inheriting the
orchestrator model. This allows Sol to remain the conversational root while a
bounded Terra worker performs repository work.

### 10.3 Claude backend

Do not assume that the existing PTY reviewer transport is the correct worker
transport. It was built for short, read-only reviews, depends on `pexpect`, and
is not a Windows solution.

Delivery B must begin with a time-boxed headless transport spike using the
installed Claude CLI's non-interactive capabilities. The spike must verify:

- subscription-backed authentication works without an interactive terminal;
- structured output is enforced by the result JSON Schema;
- the selected write tools and required validation commands run without
  approval prompts;
- denied tools fail rather than opening an interactive question;
- project instructions and the explicit worker prompt are loaded exactly once;
- model, effort, MCP isolation, session persistence, and browser integration are
  explicitly controlled;
- cancellation, timeout, exit status, logs, and partial repository changes are
  observable by the runner;
- the same subprocess design works on Windows when Claude CLI is installed.

The candidate primary path is `claude --print` with structured output,
no-session persistence, explicit model/effort, safe MCP/browser settings, and a
role-specific tool/permission allowlist. Determine and record the exact flags
from the installed CLI during the spike. Do not combine unrestricted shell
access with permission bypass merely to suppress prompts. The committed worker
policy and launcher tests must make the final permission model explicit.

Keep `scope-reviewer-claude-pexpect.py` unchanged during the spike so existing
reviews remain stable. If headless execution passes, implement the worker as a
normal subprocess backend and reuse only transport-independent preflight,
metadata, timeout, and validation helpers.

Use PTY as a worker fallback only if the spike demonstrates a concrete
subscription or tool-execution limitation and records it. In that case:

- reuse the existing PTY implementation rather than creating a second one;
- add write-worker permission and partial-change tests;
- declare Claude write workers POSIX-only;
- keep Windows support for Codex workers and existing installer assets;
- document the limitation instead of claiming full runtime parity.

Post-dogfood resolution: the authenticated headless CLI passed. Claude workers
and reviewers now run `claude --print` as normal subprocesses with stdin/stdout
transport and explicit read-only reviewer permissions. The PTY wrapper and
`pexpect` dependency were removed rather than retained as a fallback.

### 10.4 Worker policy

Store production defaults in YAML, not as new Python hardcodes. Runtime and
trusted-operation controls are shared, while model/effort routing is
provider-local so a worker installation cannot cross providers:

```text
src_shared/config/worker-runtime-policy.yaml
src_codex/config/worker-policy.yaml
src_claude/config/worker-policy.yaml
```

Each provider policy defines complete phase maps under `workers` and
`workers_on_budget`. The orchestrator selects one profile, persists it in the
run record, and may change it only between jobs through the runner. Workers do
not receive or choose routing policy. Codex worker models must remain in the
GPT-5.6 family; Claude worker models must remain Claude aliases. Exact mappings
live in the provider files above and are validated as complete phase matrices.

Shared timeout numbers are initial conservative ceilings, not measured truths.
Validate them against representative work and keep them configurable. A hard
wall-clock timeout is mandatory. A provider cost/token ceiling should also be
set when that provider exposes a reliable non-interactive limit; do not invent a
fake common token limit when the CLI cannot enforce one. Record actual usage
whenever the provider reports it.

Independent reviewer routing is separately authorized and remains shared in
`reviewer-policy.yaml`. It has independent `default`/`budget` profiles and
`standard`/`expanded` sets; only reviewers may cross providers.

## 11. Conversational Orchestrator Protocol

### 11.1 Normal progress

The orchestrator:

1. identifies the first incomplete deterministic phase;
2. shows the user only a concise milestone update;
3. creates and launches one bounded worker;
4. waits or polls without importing raw logs into the conversation;
5. validates worker result and repository changes;
6. runs the phase's deterministic gate;
7. asks for user approval only when the public workflow requires it;
8. launches the next bounded worker only after the gate passes.

### 11.2 User asks a question

The orchestrator answers from:

- confirmed durable artifacts;
- concise worker result;
- deterministic validator output.

If answering requires broad repository investigation, launch a read-only
diagnostic worker. Do not make the orchestrator perform the investigation.

### 11.3 User raises a concern

Classify the concern:

- informational: explain and continue;
- affects pending phase but not active work: include it in the next job;
- affects active worker assumptions: terminate the worker at a safe boundary,
  persist no unapproved decision, update the job, and launch a fresh worker;
- material product/architecture change: return to the appropriate user gate and
  invalidate downstream artifacts through existing validators.

Do not steer a stale worker through several conversational corrections. Restart
with a fresh job after a material change.

### 11.4 User requests a change

The orchestrator determines ownership:

- refinement contract change: refinement worker;
- implementation change inside approved boundary: implementation worker;
- change outside approved boundary: return to refinement/user approval;
- audit finding remediation: implementation remediation worker;
- destructive/external action: explicit user confirmation first.

The orchestrator explains impact and affected gates, then launches a fresh
worker. It does not edit files itself.

### 11.5 Worker asks for user input

The worker returns `status: user_input` and stops.

Before stopping, it must inspect all surfaces that do not depend on the missing
decision and batch every currently discoverable blocking question. It must not
stop after the first ambiguity merely because one valid question was found. If
that ambiguity prevents further discovery, the result says so explicitly.

The orchestrator:

1. validates that the question truly requires the user;
2. explains evidence, options, and tradeoffs;
3. makes a recommendation only when evidence supports one;
4. asks the user;
5. persists the confirmed decision through a fresh worker;
6. does not resume execution from an unrecorded chat-only answer.

### 11.6 User stops or redirects

Terminate the active worker, preserve runtime logs, report which durable files
changed, and do not launch another worker until the user resumes.

## 12. `epic_refine` Conversion

### 12.1 Public orchestrator

Replace the monolithic command body with a concise controller containing:

- outcome contract;
- authorization/stopping contract;
- phase order and user gates;
- worker protocol reference;
- validator commands;
- reviewer topology reference;
- completion conditions.

Move YAML examples, detailed design prompts, proof schemas, reviewer launch
details, and correction procedure into worker prompts, templates, policy, and
scripts.

### 12.2 Phase mapping

#### Initialize and profile

Orchestrator actions:

- locate epic and active installation;
- run Python/Claude/Codex worker preflight;
- run current profile validator to determine missing state;
- launch `refinement-worker:profile` for repository grounding and proposed
  profile;
- validate profile;
- present Gate 0 to the user.

Worker output may contain user questions, but cannot approve the profile.

#### Product contract

Launch `refinement-worker:product` with:

- confirmed profile;
- current details/acceptance/design decision sections;
- relevant product evidence;
- exact authorized write paths.

Run product validation. Orchestrator presents Gate 1.

#### Evidence-backed design

Launch `refinement-worker:design` with:

- approved product contract;
- selected capabilities/challenges;
- source/native-contract read scope;
- exact design/native-contract write scope;
- required validation commands.

Worker performs repository inspection and native validation. Run architecture
validation. Orchestrator presents Gate 2.

#### Implementation handoff

Launch `refinement-worker:handoff` to create the fewest story plans, assign
owners, define proof obligations, and reconcile generated traceability.

Before independent review, require the proof-preflight gate described in
Section 15. Do not launch reviewers from a merely schema-valid plan.

#### Independent review

The orchestrator launches existing risk-required assignments concurrently.
These remain fresh provider processes and do not become general workers.

#### Finding synthesis

Refinement finding synthesis can remain mechanical if the validator/script can
normalize reviewer output. If semantic normalization is still necessary, use a
read-only `audit-worker`-style synthesis job that may only preserve or
deduplicate source findings.

#### Correction

Launch one fresh `refinement-worker:correction` for the complete current finding
batch. The job must include:

- all open fingerprints;
- affected acceptance/manifest IDs;
- source reviewer evidence;
- closure conditions;
- required related-surface and proof checks.

Do not launch the targeted verification until correction completeness validates.

#### Targeted verification

Run only the provider/mission assignments attached to the corrected findings.
If they remain open, permit another targeted verification within policy after a
new author-side correction gate. Do not convert incomplete corrections into a
new full review.

#### Final handoff

Launch `refinement-worker:finalize` for `refinement-review.md` only after all
deterministic and independent gates are closed. Orchestrator presents Gate 3.

### 12.3 Full-review policy

Enforce one full review for the normal refinement cycle.

An additional full review is not allowed merely because:

- the author missed sibling surfaces;
- the first correction was incomplete;
- targeted verification found a closure gap;
- the targeted allowance was consumed.

A later full review requires a documented material product/architecture
boundary change and explicit user authorization. Its durable packet must state
the changed boundary and authorization. Counts must remain honest.

Do not change the medium-risk targeted-verification allowance as part of this
refactor. That is an independent review-policy decision and would make it harder
to determine whether worker isolation and correction gates improved efficiency.

## 13. `implement` Conversion

### 13.1 Public orchestrator

The implementation orchestrator owns:

- handoff validation;
- authorized refinement checkpoint commit;
- worktree creation/resume;
- exact dependency-baseline merge under existing conditions;
- story graph and order;
- environment preflight;
- one worker per story;
- post-story mechanical gates;
- epic-wide verification worker;
- nested audit execution;
- remediation sequencing;
- final evidence/completion reporting.

It does not implement code.

### 13.2 Story execution

For each story in topological order:

1. confirm dependencies are complete;
2. create a job from the story's boundary plan and current evidence;
3. capture pre-worker Git status without disturbing existing user changes;
4. launch one `implementation-worker:story` in the epic worktree;
5. validate result schema;
6. compute worker-introduced changed paths;
7. run boundary/forbidden-change gate;
8. run exact story proof obligations;
9. validate transactional evidence update;
10. continue only if story status is honestly closed.

Do not run multiple story writers concurrently in one worktree.

### 13.3 Worker-discovered files

Preserve the existing distinction:

- candidate files are advisory;
- contracts, touchpoints, forbidden changes, and proof obligations are binding;
- discovered files are allowed only with source evidence and impact.

The orchestrator must compare the result's changed paths against the actual Git
diff. Missing or unexplained paths fail the story gate.

### 13.4 Epic-wide verification

After all stories, launch one fresh `implementation-worker:epic_verify` with no
new feature authority. It may:

- run cross-story and full required validations;
- inspect wiring and value delivery;
- correct only defects clearly inside approved story boundaries;
- update implementation evidence.

It may not broaden product or architecture scope.

This is author-side verification, not an additional independent reviewer.

### 13.5 Nested audit

`implement` currently invokes the real Scope audit. Under the new design:

- the implementation orchestrator remains the user's only conversational root;
- it calls the audit execution components internally;
- audit questions/findings are surfaced through the implementation
  orchestrator;
- the user is not asked to switch to another command/thread;
- audit artifacts remain identical to a direct `audit_epic` run.

Do not create a second conversational orchestrator.

### 13.6 Audit remediation

For a failed audit:

1. group current remediable findings by coupled root cause;
2. launch one fresh `implementation-worker:audit_remediation` per bounded batch;
3. require pattern-wide related-surface checks;
4. run the same boundary/proof/evidence gates;
5. run only the policy-authorized targeted audit verification.

No remediation worker may change acceptance criteria or architecture. Such a
finding returns to the user/refinement gate.

## 14. `audit_epic` Conversion

### 14.1 Public orchestrator

The direct audit orchestrator owns:

- handoff and toolchain preflight;
- attempt preparation;
- deterministic evidence gates;
- concurrent provider launch;
- synthesis worker launch;
- final audit validation;
- user explanation and remediation discussion.

It never edits implementation.

### 14.2 Mechanical preparation

Keep `audit-artifacts.py` responsible for:

- counting attempts from durable artifacts;
- enforcing full/targeted budgets;
- selecting acceptance scope and assignments;
- constructing deterministic matrices and review packets;
- validating implementation evidence provenance.

Do not move working deterministic logic into a model worker.

### 14.3 Independent review

Preserve existing three-provider/risk topology and concurrency. Reviewers remain
fresh, read-only processes with distinct output/metadata paths.

### 14.4 Finding merge

Launch `audit-worker:merge_findings` with:

- deterministic findings;
- provider outputs;
- existing audit findings ledger;
- attempt scope and covered acceptance IDs;
- strict deduplication rules.

The worker may not inspect the repository to invent additional semantic
findings. It maps evidence already produced by assigned reviewers and
deterministic gates.

Validate merged artifacts with `audit-artifacts.py` before presenting the audit
decision.

### 14.5 User requests changes during audit

The orchestrator explains ownership:

- implementation defect inside approved boundary: eligible for implementation
  remediation worker after explicit request or when audit is nested in
  `implement`;
- product/architecture contract defect: return to refinement;
- unrelated enhancement: outside audit scope;
- question about evidence: answer from audit artifacts or launch a read-only
  diagnostic worker.

Direct audit remains read-only until the user explicitly requests remediation.

## 15. Mechanical Reliability Improvements

### 15.1 Refinement review counts

Extend `validate-refinement.py` to enumerate every valid
`reviews/refine-v3-*/review-packet.yaml`.

Each packet must contain:

```yaml
review_kind: full | targeted
review_id: refine-v3-NNN
assignments: [...]
targeted_fingerprints: []  # required for targeted
material_boundary_change: null | description
authorization: null | durable user-authorization description
```

Validator requirements:

- derived full count equals declared full count;
- derived targeted count equals declared targeted count;
- every packet has expected assignment metadata/output files;
- targeted packets list fingerprints and contain no unrelated broad focus;
- extra full packets require material boundary change plus authorization;
- correction-only changes cannot justify a full packet;
- findings outputs do not discard prior durable packet evidence;
- metrics use derived counts, not self-authored counters.

Add a SAG-112 regression fixture where three full packets plus declared count
one must fail.

### 15.2 Proof preflight before refinement review

Every proof obligation must classify its preimplementation state:

```yaml
preflight:
  status: passed | implementation_created | baseline_blocked
  command: "exact command"
  exit_code: 0
  result: "27 passed, 2 failed"
  blocker: "required only for baseline_blocked"
  substitute: "required when the planned broad proof is baseline_blocked"
```

Rules:

- Existing runnable commands must be executed exactly as written.
- `implementation_created` is allowed only when the command references a test or
  executable explicitly owned for creation by the same story.
- `baseline_blocked` must record exact failure/error/skip counts and a runnable
  substitute or an honest external blocker.
- Adding a module to the proof surface requires rerunning and recounting it.
- Review cannot start while any proof has an unclassified preflight state.

Use a small execution helper if needed, but do not let the generic validator
silently execute arbitrary project commands. The workflow explicitly invokes
the helper; the validator verifies its structured evidence.

### 15.3 Correction completeness

Replace free-form-only correction claims with structured checks in the existing
findings artifact. Do not add another permanent file.

Recommended fields per corrected finding:

```yaml
correction_checks:
  affected_artifacts:
    - docs/epics/.../design.md
  related_surface_checks:
    - method: command | inspection
      command: "rg ..."
      inspected: 17
      classified: 17
      unclassified: 0
      result: "All active matches classified"
  closure_checks:
    - command: "pytest ..."
      exit_code: 0
      passed: 23
      failed: 0
      errors: 0
      skipped: 0
  reconciliation:
    command: "python ... --phase reconcile"
    exit_code: 0
```

Validator requirements:

- `corrected` requires correction checks;
- every changed canonical artifact is listed;
- related-surface check has zero unclassified matches;
- executable closure commands include counts;
- reconciliation passed after the correction;
- targeted verification packet fingerprints match corrected findings;
- `verified` still requires fresh independent evidence.

This does not prove the model found every semantic concept, but it prevents the
specific pattern of correcting only named files without recording a complete
sweep.

### 15.4 Changed-path boundary gate

Before launching a write worker, record current status for relevant paths and
the whole worktree. After completion:

- compute paths introduced or modified by the worker;
- compare them with reported `changed_paths`;
- classify each against exact write scope, story candidate/touchpoint, or
  developer-discovered evidence;
- fail on unreported or unjustified paths;
- leave pre-existing user changes untouched;
- never auto-revert an unauthorized path when ownership is ambiguous.

### 15.5 No new semantic review

Do not add a pre-audit semantic reviewer. Worker self-check and mechanical gates
are author-side execution controls, not another provider review.

## 16. Prompt Slimming

Prompt slimming is an instruction ablation exercise, not a document-shuffling
exercise. Do not create worker prompts by copying phase sections out of the
current commands. Inventory each instruction, classify it using Section 3.6,
and rebuild each role from a minimal contract.

### 16.1 Public command target

Each public command should contain only:

- outcome;
- compact authorization boundaries;
- phase/state transitions;
- user gates;
- worker invocation contract;
- deterministic validation entry points;
- completion conditions.

Remove from the active orchestrator prompt:

- large YAML examples already represented by templates/schema;
- duplicated production-quality checklists;
- inline provider launcher details now owned by scripts;
- repeated statements of the same approval rule;
- detailed phase authoring instructions now owned by worker prompts;
- compaction recovery instructions made unnecessary by durable state discovery.

Do not enforce a brittle line-count test, but measure prompt bytes before and
after. The implementation should target at least a 50 percent reduction in the
combined active public command text while preserving behavior through workers
and validators.

### 16.2 Worker prompt target

Each worker prompt should:

- define one role;
- define only the phase being run, or list supported phases only when one shared
  prompt materially reduces duplication without creating ambiguity;
- reference only the governance/templates needed for this job;
- state write/decision boundaries once;
- require structured output;
- avoid user-facing explanations and workflow narration;
- include concrete tool examples only where they correct a measured failure.

Do not include generic advice such as how to reason, inspect code, write good
tests, or be thorough. Modern models already possess those capabilities, and
generic process prose competes with task-specific evidence. Do not retain an
instruction merely because an older model once needed it.

For every instruction retained from the old command, record one of:

- `required_boundary`: authorization, safety, write scope, or stop condition;
- `required_contract`: input/output or artifact invariant that cannot yet be
  mechanical;
- `regression_backed`: named evaluation that fails without it.

This inventory is implementation-time evidence under `tmp_debug`; it is not a
new installed artifact. Any retained instruction without one of these reasons
should be removed.

### 16.3 Orchestrator phase checklist

Use a short live checklist with one in-progress item. It should track only the
current command's major phases and gates. Do not paste the complete workflow into
every update.

## 17. Failure and Recovery

### 17.1 Infrastructure failure before worker work

Examples:

- selected Python lacks dependencies;
- CLI missing;
- authentication failure;
- incompatible launcher flags;
- output schema unsupported.

Correct infrastructure and rerun in the same job directory. Do not consume a
semantic attempt or create another review.

### 17.2 Worker malformed result

Treat malformed/missing structured output as worker failure. Preserve logs.
The orchestrator may relaunch once only after identifying a concrete prompt,
schema, or transport correction. Do not repeatedly ask the same model to repair
its own output without new information.

### 17.3 Worker semantic failure

If the worker cannot complete the bounded task:

- report the exact blocker;
- preserve any authorized changes and validation evidence;
- do not continue to the next phase;
- ask the user only when the unresolved item is genuinely theirs.

### 17.4 Material user change during execution

Terminate the worker and start a fresh job. Do not resume a worker whose core
assumptions changed.

### 17.5 Orchestrator context degradation

The refactor greatly reduces root noise but cannot eliminate very long user
conversation degradation. `scope:session-handoff` remains the supported escape
hatch. The handoff should describe current durable state; the fresh
orchestrator determines the next workflow phase through validators.

### 17.6 Timeout and liveness policy

Every worker role has a configurable hard wall-clock timeout. The runner also
records a liveness timestamp when it receives provider events, observes tool
completion, or confirms the child process is alive. An inactivity threshold
produces a diagnostic warning; it does not automatically kill a worker that may
be running a long test command. Kill only at the hard timeout, explicit user
stop, or confirmed process failure.

Before termination, capture:

- process identity and exit state;
- last provider/tool event;
- current changed-path manifest;
- log tail;
- whether a valid result already exists.

Timeout is an execution failure, not semantic completion. It does not consume a
review attempt unless a reviewer produced a valid attempt artifact.

### 17.7 Orchestrator death and worker recovery

A fresh orchestrator runs `scope-worker.py status` before launching work when an
active run record exists.

- **Worker still alive:** attach to status/log polling; do not launch a second
  worker.
- **Worker exited with a valid result:** validate its result and manifests, then
  resume at the deterministic phase gate.
- **Worker exited with no result and no post-baseline changes:** mark the job
  failed and allow one fresh launch after diagnosing the cause.
- **Worker exited with authorized in-scope changes but no result:** freeze the
  phase and launch a fresh recovery worker to inspect and either complete those
  changes or report why they are unsafe. Do not make the conversational
  orchestrator finish the work.
- **Worker exited with out-of-scope or unattributed changes:** stop and present
  exact paths to the user for ownership/disposition. Never auto-revert them.

Recovery creates a new job ID linked to the failed job. It does not resume the
failed model session or silently treat partial files as completed evidence.

### 17.8 Lock recovery and runtime hygiene

The active lock records job ID, runner PID, process start identity, provider,
access mode, and timestamp. Recovery may clear it only after proving the owner
is no longer alive and preserving the prior metadata. PID alone is insufficient
because identifiers can be reused.

Remove the active lock after clean completion, but retain failed job directories
for diagnosis. Successful job directories may be pruned by an explicit cleanup
operation after canonical evidence is durable. Cleanup is not part of semantic
workflow completion and must never delete current or failed-run evidence
automatically.

## 18. Security and Permissions

### 18.1 Least privilege

- Refinement worker: workspace write, exact post-run write-scope gate.
- Implementation worker: workspace write in the epic worktree.
- Audit synthesis worker: read-only repository access.
- Independent reviewers: existing read-only isolation.
- No worker receives permission to commit or push.

### 18.2 External/destructive actions

Workers must return `user_input` before:

- deployment;
- cloud writes;
- database mutation not already approved by an operational proof;
- destructive migration;
- purchase/cost commitment;
- production secret/config changes;
- material scope expansion.

The orchestrator asks the user and launches a fresh authorized worker only
after confirmation.

### 18.3 Git ownership

The orchestrator owns fixed Scope-internal commits. Story workers and audit
workers never commit. Final merges remain governed by current Scope rules.

## 19. Source Layout

Prefer a shared-first layout similar to:

```text
src_shared/
  commands/
    epic_refine.md                 # thin public orchestrator
    audit_epic.md                  # thin public orchestrator
  workers/
    refinement-worker.md
    implementation-worker.md
    audit-worker.md
  config/
    worker-runtime-policy.yaml
    reviewer-policy.yaml
    worker-result.schema.json
    worker-job.schema.json
  scripts/
    scope-worker.py
    validate-worker-result.py      # omit if runner owns all validation
    validate-refinement.py
    audit-artifacts.py

src_codex/
  config/
    worker-policy.yaml             # GPT-5.6-only phase/profile routing
  commands/
    implement.md                   # thin Codex orchestrator or shared overlay
  agents/
    developer.md                   # slim or retained for non-command use

src_claude/
  config/
    worker-policy.yaml             # Claude-only phase/profile routing
  commands/
    implement.md                   # behaviorally mirrored platform adaptation
  agents/
    developer.md
```

If `implement.md` can be made shared with small platform launcher placeholders,
move it to `src_shared/commands/implement.md` and delete duplicated behavioral
bodies. Do this only if the resulting command is genuinely simpler; do not
create a templating system solely to eliminate two thin files.

The installer already overlays `src_shared/agents`, commands, scripts, config,
skills, and governance. It does not currently create/copy a `workers` directory,
so both installers must be updated if that layout is used.

## 20. Installer and Documentation Changes

Update both `install.sh` and `install.bat`:

- create Claude and Codex `workers` directories;
- overlay `src_shared/workers` to both installations;
- remove obsolete worker/runner names left by earlier installations;
- install worker job/result schemas and worker policy through existing config
  overlays;
- preserve executable bits where required;
- list installed workers in installer output if useful;
- keep installer parity on Windows;
- keep Claude/Codex runtime parity when the headless Claude backend validates;
- if Claude requires the PTY fallback, document Claude write workers as
  POSIX-only and verify Codex write workers on Windows instead of claiming
  silent parity.

Update install smoke checks in `scripts/validate-pr-checks.sh` to verify:

- all three worker prompts installed for Claude and Codex;
- worker runner installed;
- worker policy/schema installed;
- public commands reference the worker protocol;
- obsolete inline launcher duplication is absent.

Update `README.md` with a concise behavioral description:

- public Scope commands remain conversational;
- fresh workers do repository work;
- users never need to enter a worker thread;
- independent reviewers remain separate;
- session handoff remains available for long conversations.

Do not expose implementation details that ordinary users do not need.

## 21. Validation Script Migration

`scripts/validate-pr-checks.sh` currently greps many exact strings in the
monolithic command bodies. Replace those expectations with checks against the
new owner:

- orchestrator rules in public commands;
- worker rules in worker prompts;
- provider/model/sandbox flags in `scope-worker.py` or worker policy;
- reviewer flags in the reviewer runner;
- review count derivation in `validate-refinement.py`;
- install destinations in smoke tests.

Do not keep obsolete strings in orchestrator prompts merely to satisfy old grep
tests.

The mirrored Claude/Codex check must continue to reject accidental behavioral
drift. Shared worker prompts should reduce mirror burden.

## 22. Tests

### 22.1 Characterization tests before refactoring

Before replacing commands, add tests that capture current required behavior:

- all user gates;
- one full refinement review policy;
- risk-based provider topology;
- exact reviewer isolation;
- automatic implementation handoff commit rules;
- exact dependency baseline merge rules;
- worktree ownership;
- sequential stories;
- audit attempt budget;
- targeted verification behavior;
- completion/evidence requirements.

These tests should target behavior, not current paragraph wording.

### 22.2 Worker schema tests

Test:

- valid completed result;
- `user_input` without questions rejected;
- `user_input` without question-discovery attestation rejected;
- a single question that neither completes current blocker discovery nor
  explains why discovery cannot continue is rejected;
- `completed` with blocking concern rejected;
- absolute changed path rejected;
- path traversal rejected;
- missing validation counts rejected;
- unknown fields rejected;
- `next_action` rejected;
- mismatched job ID rejected.

### 22.3 Worker runner tests

Use fake Codex and Claude executables. Verify:

- exact model and effort from policy;
- correct sandbox/access mode;
- no inherited user config for Codex worker;
- output schema passed;
- provider version/toolchain metadata recorded;
- infrastructure failure classified before semantic work;
- malformed output fails loudly;
- no automatic semantic retry;
- Claude preflight uses the selected Scope Python interpreter;
- headless Claude command construction includes structured output and explicit
  non-interactive role-specific permissions;
- PTY reviewer mode remains read-only and unchanged unless a tested shared
  transport helper is extracted;
- a second write worker cannot acquire the same run lock;
- a runner whose CWD is an epic worktree stores and recovers run state under
  `repository_root/tmp_debug/scope-runs`, never the worktree's `tmp_debug`;
- lock filenames are stored under the canonical runtime root but keyed from the
  normalized `working_root`;
- stale-lock recovery refuses to clear a live or identity-mismatched owner;
- timeout captures diagnostics and partial changed paths;
- worker exits with changes but no result enter recovery rather than completion;
- an unattributed path appends exactly one incident record and later ownership
  resolution updates that record instead of incrementing it again;
- simulated supervisor death with a surviving provider child is classified as
  still active and blocks another write worker;
- simulated supervisor and provider death follows the dead-worker recovery
  branches in Section 17.7.

Add one small host-process integration test per supported platform. It launches
a fake long-running provider through the real runner, terminates the supervising
orchestrator/runner boundary used on that platform, and records whether the
provider survives. Assert that `status` classifies the observed outcome and
that `recover` selects the matching Section 17.7 branch. Do not encode one
platform's orphan behavior as a universal assumption. If a platform is not
present in CI, run and report this smoke during that platform's installer
validation before claiming support.

### 22.4 Orchestrator contract tests

Static tests should verify each public command:

- identifies itself as the sole user-facing orchestrator;
- forbids direct authoring/implementation/review;
- launches the correct worker phase;
- preserves user gates;
- stops on worker `user_input`/`blocked`;
- does not accept `next_action` from workers;
- allows only one write worker;
- keeps reviewer concurrency read-only;
- uses validators to determine phase completion;
- requires valid worker receipts for post-baseline canonical changes;
- stops on unattributed changes rather than assigning them to a worker.

Avoid tests that require exact prose beyond stable contract phrases.

### 22.5 Refinement validator regressions

Add fixtures for:

- three full packets with declared count one: fail;
- targeted packet missing fingerprints: fail;
- extra full packet justified only by corrections: fail;
- extra full packet with material change but no authorization: fail;
- honest authorized material-change full packet: pass if policy permits;
- unclassified proof preflight: fail;
- baseline-blocked proof without exact counts/substitute: fail;
- corrected finding without related-surface checks: fail;
- correction sweep with unclassified matches: fail;
- verified finding without independent evidence: fail.

### 22.6 Implementation workflow regressions

Test:

- worker changes an unreported file: fail;
- worker reports a changed file not in Git diff: fail;
- developer-discovered file with evidence: pass;
- forbidden surface touched: fail;
- story completion with skipped proof: fail;
- user question stops story sequence;
- stories execute sequentially;
- nested audit reports through implementation orchestrator;
- remediation outside architecture boundary returns to refinement.

### 22.7 Audit regressions

Test:

- synthesis worker invents a finding absent from sources: reject;
- evidence-backed minority finding preserved;
- deterministic and semantic duplicate merged only when root cause/surface and
  closure match;
- direct audit remains read-only;
- target attempt budgets still derive from durable attempts;
- worker infrastructure retry does not consume an audit attempt.

### 22.8 Install and full validation

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/unit
./scripts/validate-pr-checks.sh
```

Report pass/fail/error/skip counts and coverage. Run both installer smoke paths,
including checks for the declared Windows runtime support and any explicit
Claude PTY limitation.

## 23. Representative Workflow Evaluations

Unit tests cannot establish that prompt slimming improves model behavior. Add a
small manual or scripted evaluation corpus under `tmp_debug` first; promote only
stable fixtures into tests.

Use at least these cases:

### 23.1 SAG-112 proof viability

The worker must execute every existing planned proof command and discover that
the broad E5 module has 27 passing and 2 failing tests before review.

### 23.2 SAG-112 sibling-surface sweep

Given a retained compatibility-script finding, the correction worker must
classify all matching scripts, including
`e26_validate_extraction_quality.py`, before targeted verification.

### 23.3 SAG-112 adjacent reader/header surfaces

The correction worker must inspect both populated and empty pricing header
paths plus adjacent `product -> offering` reader translation surfaces.

### 23.4 Review-budget integrity

The orchestrator must reject another full review when only incomplete
corrections changed. It should require a new author-side correction and, when
allowed, targeted verification.

### 23.5 Mid-run user change

While a worker is active, provide a material user change. The orchestrator must
terminate/restart the worker, record the confirmed decision, and avoid applying
stale output.

### 23.6 Bounded instruction ablation

Require one matched ablation during the `epic_refine` conversion, using the
primary refinement provider, the same repository snapshot, and one combined
SAG-112 job that exercises Sections 23.1-23.3:

1. minimal role, boundaries, inputs, output schema, and stop condition;
2. the current legacy-rich phase instructions as a comparison.

Compare semantic correctness, known missed surfaces, invalid actions, output
contract compliance, tokens, and elapsed time. If both variants miss a known
surface, add the smallest regression-backed instruction and rerun only the
failed case. Do not require a three-role, multi-provider experiment before
shipping the refactor.

Record exactly which evaluations ran, their results, and anything skipped. A
small honest comparison is preferable to an expensive matrix that the
implementing session cannot complete. This is a directional engineering check,
not a statistically conclusive model benchmark.

Measure:

- command prompt bytes;
- worker prompt/job bytes;
- root-context growth;
- number of worker launches;
- number of full/targeted reviews;
- findings introduced during correction;
- missed known surfaces;
- total tokens and elapsed time when available;
- final deterministic pass.

Compare current monolithic behavior with the refactored path using the same repo
snapshot and task. Do not change default models solely from anecdotal results.

## 24. Implementation Order

Do not attempt the entire refactor in one long model session. Deliver it in the
units below. Each unit must start from a describable Git state, pass its own
tests, and end with a concise handoff when another session will continue. A PR
is optional; Scope does not require a PR-based process for these increments.

Staged delivery does not mean supporting two implementations of the same
command. Commands not yet converted remain unchanged. When a command is
converted, replace its monolithic path without a feature flag or compatibility
branch.

### Delivery A: Baseline and known mechanical defects

- resolve or explicitly preserve pending prerequisite changes;
- run full repository validation;
- capture command sizes and current workflow fixtures;
- add the refinement review-count regression;
- implement the already-approved proof-preflight and correction-completeness
  gates where they can land independently;
- inventory current instructions using Section 3.6.

This unit produces immediate value even if later orchestration work pauses.

### Delivery B: Worker foundation

- job/result schemas and validator;
- command baseline and authorship-attribution manifests;
- canonical `repository_root` runtime-state resolution with worktree-CWD
  regression coverage;
- runner lock, lifecycle status, timeout, and recovery;
- Codex backend;
- time-boxed headless Claude spike, followed by either the headless backend or
  an explicit POSIX PTY fallback decision;
- worker policy and minimal worker prompts;
- fake-provider tests and installer smoke for new shared assets.

No public command changes in this unit.

### Delivery C: Convert and dogfood `epic_refine`

- reduce the public orchestrator;
- wire refinement phase/correction workers;
- derive review counts from packets;
- run the bounded SAG-112 evaluations and prompt ablation;
- run the converted command on one real low- or medium-risk epic;
- correct any lifecycle or prompt-contract defect found during that live run.

Do not begin another command conversion until the real refinement reaches its
documented handoff without bypassing a gate.

### Delivery D: Convert and dogfood `audit_epic`

- keep deterministic preparation in scripts;
- add bounded audit synthesis;
- preserve reviewer topology, minority findings, and attempt accounting;
- run the converted audit on one already-implemented epic;
- verify crash/recovery behavior with fake providers before live use.

Convert audit before implementation so the implementation orchestrator can
integrate the final audit interface once, rather than carrying a temporary
nested-audit path.

### Delivery E: Convert and dogfood `implement`

- slim the implementation worker/developer prompt;
- run one fresh worker per story and remediation batch;
- enforce changed-path/evidence attribution;
- preserve automatic handoff and dependency-baseline behavior;
- integrate the already-converted nested audit;
- dogfood on a small epic through implementation, audit, and remediation.

### Delivery F: Consolidate and document

- remove obsolete command prose, launch paths, and grep assertions;
- finish Unix/Windows installer checks and declare any Claude PTY limitation;
- update concise README behavior documentation;
- run unit/coverage, full PR validation, installer smoke, command-size
  measurement, and final artifact inspection.

Use a fresh session between delivery units when context has materially grown.
Do not mark a unit complete when an evaluation or platform check was silently
skipped; record the omission and blocker explicitly.

## 25. Acceptance Criteria

The refactor is complete only when all are true.

### Conversational behavior

- The user interacts only with the public orchestrator.
- Workers never ask the user directly.
- Questions, concerns, issues, and requested changes are handled by the
  orchestrator.
- Material user changes invalidate/restart stale worker jobs.

### Context and role isolation

- Every refinement phase, implementation story, correction batch, and audit
  synthesis starts with fresh bounded worker context.
- Workers do not inherit the full user conversation.
- No worker recursively launches another worker or reviewer.
- The runner lock mechanically prevents two Scope write workers from modifying
  the same working root at once.

### Workflow integrity

- Existing user approval gates remain.
- Existing independent reviewer topology remains.
- No new semantic review round is added.
- Refinement full/targeted counts derive from durable packets.
- Audit attempt counts continue to derive from durable attempts.
- Incomplete corrections cannot trigger another full review by default.
- Proof viability and correction completeness block review when missing.

### Implementation integrity

- Story workers operate only in the epic worktree.
- Actual changed paths match structured worker output.
- Every post-command-baseline canonical change is attributed to a valid worker
  receipt or explicitly identified as concurrent user work.
- Every unattributed-change detection is counted in `run.yaml` with its eventual
  ownership resolution.
- Forbidden/unexplained changes fail loudly.
- Evidence and proof commands remain exact and executable.
- Workers never commit or push.

### Lifecycle integrity

- Every role has an enforced hard timeout and diagnostic liveness reporting.
- A fresh orchestrator can detect and poll a still-running worker.
- Valid results survive orchestrator-session loss.
- Partial changes without a result enter explicit recovery and never become
  completed evidence automatically.
- Stale locks are cleared only after owner identity is proven dead.
- Run/lock state always resolves beneath canonical `repository_root`, including
  recovery launched from an epic worktree.
- Platform tests confirm how provider children behave when their supervisor
  session dies, and both survival outcomes map to deterministic recovery.
- `user_input` batches all currently discoverable blocking questions.

### Prompt quality

- Public commands are materially smaller and contain each core rule once.
- Worker prompts are rebuilt from minimal contracts rather than extracted from
  legacy commands.
- Every retained legacy instruction is a required boundary, required contract,
  or named regression-backed control.
- Ablation evaluations show that the selected prompt is no more prescriptive
  than necessary for reliable outcomes.
- Provider launcher syntax is centralized in scripts/configuration.
- Long raw outputs do not enter the conversational root.

### Platform/install quality

- Claude and Codex behavioral contracts remain mirrored where supported, and
  every platform transport deviation is documented and tested.
- `install.sh` and `install.bat` install every required worker asset.
- Install smoke verifies expected destinations.
- Headless Claude write-worker behavior is tested on supported platforms; if a
  PTY fallback is necessary, its POSIX-only limitation is explicit.
- Full PR validation passes with no skipped failures.

## 26. Explicit Decisions for the Implementing Session

Treat these as approved design direction unless repository evidence makes them
impossible:

1. Convert exactly `epic_refine`, `implement`, and `audit_epic`.
2. The main command is conversational orchestration only.
3. The user never interacts directly with workers.
4. Use fresh workers per phase/story/correction/synthesis, not one worker per
   command.
5. Use one write worker at a time.
6. Use controlled provider processes with structured output rather than relying
   on inherited native subagent model settings.
7. Keep existing durable workflow artifacts; do not add a permanent
   orchestration ledger.
8. Do not add `next_action` to worker results.
9. Do not add independent reviewers.
10. Make review accounting, proof preflight, and correction completeness
    validator-enforced.
11. Preserve Claude/Codex parity and Windows installer parity.
12. Do not support the legacy monolithic execution path.
13. Do not migrate historical prompt prose by default; rebuild minimal prompts
    and restore instructions only from boundary, contract, or regression
    evidence.
14. Require command baselines, worker receipts, and an exclusive runner lock;
    do not install a global edit-denial hook in the initial refactor.
15. Validate headless Claude workers before considering a PTY write-worker
    fallback.
16. Keep targeted-verification allowance changes outside this refactor.
17. Deliver and dogfood one command at a time, with `audit_epic` converted
    before `implement`.

## 27. Decisions That Still Require Repository-Level Judgment

The implementing agent must inspect current code before deciding:

- whether thin `implement.md` platform files remain clearer than a shared
  command with platform branches;
- the exact Claude worker model/effort defaults that preserve current behavior;
- the exact headless Claude tool allowlist/permission flags proven by the
  transport spike;
- whether proof-preflight execution belongs in a new small script or an
  existing validator subcommand;
- whether audit packet preparation needs any worker at all (prefer mechanical);
- exact prompt-size targets after measuring installed prompts.

These are implementation choices, not invitations to change the architecture
above.

## 28. Instructions to the Next Session

1. Read Sections 1-7 and 24-28, then use the Section 1.1 map to load only the
   current delivery unit's detailed sections.
2. Load repository instructions and the project-documentation skill.
3. Inspect Git status and prerequisite changes before editing.
4. Read the current public commands, worker/reviewer prompts, validators,
   installer overlays, and tests.
5. Challenge this brief only where current repository evidence contradicts it.
6. Prefer shared files and existing validators over duplicated prompt logic.
7. Start with the first incomplete delivery unit in Section 24; do not attempt
   all units in one context.
8. For Delivery B, resolve the headless Claude transport spike before designing
   a write-capable PTY extension.
9. Do not paste this full brief into orchestrator or worker prompts. Use it as an
   implementation reference and build minimal runtime contracts.
10. Do not stop after producing another proposal. Complete and validate the
   current delivery unit unless the user explicitly requests planning only.
11. End each delivery unit with exact tests/evaluations run, anything skipped,
   remaining state, and the next unit's prerequisites. Use
   `scope:session-handoff` before context quality degrades.
12. Do not commit without the user's confirmed meaningful label unless a fixed
   Scope-internal command label applies.

The intended outcome is not "more agents." It is a cleaner separation where
the user-facing session retains decisions and trust, bounded workers perform
noisy execution, and validators prevent known forms of procedural drift.

## 29. Retrospective Implementation Improvements

This section records improvements made while implementing and hardening the
plan. It is retrospective: it preserves the original requirements above while
distinguishing genuinely new capabilities, stronger enforcement, and planned
behavior that was completed or hardened.

### 29.1 Genuinely new capabilities

- **CodeGraph 1.5+ integration.** Workers and reviewers receive synchronized,
  worktree-specific, query-only CodeGraph access. Scope initializes only
  Git-ignored indexes, records readiness in receipts, and falls back visibly to
  `rg` and direct reads. Affected-test discovery supplements mandatory tests
  rather than replacing them. This was absent from the original plan. See
  `src_shared/config/codegraph-policy.yaml` and
  `src_shared/scripts/scope_codegraph.py`.
- **Task-specific model and effort matrices.** The plan prescribed
  provider-local policy files but left exact mappings unresolved. The
  implementation assigns models and effort per worker phase:
  - Codex uses Sol for difficult judgment, verification, and debugging; Terra
    for bounded implementation and synthesis; and Terra/Luna in budget mode.
  - Claude uses Fable for product/design judgment, Opus for handoff,
    correction, verification, remediation, and debugging, and Sonnet for
    bounded execution and synthesis.

  See `src_codex/config/worker-policy.yaml` and
  `src_claude/config/worker-policy.yaml`.
- **Evergreen Claude aliases.** Claude routes use `fable`, `opus`, and `sonnet`
  rather than version-pinned IDs, allowing Anthropic to update alias targets
  without Scope configuration changes.
- **Model-execution truthfulness.** Claude worker receipts distinguish the
  requested alias from actual model IDs reported through `modelUsage` and
  detect configured Fable-to-Opus fallback. The Claude reviewer text transport
  honestly records actual-model information as unavailable rather than treating
  the requested alias as proof.
- **Explicit reviewer model routing.** Refinement uses Codex Sol at max effort
  plus Claude Fable at max effort. Audit uses Codex Sol at max effort plus
  Claude Opus at xhigh effort. Budget reviewers remain frontier-grade at high
  effort. See `src_shared/config/reviewer-policy.yaml`.
- **Expanded reviewer sets.** Later user direction superseded the original
  plan's "do not add reviewers" constraint. An optional expanded set can add
  Antigravity with Gemini 3.1 Pro High and OpenCode with GLM 5.2 at max effort,
  while workers remain on the user's primary provider. Reviewer profile and
  reviewer set are independent choices.
- **General multi-provider reviewer supervisor.** The shared reviewer runner
  adds:
  - an all-provider preflight barrier;
  - parallel launch before waiting;
  - assignment-owned output paths;
  - strict semantic output contracts;
  - repository and Git-identity isolation checks;
  - immutable packet/template hashes and source snapshots;
  - infrastructure-only repair while preserving completed reviews;
  - prohibition of semantic retries; and
  - one narrowly bounded Antigravity audit fallback, only for a proven quota
    failure before any semantic output.

  See `src_shared/scripts/scope-reviewer.py`.
- **Provider-compatible transport schemas.** Scope projects the authoritative
  worker-result schema into a stricter provider-compatible JSON Schema,
  normalizes only transport-introduced null placeholders, and then validates
  against the complete authoritative schema.
- **Read-only audit proposals.** Audit-synthesis workers do not need repository
  write access. They return one typed `proposed_artifacts` document;
  deterministic code verifies the complete worker receipt, manifests,
  immutable source snapshot, provenance, and finding integrity before applying
  it. See `src_shared/config/worker-result.schema.json` and
  `src_shared/scripts/audit-artifacts.py`.

### 29.2 Stronger enforcement than the plan specified

- **Hash-bound Gate 0-3 approval ledger.** Approvals are durable, chained to
  prior approvals, bound to the epic and exact artifact hashes, and rejected
  when missing, reordered, tampered with, or stale.
- **Unambiguous Gate 3 ordering.** The user approves a deterministic handoff
  candidate first; only then does the finalize worker materialize the approved
  status and summary.
- **Trusted deterministic-operation channel.** Refinement scaffolding, review
  packets, reviewer runs, proof preflight, audit preparation/gates/synthesis/
  finalization, and authorized dependency-baseline merges run through an
  allowlisted, locked executor. Receipts bind the exact command, authority
  script, write scope, manifests, logs, hashes, exit status, and whether a Git
  HEAD change was authorized. See
  `src_shared/config/worker-runtime-policy.yaml` and
  `src_shared/scripts/scope-worker.py`.
- **Executable review-packet authorship.** Review assignments, topology,
  profile, reviewer set, full/targeted classification, and extra-review
  authorization are derived mechanically from policy rather than
  conversational prose.
- **Content-bound reviewer provenance.** Receipts bind the packet, template,
  assignments, output hashes, Git identity, repository manifests, decisions,
  candidates, and targeted-verification records. Minority findings are
  preserved rather than discarded through consensus.
- **Mechanical critical-risk acceptance.** `accepted_risk` requires a uniquely
  resolving durable authorization section that binds `user_approved`, the exact
  finding fingerprint, and its description. A boolean or prose assertion is
  insufficient.
- **Canonical correction receipts.** Verified correction-worker evidence is
  copied from prunable runtime state into a content-hashed epic ledger.
  Permanent validation therefore does not depend on `tmp_debug`.
- **Post-correction drift protection.** Finalization may change only explicitly
  configured mechanical frontmatter fields. Semantic hashes ensure later edits
  cannot silently invalidate accepted correction evidence.
- **Stable attribution incidents.** Incidents have stable IDs, resolve under
  the working-root lock, require current changed paths to match the incident,
  and create a fresh incident if a resolved path is modified again.
- **Cancellation/publication race protection.** A publication lock prevents a
  worker from publishing stale success after cancellation. Cancellation
  preserves process identity, descendants, process-group state, changed paths,
  and partial-result evidence. Late repository drift also invalidates an
  otherwise valid result.
- **More truthful process containment.** Process-group state is sampled before
  descendants are reaped, with a bounded natural-exit grace followed by forced
  termination. Metadata distinguishes state at parent exit, after grace, and
  after reaping.
- **Real symbol anchors.** Durable evidence can resolve headings, YAML keys and
  IDs, Python and compiled-language symbols, JavaScript assignments, shell
  functions, and HTML anchors while still requiring unique, in-scope
  resolution.

### 29.3 Planned behavior that was completed or hardened

The following improve the implementation but are not new architectural ideas
because the original plan already called for them:

- Non-completed results report only validations actually executed. Only
  `completed` requires every declared validation with zero failures, errors, or
  skips.
- The diagnostic worker is implemented end to end as a fresh, read-only,
  bounded worker.
- Proof preflight executes exact declared commands, kills complete process
  groups on timeout, records non-negative counts, and atomically binds
  stdout/stderr hashes to durable evidence. Implementation-created paths must
  appear as exact command tokens, not substrings.
- `scope_root` remains the installed Scope location even when implementation
  moves into a linked worktree; ignored `.claude` or `plugins/scope` files are
  not assumed to have been copied.
- Claude implementation shell access is bounded to configured test, build, and
  static-analysis command families rather than unrestricted Bash.
- `run.yaml` is not fully rewritten and fsynced every polling second when
  nothing changed; a bounded heartbeat preserves recovery information.
- The Codex workflow skill explicitly launches implementation and diagnostic
  work in fresh workers.
- Reviewer topology has one policy authority; duplicated prose mappings were
  removed.
- Unix and Windows installers remove `.DS_Store`, `__pycache__`,
  `.pytest_cache`, `*.pyc`, and `*.pyo`.
- The four public command bodies were reduced from 79,414 to 39,478 bytes, a
  50.3 percent reduction, while retaining executable gates.
- Live dogfood replaced the pre-existing Claude PTY reviewer with direct
  authenticated CLI stdin/stdout transport and removed the `pexpect` dependency.
- Regression coverage was added for approvals, trusted operations,
  cancellation races, incident re-tampering, process groups, audit proposals,
  model routing and fallback, CodeGraph, provider isolation, installer parity,
  and transport normalization.
