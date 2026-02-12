# Epic Tracking (File) - Test Prompts

Run each prompt independently to test the epic-tracking-file skill.

## Prerequisites

1. `.scope/config.yaml` configured for file-based tracking
2. Base path: `./tracking` (or as configured)

---

## create_epic

### Test 1: Create first epic
```
Using the epic-tracking-file skill, create an epic with:
- Title: "Test Epic Alpha"
- Description: "First test epic for validating SCOPE tracking"
- Priority: high

Return the display ID and folder path.
```

### Test 2: Create second epic
```
Using the epic-tracking-file skill, create an epic with:
- Title: "Test Epic Beta"
- Description: "Second test epic for validating SCOPE tracking"
- Priority: medium

Return the display ID and folder path.
```

---

## get_epic

### Test 3: Get epic details
```
Using the epic-tracking-file skill, get the details of epic 0001.
Show: title, description, status, priority.
```

---

## get_next_id

### Test 4: Check ID counter
```
Using the epic-tracking-file skill, show the current value in .counters/epic.id.
It should be "2" after creating 2 epics.
```

---

## transition_status (epic) - Full Workflow

### Test 5: Transition epic to refinement
```
Using the epic-tracking-file skill, transition epic 0001 to "refinement" status.
Show the contents of state.log to confirm.
```

### Test 6: Transition epic to implementation
```
Using the epic-tracking-file skill, transition epic 0001 to "implementation" status.
Show the contents of state.log to confirm progression: backlog → refinement → implementation.
```

### Test 7: Transition epic to deployment
```
Using the epic-tracking-file skill, transition epic 0001 to "deployment" status.
Show state.log now has 4 entries.
```

### Test 8: Transition epic to done
```
Using the epic-tracking-file skill, transition epic 0001 to "done" status.
Show complete state.log with all 5 states: backlog → refinement → implementation → deployment → done.
```

---

## create_story

### Test 9: Create first story for Epic 1
```
Using the epic-tracking-file skill, create a story under epic 0001:
- Title: "Story Alpha-1"
- Description: "First story in Test Epic Alpha"
- Acceptance Criteria: "Given valid input, when processed, then output is correct"

Return the display ID and folder path.
```

### Test 10: Create second story for Epic 1
```
Using the epic-tracking-file skill, create a story under epic 0001:
- Title: "Story Alpha-2"
- Description: "Second story in Test Epic Alpha"
- Acceptance Criteria: "Given error condition, when handled, then graceful failure"

Return the display ID and folder path.
```

### Test 11: Create first story for Epic 2
```
Using the epic-tracking-file skill, create a story under epic 0002:
- Title: "Story Beta-1"
- Description: "First story in Test Epic Beta"
- Acceptance Criteria: "Given user action, when completed, then state updates"

Return the display ID and folder path.
```

### Test 12: Create second story for Epic 2
```
Using the epic-tracking-file skill, create a story under epic 0002:
- Title: "Story Beta-2"
- Description: "Second story in Test Epic Beta"
- Acceptance Criteria: "Given concurrent access, when synchronized, then no conflicts"

Return the display ID and folder path.
```

---

## get_story

### Test 13: Get story details
```
Using the epic-tracking-file skill, get the details of story 0001.
Show: title, description, acceptance criteria, parent epic, status.
```

---

## get_stories_by_epic

### Test 14: List stories in epic
```
Using the epic-tracking-file skill, list all stories in epic 0001.
Show story ID, title, and status for each.
```

---

## transition_status (story) - Full Workflow

### Test 15: Transition story to in-progress
```
Using the epic-tracking-file skill, transition story 0001 to "in-progress" status.
Show the contents of state.log to confirm.
```

### Test 16: Transition story to review
```
Using the epic-tracking-file skill, transition story 0001 to "review" status.
Show state.log progression: backlog → in-progress → review.
```

### Test 17: Transition story to done
```
Using the epic-tracking-file skill, transition story 0001 to "done" status.
Show complete state.log with all 4 states: backlog → in-progress → review → done.
```

---

## get_status

### Test 18: Get current status
```
Using the epic-tracking-file skill, get the current status of story 0001.
Use: tail -1 state.log | cut -d' ' -f2
Expected: "done"
```

---

## create_bug

### Test 19: Create first bug
```
Using the epic-tracking-file skill, create a bug:
- Title: "Test Bug One"
- Description: "First test bug for validation"
- Severity: high
- Steps to Reproduce: "1. Open app\n2. Click button\n3. Observe error"

Return the display ID and folder path.
```

### Test 20: Create second bug
```
Using the epic-tracking-file skill, create a bug:
- Title: "Test Bug Two"
- Description: "Second test bug for validation"
- Severity: medium
- Steps to Reproduce: "1. Submit form\n2. Check response\n3. See incorrect data"

Return the display ID and folder path.
```

---

## get_bug

### Test 21: Get bug details
```
Using the epic-tracking-file skill, get the details of bug 0001.
Show: title, description, severity, status.
```

---

## transition_status (bug) - Full Workflow

### Test 22: Transition bug to investigating
```
Using the epic-tracking-file skill, transition bug 0001 to "investigating" status.
Show the contents of state.log to confirm.
```

### Test 23: Transition bug to fixing
```
Using the epic-tracking-file skill, transition bug 0001 to "fixing" status.
Show state.log progression: open → investigating → fixing.
```

### Test 24: Transition bug to verification
```
Using the epic-tracking-file skill, transition bug 0001 to "verification" status.
Show state.log now has 4 entries.
```

### Test 25: Transition bug to closed
```
Using the epic-tracking-file skill, transition bug 0001 to "closed" status.
Show complete state.log with all 5 states: open → investigating → fixing → verification → closed.
```

---

## list_epics

### Test 26: List all epics
```
Using the epic-tracking-file skill, list all epics.
Use: ls tracking/epics/
Show folder name and current status for each.
```

---

## list_bugs

### Test 27: List all bugs
```
Using the epic-tracking-file skill, list all bugs.
Show bug ID, title, and current status.
```

---

## add_comment

### Test 28: Add comment to epic
```
Using the epic-tracking-file skill, add a comment to epic 0001:
"Test comment added during SCOPE skill validation."

Show the contents of comments.log.
```

---

## reserve_ids

### Test 29: Reserve multiple story IDs
```
Using the epic-tracking-file skill, reserve 5 story IDs at once.
Show the starting ID returned and the new counter value.
```

---

## Cleanup

### Test 30: Verify file structure
```
Show the complete directory structure created during testing:
find tracking -type f | head -50
```

### Test 31: Delete test data (optional)
```
Remove all test data:
rm -rf tracking/epics/epic-0001-* tracking/epics/epic-0002-*
rm -rf tracking/bugs/bug-0001-* tracking/bugs/bug-0002-*
echo "0" > tracking/.counters/epic.id
echo "0" > tracking/.counters/story.id
echo "0" > tracking/.counters/bug.id
```

---

## Expected Results Summary

| Test | Operation | Expected |
|------|-----------|----------|
| 1-2 | create_epic | Folder created, issue.yaml written, state.log initialized |
| 3 | get_epic | Shows issue.yaml content + current status |
| 4 | get_next_id | Counter = 2 |
| 5-8 | epic state progression | backlog → refinement → implementation → deployment → done |
| 9-12 | create_story | Story folders under epic, counter increments |
| 13 | get_story | Shows story issue.yaml + status |
| 14 | get_stories_by_epic | Lists 2 stories |
| 15-17 | story state progression | backlog → in-progress → review → done |
| 18 | get_status | Returns "done" for story |
| 19-20 | create_bug | Bug folder in tracking/bugs/ |
| 21 | get_bug | Shows bug details |
| 22-25 | bug state progression | open → investigating → fixing → verification → closed |
| 26 | list_epics | Shows 2 epic folders |
| 27 | list_bugs | Shows 2 bug folders |
| 28 | add_comment | comments.log created/appended |
| 29 | reserve_ids | Returns starting ID, counter jumps by 5 |
