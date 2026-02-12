# Epic Documentation (File) - Test Prompts

Run each prompt independently to test the epic-documentation-file skill.

## Prerequisites

1. `.scope/config.yaml` configured for file-based documentation
2. Base path: `./docs` (or as configured)

---

## Product Documentation

### Test 1: Update product strategy
```
Using the epic-documentation-file skill, update docs/product/strategy/vision.md with:
# Vision
SCOPE enables agentic workflows with persistence.

# Markets
Development teams using Claude Code.

# Customer Problems
- Complex epics need multiple perspectives
- No persistence across sessions
```

### Test 2: Get product strategy
```
Using the epic-documentation-file skill, read docs/product/strategy/vision.md.
```

### Test 3: Update product definition
```
Using the epic-documentation-file skill, update docs/product/definition/use-cases.md with:
# Use Cases

## UC-001: Epic Refinement
Transform epic from "Ready" to "Implementation Ready"

# Capability Map
| Capability | Status |
|------------|--------|
| Plan Execution | Core |
| Agent Persistence | Core |
```

### Test 4: List product docs
```
Using the epic-documentation-file skill, list all product documentation files.
Use: find docs/product -name "*.md" -type f
```

---

## Architecture Documentation

### Test 5: Update system overview
```
Using the epic-documentation-file skill, update docs/architecture/system.md with:
# System Overview

## Context Diagram
User → SCOPE Orchestrator → Agents

## Container Diagram
- Orchestrator
- Planners
- Skills
- Agents
```

### Test 6: Get architecture page
```
Using the epic-documentation-file skill, read docs/architecture/system.md.
```

### Test 7: Update constraints
```
Using the epic-documentation-file skill, update docs/architecture/constraints.md with:
# Constraints & Non-Goals

## Constraints
- Must work with Claude Code CLI
- No external database required

## Non-Goals
- Real-time collaboration
- GUI interface
```

### Test 8: List architecture docs
```
Using the epic-documentation-file skill, list all architecture documentation files.
Use: ls docs/architecture/*.md
```

---

## Epic Documentation

### Test 9: Create first epic doc
```
Using the epic-documentation-file skill, create epic documentation for epic 0001:
- Title: "Test Epic Alpha"
- Content:
# Overview
First test epic for validating documentation.

# Acceptance Criteria
- Documentation creates correctly
- Folder structure correct
```

### Test 10: Create second epic doc
```
Using the epic-documentation-file skill, create epic documentation for epic 0002:
- Title: "Test Epic Beta"
- Content:
# Overview
Second test epic for validating documentation.

# Acceptance Criteria
- Story docs nest correctly
- ADRs link properly
```

---

## get_epic_doc

### Test 11: Get epic doc
```
Using the epic-documentation-file skill, read the overview for epic 0001.
Use: cat docs/epics/epic-0001-*/overview.md
```

### Test 12: Find epic directory
```
Using the epic-documentation-file skill, find the directory for epic 0001.
Use: find docs/epics -maxdepth 1 -type d -name "epic-0001-*"
```

---

## create_story_doc

### Test 13: Create first story for Epic 1
```
Using the epic-documentation-file skill, create a story doc under epic 0001:
- Story ID: 0001
- Title: "Story Alpha-1"
- Content for requirements.md:
# Requirements
First story requirements.

# Acceptance Criteria
Given valid input, when processed, then output is correct.
```

### Test 14: Create second story for Epic 1
```
Using the epic-documentation-file skill, create a story doc under epic 0001:
- Story ID: 0002
- Title: "Story Alpha-2"
- Content for requirements.md:
# Requirements
Second story requirements.
```

### Test 15: Create first story for Epic 2
```
Using the epic-documentation-file skill, create a story doc under epic 0002:
- Story ID: 0003
- Title: "Story Beta-1"
- Content for requirements.md:
# Requirements
Beta epic first story.
```

### Test 16: Create second story for Epic 2
```
Using the epic-documentation-file skill, create a story doc under epic 0002:
- Story ID: 0004
- Title: "Story Beta-2"
- Content for requirements.md:
# Requirements
Beta epic second story.
```

---

## get_story_doc

### Test 17: Get story doc
```
Using the epic-documentation-file skill, read the requirements for story 0001.
Use: cat docs/epics/epic-0001-*/story-0001-*/requirements.md
```

### Test 18: List stories in epic
```
Using the epic-documentation-file skill, list all stories in epic 0001.
Use: ls -d docs/epics/epic-0001-*/story-*/
```

---

## update_story_section

### Test 19: Add design section
```
Using the epic-documentation-file skill, create/update the design section for story 0001:
docs/epics/epic-0001-*/story-0001-*/design.md

Content:
# Design

## Approach
Use standard MVC pattern.

## Components
- Controller
- Service
- Repository
```

### Test 20: Add tests section
```
Using the epic-documentation-file skill, create/update the tests section for story 0001:
docs/epics/epic-0001-*/story-0001-*/tests.md

Content:
# Test Scenarios

## Happy Path
Given valid input
When processed
Then output is correct

## Error Case
Given invalid input
When validated
Then error returned
```

---

## create_epic_adr

### Test 21: Create ADR for Epic 1
```
Using the epic-documentation-file skill, create an ADR for epic 0001:
- Title: "oauth-pattern"
- Content:
# ADR: Use OAuth2 Pattern

## Context
Need authentication mechanism.

## Decision
Use OAuth2 with JWT tokens.

## Consequences
- Industry standard
- Token management needed

## Status
Accepted - 2025-12-20
```

### Test 22: Create second ADR for Epic 1
```
Using the epic-documentation-file skill, create another ADR for epic 0001:
- Title: "token-storage"
- Content:
# ADR: Token Storage Strategy

## Context
Need secure token storage.

## Decision
Use httpOnly cookies.

## Consequences
- More secure
- CSRF protection needed
```

### Test 23: Create ADR for Epic 2
```
Using the epic-documentation-file skill, create an ADR for epic 0002:
- Title: "event-driven"
- Content:
# ADR: Event-Driven Architecture

## Context
Need async processing.

## Decision
Use event bus pattern.

## Consequences
- Loose coupling
- Eventual consistency
```

---

## get_epic_decisions

### Test 24: List ADRs for epic
```
Using the epic-documentation-file skill, list all ADRs for epic 0001.
Use: ls docs/epics/epic-0001-*/adr-*.md
```

---

## create_epic_pdr

### Test 25: Create PDR for Epic 1
```
Using the epic-documentation-file skill, create a PDR for epic 0001:
- Title: "scope-decision"
- Content:
# PDR: Scope Decision

## Context
Define what's in and out of scope.

## Decision
Focus on auth only, not authorization.

## Rationale
Keep MVP small.
```

---

## create_epic_review

### Test 26: Create security review
```
Using the epic-documentation-file skill, create a review for epic 0001:
- Type: security
- Content:
# Security Review

## Outcome
Passed with recommendations.

## Findings
- Input validation needed
- Rate limiting recommended

## Recommendations
1. Add input sanitization
2. Implement rate limits
```

### Test 27: Get review
```
Using the epic-documentation-file skill, read the security review for epic 0001.
Use: cat docs/epics/epic-0001-*/review-security.md
```

---

## Release Documentation

### Test 28: Create release doc
```
Using the epic-documentation-file skill, create release documentation:
- Version: 0.1.0
- Title: "mvp"
- Content for record.md:
# Release Record

Version: 0.1.0
Date: 2025-12-20
Status: Released

## Included Epics
- epic-0001: Test Epic Alpha
- epic-0002: Test Epic Beta
```

### Test 29: Add release notes
```
Using the epic-documentation-file skill, add release notes:
docs/releases/r0.1.0-mvp/notes.md

Content:
# Release Notes

## Features
- Epic tracking
- Story management
- ADR support

## Known Limitations
- Single user only
- No concurrent access
```

### Test 30: List releases
```
Using the epic-documentation-file skill, list all releases.
Use: ls -d docs/releases/r*/
```

---

## Query Operations

### Test 31: Find all epic docs
```
Using the epic-documentation-file skill, list all epic directories.
Use: ls docs/epics/
```

### Test 32: Find story by ID
```
Using the epic-documentation-file skill, find story 0003 across all epics.
Use: find docs/epics -path "*/story-0003-*" -type d
```

### Test 33: Find all ADRs across epics
```
Using the epic-documentation-file skill, find all ADR files.
Use: find docs/epics -name "adr-*.md" -type f
```

---

## Verify Structure

### Test 34: Show complete structure
```
Using the epic-documentation-file skill, show the complete documentation structure.
Use: find docs -type f -name "*.md" | sort
```

---

## Cleanup

### Test 35: Delete test data (optional)
```
Remove all test epic documentation:
rm -rf docs/epics/epic-0001-* docs/epics/epic-0002-*
rm -rf docs/releases/r0.1.0-*
```

---

## Expected Results Summary

| Test | Operation | Expected |
|------|-----------|----------|
| 1-4 | product docs | Files created in docs/product/ |
| 5-8 | arch docs | Files in docs/architecture/ |
| 9-10 | create_epic_doc | Folders: docs/epics/epic-000x-*/ |
| 11-12 | get_epic_doc | Returns overview.md content |
| 13-16 | create_story_doc | Folders: story-000x-*/ under epic |
| 17-18 | get_story_doc | Returns requirements.md |
| 19-20 | update_story_section | design.md, tests.md created |
| 21-23 | create_epic_adr | adr-001-*.md, adr-002-*.md |
| 24 | get_epic_decisions | Lists ADR files |
| 25 | create_epic_pdr | pdr-001-*.md created |
| 26-27 | create_epic_review | review-security.md created |
| 28-30 | release docs | docs/releases/r0.1.0-mvp/ |
| 31-33 | queries | Find commands work |
| 34 | structure | Complete tree shown |
