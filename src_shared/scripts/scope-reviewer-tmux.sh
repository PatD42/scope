#!/usr/bin/env bash
#
# Run a Scope external reviewer through a persistent tmux-backed LLM session.
#
# This is intended for subscription-backed interactive CLIs where official
# headless mode is unavailable, restricted, or undesirable. The wrapper sends
# one blocking request at a time, waits for a sentinel, retries once on timeout,
# and records review timing metadata.

set -euo pipefail

reviewer=""
model=""
session=""
llm_command=""
clear_command="/clear"
force_clear=0
prompt_file=""
output_file=""
metadata_file=""
cwd=""
timeout_seconds="${SCOPE_REVIEW_TIMEOUT_SECONDS:-3600}"
retries="${SCOPE_REVIEW_RETRIES:-1}"

usage() {
  cat >&2 <<'EOF'
Usage: scope-reviewer-tmux.sh \
  --reviewer claude|gemini \
  --model "Claude Opus 4.7" \
  --session scope_claude \
  --llm-command "claude --model opus" \
  --clear-command "/clear" \
  [--force-clear] \
  --prompt-file path \
  --output-file path \
  --metadata-file path \
  --cwd path \
  [--timeout-seconds 3600] \
  [--retries 1]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reviewer) reviewer="$2"; shift 2 ;;
    --model) model="$2"; shift 2 ;;
    --session) session="$2"; shift 2 ;;
    --llm-command) llm_command="$2"; shift 2 ;;
    --clear-command) clear_command="$2"; shift 2 ;;
    --force-clear) force_clear=1; shift ;;
    --prompt-file) prompt_file="$2"; shift 2 ;;
    --output-file) output_file="$2"; shift 2 ;;
    --metadata-file) metadata_file="$2"; shift 2 ;;
    --cwd) cwd="$2"; shift 2 ;;
    --timeout-seconds) timeout_seconds="$2"; shift 2 ;;
    --retries) retries="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

for required in reviewer model session llm_command prompt_file output_file metadata_file cwd; do
  if [[ -z "${!required}" ]]; then
    echo "Missing required argument: --${required//_/-}" >&2
    usage
    exit 2
  fi
done

json_quote() {
  python3 -c 'import json, sys; print(json.dumps(sys.argv[1]))' "$1"
}

append_metadata() {
  local status="$1"
  local started_at="$2"
  local completed_at="$3"
  local duration_seconds="$4"
  local retry_count="$5"
  local error_message="${6:-}"

  mkdir -p "$(dirname "$metadata_file")"
  if [[ ! -f "$metadata_file" ]]; then
    printf 'reviews:\n' > "$metadata_file"
  fi

  {
    printf '  - reviewer: %s\n' "$(json_quote "$reviewer")"
    printf '    model: %s\n' "$(json_quote "$model")"
    printf '    transport: "tmux"\n'
    printf '    session: %s\n' "$(json_quote "$session")"
    printf '    llm_command: %s\n' "$(json_quote "$llm_command")"
    printf '    status: %s\n' "$(json_quote "$status")"
    printf '    started_at: %s\n' "$(json_quote "$started_at")"
    printf '    completed_at: %s\n' "$(json_quote "$completed_at")"
    printf '    duration_seconds: %s\n' "$duration_seconds"
    printf '    timeout_seconds: %s\n' "$timeout_seconds"
    printf '    retry_count: %s\n' "$retry_count"
    printf '    output_file: %s\n' "$(json_quote "$output_file")"
    printf '    error: %s\n' "$(json_quote "$error_message")"
  } >> "$metadata_file"
}

send_text_to_session() {
  local target_session="$1"
  local text_file="$2"
  tmux load-buffer -b scope-reviewer "$text_file"
  tmux paste-buffer -b scope-reviewer -t "$target_session"
  tmux send-keys -t "$target_session" Enter
  tmux delete-buffer -b scope-reviewer 2>/dev/null || true
}

send_clear_if_configured() {
  if [[ -n "$clear_command" ]]; then
    local tmp_clear
    tmp_clear="$(mktemp)"
    printf '%s\n' "$clear_command" > "$tmp_clear"
    send_text_to_session "$session" "$tmp_clear"
    rm -f "$tmp_clear"
    sleep "${SCOPE_TMUX_CLEAR_WAIT_SECONDS:-2}"
  fi
}

extract_review_output() {
  local capture_file="$1"
  local start_marker="$2"
  local end_marker="$3"
  python3 - "$capture_file" "$start_marker" "$end_marker" "$output_file" <<'PY'
from pathlib import Path
import sys

capture_path, start_marker, end_marker, output_path = sys.argv[1:5]
text = Path(capture_path).read_text(errors="ignore")
start = text.rfind(start_marker)
end = text.find(end_marker, start if start != -1 else 0)

if end == -1:
    raise SystemExit("end marker not found")

if start == -1:
    body = text[:end]
else:
    body = text[start + len(start_marker):end]

Path(output_path).write_text(body.strip() + "\n")
PY
}

started_epoch="$(date +%s)"
started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
mkdir -p "$(dirname "$output_file")"

if ! command -v tmux >/dev/null 2>&1; then
  completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  duration_seconds="$(( $(date +%s) - started_epoch ))"
  echo "tmux CLI not found. Skipped ${reviewer} external review." > "$output_file"
  append_metadata "unavailable" "$started_at" "$completed_at" "$duration_seconds" 0 "tmux CLI not found"
  exit 127
fi

llm_binary="${llm_command%% *}"
if ! command -v "$llm_binary" >/dev/null 2>&1; then
  completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  duration_seconds="$(( $(date +%s) - started_epoch ))"
  echo "${llm_binary} CLI not found. Skipped ${reviewer} external review." > "$output_file"
  append_metadata "unavailable" "$started_at" "$completed_at" "$duration_seconds" 0 "${llm_binary} CLI not found"
  exit 127
fi

session_created=0
if ! tmux has-session -t "$session" 2>/dev/null; then
  tmux new-session -d -s "$session" -c "$cwd" "$llm_command"
  session_created=1
  sleep "${SCOPE_TMUX_STARTUP_SECONDS:-5}"
fi

tmux set-option -g history-limit "${SCOPE_TMUX_HISTORY_LIMIT:-200000}" >/dev/null 2>&1 || true

# Clear only when Scope starts the persistent reviewer session unless the caller
# explicitly asks for isolation before this request.
if [[ "$session_created" -eq 1 || "$force_clear" -eq 1 ]]; then
  send_clear_if_configured
fi

attempt=0
status="failed"
error_message=""
while [[ "$attempt" -le "$retries" ]]; do
  nonce="$(date +%s)-$$-${attempt}"
  start_marker="SCOPE_REVIEW_START_${reviewer}_${nonce}"
  end_marker="SCOPE_REVIEW_END_${reviewer}_${nonce}"
  request_file="$(mktemp)"
  capture_file="$(mktemp)"

  {
    printf 'You are receiving one blocking Scope external review job.\n'
    printf 'Begin your answer with this exact line and no text before it:\n%s\n' "$start_marker"
    printf 'End your answer with this exact line and no text after it:\n%s\n' "$end_marker"
    printf 'Do not edit files. Return only the requested review report.\n\n'
    cat "$prompt_file"
  } > "$request_file"

  send_text_to_session "$session" "$request_file"
  rm -f "$request_file"

  sleep "${SCOPE_TMUX_ECHO_WAIT_SECONDS:-1}"
  tmux capture-pane -t "$session" -p -S -"${SCOPE_TMUX_CAPTURE_LINES:-200000}" > "$capture_file"
  end_count="$(grep -F -c "$end_marker" "$capture_file" || true)"
  required_end_count=1
  if [[ "$end_count" -eq 1 ]]; then
    required_end_count=2
  elif [[ "$end_count" -ge 2 ]]; then
    extract_review_output "$capture_file" "$start_marker" "$end_marker"
    status="completed"
    error_message=""
    rm -f "$capture_file"
    break
  fi

  deadline=$(( $(date +%s) + timeout_seconds ))
  while [[ "$(date +%s)" -lt "$deadline" ]]; do
    tmux capture-pane -t "$session" -p -S -"${SCOPE_TMUX_CAPTURE_LINES:-200000}" > "$capture_file"
    # Interactive CLIs often echo the submitted prompt, including sentinels.
    # When we detect that echo, wait for the reviewer response occurrence too.
    if [[ "$(grep -F -c "$end_marker" "$capture_file" || true)" -ge "$required_end_count" ]]; then
      extract_review_output "$capture_file" "$start_marker" "$end_marker"
      status="completed"
      error_message=""
      rm -f "$capture_file"
      break 2
    fi
    sleep "${SCOPE_REVIEW_POLL_SECONDS:-5}"
  done

  error_message="Timed out waiting for ${reviewer} review sentinel after ${timeout_seconds}s"
  tmux send-keys -t "$session" C-c || true
  sleep 1
  send_clear_if_configured
  rm -f "$capture_file"
  attempt=$((attempt + 1))
done

completed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
duration_seconds="$(( $(date +%s) - started_epoch ))"
retry_count="$attempt"
if [[ "$retry_count" -gt "$retries" ]]; then
  retry_count="$retries"
fi

if [[ "$status" != "completed" ]]; then
  {
    echo "${reviewer} external review failed."
    echo "$error_message"
  } > "$output_file"
fi

append_metadata "$status" "$started_at" "$completed_at" "$duration_seconds" "$retry_count" "$error_message"

if [[ "$status" == "completed" ]]; then
  exit 0
fi

exit 1
