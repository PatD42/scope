---
name: implement
description: Implement an epic story-by-story. Developer implements and writes tests. Runs audit on completion and apply recommendations.
args: "{epic-id}"
skills: project-documentation
agents: architect, developer
---

# /implement

Implement an epic story-by-story using a single developer agent.

**Syntax:** `/implement {epic-id}`

## Prerequisites

Before running, the epic MUST have completed `/epic_refine`:
- `docs/epics/{epic-dir}/acceptance-criteria.md` exists
- `docs/epics/{epic-dir}/architecture.md` exists
- `docs/epics/{epic-dir}/file-plan-story-*.yaml` exists
- Epic status is "ready-for-implementation"

## Refinement Stop Conditions

Do not let the Developer invent missing decisions during implementation:
- If the Developer must decide what the system should do, business requirements were incomplete and implementation must stop until the Product Owner clarifies them.
- If the Developer must decide how the system should be designed, architecture was incomplete and implementation must stop until refinement returns to the Architect.

## Completion Policy

`/implement` is not allowed to stop at "stories complete", "code complete", or any other intermediate checkpoint.

No downstream command may declare the epic complete until:
- all planned implementation and remediation work is finished
- epic-wide tests pass
- `audit_epic` has been run and the final audit passes

Before that point, report only progress or a blocked state. Do not use completion language for the epic.

---

## Orchestration Model

```
Story 0 (if exists):
  architect-story-0

Story 1:
  dev-story-1 (blocked by architect-story-0 if exists)

Story 2 (depends on Story 1):
  dev-story-2 (blocked by dev-story-1)  ← respects declared dependencies

Story N:
  dev-story-N (blocked by dev tasks of declared dependencies)

After all complete:
  /audit_epic {epic-id}
  Create fix stories from audit recommendations
  Implement fix stories
  Run all epic tests
  Final audit
```

**Key rules:**
- **ONE developer agent at a time** — concurrent writes to the same worktree cause race conditions and inconsistent state
- Developer tasks respect inter-story implementation dependencies
- The developer agent processes tasks sequentially, picking the lowest-ID unblocked dev task
- Story 0 (scaffolding) is done by the architect before any dev work
- Developer writes BOTH production code AND tests for each story

---

## Execution

### Step 0: Initialize

```bash
EPIC_ID="{epic-id}"

# Find epic directory
EPIC_DIR=$(ls docs/epics/ | grep -i "^${EPIC_ID}" | head -1)
if [ -z "$EPIC_DIR" ]; then
  echo "Epic not found in docs/epics/"
  exit 1
fi

# Verify prerequisites
if [ ! -f "docs/epics/${EPIC_DIR}/file-plan-story-01.yaml" ]; then
  echo "No file plans found. Run /epic_refine first."
  exit 1
fi

# Ensure refinement artifacts are committed before creating worktree
EPIC_FILES=$(git status --porcelain "docs/epics/${EPIC_DIR}/" "docs/architecture/13-specs/" 2>/dev/null)
if [ -n "$EPIC_FILES" ]; then
  echo "Uncommitted refinement artifacts detected:"
  echo "$EPIC_FILES"
  echo ""
  echo "Committing refinement artifacts..."
  git add "docs/epics/${EPIC_DIR}/"
  git add "docs/architecture/13-specs/" 2>/dev/null || true  # May not exist for all epics
  git commit -m "refine(${EPIC_ID}): refinement artifacts for implementation"
fi

# Create worktree for implementation
WORKTREE_DIR="wip/${EPIC_ID}"
BRANCH_NAME="epic/${EPIC_ID}"

if [ -d "$WORKTREE_DIR" ]; then
  echo "Worktree already exists at ${WORKTREE_DIR}. Resuming."
else
  git branch "$BRANCH_NAME" 2>/dev/null || true  # Branch may already exist
  git worktree add "$WORKTREE_DIR" "$BRANCH_NAME"
fi

# All subsequent work happens in the worktree
cd "$WORKTREE_DIR"
```

### Step 0b: Check for Unwrapped Epic

```python
# If another epic has a worktree but hasn't been wrapped, warn the user
existing_worktrees = Glob("wip/*/")
for wt in existing_worktrees:
    other_epic = wt.split("/")[1]
    if other_epic != EPIC_ID:
        wrap_markers = Glob(f".scope/tracking/commands/wrap_epic-*{other_epic}*.jsonl")
        if not wrap_markers:
            print(f"WARNING: Epic {other_epic} has an active worktree at wip/{other_epic}/ but hasn't been wrapped.")
            print(f"Run /wrap_epic {other_epic} first to capture decisions and lessons?")
            print("[yes — wrap first / no — proceed with {EPIC_ID}]")
            # If user says yes, run /wrap_epic for the other epic first
```

### Step 0c: Load Context Enrichment

```python
# 1. Load project lessons learned
lessons_index = Read("docs/lessons-learned/INDEX.md")
if lessons_index:
    lessons_context = lessons_index
    print(f"Loaded {lessons_index.count('- [')} lessons learned for developer context.")
else:
    lessons_context = ""

# 2. Load system-level ADRs (not just epic ADRs)
system_adrs = Read("docs/architecture/09-adr-summary.md")
system_adr_context = system_adrs if system_adrs else ""

# 3. MCP context enrichment (optional)
mcp_context = ""

# If codegraph MCP is available, query for module dependencies
# relevant to files in the epic's file plans
if mcp_available("codegraph"):
    file_plans = Glob(f"docs/epics/{EPIC_DIR}/file-plan-story-*.yaml")
    planned_files = extract_file_paths(file_plans)
    for f in planned_files:
        deps = codegraph.query_dependencies(f)
        mcp_context += f"\n# Dependencies for {f}: {deps}"
    print(f"Loaded codegraph context for {len(planned_files)} planned files.")

# If Obsidian MCP is available, query for relevant lessons and decisions
if mcp_available("obsidian"):
    epic_title = Read(f"docs/epics/{EPIC_DIR}/details.md").split("\n")[0]
    obsidian_notes = obsidian.search(epic_title)
    if obsidian_notes:
        mcp_context += f"\n# Obsidian context: {obsidian_notes}"
        print(f"Loaded {len(obsidian_notes)} relevant notes from Obsidian vault.")
```

### Step 1: Discover Stories

Find all `file-plan-story-*.yaml` files in the epic directory and sort them to ensure story-00, story-01, story-02... order.

For each file plan:
1. Read the YAML content to extract `story_id` and `story_title`
2. Extract the story number from the filename (e.g., `file-plan-story-02.yaml` → `"02"`)
3. Look for a `# Dependencies: Stories 01a, 01b, 02` comment line in the file and parse the referenced story numbers into a list (e.g., `["01a", "01b", "02"]`)
4. Record whether this is a scaffolding story (number `"00"`)

Build a list of story objects with: `number`, `story_id`, `story_title`, `file_plan_path`, `dependencies`, `is_scaffolding`.

Check if the first story is Story 0 (scaffolding).

### Step 2: Create Tasks

Create all tasks upfront with dependencies, then launch agent.

```python
task_ids = {}  # Track task IDs for dependency wiring

# --- Story 0: Architect scaffolding (if exists) ---
if has_story_0:
    story_0 = stories[0]
    task_ids["architect-story-00"] = TaskCreate(
        subject=f"architect: Implement scaffolding for {epic_id}",
        description=f"""
epic_id: {epic_id}
phase: scaffolding
story_id: {story_0['story_id']}
story_title: {story_0['story_title']}
file_plan: {story_0['file_plan_path']}
terminate_upon_completion: no

Instructions:
- Read the file plan at {story_0['file_plan_path']}
- Create all directories, modules, config files, and base classes listed
- If contracts.py is listed in the file plan, create it with Protocol classes
  that define the interfaces between components. Verify with:
  `python -c "from <module>.contracts import *"` and `mypy --strict contracts.py`
- Do NOT implement business logic — only scaffolding
- Verify the skeleton compiles/imports correctly
- DOCUMENTATION UPDATES: Read the epic's architecture.md for the documentation
  update plan. Update product-level architecture docs as specified by the architect
  during refinement. This includes:
  - backend/data.md (if schema changes are planned)
  - backend/services.md (if new services are planned)
  - backend/overview.md (if service landscape changes)
  - 05-building-blocks.md (if new components are planned)
  - 03-context.md (if new external dependencies)
  - 08-cross-cutting/domain.md (if new domain entities)
  - 12-glossary.md (if new technical terms)
  - 09-adr-summary.md (roll up epic ADRs)
  - product/decisions.md (roll up epic PDRs)
  Use the project-documentation skill templates for any new files.
  These updates reflect the DESIGNED architecture — before implementation.
  The developer must NOT update these docs during implementation to avoid
  laundering divergence.
""",
        activeForm="Implementing scaffolding"
    )

# --- For each implementation story ---
impl_stories = [s for s in stories if not s["is_scaffolding"]]

for story in impl_stories:
    num = story["number"]

    # Developer task: implement + write tests
    dev_blocked_by = []
    if has_story_0 and num == impl_stories[0]["number"]:
        # First dev task depends on scaffolding
        dev_blocked_by.append(task_ids["architect-story-00"])

    dev_task_id = TaskCreate(
        subject=f"developer: Implement story {num} - {story['story_title']}",
        description=f"""
epic_id: {epic_id}
phase: implementation
story_id: {story['story_id']}
story_title: {story['story_title']}
file_plan: {story['file_plan_path']}
terminate_upon_completion: no

Context to load:
- Read the file plan at {story['file_plan_path']}
- Read acceptance criteria from docs/epics/{epic_dir}/acceptance-criteria.md
- Read architecture from docs/epics/{epic_dir}/architecture.md
- Read ADRs from docs/epics/{epic_dir}/adr.md (epic-level decisions)
- Read system ADRs from docs/architecture/09-adr-summary.md (project-wide decisions)
- Read test strategy from docs/epics/{epic_dir}/test-strategy.md
- Read lessons learned from docs/lessons-learned/INDEX.md (if exists) — these are
  hard-won patterns and anti-patterns from previous work. Apply any relevant lessons
  as constraints during implementation. Violating a documented lesson is a bug.

{f"MCP context:{chr(10)}{mcp_context}" if mcp_context else ""}

Instructions:
- If contracts.py exists in the epic source, import Protocol types from it and
  use them as type annotations for parameters, return types, and dependency
  injection. The contracts define the agreed interfaces — implementations MUST
  satisfy them. Run `mypy --strict` on your files to verify compliance.
- Implement PRODUCTION-READY code that fulfills the file plan intent
- Follow the intent documentation in the file plan — intent is the source of truth
- Match the public_interface / signature_changes exactly
- Write tests (unit + integration as appropriate) for the code you implement
- If contracts.py exists, include tests that verify implementations satisfy the
  Protocol interfaces. Import Protocol types and assert structural compatibility.
- Run all tests after implementation — all must pass
- CRITICAL: If the file plan intent describes external I/O (API calls, HTTP
  requests, database operations, file system writes), the implementation MUST
  contain real I/O code — not hardcoded return values or placeholder stubs.
  If a dependency is unavailable for unit testing, implement the real code
  and let tests mock around it. The implementation itself must be production-ready.
- A "# Placeholder", "# TODO", or "# Stub" comment in production code is a FAILURE.

Decision tracking:
- If you make an unplanned architectural choice (different pattern, different
  library, different approach than the file plan), flag it in your agent summary
  under concerns with type: "decision_candidate" and explain why.
- If you deviate from a system ADR, flag it as type: "adr_deviation".
- These will be surfaced by /wrap_epic for formal recording.

Pre-completion review (MANDATORY before marking story done):
READ the full checklist from .claude/governance/developer-checklist.md before marking complete.
Do NOT rely on memory of the checklist. Do NOT summarize it. READ THE FILE from disk.
The checklist includes 10 items: intent match, no dead code, pattern consistency,
lesson compliance, unplanned changes, contract compliance, scope check, no hardcoded
values, LIVE SMOKE TEST for new services, no redundant tests.

{f"Project lessons:{chr(10)}{lessons_context}" if lessons_context else ""}
""",
        activeForm=f"Implementing story {num}"
    )
    task_ids[f"dev-story-{num}"] = dev_task_id

    # Wire dependencies
    if dev_blocked_by:
        TaskUpdate(taskId=dev_task_id, addBlockedBy=dev_blocked_by)

# --- Second pass: wire inter-story implementation dependencies ---
for story in impl_stories:
    num = story["number"]
    dev_task_id = task_ids[f"dev-story-{num}"]

    for dep_num in story["dependencies"]:
        dep_key = f"dev-story-{dep_num}"
        if dep_key in task_ids:
            TaskUpdate(taskId=dev_task_id, addBlockedBy=[task_ids[dep_key]])
```

### Step 3: Launch Agents

```python
# Spawn agents using Task tool — all in ONE message

# 1. Architect (if Story 0 exists)
if has_story_0:
    Task(
        prompt="Take the role of architect agent. Find and execute your scaffolding task.",
        subagent_type="general-purpose",
        description="Architect: scaffolding",
        run_in_background=True
    )

# 2. Developer agent — SINGLE agent, sequential execution
# 🚨 NEVER spawn more than ONE developer agent. Multiple developers writing to
#    the same worktree causes race conditions, merge conflicts, and corrupted state.
#    If you need to re-launch after failure, wait for the current one to finish first.
#
# 🚨 CRITICAL: The agent launch prompt MUST reference the governance checklist file.
#    Do NOT summarize the checklist — the agent must READ the file from disk.
#    This ensures instructions survive context summarization and compaction.
Task(
    prompt="""Take the role of developer agent.
    Process dev tasks ONE AT A TIME in dependency order:
    1. Check TaskList for the lowest-ID dev task that is pending and has NO blockedBy
    2. If none available, STOP — you will be re-launched when tasks unblock
    3. Read the task description — it contains file plan path, context to load, and constraints
    4. Implement production-ready code AND write tests
    5. Run all tests — all must pass
    6. BEFORE marking complete: Read and verify ALL items in the developer checklist file.
       Look for it at: .claude/governance/developer-checklist.md (or src/governance/developer-checklist.md in the SCOPE repo)
       Do NOT skip this step. Do NOT rely on memory of the checklist. READ THE FILE.
    7. Mark completed
    8. Check TaskList again for next unblocked dev task
    9. Repeat until no more dev tasks available

    CRITICAL: Only work on tasks where ALL blockedBy tasks show status=completed.
    You are responsible for BOTH implementation AND tests — there is no SDET.
    The checklist in step 6 includes: intent match, no dead code, pattern consistency,
    lesson compliance, unplanned changes, contract compliance, scope check, no hardcoded
    values, LIVE SMOKE TEST for new services, no redundant tests.""",
    subagent_type="general-purpose",
    description="Developer: implement",
    run_in_background=True
)
```

**Tell user:**
```
Implementing {epic-id} with {N} stories (no SDET):

🏗️ Architect: Story 0 scaffolding (if applicable)
💻 Developer: Implementing + testing sequentially (story 1 → 2 → ... → N)

Agent is working. I'll run the audit when it completes.
```

### Step 4: Wait for Completion

**STOP after spawning agents.** Wait for all background tasks to complete.

When all tasks are done (all marked `completed` in TaskList):

### Step 4b: Epic-Wide Lint Check

Run ruff and vulture across ALL files created/modified in this epic. Developer already linted per-story, but this catches cross-story issues (e.g., an import added in story 1 that becomes unused after story 3 refactors it).

1. Collect all production file paths from every file plan (`files_to_create` + `files_to_modify`)
2. Run `ruff check --fix` and `ruff format` on all collected files (auto-fix what you can)
3. Run `vulture` on all collected files to detect dead code
4. If `contracts.py` exists in the epic source, run `mypy --strict` on all collected files
5. Re-run ruff and vulture to check what remains unfixed
6. If any remaining violations exist, write them to `docs/epics/{epic-dir}/lint_findings.yaml` as a YAML dict with keys: `ruff_violations`, `vulture_dead_code`, `mypy_errors`
7. Re-run all tests to confirm auto-fixes didn't break anything

Any remaining lint violations that couldn't be auto-fixed are written to `lint_findings.yaml` and will be picked up by the audit in the next step.

### Step 5: Audit

```python
# Run audit
Skill(skill="audit_epic", args=epic_id)

# Read audit results
audit = Read(f"docs/epics/{epic_dir}/epic_audit.md")

# Present to user
Output: f"""
Implementation work finished for {epic_id}. Final audit is now running; the epic is not complete until audit passes.

Audit results:
- Status: {audit.status}
- Critical issues: {audit.critical_count}
- Major issues: {audit.major_count}
- Minor issues: {audit.minor_count}
"""
```

If audit status is PASS with no findings → skip to Step 8.

### Step 6: Create Fix Stories from Audit

Convert ALL audit findings (critical, major, minor) into additional stories with file plans. The architect agent handles this.

```python
if not audit.has_findings:
    # Skip to Step 8
    pass
else:
    # Number fix stories continuing from last story number
    last_story_num = impl_stories[-1]["number"]  # e.g., "07"

    fix_task_id = TaskCreate(
        subject=f"architect: Create fix stories from audit for {epic_id}",
        description=f"""
epic_id: {epic_id}
phase: audit_fix_planning
audit_report: docs/epics/{epic_dir}/epic_audit.md
last_story_number: {last_story_num}

Instructions:
- Read the audit report at docs/epics/{epic_dir}/epic_audit.md
- Create fix stories ONLY for Phase 1-7 findings (code issues).
  Do NOT create fix stories for Phase 8 (Documentation Sync) findings —
  those are recommendations that require user approval before any doc changes.
  Phase 8 findings will be handled by the user via /wrap_epic or manually.
- For each Phase 1-7 finding (critical, major, AND minor), create a fix story
- Group related findings into the same story when they affect the same files
- If audit found code divergence from architecture, fix the CODE to match
  the design — do NOT update docs to match divergent code (that launders
  the divergence and makes drift invisible)
- Number fix stories continuing from {last_story_num} (e.g., story-{next_num}, story-{next_num+1}...)
- For each fix story, create a file-plan-story-NN.yaml with:
  - files_to_modify (with intent + signature_changes if applicable)
  - files_to_create (if new test files needed)
  - Dependencies on existing stories (most fixes depend on the story they're fixing)
- Write fix stories to docs/epics/{epic_dir}/acceptance-criteria.md (append)
- Write file plans to docs/epics/{epic_dir}/file-plan-story-NN.yaml
""",
        activeForm="Creating fix stories from audit"
    )

    # Wait for architect to finish
    # (This runs synchronously — do NOT launch in background)
```

### Step 7: Implement Fix Stories

Once the architect creates fix stories, run them through the developer pipeline (no SDET).

```python
    # Discover new fix stories (file plans created by architect in Step 6)
    new_file_plans = Glob(f"docs/epics/{epic_dir}/file-plan-story-*.yaml")
    new_file_plans.sort()

    fix_stories = []
    for plan_path in new_file_plans:
        story_num = extract_story_number(plan_path)
        if int(story_num) > int(last_story_num):  # Only new stories
            plan_content = Read(plan_path)
            plan = read_yaml(plan_path)
            dep_line = [l for l in plan_content.split('\n') if l.startswith('# Dependencies:')]
            story_deps = parse_story_refs(dep_line)

            fix_stories.append({
                "number": story_num,
                "story_id": plan["story_id"],
                "story_title": plan["story_title"],
                "file_plan_path": plan_path,
                "dependencies": story_deps,
                "is_scaffolding": False
            })

    if not fix_stories:
        # Architect determined no fix stories needed — skip to Step 8
        pass
    else:
        # Create tasks for fix stories
        for story in fix_stories:
            num = story["number"]

            dev_task_id = TaskCreate(
                subject=f"developer: Implement fix story {num} - {story['story_title']}",
                description=f"""
epic_id: {epic_id}
phase: implementation
story_id: {story['story_id']}
story_title: {story['story_title']}
file_plan: {story['file_plan_path']}
terminate_upon_completion: no

Context to load:
- Read the file plan at {story['file_plan_path']}
- Read the audit report at docs/epics/{epic_dir}/epic_audit.md for context
- Read system ADRs from docs/architecture/09-adr-summary.md
- Read lessons learned from docs/lessons-learned/INDEX.md (if exists)

Instructions:
- This is a FIX story from audit findings
- Implement PRODUCTION-READY code that fixes the audit finding
- Follow the intent documentation in the file plan — intent is the source of truth
- If contracts.py exists, ensure fixes maintain Protocol compliance. Import
  Protocol types for type annotations and run `mypy --strict` to verify.
- If this is a documentation update story, update files in docs/architecture/ to
  reflect the actual implementation accurately
- Write tests that verify the audit finding is fixed
- If contracts.py exists, include tests that assert Protocol compliance for
  interfaces affected by the fix
- Run all tests after implementation — all must pass
- CRITICAL: No stubs, no placeholders, no TODOs in production code

Decision tracking:
- If the fix requires an unplanned architectural choice, flag it in your
  agent summary under concerns with type: "decision_candidate".

Pre-completion review:
READ the full checklist from .claude/governance/developer-checklist.md before marking complete.
Do NOT rely on memory. READ THE FILE.
""",
                activeForm=f"Implementing fix story {num}"
            )
            task_ids[f"dev-story-{num}"] = dev_task_id

        # Wire inter-story dependencies for fix stories
        for story in fix_stories:
            num = story["number"]
            dev_task_id = task_ids[f"dev-story-{num}"]
            for dep_num in story["dependencies"]:
                dep_key = f"dev-story-{dep_num}"
                if dep_key in task_ids:
                    TaskUpdate(taskId=dev_task_id, addBlockedBy=[task_ids[dep_key]])

        # 🚨 NEVER spawn more than ONE developer agent.
        Task(
            prompt="""Take the role of developer agent.
            Process dev tasks ONE AT A TIME in dependency order:
            1. Check TaskList for the lowest-ID dev task that is pending and has NO blockedBy
            2. If none available, STOP — you will be re-launched when tasks unblock
            3. Implement it AND write tests
            4. Run all tests — all must pass
            5. Mark completed
            6. Check TaskList again for next unblocked dev task
            7. Repeat until no more dev tasks available

            CRITICAL: Only work on tasks where ALL blockedBy tasks show status=completed.
            You are responsible for BOTH implementation AND tests — there is no SDET.""",
            subagent_type="general-purpose",
            description="Developer: fix stories",
            run_in_background=True
        )

        # Wait for fix story agent to complete
```

### Step 8: Run All Epic Tests

After all stories (original + fixes) are implemented, run the full epic test suite.

```python
# Collect ALL test files from ALL file plans (original + fix)
all_file_plans = Glob(f"docs/epics/{epic_dir}/file-plan-story-*.yaml")
test_files = []
for plan_path in all_file_plans:
    plan = read_yaml(plan_path)
    for f in plan.get("files_to_create", []) + plan.get("files_to_modify", []):
        if "/tests/" in f["path"] or f["path"].endswith(".test.ts") or f["path"].endswith("_test.py"):
            test_files.append(f["path"])

# Run all epic tests
Bash(f"run_tests {' '.join(test_files)}")  # Adapt to project test runner

if all_passed:
    Output: f"""
    All {len(test_files)} test files pass.
    """
else:
    Output: f"""
    {failed_count} test failures detected.
    Failing tests: {failing_tests}

    Investigating failures...
    """
    # Debug and fix remaining failures
    # Re-run tests until all pass or escalate to user
```

### Step 9: Final Audit

Re-run audit to confirm all findings are resolved.

```python
Skill(skill="audit_epic", args=epic_id)
audit = Read(f"docs/epics/{epic_dir}/epic_audit.md")

if audit.status == "PASS":
    Output: f"""
    Epic {epic_id} complete.
    Audit: PASS
    All tests: PASS
    """
    # Proceed to Step 10 (worktree cleanup)
else:
    Output: f"""
    Epic {epic_id} still has open findings after fix stories.
    Remaining: {audit.critical_count} critical, {audit.major_count} major, {audit.minor_count} minor
    Review docs/epics/{epic_dir}/epic_audit.md for details.
    """
    # ⚠️ DO NOT loop back to Step 6. Two audit cycles is the maximum.
    # Escalate to user for manual resolution.
```

**Max audit iterations: 2.** The initial audit (Step 5) plus one fix cycle (Steps 6-9) is the limit. If the final audit still has findings, present them to the user and stop. Do not create a third round of fix stories — diminishing returns and compounding risk of drift.

If the final audit does not pass, the epic is not complete. Report it as blocked on unresolved audit findings.

### Step 10: Worktree Cleanup

After the final audit passes (or after presenting unresolved findings to the user), do not clean up the worktree. The user will instruct you to merge and remove the worktree when he is satisfied with the quality.

### Wrap Epic Guidance

**When the user asks to commit or merge this epic's work:**
- Ask: "Would you like to run `/wrap_epic {epic-id}` first? It captures undocumented decisions and lessons learned, generates an implementation summary, and updates architecture docs before committing."

**When the user runs `/implement` for a different epic while this one has an active worktree:**
- Step 0b checks for unwrapped epics and prompts the user (see above).

**Write tracking marker** so `/decision` and `/lesson` know when implementation completed:
```bash
mkdir -p .scope/tracking/commands
echo '{"command":"implement","epic_id":"'"$EPIC_ID"'","completed_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","stories_completed":{N},"audit_status":"'"$AUDIT_STATUS"'"}' >> ".scope/tracking/commands/implement-$(date +%Y%m%d-%H%M%S).jsonl"
```

---

## Task Dependency Diagram

For stories where Story 3 depends on Stories 1 and 2:

```
architect-story-00
       ↓
dev-story-01 ──────────┐
                        │
dev-story-02 ──────────┤
                        │
dev-story-03 ←─────────┘  (blocked by dev-01 AND dev-02)
       ↓
audit_epic (after all complete)
```

Developer tasks respect declared inter-story dependencies.

**Concurrency timeline (single developer agent, sequential):**
```
Time →
                    ┌─── Implementation Phase ──────────────────┐  ┌── Fix Phase ──────────────┐
architect:  [==story-0==][                                      ]  [==fix planning==]
developer:               [==story-1==][==story-2==][==story-3==]                    [==fix-08==][==fix-09==]
audit:                                                            [==audit==]                    [==final==]
tests:                                                                                           [==all==]
```

**Full flow:**
```
Stories 01-N → Audit → Fix stories (if needed) → All epic tests → Final audit
```

---

## Error Handling

**If a task fails:**
- The agent informs the orchestrator (ie.: this command) of the failure through TaskList
- Dependent tasks remain blocked
- The orchestrator (this command) detects the failure when checking TaskList
- Present failure to user with the agent's error message
- Ask: "Fix and retry? [yes / skip story / abort]"

**If developer can't pass tests:**
- Developer returns `status: failure` with details
- Common cause: file plan signatures don't match actual requirements
- Fix: update file plan, re-run developer for that story

---

## Compaction Survival

If context is summarized during implementation, the orchestrator MUST re-read these files to recover state — do NOT rely on memory:

1. **Task state**: `TaskList()` — shows which stories are pending/in_progress/completed
2. **Epic context**: `docs/epics/{EPIC_DIR}/` — all refinement artifacts
3. **Agent summaries**: `.scope/{EPIC_DIR}/agent_summaries.jsonl` — what agents have done
4. **Developer checklist**: `.claude/governance/developer-checklist.md` — MUST be re-read before any completion
5. **Lessons learned**: `docs/lessons-learned/INDEX.md` — project constraints
6. **System ADRs**: `docs/architecture/09-adr-summary.md` — architectural decisions

**Critical rule for spawning agents after compaction:** When re-launching a developer agent after context summarization, include the full agent launch prompt from Step 3 above — including the checklist file reference. Do NOT write a shortened version from memory.

---

## Communication Style

**Progress indicators:**
- "Implementing {epic-id}: Story 0/N complete"
- "Developer: Implementing story 1/N"

**After completion:**
- Summary of all stories implemented (original + fix)
- Audit results (initial + final)
- Fix stories created and their status
- Test results (all epic tests)
