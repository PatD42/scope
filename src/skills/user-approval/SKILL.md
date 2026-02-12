---
name: user-approval
description: Handles user approval flow with preapproval modes and block-and-continue support
---

# User Approval Skill

Provides consistent approval behavior across agents with support for preapproval modes.

## Preapproval File

Location: `.scope/{epic-dir}-preapproval.yaml`

```yaml
preapproved: minor
```

**Modes:**
- `none` - Always ask for approval
- `minor` - Auto-approve if work_impact is `none` or `minor`
- `all` - Auto-approve everything
- `all until X` - Auto-approve if current task ID < X (task X requires approval)

## Usage

When agent phase requires approval:

### Step 1: Read Preapproval

```bash
# Get epic directory from context
epic_dir = "{project-key}-{id}-{slug}"
preapproval_file = ".scope/${epic_dir}-preapproval.yaml"

# Read current mode
if file_exists(preapproval_file):
    mode = read_yaml(preapproval_file).preapproved
else:
    mode = "none"  # default if file missing
```

### Step 2: Check Auto-Approval

```python
work_impact = "{from phase result}"  # none | minor | major
current_task_id = "{from TaskList}"

def is_auto_approved(mode, work_impact, current_task_id):
    if mode == "none":
        return False
    if mode == "minor":
        return work_impact in ["none", "minor"]
    if mode == "all":
        return True
    if mode.startswith("all until "):
        threshold = int(mode.split()[-1])
        return int(current_task_id) < threshold
    return False
```

### Step 3: If Auto-Approved

```
Print to console:
  "✓ Auto-approved (preapproval: {mode}, work_impact: {work_impact})"

Log to agent_summaries.jsonl:
  {
    "approval": "auto",
    "mode": "{mode}",
    "work_impact": "{work_impact}",
    "task_id": "{current_task_id}"
  }

Return: approved
```

### Step 4: If Approval Required

Ask user for approval. User may:
- **Approve**: Clear affirmative response
- **Request changes**: Agent follows instructions, then asks again
- **Ask questions**: Agent answers, then asks again
- **Block and continue**: Agent blocks story and moves on

**Clear approval responses** (case-insensitive):
- approved, approve, yes, ok, good, let's go, move on, continue
- looks good, all good, lgtm, ship it, awesome, you rock, nice, great

**Block and continue responses**:
- block and continue, block and move on
- set to blocked, mark as blocked
- implementation-blocked, refinement-blocked

### Step 5: Handle Block and Continue

When user requests block:

```python
# Determine block status based on current phase
if phase in ["test_implementation", "implementation", "code_review"]:
    block_status = "implementation-blocked"
else:
    block_status = "refinement-blocked"

# Update story status via project-tracking skill
transition_story(story_id, block_status)

# Log to agent summary
{
    "approval": "blocked",
    "block_status": "{block_status}",
    "reason": "{user's reason if provided}",
    "task_id": "{current_task_id}"
}

# Print to console
"⚠️ Story {story_id} set to {block_status}. Continuing to next task."

# Mark task as complete (pipeline continues)
Return: blocked (treated as complete for workflow purposes)
```

## Agent Integration

Agents with approval phases should:

1. Complete phase work
2. Call this skill's approval flow
3. Handle result:
   - `approved` → mark task complete, continue
   - `blocked` → mark task complete, pipeline continues to next story
   - `rejected` → mark task failed (rare, user usually blocks instead)

## Example Flow

```
Agent: I've written 5 test files for SCOPE-43.

       Test coverage:
       - Unit tests for ReviewService
       - Integration tests for API endpoints
       - E2E test for review submission flow

       Ready for your review. Approve to continue?

User: Can you add a test for the edge case where review text is empty?

Agent: Added empty review text test case.

       Updated test coverage:
       - Unit tests for ReviewService (including empty text edge case)
       - Integration tests for API endpoints
       - E2E test for review submission flow

       Approve to continue?

User: looks good

Agent: ✓ Approved. Marking task complete.
```

## Example Block Flow

```
Agent: I've implemented the review API endpoint.

       Changes:
       - src/api/reviews/routes.py (new)
       - src/api/reviews/service.py (new)
       - 3 tests passing

       Approve to continue?

User: There's a security concern with the input validation.
      Block this and continue - I'll file a separate issue.

Agent: ⚠️ Story SCOPE-43 set to implementation-blocked.
       Reason: Security concern with input validation.
       Continuing to next task.
```
