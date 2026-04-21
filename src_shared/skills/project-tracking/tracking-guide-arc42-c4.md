# Project Tracking Guide

**Purpose:** Ephemeral, tactical tracking. Backend-agnostic structure and agent responsibilities.

**Key principle:** Stories are self-contained (Developer doesn't fetch epic docs during implementation).

---

## Tracking Structure

### Epic

**Workflow:** To do → Refinement → Implementation Ready → In Progress → Done

**Fields:**
| Field | Type | Content |
|-------|------|---------|
| Description | Text | - Link to epic details (documentation)<br>- 400-word summary<br>- Tech stack<br>- Key metrics |
| Dependencies | List | Other epic IDs (e.g., [SCOPE-40, SCOPE-41]) |
| Fix Version | Standard | Target release (e.g., 2.5.0) |

**Agent responsibilities:**
| Agent | Read | Write |
|-------|------|-------|
| Product Owner | Status, summary | Create, update status |
| Architect | Status, dependencies | Collaborate on creation |
| Epic Housekeeping | Status, all stories | Set status to Done |

---

### Story

**Workflow:** To Do → In Progress → (Blocked) → Done

**Fields:**
| Field | Type | Content |
|-------|------|---------|
| Description | Text | - Story statement<br>- Tech stack<br>- Technical scope<br>- Acceptance criteria<br>- Technical notes<br>- Reference to Epic ADR (if relevant) |
| Epic Link | Standard | Parent epic ID |

**Agent responsibilities:**
| Agent | Read | Write |
|-------|------|-------|
| Architect | Context | Create stories |
| SDET | Detailed | Contribute acceptance criteria |
| Developer | Extensive (primary context) | (none - writes to `.scope/{story-id}/agent_summaries.jsonl`) |

---

## Critical Rules

### Self-Contained Stories
**Rule:** Story description must be complete. Developer should NOT need to fetch epic documentation during implementation.

**Include in description:**
- Story statement
- Tech stack (specific)
- Technical scope (files/components)
- Acceptance criteria (detailed, testable)
- Technical notes (implementation hints, edge cases)
- Reference to Epic ADR (link if relevant)

**Omit:**
- Story points (no value for agentic teams)
- Story type (no value for tactical units)
- Dependencies (epics complete in ≤1 hour)

---

### Developer Feedback
**Rule:** Developer does NOT write to tracking.

Developer writes to: `.scope/{story-id}/agent_summaries.jsonl`

Epic Housekeeping reads summaries and updates: **Epic status to Done** + creates **Epic Implementation Summary** in documentation.

---

## Agent Responsibilities Matrix

| Agent | Reads | Writes | Contributes To |
|-------|-------|--------|----------------|
| **Product Owner** | Epic (status, summary) | Epic (create, update status) | - |
| **Architect** | Epic (status, dependencies)<br>Story (context) | Story (create) | Epic (technical content) |
| **SDET** | Story (detailed) | - | Story (acceptance criteria) |
| **Developer** | Story (primary context) | `.scope/{story-id}/agent_summaries.jsonl`<br>(NOT tracking) | - |
| **Epic Housekeeping** | Epic (status)<br>Story (all statuses) | Epic (set Done)<br>Epic Implementation Summary (documentation) | - |
| **Release Planner** | Epic/Story (release scope, status) | Release Record (documentation) | - |
| **Release Documentation** | Epic/Story (release scope) | Release Notes (documentation) | - |

---

## Backend Integration

The `project-tracking` skill wrapper loads this guide and dispatches to configured backend.

**Backend responsibilities:**
- Storage/retrieval
- Workflow state transitions
- Search/filtering
- Access control
