#!/bin/bash
if [ -n "$CLAUDE_TTY" ]; then
    echo -ne "\033]2;$1 $2 $3 $4 $5 $6\007" > "$CLAUDE_TTY"
else
    echo -ne "\033]2;$1 $2 $3 $4 $5 $6\007"
fi
