---
name: agent-summary-core
description: Minimal agent summary protocol for execution agents (Developer, SDET)
---

# Agent Summary Protocol - Core

All agents must return structured output following this protocol. Output is appended to `.scope/{epic-id}/agent_summaries.jsonl`.

**Note:** Cost tracking is in a separate file: `agent_summaries_telemetry.jsonl`

## Required Fields from Environment

**CRITICAL: Do NOT hallucinate these values. Use the tools specified to get real values.**

### Session ID
Get your actual Claude session ID using the `session-id-finder` skill:
```
Skill(skill="session-id-finder")
```
This returns your real session ID (e.g., `30c0069d-7cdb-4840-826d-2ab70bfc48e5`).

### Timestamp
Get the actual current timestamp using Bash:
```bash
date +%Y-%m-%dT%H:%M:%S%z | sed 's/\(..\)$/:\1/'
```
This returns local timezone (e.g., `2026-01-27T16:30:00-05:00`).

## AgentResult Schema

```json
{
  "agent": "string (your agent name)",
  "session_id": "string (from session-id-finder skill)",
  "task_id": "string (from TaskGet if applicable)",
  "completed_at": "string (from Bash date command)",
  "status": "success | failure | user_input",
  "work_impact": "none | minor | major",
  "phase": "string",
  "deliverables": {
    "...": "Agent-specific fields"
  },
  "handoff": {
    "summary": "string",
    "artifacts": ["object"],
    "concerns": ["object"]
  },
  "error": "string | null"
}
```

## Status Codes

| Status | Meaning | When to Use | Next Action |
|--------|---------|-------------|-------------|
| `success` | Work complete | All required work done, deliverables ready, no blocking issues | Proceed to next step |
| `failure` | Cannot proceed | Blocking issue, critical gaps in input/context, validation failures | Handle failure path or escalate |
| `user_input` | Need clarification | Ambiguities requiring user decision, multiple valid approaches | Pause, ask user, resume agent |

**Requirements:**
- `success`: Set `work_impact` (minor/major), provide `deliverables`, set `error: null`
- `failure`: Set `work_impact: none`, `deliverables: null`, populate `error` field with clear issue description
- `user_input`: Set `work_impact: none`, include `questions` list, populate `error` explaining why input needed

## Work Impact

| Impact | When to Use | Examples |
|--------|-------------|----------|
| `none` | No deliverables produced | Agent returned error, agent asked questions, validation only with no changes |
| `minor` | Review/validation work, small updates | Code review with comments, test execution report, documentation edits |
| `major` | Creating new artifacts, significant work | New features implemented, test suites created, architecture designed |

## Concern Format

Report issues to orchestrator and subsequent agents:

```json
{
  "concerns": [
    {
      "area": "string",
      "issue": "string",
      "severity": "low | medium | high"
    }
  ]
}
```

**Common areas:** business_requirements, architecture, security, epic_coverage, story_coverage, technical_risk, dependencies

**Severity:**
- `high` = blocking
- `medium` = important
- `low` = minor

**Be specific:**
- ✅ "User authentication error scenarios not covered in stories"
- ❌ "Stories incomplete"

## Examples

### Success
```json
{
  "agent": "developer",
  "session_id": "30c0069d-7cdb-4840-826d-2ab70bfc48e5",
  "task_id": "5",
  "completed_at": "2026-01-27T14:30:00-05:00",
  "status": "success",
  "work_impact": "major",
  "phase": "implementation",
  "deliverables": {
    "files_modified": ["src/auth/oauth.ts", "src/auth/tokens.ts"],
    "tests_added": 12,
    "coverage": 94
  },
  "handoff": {
    "summary": "OAuth integration complete with tests",
    "artifacts": [
      {
        "type": "story",
        "id": "CODINT-42"
      }
    ],
    "concerns": []
  },
  "error": null
}
```

### Failure
```json
{
  "agent": "developer",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "task_id": "6",
  "completed_at": "2026-01-27T15:30:00-05:00",
  "status": "failure",
  "work_impact": "none",
  "phase": "implementation",
  "deliverables": null,
  "handoff": {
    "summary": "Cannot implement without API specification",
    "concerns": [
      {
        "area": "technical_risk",
        "issue": "OAuth provider endpoints not documented in story",
        "severity": "high"
      }
    ]
  },
  "error": "Story lacks OAuth provider API endpoint documentation. Cannot implement without specification."
}
```
