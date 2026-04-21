#!/bin/bash
# Generic Jira Client - Complete Version
# Usage: ./jira.sh <command> [args...]

set -euo pipefail

GATEWAY_URL="${GATEWAY_URL:-http://localhost:3000}"
SSE_OUTPUT="/tmp/jira_sse_$$"
SSE_PID_FILE="/tmp/jira_sse_pid_$$"
SESSION_ID=""

# Cleanup on exit
cleanup() {
    if [ -f "$SSE_PID_FILE" ]; then
        kill $(cat "$SSE_PID_FILE") 2>/dev/null || true
    fi
    rm -f "$SSE_PID_FILE" "$SSE_OUTPUT"
}
trap cleanup EXIT

# Initialize connection
init() {
    curl -s -N "$GATEWAY_URL/sse" > "$SSE_OUTPUT" &
    echo $! > "$SSE_PID_FILE"
    sleep 2

    SESSION_ID=$(grep "sessionId=" "$SSE_OUTPUT" | head -1 | sed 's/.*sessionId=\([^&]*\).*/\1/')

    if [ -z "$SESSION_ID" ]; then
        echo "ERROR: Could not get session ID" >&2
        exit 1
    fi

    curl -s -X POST "$GATEWAY_URL/message?sessionId=$SESSION_ID" \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"jira-cli","version":"1.0"}}}' > /dev/null
    sleep 1
}

# Call MCP tool
call_tool() {
    local tool_name="$1"
    local arguments="$2"
    local request_id="${3:-200}"

    curl -s -X POST "$GATEWAY_URL/message?sessionId=$SESSION_ID" \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":$request_id,\"method\":\"tools/call\",\"params\":{\"name\":\"$tool_name\",\"arguments\":$arguments}}" > /dev/null

    sleep 3

    grep "\"id\":$request_id" "$SSE_OUTPUT" | tail -1 | sed 's/^data: //'
}

# Get user profile
cmd_get_user_profile() {
    init
    call_tool "jira_get_user_profile" "{}" 100
}

# Get issue
cmd_get_issue() {
    local issue_key="$1"
    init
    local args=$(jq -n --arg key "$issue_key" '{issue_key: $key}')
    call_tool "jira_get_issue" "$args" 110
}

# Search issues
cmd_search() {
    local jql="$1"
    init
    local args=$(jq -n --arg q "$jql" '{jql: $q}')
    call_tool "jira_search" "$args" 120
}

# Search fields
cmd_search_fields() {
    init
    call_tool "jira_search_fields" "{}" 130
}

# Get project issues
cmd_get_project_issues() {
    local project_key="$1"
    init
    local args=$(jq -n --arg key "$project_key" '{project_key: $key}')
    call_tool "jira_get_project_issues" "$args" 140
}

# Get transitions
cmd_get_transitions() {
    local issue_key="$1"
    init
    local args=$(jq -n --arg key "$issue_key" '{issue_key: $key}')
    call_tool "jira_get_transitions" "$args" 150
}

# Get worklog
cmd_get_worklog() {
    local issue_key="$1"
    init
    local args=$(jq -n --arg key "$issue_key" '{issue_key: $key}')
    call_tool "jira_get_worklog" "$args" 160
}

# Get agile boards
cmd_get_agile_boards() {
    init
    call_tool "jira_get_agile_boards" "{}" 170
}

# Get board issues
cmd_get_board_issues() {
    local board_id="$1"
    init
    local args=$(jq -n --arg id "$board_id" '{board_id: $id}')
    call_tool "jira_get_board_issues" "$args" 180
}

# Get sprints from board
cmd_get_sprints_from_board() {
    local board_id="$1"
    init
    local args=$(jq -n --arg id "$board_id" '{board_id: $id}')
    call_tool "jira_get_sprints_from_board" "$args" 190
}

# Get sprint issues
cmd_get_sprint_issues() {
    local sprint_id="$1"
    init
    local args=$(jq -n --arg id "$sprint_id" '{sprint_id: $id}')
    call_tool "jira_get_sprint_issues" "$args" 200
}

# Get link types
cmd_get_link_types() {
    init
    call_tool "jira_get_link_types" "{}" 210
}

# Create issue
cmd_create_issue() {
    local project_key="$1"
    local summary="$2"
    local issue_type="${3:-Task}"
    init
    local args=$(jq -n --arg pk "$project_key" --arg s "$summary" --arg t "$issue_type" '{project_key: $pk, summary: $s, issue_type: $t}')
    call_tool "jira_create_issue" "$args" 300
}

# Update issue
cmd_update_issue() {
    local issue_key="$1"
    local fields="$2"
    init
    local args=$(jq -n --arg key "$issue_key" --argjson f "$fields" '{issue_key: $key, fields: $f}')
    call_tool "jira_update_issue" "$args" 310
}

# Delete issue
cmd_delete_issue() {
    local issue_key="$1"
    init
    local args=$(jq -n --arg key "$issue_key" '{issue_key: $key}')
    call_tool "jira_delete_issue" "$args" 320
}

# Add comment
cmd_add_comment() {
    local issue_key="$1"
    local comment="$2"
    init
    local args=$(jq -n --arg key "$issue_key" --arg c "$comment" '{issue_key: $key, comment: $c}')
    call_tool "jira_add_comment" "$args" 330
}

# Edit comment
cmd_edit_comment() {
    local issue_key="$1"
    local comment_id="$2"
    local comment="$3"
    init
    local args=$(jq -n --arg key "$issue_key" --arg cid "$comment_id" --arg c "$comment" '{issue_key: $key, comment_id: $cid, comment: $c}')
    call_tool "jira_edit_comment" "$args" 340
}

# Add worklog
cmd_add_worklog() {
    local issue_key="$1"
    local time_spent="$2"
    init
    local args=$(jq -n --arg key "$issue_key" --arg t "$time_spent" '{issue_key: $key, time_spent: $t}')
    call_tool "jira_add_worklog" "$args" 350
}

# Link to epic
cmd_link_to_epic() {
    local issue_key="$1"
    local epic_key="$2"
    init
    local args=$(jq -n --arg key "$issue_key" --arg epic "$epic_key" '{issue_key: $key, epic_key: $epic}')
    call_tool "jira_link_to_epic" "$args" 360
}

# Create issue link
cmd_create_issue_link() {
    local inward_issue="$1"
    local outward_issue="$2"
    local link_type="$3"
    init
    local args=$(jq -n --arg in "$inward_issue" --arg out "$outward_issue" --arg type "$link_type" '{inward_issue: $in, outward_issue: $out, link_type: $type}')
    call_tool "jira_create_issue_link" "$args" 370
}

# Transition issue
cmd_transition_issue() {
    local issue_key="$1"
    local transition_id="$2"
    init
    local args=$(jq -n --arg key "$issue_key" --arg tid "$transition_id" '{issue_key: $key, transition_id: $tid}')
    call_tool "jira_transition_issue" "$args" 380
}

# Get all projects
cmd_get_all_projects() {
    init
    call_tool "jira_get_all_projects" "{}" 390
}

# Get project versions
cmd_get_project_versions() {
    local project_key="$1"
    init
    local args=$(jq -n --arg key "$project_key" '{project_key: $key}')
    call_tool "jira_get_project_versions" "$args" 400
}

# Create version
cmd_create_version() {
    local project_key="$1"
    local version_name="$2"
    init
    local args=$(jq -n --arg pk "$project_key" --arg vn "$version_name" '{project_key: $pk, version_name: $vn}')
    call_tool "jira_create_version" "$args" 410
}

# Main dispatcher
case "${1:-}" in
    get_user_profile)
        cmd_get_user_profile
        ;;
    get_issue)
        [ -z "${2:-}" ] && { echo "Usage: $0 get_issue <issue_key>" >&2; exit 1; }
        cmd_get_issue "$2"
        ;;
    search)
        [ -z "${2:-}" ] && { echo "Usage: $0 search <jql>" >&2; exit 1; }
        cmd_search "$2"
        ;;
    search_fields)
        cmd_search_fields
        ;;
    get_project_issues)
        [ -z "${2:-}" ] && { echo "Usage: $0 get_project_issues <project_key>" >&2; exit 1; }
        cmd_get_project_issues "$2"
        ;;
    get_transitions)
        [ -z "${2:-}" ] && { echo "Usage: $0 get_transitions <issue_key>" >&2; exit 1; }
        cmd_get_transitions "$2"
        ;;
    get_worklog)
        [ -z "${2:-}" ] && { echo "Usage: $0 get_worklog <issue_key>" >&2; exit 1; }
        cmd_get_worklog "$2"
        ;;
    get_agile_boards)
        cmd_get_agile_boards
        ;;
    get_board_issues)
        [ -z "${2:-}" ] && { echo "Usage: $0 get_board_issues <board_id>" >&2; exit 1; }
        cmd_get_board_issues "$2"
        ;;
    get_sprints_from_board)
        [ -z "${2:-}" ] && { echo "Usage: $0 get_sprints_from_board <board_id>" >&2; exit 1; }
        cmd_get_sprints_from_board "$2"
        ;;
    get_sprint_issues)
        [ -z "${2:-}" ] && { echo "Usage: $0 get_sprint_issues <sprint_id>" >&2; exit 1; }
        cmd_get_sprint_issues "$2"
        ;;
    get_link_types)
        cmd_get_link_types
        ;;
    create_issue)
        [ -z "${2:-}" ] || [ -z "${3:-}" ] && { echo "Usage: $0 create_issue <project_key> <summary> [issue_type]" >&2; exit 1; }
        cmd_create_issue "$2" "$3" "${4:-Task}"
        ;;
    update_issue)
        [ -z "${2:-}" ] || [ -z "${3:-}" ] && { echo "Usage: $0 update_issue <issue_key> <fields_json>" >&2; exit 1; }
        cmd_update_issue "$2" "$3"
        ;;
    delete_issue)
        [ -z "${2:-}" ] && { echo "Usage: $0 delete_issue <issue_key>" >&2; exit 1; }
        cmd_delete_issue "$2"
        ;;
    add_comment)
        [ -z "${2:-}" ] || [ -z "${3:-}" ] && { echo "Usage: $0 add_comment <issue_key> <comment>" >&2; exit 1; }
        cmd_add_comment "$2" "$3"
        ;;
    edit_comment)
        [ -z "${2:-}" ] || [ -z "${3:-}" ] || [ -z "${4:-}" ] && { echo "Usage: $0 edit_comment <issue_key> <comment_id> <comment>" >&2; exit 1; }
        cmd_edit_comment "$2" "$3" "$4"
        ;;
    add_worklog)
        [ -z "${2:-}" ] || [ -z "${3:-}" ] && { echo "Usage: $0 add_worklog <issue_key> <time_spent>" >&2; exit 1; }
        cmd_add_worklog "$2" "$3"
        ;;
    link_to_epic)
        [ -z "${2:-}" ] || [ -z "${3:-}" ] && { echo "Usage: $0 link_to_epic <issue_key> <epic_key>" >&2; exit 1; }
        cmd_link_to_epic "$2" "$3"
        ;;
    create_issue_link)
        [ -z "${2:-}" ] || [ -z "${3:-}" ] || [ -z "${4:-}" ] && { echo "Usage: $0 create_issue_link <inward> <outward> <link_type>" >&2; exit 1; }
        cmd_create_issue_link "$2" "$3" "$4"
        ;;
    transition_issue)
        [ -z "${2:-}" ] || [ -z "${3:-}" ] && { echo "Usage: $0 transition_issue <issue_key> <transition_id>" >&2; exit 1; }
        cmd_transition_issue "$2" "$3"
        ;;
    get_all_projects)
        cmd_get_all_projects
        ;;
    get_project_versions)
        [ -z "${2:-}" ] && { echo "Usage: $0 get_project_versions <project_key>" >&2; exit 1; }
        cmd_get_project_versions "$2"
        ;;
    create_version)
        [ -z "${2:-}" ] || [ -z "${3:-}" ] && { echo "Usage: $0 create_version <project_key> <version_name>" >&2; exit 1; }
        cmd_create_version "$2" "$3"
        ;;
    list|help)
        cat << 'EOF'
Jira CLI - All Available Commands

Read Operations:
  get_user_profile                      - Get current user profile
  get_issue <issue_key>                 - Get issue details
  search <jql>                          - Search issues with JQL
  search_fields                         - List all available fields
  get_project_issues <project_key>      - Get all issues in project
  get_transitions <issue_key>           - Get available transitions
  get_worklog <issue_key>               - Get worklog entries
  get_agile_boards                      - List all agile boards
  get_board_issues <board_id>           - Get issues on board
  get_sprints_from_board <board_id>     - Get sprints from board
  get_sprint_issues <sprint_id>         - Get issues in sprint
  get_link_types                        - List issue link types
  get_all_projects                      - List all projects
  get_project_versions <project_key>    - Get versions in project

Write Operations:
  create_issue <project> <summary> [type]     - Create issue
  update_issue <issue_key> <fields_json>      - Update issue
  delete_issue <issue_key>                    - Delete issue
  add_comment <issue_key> <comment>           - Add comment
  edit_comment <issue> <comment_id> <text>    - Edit comment
  add_worklog <issue_key> <time_spent>        - Log work (e.g., "2h")
  link_to_epic <issue_key> <epic_key>         - Link to epic
  create_issue_link <in> <out> <type>         - Create issue link
  transition_issue <issue_key> <trans_id>     - Transition issue
  create_version <project> <version_name>     - Create version

Examples:
  ./jira.sh search "project = CODINT"
  ./jira.sh get_issue CODINT-13
  ./jira.sh get_project_issues CODINT
  ./jira.sh create_issue CODINT "Fix bug" Story
  ./jira.sh add_comment CODINT-13 "Work completed"
  ./jira.sh transition_issue CODINT-13 21

Aliases:
  help  -> list
EOF
        ;;
    *)
        echo "Usage: $0 <command> [args]" >&2
        echo "Run '$0 help' to see all available commands" >&2
        exit 1
        ;;
esac
