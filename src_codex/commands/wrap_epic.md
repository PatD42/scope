---
name: wrap_epic
description: Wrap up an epic — capture decisions, lessons learned, update documentation, sync to Obsidian, commit and merge.
args: "{epic-id}"
skills: project-documentation, session-id-finder
---

# /wrap_epic

Close out an epic by capturing all outstanding decisions and lessons, updating documentation to reflect what actually happened, and committing the result.

**Syntax:** `/wrap_epic {epic-id}`

This is the natural end-of-epic routine. In most cases, the user just runs `/wrap_epic` after testing and the agent handles the rest.

---

## Workflow Overview

```
┌──────────────────────────────────────────────────────┐
│ Step 1: Verify epic is ready to wrap                 │
│ - All stories implemented                            │
│ - Tests passing                                      │
│ - Audit completed (or not needed)                    │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Step 2: /decision (auto-detect mode)                 │
│ - Scan for undocumented decisions since /implement   │
│ - Present candidates for discussion and approval     │
│ → USER REVIEWS AND APPROVES DECISIONS                │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Step 3: /lesson (auto-detect mode)                   │
│ - Scan for lessons from test failures, retries,      │
│   workarounds, corrections                           │
│ - Present candidates for discussion and approval     │
│ → USER REVIEWS AND APPROVES LESSONS                  │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Step 4: Generate implementation summary              │
│ - Diff plan vs. reality                              │
│ - Per-story outcomes                                  │
│ - Deviations and unplanned changes                   │
│ → USER REVIEWS SUMMARY                               │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Step 5: Update product-level documentation           │
│ - Roll up ADRs to 09-adr-summary.md                  │
│ - Roll up PDRs to product/decisions.md               │
│ - Update architecture docs if components changed     │
│ - Update operations docs if infra changed            │
│ → USER REVIEWS DOC UPDATES                           │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Step 6: Sync to external systems                     │
│ - Obsidian vault (if MCP available)                  │
│ - Project tracking (if configured)                   │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Step 7: Commit and merge                             │
│ - Stage documentation + code changes                 │
│ - Commit with epic merge message                     │
│ - Move epic folder to _implemented/                  │
│ → USER CONFIRMS BEFORE MERGE                         │
└──────────────────────────────────────────────────────┘
```

---

## Execution

### Step 0: Initialize

```python
EPIC_ID = "{epic-id}"

# Codex/Scope path convention:
# - wrap_epic may be invoked from the main project root or from ./wip/{epic-id}
# - implementation work is committed from the worktree
# - final merge and root CodeGraph sync happen from the main project root
current_dir = Bash("pwd").strip()
if "/wip/" in current_dir:
    PROJECT_ROOT = current_dir.split("/wip/")[0]
    WORKTREE_DIR = current_dir
else:
    PROJECT_ROOT = current_dir
    WORKTREE_DIR = f"{PROJECT_ROOT}/wip/{EPIC_ID}"

BRANCH_NAME = f"epic/{EPIC_ID}"

# Find epic directory
epic_dirs = Glob(f"docs/epics/{EPIC_ID}*/details.md")
# Exclude _implemented/ and _deferred_superseded/
epic_dirs = [d for d in epic_dirs if "/_" not in d]

if not epic_dirs:
    print(f"Epic {EPIC_ID} not found in docs/epics/")
    exit(1)

EPIC_DIR = epic_dirs[0].split("/")[-2]
SCOPE_DIR = f".scope/{EPIC_DIR}"
SUMMARIES = f"{SCOPE_DIR}/agent_summaries.jsonl"
```

---

### Step 1: Verify Epic Is Ready

Check prerequisites:

```python
# Required files
assert exists(f"docs/epics/{EPIC_DIR}/acceptance-criteria.md"), "Missing acceptance criteria"
assert exists(f"docs/epics/{EPIC_DIR}/architecture.md"), "Missing architecture"

# Check agent summaries for completion
summaries = Read(SUMMARIES)
# All stories should have status: success or the last audit should be clean

# Check tests pass
print("Verify: Are all tests passing for this epic? [yes / no / skip]")
```

If tests aren't passing or stories are incomplete, warn but allow the user to proceed (they may be wrapping a partial epic intentionally).

---

### Step 2: Capture Decisions

Execute `/decision` in auto-detect mode (no args):

**Context to provide:**
- Epic ID and directory for scoping the search
- Agent summaries file for this epic

**Time window:** `/decision` determines its own time window from tracking markers. If no markers exist (first run, compaction, fresh session), it scans the full epic history and filters out already-recorded decisions.

```
Capturing decisions for {EPIC_ID}...

Running /decision (auto-detect mode) — scanning for undocumented
architectural and product decisions.
```

Follow the full `/decision` auto-detect flow:
1. Scan git history, agent summaries, code changes
2. Present candidates (excluding already-recorded decisions)
3. User reviews, edits, approves
4. Save approved decisions

If no decisions detected: "No undocumented decisions found. Moving on."

---

### Step 3: Capture Lessons

Execute `/lesson` in auto-detect mode (no args):

**Context to provide:**
- Same epic scope as Step 2
- `/lesson` determines its own time window from tracking markers (same fallback: full epic history if no markers exist)

```
Capturing lessons learned for {EPIC_ID}...

Running /lesson (auto-detect mode) — scanning for patterns,
anti-patterns, and hard-won knowledge from this epic.
```

Follow the full `/lesson` auto-detect flow:
1. Scan agent summaries for failures/retries, git for fix patterns, audit findings
2. Present candidates
3. User reviews, edits, approves
4. Save approved lessons

If no lessons detected: "No lessons identified. Moving on."

---

### Step 4: Generate Implementation Summary

Create `docs/epics/{EPIC_DIR}/implementation-summary.md`:

#### 4.1: Diff Plan vs. Reality

```python
# Load file plans
file_plans = Glob(f"docs/epics/{EPIC_DIR}/file-plan-story-*.yaml")

# Load agent summaries for actual changes
summaries = Read(SUMMARIES)

# Load git changes attributed to this epic
git_changes = Bash(f"git log --name-only --pretty=format:'%s' -- . | head -200")
```

Compare:
- **Planned files** (from file plans) vs. **actual files changed** (from git/summaries)
- **Planned stories** vs. **completed stories** (from agent summaries)
- **Unplanned modifications** (from agent summaries — `unplanned_modifications` field)

#### 4.2: Write Summary

```markdown
# Implementation Summary: {EPIC_ID}

**Completed:** {date}
**Stories:** {N planned} planned, {M completed} completed, {K skipped} skipped
**Duration:** {first commit} to {last commit}

## Per-Story Outcomes

### Story 0: {Title}
- **Status:** {Complete | Partial | Skipped}
- **Files:** {N created}, {M modified}
- **Notes:** {any deviations or issues}

### Story 1: {Title}
...

## Deviations from Plan

| Planned | Actual | Reason |
|---------|--------|--------|
| {planned file/approach} | {what actually happened} | {why it changed} |

## Unplanned Changes

| File | Change | Justification |
|------|--------|---------------|
| {file} | {what changed} | {why — from agent summaries} |

## Decisions Made During Implementation

{List ADRs/PDRs recorded in Step 2, with links}

## Lessons Learned

{List lessons recorded in Step 3, with links}

## Acceptance Criteria Status

| AC | Status | Notes |
|----|--------|-------|
| {criterion} | {Met | Partial | Not Met} | {explanation if not met} |
```

Present to user for review: "Here's the implementation summary. Anything to correct or add?"

---

### Step 5: Update Product-Level Documentation

#### 5.1: Roll Up ADRs

Read `docs/epics/{EPIC_DIR}/adr.md` and update `docs/architecture/09-adr-summary.md`:

```python
# Read epic ADRs
epic_adrs = Read(f"docs/epics/{EPIC_DIR}/adr.md")

# Append summaries to 09-adr-summary.md under appropriate scope sections
# Format per SKILL.md:
# ## Backend ADRs
# - [ADR-037: Queue Strategy](backend/adr/ADR-037-queue-strategy.md) — Accepted, 2026-02-16
```

Also create individual ADR files in `docs/architecture/adr/`, `backend/adr/`, or `frontend/adr/` if the epic ADRs are significant enough for system-level documentation.

#### 5.2: Roll Up PDRs

Read `docs/epics/{EPIC_DIR}/pdr.md` (if exists) and update `docs/product/decisions.md`:

```python
# Append product decisions with link to epic source
```

#### 5.3: Update Architecture Docs (If Changed)

Check if the epic's implementation changed architecture-level components:

```python
# Did the epic add new services?
if new_service_added:
    print("Epic added new service(s). Update docs/architecture/backend/services.md? [yes/no]")

# Did schema change?
if schema_changed:
    print("Database schema changed. Update docs/architecture/backend/data.md? [yes/no]")

# Did deployment change?
if deployment_changed:
    print("Deployment config changed. Update docs/architecture/07-deployment.md? [yes/no]")

# Did new cross-cutting patterns emerge?
if new_patterns:
    print("New patterns introduced. Update docs/architecture/08-cross-cutting/? [yes/no]")
```

For each "yes", read the current doc and the epic's changes, then update the doc. Present updates for user review.

#### 5.4: Update Operations Docs (If Changed)

```python
# Did deployment process change?
if ci_cd_changed or dockerfile_changed:
    print("Deployment process changed. Update docs/operations/runbooks/deployment.md? [yes/no]")

# Did new secrets/config get added?
if new_secrets:
    print("New secrets added. Update docs/operations/runbooks/secrets-management.md? [yes/no]")

# Did infra change?
if infra_changed:
    print("Infrastructure changed. Update docs/operations/environments.md? [yes/no]")
```

#### 5.5: Update Building Blocks

```python
# Always update 05-building-blocks.md with link to epic architecture
building_blocks = Read("docs/architecture/05-building-blocks.md")
# Append summary of components added/changed by this epic
```

---

### Step 6: Sync to External Systems

#### 6.1: Obsidian (if MCP available)

```python
if mcp_available("obsidian"):
    # Sync decisions
    for decision in approved_decisions:
        obsidian.write(f"decisions/{decision.id}-{decision.slug}.md", decision.content)

    # Sync lessons
    for lesson in approved_lessons:
        obsidian.write(f"lessons-learned/{lesson.id}-{lesson.slug}.md", lesson.content)

    # Sync implementation summary
    obsidian.write(
        f"epics/{EPIC_ID}/implementation-summary.md",
        implementation_summary
    )

    print(f"Synced to Obsidian vault: {len(approved_decisions)} decisions, {len(approved_lessons)} lessons")
```

#### 6.2: Project Tracking (if configured)

```python
# Read .scope/config.yaml for tracking backend
config = Read(".scope/config.yaml")

if config.get("tracking", {}).get("backend"):
    # Transition epic to "done" / "closed"
    Skill(skill="project-tracking", args=f"transition_epic {EPIC_ID} done")
```

---

### Step 7: Commit and Merge

Run Step 7.1 through Step 7.5 from the active epic worktree when it exists:

```bash
PROJECT_ROOT="${PROJECT_ROOT}"
WORKTREE_DIR="${WORKTREE_DIR}"
BRANCH_NAME="epic/${EPIC_ID}"

if [ -d "$WORKTREE_DIR" ]; then
  cd "$WORKTREE_DIR"
fi
```

#### 7.1: Stage Changes

```bash
# Show what will be committed
git status

# Stage documentation updates
git add docs/epics/{EPIC_DIR}/implementation-summary.md
git add docs/epics/{EPIC_DIR}/adr.md
git add docs/epics/{EPIC_DIR}/pdr.md
git add docs/architecture/09-adr-summary.md
git add docs/product/decisions.md
git add docs/lessons-learned/

# Stage any architecture/operations doc updates from Step 5
# (list specific files that were updated)
```

Present to user:
```
Ready to commit the following changes:

Documentation:
  - docs/epics/{EPIC_DIR}/implementation-summary.md (new)
  - docs/architecture/09-adr-summary.md (updated with N ADRs)
  - docs/product/decisions.md (updated with N PDRs)
  - docs/lessons-learned/ (N new lessons)
  - {any architecture/operations docs updated}

Code:
  {list code files if any are unstaged}

Commit message:
  wrap({EPIC_ID}): implementation summary, decisions, lessons learned

  - {N} ADRs rolled up to architecture summary
  - {N} PDRs rolled up to product decisions
  - {N} lessons learned recorded
  - Implementation summary with plan vs. reality diff

Proceed? [commit / edit message / cancel]
```

#### 7.2: Commit

```bash
git commit -m "$(cat <<'EOF'
wrap({EPIC_ID}): implementation summary, decisions, lessons learned

- {N} ADRs rolled up to architecture summary
- {N} PDRs rolled up to product decisions
- {N} lessons learned recorded
- Implementation summary with plan vs. reality diff
EOF
)"
```

#### 7.3: Move Epic to _implemented/

```bash
mkdir -p docs/epics/_implemented/
mv docs/epics/{EPIC_DIR} docs/epics/_implemented/{EPIC_DIR}
git add docs/epics/
git commit -m "wrap({EPIC_ID}): move to _implemented"
```

#### 7.4: Write Tracking Marker

```bash
mkdir -p .scope/tracking/commands
echo '{"command":"wrap_epic","epic_id":"'"$EPIC_ID"'","completed_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","decisions_recorded":{D},"lessons_recorded":{L},"docs_updated":[...]}' >> ".scope/tracking/commands/wrap_epic-$(date +%Y%m%d-%H%M%S).jsonl"
git add .scope/tracking/commands/
git commit -m "wrap({EPIC_ID}): record wrap marker"
```

#### 7.5: Merge Worktree Branch to Main Project Root

Ask for explicit user confirmation before merging:

```
Ready to merge branch epic/{EPIC_ID} into the main project root.

Project root: {PROJECT_ROOT}
Worktree:     {WORKTREE_DIR}
Branch:       epic/{EPIC_ID}

Proceed? [merge / cancel]
```

Then merge from the main project root:

```bash
cd "$PROJECT_ROOT"

# Ensure the root working tree is clean enough for merge.
git status

# Merge the completed epic branch.
git merge --no-ff "$BRANCH_NAME" -m "merge({EPIC_ID}): complete epic"
```

#### 7.6: Return to Project Root and Sync CodeGraph

After a successful merge, the current working directory must be the main project root again. Sync the root CodeGraph DB so future refinement and planning see the merged code:

```bash
cd "$PROJECT_ROOT"

if [ ! -d ".codegraph" ]; then
  codegraph init .
fi

codegraph sync-if-dirty . || codegraph sync .
codegraph status .
```

---

### Completion

```
Epic {EPIC_ID} wrapped.

  Decisions:   {D} recorded (ADRs: {A}, PDRs: {P})
  Lessons:     {L} recorded ({C} critical, {I} important, {N} informational)
  Docs updated: {list of updated architecture/operations docs}
  Summary:     docs/epics/_implemented/{EPIC_DIR}/implementation-summary.md
  Obsidian:    {synced / not configured}
  Tracking:    {updated / not configured}
  Commits:     {N} commits created and merged to main project root
  CodeGraph:   root index synced

Epic moved to docs/epics/_implemented/{EPIC_DIR}
```

---

## Running Steps Independently

Each step can be run independently:

- `/decision` — just capture decisions (any time)
- `/lesson` — just capture lessons (any time)
- `/wrap_epic {epic-id}` — full wrap routine

The user doesn't have to wait for `/wrap_epic` to record decisions or lessons. They can use `/decision` and `/lesson` throughout development, and `/wrap_epic` will detect what's already been recorded and skip duplicates.

---

## Key Principles

1. **User approves everything** — no silent doc updates. Every decision, lesson, and doc change is presented for review.
2. **Best-effort auto-detect** — scanning is heuristic. The user can always add what was missed.
3. **Lightweight** — the whole wrap should take 15-30 minutes, not hours. Most time is user review, not agent work.
4. **Idempotent** — running `/wrap_epic` twice won't duplicate entries. It checks for existing records.
5. **Graceful without MCP** — Obsidian sync is optional. The repo-based docs are always the primary record.
