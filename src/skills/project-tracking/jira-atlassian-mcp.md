---
name: jira-atlassian-mcp
description: Jira implementation for project tracking - uses Atlassian MCP tools to interact with Jira
---

# Project Tracking - Jira Implementation

This implementation uses Atlassian MCP tools to track epics, stories, and tasks in Jira.

## Configuration

This implementation expects these parameters from `.scope/config.yaml`:

```yaml
tracking:
  skill: jira-atlassian-mcp
  project_key: CODINT              # Jira project key
  atlassian_url: https://yoursite.atlassian.net
```

The wrapper skill (`project-tracking/SKILL.md`) reads this config and passes parameters to this implementation.

## Status Mapping

| SCOPE Phase | Jira Status |
|-------------|-------------|
| backlog | Backlog |
| refinement | Refinement |
| in_progress | In Progress |
| deploying | Deploying |
| done | Done |

## Operations

### get_epic(epic_id)

Get epic details including status, assignee, summary, and description.

**Implementation:**
```python
cloudId = config.tracking.atlassian_url
epic = mcp__atlassian__getJiraIssue(
    cloudId=cloudId,
    issueIdOrKey=epic_id
)
```

**Returns:**
```yaml
epic:
  id: CODINT-1
  status: Refinement
  summary: "Intent Extraction Language Support"
  description: "..."
  assignee: "John Doe"
  created: "2024-01-15T10:00:00Z"
```

### get_stories(epic_id)

Get all stories linked to an epic.

**Implementation:**
```python
cloudId = config.tracking.atlassian_url
project_key = config.tracking.project_key

stories = mcp__atlassian__searchJiraIssuesUsingJql(
    cloudId=cloudId,
    jql=f'"Epic Link" = {epic_id}',
    fields=["summary", "status", "assignee", "created"]
)
```

**Returns:**
```yaml
stories:
  - id: CODINT-2
    summary: "User login with OAuth"
    status: In Progress
    assignee: "Jane Smith"
  - id: CODINT-3
    summary: "Session management"
    status: Backlog
```

### create_story(epic_id, story_data)

Create a new story under an epic.

**Parameters:**
- `epic_id`: Parent epic ID
- `story_data`:
  - `title`: Story summary
  - `description`: Story description (markdown)
  - `acceptance_criteria`: List of acceptance criteria
  - `assignee_account_id` (optional): Jira account ID

**Implementation:**
```python
cloudId = config.tracking.atlassian_url
project_key = config.tracking.project_key

# Format description with acceptance criteria
description = f"{story_data.description}\n\n## Acceptance Criteria\n"
for criterion in story_data.acceptance_criteria:
    description += f"- {criterion}\n"

story = mcp__atlassian__createJiraIssue(
    cloudId=cloudId,
    projectKey=project_key,
    issueTypeName="Story",
    summary=story_data.title,
    description=description,
    parent=epic_id,  # Links to epic
    assignee_account_id=story_data.get("assignee_account_id")
)
```

**Returns:**
```yaml
story:
  id: CODINT-4
  key: CODINT-4
  url: https://yoursite.atlassian.net/browse/CODINT-4
```

### update_story(story_id, fields)

Update story fields.

**Parameters:**
- `story_id`: Story ID to update
- `fields`: Dictionary of fields to update (e.g., `{"summary": "New title", "description": "..."}`)

**Implementation:**
```python
cloudId = config.tracking.atlassian_url

mcp__atlassian__editJiraIssue(
    cloudId=cloudId,
    issueIdOrKey=story_id,
    fields=fields
)
```

### transition_epic(epic_id, status)

Change epic status. Automatically finds and applies the correct transition.

**Parameters:**
- `epic_id`: Epic ID to transition
- `status`: Target status (e.g., "In Progress", "Done")

**Implementation:**
```python
cloudId = config.tracking.atlassian_url

# Get available transitions
transitions = mcp__atlassian__getTransitionsForJiraIssue(
    cloudId=cloudId,
    issueIdOrKey=epic_id
)

# Find transition ID for target status
transition_id = None
for transition in transitions["transitions"]:
    if transition["to"]["name"] == status:
        transition_id = transition["id"]
        break

if not transition_id:
    raise ValueError(f"No transition available to status '{status}'. Available transitions: {[t['to']['name'] for t in transitions['transitions']]}")

# Apply transition
mcp__atlassian__transitionJiraIssue(
    cloudId=cloudId,
    issueIdOrKey=epic_id,
    transition={"id": transition_id}
)
```

### add_comment(issue_id, comment)

Add a comment to an issue (epic, story, or task).

**Implementation:**
```python
cloudId = config.tracking.atlassian_url

mcp__atlassian__addCommentToJiraIssue(
    cloudId=cloudId,
    issueIdOrKey=issue_id,
    commentBody=comment  # Markdown format
)
```

### create_epic(epic_data)

Create a new epic.

**Parameters:**
- `epic_data`:
  - `title`: Epic summary
  - `description`: Epic description (markdown)
  - `epic_name`: Short name for epic

**Implementation:**
```python
cloudId = config.tracking.atlassian_url
project_key = config.tracking.project_key

epic = mcp__atlassian__createJiraIssue(
    cloudId=cloudId,
    projectKey=project_key,
    issueTypeName="Epic",
    summary=epic_data.title,
    description=epic_data.description,
    additional_fields={
        "customfield_10011": epic_data.epic_name  # Epic Name field
    }
)
```

**Note:** The Epic Name custom field ID may vary by Jira instance. Check your Jira configuration for the correct field ID.

### add_worklog(issue_id, time_spent, comment=None)

Log work on an issue.

**Parameters:**
- `issue_id`: Issue to log work on
- `time_spent`: Time in Jira format (e.g., "2h", "30m", "1d 4h")
- `comment` (optional): Work log comment

**Implementation:**
```python
cloudId = config.tracking.atlassian_url

mcp__atlassian__addWorklogToJiraIssue(
    cloudId=cloudId,
    issueIdOrKey=issue_id,
    timeSpent=time_spent
)

# If comment provided, add it separately
if comment:
    add_comment(issue_id, comment)
```

---

## Error Handling

### Authentication Failures

**Error:** `401 Unauthorized` or `Authentication expired`

**Solution:** Ask user to re-authenticate:

```
Atlassian authentication expired or connection lost.

To re-authenticate:
1. Run /mcp
2. Select 'atlassian' MCP server
3. Choose 'Reconnect' or 'Re-authenticate'
4. Complete the OAuth flow
5. Resume this operation

After re-authenticating, I'll retry the operation.
```

**DO NOT fall back to direct API calls.** MCP manages authentication centrally.

### Permission Errors

**Error:** `403 Forbidden - User lacks permission`

**Common causes:**
- User doesn't have "Create Issue" permission in project
- User cannot edit epic/story (restricted by permissions)
- User cannot transition issue (workflow restrictions)

**Fix:**
- Verify user has correct permissions in Jira project settings
- Check workflow allows transition for user's role
- Use `getTransitionsForJiraIssue` to see available transitions

### Issue Not Found

**Error:** `404 Not Found - Issue does not exist`

**Common causes:**
- Issue key typo (e.g., `SCOPE-1` vs `SCOP-1`)
- Issue deleted or in different project
- User lacks permission to view issue

**Fix:**
- Verify issue key format: `{PROJECT_KEY}-{NUMBER}`
- Use `searchJiraIssuesUsingJql` to find issue
- Check project key matches config

### Invalid Transition

**Error:** `400 Bad Request - Transition not valid`

**Common causes:**
- Status doesn't exist in workflow
- Transition not allowed from current status
- Required fields missing for transition

**Fix:**
1. Get available transitions with `getTransitionsForJiraIssue`
2. Use transition `id` (not status name)
3. Check Jira workflow configuration if transition unavailable

**Example:**
```yaml
# Wrong: using status name
transition: { name: "In Progress" }

# Correct: using transition ID from getTransitionsForJiraIssue
transition: { id: "31" }
```

### Field Validation Errors

**Error:** `400 Bad Request - Field required or invalid`

**Fix:**
- Get field metadata: `mcp__atlassian__getJiraProjectIssueTypesMetadata`
- Check required fields for issue type
- Verify field formats match expectations

---

## Examples

### Complete Story Creation Flow

```python
# Read config
config = read_yaml(".scope/config.yaml")
cloudId = config.tracking.atlassian_url
project_key = config.tracking.project_key

# Create story
story_data = {
    "title": "User login with OAuth",
    "description": "Implement OAuth 2.0 login flow",
    "acceptance_criteria": [
        "User can click 'Sign in with Google'",
        "User is redirected to Google OAuth",
        "User is logged in after authentication"
    ]
}

story = create_story(
    epic_id="CODINT-1",
    story_data=story_data
)

# Add initial comment
add_comment(
    issue_id=story["id"],
    comment="Story created via SCOPE automation"
)

# Get stories for epic
stories = get_stories(epic_id="CODINT-1")
print(f"Epic CODINT-1 has {len(stories)} stories")
```

### Epic Status Transition

```python
# Get current epic status
epic = get_epic(epic_id="CODINT-1")
print(f"Current status: {epic['status']}")

# Transition to In Progress
transition_epic(
    epic_id="CODINT-1",
    status="In Progress"
)

# Verify transition
epic = get_epic(epic_id="CODINT-1")
print(f"New status: {epic['status']}")
```
