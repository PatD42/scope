---
name: jira-sooperset-mcp-http
description: Jira implementation for project tracking - uses Atlassian MCP via HTTP API (SSE + POST) for subagent access
---

# Project Tracking - Jira Implementation (HTTP API)

This implementation uses the Atlassian MCP server via HTTP API (SSE + POST transport). It provides the same interface as `jira-sooperset-mcp` but connects through HTTP instead of stdio, enabling subagent access without MCP server integration issues.

**Key advantage:** HTTP API allows subagents to reliably access Atlassian APIs using standard curl/HTTP requests without depending on Claude Code's MCP server features, which can be unreliable for subagents.

## Configuration

Expects parameters from `.scope/config.yaml`:

```yaml
tracking:
  skill: jira-sooperset-mcp-http
  project_key: CODINT              # Jira project key
  atlassian_url: https://yoursite.atlassian.net
  http_endpoint: http://localhost:3000  # HTTP gateway endpoint
```

## HTTP Gateway Setup

**Launch the gateway:**
```bash
# From the project root directory
./launch-mcp-ws.sh  # Despite the name, it launches SSE + HTTP POST gateway
```

This script:
1. Wraps `uvx mcp-atlassian` with supergateway
2. Exposes MCP server via SSE + HTTP POST at http://localhost:3000
3. SSE endpoint: `GET http://localhost:3000/sse`
4. Message endpoint: `POST http://localhost:3000/message`

**Environment variables:**
- `ATLASSIAN_WS_PORT`: Port for HTTP server (default: 3000)
- `ATLASSIAN_WS_HOST`: Host binding (default: localhost)

**Authentication:** The underlying MCP server requires these variables (set in .env):
- `ATLASSIAN_URL`
- `ATLASSIAN_USERNAME`
- `ATLASSIAN_API_TOKEN`

## HTTP API Pattern

The gateway uses SSE (Server-Sent Events) + HTTP POST, not WebSocket:

1. **Establish SSE connection** to get session ID:
   ```bash
   curl -N 'http://localhost:3000/sse'
   # Returns: event: endpoint
   #          data: /message?sessionId=<SESSION_ID>
   ```

2. **Initialize MCP session**:
   ```bash
   curl -X POST "http://localhost:3000/message?sessionId=<SESSION_ID>" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "initialize",
       "params": {
         "protocolVersion": "2024-11-05",
         "capabilities": {},
         "clientInfo": {"name": "agent", "version": "1.0"}
       }
     }'
   ```

3. **Call MCP tools**:
   ```bash
   curl -X POST "http://localhost:3000/message?sessionId=<SESSION_ID>" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 2,
       "method": "tools/call",
       "params": {
         "name": "jira_search",
         "arguments": {
           "jql": "project = CODINT"
         }
       }
     }'
   ```

4. **Responses arrive via SSE** (read from SSE connection):
   ```
   event: message
   data: {"jsonrpc":"2.0","id":2,"result":{...}}
   ```

## Status Mapping

| SCOPE Phase | Jira Status |
|-------------|-------------|
| backlog | Backlog |
| refinement | Refinement |
| in_progress | In Progress |
| deploying | Deploying |
| done | Done |

## Operations

**IMPORTANT: Use the jira-sooperset-mcp-http.sh script instead of manual HTTP requests.**

All operations use the `jira-sooperset-mcp-http.sh` bash script co-located with this skill. This script handles SSE connection management, session initialization, and request/response parsing automatically.

**Script location:** Script is located via resolution order:
1. `./.claude/skills/project-tracking/scripts/jira-sooperset-mcp-http.sh` (project-level)
2. `~/.claude/skills/project-tracking/scripts/jira-sooperset-mcp-http.sh` (user-level)

When invoking, use the Bash tool to find and execute the script:
```bash
# Find script location
if [ -f "./.claude/skills/project-tracking/scripts/jira-sooperset-mcp-http.sh" ]; then
  SCRIPT="./.claude/skills/project-tracking/scripts/jira-sooperset-mcp-http.sh"
elif [ -f "$HOME/.claude/skills/project-tracking/scripts/jira-sooperset-mcp-http.sh" ]; then
  SCRIPT="$HOME/.claude/skills/project-tracking/scripts/jira-sooperset-mcp-http.sh"
else
  echo "Error: jira-sooperset-mcp-http.sh not found"
  exit 1
fi

# Use the script
bash "$SCRIPT" <command> <args>
```

### get_epic(epic_id)

Get epic details including status, assignee, summary, and description.

**Using jira.sh:**
```bash
$SCRIPT get_issue CODINT-13
```

**Returns:** JSON with issue details

**Performance:** ~6 seconds

### get_stories(epic_id)

Get all stories linked to an epic.

**Using jira.sh:**
```bash
$SCRIPT search '"Epic Link" = CODINT-13'
```

**Returns:** JSON with list of issues
}
```

### create_story(epic_id, story_data)

Create a new story under an epic.

**Parameters:**
- `epic_id`: Parent epic ID
- `story_data`:
  - `title`: Story summary
  - `description`: Story description (markdown)
  - `acceptance_criteria`: List of acceptance criteria

**Using jira.sh:**
```bash
# Note: jira.sh doesn't directly support parent/description in create_issue
# Use create_issue to create, then update_issue to set description, then link_to_epic

# Step 1: Create story
$SCRIPT create_issue CODINT "User login with OAuth" Story

# Step 2: Update description (assuming story key is CODINT-17)
$SCRIPT update_issue CODINT-17 '{"description": "Story description\n\n## Acceptance Criteria\n- AC1\n- AC2"}'

# Step 3: Link to epic
$SCRIPT link_to_epic CODINT-17 CODINT-13
```

**Returns:** Issue object with `key`, `id`, `self` URL

**Performance:** ~6 seconds per operation

### update_story(story_id, fields)

Update story fields.

**Using jira.sh:**
```bash
$SCRIPT update_issue CODINT-17 '{"summary": "New title", "description": "Updated description"}'
```

**Performance:** ~6 seconds

### transition_epic(epic_id, status)

Change epic status. Automatically finds and applies the correct transition.

**Using jira.sh:**
```bash
# Step 1: Get available transitions
$SCRIPT get_transitions CODINT-13

# Response includes transitions with IDs
# Find transition ID where to.name == target status

# Step 2: Apply transition
$SCRIPT transition_issue CODINT-13 31
```

**Performance:** ~6 seconds per operation

### add_comment(issue_id, comment)

Add a comment to an issue (epic, story, or task).

**Using jira.sh:**
```bash
$SCRIPT add_comment CODINT-13 "Story created via SCOPE automation"
```

**Performance:** ~6 seconds

### create_epic(epic_data)

Create a new epic.

**Parameters:**
- `epic_data`: `title`, `description` (markdown), `epic_name`

**Using jira.sh:**
```bash
# Note: jira.sh doesn't directly support epic_name or description in create_issue
# Use create_issue to create, then update_issue to set description

# Step 1: Create epic
$SCRIPT create_issue CODINT "New Epic Title" Epic

# Step 2: Update description (assuming epic key is CODINT-20)
$SCRIPT update_issue CODINT-20 '{"description": "Epic description..."}'
```

**Returns:** Epic object with `key`, `id`, `self` URL

**Performance:** ~6 seconds per operation

**Note:** The Epic Name field ID may vary by Jira instance. Check your Jira configuration.

### add_worklog(issue_id, time_spent, comment=None)

Log work on an issue.

**Parameters:**
- `issue_id`: Issue to log work on
- `time_spent`: Time in Jira format (e.g., "2h", "30m", "1d 4h")
- `comment` (optional): Work log comment

**Using jira.sh:**
```bash
$SCRIPT add_worklog CODINT-17 "2h"

# If comment provided, add it separately
$SCRIPT add_comment CODINT-17 "Completed OAuth integration"
```

**Performance:** ~6 seconds per operation

---

## Using jira.sh Script

The `jira.sh` script in the project root provides a simple interface to all Jira operations. It handles all SSE connection management, session initialization, and response parsing automatically.

**View all commands:**
```bash
$SCRIPT help
```

**Example workflow:**
```bash
# Search for epic
$SCRIPT get_issue CODINT-13

# Get stories for epic
$SCRIPT search '"Epic Link" = CODINT-13'

# Get all project issues
$SCRIPT get_project_issues CODINT

# Create new story
$SCRIPT create_issue CODINT "User authentication" Story

# Link story to epic
$SCRIPT link_to_epic CODINT-17 CODINT-13

# Add comment
$SCRIPT add_comment CODINT-17 "Implementation complete"

# Get available transitions
$SCRIPT get_transitions CODINT-13

# Transition issue
$SCRIPT transition_issue CODINT-13 31
```

**Performance:** ~6 seconds per operation (significantly faster than manual SSE management)

---

## Error Handling

**Using jira.sh:** The script handles connection management automatically. Common errors:

**Error types:**
- **Connection refused**: Gateway not running - Start `./launch-mcp-ws.sh`
- **401 Unauthorized** (rare): Auth expired - Restart gateway to re-authenticate
- **403 Forbidden**: Missing permissions - Check Jira project permissions
- **404 Not Found**: Invalid issue key - Use `$SCRIPT search` to find correct key
- **400 Bad Request** (transitions): Invalid transition ID - Use `$SCRIPT get_transitions` to see available options
- **Script not found**: Run from project root or use absolute path to script

**Gateway restart (fixes most authentication issues):**
```bash
# Stop gateway (Ctrl+C in terminal where it's running)
# Restart gateway
./launch-mcp-ws.sh
```

**Transition ID example:**
```bash
# Get available transitions
$SCRIPT get_transitions CODINT-13

# Use transition ID (not status name)
$SCRIPT transition_issue CODINT-13 31
```

---

## Migration from jira-sooperset-mcp

**Minimal changes required.** Update `.scope/config.yaml`:

```yaml
# Before:
tracking:
  skill: jira-sooperset-mcp
  project_key: CODINT
  atlassian_url: https://yoursite.atlassian.net

# After:
tracking:
  skill: jira-sooperset-mcp-http  # Change skill name
  project_key: CODINT
  atlassian_url: https://yoursite.atlassian.net
  http_endpoint: http://localhost:3000    # Add HTTP endpoint
```

**Code changes:**
- Replace `mcp__atlassian__*` calls with `$SCRIPT` commands via Bash tool
- All operations now use simple bash script: `$SCRIPT <command> <args>`
- No manual SSE connection management needed
- Significant performance improvement (~6 seconds per operation)
