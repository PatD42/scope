---
name: agent-summary-complex
description: Full agent summary protocol for coordination agents (PO, Architect, Epic Housekeeping)
---

# Agent Summary Protocol - Complex

All agents return structured output appended to `.scope/{epic-id}/agent_summaries.jsonl` for use by subsequent agents and orchestrator.

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
- `failure`: Set `work_impact: none`, `deliverables: null`, populate `error` with clear issue description
- `user_input`: Set `work_impact: none`, include `questions` list or use AskUserQuestion tool, populate `error`

## Work Impact

| Impact | When to Use | Examples |
|--------|-------------|----------|
| `none` | No deliverables | Agent returned error, agent asked questions, validation only |
| `minor` | Review/validation, small updates | Reviewing architect's work, small documentation updates, analyzing existing artifacts |
| `major` | Creating new artifacts | Architecture diagrams, ADRs, file plans, stories, epic documentation, test plans |

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

**Common areas:**
- `business_requirements` - Product/business issues
- `architecture` - Technical design issues
- `security` - Security concerns
- `epic_coverage` - Epic requirements not fully covered
- `story_coverage` - Story gaps or quality issues
- `technical_risk` - Implementation risks
- `dependencies` - Blocking dependencies

**Be specific:**
- ✅ "OAuth token storage strategy not specified in epic"
- ❌ "Epic incomplete"

**Severity guidelines:**
- `high` - Blocking issue, must be addressed before proceeding
- `medium` - Important issue, should be addressed soon
- `low` - Minor issue, can be addressed later

## Handoff Artifacts

Document what was created or updated for traceability:

```json
{
  "handoff": {
    "artifacts": [
      {
        "type": "string",
        "id": "string",
        "title": "string (optional)",
        "location": "string (optional)"
      }
    ]
  }
}
```

**Common artifact types:**

| Type | Description | Used By |
|------|-------------|---------|
| `epic_validation` | Epic business validation | Product Owner |
| `architecture` | Architecture design + diagrams | Architect |
| `adr` | Architecture Decision Record | Architect |
| `story` | User story | Architect |
| `story_validation` | Story review results | Product Owner |
| `file_plan` | Implementation file plan | Architect |
| `test_plan` | Test strategy and scenarios | Test Engineer |

**Example:**
```json
{
  "handoff": {
    "artifacts": [
      {
        "type": "architecture",
        "epic_id": "SCOPE-42",
        "location": "Confluence epic architecture page"
      },
      {
        "type": "adr",
        "id": "ADR-1",
        "title": "Use OAuth2 for authentication",
        "location": "Confluence epic ADR page"
      }
    ]
  }
}
```

## Reading Previous Work

Access previous agent outputs to understand context and build on their work:

```
.scope/{epic-id}/agents_summaries.jsonl
```

**Usage pattern:**
1. Read file using Read tool
2. Parse JSONL to extract (one JSON object per line):
   - Previous deliverables (what was created)
   - Identified concerns (issues to address)
   - Phase progression (what work is complete)
   - Artifacts created (where to find outputs)

**Example structure:**
```jsonl
{"agent":"product-owner","session_id":"abc123...","task_id":"1","completed_at":"2026-01-27T10:30:00-05:00","status":"success","phase":"epic_validation","deliverables":{"epic_analysis":{"business_value":"...","completeness_score":"high"}},"handoff":{"summary":"Epic validated and ready for architecture","artifacts":[{"type":"epic_validation","epic_id":"SCOPE-42"}]},"error":null}
{"agent":"architect","session_id":"def456...","task_id":"2","completed_at":"2026-01-27T11:00:00-05:00","status":"success","phase":"initial_analysis","deliverables":{"components":["OAuthProvider","TokenManager"],"adrs":[{"id":"ADR-1","title":"Use Passport.js"}]},"handoff":{"summary":"Initial architecture complete","artifacts":[{"type":"architecture","epic_id":"SCOPE-42"}]},"error":null}
```

## Asking Questions (user_input)

When you need user clarification:

**Option 1: AskUserQuestion tool (preferred)**
- Provides structured question UI
- Supports multiple choice + custom input
- Better user experience

**Option 2: Return status: user_input**
```yaml
status: user_input
work_impact: none
deliverables: null
handoff:
  summary: "Need technical clarification"
  concerns:
    - area: architecture
      issue: "OAuth provider selection not specified"
      severity: high
questions:
  - "Which OAuth providers should be supported (Google, GitHub, Microsoft, all)?"
  - "Should tokens be stored in database or Redis?"
error: "Cannot design authentication architecture without provider and storage requirements. See questions above."
```

**Agent will be resumed** with user's answers in context. You may:
- Ask follow-up questions (return `user_input` again)
- Proceed with work (return `success`)

## Example - Architecture Complete

```json
{
  "agent": "architect",
  "session_id": "30c0069d-7cdb-4840-826d-2ab70bfc48e5",
  "task_id": "2",
  "completed_at": "2026-01-27T16:00:00-05:00",
  "status": "success",
  "work_impact": "major",
  "phase": "initial_analysis",
  "deliverables": {
    "components": [
      {
        "name": "OAuthProvider",
        "purpose": "Abstract OAuth2 provider interactions",
        "technology": "Node.js, Passport.js"
      },
      {
        "name": "TokenManager",
        "purpose": "JWT token generation and validation",
        "technology": "jsonwebtoken library"
      }
    ],
    "adrs": [
      {
        "id": "ADR-1",
        "title": "Use Passport.js for OAuth abstraction",
        "status": "Accepted",
        "decision": "Use Passport.js to abstract provider-specific OAuth flows"
      }
    ],
    "stories": [
      {
        "title": "Implement Google OAuth integration",
        "epic_id": "SCOPE-42",
        "description": "As a user, I want to sign in with Google...",
        "acceptance_criteria": ["..."]
      }
    ]
  },
  "handoff": {
    "summary": "Initial architecture complete with 5 stories created",
    "artifacts": [
      {
        "type": "architecture",
        "epic_id": "SCOPE-42",
        "location": "Confluence epic architecture page"
      },
      {
        "type": "adr",
        "id": "ADR-1",
        "title": "Use Passport.js for OAuth abstraction",
        "location": "Confluence epic ADR page"
      },
      {
        "type": "story",
        "id": "CODINT-43",
        "title": "Implement Google OAuth integration"
      }
    ],
    "concerns": [
      {
        "area": "security",
        "issue": "Token encryption at rest not addressed in initial design",
        "severity": "medium"
      },
      {
        "area": "epic_coverage",
        "issue": "MFA integration deferred to future epic",
        "severity": "low"
      }
    ]
  },
  "error": null
}
```

## Phase Field

The `phase` field is agent-specific and used for documentation/logging. It does NOT affect orchestrator routing.

**Define your own phase values in your agent file.** Examples:
- Product Owner: `epic_validation`, `story_review`
- Architect: `initial_analysis`, `refinement`, `file_plan`
- Test Engineer: `test_planning`, `test_review`
