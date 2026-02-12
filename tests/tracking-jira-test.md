# Epic Tracking (Jira) - Test Prompts

Run each prompt independently to test the epic-tracking-jira skill.

## Prerequisites

1. `.scope/config.yaml` configured for Jira
2. Atlassian MCP authenticated
3. Test project exists in Jira

---

## create_epic

### Test 1: Create first epic
```
Using the epic-tracking-jira skill, create an epic with:
- Title: "Test Epic Alpha"
- Description: "First test epic for validating SCOPE tracking"
- Priority: high

Return the epic key.
```

### Test 2: Create second epic
```
Using the epic-tracking-jira skill, create an epic with:
- Title: "Test Epic Beta"
- Description: "Second test epic for validating SCOPE tracking"
- Priority: medium

Return the epic key.
```

---

## get_epic

### Test 3: Get epic details
```
Using the epic-tracking-jira skill, get the details of epic {EPIC-1-KEY}.
Show: title, description, status, priority.
```

---

## transition_status (epic) - Full Workflow

### Test 4: Transition epic to Refinement
```
Using the epic-tracking-jira skill, transition epic {EPIC-1-KEY} to "Refinement" status.
Confirm the new status.
```

### Test 5: Transition epic to Implementation
```
Using the epic-tracking-jira skill, transition epic {EPIC-1-KEY} to "Implementation" status.
Confirm progression: Backlog → Refinement → Implementation.
```

### Test 6: Transition epic to Deployment
```
Using the epic-tracking-jira skill, transition epic {EPIC-1-KEY} to "Deployment" status.
Confirm the new status.
```

### Test 7: Transition epic to Done
```
Using the epic-tracking-jira skill, transition epic {EPIC-1-KEY} to "Done" status.
Confirm complete workflow: Backlog → Refinement → Implementation → Deployment → Done.
```

---

## create_story

### Test 8: Create first story for Epic 1
```
Using the epic-tracking-jira skill, create a story under epic {EPIC-1-KEY}:
- Title: "Story Alpha-1"
- Description: "First story in Test Epic Alpha"
- Acceptance Criteria: "Given valid input, when processed, then output is correct"

Return the story key.
```

### Test 9: Create second story for Epic 1
```
Using the epic-tracking-jira skill, create a story under epic {EPIC-1-KEY}:
- Title: "Story Alpha-2"
- Description: "Second story in Test Epic Alpha"
- Acceptance Criteria: "Given error condition, when handled, then graceful failure"

Return the story key.
```

### Test 10: Create first story for Epic 2
```
Using the epic-tracking-jira skill, create a story under epic {EPIC-2-KEY}:
- Title: "Story Beta-1"
- Description: "First story in Test Epic Beta"
- Acceptance Criteria: "Given user action, when completed, then state updates"

Return the story key.
```

### Test 11: Create second story for Epic 2
```
Using the epic-tracking-jira skill, create a story under epic {EPIC-2-KEY}:
- Title: "Story Beta-2"
- Description: "Second story in Test Epic Beta"
- Acceptance Criteria: "Given concurrent access, when synchronized, then no conflicts"

Return the story key.
```

---

## get_story

### Test 12: Get story details
```
Using the epic-tracking-jira skill, get the details of story {STORY-1-KEY}.
Show: title, description, acceptance criteria, parent epic, status.
```

---

## get_stories_by_epic

### Test 13: List stories in epic
```
Using the epic-tracking-jira skill, list all stories in epic {EPIC-1-KEY}.
Show story key and status for each.
```

---

## transition_status (story) - Full Workflow

### Test 14: Transition story to In Progress
```
Using the epic-tracking-jira skill, transition story {STORY-1-KEY} to "In Progress" status.
Confirm the new status.
```

### Test 15: Transition story to Review
```
Using the epic-tracking-jira skill, transition story {STORY-1-KEY} to "Review" status.
Confirm progression: Backlog → In Progress → Review.
```

### Test 16: Transition story to Done
```
Using the epic-tracking-jira skill, transition story {STORY-1-KEY} to "Done" status.
Confirm complete workflow: Backlog → In Progress → Review → Done.
```

---

## create_bug

### Test 17: Create first bug
```
Using the epic-tracking-jira skill, create a bug:
- Title: "Test Bug One"
- Description: "First test bug for validation"
- Severity: high
- Steps to Reproduce: "1. Open app\n2. Click button\n3. Observe error"

Return the bug key.
```

### Test 18: Create second bug
```
Using the epic-tracking-jira skill, create a bug:
- Title: "Test Bug Two"
- Description: "Second test bug for validation"
- Severity: medium
- Steps to Reproduce: "1. Submit form\n2. Check response\n3. See incorrect data"

Return the bug key.
```

---

## get_bug

### Test 19: Get bug details
```
Using the epic-tracking-jira skill, get the details of bug {BUG-1-KEY}.
Show: title, description, severity, status.
```

---

## transition_status (bug) - Full Workflow

### Test 20: Transition bug to Investigating
```
Using the epic-tracking-jira skill, transition bug {BUG-1-KEY} to "Investigating" status.
Confirm the new status.
```

### Test 21: Transition bug to Fixing
```
Using the epic-tracking-jira skill, transition bug {BUG-1-KEY} to "Fixing" status.
Confirm progression: Open → Investigating → Fixing.
```

### Test 22: Transition bug to Verification
```
Using the epic-tracking-jira skill, transition bug {BUG-1-KEY} to "Verification" status.
Confirm the new status.
```

### Test 23: Transition bug to Closed
```
Using the epic-tracking-jira skill, transition bug {BUG-1-KEY} to "Closed" status.
Confirm complete workflow: Open → Investigating → Fixing → Verification → Closed.
```

---

## add_comment

### Test 24: Add comment to epic
```
Using the epic-tracking-jira skill, add a comment to epic {EPIC-1-KEY}:
"Test comment added during SCOPE skill validation."
```

### Test 25: Add comment to story
```
Using the epic-tracking-jira skill, add a comment to story {STORY-1-KEY}:
"Implementation notes: Using standard pattern."
```

---

## list_epics

### Test 26: List all epics
```
Using the epic-tracking-jira skill, list all epics in the project.
Show epic key, title, and status.
```

---

## list_bugs

### Test 27: List open bugs
```
Using the epic-tracking-jira skill, list all bugs with status "Open".
Show bug key, title, and severity.
```

---

## Cleanup

### Test 28: Delete test data (optional)
```
Delete the test epics, stories, and bugs created during this test session:
- Epics: {EPIC-1-KEY}, {EPIC-2-KEY}
- Stories: {STORY-1-KEY}, {STORY-2-KEY}, {STORY-3-KEY}, {STORY-4-KEY}
- Bugs: {BUG-1-KEY}, {BUG-2-KEY}
```

---

## Expected Results Summary

| Test | Operation | Expected |
|------|-----------|----------|
| 1-2 | create_epic | Returns epic key |
| 3 | get_epic | Shows epic details |
| 4-7 | epic state progression | Backlog → Refinement → Implementation → Deployment → Done |
| 8-11 | create_story | Returns story key, linked to epic |
| 12 | get_story | Shows story with parent epic |
| 13 | get_stories_by_epic | Lists 2 stories |
| 14-16 | story state progression | Backlog → In Progress → Review → Done |
| 17-18 | create_bug | Returns bug key |
| 19 | get_bug | Shows bug details |
| 20-23 | bug state progression | Open → Investigating → Fixing → Verification → Closed |
| 24-25 | add_comment | Comment added |
| 26 | list_epics | Shows test epics |
| 27 | list_bugs | Shows test bugs |
