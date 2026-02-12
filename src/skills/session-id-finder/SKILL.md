---
name: session-id-finder
description: Get Claude Code session ID for cost tracking.
---

# Session ID Finder

## get_session_id()

```bash
MARKER="scope-session-$(uuidgen)"
echo "SESSION_MARKER: $MARKER"

PROJECT_PATH=$(pwd | sed 's|^/||; s|/|-|g')
SESSIONS_DIR="$HOME/.claude/projects/-$PROJECT_PATH"

sleep 0.5

for f in $(ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | head -5); do
    if grep -q "$MARKER" "$f" 2>/dev/null; then
        basename "$f" .jsonl
        exit 0
    fi
done

# Fallback: most recent session
ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | head -1 | xargs basename | sed 's/.jsonl$//'
```

## list_sessions()

```bash
PROJECT_PATH=$(pwd | sed 's|^/||; s|/|-|g')
ls -lt "$HOME/.claude/projects/-$PROJECT_PATH"/*.jsonl 2>/dev/null
```
