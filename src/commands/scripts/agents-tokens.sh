#!/usr/bin/env bash
# Agent Token Usage Analyzer
# Usage:
#   agents-tokens.sh --session-id <id> [--after <timestamp>] [--to <timestamp>] [--verbose|-v]
#   agents-tokens.sh --free --session-id <id>
#   agents-tokens.sh --aggregate [<agent-summaries.jsonl>] [--storeInSummaries]
#
# Session logs are found automatically by searching ~/.claude/projects/ for the session ID.
# --aggregate: If no file specified, defaults to ./agent_summaries.jsonl
# Output: JSON format

set -euo pipefail

# Default values
SESSION_ID=""
AFTER_TIMESTAMP=""
TO_TIMESTAMP=""
VERBOSE=false
FREE_MODE=false
AGGREGATE_FILE=""
STORE_IN_SUMMARIES=false
PROJECT_PATH_OVERRIDE=""

# Parse named arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --session-id)
            SESSION_ID="$2"
            shift 2
            ;;
        --after)
            AFTER_TIMESTAMP="$2"
            shift 2
            ;;
        --to)
            TO_TIMESTAMP="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --free)
            FREE_MODE=true
            shift
            ;;
        --aggregate)
            AGGREGATE_FILE="$2"
            shift 2
            ;;
        --storeInSummaries)
            STORE_IN_SUMMARIES=true
            shift
            ;;
        --project)
            PROJECT_PATH_OVERRIDE="$2"
            shift 2
            ;;
        *)
            echo '{"error": "Unknown parameter: '"$1"'"}' >&2
            echo 'Usage: agents-tokens.sh --session-id <id> [--after <timestamp>] [--to <timestamp>] [--verbose|-v]' >&2
            echo '       agents-tokens.sh --free --session-id <id>' >&2
            echo '       agents-tokens.sh --aggregate <agent-summaries.jsonl> [--storeInSummaries]' >&2
            exit 1
            ;;
    esac
done

# Check for jq dependency
if ! command -v jq &> /dev/null; then
    echo '{"error": "jq is required but not installed. Install with: brew install jq (macOS) or apt-get install jq (Linux)"}' >&2
    exit 1
fi

# Get project folder (from override or current working directory)
if [ -n "$PROJECT_PATH_OVERRIDE" ]; then
    PROJECT_PATH="$PROJECT_PATH_OVERRIDE"
else
    PROJECT_PATH="$(pwd)"
fi
FILESAFE_PATH="$(echo "$PROJECT_PATH" | sed 's/\//-/g')"

# ========== AGGREGATE MODE ==========
if [ -n "$AGGREGATE_FILE" ]; then
    # Default to ./agent_summaries.jsonl if no file specified
    if [ "$AGGREGATE_FILE" = "true" ] || [ -z "$AGGREGATE_FILE" ]; then
        AGGREGATE_FILE="./agent_summaries.jsonl"
    fi

    if [ ! -f "$AGGREGATE_FILE" ]; then
        echo "{\"error\": \"File not found: $AGGREGATE_FILE\"}" >&2
        exit 1
    fi

    # Derive telemetry filename: {basename}_telemetry.jsonl
    TELEMETRY_FILE="${AGGREGATE_FILE%.jsonl}_telemetry.jsonl"

    # Read baseline timestamp from telemetry file
    BASELINE=""
    if [ -f "$TELEMETRY_FILE" ]; then
        BASELINE=$(jq -r 'select(.type == "baseline") | .completed_at' "$TELEMETRY_FILE" | head -1)
    fi
    if [ -z "$BASELINE" ] || [ "$BASELINE" = "null" ]; then
        echo "{\"error\": \"No baseline entry found in telemetry file: $TELEMETRY_FILE\"}" >&2
        exit 1
    fi

    # Process each agent entry
    RESULTS="[]"
    TOTAL_COST=0

    while IFS= read -r line; do
        AGENT=$(echo "$line" | jq -r '.agent')
        # Skip baseline and cost_summary entries
        [ "$AGENT" = "baseline" ] && continue
        [ "$AGENT" = "cost_summary" ] && continue

        SESSION=$(echo "$line" | jq -r '.session_id')
        COMPLETED=$(echo "$line" | jq -r '.completed_at')
        TASK_ID=$(echo "$line" | jq -r '.task_id')

        if [ -n "$SESSION" ] && [ "$SESSION" != "null" ]; then
            # Get cost for this session from baseline to completed_at
            COST_DATA=$("$0" --session-id "$SESSION" --after "$BASELINE" --to "$COMPLETED" 2>&1) || true

            # Check if session log was found (error field exists and is not null)
            HAS_ERROR=$(echo "$COST_DATA" | jq -r 'if .error then "yes" else "no" end' 2>/dev/null || echo "no")
            if [ "$HAS_ERROR" = "yes" ]; then
                ERROR_MSG=$(echo "$COST_DATA" | jq -r '.error')
                RESULTS=$(echo "$RESULTS" | jq \
                    --arg agent "$AGENT" \
                    --arg session "$SESSION" \
                    --arg task_id "$TASK_ID" \
                    --arg completed "$COMPLETED" \
                    --arg error "$ERROR_MSG" \
                    '. + [{agent: $agent, session_id: $session, task_id: $task_id, completed_at: $completed, cost_usd: 0, error: $error}]')
                continue
            fi

            MAIN_COST=$(echo "$COST_DATA" | jq -r '.main_agent.total_cost_usd // 0')
            SUBAGENTS=$(echo "$COST_DATA" | jq -c '.subagents // []')
            SUBAGENT_COST=$(echo "$COST_DATA" | jq -r '[.subagents[]?.summary_statistics.total_cost_usd // 0] | add // 0')
            COMBINED_COST=$(echo "$COST_DATA" | jq -r '.combined_cost_usd // 0')

            RESULTS=$(echo "$RESULTS" | jq \
                --arg agent "$AGENT" \
                --arg session "$SESSION" \
                --arg task_id "$TASK_ID" \
                --arg completed "$COMPLETED" \
                --argjson main_cost "$MAIN_COST" \
                --argjson subagent_cost "$SUBAGENT_COST" \
                --argjson combined_cost "$COMBINED_COST" \
                --argjson subagents "$SUBAGENTS" \
                '. + [{agent: $agent, session_id: $session, task_id: $task_id, completed_at: $completed, main_cost_usd: $main_cost, subagent_cost_usd: $subagent_cost, cost_usd: $combined_cost, subagents: $subagents}]')

            TOTAL_COST=$(awk -v t="$TOTAL_COST" -v c="$COMBINED_COST" 'BEGIN {printf "%.4f", t + c}')
        fi
    done < "$AGGREGATE_FILE"

    # Generate the output JSON
    OUTPUT_JSON=$(jq -n \
        --arg baseline "$BASELINE" \
        --arg file "$AGGREGATE_FILE" \
        --argjson agents "$RESULTS" \
        --argjson total_cost "$TOTAL_COST" \
        '{baseline: $baseline, file: $file, agents: $agents, total_cost_usd: $total_cost}')

    # Output to stdout
    echo "$OUTPUT_JSON"

    # Append to telemetry file if --storeInSummaries is set
    if [ "$STORE_IN_SUMMARIES" = true ]; then
        COMPLETED_AT=$(date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/')
        COST_ENTRY=$(jq -n \
            --arg completed_at "$COMPLETED_AT" \
            --arg baseline "$BASELINE" \
            --argjson total_cost "$TOTAL_COST" \
            --argjson agents "$RESULTS" \
            '{
                type: "cost_summary",
                baseline: $baseline,
                completed_at: $completed_at,
                total_cost_usd: $total_cost,
                agents: $agents
            }')
        echo "$COST_ENTRY" >> "$TELEMETRY_FILE"
    fi
    exit 0
fi

# ========== FREE MODE ==========
if [ "$FREE_MODE" = true ]; then
    if [ -z "$SESSION_ID" ]; then
        echo '{"error": "Missing required parameter: --session-id for --free mode"}' >&2
        exit 1
    fi

    MAIN_LOG="$HOME/.claude/projects/${FILESAFE_PATH}/${SESSION_ID}.jsonl"
    if [ ! -f "$MAIN_LOG" ]; then
        echo "{\"error\": \"Session log not found: $MAIN_LOG\"}" >&2
        exit 1
    fi

    # Get current context usage from last message
    CONTEXT=$(jq -rs '
        [.[] | select(.message.usage != null)] | last |
        if . then
            (.message.usage.cache_read_input_tokens // 0) +
            (.message.usage.cache_creation_input_tokens // 0) +
            (.message.usage.input_tokens // 0) +
            (.message.usage.output_tokens // 0)
        else 0 end
    ' "$MAIN_LOG")

    # Context window is 200k for Claude
    MAX_CONTEXT=200000
    FREE=$((MAX_CONTEXT - CONTEXT))

    jq -n \
        --arg session_id "$SESSION_ID" \
        --argjson context_used "$CONTEXT" \
        --argjson context_max "$MAX_CONTEXT" \
        --argjson context_free "$FREE" \
        '{session_id: $session_id, context_used: $context_used, context_max: $context_max, context_free: $context_free}'
    exit 0
fi

# ========== STANDARD MODE ==========
# Validate required parameters
if [ -z "$SESSION_ID" ]; then
    echo '{"error": "Missing required parameter: --session-id"}' >&2
    echo 'Usage: agents-tokens.sh --session-id <id> [--after <timestamp>] [--to <timestamp>] [--verbose|-v]' >&2
    exit 1
fi

# Convert timestamps to UTC for comparison
convert_to_utc() {
    local ts=$1

    if date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        date -u -d "$ts" "+%Y-%m-%dT%H:%M:%SZ" 2>/dev/null
    else
        # BSD date (macOS)
        # First try ISO 8601 with timezone offset format
        if echo "$ts" | grep -qE '[+-][0-9]{4}$'; then
            UNIX_TS=$(date -jf "%Y-%m-%dT%H:%M:%S%z" "$ts" "+%s" 2>/dev/null)
        # Then try UTC format with Z suffix
        elif echo "$ts" | grep -qE 'Z$'; then
            TS_CLEAN=$(echo "$ts" | sed 's/\.[0-9]*Z$/Z/')
            UNIX_TS=$(TZ=UTC date -jf "%Y-%m-%dT%H:%M:%SZ" "$TS_CLEAN" "+%s" 2>/dev/null)
        else
            UNIX_TS=""
        fi

        if [ -n "$UNIX_TS" ]; then
            TZ=UTC date -r "$UNIX_TS" "+%Y-%m-%dT%H:%M:%SZ"
        else
            echo ""
        fi
    fi
}

# Calculate duration in seconds between two timestamps
calculate_duration() {
    local after_ts=$1
    local to_ts=$2

    if date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        local after_epoch=$(date -u -d "$after_ts" "+%s" 2>/dev/null)
        local to_epoch=$(date -u -d "$to_ts" "+%s" 2>/dev/null)
    else
        # BSD date (macOS)
        local after_clean=$(echo "$after_ts" | sed 's/\.[0-9]*Z$/Z/')
        local to_clean=$(echo "$to_ts" | sed 's/\.[0-9]*Z$/Z/')

        # Try ISO 8601 with timezone offset format first
        if echo "$after_ts" | grep -qE '[+-][0-9]{4}$'; then
            after_epoch=$(date -jf "%Y-%m-%dT%H:%M:%S%z" "$after_ts" "+%s" 2>/dev/null)
        else
            after_epoch=$(TZ=UTC date -jf "%Y-%m-%dT%H:%M:%SZ" "$after_clean" "+%s" 2>/dev/null)
        fi

        if echo "$to_ts" | grep -qE '[+-][0-9]{4}$'; then
            to_epoch=$(date -jf "%Y-%m-%dT%H:%M:%S%z" "$to_ts" "+%s" 2>/dev/null)
        else
            to_epoch=$(TZ=UTC date -jf "%Y-%m-%dT%H:%M:%SZ" "$to_clean" "+%s" 2>/dev/null)
        fi
    fi

    if [ -n "$after_epoch" ] && [ -n "$to_epoch" ]; then
        echo $((to_epoch - after_epoch))
    else
        echo "0"
    fi
}

# Convert input timestamps to UTC (if provided)
AFTER_TIMESTAMP_UTC=""
TO_TIMESTAMP_UTC=""

if [ -n "$AFTER_TIMESTAMP" ]; then
    AFTER_TIMESTAMP_UTC=$(convert_to_utc "$AFTER_TIMESTAMP")
    if [ -z "$AFTER_TIMESTAMP_UTC" ]; then
        echo "{\"error\": \"Could not parse --after timestamp '$AFTER_TIMESTAMP'\"}" >&2
        exit 1
    fi
fi

if [ -n "$TO_TIMESTAMP" ]; then
    TO_TIMESTAMP_UTC=$(convert_to_utc "$TO_TIMESTAMP")
    if [ -z "$TO_TIMESTAMP_UTC" ]; then
        echo "{\"error\": \"Could not parse --to timestamp '$TO_TIMESTAMP'\"}" >&2
        exit 1
    fi
fi

# Define reusable jq timestamp filter function
# This will be used throughout the script to handle optional timestamps
JQ_TIMESTAMP_FILTER='
  def timestamp_filter($has_after; $has_to; $after; $to):
    if $has_after and $has_to then
      select(.timestamp > $after and .timestamp <= $to)
    elif $has_after then
      select(.timestamp > $after)
    elif $has_to then
      select(.timestamp <= $to)
    else
      .
    end;
'

# Find main agent log by session ID (search all projects)
MAIN_LOG=$(find "$HOME/.claude/projects" -name "${SESSION_ID}.jsonl" -type f 2>/dev/null | head -1)

# Check if log exists
if [ -z "$MAIN_LOG" ] || [ ! -f "$MAIN_LOG" ]; then
    echo "{\"error\": \"Session log not found for session_id: $SESSION_ID\"}" >&2
    exit 1
fi

# Derive project path from found log location
PROJECT_PATH=$(dirname "$MAIN_LOG" | sed "s|$HOME/.claude/projects/||" | sed 's/-/\//g')
FILESAFE_PATH="$(echo "$PROJECT_PATH" | sed 's/\//-/g')"

# Calculate duration between timestamps (only if both provided)
DURATION_SECONDS=""
if [ -n "$AFTER_TIMESTAMP" ] && [ -n "$TO_TIMESTAMP" ]; then
    DURATION_SECONDS=$(calculate_duration "$AFTER_TIMESTAMP" "$TO_TIMESTAMP")
fi

# Check if after > to (return empty results)
if [ -n "$AFTER_TIMESTAMP_UTC" ] && [ -n "$TO_TIMESTAMP_UTC" ]; then
    if [[ "$AFTER_TIMESTAMP_UTC" > "$TO_TIMESTAMP_UTC" ]]; then
        if [ -n "$DURATION_SECONDS" ]; then
            jq -n \
                --arg session_id "$SESSION_ID" \
                --arg project "$PROJECT_PATH" \
                --arg after "$AFTER_TIMESTAMP" \
                --arg to "$TO_TIMESTAMP" \
                --argjson duration_seconds "$DURATION_SECONDS" \
                '{
                    session_id: $session_id,
                    project: $project,
                    log: null,
                    filter: {after: $after, to: $to},
                    duration_seconds: $duration_seconds,
                    main_agent: {
                        per_model_statistics: [],
                        total_cost_usd: 0,
                        timestamp: null,
                        context_usage: 0
                    },
                    subagents: [],
                    combined_cost_usd: 0,
                    note: "No results: --after timestamp is later than --to timestamp"
                }'
        else
            jq -n \
                --arg session_id "$SESSION_ID" \
                --arg project "$PROJECT_PATH" \
                --arg after "$AFTER_TIMESTAMP" \
                --arg to "$TO_TIMESTAMP" \
                '{
                    session_id: $session_id,
                    project: $project,
                    log: null,
                    filter: {after: $after, to: $to},
                    main_agent: {
                        per_model_statistics: [],
                        total_cost_usd: 0,
                        timestamp: null,
                        context_usage: 0
                    },
                    subagents: [],
                    combined_cost_usd: 0,
                    note: "No results: --after timestamp is later than --to timestamp"
                }'
        fi
        exit 0
    fi
fi

# Pricing table (per million tokens in USD)
get_pricing() {
    local model=$1
    case "$model" in
        *"opus-4"*)
            echo "5:6.25:0.50:25"
            ;;
        *"sonnet-4"*)
            echo "3:3.75:0.30:15"
            ;;
        *"haiku-4"*)
            echo "1:1.25:0.10:5"
            ;;
        *)
            echo "0:0:0:0"
            ;;
    esac
}

# ========== SUBAGENT TOKEN ANALYSIS FUNCTION ==========
# Embedded version of subagent-tokens.sh
# Returns JSON output for a single subagent
analyze_subagent_tokens() {
    local AGENT_ID="$1"
    local AGENT_NAME="$2"
    local AFTER_TIMESTAMP="$3"
    local TO_TIMESTAMP="$4"
    local SUBAGENT_VERBOSE="$5"

    # Validate required parameter
    if [ -z "$AGENT_ID" ]; then
        echo '{"error": "Missing required parameter: agent_id"}' >&2
        return 1
    fi

    # Convert input timestamps to UTC (use main script's convert_to_utc function)
    local AFTER_TIMESTAMP_UTC=""
    local TO_TIMESTAMP_UTC=""

    if [ -n "$AFTER_TIMESTAMP" ]; then
        AFTER_TIMESTAMP_UTC=$(convert_to_utc "$AFTER_TIMESTAMP")
        if [ -z "$AFTER_TIMESTAMP_UTC" ]; then
            echo "{\"error\": \"Could not parse --after timestamp '$AFTER_TIMESTAMP'\"}" >&2
            return 1
        fi
    fi

    if [ -n "$TO_TIMESTAMP" ]; then
        TO_TIMESTAMP_UTC=$(convert_to_utc "$TO_TIMESTAMP")
        if [ -z "$TO_TIMESTAMP_UTC" ]; then
            echo "{\"error\": \"Could not parse --to timestamp '$TO_TIMESTAMP'\"}" >&2
            return 1
        fi
    fi

    # Check if after > to (return empty results)
    if [ -n "$AFTER_TIMESTAMP_UTC" ] && [ -n "$TO_TIMESTAMP_UTC" ]; then
        if [[ "$AFTER_TIMESTAMP_UTC" > "$TO_TIMESTAMP_UTC" ]]; then
            jq -n \
                --arg agent_id "$AGENT_ID" \
                --arg agent_name "$AGENT_NAME" \
                --arg project "$PROJECT_PATH" \
                --arg after "$AFTER_TIMESTAMP" \
                --arg to "$TO_TIMESTAMP" \
                '{
                    agent_id: $agent_id,
                    agent_name: (if $agent_name == "" then null else $agent_name end),
                    project: $project,
                    log: null,
                    model: null,
                    filter: {after: $after, to: $to},
                    summary_statistics: {
                        turns: 0,
                        input_tokens: 0,
                        cache_writes_5m: 0,
                        cache_hits_and_refreshes: 0,
                        output_tokens: 0,
                        total_cost_usd: 0
                    },
                    max_context_usage: {timestamp: null, context_usage: 0},
                    note: "No results: --after timestamp is later than --to timestamp"
                }'
            return 0
        fi
    fi

    # Convert to filesafe format (use PROJECT_PATH from main script)
    local FILESAFE_PATH="$(echo "$PROJECT_PATH" | sed 's/\//-/g')"

    # Try to find agent log in new location (Claude Code 2.1.2+)
    local AGENT_LOG=""
    local PROJECT_DIR="$HOME/.claude/projects/${FILESAFE_PATH}"

    if [ -d "$PROJECT_DIR" ]; then
        # Try to find in session subdirectories first (new format)
        for session_dir in "$PROJECT_DIR"/*/; do
            session_dir="${session_dir%/}"
            if [ -d "${session_dir}/subagents" ]; then
                local candidate="${session_dir}/subagents/agent-${AGENT_ID}.jsonl"
                if [ -f "$candidate" ]; then
                    AGENT_LOG="$candidate"
                    break
                fi
            fi
        done
    fi

    # Fallback to old location (pre-2.1.2)
    if [ -z "$AGENT_LOG" ] || [ ! -f "$AGENT_LOG" ]; then
        local OLD_LOCATION="$HOME/.claude/projects/${FILESAFE_PATH}/agent-${AGENT_ID}.jsonl"
        if [ -f "$OLD_LOCATION" ]; then
            AGENT_LOG="$OLD_LOCATION"
        fi
    fi

    # Check if log was found
    if [ -z "$AGENT_LOG" ] || [ ! -f "$AGENT_LOG" ]; then
        echo "{\"error\": \"Agent log not found for agent_id=$AGENT_ID\"}" >&2
        return 1
    fi

    # Get model
    local MODEL=$(jq -rs 'first(.[] | select(.message.model != null) | .message.model)' "$AGENT_LOG")
    if [ -z "$MODEL" ] || [ "$MODEL" = "null" ]; then
        MODEL="unknown"
    fi

    # Get pricing for the model (use main script's get_pricing function)
    local PRICING=$(get_pricing "$MODEL")
    local INPUT_PRICE=$(echo "$PRICING" | cut -d':' -f1)
    local CACHE_WRITE_PRICE=$(echo "$PRICING" | cut -d':' -f2)
    local CACHE_HIT_PRICE=$(echo "$PRICING" | cut -d':' -f3)
    local OUTPUT_PRICE=$(echo "$PRICING" | cut -d':' -f4)

    # Get summary statistics
    local STATS=""
    if [ -n "$AFTER_TIMESTAMP_UTC" ] && [ -n "$TO_TIMESTAMP_UTC" ]; then
        STATS=$(jq -sr --arg after "$AFTER_TIMESTAMP_UTC" --arg to "$TO_TIMESTAMP_UTC" '
          [.[] | select(.timestamp > $after and .timestamp <= $to) | select(.message.usage != null) | .message.usage] |
          {
            turns: length,
            input_tokens: ([.[].input_tokens // 0] | add),
            cache_writes_5m: ([.[].cache_creation_input_tokens // 0] | add),
            cache_hits_and_refreshes: ([.[].cache_read_input_tokens // 0] | add),
            output_tokens: ([.[].output_tokens // 0] | add)
          } |
          "\(.turns)|\(.input_tokens)|\(.cache_writes_5m)|\(.cache_hits_and_refreshes)|\(.output_tokens)"
        ' "$AGENT_LOG")
    elif [ -n "$AFTER_TIMESTAMP_UTC" ]; then
        STATS=$(jq -sr --arg after "$AFTER_TIMESTAMP_UTC" '
          [.[] | select(.timestamp > $after) | select(.message.usage != null) | .message.usage] |
          {
            turns: length,
            input_tokens: ([.[].input_tokens // 0] | add),
            cache_writes_5m: ([.[].cache_creation_input_tokens // 0] | add),
            cache_hits_and_refreshes: ([.[].cache_read_input_tokens // 0] | add),
            output_tokens: ([.[].output_tokens // 0] | add)
          } |
          "\(.turns)|\(.input_tokens)|\(.cache_writes_5m)|\(.cache_hits_and_refreshes)|\(.output_tokens)"
        ' "$AGENT_LOG")
    elif [ -n "$TO_TIMESTAMP_UTC" ]; then
        STATS=$(jq -sr --arg to "$TO_TIMESTAMP_UTC" '
          [.[] | select(.timestamp <= $to) | select(.message.usage != null) | .message.usage] |
          {
            turns: length,
            input_tokens: ([.[].input_tokens // 0] | add),
            cache_writes_5m: ([.[].cache_creation_input_tokens // 0] | add),
            cache_hits_and_refreshes: ([.[].cache_read_input_tokens // 0] | add),
            output_tokens: ([.[].output_tokens // 0] | add)
          } |
          "\(.turns)|\(.input_tokens)|\(.cache_writes_5m)|\(.cache_hits_and_refreshes)|\(.output_tokens)"
        ' "$AGENT_LOG")
    else
        STATS=$(jq -sr '
          [.[] | select(.message.usage != null) | .message.usage] |
          {
            turns: length,
            input_tokens: ([.[].input_tokens // 0] | add),
            cache_writes_5m: ([.[].cache_creation_input_tokens // 0] | add),
            cache_hits_and_refreshes: ([.[].cache_read_input_tokens // 0] | add),
            output_tokens: ([.[].output_tokens // 0] | add)
          } |
          "\(.turns)|\(.input_tokens)|\(.cache_writes_5m)|\(.cache_hits_and_refreshes)|\(.output_tokens)"
        ' "$AGENT_LOG")
    fi

    # Validate non-empty statistics
    if [ -z "$STATS" ] || [ "$STATS" = "||||" ]; then
        echo '{"error": "No usage statistics found in agent log"}' >&2
        return 1
    fi

    # Parse stats
    local TURNS=$(echo "$STATS" | cut -d'|' -f1)
    local INPUT_TOKENS=$(echo "$STATS" | cut -d'|' -f2)
    local CACHE_WRITES=$(echo "$STATS" | cut -d'|' -f3)
    local CACHE_HITS=$(echo "$STATS" | cut -d'|' -f4)
    local OUTPUT_TOKENS=$(echo "$STATS" | cut -d'|' -f5)

    # Count compactions
    local COMPACTIONS=0
    if [ -n "$AFTER_TIMESTAMP_UTC" ] && [ -n "$TO_TIMESTAMP_UTC" ]; then
        COMPACTIONS=$(jq -sr --arg after "$AFTER_TIMESTAMP_UTC" --arg to "$TO_TIMESTAMP_UTC" '
          [.[] | select(.timestamp > $after and .timestamp <= $to) | select(.compactMetadata != null)] | length
        ' "$AGENT_LOG")
    elif [ -n "$AFTER_TIMESTAMP_UTC" ]; then
        COMPACTIONS=$(jq -sr --arg after "$AFTER_TIMESTAMP_UTC" '
          [.[] | select(.timestamp > $after) | select(.compactMetadata != null)] | length
        ' "$AGENT_LOG")
    elif [ -n "$TO_TIMESTAMP_UTC" ]; then
        COMPACTIONS=$(jq -sr --arg to "$TO_TIMESTAMP_UTC" '
          [.[] | select(.timestamp <= $to) | select(.compactMetadata != null)] | length
        ' "$AGENT_LOG")
    else
        COMPACTIONS=$(jq -sr '
          [.[] | select(.compactMetadata != null)] | length
        ' "$AGENT_LOG")
    fi

    # Calculate cost
    local TOTAL_COST=$(awk -v inp="$INPUT_TOKENS" -v inp_p="$INPUT_PRICE" \
                     -v cw="$CACHE_WRITES" -v cw_p="$CACHE_WRITE_PRICE" \
                     -v ch="$CACHE_HITS" -v ch_p="$CACHE_HIT_PRICE" \
                     -v out="$OUTPUT_TOKENS" -v out_p="$OUTPUT_PRICE" \
                     'BEGIN {
                         cost = (inp/1000000)*inp_p + (cw/1000000)*cw_p + (ch/1000000)*ch_p + (out/1000000)*out_p
                         printf "%.4f", cost
                     }')

    # Get max context usage with timestamp
    local CONTEXT_RESULT=""
    if [ -n "$AFTER_TIMESTAMP_UTC" ] && [ -n "$TO_TIMESTAMP_UTC" ]; then
        CONTEXT_RESULT=$(jq -sr --arg after "$AFTER_TIMESTAMP_UTC" --arg to "$TO_TIMESTAMP_UTC" '
          [.[] | select(.timestamp > $after and .timestamp <= $to) | select(.message.usage != null)] |
          if length > 0 then
            map({
              timestamp: .timestamp,
              window: ((.message.usage.cache_read_input_tokens // 0) +
                       (.message.usage.cache_creation_input_tokens // 0) +
                       (.message.usage.input_tokens // 0) +
                       (.message.usage.output_tokens // 0))
            }) |
            max_by(.window) |
            {timestamp, context_usage: .window}
          else
            {timestamp: null, context_usage: 0}
          end
        ' "$AGENT_LOG")
    elif [ -n "$AFTER_TIMESTAMP_UTC" ]; then
        CONTEXT_RESULT=$(jq -sr --arg after "$AFTER_TIMESTAMP_UTC" '
          [.[] | select(.timestamp > $after) | select(.message.usage != null)] |
          if length > 0 then
            map({
              timestamp: .timestamp,
              window: ((.message.usage.cache_read_input_tokens // 0) +
                       (.message.usage.cache_creation_input_tokens // 0) +
                       (.message.usage.input_tokens // 0) +
                       (.message.usage.output_tokens // 0))
            }) |
            max_by(.window) |
            {timestamp, context_usage: .window}
          else
            {timestamp: null, context_usage: 0}
          end
        ' "$AGENT_LOG")
    elif [ -n "$TO_TIMESTAMP_UTC" ]; then
        CONTEXT_RESULT=$(jq -sr --arg to "$TO_TIMESTAMP_UTC" '
          [.[] | select(.timestamp <= $to) | select(.message.usage != null)] |
          if length > 0 then
            map({
              timestamp: .timestamp,
              window: ((.message.usage.cache_read_input_tokens // 0) +
                       (.message.usage.cache_creation_input_tokens // 0) +
                       (.message.usage.input_tokens // 0) +
                       (.message.usage.output_tokens // 0))
            }) |
            max_by(.window) |
            {timestamp, context_usage: .window}
          else
            {timestamp: null, context_usage: 0}
          end
        ' "$AGENT_LOG")
    else
        CONTEXT_RESULT=$(jq -sr '
          [.[] | select(.message.usage != null)] |
          if length > 0 then
            map({
              timestamp: .timestamp,
              window: ((.message.usage.cache_read_input_tokens // 0) +
                       (.message.usage.cache_creation_input_tokens // 0) +
                       (.message.usage.input_tokens // 0) +
                       (.message.usage.output_tokens // 0))
            }) |
            max_by(.window) |
            {timestamp, context_usage: .window}
          else
            {timestamp: null, context_usage: 0}
          end
        ' "$AGENT_LOG")
    fi

    # Convert timestamp to local timezone
    local TS=$(echo "$CONTEXT_RESULT" | jq -r '.timestamp')
    local WINDOW=$(echo "$CONTEXT_RESULT" | jq -r '.context_usage')

    local LOCAL_TS="null"
    if [ "$TS" != "null" ] && [ -n "$TS" ]; then
        local TS_CLEAN=$(echo "$TS" | sed 's/\.[0-9]*Z$/Z/')

        if date --version >/dev/null 2>&1; then
            # GNU date (Linux)
            LOCAL_TS=$(date -d "$TS_CLEAN" "+%Y-%m-%dT%H:%M:%S%z")
        else
            # BSD date (macOS)
            local UNIX_TS=$(TZ=UTC date -jf "%Y-%m-%dT%H:%M:%SZ" "$TS_CLEAN" "+%s" 2>/dev/null)
            if [ -n "$UNIX_TS" ]; then
                LOCAL_TS=$(date -r "$UNIX_TS" "+%Y-%m-%dT%H:%M:%S%z")
            else
                LOCAL_TS="$TS"
            fi
        fi
    else
        WINDOW=0
    fi

    # Build JSON output (without verbose)
    if [ "$SUBAGENT_VERBOSE" != "true" ]; then
        jq -n \
            --arg agent_id "$AGENT_ID" \
            --arg agent_name "$AGENT_NAME" \
            --arg project "$PROJECT_PATH" \
            --arg log "$AGENT_LOG" \
            --arg model "$MODEL" \
            --arg after "${AFTER_TIMESTAMP:-null}" \
            --arg to "${TO_TIMESTAMP:-null}" \
            --argjson turns "$TURNS" \
            --argjson compactions "$COMPACTIONS" \
            --argjson input_tokens "$INPUT_TOKENS" \
            --argjson cache_writes "$CACHE_WRITES" \
            --argjson cache_hits "$CACHE_HITS" \
            --argjson output_tokens "$OUTPUT_TOKENS" \
            --argjson total_cost "$TOTAL_COST" \
            --arg timestamp "$LOCAL_TS" \
            --argjson context_usage "$WINDOW" \
            '{
                agent_id: $agent_id,
                agent_name: (if $agent_name == "" or $agent_name == "null" then null else $agent_name end),
                project: $project,
                log: $log,
                model: $model,
                filter: {
                    after: (if $after == "null" then null else $after end),
                    to: (if $to == "null" then null else $to end)
                },
                summary_statistics: {
                    turns: $turns,
                    compactions: $compactions,
                    input_tokens: $input_tokens,
                    cache_writes_5m: $cache_writes,
                    cache_hits_and_refreshes: $cache_hits,
                    output_tokens: $output_tokens,
                    total_cost_usd: $total_cost
                },
                max_context_usage: {
                    timestamp: (if $timestamp == "null" then null else $timestamp end),
                    context_usage: $context_usage
                }
            }'
    else
        # Get turn-by-turn data for verbose output
        local TURNS_DATA=""
        if [ -n "$AFTER_TIMESTAMP_UTC" ] && [ -n "$TO_TIMESTAMP_UTC" ]; then
            TURNS_DATA=$(jq -r --arg after "$AFTER_TIMESTAMP_UTC" --arg to "$TO_TIMESTAMP_UTC" '
              select(.timestamp > $after and .timestamp <= $to) | select(.message.usage != null) |
              [
                .timestamp,
                (.message.usage.input_tokens // 0),
                (.message.usage.cache_creation_input_tokens // 0),
                (.message.usage.cache_read_input_tokens // 0),
                (.message.usage.output_tokens // 0),
                ((.message.usage.cache_read_input_tokens // 0) +
                 (.message.usage.cache_creation_input_tokens // 0) +
                 (.message.usage.input_tokens // 0) +
                 (.message.usage.output_tokens // 0))
              ] | @tsv
            ' "$AGENT_LOG")
        elif [ -n "$AFTER_TIMESTAMP_UTC" ]; then
            TURNS_DATA=$(jq -r --arg after "$AFTER_TIMESTAMP_UTC" '
              select(.timestamp > $after) | select(.message.usage != null) |
              [
                .timestamp,
                (.message.usage.input_tokens // 0),
                (.message.usage.cache_creation_input_tokens // 0),
                (.message.usage.cache_read_input_tokens // 0),
                (.message.usage.output_tokens // 0),
                ((.message.usage.cache_read_input_tokens // 0) +
                 (.message.usage.cache_creation_input_tokens // 0) +
                 (.message.usage.input_tokens // 0) +
                 (.message.usage.output_tokens // 0))
              ] | @tsv
            ' "$AGENT_LOG")
        elif [ -n "$TO_TIMESTAMP_UTC" ]; then
            TURNS_DATA=$(jq -r --arg to "$TO_TIMESTAMP_UTC" '
              select(.timestamp <= $to) | select(.message.usage != null) |
              [
                .timestamp,
                (.message.usage.input_tokens // 0),
                (.message.usage.cache_creation_input_tokens // 0),
                (.message.usage.cache_read_input_tokens // 0),
                (.message.usage.output_tokens // 0),
                ((.message.usage.cache_read_input_tokens // 0) +
                 (.message.usage.cache_creation_input_tokens // 0) +
                 (.message.usage.input_tokens // 0) +
                 (.message.usage.output_tokens // 0))
              ] | @tsv
            ' "$AGENT_LOG")
        else
            TURNS_DATA=$(jq -r '
              select(.message.usage != null) |
              [
                .timestamp,
                (.message.usage.input_tokens // 0),
                (.message.usage.cache_creation_input_tokens // 0),
                (.message.usage.cache_read_input_tokens // 0),
                (.message.usage.output_tokens // 0),
                ((.message.usage.cache_read_input_tokens // 0) +
                 (.message.usage.cache_creation_input_tokens // 0) +
                 (.message.usage.input_tokens // 0) +
                 (.message.usage.output_tokens // 0))
              ] | @tsv
            ' "$AGENT_LOG")
        fi

        # Build turn-by-turn array
        local TURN_ARRAY="[]"
        while IFS=$'\t' read -r ts input cache_writes cache_hits output window; do
            if [ -n "$ts" ]; then
                # Convert timestamp to local
                local ts_clean=$(echo "$ts" | sed 's/\.[0-9]*Z$/Z/')
                local local_ts=""
                if date --version >/dev/null 2>&1; then
                    local_ts=$(date -d "$ts_clean" "+%Y-%m-%dT%H:%M:%S%z")
                else
                    local unix_ts=$(TZ=UTC date -jf "%Y-%m-%dT%H:%M:%SZ" "$ts_clean" "+%s" 2>/dev/null)
                    if [ -n "$unix_ts" ]; then
                        local_ts=$(date -r "$unix_ts" "+%Y-%m-%dT%H:%M:%S%z")
                    else
                        local_ts="$ts"
                    fi
                fi

                TURN_ARRAY=$(echo "$TURN_ARRAY" | jq \
                    --arg timestamp "$local_ts" \
                    --argjson input "$input" \
                    --argjson cache_writes "$cache_writes" \
                    --argjson cache_hits "$cache_hits" \
                    --argjson output "$output" \
                    --argjson window "$window" \
                    '. + [{timestamp: $timestamp, input: $input, cache_writes_5m: $cache_writes, cache_hits: $cache_hits, output: $output, window: $window}]')
            fi
        done <<< "$TURNS_DATA"

        # Output with verbose data
        jq -n \
            --arg agent_id "$AGENT_ID" \
            --arg agent_name "$AGENT_NAME" \
            --arg project "$PROJECT_PATH" \
            --arg log "$AGENT_LOG" \
            --arg model "$MODEL" \
            --arg after "${AFTER_TIMESTAMP:-null}" \
            --arg to "${TO_TIMESTAMP:-null}" \
            --argjson turns "$TURNS" \
            --argjson compactions "$COMPACTIONS" \
            --argjson input_tokens "$INPUT_TOKENS" \
            --argjson cache_writes "$CACHE_WRITES" \
            --argjson cache_hits "$CACHE_HITS" \
            --argjson output_tokens "$OUTPUT_TOKENS" \
            --argjson total_cost "$TOTAL_COST" \
            --arg timestamp "$LOCAL_TS" \
            --argjson context_usage "$WINDOW" \
            --argjson turn_by_turn "$TURN_ARRAY" \
            '{
                agent_id: $agent_id,
                agent_name: (if $agent_name == "" or $agent_name == "null" then null else $agent_name end),
                project: $project,
                log: $log,
                model: $model,
                filter: {
                    after: (if $after == "null" then null else $after end),
                    to: (if $to == "null" then null else $to end)
                },
                summary_statistics: {
                    turns: $turns,
                    compactions: $compactions,
                    input_tokens: $input_tokens,
                    cache_writes_5m: $cache_writes,
                    cache_hits_and_refreshes: $cache_hits,
                    output_tokens: $output_tokens,
                    total_cost_usd: $total_cost
                },
                max_context_usage: {
                    timestamp: (if $timestamp == "null" then null else $timestamp end),
                    context_usage: $context_usage
                },
                turn_by_turn: $turn_by_turn
            }'
    fi
}

# Get list of unique models used (with conditional timestamp filtering)
MODELS=$(jq -rs \
  --arg after "$AFTER_TIMESTAMP_UTC" \
  --arg to "$TO_TIMESTAMP_UTC" \
  --argjson has_after "$([ -n "$AFTER_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" \
  --argjson has_to "$([ -n "$TO_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" '

  [.[] |
    # Conditional timestamp filtering
    if $has_after and $has_to then
      select(.timestamp > $after and .timestamp <= $to)
    elif $has_after then
      select(.timestamp > $after)
    elif $has_to then
      select(.timestamp <= $to)
    else
      .
    end |
    select(.message.model != null) |
    .message.model
  ] |
  unique |
  .[]
' "$MAIN_LOG")

# Check if any models found
if [ -z "$MODELS" ]; then
    if [ -n "$DURATION_SECONDS" ]; then
        jq -n \
            --arg session_id "$SESSION_ID" \
            --arg project "$PROJECT_PATH" \
            --arg log "$MAIN_LOG" \
            --arg after "$AFTER_TIMESTAMP" \
            --arg to "$TO_TIMESTAMP" \
            --argjson duration_seconds "$DURATION_SECONDS" \
            '{
                session_id: $session_id,
                project: $project,
                log: $log,
                filter: {after: $after, to: $to},
                duration_seconds: $duration_seconds,
                main_agent: {
                    per_model_statistics: [],
                    total_cost_usd: 0,
                    timestamp: null,
                    context_usage: 0
                },
                subagents: [],
                combined_cost_usd: 0
            }'
    else
        jq -n \
            --arg session_id "$SESSION_ID" \
            --arg project "$PROJECT_PATH" \
            --arg log "$MAIN_LOG" \
            --arg after "$AFTER_TIMESTAMP" \
            --arg to "$TO_TIMESTAMP" \
            '{
                session_id: $session_id,
                project: $project,
                log: $log,
                filter: {after: $after, to: $to},
                main_agent: {
                    per_model_statistics: [],
                    total_cost_usd: 0,
                    timestamp: null,
                    context_usage: 0
                },
                subagents: [],
                combined_cost_usd: 0
            }'
    fi
    exit 0
fi

# Build per-model statistics array
MODEL_STATS_ARRAY="[]"
TOTAL_COST=0

while IFS= read -r MODEL; do
    # Get pricing for this model
    PRICING=$(get_pricing "$MODEL")
    INPUT_PRICE=$(echo "$PRICING" | cut -d':' -f1)
    CACHE_WRITE_PRICE=$(echo "$PRICING" | cut -d':' -f2)
    CACHE_HIT_PRICE=$(echo "$PRICING" | cut -d':' -f3)
    OUTPUT_PRICE=$(echo "$PRICING" | cut -d':' -f4)

    # Get statistics for this model (with conditional timestamp filtering)
    STATS=$(jq -sr \
      --arg after "$AFTER_TIMESTAMP_UTC" \
      --arg to "$TO_TIMESTAMP_UTC" \
      --argjson has_after "$([ -n "$AFTER_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" \
      --argjson has_to "$([ -n "$TO_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" \
      --arg model "$MODEL" '

      [.[] |
        # Conditional timestamp filtering
        if $has_after and $has_to then
          select(.timestamp > $after and .timestamp <= $to)
        elif $has_after then
          select(.timestamp > $after)
        elif $has_to then
          select(.timestamp <= $to)
        else
          .
        end |
        select(.message.model == $model) |
        select(.message.usage != null) |
        .message.usage
      ] |
      {
        turns: length,
        input_tokens: ([.[].input_tokens // 0] | add),
        cache_writes_5m: ([.[].cache_creation_input_tokens // 0] | add),
        cache_hits_and_refreshes: ([.[].cache_read_input_tokens // 0] | add),
        output_tokens: ([.[].output_tokens // 0] | add)
      } |
      "\(.turns)|\(.input_tokens)|\(.cache_writes_5m)|\(.cache_hits_and_refreshes)|\(.output_tokens)"
    ' "$MAIN_LOG")

    # Parse stats
    TURNS=$(echo "$STATS" | cut -d'|' -f1)
    INPUT_TOKENS=$(echo "$STATS" | cut -d'|' -f2)
    CACHE_WRITES=$(echo "$STATS" | cut -d'|' -f3)
    CACHE_HITS=$(echo "$STATS" | cut -d'|' -f4)
    OUTPUT_TOKENS=$(echo "$STATS" | cut -d'|' -f5)

    # Calculate cost for this model (prices are per million tokens)
    MODEL_COST=$(awk -v inp="$INPUT_TOKENS" -v inp_p="$INPUT_PRICE" \
                     -v cw="$CACHE_WRITES" -v cw_p="$CACHE_WRITE_PRICE" \
                     -v ch="$CACHE_HITS" -v ch_p="$CACHE_HIT_PRICE" \
                     -v out="$OUTPUT_TOKENS" -v out_p="$OUTPUT_PRICE" \
                     'BEGIN {
                         cost = (inp/1000000)*inp_p + (cw/1000000)*cw_p + (ch/1000000)*ch_p + (out/1000000)*out_p
                         printf "%.4f", cost
                     }')

    # Add to total cost
    TOTAL_COST=$(awk -v total="$TOTAL_COST" -v model="$MODEL_COST" 'BEGIN { printf "%.4f", total + model }')

    # Add model stats to array
    MODEL_STATS_ARRAY=$(echo "$MODEL_STATS_ARRAY" | jq \
        --arg model "$MODEL" \
        --argjson turns "$TURNS" \
        --argjson input_tokens "$INPUT_TOKENS" \
        --argjson cache_writes "$CACHE_WRITES" \
        --argjson cache_hits "$CACHE_HITS" \
        --argjson output_tokens "$OUTPUT_TOKENS" \
        --argjson cost_usd "$MODEL_COST" \
        '. + [{model: $model, turns: $turns, input_tokens: $input_tokens, cache_writes_5m: $cache_writes, cache_hits_and_refreshes: $cache_hits, output_tokens: $output_tokens, cost_usd: $cost_usd}]')
done <<< "$MODELS"

# ========== SUBAGENT INTEGRATION ==========
# Extract subagent IDs and names from Task tool calls

# Extract unique subagent IDs and names within timestamp range
# Format: agent_id|agent_name (e.g., "a796124|product-owner-haiku")
SUBAGENT_DATA=$(jq -rs \
  --arg after "$AFTER_TIMESTAMP_UTC" \
  --arg to "$TO_TIMESTAMP_UTC" \
  --argjson has_after "$([ -n "$AFTER_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" \
  --argjson has_to "$([ -n "$TO_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" '

  # Extract tool_use messages (Task calls with subagent_type)
  ([.[] |
    # Conditional timestamp filtering
    if $has_after and $has_to then
      select(.timestamp > $after and .timestamp <= $to)
    elif $has_after then
      select(.timestamp > $after)
    elif $has_to then
      select(.timestamp <= $to)
    else
      .
    end |
    select(.message.content != null) |
    select(.message.content | type == "array") |
    .message.content[] |
    select(.type == "tool_use") |
    select(.name == "Task") |
    select(.input.subagent_type != null) |
    {
      tool_use_id: .id,
      agent_name: .input.subagent_type
    }
  ]) as $tool_uses |
  # Extract tool_result messages (agentId in result)
  ([.[] |
    # Conditional timestamp filtering
    if $has_after and $has_to then
      select(.timestamp > $after and .timestamp <= $to)
    elif $has_after then
      select(.timestamp > $after)
    elif $has_to then
      select(.timestamp <= $to)
    else
      .
    end |
    select(.message.content != null) |
    select(.message.content | type == "array") |
    .message.content[] |
    select(.type == "tool_result") |
    {
      tool_use_id: .tool_use_id,
      content_text: (
        if (.content | type == "string") then
          .content
        elif (.content | type == "array") then
          [.content[] | select(.type == "text") | .text] | join(" ")
        else
          ""
        end
      )
    } |
    select(.content_text != "") |
    select(.content_text | test("agentId")) |
    {
      tool_use_id: .tool_use_id,
      agent_id: (.content_text | capture("agentId:\\s*(?<id>[a-f0-9]+)"; "i").id // null)
    } |
    select(.agent_id != null)
  ]) as $tool_results |
  # Match tool_use with tool_result by tool_use_id
  [$tool_uses[] as $use |
   $tool_results[] as $result |
   select($use.tool_use_id == $result.tool_use_id) |
   {
     agent_id: $result.agent_id,
     agent_name: $use.agent_name
   }
  ] |
  # Get unique combinations
  unique_by(.agent_id) |
  .[] |
  "\(.agent_id)|\(.agent_name)"
' "$MAIN_LOG")

# Process each subagent
SUBAGENTS_ARRAY="[]"

if [ -n "$SUBAGENT_DATA" ]; then
    while IFS='|' read -r AGENT_ID AGENT_NAME; do
        if [ -n "$AGENT_ID" ]; then
            # Call embedded analyze_subagent_tokens function
            SUBAGENT_RESULT=$(analyze_subagent_tokens "$AGENT_ID" "$AGENT_NAME" "$AFTER_TIMESTAMP" "$TO_TIMESTAMP" "$VERBOSE" 2>/dev/null)

            # Add to array if successful
            if [ $? -eq 0 ] && [ -n "$SUBAGENT_RESULT" ]; then
                SUBAGENTS_ARRAY=$(echo "$SUBAGENTS_ARRAY" | jq --argjson sub "$SUBAGENT_RESULT" '. + [$sub]')
            fi
        fi
    done <<< "$SUBAGENT_DATA"
fi

# Calculate combined cost (main + all subagents)
COMBINED_COST=$(echo "$SUBAGENTS_ARRAY" | jq -r '
  [.[].summary_statistics.total_cost_usd] | add // 0
' | awk -v main="$TOTAL_COST" '{printf "%.4f", main + $1}')

# Get timestamp and context usage from last non-zero cost transaction (with conditional timestamp filtering)
RESULT=$(jq -sr \
  --arg after "$AFTER_TIMESTAMP_UTC" \
  --arg to "$TO_TIMESTAMP_UTC" \
  --argjson has_after "$([ -n "$AFTER_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" \
  --argjson has_to "$([ -n "$TO_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" '

  [.[] |
    # Conditional timestamp filtering
    if $has_after and $has_to then
      select(.timestamp > $after and .timestamp <= $to)
    elif $has_after then
      select(.timestamp > $after)
    elif $has_to then
      select(.timestamp <= $to)
    else
      .
    end |
    select(.message.usage != null)
  ] |
  map({
    timestamp: .timestamp,
    usage: .message.usage,
    window: ((.message.usage.cache_read_input_tokens // 0) +
             (.message.usage.cache_creation_input_tokens // 0) +
             (.message.usage.input_tokens // 0) +
             (.message.usage.output_tokens // 0)),
    has_cost: (
      ((.message.usage.input_tokens // 0) > 0) or
      ((.message.usage.cache_creation_input_tokens // 0) > 0) or
      ((.message.usage.cache_read_input_tokens // 0) > 0) or
      ((.message.usage.output_tokens // 0) > 0)
    )
  }) |
  map(select(.has_cost == true)) |
  if length > 0 then
    last |
    "\(.timestamp)|\(.window)"
  else
    "null|0"
  end
' "$MAIN_LOG")

# Parse result and convert timestamp to local timezone
TS=$(echo "$RESULT" | cut -d'|' -f1)
WINDOW=$(echo "$RESULT" | cut -d'|' -f2)

if [ "$TS" != "null" ] && [ -n "$TS" ]; then
    # Strip milliseconds and Z suffix, convert to local timezone
    TS_CLEAN=$(echo "$TS" | sed 's/\.[0-9]*Z$/Z/')

    if date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        LOCAL_TS=$(date -d "$TS_CLEAN" "+%Y-%m-%dT%H:%M:%S%z")
    else
        # BSD date (macOS)
        UNIX_TS=$(TZ=UTC date -jf "%Y-%m-%dT%H:%M:%SZ" "$TS_CLEAN" "+%s" 2>/dev/null)
        if [ -n "$UNIX_TS" ]; then
            LOCAL_TS=$(date -r "$UNIX_TS" "+%Y-%m-%dT%H:%M:%S%z")
        else
            LOCAL_TS="$TS"
        fi
    fi
else
    LOCAL_TS="null"
    WINDOW=0
fi

# Build JSON output (without verbose)
if [ "$VERBOSE" = false ]; then
    if [ -n "$DURATION_SECONDS" ]; then
        jq -n \
            --arg session_id "$SESSION_ID" \
            --arg project "$PROJECT_PATH" \
            --arg log "$MAIN_LOG" \
            --arg after "$AFTER_TIMESTAMP" \
            --arg to "$TO_TIMESTAMP" \
            --argjson duration_seconds "$DURATION_SECONDS" \
            --argjson per_model_statistics "$MODEL_STATS_ARRAY" \
            --argjson total_cost "$TOTAL_COST" \
            --arg timestamp "$LOCAL_TS" \
            --argjson context_usage "$WINDOW" \
            --argjson subagents "$SUBAGENTS_ARRAY" \
            --argjson combined_cost "$COMBINED_COST" \
            '{
                session_id: $session_id,
                project: $project,
                log: $log,
                filter: {after: $after, to: $to},
                duration_seconds: $duration_seconds,
                main_agent: {
                    per_model_statistics: $per_model_statistics,
                    total_cost_usd: $total_cost,
                    timestamp: (if $timestamp == "null" then null else $timestamp end),
                    context_usage: $context_usage
                },
                subagents: $subagents,
                combined_cost_usd: $combined_cost
            }'
    else
        jq -n \
            --arg session_id "$SESSION_ID" \
            --arg project "$PROJECT_PATH" \
            --arg log "$MAIN_LOG" \
            --arg after "$AFTER_TIMESTAMP" \
            --arg to "$TO_TIMESTAMP" \
            --argjson per_model_statistics "$MODEL_STATS_ARRAY" \
            --argjson total_cost "$TOTAL_COST" \
            --arg timestamp "$LOCAL_TS" \
            --argjson context_usage "$WINDOW" \
            --argjson subagents "$SUBAGENTS_ARRAY" \
            --argjson combined_cost "$COMBINED_COST" \
            '{
                session_id: $session_id,
                project: $project,
                log: $log,
                filter: {after: $after, to: $to},
                main_agent: {
                    per_model_statistics: $per_model_statistics,
                    total_cost_usd: $total_cost,
                    timestamp: (if $timestamp == "null" then null else $timestamp end),
                    context_usage: $context_usage
                },
                subagents: $subagents,
                combined_cost_usd: $combined_cost
            }'
    fi
else
    # Helper function to convert UTC timestamp to local timezone
    convert_to_local_tz() {
        local ts=$1
        # Strip milliseconds and Z suffix
        local ts_clean=$(echo "$ts" | sed 's/\.[0-9]*Z$/Z/')

        if date --version >/dev/null 2>&1; then
            # GNU date (Linux)
            date -d "$ts_clean" "+%Y-%m-%dT%H:%M:%S%z"
        else
            # BSD date (macOS) - convert via Unix timestamp
            local unix_ts=$(TZ=UTC date -jf "%Y-%m-%dT%H:%M:%SZ" "$ts_clean" "+%s" 2>/dev/null)
            if [ -n "$unix_ts" ]; then
                date -r "$unix_ts" "+%Y-%m-%dT%H:%M:%S%z"
            else
                # Fallback to original timestamp if conversion fails
                echo "$ts"
            fi
        fi
    }

    # Get turn-by-turn data (with conditional timestamp filtering)
    TURNS_DATA=$(jq -r \
      --arg after "$AFTER_TIMESTAMP_UTC" \
      --arg to "$TO_TIMESTAMP_UTC" \
      --argjson has_after "$([ -n "$AFTER_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" \
      --argjson has_to "$([ -n "$TO_TIMESTAMP_UTC" ] && echo 'true' || echo 'false')" '

      # Conditional timestamp filtering
      if $has_after and $has_to then
        select(.timestamp > $after and .timestamp <= $to)
      elif $has_after then
        select(.timestamp > $after)
      elif $has_to then
        select(.timestamp <= $to)
      else
        .
      end |
      select(.message.usage != null) |
      [
        .timestamp,
        (.message.model // "unknown"),
        (.message.usage.input_tokens // 0),
        (.message.usage.cache_creation_input_tokens // 0),
        (.message.usage.cache_read_input_tokens // 0),
        (.message.usage.output_tokens // 0),
        ((.message.usage.cache_read_input_tokens // 0) +
         (.message.usage.cache_creation_input_tokens // 0) +
         (.message.usage.input_tokens // 0) +
         (.message.usage.output_tokens // 0))
      ] | @tsv
    ' "$MAIN_LOG")

    # Build turn-by-turn array
    TURN_ARRAY="[]"
    while IFS=$'\t' read -r ts model input cache_writes cache_hits output window; do
        if [ -n "$ts" ]; then
            # Convert timestamp to local
            local_ts=$(convert_to_local_tz "$ts")

            TURN_ARRAY=$(echo "$TURN_ARRAY" | jq \
                --arg timestamp "$local_ts" \
                --arg model "$model" \
                --argjson input "$input" \
                --argjson cache_writes "$cache_writes" \
                --argjson cache_hits "$cache_hits" \
                --argjson output "$output" \
                --argjson window "$window" \
                '. + [{timestamp: $timestamp, model: $model, input: $input, cache_writes_5m: $cache_writes, cache_hits: $cache_hits, output: $output, window: $window}]')
        fi
    done <<< "$TURNS_DATA"

    # Output with verbose data
    if [ -n "$DURATION_SECONDS" ]; then
        jq -n \
            --arg session_id "$SESSION_ID" \
            --arg project "$PROJECT_PATH" \
            --arg log "$MAIN_LOG" \
            --arg after "$AFTER_TIMESTAMP" \
            --arg to "$TO_TIMESTAMP" \
            --argjson duration_seconds "$DURATION_SECONDS" \
            --argjson per_model_statistics "$MODEL_STATS_ARRAY" \
            --argjson total_cost "$TOTAL_COST" \
            --arg timestamp "$LOCAL_TS" \
            --argjson context_usage "$WINDOW" \
            --argjson turn_by_turn "$TURN_ARRAY" \
            --argjson subagents "$SUBAGENTS_ARRAY" \
            --argjson combined_cost "$COMBINED_COST" \
            '{
                session_id: $session_id,
                project: $project,
                log: $log,
                filter: {after: $after, to: $to},
                duration_seconds: $duration_seconds,
                main_agent: {
                    per_model_statistics: $per_model_statistics,
                    total_cost_usd: $total_cost,
                    timestamp: (if $timestamp == "null" then null else $timestamp end),
                    context_usage: $context_usage,
                    turn_by_turn: $turn_by_turn
                },
                subagents: $subagents,
                combined_cost_usd: $combined_cost
            }'
    else
        jq -n \
            --arg session_id "$SESSION_ID" \
            --arg project "$PROJECT_PATH" \
            --arg log "$MAIN_LOG" \
            --arg after "$AFTER_TIMESTAMP" \
            --arg to "$TO_TIMESTAMP" \
            --argjson per_model_statistics "$MODEL_STATS_ARRAY" \
            --argjson total_cost "$TOTAL_COST" \
            --arg timestamp "$LOCAL_TS" \
            --argjson context_usage "$WINDOW" \
            --argjson turn_by_turn "$TURN_ARRAY" \
            --argjson subagents "$SUBAGENTS_ARRAY" \
            --argjson combined_cost "$COMBINED_COST" \
            '{
                session_id: $session_id,
                project: $project,
                log: $log,
                filter: {after: $after, to: $to},
                main_agent: {
                    per_model_statistics: $per_model_statistics,
                    total_cost_usd: $total_cost,
                    timestamp: (if $timestamp == "null" then null else $timestamp end),
                    context_usage: $context_usage,
                    turn_by_turn: $turn_by_turn
                },
                subagents: $subagents,
                combined_cost_usd: $combined_cost
            }'
    fi
fi
