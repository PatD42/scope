---
name: implement
description: Implement an epic story-by-story using TDD. SDET writes tests first, then developer implements. Runs audit on completion.
args: "{epic-id}"
skills: project-documentation, project-tracking, session-id-finder
agents: architect, sdet, developer
---

# /implement

Implement an epic story-by-story using TDD orchestration. Alternative to Auto Claude — uses SCOPE agents (architect, sdet, developer) with task-based coordination.

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
  sdet-story-1 (blocked by architect-story-0 if exists)
    ↓
  dev-story-1 (blocked by sdet-story-1)

Story 2 (depends on Story 1):
  sdet-story-2 (blocked by sdet-story-1)  ← SDET is sequential
    ↓
  dev-story-2 (blocked by sdet-story-2 + dev-story-1)  ← dev waits for its SDET + story deps

Story N:
  sdet-story-N (blocked by sdet-story-(N-1))
    ↓
  dev-story-N (blocked by sdet-story-N + dev tasks of declared dependencies)

After all complete:
  /audit_epic {epic-id}
  Apply recommendations from epic_audit.md
```

**Key rules:**
- SDET tasks are **sequential** (no concurrent SDET — test design needs prior context)
- Developer tasks start when their SDET task AND all implementation dependencies complete
- **ONE developer agent at a time** — concurrent writes to the same worktree cause race conditions and inconsistent state
- The developer agent processes tasks sequentially, picking the lowest-ID unblocked dev task
- Story 0 (scaffolding) is done by the architect before any SDET/dev work

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

# Create .scope directory
mkdir -p ".scope/${EPIC_DIR}"
SUMMARIES_FILE=".scope/${EPIC_DIR}/implement_summaries.jsonl"

# Get session ID for cost tracking
SESSION_ID=$(skill session-id-finder)

# Write baseline entry
echo '{"agent":"baseline","phase":"implement","completed_at":"'"$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')"'"}' > "$SUMMARIES_FILE"
```

### Step 1: Discover Stories

```python
# Find all file-plan-story-*.yaml files
file_plans = Glob("docs/epics/{epic_dir}/file-plan-story-*.yaml")
file_plans.sort()  # Ensures story-00, story-01, story-02... order

# Parse story info from each file plan
stories = []
for plan_path in file_plans:
    plan_content = Read(plan_path)
    plan = read_yaml(plan_path)
    story_num = extract_story_number(plan_path)  # "00", "01", etc.

    # Parse dependency comment: "# Dependencies: Stories 01a, 01b, 02"
    dep_line = [l for l in plan_content.split('\n') if l.startswith('# Dependencies:')]
    story_deps = parse_story_refs(dep_line)  # Returns ["01a", "01b", "02", ...]

    stories.append({
        "number": story_num,
        "story_id": plan["story_id"],
        "story_title": plan["story_title"],
        "file_plan_path": plan_path,
        "dependencies": story_deps,
        "is_scaffolding": story_num == "00"
    })

has_story_0 = stories[0]["is_scaffolding"] if stories else False
```

### Step 2: Create Tasks

Create all tasks upfront with dependencies, then launch agents.

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
agent_summaries: {summaries_file}
terminate_upon_completion: no

Instructions:
- Read the file plan at {story_0['file_plan_path']}
- Create all directories, modules, config files, and base classes listed
- Do NOT implement business logic — only scaffolding
- Verify the skeleton compiles/imports correctly
""",
        activeForm="Implementing scaffolding"
    )

# --- For each implementation story ---
impl_stories = [s for s in stories if not s["is_scaffolding"]]
prev_sdet_task_id = None

for story in impl_stories:
    num = story["number"]

    # SDET task: write tests first
    sdet_blocked_by = []
    if prev_sdet_task_id:
        sdet_blocked_by.append(prev_sdet_task_id)
    if has_story_0 and not prev_sdet_task_id:
        # First SDET task depends on scaffolding
        sdet_blocked_by.append(task_ids["architect-story-00"])

    sdet_task_id = TaskCreate(
        subject=f"sdet: Write tests for story {num} - {story['story_title']}",
        description=f"""
epic_id: {epic_id}
phase: test_writing
story_id: {story['story_id']}
story_title: {story['story_title']}
file_plan: {story['file_plan_path']}
agent_summaries: {summaries_file}
terminate_upon_completion: no

Instructions:
- Read the file plan at {story['file_plan_path']}
- Read acceptance criteria from docs/epics/{epic_dir}/acceptance-criteria.md
- Read test strategy from docs/epics/{epic_dir}/test-strategy.md
- Write tests BEFORE implementation (TDD)
- Use public_interface from file plan to write tests against expected signatures
- Use signature_changes to write backward compatibility tests where needed
- Include unit tests for all new/modified files
- Include integration tests if story completes a component integration
- Include e2e tests if story completes a user flow
- All tests should FAIL at this point (no implementation yet)
""",
        activeForm=f"Writing tests for story {num}"
    )
    task_ids[f"sdet-story-{num}"] = sdet_task_id

    # Developer task: implement to pass tests
    dev_task_id = TaskCreate(
        subject=f"developer: Implement story {num} - {story['story_title']}",
        description=f"""
epic_id: {epic_id}
phase: implementation
story_id: {story['story_id']}
story_title: {story['story_title']}
file_plan: {story['file_plan_path']}
agent_summaries: {summaries_file}
terminate_upon_completion: no

Instructions:
- Read the file plan at {story['file_plan_path']}
- Read architecture from docs/epics/{epic_dir}/architecture.md
- Read ADRs from docs/epics/{epic_dir}/adr.md
- Implement PRODUCTION-READY code that fulfills the file plan intent
- Follow the intent documentation in the file plan — intent is the source of truth
- Match the public_interface / signature_changes exactly
- Run tests after implementation — all must pass
- Do NOT modify test files (only implementation files)
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

    # Wire dependencies: sdet blocked by prev sdet, dev blocked by its sdet
    if sdet_blocked_by:
        TaskUpdate(taskId=sdet_task_id, addBlockedBy=sdet_blocked_by)
    TaskUpdate(taskId=dev_task_id, addBlockedBy=[sdet_task_id])

    prev_sdet_task_id = sdet_task_id

# --- Second pass: wire inter-story implementation dependencies ---
# dev-story-N is also blocked by dev tasks of its declared dependencies
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
# Spawn agents using Task tool — all in ONE message for parallel execution

# 1. Architect (if Story 0 exists)
if has_story_0:
    Task(
        prompt="Take the role of architect agent. Find and execute your scaffolding task.",
        subagent_type="general-purpose",
        description="Architect: scaffolding",
        run_in_background=True
    )

# 2. SDET agent (sequential — one agent handles all SDET tasks via polling)
Task(
    prompt="Take the role of sdet agent. Find and execute your tasks in order. Poll for new tasks after completing each one.",
    subagent_type="general-purpose",
    description="SDET: write tests",
    run_in_background=True
)

# 3. Developer agent — SINGLE agent, sequential execution
# 🚨 NEVER spawn more than ONE developer agent. Multiple developers writing to
#    the same worktree causes race conditions, merge conflicts, and corrupted state.
#    If you need to re-launch after failure, wait for the current one to finish first.
Task(
    prompt="""Take the role of developer agent.
    Process dev tasks ONE AT A TIME in dependency order:
    1. Check TaskList for the lowest-ID dev task that is pending and has NO blockedBy
    2. If none available, STOP — you will be re-launched when tasks unblock
    3. Implement it, run tests
    4. Mark completed
    5. Check TaskList again for next unblocked dev task
    6. Repeat until no more dev tasks available

    CRITICAL: Only work on tasks where ALL blockedBy tasks show status=completed.""",
    subagent_type="general-purpose",
    description="Developer: implement",
    run_in_background=True
)
```

**Tell user:**
```
Implementing {epic-id} with {N} stories:

🏗️ Architect: Story 0 scaffolding (if applicable)
🧪 SDET: Writing tests sequentially (story 1 → 2 → ... → N)
💻 Developer: Implementing as tests become available

Agents are working. I'll run the audit when they complete.
```

### Step 4: Wait for Completion

**STOP after spawning agents.** Wait for all background tasks to complete.

When all tasks are done (all marked `completed` in TaskList):

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

{If critical or major issues exist:}
Applying fix recommendations from epic_audit.md...
"""

# Apply fixes from audit
if audit.has_critical_or_major:
    # Read fix plan from audit
    fix_plan = extract_fix_plan(audit)

    for fix in fix_plan.priority_1 + fix_plan.priority_2:
        # Apply each fix
        apply_fix(fix)

    # Re-run audit to verify
    Skill(skill="audit_epic", args=epic_id)
```

### Step 6: Run All Epic Tests

After fixes are applied (or immediately after audit if no fixes needed), run all tests created/modified during this epic.

```python
# Collect all test files from file plans
test_files = []
for plan_path in file_plans:
    plan = read_yaml(plan_path)
    for f in plan.get("files_to_create", []) + plan.get("files_to_modify", []):
        if "/tests/" in f["path"] or f["path"].endswith(".test.ts") or f["path"].endswith("_test.py"):
            test_files.append(f["path"])

# Run all epic tests
Bash(f"run_tests {' '.join(test_files)}")  # Adapt to project test runner

# Present results
if all_passed:
    Output: f"""
    All {len(test_files)} test files pass.
    Epic {epic_id} implementation complete.
    """
else:
    Output: f"""
    {failed_count} test failures detected after audit fixes.
    Failing tests: {failing_tests}

    Investigating failures...
    """
    # Debug and fix remaining failures
    # Re-run tests until all pass or escalate to user
```

---

## Task Dependency Diagram

For stories where Story 3 depends on Stories 1 and 2:

```
architect-story-00
       ↓
sdet-story-01 ──→ dev-story-01 ──────────┐
       ↓                                  │
sdet-story-02 ──→ dev-story-02 ──────────┤
       ↓                                  │
sdet-story-03 ──→ dev-story-03 ←─────────┘  (blocked by dev-01 AND dev-02)
                        ↓
                 audit_epic (after all complete)
```

Developer tasks respect BOTH:
1. Their SDET task (tests must exist first)
2. Their story's implementation dependencies (imported code must exist)

**Concurrency timeline (single developer agent, sequential):**
```
Time →
architect:  [====story-0====]
sdet:                        [====story-1====][====story-2====][====story-3====]
developer:                                    [====story-1====][====story-2====][====story-3====]
```

Note: Developer processes tasks one at a time. A dev task only starts when both its SDET task AND all declared story dependencies (other dev tasks) are complete. This prevents concurrent writes to the same worktree.

---

## Error Handling

**If a task fails:**
- The agent writes `status: failure` in agent_summaries
- Dependent tasks remain blocked
- The orchestrator (this command) detects the failure when checking TaskList
- Present failure to user with the agent's error message
- Ask: "Fix and retry? [yes / skip story / abort]"

**If SDET tests can't be written (missing context):**
- SDET returns `status: user_input` with questions
- Orchestrator pauses and presents questions to user
- After user answers, SDET resumes

**If developer can't pass tests:**
- Developer returns `status: failure` with details
- Common cause: file plan signatures don't match actual requirements
- Fix: update file plan, re-run SDET + developer for that story

---

## Compaction Survival

If session compacts mid-implementation:

1. Check `.scope/{epic-dir}/implement_summaries.jsonl` for completed phases
2. Check TaskList for task statuses:
   - All `completed` → proceed to audit
   - Some `in_progress` → wait for agents
   - Some `pending` with no `in_progress` → agents may have died, re-launch
3. Resume from appropriate point

---

## Communication Style

**Progress indicators:**
- "Implementing {epic-id}: Story 0/N complete"
- "SDET: Writing tests for story 2/N"
- "Developer: Implementing story 1/N"

**After completion:**
- Summary of all stories implemented
- Audit results
- Cost breakdown

---

## Cost Tracking

```bash
# After all agents complete, aggregate costs
SCRIPT=$(find ./.claude/commands/scripts ~/.claude/commands/scripts -name "agents-tokens.sh" 2>/dev/null | head -1)
if [ -n "$SCRIPT" ]; then
    $SCRIPT --aggregate "$SUMMARIES_FILE" --storeInSummaries
fi
```
