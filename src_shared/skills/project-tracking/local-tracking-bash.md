---
name: local-tracking-bash
description: File-based implementation for project tracking - uses bash script wrapper for reliable operations
---

# Project Tracking - File Implementation (Bash Wrapper)

This implementation uses a bash script (`local-tracking.sh`) to reliably handle all tracking operations. The script manages ID generation, state transitions, and file operations using shell code rather than agent instructions.

**Key advantage:** Bash script provides reliable ID generation and state management without requiring the agent to re-implement complex logic each time.

## Configuration

This implementation expects these parameters from `.scope/config.yaml`:

```yaml
tracking:
  skill: local-tracking-bash
  base_path: ./tracking           # Base directory for tracking files
  project_key: PROJECT            # Prefix for display IDs
```

The wrapper skill (`project-tracking/SKILL.md`) reads this config and sets environment variables for the bash script.

## Environment Variables

The bash script reads configuration from environment variables:

- `TRACKING_BASE_PATH`: Base directory (default: `.scope/tracking`)
- `TRACKING_PROJECT_KEY`: Project key for display IDs (default: `PROJECT`)

**Example:**
```bash
export TRACKING_BASE_PATH=".scope/tracking"
export TRACKING_PROJECT_KEY="CODINT"
```

## Script Location

The bash script is located at:
```
.claude/skills/project-tracking/scripts/local-tracking.sh (if not found, check in ~/.claude)
```

## Usage Pattern

All operations follow this pattern:

```bash
# Set environment variables from config
export TRACKING_BASE_PATH="<base_path from config>"
export TRACKING_PROJECT_KEY="<project_key from config>"

# Call the script
.claude/skills/project-tracking/scripts/local-tracking.sh <operation> [args...]
```

## File Organization

The script manages this directory structure:

```
{base_path}/
├── .counter                    # Single counter for all issues
├── epics/
│   └── {project_key}-{id}-{slug}/
│       ├── issue.yaml          # Epic metadata
│       ├── state.log           # Status history
│       └── stories/
│           └── {project_key}-{id}-{slug}/
│               ├── issue.yaml
│               └── state.log
└── tasks/
    └── {project_key}-{id}-{slug}/
        ├── issue.yaml
        └── state.log
```

**Key principles:**
- Single `.counter` file for all issue types (sequential: 1, 2, 3...)
- Display ID format: `{PROJECT_KEY}-{id}` (e.g., CODINT-1, CODINT-23)
- Folder names: `{project_key}-{id}-{slug}` (e.g., `codint-23-user-authentication`)
- Consistent with documentation backend folder naming
- YAML for structured metadata
- Append-only `state.log` for status history

## Operations

### 1. create_epic

Create a new epic.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh create_epic \
  "<title>" \
  "<description>"
```

**Returns JSON:**
```json
{
  "id": "1",
  "display_id": "CODINT-1",
  "type": "epic",
  "title": "User Authentication",
  "status": "new",
  "directory": ".scope/tracking/epics/codint-1-user-authentication"
}
```

**Example:**
```bash
export TRACKING_BASE_PATH=".scope/tracking"
export TRACKING_PROJECT_KEY="CODINT"

.claude/skills/project-tracking/scripts/local-tracking.sh create_epic \
  "Implement User Authentication" \
  "Add OAuth 2.0 login flow with Google and GitHub providers"
```

### 2. get_epic

Get epic details.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh get_epic <issue_id>
```

**Returns:**
- JSON with directory path, current status, and YAML content

**Example:**
```bash
.claude/skills/project-tracking/scripts/local-tracking.sh get_epic 1
```

### 3. update_epic

Update epic field.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh update_epic \
  <issue_id> \
  <field> \
  "<value>"
```

**Supported fields:**
- `title`: Issue title
- `description`: Issue description
- `assignee`: Assignee name
- `labels`: Comma-separated labels (e.g., "backend,security")

**Example:**
```bash
.claude/skills/project-tracking/scripts/local-tracking.sh update_epic 1 assignee "john-doe"
.claude/skills/project-tracking/scripts/local-tracking.sh update_epic 1 labels "backend,security,oauth"
```

### 4. transition_epic

Change epic status.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh transition_epic \
  <issue_id> \
  <new_status> \
  [author]
```

**Common statuses:**
- `new`: Initial state
- `refining`: Being refined
- `ready`: Ready for implementation
- `in_progress`: Implementation started
- `done`: Completed

**Example:**
```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  transition_epic 1 refining agent:architect
.claude/skills/project-tracking/scripts/local-tracking.sh  transition_epic 1 ready
```

### 5. create_story

Create a story under an epic.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  create_story \
  <epic_id> \
  "<title>" \
  "<description>"
```

**Returns JSON:**
```json
{
  "id": "2",
  "display_id": "CODINT-2",
  "type": "story",
  "title": "OAuth Login Button",
  "parent_id": "1",
  "status": "new",
  "directory": ".scope/tracking/epics/codint-1-user-authentication/stories/codint-2-oauth-login-button"
}
```

**Example:**
```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  create_story 1 \
  "Add OAuth login button" \
  "Display Google and GitHub login buttons on the login page"
```

### 6. get_story

Get story details.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  get_story <issue_id>
```

**Example:**
```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  get_story 2
```

### 7. get_stories

Get all stories for an epic.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  get_stories <epic_id>
```

**Returns:** JSON array of all stories under the epic

**Example:**
```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  get_stories 1
```

### 8. update_story

Update story field.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  update_story \
  <issue_id> \
  <field> \
  "<value>"
```

**Supported fields:** Same as `update_epic`

**Example:**
```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  update_story 2 assignee "jane-smith"
```

### 9. transition_story

Change story status.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  transition_story \
  <issue_id> \
  <new_status> \
  [author]
```

**Example:**
```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  transition_story 2 in_progress agent:developer
```

### 10. add_comment

Add a comment to any issue (epic, story, or task).

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  add_comment \
  <issue_id> \
  "<comment_text>" \
  [author]
```

**Example:**
```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  add_comment 1 \
  "Need to clarify OAuth token refresh strategy" \
  "agent:architect"
```

### 11. search_issues

Search issues by text query.

```bash
.claude/skills/project-tracking/scripts/local-tracking.sh  search_issues \
  "<query>" \
  [type]
```

**Optional type filter:** `epic`, `story`, or `task`

**Returns:** JSON array of matching issues

**Example:**
```bash
# Search all issues
.claude/skills/project-tracking/scripts/local-tracking.sh  search_issues "authentication"

# Search only epics
.claude/skills/project-tracking/scripts/local-tracking.sh  search_issues "authentication" epic
```

## Complete Example Workflow

```bash
# Setup environment
export TRACKING_BASE_PATH=".scope/tracking"
export TRACKING_PROJECT_KEY="CODINT"

SCRIPT=".claude/skills/project-tracking/scripts/local-tracking.sh "

# 1. Create an epic
epic_result=$($SCRIPT create_epic \
  "User Authentication System" \
  "Implement OAuth 2.0 login with multiple providers")

# Extract epic ID (parsing JSON - in practice use jq)
epic_id=$(echo "$epic_result" | grep '"id"' | head -1 | cut -d'"' -f4)

echo "Created epic: CODINT-${epic_id}"

# 2. Transition epic to refining
$SCRIPT transition_epic "$epic_id" refining "agent:architect"

# 3. Create stories
$SCRIPT create_story "$epic_id" \
  "OAuth login button UI" \
  "Add login buttons for Google and GitHub"

$SCRIPT create_story "$epic_id" \
  "OAuth callback handler" \
  "Implement /auth/callback endpoint"

$SCRIPT create_story "$epic_id" \
  "User session management" \
  "Store user session in Redis with JWT tokens"

# 4. Get all stories
$SCRIPT get_stories "$epic_id"

# 5. Transition epic to ready
$SCRIPT transition_epic "$epic_id" ready "agent:product-owner"

# 6. Search for authentication issues
$SCRIPT search_issues "OAuth" story
```

## Error Handling

The script exits with non-zero status and outputs error JSON to stderr:

```json
{"error": "Epic 99 not found"}
```

**Common errors:**
- Issue not found (wrong ID or type)
- Epic not found when creating story
- Invalid field name in update operations

## Data Formats

### issue.yaml Structure

```yaml
id: "23"
display_id: "CODINT-23"
type: story
title: "OAuth login button UI"
description: |
  Add login buttons for Google and GitHub on the login page.
  Style according to brand guidelines.
created: "2025-01-15T10:00:00Z"
updated: "2025-01-20T14:30:00Z"
status: in_progress
parent_id: "15"                 # For stories/tasks
assignee: "jane-smith"
labels: [frontend, ui, oauth]
acceptance_criteria:
  - "Google login button displays correctly"
  - "GitHub login button displays correctly"
  - "Buttons redirect to OAuth flow"
comments:
  - author: "agent:architect"
    timestamp: "2025-01-15T11:00:00Z"
    body: "Consider adding Apple Sign-In as well"
```

### state.log Format

Append-only log with pipe-separated values:

```
2025-01-15T10:00:00Z|new|system
2025-01-15T11:30:00Z|in_progress|agent:developer
2025-01-20T14:30:00Z|done|agent:developer
```

**Format:** `timestamp|status|author`

## Advantages Over Direct Operations

1. **Reliable ID generation**: Counter management in bash code (no risk of agent mistakes)
2. **Consistent state log format**: Append logic is coded once
3. **Atomic operations**: Each script call is a complete transaction
4. **Easier debugging**: Can test operations independently with bash
5. **Lower cognitive load**: Agent just calls script with parameters

## Comparison to Jira Backend

| Feature | Jira Backend | Local Bash Backend |
|---------|--------------|-------------------|
| Issue IDs | Server-generated | Sequential counter |
| Display IDs | PROJECT-123 | PROJECT-123 |
| Status transitions | Workflow API | state.log append |
| Relationships | parent field + API | parent_id + folders |
| Comments | REST API | YAML array |
| Search | JQL queries | grep in YAML files |
| Concurrency | Server handles | Single-user assumed |
| Authentication | Required | None (local files) |

## Token Efficiency

**Backend file:** ~450 lines
**Bash script:** ~650 lines (not loaded into context)

**Total context cost:** ~450 lines (bash script is called, not read)

Compare to direct operations approach:
- Direct operations: ~1000 lines of instructions
- Bash wrapper: ~450 lines of instructions + script (not in context)

**Savings:** ~55% fewer tokens loaded per operation
