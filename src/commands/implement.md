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

Instructions:
- Read the file plan at {story['file_plan_path']}
- Read acceptance criteria from docs/epics/{epic_dir}/acceptance-criteria.md
- Read architecture from docs/epics/{epic_dir}/architecture.md
- Read ADRs from docs/epics/{epic_dir}/adr.md
- Read test strategy from docs/epics/{epic_dir}/test-strategy.md
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
Implementation complete for {epic_id}.

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
- For each finding (critical, major, AND minor), create a fix story
- Group related findings into the same story when they affect the same files
- Include documentation update stories for docs/architecture/ changes if the audit
  found architectural divergence (update the relevant architecture docs to match
  what was actually implemented, or fix the code to match the architecture)
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

Instructions:
- This is a FIX story from audit findings
- Read the file plan at {story['file_plan_path']}
- Read the audit report at docs/epics/{epic_dir}/epic_audit.md for context
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
    Epic {epic_id} implementation complete.
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

### Step 10: Worktree Cleanup

After the final audit passes (or after presenting unresolved findings to the user), do not clean up the worktree. The user will instruct you to merge and remove the worktree when he is satisfied with the quality.

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

## Communication Style

**Progress indicators:**
- "Implementing {epic-id}: Story 0/N complete"
- "Developer: Implementing story 1/N"

**After completion:**
- Summary of all stories implemented (original + fix)
- Audit results (initial + final)
- Fix stories created and their status
- Test results (all epic tests)
