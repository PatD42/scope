---
name: projectstatus
description: Show all epics with their current status
model: sonnet
tools: Read, Bash
---

# Project Status

Show all epics with their current status in reverse issue number order.

**Usage:** `/projectstatus`

## Implementation

1. Read `.scope/config.yaml` → Extract `tracking.project_key`, `tracking.skill`

2. Find tracking script:
   - Check: `./.claude/skills/project-tracking/scripts/{skill}.sh`
   - Else: `~/.claude/skills/project-tracking/scripts/{skill}.sh`
   - If not found: Error "Project tracking script not found"

3. Search epics: `bash {script} search "project = {project_key} AND type = Epic ORDER BY key DESC"`

4. Parse JSON response, extract: key, summary, status

5. Display with indicators: ✅ Done, 🔴 Blocking/Blocked, 🟢 Ready, 📝 To Do, 🟠 In Progress
