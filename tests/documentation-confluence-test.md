# Epic Documentation (Confluence) - Test Prompts

Run each prompt independently to test the epic-documentation-confluence skill.

## Prerequisites

1. `.scope/config.yaml` configured for Confluence
2. Atlassian MCP authenticated
3. Confluence space exists with project key

---

## Product Documentation

### Test 1: Update product strategy
```
Using the epic-documentation-confluence skill, update the Product Strategy page with:
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
Using the epic-documentation-confluence skill, get the content of the Product Strategy page.
```

### Test 3: Update product definition
```
Using the epic-documentation-confluence skill, update the Product Definition page with:
# Use Cases
## UC-001: Epic Refinement
Transform epic from "Ready" to "Implementation Ready"

# Capability Map
| Capability | Status |
|------------|--------|
| Plan Execution | Core |
| Agent Persistence | Core |
```

---

## Architecture Documentation

### Test 4: Update system overview
```
Using the epic-documentation-confluence skill, update the System Overview architecture page with:
# Context Diagram
User → SCOPE Orchestrator → Agents

# Container Diagram
- Orchestrator
- Planners
- Skills
- Agents
```

### Test 5: Get architecture page
```
Using the epic-documentation-confluence skill, get the content of the System Overview page.
```

---

## Epic Documentation

### Test 6: Create first epic page
```
Using the epic-documentation-confluence skill, create an epic page for SCOPE-E0001:
- Title: "Test Epic Alpha"
- Content:
# Overview
First test epic for validating documentation.

# Acceptance Criteria
- Documentation creates correctly
- Labels applied properly
```

### Test 7: Create second epic page
```
Using the epic-documentation-confluence skill, create an epic page for SCOPE-E0002:
- Title: "Test Epic Beta"
- Content:
# Overview
Second test epic for validating documentation.

# Acceptance Criteria
- Story pages nest correctly
- ADRs link properly
```

---

## get_epic_page

### Test 8: Get epic page
```
Using the epic-documentation-confluence skill, get the epic page for SCOPE-E0001.
Show the page content and labels.
```

---

## create_story_doc

### Test 9: Create first story page for Epic 1
```
Using the epic-documentation-confluence skill, create a story page under SCOPE-E0001:
- Story ID: SCOPE-S0001
- Title: "Story Alpha-1"
- Content:
# Requirements
First story requirements.

# Design
Implementation approach.

# Test Scenarios
Given/When/Then criteria.
```

### Test 10: Create second story page for Epic 1
```
Using the epic-documentation-confluence skill, create a story page under SCOPE-E0001:
- Story ID: SCOPE-S0002
- Title: "Story Alpha-2"
- Content:
# Requirements
Second story requirements.

# Design
Alternative implementation.
```

### Test 11: Create first story page for Epic 2
```
Using the epic-documentation-confluence skill, create a story page under SCOPE-E0002:
- Story ID: SCOPE-S0003
- Title: "Story Beta-1"
- Content:
# Requirements
Beta epic first story.
```

### Test 12: Create second story page for Epic 2
```
Using the epic-documentation-confluence skill, create a story page under SCOPE-E0002:
- Story ID: SCOPE-S0004
- Title: "Story Beta-2"
- Content:
# Requirements
Beta epic second story.
```

---

## get_story_doc

### Test 13: Get story page
```
Using the epic-documentation-confluence skill, get the story page for SCOPE-S0001.
Show content and verify parent is SCOPE-E0001.
```

---

## create_epic_adr

### Test 14: Create ADR for Epic 1
```
Using the epic-documentation-confluence skill, create an ADR under SCOPE-E0001:
- Title: "Use OAuth2 Pattern"
- Content:
# Context
Need authentication mechanism.

# Decision
Use OAuth2 with JWT tokens.

# Consequences
- Industry standard
- Token management needed
```

### Test 15: Create ADR for Epic 2
```
Using the epic-documentation-confluence skill, create an ADR under SCOPE-E0002:
- Title: "Event-Driven Architecture"
- Content:
# Context
Need async processing.

# Decision
Use event bus pattern.

# Consequences
- Loose coupling
- Eventual consistency
```

---

## get_epic_decisions

### Test 16: Get all ADRs for epic
```
Using the epic-documentation-confluence skill, get all ADRs for SCOPE-E0001.
List titles and page IDs.
```

---

## create_epic_review

### Test 17: Create security review
```
Using the epic-documentation-confluence skill, create a review for SCOPE-E0001:
- Review Type: security
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

---

## Query Operations

### Test 18: Search by label
```
Using the epic-documentation-confluence skill, search for all pages with label "scope-e0001".
List page titles.
```

### Test 19: Get all epic documentation
```
Using the epic-documentation-confluence skill, get all documentation for SCOPE-E0001.
Categorize into: overview, stories, ADRs, reviews.
```

---

## Release Documentation

### Test 20: Create release page
```
Using the epic-documentation-confluence skill, create a release page:
- Version: r0.1.0
- Title: "MVP Release"
- Content:
# Release Records
Version: 0.1.0
Date: 2025-12-20

## Included Epics
- SCOPE-E0001: Test Epic Alpha
- SCOPE-E0002: Test Epic Beta

# Release Notes
Initial release with core functionality.
```

### Test 21: Get release page
```
Using the epic-documentation-confluence skill, get the release page for r0.1.0.
```

---

## Label Operations

### Test 22: Add labels to page
```
Using the epic-documentation-confluence skill, add labels to the SCOPE-E0001 epic page:
- test-label
- validation

Verify labels were added.
```

### Test 23: Get page labels
```
Using the epic-documentation-confluence skill, get all labels on the SCOPE-E0001 epic page.
```

---

## Expected Results Summary

| Test | Operation | Expected |
|------|-----------|----------|
| 1-3 | update/get product doc | Page updated, content matches |
| 4-5 | update/get arch doc | Architecture page updated |
| 6-7 | create_epic_page | Pages created with labels [epic, scope-e0001] |
| 8 | get_epic_page | Returns page content |
| 9-12 | create_story_doc | Story pages nested under epic |
| 13 | get_story_doc | Story page with parent link |
| 14-15 | create_epic_adr | ADR pages with [epic, epic-adr, scope-e000x] labels |
| 16 | get_epic_decisions | Lists ADR pages |
| 17 | create_epic_review | Review page created |
| 18 | search by label | Returns tagged pages |
| 19 | get_all_epic_documentation | Categorized page list |
| 20-21 | release doc | Release page with [release, r0.1.0] labels |
| 22-23 | label operations | Labels added/retrieved |
