#!/usr/bin/env bash
set -euo pipefail

# local-tracking.sh - File-based project tracking backend
# Reliable bash implementation for issue creation and management

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_PATH="${TRACKING_BASE_PATH:-./tracking}"
PROJECT_KEY="${TRACKING_PROJECT_KEY:-PROJECT}"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Get next issue ID (single counter for all types)
get_next_id() {
    local counter_file="${BASE_PATH}/.counter"

    # Ensure base directory exists
    mkdir -p "${BASE_PATH}"

    # Initialize counter if doesn't exist
    if [[ ! -f "$counter_file" ]]; then
        echo "0" > "$counter_file"
    fi

    # Read current value
    local current
    current=$(cat "$counter_file")

    # Increment
    local next=$((current + 1))

    # Write back
    echo "$next" > "$counter_file"

    # Return new ID
    echo "$next"
}

# Convert title to filesafe slug
filesafe_slug() {
    local title="$1"
    echo "$title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//'
}

# Get current timestamp in ISO-8601 UTC
current_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Find issue directory by ID and type
# Folder naming: {project_key}-{id}-{slug} (e.g., codint-23-user-authentication)
find_issue_dir() {
    local issue_id="$1"
    local issue_type="$2"  # epic, story, task
    local project_key_lower="${PROJECT_KEY,,}"  # lowercase

    case "$issue_type" in
        epic)
            find "${BASE_PATH}/epics" -maxdepth 1 -type d -name "${project_key_lower}-${issue_id}-*" 2>/dev/null | head -n1
            ;;
        story)
            find "${BASE_PATH}/epics" -mindepth 3 -maxdepth 3 -type d -name "${project_key_lower}-${issue_id}-*" 2>/dev/null | head -n1
            ;;
        task)
            find "${BASE_PATH}/tasks" -maxdepth 1 -type d -name "${project_key_lower}-${issue_id}-*" 2>/dev/null | head -n1
            ;;
        *)
            # Try all locations
            {
                find "${BASE_PATH}/epics" -maxdepth 1 -type d -name "${project_key_lower}-${issue_id}-*" 2>/dev/null
                find "${BASE_PATH}/epics" -mindepth 3 -maxdepth 3 -type d -name "${project_key_lower}-${issue_id}-*" 2>/dev/null
                find "${BASE_PATH}/tasks" -maxdepth 1 -type d -name "${project_key_lower}-${issue_id}-*" 2>/dev/null
            } | head -n1
            ;;
    esac
}

# Parse state.log to get current status
get_current_status() {
    local state_log="$1"

    if [[ ! -f "$state_log" ]]; then
        echo "new"
        return
    fi

    # Get last line and extract status (format: timestamp|status|author)
    tail -n1 "$state_log" | cut -d'|' -f2
}

# Append to state.log
append_state_log() {
    local state_log="$1"
    local status="$2"
    local author="${3:-agent}"
    local timestamp
    timestamp=$(current_timestamp)

    echo "${timestamp}|${status}|${author}" >> "$state_log"
}

# ============================================================================
# OPERATIONS
# ============================================================================

# Create epic
create_epic() {
    local title="$1"
    local description="${2:-}"

    # Get next ID
    local issue_id
    issue_id=$(get_next_id)
    local display_id="${PROJECT_KEY}-${issue_id}"
    local project_key_lower="${PROJECT_KEY,,}"  # lowercase

    # Create slug
    local slug
    slug=$(filesafe_slug "$title")

    # Create directory (format: {project_key}-{id}-{slug})
    local epic_dir="${BASE_PATH}/epics/${project_key_lower}-${issue_id}-${slug}"
    mkdir -p "$epic_dir"

    # Create issue.yaml
    local now
    now=$(current_timestamp)
    cat > "${epic_dir}/issue.yaml" <<EOF
id: "${issue_id}"
display_id: "${display_id}"
type: epic
title: "${title}"
description: |
  ${description}
created: "${now}"
updated: "${now}"
status: new
assignee: null
labels: []
acceptance_criteria: []
comments: []
EOF

    # Create state.log
    append_state_log "${epic_dir}/state.log" "new" "system"

    # Create stories directory
    mkdir -p "${epic_dir}/stories"

    # Output result as JSON
    cat <<EOF
{
  "id": "${issue_id}",
  "display_id": "${display_id}",
  "type": "epic",
  "title": "${title}",
  "status": "new",
  "directory": "${epic_dir}"
}
EOF
}

# Get epic
get_epic() {
    local issue_id="$1"

    local epic_dir
    epic_dir=$(find_issue_dir "$issue_id" "epic")

    if [[ -z "$epic_dir" ]]; then
        echo "{\"error\": \"Epic ${issue_id} not found\"}" >&2
        return 1
    fi

    local issue_yaml="${epic_dir}/issue.yaml"
    local state_log="${epic_dir}/state.log"

    # Get current status
    local current_status
    current_status=$(get_current_status "$state_log")

    # Output issue data (simplified - just output the YAML content plus current status)
    echo "{"
    echo "  \"directory\": \"${epic_dir}\","
    echo "  \"current_status\": \"${current_status}\","
    echo "  \"issue_data\":"
    # Convert YAML to JSON-like format (simplified)
    cat "$issue_yaml"
    echo "}"
}

# Update epic
update_epic() {
    local issue_id="$1"
    local field="$2"
    local value="$3"

    local epic_dir
    epic_dir=$(find_issue_dir "$issue_id" "epic")

    if [[ -z "$epic_dir" ]]; then
        echo "{\"error\": \"Epic ${issue_id} not found\"}" >&2
        return 1
    fi

    local issue_yaml="${epic_dir}/issue.yaml"
    local now
    now=$(current_timestamp)

    # Update field using yq or sed (using sed for simplicity)
    case "$field" in
        title|description|assignee)
            # Simple string field update
            sed -i.bak "s/^${field}:.*/${field}: \"${value}\"/" "$issue_yaml"
            ;;
        labels)
            # Array field (expecting comma-separated)
            local labels_array
            labels_array=$(echo "$value" | sed 's/,/, /g')
            sed -i.bak "s/^labels:.*/labels: [${labels_array}]/" "$issue_yaml"
            ;;
    esac

    # Update timestamp
    sed -i.bak "s/^updated:.*/updated: \"${now}\"/" "$issue_yaml"
    rm -f "${issue_yaml}.bak"

    echo "{\"status\": \"updated\", \"id\": \"${issue_id}\", \"field\": \"${field}\"}"
}

# Transition epic
transition_epic() {
    local issue_id="$1"
    local new_status="$2"
    local author="${3:-agent}"

    local epic_dir
    epic_dir=$(find_issue_dir "$issue_id" "epic")

    if [[ -z "$epic_dir" ]]; then
        echo "{\"error\": \"Epic ${issue_id} not found\"}" >&2
        return 1
    fi

    local issue_yaml="${epic_dir}/issue.yaml"
    local state_log="${epic_dir}/state.log"

    # Append to state log
    append_state_log "$state_log" "$new_status" "$author"

    # Update issue.yaml
    local now
    now=$(current_timestamp)
    sed -i.bak "s/^status:.*/status: ${new_status}/" "$issue_yaml"
    sed -i.bak "s/^updated:.*/updated: \"${now}\"/" "$issue_yaml"
    rm -f "${issue_yaml}.bak"

    echo "{\"status\": \"transitioned\", \"id\": \"${issue_id}\", \"new_status\": \"${new_status}\"}"
}

# Create story
create_story() {
    local epic_id="$1"
    local title="$2"
    local description="${3:-}"

    # Find epic directory
    local epic_dir
    epic_dir=$(find_issue_dir "$epic_id" "epic")

    if [[ -z "$epic_dir" ]]; then
        echo "{\"error\": \"Epic ${epic_id} not found\"}" >&2
        return 1
    fi

    # Get next ID
    local issue_id
    issue_id=$(get_next_id)
    local display_id="${PROJECT_KEY}-${issue_id}"
    local project_key_lower="${PROJECT_KEY,,}"  # lowercase

    # Create slug
    local slug
    slug=$(filesafe_slug "$title")

    # Create directory (format: {project_key}-{id}-{slug})
    local story_dir="${epic_dir}/stories/${project_key_lower}-${issue_id}-${slug}"
    mkdir -p "$story_dir"

    # Create issue.yaml
    local now
    now=$(current_timestamp)
    cat > "${story_dir}/issue.yaml" <<EOF
id: "${issue_id}"
display_id: "${display_id}"
type: story
title: "${title}"
description: |
  ${description}
created: "${now}"
updated: "${now}"
status: new
parent_id: "${epic_id}"
assignee: null
labels: []
acceptance_criteria: []
comments: []
EOF

    # Create state.log
    append_state_log "${story_dir}/state.log" "new" "system"

    # Output result as JSON
    cat <<EOF
{
  "id": "${issue_id}",
  "display_id": "${display_id}",
  "type": "story",
  "title": "${title}",
  "parent_id": "${epic_id}",
  "status": "new",
  "directory": "${story_dir}"
}
EOF
}

# Get story
get_story() {
    local issue_id="$1"

    local story_dir
    story_dir=$(find_issue_dir "$issue_id" "story")

    if [[ -z "$story_dir" ]]; then
        echo "{\"error\": \"Story ${issue_id} not found\"}" >&2
        return 1
    fi

    local issue_yaml="${story_dir}/issue.yaml"
    local state_log="${story_dir}/state.log"

    # Get current status
    local current_status
    current_status=$(get_current_status "$state_log")

    # Output issue data
    echo "{"
    echo "  \"directory\": \"${story_dir}\","
    echo "  \"current_status\": \"${current_status}\","
    echo "  \"issue_data\":"
    cat "$issue_yaml"
    echo "}"
}

# Get all stories for an epic
get_stories() {
    local epic_id="$1"

    local epic_dir
    epic_dir=$(find_issue_dir "$epic_id" "epic")

    if [[ -z "$epic_dir" ]]; then
        echo "{\"error\": \"Epic ${epic_id} not found\"}" >&2
        return 1
    fi

    echo "["
    local first=true
    # Pattern: {project_key}-{id}-{slug}/
    for story_dir in "${epic_dir}/stories"/*-*-*/; do
        if [[ -d "$story_dir" ]]; then
            if [[ "$first" == "false" ]]; then
                echo ","
            fi
            first=false

            local issue_yaml="${story_dir}issue.yaml"
            local state_log="${story_dir}state.log"
            local current_status
            current_status=$(get_current_status "$state_log")

            echo "  {"
            echo "    \"directory\": \"${story_dir}\","
            echo "    \"current_status\": \"${current_status}\","
            echo "    \"issue_data\":"
            cat "$issue_yaml"
            echo "  }"
        fi
    done
    echo "]"
}

# Update story
update_story() {
    local issue_id="$1"
    local field="$2"
    local value="$3"

    local story_dir
    story_dir=$(find_issue_dir "$issue_id" "story")

    if [[ -z "$story_dir" ]]; then
        echo "{\"error\": \"Story ${issue_id} not found\"}" >&2
        return 1
    fi

    local issue_yaml="${story_dir}/issue.yaml"
    local now
    now=$(current_timestamp)

    # Update field
    case "$field" in
        title|description|assignee)
            sed -i.bak "s/^${field}:.*/${field}: \"${value}\"/" "$issue_yaml"
            ;;
        labels)
            local labels_array
            labels_array=$(echo "$value" | sed 's/,/, /g')
            sed -i.bak "s/^labels:.*/labels: [${labels_array}]/" "$issue_yaml"
            ;;
    esac

    # Update timestamp
    sed -i.bak "s/^updated:.*/updated: \"${now}\"/" "$issue_yaml"
    rm -f "${issue_yaml}.bak"

    echo "{\"status\": \"updated\", \"id\": \"${issue_id}\", \"field\": \"${field}\"}"
}

# Transition story
transition_story() {
    local issue_id="$1"
    local new_status="$2"
    local author="${3:-agent}"

    local story_dir
    story_dir=$(find_issue_dir "$issue_id" "story")

    if [[ -z "$story_dir" ]]; then
        echo "{\"error\": \"Story ${issue_id} not found\"}" >&2
        return 1
    fi

    local issue_yaml="${story_dir}/issue.yaml"
    local state_log="${story_dir}/state.log"

    # Append to state log
    append_state_log "$state_log" "$new_status" "$author"

    # Update issue.yaml
    local now
    now=$(current_timestamp)
    sed -i.bak "s/^status:.*/status: ${new_status}/" "$issue_yaml"
    sed -i.bak "s/^updated:.*/updated: \"${now}\"/" "$issue_yaml"
    rm -f "${issue_yaml}.bak"

    echo "{\"status\": \"transitioned\", \"id\": \"${issue_id}\", \"new_status\": \"${new_status}\"}"
}

# Add comment
add_comment() {
    local issue_id="$1"
    local comment_text="$2"
    local author="${3:-agent}"

    # Find issue (any type)
    local issue_dir
    issue_dir=$(find_issue_dir "$issue_id" "")

    if [[ -z "$issue_dir" ]]; then
        echo "{\"error\": \"Issue ${issue_id} not found\"}" >&2
        return 1
    fi

    local issue_yaml="${issue_dir}/issue.yaml"
    local now
    now=$(current_timestamp)

    # Append comment to YAML (simplified - append to end)
    cat >> "$issue_yaml" <<EOF
  - author: "${author}"
    timestamp: "${now}"
    body: "${comment_text}"
EOF

    # Update timestamp
    sed -i.bak "s/^updated:.*/updated: \"${now}\"/" "$issue_yaml"
    rm -f "${issue_yaml}.bak"

    echo "{\"status\": \"comment_added\", \"id\": \"${issue_id}\"}"
}

# Search issues
search_issues() {
    local query="$1"
    local issue_type="${2:-}"  # Optional: epic, story, task

    echo "["
    local first=true

    # Search in all issue.yaml files
    for issue_yaml in $(find "${BASE_PATH}" -name "issue.yaml" 2>/dev/null); do
        # Check if matches query (grep in title or description)
        if grep -iq "$query" "$issue_yaml"; then
            # Check type filter if specified
            if [[ -n "$issue_type" ]]; then
                if ! grep -q "^type: ${issue_type}$" "$issue_yaml"; then
                    continue
                fi
            fi

            if [[ "$first" == "false" ]]; then
                echo ","
            fi
            first=false

            local issue_dir
            issue_dir=$(dirname "$issue_yaml")
            local state_log="${issue_dir}/state.log"
            local current_status
            current_status=$(get_current_status "$state_log")

            echo "  {"
            echo "    \"directory\": \"${issue_dir}\","
            echo "    \"current_status\": \"${current_status}\","
            echo "    \"issue_data\":"
            cat "$issue_yaml"
            echo "  }"
        fi
    done
    echo "]"
}

# ============================================================================
# MAIN DISPATCHER
# ============================================================================

main() {
    local operation="${1:-}"
    shift || true

    case "$operation" in
        create_epic)
            create_epic "$@"
            ;;
        get_epic)
            get_epic "$@"
            ;;
        update_epic)
            update_epic "$@"
            ;;
        transition_epic)
            transition_epic "$@"
            ;;
        create_story)
            create_story "$@"
            ;;
        get_story)
            get_story "$@"
            ;;
        get_stories)
            get_stories "$@"
            ;;
        update_story)
            update_story "$@"
            ;;
        transition_story)
            transition_story "$@"
            ;;
        add_comment)
            add_comment "$@"
            ;;
        search_issues)
            search_issues "$@"
            ;;
        *)
            echo "Usage: $0 <operation> [args...]" >&2
            echo "" >&2
            echo "Operations:" >&2
            echo "  create_epic <title> [description]" >&2
            echo "  get_epic <issue_id>" >&2
            echo "  update_epic <issue_id> <field> <value>" >&2
            echo "  transition_epic <issue_id> <status> [author]" >&2
            echo "  create_story <epic_id> <title> [description]" >&2
            echo "  get_story <issue_id>" >&2
            echo "  get_stories <epic_id>" >&2
            echo "  update_story <issue_id> <field> <value>" >&2
            echo "  transition_story <issue_id> <status> [author]" >&2
            echo "  add_comment <issue_id> <text> [author]" >&2
            echo "  search_issues <query> [type]" >&2
            exit 1
            ;;
    esac
}

main "$@"
