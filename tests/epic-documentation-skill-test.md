# Epic Documentation Skill Test

## Purpose
Validate the epic-documentation skill by creating the full SCOPE product documentation structure in Confluence.

## Prerequisites
1. Atlassian MCP authenticated (run any MCP command, browser will open for OAuth)
2. Confluence space exists for SCOPE documentation

## Test Structure

Create this page hierarchy with proper tags:

```
SCOPE (tag: scope)
├── Product Documentation (tags: scope, product)
│   ├── Product Strategy (tags: scope, product, strategy)
│   ├── Product Definition (tags: scope, product, definition)
│   ├── Product Reference (tags: scope, product, ref)
│   └── Product Decisions (tags: scope, product, pdr)
│
├── Architecture Documentation (tags: scope, architecture)
│   ├── System Overview (tags: scope, architecture, system)
│   ├── Data Architecture (tags: scope, architecture, data)
│   ├── Constraints & Non-Goals (tags: scope, architecture, constraints)
│   ├── Interfaces (tags: scope, architecture, interface)
│   ├── Security (tags: scope, architecture, security)
│   ├── Cross-cutting Concerns (tags: scope, architecture, common)
│   ├── Operations (tags: scope, architecture, operations)
│   ├── Architecture Decisions (tags: scope, architecture, adr)
│   └── Technical Debt (tags: scope, architecture, tech-debt)
│
├── Epic Documentation (tags: scope, epic)
│   └── SCOPE-001 - Core Orchestration (tags: scope, epic, scope-001)
│       ├── SCOPE-STORY-001 - Plan Execution (tags: scope, epic, story, scope-001, scope-story-001)
│       ├── SCOPE-STORY-002 - Agent Spawning (tags: scope, epic, story, scope-001, scope-story-002)
│       ├── ADR: Agent Resume Pattern (tags: scope, epic, epic-adr, scope-001)
│       └── Epic Summary (tags: scope, epic, epic-summary, scope-001)
│
└── Releases Documentation (tags: scope, release)
    └── scope-release-0.1.0 - MVP (tags: scope, release, scope-release-0.1.0)
```

## Test Execution

### Step 1: Authenticate
Run any Atlassian MCP command to trigger OAuth:
```
mcp__atlassian__atlassianUserInfo()
```
Browser will open for login.

### Step 2: Get/Create Space
```
mcp__atlassian__getConfluenceSpaces(cloudId: "{cloudId}", keys: ["SCOPE"])
```
If space doesn't exist, create it manually or use API.

### Step 3: Create Root Page
```python
# SCOPE root page
mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  title: "SCOPE",
  body: """
# SCOPE - Simple Claude Orchestrator & Persistence Engine

This is the documentation root for the SCOPE project.

## Quick Links
- [Product Documentation](#product-documentation)
- [Architecture Documentation](#architecture-documentation)
- [Epic Documentation](#epic-documentation)
- [Releases](#releases-documentation)
"""
)
# Add label: scope
```

### Step 4: Create Product Documentation Branch

```python
# Product Documentation parent
product_page = mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{scope_root_id}",
  title: "Product Documentation",
  body: """
# Product Documentation

Documentation for SCOPE product strategy, definition, and reference materials.
"""
)
# Labels: scope, product

# Product Strategy
mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{product_page_id}",
  title: "Product Strategy",
  body: """
# Product Strategy

## Vision Statement
SCOPE separates planning (domain expertise) from execution (mechanics), enabling flexibility while keeping the orchestrator simple.

### Purpose
Enable Claude Code to execute multi-step agentic workflows with persistence and user oversight.

### North Star
Any Claude Code user can orchestrate complex multi-agent workflows without writing custom code.

### In Scope
- Epic refinement orchestration
- Agent spawning and resumption
- Plan execution with hooks
- User approval workflows

### Out of Scope
- Code execution/deployment (separate agents handle this)
- Direct Jira/Confluence operations (skills abstract these)

## Markets
- Target: Development teams using Claude Code
- Persona: Technical leads managing epics

## Customer Problems
- Complex epics require multiple expert perspectives
- Manual coordination between agents is error-prone
- No persistence across Claude Code sessions
"""
)
# Labels: scope, product, strategy

# Product Definition
mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{product_page_id}",
  title: "Product Definition",
  body: """
# Product Definition

## Use Cases

### UC-001: Epic Refinement
**Goal**: Transform an epic from "Ready for Refinement" to "Implementation Ready"

**Flow**:
1. User runs `/workplan EPIC-001`
2. Planner analyzes epic, creates execution plan
3. Orchestrator executes steps (spawn/resume agents)
4. User approves major work via hooks
5. Epic marked ready for implementation

### UC-002: Agent Interview
**Goal**: Gather missing requirements from user

**Flow**:
1. Agent identifies incomplete epic
2. Agent prints questions, returns `status: user_input`
3. User provides answers
4. Agent resumes with user's input

## Capability Map

| Capability | Value Proposition | Status |
|------------|------------------|--------|
| Plan Execution | Automated step-by-step agent orchestration | Core |
| Agent Persistence | Resume agents with full context | Core |
| User Approval Hooks | Human-in-the-loop for major decisions | Core |
| Dynamic Planning | Planners create custom plans per epic | Core |
| Skill Abstraction | Swap Jira/Confluence without agent changes | Core |
"""
)
# Labels: scope, product, definition

# Product Reference
mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{product_page_id}",
  title: "Product Reference",
  body: """
# Product Reference

## Modules Overview

| Module | Purpose |
|--------|---------|
| Orchestrator | Execute plans, manage agent lifecycle |
| Planners | Generate execution plans for epics |
| Skills | Abstract external system operations |
| Agents | Domain experts (product-owner, architect, etc.) |

## Glossary

| Term | Definition |
|------|------------|
| Epic | Large body of work tracked in Jira |
| Plan | YAML file defining execution steps |
| Agent | Specialized Claude subagent with domain expertise |
| Skill | Reusable instruction set for common operations |
| Hook | Execution pause point for user interaction |
| AgentResult | Structured YAML response from agents |
| work_impact | Agent self-assessment: none, minor, major |
"""
)
# Labels: scope, product, ref

# Product Decisions
mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{product_page_id}",
  title: "Product Decisions",
  body: """
# Product Decisions Record (PDR)

Summary of product decisions. Detailed rationale lives in epic PDRs.

| ID | Decision | Epic | Date |
|----|----------|------|------|
| PDR-001 | Use YAML for plan format | SCOPE-001 | 2025-12 |
| PDR-002 | Agents return structured AgentResult | SCOPE-001 | 2025-12 |
| PDR-003 | Status: user_input for agent interviews | SCOPE-001 | 2025-12 |
"""
)
# Labels: scope, product, pdr
```

### Step 5: Create Architecture Documentation Branch

```python
# Architecture Documentation parent
arch_page = mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{scope_root_id}",
  title: "Architecture Documentation",
  body: "# Architecture Documentation\n\nTechnical architecture for SCOPE."
)
# Labels: scope, architecture

# System Overview
mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{arch_page_id}",
  title: "System Overview",
  body: """
# System Overview

## L1: Context Diagram

```
┌─────────────────┐     ┌─────────────────┐
│   Claude Code   │────▶│      SCOPE      │
│     (User)      │◀────│  Orchestrator   │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  Jira    │ │Confluence│ │  Agents  │
              │  (MCP)   │ │  (MCP)   │ │ (Claude) │
              └──────────┘ └──────────┘ └──────────┘
```

## L2: Container Diagram

```
SCOPE/
├── Orchestrator Agent     # Executes plans
├── Planners/              # Generate plans
│   ├── backend-planner
│   └── tdd-planner
├── Skills/                # Abstract operations
│   ├── epic-tracking
│   └── epic-documentation
└── Execution Agents/      # Domain experts
    ├── product-owner
    ├── software-architect
    └── test-engineer
```
"""
)
# Labels: scope, architecture, system

# Create remaining architecture pages (abbreviated for length)
# - Data Architecture (tags: scope, architecture, data)
# - Constraints & Non-Goals (tags: scope, architecture, constraints)
# - Interfaces (tags: scope, architecture, interface)
# - Security (tags: scope, architecture, security)
# - Cross-cutting Concerns (tags: scope, architecture, common)
# - Operations (tags: scope, architecture, operations)
# - Architecture Decisions (tags: scope, architecture, adr)
# - Technical Debt (tags: scope, architecture, tech-debt)
```

### Step 6: Create Epic Documentation Branch

```python
# Epic Documentation parent
epic_parent = mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{scope_root_id}",
  title: "Epic Documentation",
  body: "# Epic Documentation\n\nDocumentation for SCOPE epics."
)
# Labels: scope, epic

# Sample Epic
epic_page = mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{epic_parent_id}",
  title: "SCOPE-001 - Core Orchestration",
  body: """
# SCOPE-001 - Core Orchestration

## Epic Overview

Implement the core SCOPE orchestration engine including plan execution,
agent spawning/resumption, and hook handling.

## Stories

| ID | Title | Status |
|----|-------|--------|
| SCOPE-STORY-001 | Plan Execution | In Progress |
| SCOPE-STORY-002 | Agent Spawning | Not Started |

## Acceptance Criteria
- Orchestrator can execute YAML plans
- Agents can be spawned and resumed
- User approval hooks pause execution
- Agent results are persisted to summaries file
"""
)
# Labels: scope, epic, scope-001

# Story page
mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{epic_page_id}",
  title: "SCOPE-STORY-001 - Plan Execution",
  body: """
# SCOPE-STORY-001 - Plan Execution

## Requirements

As an orchestrator, I want to execute plans step-by-step so that
agents complete their work in the correct order.

### Acceptance Criteria
- Parse YAML plan from .scope/{epic-id}/refine-plan.yaml
- Execute steps in order based on on_success transitions
- Handle agent steps (spawn/resume) and hook steps (approval/gate)
- Persist current_step to current_state.yaml

## Design

### Execution Loop
1. Read current_state.yaml
2. Find current step in plan
3. Execute step (agent or hook)
4. Update current_step based on result
5. Repeat until plan completed or escalated

### Agent Step Handling
- First call to agent: spawn new
- Subsequent calls: resume with agent_id
- Parse AgentResult from agent output
- Append to agents_summaries file

## Test Scenarios

### Happy Path
Given a 3-step plan with 2 agents and 1 approval hook
When orchestrator executes
Then steps complete in order with user approval at hook

### Agent Failure
Given agent returns status: failure
When orchestrator processes result
Then execution follows on_failure transition

### User Input
Given agent returns status: user_input
When orchestrator receives result
Then execution pauses for user response
And resumes agent with user's answer
"""
)
# Labels: scope, epic, story, scope-001, scope-story-001

# Epic ADR
mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{epic_page_id}",
  title: "ADR: Agent Resume Pattern",
  body: """
# ADR: Agent Resume Pattern

## Context
Subagents in Claude Code run to completion and cannot pause mid-execution.
When an agent needs user input, we need a way to collect it and continue.

## Decision
Agents return `status: user_input` to signal they need input.
Orchestrator collects user response and resumes agent with answer as prompt.

## Consequences
- Agents can conduct multi-turn interviews
- No special hook type needed for user input
- AgentResult schema extended with third status value
- Orchestrator must track agent_id for resume

## Status
Accepted - 2025-12-19
"""
)
# Labels: scope, epic, epic-adr, scope-001
```

### Step 7: Create Releases Documentation Branch

```python
# Releases parent
release_parent = mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{scope_root_id}",
  title: "Releases Documentation",
  body: "# Releases Documentation\n\nFactual release records. Not a roadmap."
)
# Labels: scope, release

# Sample Release
mcp__atlassian__createConfluencePage(
  cloudId: "{cloudId}",
  spaceId: "{spaceId}",
  parentId: "{release_parent_id}",
  title: "scope-release-0.1.0 - MVP",
  body: """
# scope-release-0.1.0 - MVP

## Release Records

**Version**: 0.1.0
**Date**: TBD
**Status**: In Development

### Included Epics
| Epic | Title | Status |
|------|-------|--------|
| SCOPE-001 | Core Orchestration | In Progress |

## Release Notes

### Features
- Plan execution engine
- Agent spawn/resume
- User approval hooks
- Skill abstraction layer

### Known Limitations
- Single epic at a time
- No parallel agent execution

## Post-mortem

*To be completed after release*
"""
)
# Labels: scope, release, scope-release-0.1.0
```

## Validation Queries

After creating the structure, validate with these CQL queries:

```python
# All SCOPE docs
mcp__atlassian__searchConfluenceUsingCql(cql: 'label = "scope"')
# Expected: All pages created above

# Product documentation only
mcp__atlassian__searchConfluenceUsingCql(cql: 'label = "scope" AND label = "product"')
# Expected: Product Strategy, Definition, Reference, Decisions

# All stories in SCOPE-001
mcp__atlassian__searchConfluenceUsingCql(cql: 'label = "story" AND label = "scope-001"')
# Expected: SCOPE-STORY-001

# All ADRs (epic level)
mcp__atlassian__searchConfluenceUsingCql(cql: 'label = "epic-adr" AND label = "scope"')
# Expected: ADR: Agent Resume Pattern

# Architecture system overview
mcp__atlassian__searchConfluenceUsingCql(cql: 'label = "architecture" AND label = "system" AND label = "scope"')
# Expected: System Overview page
```

## Success Criteria

1. ✅ All pages created with correct parent hierarchy
2. ✅ All pages have correct tags (location + type + identifier)
3. ✅ No orphan pages
4. ✅ No tiny pages (content consolidated into sections)
5. ✅ CQL queries return expected results
6. ✅ Tags are lowercase with hyphens
7. ✅ No status tags (Jira is source of truth)
