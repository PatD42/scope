---
name: project-tracking
description: Generic project tracking adapter - dispatches to configured backend based on project config
---

# Project Tracking Skill

This is a wrapper skill that dispatches to the configured tracking backend.

## Backend Selection

Local file tracking is the default. If `.scope/config.yaml` is missing, or its
`tracking` section is missing, use these values without asking the user to
choose a backend:

```yaml
tracking:
  method: arc42-c4
  skill: local-tracking-bash
  project_key: PROJECT
  base_path: ./tracking
```

Only use Jira when the active `tracking.skill` value explicitly names a Jira
backend. Comments, examples, available MCP tools, and the presence of an
Atlassian account do not select Jira. Do not ask for a Jira project key or
Atlassian URL while local tracking is active.

## Usage

**Step 1: Read config and infer guide**

```python
config = read_yaml(".scope/config.yaml") if exists(".scope/config.yaml") else {}
tracking = config.get("tracking") or {
    "skill": "local-tracking-bash",
    "method": "arc42-c4",
    "project_key": "PROJECT",
    "base_path": "./tracking",
}
backend_skill = tracking["skill"]
method = tracking["method"]

# Infer guide from method
guide_name = f"tracking-guide-{method}.md"  # e.g., "tracking-guide-arc42-c4.md"
```

**Step 2: Load tracking guide**

The guide defines the tracking structure and agent responsibilities:

```python
import os

# Try project directory first
guide_path = f"./.claude/skills/project-tracking/{guide_name}"
if not os.path.exists(guide_path):
    # Fall back to user directory (expand ~ to absolute path)
    home = os.path.expanduser("~")
    guide_path = f"{home}/.claude/skills/project-tracking/{guide_name}"

# Read guide (requires absolute path)
guide = Read(file_path=guide_path)

# The guide is now loaded into your context
# It defines:
# - Tracking structure (Epic, Story fields and workflows)
# - Agent responsibilities (who reads/writes what)
# - Critical rules (self-contained stories, developer feedback)
```

**Step 3: Load backend implementation**

Try loading from project, then user directory:

```python
import os

# Try project directory first
impl_path = f"./.claude/skills/project-tracking/{backend_skill}.md"
if not os.path.exists(impl_path):
    # Fall back to user directory (expand ~ to absolute path)
    home = os.path.expanduser("~")
    impl_path = f"{home}/.claude/skills/project-tracking/{backend_skill}.md"

# Read implementation (requires absolute path)
implementation = Read(file_path=impl_path)

# Follow the loaded implementation instructions
# All config parameters from tracking.* are available to the implementation
```

**Step 4: Follow loaded instructions**

The loaded implementation file contains all operations and usage patterns. Follow its instructions with config parameters from `config.tracking.*`.

Use the guide to understand WHAT to track and WHERE, and use the backend implementation to understand HOW to store/retrieve it.

## Efficiency Guidelines

**Story creation:**
- **Batch create when possible**: Most backends support batch operations. Create all stories in one operation, then link them to the epic (don't create+link one by one).
- **Pattern**:
  1. Collect all story data in memory
  2. Batch create stories (check backend implementation for batch_create_stories or similar)
  3. Loop to link each to epic (linking often can't be batched)

**Expected improvement**: 6 stories: 18 operations → 7 operations (1 batch create + 6 links) = 61% reduction in API calls.

**Data fetching:**
- **Use cached data when available**: Check agent_summaries for deliverables from previous steps before fetching from tracking system
- **Load once, use multiple times**: Read epic details at the start of your work, keep in memory

## Error Handling

If guide file not found, fail immediately:

```yaml
error:
  type: guide_not_found
  message: "Cannot find {guide_name} in ./.claude/skills/project-tracking/ or ~/.claude/skills/project-tracking/"
  config_value: "{config.tracking.guide}"
```

If implementation file not found, fail immediately:

```yaml
error:
  type: implementation_not_found
  message: "Cannot find {backend_skill}.md in ./.claude/skills/project-tracking/ or ~/.claude/skills/project-tracking/"
  config_value: "{config.tracking.skill}"
```

If an explicit, non-local config is incomplete:

```yaml
error:
  type: configuration_error
  message: "The selected external tracking backend is missing required configuration"
```

Do not raise a configuration error for a missing config file or missing
`tracking` section; apply the local defaults above.
