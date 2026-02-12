# SCOPE - Simple Claude Orchestrator & Persistence Engine

**Version:** 2.6
**Date:** January 2026
**Status:** Design

## Version History

- **2.6** (January 2026) - TDD implementation workflow refinement: removed pytest verification gate (4 steps per story instead of 5), developer autonomous test execution with 4-retry logic, explicit agent responsibility boundaries (SDET writes tests, developer implements and runs tests, architect documents during design), file plan intent documentation (600-1200 chars, 5-part template with positive delegation via "Related modules"), semantic search optimization for code-intent-rag MCP
- **2.5** (December 2025) - Wrapper skill pattern for backend abstraction, minimal agent prompts (epic_id + phase only), renamed epic-* skills to project-*, agents read config dynamically, static skill declaration in frontmatter, implementation phase architecture with dynamic skill loading, agent catalog filtering (agent-summary requirement), Atlassian MCP backend options (atlassian vs sooperset for better auth), renamed backend skill files (confluence-atlassian-mcp, jira-atlassian-mcp), token efficiency guidance for MCP tools, path expansion in wrapper skills (os.path.expanduser), proactive question-asking in product-owner and architect agents
- **2.4** (December 2025) - Removed test-engineer agent, formalized architect-led story breakdown with PO validation, test-as-soon-as-possible principle, progressive E2E evolution, agent-summary skill, context window optimization
- **2.3** - Added Atlassian Rovo Remote MCP integration
- **2.2** - Added skill abstraction layer
- **2.1** - Added orchestrator execution model
- **2.0** - Initial SCOPE architecture

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. File Structures](#2-file-structures)
  - [2.1 This Project (Pre-Install)](#21-this-project-pre-install)
  - [2.2 Post-Installation Structure](#22-post-installation-structure)
  - [2.3 Worktree Structure (Implementation/Deployment)](#23-worktree-structure-implementationdeployment)
- [3. Project Configuration](#3-project-configuration)
  - [3.1 Skill Selection](#31-skill-selection)
  - [3.2 Configuration Precedence](#32-configuration-precedence)
  - [3.3 Environment Variables](#33-environment-variables)
- [4. Installation](#4-installation)
  - [4.1 Quick Start](#41-quick-start)
  - [4.2 Prerequisites](#42-prerequisites)
  - [4.3 Install Script Options](#43-install-script-options)
  - [4.4 What Gets Installed](#44-what-gets-installed)
  - [4.5 Atlassian Rovo Remote MCP Configuration](#45-atlassian-rovo-remote-mcp-configuration)
  - [4.6 Sooperset vs Atlassian MCP](#46-sooperset-vs-atlassian-mcp)
- [5. Commands](#5-commands)
  - [5.1 Orchestrator Commands](#51-orchestrator-commands)
  - [5.2 Agent Communication](#52-agent-communication)
- [6. Core Concepts](#6-core-concepts)
  - [6.1 Architectural Decisions (v2.4-v2.6)](#61-architectural-decisions-v24-v26)
    - [6.1.1 Test-Engineer Agent Removal](#611-test-engineer-agent-removal)
    - [6.1.2 Test-as-Soon-as-Possible Principle](#612-test-as-soon-as-possible-principle)
    - [6.1.3 Cross-Epic Test Evolution](#613-cross-epic-test-evolution)
    - [6.1.4 Agent Summary Skill](#614-agent-summary-skill)
    - [6.1.5 Agent Execution Metadata](#615-agent-execution-metadata)
    - [6.1.6 Context Window Optimization](#616-context-window-optimization)
    - [6.1.7 Epic Refinement Workflow](#617-epic-refinement-workflow)
    - [6.1.8 Implementation Phase Architecture](#618-implementation-phase-architecture-v25)
    - [6.1.9 Implementation Phase Build Order](#619-implementation-phase-build-order)
    - [6.1.10 TDD Implementation Workflow](#6110-tdd-implementation-workflow)
  - [6.2 Epic Skills Abstraction](#62-epic-skills-abstraction)
  - [6.3 Dynamic Agent Discovery](#63-dynamic-agent-discovery)
  - [6.4 Specialized Planners](#64-specialized-planners)
- [7. Plan Schema](#7-plan-schema)
  - [7.1 Schema for Planners](#71-schema-for-planners)
  - [7.2 Schema for Orchestrator](#72-schema-for-orchestrator)
  - [7.3 Hook Types](#73-hook-types)
  - [7.4 Work Impact & Pre-Approval](#74-work-impact--pre-approval)
- [8. Agent Summaries](#8-agent-summaries)
  - [8.1 Summary Schema](#81-summary-schema)
  - [8.2 Summary File Example](#82-summary-file-example)
- [9. State Management](#9-state-management)
  - [9.1 Current State File](#91-current-state-file)
  - [9.2 Plan Status](#92-plan-status)
- [10. Orchestrator Execution](#10-orchestrator-execution)
  - [10.1 Execution Loop](#101-execution-loop)
  - [10.2 Approval Logic](#102-approval-logic)
- [11. Subagent Execution Model](#11-subagent-execution-model)
  - [11.1 No Nested Spawning](#111-no-nested-spawning)
  - [11.2 Persistent Context Windows](#112-persistent-context-windows)
  - [11.3 Resume by Agent Name](#113-resume-by-agent-name)
  - [11.4 User Input Pattern](#114-user-input-pattern)
- [12. Skill Reference](#12-skill-reference)
  - [12.1 Epic Skills](#121-epic-skills)
  - [12.2 Git Workflow Skill](#122-git-workflow-skill)
  - [12.3 Agent Catalog Skill](#123-agent-catalog-skill)
- [13. User Workflow](#13-user-workflow)
- [14. Build Order](#14-build-order)
- [15. Summary](#15-summary)

---

## 1. Overview

SCOPE separates planning (domain expertise) from execution (mechanics), enabling flexibility while keeping the orchestrator simple.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Commands                                  │
│                                                                             │
│   /workplan EPIC-001         Start epic refinement (auto-routes domain)     │
│   /workplan tdd STORY-42     Start TDD implementation                       │
│   /workflow.                 Continue after escalation                      │
│   /tell product-owner        Talk to a specific agent                       │
└──────────────────────────────────────────┬──────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Generic Orchestrator                                 │
│                                                                              │
│   Responsibilities:                                                          │
│   - Invoke appropriate planner for phase                                    │
│   - Execute plan step by step (spawn/resume agents based on context usage)  │
│   - Handle hooks (approval, input, gate)                                    │
│   - Track token usage and costs per step                                    │
│   - Append agent summaries to JSONL file                                    │
│                                                                              │
│   Does NOT:                                                                  │
│   - Make decisions about architecture, code, or business logic              │
│   - Require Jira/Confluence MCP (agents use those, not orchestrator)        │
└──────────────────────────────────────────┬──────────────────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────────┐
              │                            │                                │
              ▼                            ▼                                ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│   Epic Planner Router   │  │  Implementation         │  │  Deployment             │
│   (epic-planner)        │  │  Planners               │  │  Planners               │
│                         │  │                         │  │                         │
│   Routes to domain:     │  │  - tdd-implementation   │  │  - kubernetes-deployer  │
│   ↓                     │  │    -planner             │  │  - monolith-deployer    │
│   • Backend             │  │                         │  │  - local-deployer       │
│   • Frontend            │  └─────────────────────────┘  └─────────────────────────┘
│   • Marketing           │
└──────────┬──────────────┘
           │
           ├──→ epic-backend-planner   (APIs, services, databases)
           ├──→ epic-frontend-planner  (UI, components, dashboards)
           └──→ epic-marketing-planner (campaigns, content, messaging)
                          │
              ┌───────────┴───────────────────────────────────────────┐
              │                                                       │
              ▼                                                       ▼
┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐
│   Project Documentation Skill       │  │   Project Tracking Skill            │
│   (Wrapper - routes to backend)     │  │   (Wrapper - routes to backend)     │
│                                     │  │                                      │
│   Backends:                         │  │   Backends:                          │
│   - confluence-atlassian-mcp        │  │   - jira-atlassian-mcp               │
│   - confluence-sooperset-mcp        │  │   - jira-sooperset-mcp               │
│   - project-documentation-file      │  │   - project-tracking-file            │
│   - project-documentation-notion    │  │   - project-tracking-github          │
│                                     │  │                                      │
│   Stores: design docs, ADRs         │  │   Tracks: status, stories, progress  │
│   Token optimization: -ro variants  │  │                                      │
└─────────────────────────────────────┘  └─────────────────────────────────────┘
```

---

## 2. File Structures

This document references distinct file structures. Do not confuse them.

### 2.1 This Project (Pre-Install)

This project is git-managed and contains all source materials.

```
eng-crew/                                    # This repo (git-managed)
├── README.md
├── INSTALL.md
├── USAGE.md
│
├── src/                                     # Source materials for installation
│   ├── agents/                              # Agent definitions
│   │   ├── orchestrator.md
│   │   ├── planners/
│   │   │   ├── epic-planner.md              # Universal router
│   │   │   ├── epic-backend-planner.md      # Backend domain
│   │   │   ├── epic-frontend-planner.md     # Frontend domain
│   │   │   ├── epic-marketing-planner.md    # Marketing domain
│   │   │   ├── tdd-implementation-planner.md
│   │   │   ├── kubernetes-deployer.md
│   │   │   └── local-deployer.md
│   │   ├── architects/
│   │   ├── developers/
│   │   ├── reviewers/
│   │   └── scripts/                         # Agent-related scripts
│   │       ├── agents-tokens.sh             # Token usage analysis (Unix/Mac)
│   │       └── agents-tokens.ps1            # Token usage analysis (Windows)
│   │
│   ├── skills/                              # Skills (wrapper pattern)
│   │   ├── project-documentation/           # Documentation wrapper + implementations
│   │   │   ├── SKILL.md                     # Generic wrapper (dispatches to backend)
│   │   │   ├── confluence-atlassian-mcp.md  # Atlassian MCP (original)
│   │   │   ├── confluence-sooperset-mcp.md  # Sooperset MCP (better auth)
│   │   │   ├── project-documentation-file.md        # File-based implementation
│   │   │   └── project-documentation-notion.md      # Notion implementation (future)
│   │   ├── project-tracking/                # Tracking wrapper + implementations
│   │   │   ├── SKILL.md                     # Generic wrapper (dispatches to backend)
│   │   │   ├── jira-atlassian-mcp.md        # Atlassian MCP (original)
│   │   │   ├── jira-sooperset-mcp.md        # Sooperset MCP (better auth)
│   │   │   ├── project-tracking-file.md     # File-based implementation
│   │   │   ├── project-tracking-github.md   # GitHub implementation (future)
│   │   │   └── scripts/                     # Skill-specific scripts
│   │   │       └── jira-sooperset-mcp-http.sh  # HTTP wrapper for Jira MCP
│   │   ├── agent-summary/                   # Common agent output protocol
│   │   │   └── SKILL.md
│   │   ├── git-workflow/                    # Worktree management
│   │   │   └── SKILL.md
│   │   └── agent-catalog/                   # Agent discovery
│   │       └── SKILL.md
│   │
│   ├── commands/                            # Slash commands
│   │   ├── scope.md                         # /scope hub command
│   │   └── config_example.yaml              # Template for .scope/config.yaml
│   │
│   └── templates/
│       └── artifact-structure.md            # Template for .scope/
│
├── scripts/
│   ├── install.sh                           # One-time installation
│   ├── scope-init.sh                        # Per-project initialization
│   └── uninstall.sh
│
├── docker/
│   └── docker-compose.memgraph.yaml
│
├── design/
│   ├── scope-architecture.md                # This document
│   └── skill-interface-contract.md
│
└── tests/
```

### 2.2 Post-Installation Structure

After running `./install.sh` (default: project installation to `./.claude`):

```
user-project/
├── .claude/                              # Project-level: ./.claude (default install)
│   ├── agents/
│   │   ├── orchestrator.md
│   │   ├── planners/
│   │   │   ├── epic-planner.md           # Universal router
│   │   │   ├── epic-backend-planner.md   # Backend domain
│   │   │   ├── epic-frontend-planner.md  # Frontend domain
│   │   │   ├── epic-marketing-planner.md # Marketing domain
│   │   │   ├── tdd-implementation-planner.md
│   │   │   ├── kubernetes-deployer.md
│   │   │   └── local-deployer.md
│   │   ├── architects/
│   │   ├── developers/
│   │   ├── reviewers/
│   │   └── scripts/                      # Agent-related scripts
│   │       ├── agents-tokens.sh          # Token usage analysis (Unix/Mac)
│   │       └── agents-tokens.ps1         # Token usage analysis (Windows)
│   │
│   ├── skills/                           # Skills (wrapper pattern)
│   │   ├── project-documentation/        # Documentation wrapper + selected implementation
│   │   │   ├── SKILL.md                  # Generic wrapper (copied from src/)
│   │   │   └── {backend}.md              # confluence-atlassian-mcp, confluence-sooperset-mcp, or file
│   │   ├── project-tracking/             # Tracking wrapper + selected implementation
│   │   │   ├── SKILL.md                  # Generic wrapper (copied from src/)
│   │   │   ├── {backend}.md              # jira-atlassian-mcp, jira-sooperset-mcp, or file
│   │   │   └── scripts/                  # Skill-specific scripts
│   │   │       └── jira-sooperset-mcp-http.sh
│   │   ├── agent-summary/                # Always included
│   │   │   └── SKILL.md
│   │   ├── git-workflow/                 # Always included
│   │   │   └── SKILL.md
│   │   └── agent-catalog/                # Always included
│   │       └── SKILL.md
│   │
│   └── commands/
│       ├── scope.md                      # /scope hub command
│       └── config_example.yaml           # Template for .scope/config.yaml
│
├── .scope/                               # SCOPE runtime state
│   ├── config.yaml                       # Project config (YAML format)
│   ├── artifact-structure.md             # Where agents store artifacts
│   ├── agents_catalog.json               # Available agents (JSON format)
│   │
│   └── EPIC-001/                         # Per-epic directory (main = refinement only)
│       ├── refine-plan.json              # Epic refinement plan (JSON format)
│       ├── current_state.json            # Execution state (JSON format)
│       ├── refine-agents-summaries.jsonl # Agent summaries (JSONL format)
│       └── EPIC-001_token_costs.jsonl    # Token usage and costs per step
│
└── .env                                  # Environment variables
```

**Key points:**
- Main branch only has **refinement** artifacts
- Implementation and deployment happen in **worktrees**
- Wrapper skills with selected backend implementations installed
- Plan files are phase-specific: `refine-plan.json`, `impl-plan.json`, `deploy-plan.json`

### 2.3 Worktree Structure (Implementation/Deployment)

Implementation and deployment phases create worktrees:

```
user-project/
├── wip/                                  # Worktrees for implementation
│   └── epic-001-user-authentication/     # Worktree for EPIC-001
│       ├── .git                          # Worktree link
│       ├── .scope/EPIC-001/              # Epic state (copied from main)
│       │   ├── impl-plan.json            # Implementation plan
│       │   ├── current_state.json        # Current execution state
│       │   ├── refine-agents-summaries.jsonl  # Copied from main (reference)
│       │   └── impl-agents-summaries.jsonl    # Implementation summaries
│       └── src/                          # Code changes here
```

**Note:** Refinement plan stays in main branch. Only impl-plan.json and deploy-plan.json are created in worktrees.

---

## 3. Project Configuration

### 3.1 Project documentation and tracking selection

During `scope-init.sh`, you select TWO skills:

1. **Project Documentation** - Where design docs and ADRs are stored
2. **Project Tracking** - Where epic status and stories are tracked

```bash
# Interactive prompt during scope-init.sh
Select your project DOCUMENTATION backend:
1. Confluence (Atlassian)
2. Local files

Select your project TRACKING backend:
1. Jira (Atlassian)
2. Local files
```

**Available options:**

| Category | Option | Source File | Installed To | Dependencies |
|----------|--------|-------------|--------------|--------------|
| Project Documentation | Confluence (Atlassian) | `confluence-atlassian-mcp.md` | `.claude/skills/project-documentation/` | Atlassian MCP |
| Project Documentation | Confluence (Sooperset) | `confluence-sooperset-mcp.md` | `.claude/skills/project-documentation/` | Sooperset MCP - Better auth |
| Project Documentation | Local files | `project-documentation-file.md` | `.claude/skills/project-documentation/` | None |
| Project Tracking | Jira (Atlassian) | `jira-atlassian-mcp.md` | `.claude/skills/project-tracking/` | Atlassian MCP |
| Project Tracking | Jira (Sooperset) | `jira-sooperset-mcp.md` | `.claude/skills/project-tracking/` | Sooperset MCP - Better auth |
| Project Tracking | Local files | `project-tracking-file.md` | `.claude/skills/project-tracking/` | None |

**Installation:** Both wrapper (`SKILL.md`) and selected backend implementation are copied to the skill directory.

**Common combinations:**
- **Corporate**: Confluence + Jira (requires Atlassian Cloud account + Rovo MCP enabled)
- **Solo developer**: Local files + Local files (no external dependencies)

### 3.2 Configuration Precedence

SCOPE follows Claude Code conventions for configuration:

1. **Project config** (`.scope/config`) - Highest priority
2. **User config** (`~/.scope/config`) - Default fallback

```bash
# Check which config is active
cat .scope/config 2>/dev/null || cat ~/.scope/config
```

### 3.3 Environment Variables

```bash
# ~/.scope/config or .scope/config

# Atlassian Rovo Remote MCP uses OAuth 2.1 - no credentials needed here
# Authentication happens via browser on first connection

# For code-graph-rag (see https://github.com/vitali87/code-graph-rag)
OPENAI_API_KEY=your_openai_api_key      # If using OpenAI
GOOGLE_API_KEY=your_google_api_key      # If using Gemini
CYPHER_PROVIDER=openai                   # or "gemini"
CYPHER_MODEL=gpt-4o-mini                 # or "gemini-1.5-flash"
```

---

## 4. Installation

### 4.1 Quick Start

```bash
# Run the install script
# Default: Installs to ./.claude (project directory, no interaction)
./install.sh

# For user-level installation (available in all projects):
./install.sh --user

# For custom directory installation:
./install.sh /path/to/project

# Edit configuration
vim .scope/config.yaml

# Validate environment (for Atlassian integration)
/scope validate
```

### 4.2 Prerequisites

| Requirement | Purpose | Installation |
|-------------|---------|--------------|
| Node.js v18+ | Atlassian Rovo Remote MCP proxy | `brew install node` or [nodejs.org](https://nodejs.org) |
| Docker | Run Memgraph for code-graph-rag | [docker.com](https://docker.com) |
| Git | Version control | `brew install git` |
| uv | Install code-graph-rag | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| OpenAI or Google API Key | Code-graph LLM | [platform.openai.com](https://platform.openai.com) or [ai.google.dev](https://ai.google.dev) |
| Atlassian Cloud Account | Only if using Confluence/Jira | [atlassian.com](https://atlassian.com) |

### 4.3 Installation Modes

**Project Installation (default):**
```bash
./install.sh
# Installs to ./.claude
# Creates .scope/config.yaml
# No user interaction required
```

**User Installation:**
```bash
./install.sh --user
# Installs to ~/.claude
# Available in all projects
# Each project needs: /scope init
```

**Custom Directory:**
```bash
./install.sh /path/to/project
# Installs to /path/to/project/.claude
# Creates /path/to/project/.scope/config.yaml
```

**All Commands Installed:**
- All shortcut commands are installed by default
- No interactive prompts during installation
- Clean, fast, predictable installation experience

### 4.4 What Gets Installed

1. **Agents** → `~/.claude/agents/`
   - Orchestrator, planners, architects, developers, reviewers

2. **Skills** → `.claude/skills/` (selected per-project during scope-init)
   - `project-documentation/` - Wrapper + backend implementation (e.g., confluence, file, notion)
   - `project-tracking/` - Wrapper + backend implementation (e.g., jira, file, github)
   - `git-workflow.md` - Worktree management (always included)
   - `agent-catalog.md` - Agent discovery (always included)

3. **Commands** → `~/.claude/commands/`
   - `/tell` - Talk to a specific agent

4. **Code Graph RAG** → uv tool + Memgraph containers
   - See [code-graph-rag](https://github.com/vitali87/code-graph-rag) for full setup

### 4.5 Atlassian Rovo Remote MCP Configuration

SCOPE uses the [Atlassian Rovo Remote MCP Server](https://github.com/atlassian/atlassian-mcp-server) for Jira and Confluence integration. This is Atlassian's official cloud-hosted MCP server with OAuth 2.1 authentication.

**Configuration (`.mcp.json` in project root):**

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"]
    }
  }
}
```

**First-time setup:**
1. Ensure Node.js v18+ is installed
2. Enable Rovo MCP in Atlassian Admin: `Admin → Apps → AI settings → Rovo MCP server`
3. Restart Claude Code after creating `.mcp.json`
4. On first MCP call within a Claude session, a browser opens for OAuth authentication
5. Log in with your Atlassian account to grant access

**Benefits:**
- No API tokens to manage (OAuth 2.1)
- Respects existing Atlassian permissions
- Official Atlassian support
- Cloud-hosted (no Docker containers needed for MCP)

**Rate limits:** 1000 requests/hour (beta)

### 4.6 Sooperset vs Atlassian MCP

**Sooperset MCP** (`@sooperset/mcp-atlassian`) provides better authentication handling compared to the official Atlassian MCP:

**Key advantages:**
- Longer-lived OAuth sessions
- Automatic token refresh
- Fewer re-authentication failures
- More reliable for long-running agent operations

**When to use Sooperset:**
- Agents frequently fail with authentication errors
- Long-running operations (epic refinement, multiple agent steps)
- Multiple agents accessing Confluence/Jira sequentially

**Token efficiency considerations:**
- Sooperset MCP loads all tools: ~37k tokens (27k Jira + 10k Confluence)
- SCOPE requires only 15 of ~50 available tools
- Recommended: Configure selective tool exposure if supported

**Required tools for SCOPE:**
```
mcp__atlassian__search, mcp__atlassian__getConfluencePage, mcp__atlassian__updateConfluencePage, mcp__atlassian__createConfluencePage, mcp__atlassian__searchConfluenceUsingCql, mcp__atlassian__getJiraIssue, mcp__atlassian__createJiraIssue, mcp__atlassian__editJiraIssue, mcp__atlassian__searchJiraIssuesUsingJql, mcp__atlassian__transitionJiraIssue, mcp__atlassian__getTransitionsForJiraIssue, mcp__atlassian__getConfluencePageDescendants, mcp__atlassian__getPagesInConfluenceSpace, mcp__atlassian__addCommentToJiraIssue, mcp__atlassian__addWorklogToJiraIssue
```

**Installation:**
```bash
npm install -g @sooperset/mcp-atlassian
```

**MCP Configuration** (add to Claude Desktop config):
```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@sooperset/mcp-atlassian"]
    }
  }
}
```

**Project Configuration** (`.scope/config.yaml`):
```yaml
documentation:
  skill: confluence-sooperset-mcp     # or confluence-atlassian-mcp
  space_key: YOUR_SPACE_KEY
  atlassian_url: https://yoursite.atlassian.net

tracking:
  skill: jira-sooperset-mcp           # or jira-atlassian-mcp
  project_key: YOUR_PROJECT_KEY
  atlassian_url: https://yoursite.atlassian.net
```

**Backend comparison:**

| Feature | Atlassian MCP | Sooperset MCP |
|---------|---------------|---------------|
| OAuth support | ✅ Yes | ✅ Yes |
| Token refresh | Manual | Automatic |
| Auth failures | Frequent | Rare |
| Token cost | ~37k tokens | ~37k tokens |
| Selective tools | Unknown | Unknown |
| Maintenance | Official | Community |

**Migration:** Zero code changes needed. Simply update `skill:` value in `.scope/config.yaml`. All function signatures are identical.

---

## 5. Commands

### 5.1 Command Hub Architecture

SCOPE uses `/scope` as the main command hub. All functionality is accessible via `/scope {subcommand}`, with optional shortcuts for frequently used commands.

**Core Commands:**
- **Epic Planning:** `/workplan {epic-id}` - Universal router that auto-detects domain (backend/frontend/marketing)
- **Implementation:** `/workplan {issue-id}` - Explicit planner selection (e.g., `tdd`, `kubernetes-deployer`)
- **Execution:** `/scope continue`, `/scope approve` - Control plan execution
- **Creation:** `/scope create {type}`, `/scope prd develop` - Create work items and PRDs
- **Status:** `/scope status`, `/scope listplan` - View epic status and plans

```
/scope {subcommand} [args]
   │
   ├── Planning:
   │   ├── plan {epic-id}           → Auto-route to domain planner
   │   ├── plan {planner} {id}      → Explicit planner selection
   │   └── prd {develop|breakdown}  → PRD development and breakdown
   │
   ├── Creation:
   │   ├── create {epic|story|task|bug}  → Create work items
   │   └── init                          → Initialize project config
   │
   ├── Execution:
   │   ├── continue [{epic-id}] [{prompt}]  → Resume execution
   │   ├── approve                          → Approve current step
   │   ├── gobackto {step}                  → Resume from earlier step
   │   └── r                                → Resume agent (shorthand)
   │
   ├── Information:
   │   ├── listplan      → Show current plan
   │   ├── status        → Show all epics with status
   │   └── validate      → Validate environment
   │
   └── Configuration:
       ├── preapprove {level}   → Set pre-approval level
       └── tell {agent} {msg}   → Message specific agent
```

### 5.2 Command Installation

All shortcut commands are installed automatically during `./install.sh` with no user interaction required.

**Installed Commands:**
- `/scope` - Hub command (always available)
- `/approve` - Approve current plan step
- `/continue` (alias `/c`) - Resume agent with context
- `/create` - Create epic/story/task/bug
- `/gobackto` - Resume from earlier step
- `/listplan` - Show current plan
- `/preapprove` - Set auto-approval level
- `/r` - Resume agent (shorthand)
- `/tell` - Message specific agent
- `/validate` - Validate environment
- `/init` - Initialize project configuration
- `/pl` - Plan shortcut

**Installation Behavior:**
- All shortcuts installed by default
- No interactive prompts
- Clean, predictable installation
- Hub `/scope {subcommand}` always available as fallback

### 5.3 Subcommand Reference

**For detailed command documentation, see `src/commands/scope.md`**

| Subcommand | Shortcut | Description | Example |
|------------|----------|-------------|---------|
| `plan {epic-id}` | `/pl` | Auto-route epic to domain planner | `/workplan SCOPE-1` |
| `plan {planner} {id}` | `/pl` | Launch specific planner | `/workplan STORY-42` |
| `create {type} {desc}` | `/create` | Create epic/story/task/bug | `/scope create bug embeddings fail` |
| `prd develop [name]` | - | Interactive PRD creation | `/scope prd develop MyProduct` |
| `prd breakdown` | - | Convert PRD to epics | `/prd_breakdown` |
| `approve` | `/approve` | Approve and proceed | `/scope approve` |
| `continue [{epic}] [{ctx}]` | `/continue` | Resume execution | `/scope continue fixed the test` |
| `gobackto {step} [{ctx}]` | `/gobackto` | Resume from earlier step | `/scope gobackto 3` |
| `listplan` | `/listplan` | Show current plan | `/scope listplan` |
| `status` | - | Show all epics with status | `/scope status` |
| `preapprove {level}` | `/preapprove` | Set pre-approval level | `/scope preapprove minor` |
| `tell {agent} {msg}` | `/tell` | Message specific agent | `/scope tell architect why JWT?` |
| `validate` | `/validate` | Validate environment | `/scope validate` |
| `init` | `/init` | Initialize project config | `/scope init` |
| `r` | `/r` | Resume agent | `/scope r` |

### 5.4 Create Command

Create issues interactively via the product-owner agent.

**Syntax:** `/scope create {type} {description}`

**Types:** `epic` | `story` | `task` | `bug`

**Workflow:**
1. Parse type and initial description
2. Load `.scope/config.yaml` for skill mappings
3. Spawn/resume product-owner with context
4. Product-owner asks clarifying questions (based on type)
5. Product-owner creates Jira issue
6. For epics/stories: also creates Confluence page with labels

**Question templates by type:**

| Type | Questions Asked |
|------|-----------------|
| Epic | Business value? Success metrics? Scope boundaries? Constraints? |
| Story | Parent epic (auto-detected)? Acceptance criteria? Dependencies? |
| Task | Parent story/epic (auto-detected)? Definition of done? |
| Bug | Affected component (auto-detected)? Steps to reproduce? Expected vs actual? Severity? |

**Auto-detection:** References like "story 14" or "SCOPE-14" in description are automatically parsed and linked without asking.

**Example:**
```
User: /scope create bug There is a bug in story 14. The embeddings
      are not always using the right sentence transformer.

Agent: Creating bug report...

       Detected: Parent = SCOPE-14 (story)

       Please provide:
       1. Steps to reproduce?
       2. Expected behavior?
       3. Severity? [critical/high/medium/low]

User: Steps: Generate embeddings for documents > 1000 tokens.
      Expected: Use all-MiniLM-L6-v2 as configured.
      Severity: high

Agent: Created SCOPE-15: "Embeddings using wrong sentence transformer"

       Parent: SCOPE-14
       Severity: High
       Jira: https://aquaforge-ai.atlassian.net/browse/SCOPE-15
```

**Documentation creation:**
- **Epic/Story:** Creates Confluence page with proper labels via direct API
- **Task/Bug:** Jira only (no Confluence page)

### 5.5 Plan Execution Commands

**Difference between `/approve` and `/continue`:**
- `/approve` - Move to next step without re-engaging the agent (output looks good)
- `/continue` - Resume the agent with new context (agent needs to do more work)

**Epic Planning:**
- `/workplan {epic-id}` - Epic-planner auto-detects domain (backend/frontend/marketing) and routes to appropriate domain planner
- Epic domain determined by semantic analysis of labels, title, and description
- No explicit domain selection needed for epic refinement

**Implementation Planning:**
- `/workplan {issue-id}` - Explicit planner selection for implementation/deployment
- Planner naming: If name doesn't end with `-planner`, it's appended
  - `tdd` → `tdd-implementation-planner`
  - `kubernetes` → `kubernetes-deployer-planner`

**Pre-approval settings:**
- `none` - Only auto-approve when work_impact is `none`
- `minor` - Auto-approve `none` and `minor`
- `all` - Auto-approve everything
- `all-until {step}` - Auto-approve until reaching step, then revert to `none`

### 5.6 Agent Communication

| Command | Description | Example |
|---------|-------------|---------|
| `/scope tell {agent} {message}` | Send a message to a specific agent | `/tell product-owner why OAuth?` |

**Examples:**
```bash
# Ask product-owner about a decision
/tell product-owner why did we choose OAuth over SAML?

# Ask architect to reconsider
/tell software-architect can we use an event-driven approach instead?

# Get clarification from test-engineer
/tell test-engineer what test data do we need for the login scenarios?
```

---

## 6. Core Concepts

### 6.1 Architectural Decisions (v2.4-v2.6)

This section documents key architectural decisions made during development.

#### 6.1.1 Test-Engineer Agent Removal

**Decision:** Removed test-engineer agent from epic refinement workflow.

**Rationale:**
- Test-engineer had significant overlap with architect-reviewer
- Only valuable for specialized testing (performance, security, chaos)
- Most test validation can be done by existing agents
- Simplifies workflow and reduces agent count

**Impact:**
- Test validation integrated into software-architect (identifies test boundaries, test data requirements)
- Test validation integrated into architect-reviewer (validates test coverage, testable acceptance criteria)
- Product-owner ensures acceptance criteria are testable
- Testing architecture tightly coupled with product architecture (same agent designs both)

#### 6.1.2 Test-as-Soon-as-Possible Principle

**Decision:** Write tests at the EARLIEST point where the test becomes possible.

**Rationale:**
- Fixing issues in closed stories is expensive in agentic teams (context lost after completion)
- Deferring all tests to epic end creates "big bang" integration risk
- Early testing catches issues while context is fresh

**Implementation by test type:**

**Unit Tests:** Always in each story
- Every story includes unit tests for code it implements
- Fast, isolated, no external dependencies

**Integration Tests:** When component integration exists
- Include in story if component integrates with external service or database
- Defer to later story if integration requires multiple stories

**E2E Tests:** When user flow completes
- Include in story if story delivers vertical slice or completes user-facing feature
- Defer to later story if user flow requires multiple stories

#### 6.1.3 Cross-Epic Test Evolution

**Decision:** Tests evolve progressively across epics rather than written all at once.

**Pattern:** Progressive E2E Evolution
```yaml
Epic 1: User Authentication
  E2E Tests:
    - user_lifecycle_journey.test.ts
      ✅ User logs in with Google OAuth
      ✅ User sees dashboard
      🔵 Future (Epic 2): User updates profile
      🔵 Future (Epic 3): User changes settings
      ✅ User logs out

Epic 2: User Profile Management
  E2E Tests (EXTENDS):
    - user_lifecycle_journey.test.ts
      ✅ User logs in
      ✅ User sees dashboard
      ✅ User updates profile (NEW - added in Epic 2)
      🔵 Future (Epic 3): User changes settings
      ✅ User logs out

Epic 3: User Settings
  E2E Tests (EXTENDS):
    - user_lifecycle_journey.test.ts
      ✅ User logs in
      ✅ User sees dashboard
      ✅ User updates profile
      ✅ User changes settings (NEW - added in Epic 3)
      ✅ User logs out
```

**Benefits:**
- Catch integration issues early (while context fresh)
- Each epic tests current system state
- No "big bang" integration at the end
- Tests grow with system naturally

**Organization:** Tests organized by user journey, not by epic (prevents duplication)

#### 6.1.4 Agent Summary Skill

**Decision:** Created `agent-summary` skill as common protocol for all agent outputs.

**Rationale:**
- All agents must return structured output following same schema
- Single source of truth for AgentResult schema, status codes, work impact levels
- Reduces duplication across agent definitions

**Location:** Split into three specialized skills:
- `src/skills/agent-summary-core/SKILL.md` - For execution agents (Developer, SDET, Code Reviewer)
- `src/skills/agent-summary-complex/SKILL.md` - For coordination agents (PO, Architect, Test Engineer)
- `src/skills/agent-summary-orchestrator/SKILL.md` - For orchestrator telemetry and routing

**Schema:**
```yaml
status: success | failure | user_input
work_impact: none | minor | major
timestamp: string                     # ISO-8601 UTC
phase: string                         # Agent-specific phase identifier
deliverables: object | null           # Agent-specific structure
handoff:
  summary: string
  artifacts?: [object]
  concerns?: [object]
error: string | null                  # Required if status == failure
```

#### 6.1.5 Agent Execution Metadata

**Decision:** Orchestrator does NOT capture agent execution metadata (tool_uses, tokens, duration).

**Rationale:**
- Task tool does not expose this data via API
- Console output parsing is fragile and error-prone
- JSONL log parsing is complex and high-effort
- Keeping orchestrator simple is higher priority

**Impact:** Metadata visible in console for user observation but not programmatically accessible to orchestrator.

#### 6.1.6 Context Window Optimization

**Key insight:** Models often perform optimally when context window is at 15-20% capacity. Attention fades as context window grows ("lost in the middle" problem).

**Guidelines:**
- Agent files loaded at session START are in high-attention area (not a problem)
- 856-line agent file is acceptable when loaded once at start
- Agent resume pattern means file loaded once, context continues across phases
- Real concern is total session context growth, not individual agent file size
- Monitor session context usage (aim to stay under 60-70% capacity)

#### 6.1.7 Epic Refinement Workflow

**Decision:** Architect-led story breakdown with product-owner validation.

**Workflow phases:**

**Phase 1: Product Discovery (Product-Owner)**
- PO validates epic business requirements before architecture work begins
- PO asks clarifying questions to ensure epic is business-complete
- PO documents value proposition, user impact, success metrics
- PO ensures acceptance criteria are testable
- **Gate:** Epic must be business-ready before architect begins

**Phase 2: Technical Discovery (Software-Architect)**
- Architect analyzes technical approach after PO validation
- Architect identifies technical unknowns, risks, decisions
- Architect asks clarifying questions as needed
- Architect may invoke specialist agents (data-architect, devops, security-reviewer)

**Phase 3: Definition (Sequential)**

*Step 1 - Product Owner:*
- **PO writes epic-level acceptance criteria**
  - Given/When/Then format focusing on business outcomes
  - Testable and measurable criteria
- **PO defines end-to-end test scenarios**
  - Main user flows
  - Error scenarios and edge cases
  - Test data requirements
- **PO documents scope boundaries**
  - What's IN scope for this epic
  - What's OUT of scope (deferred to future epics)

*Step 2 - Software Architect (runs after PO):*
- **Architect designs architecture**
  - High-level component design
  - System diagrams
- **Architect creates ADRs** for key technical decisions
- **Architect identifies test boundaries** (unit/integration/e2e)
- **Architect documents test data requirements** at technical level
- **Testing strategy formalized:** Test boundaries, test evolution, test architecture

**Phase 4: Review & Epic Approval**
- Architect-reviewer validates completeness (includes test coverage)
- User approves complete epic definition
- **Gate:** No story breakdown until epic definition approved

**Phase 5: Story Breakdown (Architect + PO)**
- **Architect breaks epic into user stories**
  - Story structure aligned with technical boundaries
  - Dependency order considered
  - Test requirements documented per story
  - **File plan with intent documentation** (see File Plan Structure below)
- **PO reviews story breakdown**
  - Validates stories serve business needs and user value
  - Checks epic coverage (no missing features/scenarios)
  - Verifies acceptance criteria are testable and business-focused
  - Raises concerns if stories don't align with product vision

**File Plan Structure:**

Architect creates file plan organized by story (pure YAML format for Confluence storage):

```yaml
epic_id: "CODINT-1"
epic_title: "Intent-Centric Code Integration"

stories:
  - story_id: "CODINT-6"
    story_title: "Intent Data Model"

    files_to_create:
      - path: "src/models/intent.ts"
        intent: |
          [600-1200 character intent description]

    files_to_modify:
      - path: "src/types/index.ts"
        intent: |
          [600-1200 character intent description]
```

**Intent Documentation Guidelines:**

Each intent must be **600-1200 characters** following this 5-part structure:

1. **WHAT** (~100 chars): Brief description of core functionality
2. **WHY** (~150-250 chars): Architectural purpose and design rationale
3. **RESPONSIBILITIES** (~150-250 chars): Key responsibilities (3-5 main functions)
4. **DEPENDENCIES** (~100-150 chars): Dependencies on other modules
5. **RELATED MODULES** (~100-150 chars): Positive delegation to related functionality

**Why "Related modules" instead of "Boundaries":**

Use positive delegation instead of negation to avoid confusing semantic search:
- ❌ BAD: "Boundaries: Does NOT handle session encryption"
- ✓ GOOD: "Related modules: session encryption via SessionStore"

When a user queries "session encryption", positive delegation routes correctly to SessionStore rather than matching the module that explicitly says it doesn't handle it.

**Intent serves two purposes:**
1. **Human understanding** - Complete picture of module purpose and responsibilities
2. **RAG semantic search** - Rich semantic content for code-intent-rag MCP to match queries to relevant modules

**What to exclude from file plan:**
- LOC estimates (inaccurate, no value for SDET)
- Epic descriptions (fetch from tracking system)
- Related epics (query tracking system)
- Markdown formatting (pure YAML only)

**Key principle:** Architect leads technical breakdown (stories, file plan, test strategy). PO validates business alignment at epic start and story end.

**Rationale:**
- Technical boundaries drive story breakdown (component alignment, dependencies)
- Architect has full context of architecture decisions needed for story sequencing
- PO ensures stories deliver coherent user value without dictating technical structure
- Testing architecture tightly coupled with product architecture (same agent designs both)
- Intent documentation optimized for both human understanding and semantic RAG search

#### 6.1.8 Implementation Phase Architecture (v2.5)

**Decision:** One story = one agent implementation, using dynamic skill loading for technology specialization.

**Key Constraint:** A single agent must implement the complete story. Splitting implementation across multiple agents creates context coordination complexity and breaks story cohesion.

**Problem:** Stories frequently span multiple technologies:
- **Example:** "Add real-time user presence indicator"
  - Frontend: React component with presence UI
  - Backend: WebSocket server for real-time updates
  - Cache: Redis for presence state
  - **Three different technology specializations in one story**

**Solution:** Domain-level agents with dynamic technology skill loading.

---

**Architecture: Two-Layer System**

**Agent Layer (Domain-level, 5-8 core agents):**

| Agent | Purpose | Loads Skills Dynamically |
|-------|---------|--------------------------|
| `developer` | Implements features | Language, framework, backend tech |
| `sdet` | Writes tests (unit/integration/e2e) | Language, testing frameworks |
| `code-reviewer` | Reviews code quality | Language, best practices |
| `security-reviewer` | Security-specific review | Security patterns, vulnerabilities |
| `devops-engineer` | Infrastructure/deployment | Cloud providers, IaC tools |
| `database-developer` | Complex data modeling | Database technologies |

**Skills Layer (Technology-specific, 20-30 skills):**

```
Frontend:
  - frontend-react, frontend-angular, frontend-vue
  - frontend-mobile-ios, frontend-mobile-android
  - frontend-electron

Backend:
  - backend-rest-api, backend-graphql, backend-websocket
  - backend-microservices, backend-grpc, backend-llm

Database:
  - database-postgresql, database-mongodb, database-redis
  - database-vector

DevOps:
  - devops-aws, devops-azure, devops-gcp
  - devops-terraform, devops-kubernetes

Testing:
  - testing-jest, testing-pytest, testing-playwright
  - testing-k6
```

---

**Skill Loading: Agent Self-Discovery (Approach B)**

**Workflow:**
```yaml
- step: 8
  agent: developer
  prompt: |
    story_id: "SCOPE-42"
    title: "Add real-time user presence indicator"
  on_success: 9
```

**Agent execution:**
1. **Analyze story** - Reads description, acceptance criteria, examines codebase
2. **Identify technologies** - "Needs React frontend, WebSocket backend, Redis caching"
3. **Load skills dynamically** - `Skill(skill: "skill-loader", args: "load frontend-react backend-websocket database-redis")`
4. **Receive combined expertise** - ~3k tokens of React + WebSocket + Redis patterns, best practices, anti-patterns
5. **Implement cohesively** - Single agent with all needed knowledge for complete story

---

**Skill Structure**

**Skills catalog** (`.scope/skills_catalog.json`):
```yaml
skills:
  - name: frontend-react
    domain: frontend
    description: React patterns, hooks, state management, performance optimization
    expertise:
      - Component composition and props patterns
      - Hooks: useState, useEffect, useCallback, useMemo rules
      - Context vs prop drilling decisions
      - Re-render optimization (memo, PureComponent)
      - Error boundaries and suspense
```

**Skill loader wrapper** (`src/skills/skill-loader/SKILL.md`):
- Loads multiple skills and returns combined expertise instructions
- Usage: `Skill(skill: "skill-loader", args: "load frontend-react backend-websocket")`
- Returns: Combined markdown with best practices, patterns, security, performance tips

---

**Token Overhead Analysis**

| Component | Tokens | Notes |
|-----------|--------|-------|
| Skills catalog | ~1k | List of available skills |
| Skill selection logic | ~1k | Agent analyzes story, determines needed skills |
| Loaded skills (3 skills) | ~3k | Combined expertise for selected technologies |
| **Total overhead** | **~5k** | **2.5% of 200k context budget** |

**Verdict:** Acceptable overhead for quality gain and flexibility.

---

**Alternative Approaches Rejected**

**Option A: Specialized agents per technology**
- Example: `frontend-react-developer`, `backend-websocket-developer`, `database-redis-developer`
- **Rejected:** Agent explosion (20-30+ agents), maintenance burden, violates "one agent per story" constraint

**Option B: Generic agent without specialization**
- Example: Single `developer` agent with no technology expertise
- **Rejected:** Poor quality (no React best practices, no WebSocket patterns, no Redis optimization)

**Option C: Planner pre-loads skills (static)**
- Example: Planner analyzes story, tells agent which skills to load
- **Rejected:** Less flexible (planner must guess), agent knows implementation needs better after reading code

---

**Why Dynamic Skills Matter**

**Without dynamic skills (specialized agents only):**
- Story: "Add real-time notifications" → Need 3 agents (frontend, backend, cache)
- **Problem:** Coordination overhead, context fragmentation, artificial story splitting

**With dynamic skills (domain agent + skills):**
- Story: "Add real-time notifications" → 1 developer loads 3 skills
- **Benefit:** Cohesive implementation, no coordination, natural story boundaries

**Industry context:**
- **SDET (Software Development Engineer in Test)** - Modern term for test-first engineering
- **Three Amigos (BDD/ATDD)** - Business/Dev/QA collaborate on acceptance tests
- Stories often cross technology boundaries in modern systems (microservices, full-stack features)

---

**Agent Catalog Filtering**

**Decision:** Agent catalog only includes agents with `agent-summary` skill.

**Rationale:**
- `agent-summary` provides standard output format required by orchestrator
- Filtering at catalog build time simplifies planner logic (no validation needed)
- Planners only see compatible agents

**Implementation:**
```bash
# src/skills/agent-catalog/SKILL.md
if [[ ! "$skills" =~ "agent-summary" ]]; then
  continue  # Skip agents without agent-summary skill
fi
```

**Agents excluded from catalog:**
- `orchestrator` (no agent-summary - not selectable)
- `epic-backend-planner` (no agent-summary - not selectable)
- `tdd-implementation-planner` (no agent-summary - not selectable)

**Agents included in catalog:**
- `developer` (has agent-summary ✓)
- `sdet` (has agent-summary ✓)
- `product-owner` (has agent-summary ✓)
- `software-architect` (has agent-summary ✓)
- `architect-reviewer` (has agent-summary ✓)

---

**Benefits Summary**

1. **One agent per story** - No coordination complexity ✓
2. **Multi-technology stories** - Agent has all needed expertise ✓
3. **Maintainable** - 6 agents + 25 skills vs 30+ specialized agents ✓
4. **Flexible** - Skills compose for any tech combination ✓
5. **Quality** - Specialized expertise for each technology ✓
6. **Reasonable overhead** - 2-5k tokens acceptable for quality ✓
7. **Agent autonomy** - Agent decides which skills to load based on actual needs ✓

#### 6.1.9 Implementation Phase Build Order

**Decision:** Phased approach to building implementation agents and technology skills, starting with MVP and expanding based on project needs.

---

**Phase 1: Core Implementation (MVP)**

**Goal:** Minimum viable implementation capability for full-stack stories.

**Agents (3):**

| Agent | Location | Phases | When to Use |
|-------|----------|--------|-------------|
| `developer` | `src/agents/implementation/developer.md` | implementation, debugging, refactoring | All feature and refactoring stories |
| `sdet` | `src/agents/implementation/sdet.md` | test_planning, test_implementation, test_debugging | All stories requiring test coverage |
| `code-reviewer` | `src/agents/reviewers/code-reviewer.md` | code_review, suggest_refactoring | All PRs, periodic codebase analysis |

**Technology Skills (12):**

| Skill | Location | Coverage |
|-------|----------|----------|
| `frontend-react` | `src/skills/technology/frontend-react.md` | React 18+, hooks, server components |
| `frontend-typescript` | `src/skills/technology/frontend-typescript.md` | TypeScript patterns, types, generics |
| `frontend-tailwind` | `src/skills/technology/frontend-tailwind.md` | Tailwind CSS, utility-first styling |
| `backend-rest-api` | `src/skills/technology/backend-rest-api.md` | REST design, OpenAPI, versioning |
| `backend-nodejs` | `src/skills/technology/backend-nodejs.md` | Node.js, Express/Fastify patterns |
| `backend-websocket` | `src/skills/technology/backend-websocket.md` | WebSocket, real-time patterns |
| `database-postgresql` | `src/skills/technology/database-postgresql.md` | PostgreSQL, JSONB, optimization |
| `database-redis` | `src/skills/technology/database-redis.md` | Redis caching, pub/sub patterns |
| `testing-jest` | `src/skills/technology/testing-jest.md` | Jest, mocking, coverage |
| `testing-playwright` | `src/skills/technology/testing-playwright.md` | Playwright e2e testing |
| `quality-design-patterns` | `src/skills/quality/quality-design-patterns.md` | GoF patterns, SOLID principles |
| `security-owasp` | `src/skills/quality/security-owasp.md` | OWASP Top 10, vulnerabilities |

**Infrastructure Skill (1):**

| Skill | Location | Purpose |
|-------|----------|---------|
| `skill-loader` | `src/skills/skill-loader/SKILL.md` | Load and combine multiple technology skills |

**Build order:**
1. Create `skill-loader` infrastructure
2. Create `developer` agent
3. Create 6 core technology skills (React, TypeScript, REST, Node.js, PostgreSQL, Redis)
4. Create `sdet` agent + testing skills (Jest, Playwright)
5. Create `code-reviewer` agent + quality skills (design patterns, OWASP)

**Timeline:** ~4 weeks for usable MVP system

**Coverage:** Handles modern full-stack applications with React frontend, Node.js backend, PostgreSQL/Redis data layer.

---

**Phase 2: Quality & Security**

**Goal:** Add specialized review capabilities for security-critical and performance-sensitive stories.

**Agents (2):**

| Agent | Location | Phases | When to Add |
|-------|----------|--------|-------------|
| `security-reviewer` | `src/agents/reviewers/security-reviewer.md` | threat_modeling, security_testing, compliance_review | Security-critical domain (auth, payments, PII) |
| `performance-reviewer` | `src/agents/reviewers/performance-reviewer.md` | performance_analysis, optimization, load_testing | Performance is explicit requirement or SLA-driven |

**Additional Technology Skills (6):**

| Skill | Location | When to Add |
|-------|----------|-------------|
| `backend-graphql` | `src/skills/technology/backend-graphql.md` | Using GraphQL APIs |
| `backend-python` | `src/skills/technology/backend-python.md` | Python backend services |
| `devops-docker` | `src/skills/technology/devops-docker.md` | Containerized deployments |
| `devops-ci-cd` | `src/skills/technology/devops-ci-cd.md` | Automated pipelines |
| `testing-k6` | `src/skills/technology/testing-k6.md` | Load/performance testing |
| `quality-clean-code` | `src/skills/quality/quality-clean-code.md` | Refactoring patterns |

**Cumulative:** 5 agents, 19 skills

**Timeline:** +2 weeks

**Trigger:** Add when:
- Handling sensitive data (security-reviewer)
- Performance SLAs exist (performance-reviewer)
- Using GraphQL or Python (respective skills)
- Need automated deployment (devops skills)

---

**Phase 3: Specialized Capabilities**

**Goal:** Support complex data modeling, infrastructure work, and advanced UI requirements.

**Agents (3):**

| Agent | Location | Phases | When to Add |
|-------|----------|--------|-------------|
| `database-developer` | `src/agents/implementation/database-developer.md` | schema_design, migration_implementation, query_optimization | Complex data modeling beyond CRUD |
| `devops-engineer` | `src/agents/implementation/devops-engineer.md` | infrastructure_design, deployment_automation, observability | Infrastructure stories in implementation phase |
| `ui-specialist` | `src/agents/implementation/ui-specialist.md` | ui_implementation, accessibility_review, animation_implementation | Complex UI (design systems, animations, a11y) |

**Additional Technology Skills (12):**

| Domain | Skills | When to Add |
|--------|--------|-------------|
| **Frontend** | `frontend-vue`, `frontend-angular`, `frontend-nextjs` | Alternative frameworks needed |
| **Backend** | `backend-microservices`, `backend-llm`, `backend-event-driven` | Advanced architecture patterns |
| **Database** | `database-mongodb`, `database-vector` | NoSQL or vector search |
| **DevOps** | `devops-aws`, `devops-terraform`, `devops-kubernetes` | Cloud infrastructure work |
| **Mobile** | `frontend-react-native` | Mobile application development |

**Cumulative:** 8 agents, 31 skills

**Timeline:** Add incrementally as needed

**Trigger:** Add when:
- Complex data models requiring specialized expertise
- Infrastructure/deployment stories in implementation phase
- Advanced UI requirements (accessibility, animations, design systems)
- Using specialized technologies (LLM, vector DB, microservices)

---

**Directory Structure**

```
src/
├── agents/
│   ├── implementation/
│   │   ├── developer.md              # Phase 1
│   │   ├── sdet.md                   # Phase 1
│   │   ├── database-developer.md     # Phase 3
│   │   ├── devops-engineer.md        # Phase 3
│   │   └── ui-specialist.md          # Phase 3
│   └── reviewers/
│       ├── code-reviewer.md          # Phase 1
│       ├── security-reviewer.md      # Phase 2
│       └── performance-reviewer.md   # Phase 2
│
└── skills/
    ├── skill-loader/
    │   └── SKILL.md                  # Phase 1 (infrastructure)
    ├── technology/
    │   ├── frontend-react.md         # Phase 1
    │   ├── frontend-typescript.md    # Phase 1
    │   ├── frontend-tailwind.md      # Phase 1
    │   ├── frontend-vue.md           # Phase 3
    │   ├── frontend-angular.md       # Phase 3
    │   ├── frontend-nextjs.md        # Phase 3
    │   ├── frontend-react-native.md  # Phase 3
    │   ├── backend-rest-api.md       # Phase 1
    │   ├── backend-nodejs.md         # Phase 1
    │   ├── backend-python.md         # Phase 2
    │   ├── backend-graphql.md        # Phase 2
    │   ├── backend-websocket.md      # Phase 1
    │   ├── backend-microservices.md  # Phase 3
    │   ├── backend-llm.md            # Phase 3
    │   ├── backend-event-driven.md   # Phase 3
    │   ├── database-postgresql.md    # Phase 1
    │   ├── database-redis.md         # Phase 1
    │   ├── database-mongodb.md       # Phase 3
    │   ├── database-vector.md        # Phase 3
    │   ├── testing-jest.md           # Phase 1
    │   ├── testing-playwright.md     # Phase 1
    │   ├── testing-k6.md             # Phase 2
    │   ├── devops-docker.md          # Phase 2
    │   ├── devops-ci-cd.md           # Phase 2
    │   ├── devops-aws.md             # Phase 3
    │   ├── devops-terraform.md       # Phase 3
    │   └── devops-kubernetes.md      # Phase 3
    └── quality/
        ├── quality-design-patterns.md  # Phase 1
        ├── quality-clean-code.md       # Phase 2
        └── security-owasp.md           # Phase 1
```

---

**Implementation Priority Matrix**

| Priority | Agents | Skills | Use Case |
|----------|--------|--------|----------|
| **Critical** (MVP) | developer, sdet, code-reviewer | React, TypeScript, REST, Node.js, PostgreSQL, Redis, Jest, Playwright, design-patterns, OWASP, skill-loader | Modern full-stack web applications |
| **High** (Quality) | security-reviewer, performance-reviewer | GraphQL, Python, Docker, CI/CD, k6, clean-code | Production-grade applications with security/performance requirements |
| **Medium** (Specialized) | database-developer, devops-engineer | MongoDB, AWS, Terraform, microservices, event-driven | Complex data or infrastructure needs |
| **Low** (Optional) | ui-specialist | Vue, Angular, Next.js, React Native, vector DB, LLM, K8s | Specific technology requirements |

---

**Token Overhead by Phase**

| Phase | Agents | Skills | Est. Overhead | % of 200k Budget |
|-------|--------|--------|---------------|------------------|
| Phase 1 | 3 | 13 | ~8k tokens | 4% |
| Phase 2 | +2 | +6 | +4k tokens | +2% |
| Phase 3 | +3 | +12 | +6k tokens | +3% |
| **Total** | **8** | **31** | **~18k tokens** | **9%** |

**Verdict:** Acceptable overhead for comprehensive technology coverage.

---

**Recommended Adoption Strategy**

1. **Start with Phase 1 MVP** (4 weeks)
   - Build and validate core workflow
   - Test with simple full-stack stories
   - Refine skill content based on experience

2. **Add Phase 2 selectively** (2 weeks)
   - Add security-reviewer if handling sensitive data
   - Add performance-reviewer if SLAs exist
   - Add technology skills as tech stack grows

3. **Add Phase 3 incrementally** (ongoing)
   - Add specialized agents when needed for specific stories
   - Add technology skills when adopting new technologies
   - Don't build speculatively - wait for actual need

**Success criteria for MVP:**
- Developer can implement full-stack story with React + Node.js + PostgreSQL
- SDET can write unit tests (Jest) and e2e tests (Playwright)
- Code-reviewer can review PR and identify quality issues
- All agents successfully load required skills dynamically

#### 6.1.10 TDD Implementation Workflow

**Decision:** Test-first implementation workflow with 4 steps per story. Developer owns test execution with 4-retry logic before escalation.

---

**Workflow Structure**

TDD planner (`tdd-implementation-planner`) generates 4 steps per story:

```yaml
# Per story workflow:

1. **Test implementation** - SDET writes executable tests from story AC
   - agent: sdet
   - prompt: "story_id: {story_key}\nphase: test_implementation"
   - agents_summaries: story-{story_number}-summaries.jsonl

2. **Approval hook (optional)** - User validates tests
   - hook_type: user_approval
   - message: "Review tests for {story_key}: {story_title}"
   - Can be pre-approved

3. **Code implementation** - Developer implements story
   - agent: developer (or frontend-developer, backend-developer)
   - prompt: "story_id: {story_key}\nphase: implementation"
   - agents_summaries: story-{story_number}-summaries.jsonl
   - **CRITICAL**: Implementation phase includes test execution (see below)

4. **Approval hook (optional)** - Confirm story complete
   - hook_type: user_approval
   - message: "Story {story_key} complete - tests passing"
   - Can be pre-approved
```

**Why 4 steps (not 5):**
- Removed pytest verification gate (step 4 in v2.4)
- Developer already runs tests and retries autonomously
- Pytest gate was redundant verification
- Reduced complexity while maintaining quality

---

**Developer Test Execution Responsibility**

When developer receives `phase: implementation`, the implementation phase **MUST include**:

1. **Read tests created by SDET** - Understand requirements from test specifications
2. **Implement production code** - Write code that makes tests pass
3. **Run all relevant tests** - Execute test suite after implementation
4. **Fix test failures autonomously** - Debug and retry up to 4 times
5. **Escalate if stuck** - Return `status: failure` after 4 failed attempts
6. **Update tracking to "Done"** - When all tests pass

**Test Execution Retry Logic:**

```
Attempt 1: Run tests
  → Failed? Analyze error, debug, fix code

Attempt 2: Run tests again
  → Failed? Analyze error, try different approach

Attempt 3: Run tests again
  → Failed? Check for missed requirements, fix code

Attempt 4: Run tests again (FINAL ATTEMPT)
  → Failed? ESCALATE TO USER (return status: failure)
  → Passed? Success! (update tracking to "Done")
```

**Technology-agnostic test commands:**

Developer references loaded technology skills for test execution:
- Python: `pytest tests/ -v -k "story_042"`
- Node.js: `npm test -- --testNamePattern="story_042"`
- Go: `go test ./... -run TestStory042`
- Rust: `cargo test story_042`

---

**Agent Prompt Format**

Prompts contain **only** `story_id` and `phase` (minimal, no custom instructions):

```yaml
prompt: |
  story_id: SCOPE-42
  phase: test_implementation
```

```yaml
prompt: |
  story_id: SCOPE-42
  phase: implementation
```

**Why minimal prompts:**
- Reduces token usage (2 lines vs 10+ lines per prompt)
- Eliminates redundant parameter passing
- Agents read `.scope/config.yaml` themselves (single source of truth)
- Config changes take effect immediately (no plan regeneration)
- Phase name maps to agent's internal workflow definition

---

**Agent Responsibilities Clarification**

| Agent | Phase | Responsibility |
|-------|-------|----------------|
| **SDET** | `test_implementation` | Write all tests (unit, integration, e2e) from acceptance criteria |
| **Developer** | `implementation` | Implement code to make SDET's tests pass, run tests, fix failures (4 retries), update tracking to "Done" |
| **Architect** | Epic refinement | Design architecture, create file plan with intent documentation, update API docs during design |

**What Developer does NOT do:**
- ❌ Write tests (SDET's job)
- ❌ Update API documentation (architect does this before implementation)
- ❌ Design architecture (architect does this during refinement)
- ❌ Define acceptance criteria (product owner does this during refinement)

**Critical Rule:** Developer escalates to user only after 4 failed test attempts, not before.

---

**File Plan Usage**

When implementing a story:

1. **Read file plan** (`.scope/{epic-id}/file_plan.json`) for architectural intent
2. **SDET has created test files** - Developer creates/modifies implementation files
3. **Follow intent principles** - Understand WHY design choices were made
4. **Example intent structure:**

```yaml
- path: src/auth/oauth_provider.ts
  intent: |
    [WHAT] Abstracts OAuth2 provider interactions (Google, GitHub, Microsoft).

    [WHY] Isolate provider-specific logic to enable adding providers without
    touching core authentication flow. Maintains separation of concerns.

    [RESPONSIBILITIES] Unified interface for token exchange, user profile
    retrieval, provider discovery, error normalization.

    [DEPENDENCIES] Uses AuthConfig for provider credentials, HttpClient
    for API requests, TokenStore for token persistence.

    [RELATED MODULES] Session management via SessionStore, user profiles
    via UserService.
```

Developer implements following the isolation principle (the "WHY"), not just the "WHAT".

---

**Benefits of TDD Workflow**

1. **Tests first** - Clear specification before implementation
2. **Autonomous retry** - Developer fixes failures without manual intervention
3. **Explicit escalation** - User notified only when truly stuck
4. **Technology-agnostic** - Works with any language/framework via dynamic skills
5. **Minimal prompts** - Low token overhead per step
6. **Clear responsibilities** - No role overlap between SDET and developer

#### 6.1.11 Documentation Skill Token Efficiency

**Decision:** Documentation skills provide read-only (`-ro`) variants for agents that only need to read documentation, dramatically reducing token costs.

**Rationale:**
- Full documentation skills load ~8K tokens (guides + backend implementations)
- Read-only variants load ~500 tokens (lightweight backend operations only)
- Most agents only read documentation (developers, SDET, reviewers)
- Only coordination agents (PO, Architect, Epic Housekeeping) need write access

**Token Comparison:**

| Operation Mode | Agent Types | Guide Loaded | Backend Loaded | Total Tokens |
|----------------|-------------|--------------|----------------|--------------|
| **Read-only** | Developer, SDET, Code Reviewer | No guide | `-ro` variant (~500 tokens) | ~500 |
| **Read-write** | Product Owner, Architect, Epic Housekeeping | Full guide (~4K tokens) | Full backend (~3.5K tokens) | ~8,000 |

**Read-Only Agents (load `-ro` variants):**
- **Developer** - Reads architecture docs for implementation context
- **SDET** - Reads test strategies (not creating comprehensive test plans)
- **Security Reviewer** - Reads ADRs to validate security decisions
- **DevOps Agent** - Reads architecture diagrams for deployment

**Read-Write Agents (load full documentation):**
- **Product Owner** - Creates/updates requirements and acceptance criteria
- **Architect** - Creates/updates architecture docs, ADRs, test strategies
- **Epic Housekeeping** - Updates epic summaries and completion reports

**Agent Self-Awareness:**

Agents determine their own mode based on task:
```yaml
# Agent knows its task from system prompt
IF task involves creating or updating documentation:
  → Load full documentation skill (guide + full backend)
ELSE IF task only involves reading existing documentation:
  → Load read-only variant (no guide, -ro backend)
```

**Skill Variant Resolution:**

When agent loads project-documentation skill:

1. Agent determines operation mode from its task
2. If read-only mode:
   - Try `./.claude/skills/project-documentation/{backend}-ro.md`
   - Fallback to full version if `-ro` not found
3. If read-write mode:
   - Load guide: `./.claude/skills/project-documentation/{guide}.md`
   - Load backend: `./.claude/skills/project-documentation/{backend}.md`

**File Naming Convention:**
- **Read-only backend:** `confluence-atlassian-mcp-ro.md`, `project-documentation-file-ro.md`
- **Full backend:** `confluence-atlassian-mcp.md`, `project-documentation-file.md`
- **Guides:** `product-guide-atlassian.md`, `technical-guide-arc42-c4.md`

**Benefits:**
- 94% token reduction for read-only operations (500 vs 8,000 tokens)
- Developers don't pay cost for documentation creation workflows
- Guide complexity hidden from agents that don't need it
- Seamless fallback if `-ro` variant unavailable

**Why this matters:** In a 10-step epic refinement plan with 6 read-only agents and 4 read-write agents, this saves ~45K tokens ((6 agents × 7,500 tokens saved) = 45,000 tokens saved).

### 6.2 Wrapper Skill Pattern

**Problem:** Skills must be declared statically in agent frontmatter, but projects use different backends (Jira/Confluence, GitHub, file-based, etc.).

**Solution:** Wrapper skills that dispatch to backend-specific implementations based on config.

#### 6.2.1 Architecture

```
Agent declares static skill in frontmatter
         ↓
  project-tracking (wrapper skill)
         ↓
  Reads .scope/config.yaml
         ↓
  Dispatches to implementation:
    - jira-atlassian-mcp
    - jira-sooperset-mcp
    - project-tracking-file
    - project-tracking-github
```

**Agent frontmatter (static, works for all backends):**
```yaml
---
name: product-owner
skills: agent-summary, project-documentation, project-tracking
phases:
  - name: epic_validation
    description: Validate epic business requirements
  - name: epic_definition
    description: Write epic acceptance criteria
---
```

**Config determines backend:**
```yaml
# .scope/config.yaml
tracking:
  skill: jira-atlassian-mcp       # Wrapper dispatches to this implementation
  project_key: CODINT
  atlassian_url: https://...

documentation:
  skill: confluence-atlassian-mcp
  space_key: CODEINTENT
  atlassian_url: https://...
```

#### 6.2.2 Skill Structure

```
src/skills/project-tracking/
├── SKILL.md                      # Wrapper (dispatch logic)
├── jira-atlassian-mcp.md         # Atlassian MCP implementation
├── jira-sooperset-mcp.md         # Sooperset MCP implementation (better auth)
├── project-tracking-file.md      # YAML file implementation
└── project-tracking-github.md    # GitHub Issues implementation

src/skills/project-documentation/
├── SKILL.md                      # Wrapper (dispatch logic)
├── confluence-atlassian-mcp.md   # Atlassian MCP implementation
├── confluence-sooperset-mcp.md   # Sooperset MCP implementation (better auth)
├── project-documentation-file.md
└── project-documentation-notion.md
```

**Wrapper SKILL.md pattern:**
1. Read `.scope/config.yaml` to get backend (e.g., `tracking.skill`)
2. Load corresponding implementation file from same directory
3. Follow implementation instructions with config parameters

**Implementation files:**
- Define operations (get_epic, create_story, etc.)
- Use MCP tools or file operations
- Expect config parameters from wrapper

#### 6.2.3 Core Skills

Three core skills handle project-related operations:

**project-tracking** (wrapper) - Work item tracking:
- Query epics by status
- Create/update stories
- Transition status
- Log progress via comments
- **Implementations:** jira, file, github

**project-documentation** (wrapper) - Corporate memory:
- Store epic design documents
- Create and retrieve ADRs
- Search documentation
- **Implementations:** confluence, file, notion

**agent-summary** - Common protocol:
- Standardized output format for all agents
- AgentResult schema definition
- Status codes and work impact levels
- Concern format and handoff structure
- **Not a wrapper** (single implementation)

All skill types implement a standard interface (see [Skill Interface Contract](./skill-interface-contract.md)).

#### 6.2.4 Adding New Backend Implementations

To add support for a new tracking or documentation system:

**1. Create implementation file in skill directory:**

```bash
# For tracking (e.g., Azure DevOps)
touch src/skills/project-tracking/project-tracking-azuredevops.md

# For documentation (e.g., SharePoint)
touch src/skills/project-documentation/project-documentation-sharepoint.md
```

**2. Implement standard operations:**

Follow existing implementation patterns. Required operations:

**Tracking implementations must provide:**
- `get_epic(epic_id)` - Get epic details and status
- `get_stories(epic_id)` - Get all stories for epic
- `create_story(epic_id, story_data)` - Create story under epic
- `update_story(story_id, fields)` - Update story fields
- `transition_epic(epic_id, status)` - Change epic status
- `add_comment(issue_id, comment)` - Add comment to issue
- `create_epic(epic_data)` - Create new epic

**Documentation implementations must provide:**
- `read(space_key, page_id)` - Read documentation page content
- `write(space_key, page_id, content)` - Create or update page
- `search(query, filters)` - Search documentation
- `ai_search(page_title, additional_details, token_limit)` - AI-powered context search
- `create_page(space_key, title, content, labels)` - Create new page
- `get_page_metadata(page_id)` - Get page metadata

**3. Document configuration requirements:**

```yaml
# Example: Azure DevOps tracking
tracking:
  skill: project-tracking-azuredevops
  organization: myorg
  project: myproject
  personal_access_token: ${AZURE_DEVOPS_PAT}

# Example: SharePoint documentation
documentation:
  skill: project-documentation-sharepoint
  site_url: https://company.sharepoint.com/sites/engineering
  library: Documents
  folder: epics
  access_token: ${SHAREPOINT_TOKEN}
```

**4. Handle errors gracefully:**

Follow error handling patterns from existing implementations:
- Authentication failures → Ask user to re-authenticate
- Permission errors → Explain required permissions
- Resource not found → Clear error message with fix instructions

**5. Install for project:**

```bash
# Copy to project directory
cp src/skills/project-tracking/project-tracking-azuredevops.md \
   ./.claude/skills/project-tracking/

# Or install to user directory
cp src/skills/project-tracking/project-tracking-azuredevops.md \
   ~/.claude/skills/project-tracking/

# Update project config
vim .scope/config.yaml
# Change tracking.skill to "project-tracking-azuredevops"
```

**Wrapper automatically discovers and uses the new implementation** - no wrapper changes needed.

#### 6.2.5 Minimal Agent Prompts

**Decision:** Planners generate minimal prompts containing only `epic_id` and `phase`. Agents read configuration themselves.

**Rationale:**
- Reduces token usage (2 lines vs 10+ lines per prompt)
- Eliminates redundant parameter passing
- Agents access config directly (single source of truth)
- Config changes take effect immediately (no plan regeneration needed)
- Less coupling between planner and agents

**Planner generates:**
```yaml
- step: 1
  agent: product-owner
  prompt: |
    epic_id: "CODINT-1"
    phase: "epic_validation"
  on_success: 2
  on_failure: escalate to user
```

**Agent workflow:**
1. Parse prompt → extract `epic_id` and `phase`
2. Read `.scope/config.yaml` → get tracking/documentation config
3. Load project-tracking skill (wrapper handles dispatch)
4. Load project-documentation skill (wrapper handles dispatch)
5. Execute phase-specific work from agent definition
6. Return AgentResult via agent-summary skill

**Agent reads config dynamically:**
```python
# Agent execution
config = read_yaml(".scope/config.yaml")

# Get tracking backend and parameters
tracking_skill = config.tracking.skill          # "jira-atlassian-mcp"
tracking_params = config.tracking               # {project_key: "CODINT", ...}

# Get documentation backend and parameters
documentation_skill = config.documentation.skill  # "confluence-atlassian-mcp"
documentation_params = config.documentation      # {space_key: "CODEINTENT", ...}

# Invoke wrapper skills (they dispatch to implementations)
Skill(skill="project-tracking", args=f"get {epic_id}")
Skill(skill="project-documentation", args=f"read {epic_id}")
```

**Benefits:**
- Token cost: ~50 tokens/prompt vs ~200+ tokens with full parameters
- Config changes immediate (no plan regen)
- Planner doesn't need to know what parameters each backend needs
- Single source of truth for configuration

### 6.3 Dynamic Agent Discovery

Subagents don't have native access to the agent registry. The planner builds a catalog and stores it in `.scope/` to survive compaction.

**Discovery command:**

Use the `agent-catalog` skill to build the catalog:
```bash
# Generates .scope/agents_catalog.json
# See src/skills/agent-catalog/SKILL.md for implementation
```

### 6.4 Planner Router Architecture

**Decision:** Universal epic-planner acts as router to domain-specific planners based on semantic analysis of epic characteristics.

**Router Pattern (3-step flow):**

```
User invokes: /workplan EPIC-001
       ↓
Step 1: epic-planner (universal router)
       ├─ Fetches epic from tracking system
       ├─ Analyzes labels, title, description
       └─ Determines domain: backend | frontend | marketing
       ↓
Step 2: Load domain-specific planner
       └─ Glob to find: epic-{domain}-planner.md
       ↓
Step 3: Execute domain planner instructions
       └─ Domain planner checks epic_status and creates appropriate plan
```

**Domain Determination Logic:**

Epic-planner uses semantic analysis to route:

| Domain | Indicators | Example Epic |
|--------|-----------|--------------|
| **Backend** | APIs, microservices, databases, authentication, server-side logic, data models, infrastructure | "REST API for user management", "Payment processing service", "Database schema migration" |
| **Frontend** | UI, components, dashboards, user experience, visual design, client-side applications | "Dashboard redesign", "Component library", "Checkout flow UI", "Responsive navigation" |
| **Marketing** | Campaigns, content creation, brand messaging, social media, email marketing, promotional activities | "Q1 product launch campaign", "Content strategy", "Social media promotion" |

**Default:** If domain is ambiguous, routes to backend domain.

**Domain-Specific Planners:**

| Planner | File | Responsibility |
|---------|------|----------------|
| **Epic Backend** | `epic-backend-planner.md` | APIs, services, data processing, authentication, databases |
| **Epic Frontend** | `epic-frontend-planner.md` | UI/UX, components, dashboards, client-side applications |
| **Epic Marketing** | `epic-marketing-planner.md` | Campaigns, content, messaging, promotional activities |
| **TDD Implementation** | `tdd-implementation-planner.md` | Test-first implementation for any epic |
| **Kubernetes Deployer** | `kubernetes-deployer.md` | K8s deployments |
| **Local Deployer** | `local-deployer.md` | E2E tests on laptop |

**Why Router Pattern:**
- Single entry point for epic planning (`/workplan {epic-id}`)
- User doesn't need to specify domain
- Domain expertise encapsulated in domain planners
- Easy to add new domains (add new epic-{domain}-planner.md)
- Epic-planner remains simple (just routing logic)

**Implementation Planning (implicit planner selection through tracking state):**
- User does not need to explicitly specifies planner type: `/workplan STORY-42`
- No router needed - orchestrator invokes planner directly
- For stories, tasks, deployment phases where domain is clear from context

---

## 7. Plan Schema

**File Format:** All plan files, state files, and agent summaries use **JSON format**. Only `.scope/config.yaml` uses YAML.

**File Inventory:**
- **JSON files:** `refine-plan.json`, `impl-plan.json`, `deploy-plan.json`, `current_state.json`, `agents_catalog.json`, `file_plan.json`, `*_token_costs.jsonl`
- **JSONL files:** `refine-agents-summaries.jsonl`, `impl-agents-summaries.jsonl` (newline-delimited JSON)
- **YAML files:** `.scope/config.yaml` (only configuration file in YAML)

### 7.1 Schema for Planners

This is the authoritative schema that planners must generate (shown in YAML notation for readability, but **files are written as JSON**):

```yaml
# Schema Definition for plan.json (JSON format)
# (YAML notation used here for documentation only)

plan:
  metadata: Metadata
  steps: [Step]

---

## Metadata (all fields required)

Metadata:
  epic_id: string                 # Immutable epic identifier
  planner: string                 # Planner agent/system name
  created: string                 # ISO-8601 UTC timestamp
  agents_summaries: string        # Path to aggregated agent summaries output

---

## Step (all fields required unless stated otherwise with a "?")

Step:
  step: integer
  agent?: string                  # If present, orchestrator auto spawn/resume
  prompt?: string
  action?: hook                   # Only for hook steps
  hook_type?: user_approval | system_gate | update_plan
  message?: string
  command?: string
  on_success: Transition
  on_failure: Transition

Required-by-step-type rules:
- Agent step (has `agent`) → agent, prompt
- Hook step (has `action: hook`) → hook_type, plus:
  - user_approval → message
  - system_gate → command
  - update_plan → (no additional fields)

Note: Orchestrator auto-decides spawn vs resume based on agent registry.
First call to an agent = spawn, subsequent calls = resume.

---

## Transition

Transition:
  - integer            # next step number
  - "plan completed"   # terminal success
  - "escalate to user" # manual intervention to address an issue that the agent cannot resolve on its own.

---

## Agent Prompt Contract (planner responsibility)

Every `spawn` or `resume` step MUST instruct the agent to return:

AgentResult:
  status: success | failure | user_input
  work_impact: none | minor | major
  timestamp: string               # ISO-8601 UTC timestamp
  deliverables: json_object | null
  handoff:
    summary: string
    concerns?: [json_object]
  error: string | null

Rules:
- status == success → error must be null
- status == failure → error must be non-null
- status == user_input → agent printed questions, only status field required
- handoff.summary is mandatory for success/failure
- No free-form output outside this structure

---

## Planner Invariants

- Steps are strictly ordered and explicitly linked by transitions
- All branching is declared via on_success / on_failure
- Exactly one step starts execution (step == 1)
- Terminal states must be explicit
- The plan must be executable without external interpretation
```

**Example plan.json:**

```json
// .scope/EPIC-001/refine-plan.json
{
  "metadata": {
    "epic_id": "EPIC-001",
    "planner": "epic-backend-planner",
    "created": "2025-12-15T10:00:00Z",
    "agents_summaries": "refine-agents-summaries.jsonl"
  },
  "steps": [
    {
      "step": 1,
      "agent": "product-owner",
      "prompt": "Define stories for epic EPIC-001.\nRead previous summaries from: .scope/EPIC-001/{{agents_summaries}}",
      "on_success": 2,
      "on_failure": "escalate to user"
    },
    {
      "step": 2,
      "action": "hook",
      "hook_type": "user_approval",
      "message": "Review stories before architecture design",
      "on_success": 3,
      "on_failure": "escalate to user"
    },
    {
      "step": 3,
      "agent": "software-architect",
      "prompt": "Design architecture for EPIC-001.\nRead previous summaries from: .scope/EPIC-001/{{agents_summaries}}",
      "on_success": 4,
      "on_failure": "escalate to user"
    },
    {
      "step": 4,
      "action": "hook",
      "hook_type": "user_approval",
      "message": "Final approval - ready for development?",
      "on_success": "plan completed",
      "on_failure": "escalate to user"
    }
  ]
}
```

### 7.2 Hook Types

| Hook Type | Blocking | Behavior |
|-----------|----------|----------|
| `user_approval` | Yes | Compare `work_impact` vs pre-approval, escalate if needed |
| `system_gate` | Yes | Run `command` via Bash; exit 0 = success, non-zero = failure |
| `update_plan` | No | Reload plan from `current_state.plan_file`, then continue |

**Hook-specific fields:**
- `user_approval`: requires `message`
- `system_gate`: requires `command` (script handles output/retries/delays)
- `update_plan`: no additional fields

**Note on `update_plan`:** Used after a planner agent modifies the plan mid-execution. The initial plan load (via `/scope` command) is handled separately—orchestrator spawns the planner, waits for success, then loads the newly created plan.

**Note on user input:** Planners should NOT use a `user_input` hook type. Instead, agents dynamically request input by returning `status: user_input` when they need it (see [11.4 User Input Pattern](#114-user-input-pattern)). This allows agents to conduct multi-turn interviews as needed, rather than the planner predicting exactly when input is required.

### 7.3 Work Impact & Pre-Approval

Agents report `work_impact` in their output:
- `none` - No changes (read-only analysis)
- `minor` - Small updates, fixes, clarifications
- `major` - New stories, architecture changes, significant work

**Approval logic:**
```
if preapproval == "all":
    continue
elif preapproval == "minor" and work_impact in [none, minor]:
    continue
elif preapproval == "none" and work_impact == none:
    continue
else:
    escalate to user
```

---

## 8. Agent Summaries

**Only agents (spawn/resume actions) write to the summaries file.** Hooks do not produce summaries.

### 8.1 Summary Schema

```yaml
# Schema Definition for agent summaries

## Root

summaries: [SummaryEntry]

---

## SummaryEntry (all fields required unless stated otherwise with a "?")

SummaryEntry:
  step: integer
  agent_name: string
  status: success | failure
  work_impact: none | minor | major   # Scope of work performed in this step
  timestamp: string                   # ISO-8601 UTC timestamp
  deliverables?: yaml_object | null   # Agent- and step-specific. Orchestrator treats as opaque
  handoff: Handoff
  error: string | null                # non-null if status == failure, null if status == success

## Handoff

Handoff:
  summary: string                     # Human-readable description (supports multiline)
  artifacts?: [json_object]           # References to produced artifacts
  concerns?: [Concern]                # Risks, blockers, or questions for downstream steps

## Concern

Concern:
  area: string                        # Domain or system area affected
  issue: string                       # Description of the concern
  severity: low | medium | high

---

## Invariants

- SummaryEntry.step must correspond to an executed plan step
- Orchestrator logic relies only on `status`. All other fields are informational and pass-through
```

### 8.2 Agent Phase Declaration

**Decision:** Agents declare phases in frontmatter to ensure predictable documentation structure and enable phase-specific workflows.

**Frontmatter Format:**

```yaml
---
name: product-owner
description: Product owner responsible for epic validation and definition
model: sonnet
tools: Read, Write, Edit, Bash, Glob, Grep
skills: agent-summary-complex, project-tracking, project-documentation
phases:
  - name: product_discovery
    description: Analyze epic and identify product questions
  - name: product_definition
    description: Define acceptance criteria and user scenarios
  - name: story_validation
    description: Validate story alignment with epic goals
---
```

**Phase Usage:**

1. **In Planner Prompts:**
   ```yaml
   prompt: |
     epic_id: SCOPE-42
     phase: product_discovery
   ```

2. **In Agent Summaries:**
   ```json
   {
     "step": 1,
     "agent_name": "product-owner",
     "phase": "product_discovery",
     "status": "success",
     ...
   }
   ```

3. **In Documentation:**
   - Confluence/Notion: Creates sections based on phase names
   - File-based: Creates files named `{epic-id}-{phase}.md`
   - Enables consistent documentation structure across epics

**Benefits:**
- Predictable documentation layout
- Phase-specific workflows in agent definitions
- Clear separation of concerns within agents
- Documentation tools know where to create/update content
- Orchestrator can track progress by phase

**Common Phase Patterns:**

| Agent | Typical Phases |
|-------|----------------|
| **Product Owner** | `product_discovery`, `product_definition`, `story_validation` |
| **Architect** | `technical_discovery`, `architecture_design`, `story_breakdown`, `file_plan` |
| **Architect Reviewer** | `architecture_review`, `test_strategy_review` |
| **SDET** | `test_implementation` |
| **Developer** | `implementation` |
| **Code Reviewer** | `code_review` |

### 8.3 Summary File Example

```jsonl
# .scope/EPIC-001/refine-agents-summaries.jsonl
{"step":1,"agent_name":"product-owner","status":"success","work_impact":"none","timestamp":"2025-12-15T10:00:00Z","deliverables":null,"handoff":{"summary":"Initialized and ready for epic EPIC-001"},"error":null}
{"step":2,"agent_name":"product-owner","status":"success","work_impact":"major","timestamp":"2025-12-15T10:15:00Z","deliverables":{"stories":[{"title":"User login with OAuth","acceptance_criteria":["Given a user clicks login, they are redirected to OAuth provider","When authentication succeeds, user is logged in"]},{"title":"Session management","acceptance_criteria":["Sessions expire after 24 hours"]}]},"handoff":{"summary":"Created 4 stories for EPIC-001 user authentication","artifacts":[{"type":"story","id":"EPIC-001-1","title":"User login with OAuth"},{"type":"story","id":"EPIC-001-2","title":"Session management"}],"concerns":[{"area":"security","issue":"MFA requirements not specified in epic","severity":"medium"}]},"error":null}
{"step":4,"agent_name":"software-architect","status":"success","work_impact":"minor","timestamp":"2025-12-15T10:45:00Z","deliverables":{"components":[{"name":"AuthService","purpose":"Handle OAuth flow"},{"name":"SessionManager","purpose":"Manage user sessions"}],"decisions":[{"title":"ADR-001: Use JWT for session tokens","rationale":"Stateless, scalable"}]},"handoff":{"summary":"Designed 3-service architecture with JWT auth.\nCreated ADR-001 for session management decision.","artifacts":[{"type":"adr","id":"ADR-001","title":"JWT for session management"}],"concerns":[]},"error":null}
```

---

## 9. State Management

### 9.1 Current State File

The orchestrator's source of truth is `.scope/{epic-id}/current_state.json`:

```json
// .scope/EPIC-001/current_state.json
{
  "plan_file": "refine-plan.json",
  "current_step": 3,
  "agents_summaries": "refine-agents-summaries.jsonl",
  "preapproval": "minor"
}
```

**Fields:**
- `plan_file` - Which plan is being executed
- `current_step` - Current step number
- `agents_summaries` - Where agent summaries are stored
- `preapproval` - Pre-approval setting (optional)

### 9.2 Plan Status

Plan status is inferred, not stored:
- **in_progress** - Orchestrator is executing steps
- **escalated** - Waiting for `/continue` or `/gobackto`
- **completed** - Reached `on_success: plan completed`

---

## 10. Orchestrator Execution

### 10.1 Execution Loop

**Initial Setup (before loop):**
```
0. Read current_state.json → get plan_file name
1. Read plan from plan_file (ONCE - keep in memory)
2. Read config.yaml → orchestration settings (usable_window, min_available_*)
3. Discover session ID:
   a. Generate UUID marker
   b. Echo marker: bash("echo 'ORCHESTRATOR_MARKER: {marker}'")
   c. Find log file: grep -l '{marker}' ~/.claude/projects/{path}/*.jsonl | grep -v agent-
   d. Extract session_id from log: tail -1 {log_file} | jq -r '.sessionId'
4. Detect OS and set script extension:
   a. script_ext = '.ps1' if Windows else '.sh'
5. Discover script path:
   a. Check ./.claude/agents/scripts/agents-tokens{script_ext}
   b. If not found, check ~/.claude/agents/scripts/agents-tokens{script_ext}
   c. If not found, ERROR - scripts not found
6. Get baseline timestamp:
   a. Run: bash("{script_path}/agents-tokens{script_ext} --session-id {session_id}")
   b. Parse JSON: initial_data = json.loads(result.stdout)
   c. Store: previous_timestamp = initial_data['main_agent']['timestamp']
```

**Execution Loop:**
```
1. Read current_state.json → plan_file, current_step, agents_summaries, preapproval
   (Plan stays in memory - NOT re-read unless update_plan hook triggered)
2. Find step in plan where step == current_step
3. Execute step based on action:

   IF step.agent:
     # SPAWN/RESUME DECISION: Check context usage (see Section 11.3)
     should_resume_result, agent_id_or_reason = should_resume(
         step.agent, epic_id, agents_summaries, config
     )

     # Capture start timestamp for telemetry
     started_timestamp = current_time_utc()  # ISO-8601 format

     # Execute with error recovery for corrupted conversations
     resume_failed = False
     resume_failure_reason = None

     IF should_resume_result:
       TRY:
         result = Task(agent, prompt, resume=agent_id_or_reason)
         print(f"✓ Resumed {step.agent} (agent_id: {agent_id_or_reason})")

       EXCEPT APIError as e:
         IF "tool use concurrency" in str(e) OR "400" in str(e):
           # Agent conversation corrupted, spawn fresh instead
           result = Task(agent, prompt)
           agent_id = result.agent_id
           resume_failed = True
           resume_failure_reason = str(e)
         ELSE:
           RAISE e
     ELSE:
       result = Task(agent, prompt)
       agent_id = result.agent_id
       print(f"✓ Spawned new {step.agent} (reason: {agent_id_or_reason})")

     # Analyze token usage (see Section 10.3)
     tokens_result = bash(f"{script_path}/agents-tokens{script_ext} --session-id {session_id} --after {previous_timestamp}")

     IF tokens_result.exit_code != 0:
       # Script failed - use safe defaults
       current_timestamp = current_time_utc().isoformat()
       main_context_usage = 0
       subagent_context_usage = config.orchestration.usable_window - 5000
       main_cost = 0.0
       subagent_cost = 0.0
       tokens_data = None
     ELSE:
       tokens_data = json.loads(tokens_result.stdout)
       current_timestamp = tokens_data['main_agent']['timestamp']
       main_context_usage = tokens_data['main_agent']['context_usage']
       main_cost = tokens_data['main_agent']['total_cost_usd']

       # Find current subagent in subagents array
       current_subagent = find_subagent_by_id(tokens_data['subagents'], agent_id)
       IF current_subagent:
         subagent_context_usage = current_subagent['max_context_usage']['context_usage']
         subagent_cost = current_subagent['summary_statistics']['total_cost_usd']
       ELSE:
         subagent_context_usage = config.orchestration.usable_window - 5000
         subagent_cost = 0.0

     # Append token costs to JSONL file
     IF tokens_data is not None:
       token_costs_file = f".scope/{epic_id}/{epic_id}_token_costs.jsonl"
       token_cost_entry = {
         **tokens_data,
         'step': current_step,
         'agent': step.agent,
         'timestamp_recorded': current_time_utc().isoformat()
       }
       append_jsonl(token_costs_file, token_cost_entry)

     # Calculate duration
     duration_seconds = calculate_duration(previous_timestamp, current_timestamp)

     # Log spawn/resume decision (see Section 10.3)
     IF resume_failed:
       log_decision(epic_id, current_step, step.agent,
                   'spawn_after_resume_failure',
                   f"resume_failed: {resume_failure_reason}",
                   0, config)
     ELSE:
       log_decision(epic_id, current_step, step.agent,
                   'resume' if should_resume_result else 'spawn',
                   agent_id_or_reason, subagent_context_usage, config)

     # Handle agent result based on status
     IF result.status == user_input:
       Display agent output to user
       STOP and wait for user response
       # When user responds: Resume agent with user response
       # Loop until status != user_input

     IF result.status == success:
       # Build enhanced telemetry with cost breakdown
       telemetry = {
         'agent_name': step.agent,
         'agent_id': agent_id,
         'tokens_used': subagent_context_usage,
         'subagent_context_usage': subagent_context_usage,
         'main_agent_context_usage': main_context_usage,
         'completed': current_timestamp,
         'duration_seconds': duration_seconds,
         'costs': {
           'subagent_usd': subagent_cost,
           'main_agent_usd': main_cost,
           'total_step_usd': subagent_cost + main_cost
         }
       }

       summary_entry = {**result, 'telemetry': telemetry}
       append_jsonl(agents_summaries_file, summary_entry)
       current_step = step.on_success
       previous_timestamp = current_timestamp

     IF result.status == failure:
       # Build enhanced telemetry with cost breakdown
       telemetry = {
         'agent_name': step.agent,
         'agent_id': agent_id,
         'tokens_used': subagent_context_usage,
         'subagent_context_usage': subagent_context_usage,
         'main_agent_context_usage': main_context_usage,
         'completed': current_timestamp,
         'duration_seconds': duration_seconds,
         'costs': {
           'subagent_usd': subagent_cost,
           'main_agent_usd': main_cost,
           'total_step_usd': subagent_cost + main_cost
         }
       }

       summary_entry = {**result, 'telemetry': telemetry}
       append_jsonl(agents_summaries_file, summary_entry)
       current_step = step.on_failure
       previous_timestamp = current_timestamp

   IF action == hook:
     # Hooks do NOT write to summaries file
     IF hook_type == user_approval:
       Check preapproval against work_impact (in memory from previous agent)
       IF should_auto_approve(preapproval, work_impact): current_step = on_success
       ELSE: escalate to user (wait for /approve), STOP
     ELIF hook_type == user_input:
       Request input from user, STOP
     ELIF hook_type == update_plan:
       Reload plan from current_state.plan_file
       current_step = step.on_success
     ELIF hook_type == system_gate:
       Run step.command via Bash (foreground, output visible)
       IF exit code == 0: current_step = on_success
       ELSE: current_step = on_failure

5. IF current_step == "plan completed": Done!
   ELIF current_step == "escalate to user": Wait for /continue
   ELSE:
     # Handle all-until expiration
     IF preapproval starts with "all-until" AND current_step == target_step:
       preapproval = "none"
     Save current_step (and preapproval if changed), GOTO step 3
```

### 10.2 Approval Logic

```python
def should_auto_approve(preapproval, work_impact):
    if preapproval == "all" or preapproval.startswith("all-until"):
        return True
    if preapproval == "minor" and work_impact in ["none", "minor"]:
        return True
    if preapproval == "none" and work_impact == "none":
        return True
    return False
```

### 10.3 Token Usage and Cost Tracking

**Decision:** Orchestrator tracks token usage and costs per step to enable cost analysis and optimization.

**Tracking Mechanism:**

After each agent execution, orchestrator:
1. Runs `agents-tokens.{sh|ps1}` script with timestamp filtering
2. Extracts token usage for main agent and current subagent
3. Calculates costs based on API pricing
4. Appends to `{epic-id}_token_costs.jsonl`

**Script Usage:**

```bash
# Initial baseline (before first step)
agents-tokens.sh --session-id abc123-def456
# Returns: {main_agent: {timestamp: "2025-01-12T10:00:00Z", ...}, subagents: [...]}

# After each step (incremental tracking)
agents-tokens.sh --session-id abc123-def456 --after "2025-01-12T10:00:00Z"
# Returns: Only new events since timestamp
```

**Token Data Structure:**

```json
{
  "main_agent": {
    "sessionId": "abc123-def456",
    "timestamp": "2025-01-12T10:15:30.123Z",
    "context_usage": 45234,
    "total_cost_usd": 0.15
  },
  "subagents": [
    {
      "agent_id": "agent_789xyz",
      "agent_name": "product-owner",
      "max_context_usage": {
        "timestamp": "2025-01-12T10:12:45.678Z",
        "context_usage": 28456
      },
      "summary_statistics": {
        "total_cost_usd": 0.08,
        "total_input_tokens": 25000,
        "total_output_tokens": 3456
      }
    }
  ]
}
```

**Cost Breakdown Calculation:**

```python
# After running agents-tokens script
tokens_data = json.loads(script_output)

# Main agent costs (orchestrator conversation)
main_cost = tokens_data['main_agent']['total_cost_usd']
main_context_usage = tokens_data['main_agent']['context_usage']

# Find current subagent by agent_id
current_subagent = find_by_id(tokens_data['subagents'], agent_id)
subagent_cost = current_subagent['summary_statistics']['total_cost_usd']
subagent_context_usage = current_subagent['max_context_usage']['context_usage']

# Total step cost
total_step_cost = main_cost + subagent_cost

# Append to token costs file
telemetry = {
  'agent_name': agent_name,
  'agent_id': agent_id,
  'subagent_context_usage': subagent_context_usage,
  'main_agent_context_usage': main_context_usage,
  'costs': {
    'subagent_usd': subagent_cost,
    'main_agent_usd': main_cost,
    'total_step_usd': total_step_cost
  }
}
```

**Token Costs File Format:**

`.scope/{epic-id}/{epic-id}_token_costs.jsonl` (newline-delimited JSON):

```jsonl
{"step":1,"agent":"product-owner","timestamp_recorded":"2025-01-12T10:15:30Z","main_agent":{"context_usage":45234,"total_cost_usd":0.15},"subagents":[{"agent_id":"agent_789xyz","agent_name":"product-owner","max_context_usage":{"context_usage":28456},"summary_statistics":{"total_cost_usd":0.08}}]}
{"step":2,"agent":"architect","timestamp_recorded":"2025-01-12T10:45:12Z","main_agent":{"context_usage":52891,"total_cost_usd":0.18},"subagents":[{"agent_id":"agent_abc123","agent_name":"architect","max_context_usage":{"context_usage":35678},"summary_statistics":{"total_cost_usd":0.12}}]}
```

**Timestamp Filtering (`--after` parameter):**

- **Purpose:** Only fetch token data for NEW events since last check
- **Benefit:** Reduces script execution time from ~3s to ~0.5s for incremental updates
- **Usage:** `--after "2025-01-12T10:00:00Z"` returns only events after timestamp
- **Format:** ISO-8601 UTC timestamp from previous execution

**Error Handling:**

If `agents-tokens` script fails (exit code != 0):
- Use safe defaults to avoid blocking execution
- Log warning to user
- Set `subagent_context_usage` to `usable_window - 5000` (conservative estimate)
- Set costs to 0.0
- Continue execution (don't block on telemetry failures)

**Script Location Resolution:**

Orchestrator checks in order:
1. `./.claude/agents/scripts/agents-tokens.{sh|ps1}` (project override)
2. `~/.claude/agents/scripts/agents-tokens.{sh|ps1}` (user install)
3. ERROR if not found

**OS Detection:**

```python
import platform
script_ext = '.ps1' if platform.system() == 'Windows' else '.sh'
script_name = f'agents-tokens{script_ext}'
```

**Session ID Discovery:**

Orchestrator discovers session ID by:
1. Generate unique UUID marker
2. Echo marker to conversation: `bash("echo 'ORCHESTRATOR_MARKER: {marker}'")`
3. Find log file: `grep -l '{marker}' ~/.claude/projects/{path}/*.jsonl`
4. Filter out agent logs: `grep -v agent-`
5. Extract session_id: `tail -1 {log_file} | jq -r '.sessionId'`

**Cost Analysis Use Cases:**

- **Per-Epic Cost:** Sum all `total_step_usd` from token_costs.jsonl
- **Per-Agent Cost:** Sum costs grouped by `agent` field
- **Optimization:** Identify high-cost agents for refactoring
- **Budget Tracking:** Monitor cumulative costs across epics
- **Context Window Management:** Track when agents approach limits

**Integration with Agent Summaries:**

Telemetry is embedded in agent summaries (see Section 8.1):

```json
{
  "step": 1,
  "agent_name": "product-owner",
  "status": "success",
  "telemetry": {
    "agent_id": "agent_789xyz",
    "subagent_context_usage": 28456,
    "main_agent_context_usage": 45234,
    "duration_seconds": 195,
    "costs": {
      "subagent_usd": 0.08,
      "main_agent_usd": 0.15,
      "total_step_usd": 0.23
    }
  }
}
```

---

## 11. Subagent Execution Model

### 11.1 No Nested Spawning

**Subagents cannot spawn other subagents.** This is a Claude Code constraint. Only the orchestrator can spawn subagents.

```
✓ Main Agent → Subagent A
✓ Main Agent → Subagent B
✗ Subagent A → Subagent C  (NOT ALLOWED)
```

### 11.2 Persistent Context Windows

When a subagent completes a task, its context window is NOT flushed. Using `resume`, the orchestrator continues the conversation with the same agent, and the agent retains full history.

### 11.3 Context-Aware Resume Logic

**Decision:** Orchestrator decides spawn vs resume based on agent's context window usage, with per-agent overrides for optimization.

**Problem:**
- Resuming agents with large context can hit API limits (200K tokens)
- Not all agents need full conversation history
- Fresh spawns reset context but lose agent-specific knowledge

**Solution:**
Orchestrator uses `should_resume()` function with configurable thresholds:

```python
def should_resume(agent_name, epic_id, agents_summaries, config):
    """
    Determine if agent should be resumed or spawned fresh.

    Returns:
        (True, agent_id) - Resume with this agent_id
        (False, reason) - Spawn fresh with reason
    """
    # 1. Load config with defaults
    usable_window = config.orchestration.usable_window  # Default: 190000
    min_available_default = config.orchestration.min_available_default  # Default: 10000

    # 2. Check for agent-specific override
    agent_overrides = config.orchestration.agent_min_available or {}
    min_available = agent_overrides.get(agent_name, min_available_default)

    # 3. Find previous execution for this agent
    previous_summary = find_latest_summary(agents_summaries, agent_name)

    if previous_summary is None:
        return (False, "first_invocation")

    # 4. Check context usage from telemetry
    telemetry = previous_summary.get('telemetry', {})
    context_usage = telemetry.get('subagent_context_usage', 0)

    # 5. Calculate available headroom
    available = usable_window - context_usage

    # 6. Decision based on available headroom
    if available >= min_available:
        agent_id = telemetry.get('agent_id')
        if agent_id:
            return (True, agent_id)
        else:
            return (False, "no_agent_id_in_telemetry")
    else:
        reason = f"insufficient_headroom (available: {available}, needed: {min_available})"
        return (False, reason)
```

**Configuration Example:**

`.scope/config.yaml`:
```yaml
orchestration:
  usable_window: 190000           # Conservative limit (200K - 10K buffer)
  min_available_default: 10000    # Default headroom needed
  agent_min_available:            # Per-agent overrides
    architect: 25000              # Architect needs more room for documentation
    developer: 15000              # Developer needs moderate room for code
    product-owner: 5000           # PO needs minimal room (reads summaries)
```

**Decision Logic:**

| Agent | Context Usage | Available Headroom | Min Required | Decision |
|-------|---------------|-------------------|--------------|----------|
| product-owner | 28K | 162K | 5K | ✅ Resume (ample headroom) |
| architect | 165K | 25K | 25K | ✅ Resume (exactly at threshold) |
| architect | 170K | 20K | 25K | ❌ Spawn (insufficient headroom) |
| developer | 180K | 10K | 15K | ❌ Spawn (insufficient headroom) |

**Why Per-Agent Overrides:**

Different agents have different continuation needs:

| Agent Type | Min Required | Rationale |
|------------|--------------|-----------|
| **Architect** | 25K | Needs room to write architecture docs, ADRs, test strategies |
| **Developer** | 15K | Needs room to write implementation code and debug |
| **SDET** | 15K | Needs room to write test code |
| **Product Owner** | 5K | Mostly reads summaries, minimal new output |
| **Reviewer** | 10K | Reads existing work, provides feedback |

**Resume Failure Recovery:**

If resume fails with API error (400, tool concurrency):
```python
try:
    result = Task(agent, prompt, resume=agent_id)
except APIError as e:
    if "400" in str(e) or "tool use concurrency" in str(e):
        # Conversation corrupted, spawn fresh
        result = Task(agent, prompt)
        log_decision(epic_id, step, agent, 'spawn_after_resume_failure', str(e))
    else:
        raise e
```

**Decision Logging:**

Orchestrator logs spawn/resume decisions for analysis:

```jsonl
{"epic_id":"SCOPE-42","step":1,"agent":"product-owner","decision":"spawn","reason":"first_invocation","context_usage":0}
{"epic_id":"SCOPE-42","step":3,"agent":"product-owner","decision":"resume","reason":"agent_abc123","context_usage":28456}
{"epic_id":"SCOPE-42","step":5,"agent":"architect","decision":"spawn","reason":"insufficient_headroom (available: 20000, needed: 25000)","context_usage":170000}
{"epic_id":"SCOPE-42","step":7,"agent":"architect","decision":"spawn_after_resume_failure","reason":"APIError: 400 Bad Request - tool use concurrency","context_usage":0}
```

**Benefits:**

1. **Automatic optimization** - Agents spawn fresh when needed
2. **Cost efficiency** - Resume when safe (lower API costs)
3. **Agent-specific tuning** - Different agents have different needs
4. **Error recovery** - Graceful handling of corrupted conversations
5. **Observability** - Decision logging for debugging

**Token Cost Impact:**

- **Resume:** ~$0.05 per continuation (uses existing context)
- **Spawn:** ~$0.15 per fresh start (loads all skills, instructions)
- **Savings:** 66% cost reduction when resuming is safe

**Default Behavior (no config):**

If config missing, use safe defaults:
```python
usable_window = 190000
min_available_default = 10000
agent_min_available = {}  # No overrides, all agents use 10K
```

**Agent Context Access:**

Agents read summaries file for previous work:
- Each agent reads `.scope/{epic-id}/{agents_summaries_file}`
- Agents see all previous agent outputs (not full conversation context)
- Fresh spawn agents still have full knowledge of epic progress

### 11.4 User Input Pattern

Subagents spawned via the Task tool run to completion - they cannot pause mid-execution to wait for user input. When an agent needs user input:

1. **Agent prints questions** directly to output
2. **Agent returns** `status: user_input` (minimal return, no other fields required)
3. **Orchestrator displays** agent output to user
4. **Orchestrator waits** for user response
5. **Orchestrator resumes** agent with user's answer as the prompt
6. **Agent continues** processing, may return `user_input` again or `success`/`failure`

**Example flow:**
```
Orchestrator: Task(product-owner, "Break epic into stories")
Agent output: "The epic description is incomplete. What is the target user persona?"
Agent return: status: user_input

User types: "Mobile app users aged 25-40"

Orchestrator: Task(product-owner, "Mobile app users aged 25-40", resume=agent_id)
Agent output: "Thanks. What are the main pain points we're solving?"
Agent return: status: user_input

User types: "Slow checkout process and limited payment options"

Orchestrator: Task(product-owner, "Slow checkout process...", resume=agent_id)
Agent output: [Creates stories based on gathered information]
Agent return: status: success, work_impact: major, ...
```

This pattern allows agents to conduct multi-turn interviews when epic details are incomplete.

---

## 12. Skills

Skills provide abstraction layers between agents and external systems, allowing different backends (Jira/Confluence, GitHub, local files) to be swapped without changing agent logic.

### 12.1 Skill Configuration

Skills are configured in `.scope/config.yaml`:

```yaml
tracking:
  skill: jira-atlassian-mcp             # or jira-sooperset-mcp, project-tracking-file, project-tracking-github
  project_key: CODINT
  atlassian_url: https://aquaforge-ai.atlassian.net

documentation:
  skill: confluence-atlassian-mcp       # or confluence-sooperset-mcp, project-documentation-file, project-documentation-notion
  space_key: CODEINTENT
  atlassian_url: https://aquaforge-ai.atlassian.net
```

Agents use wrapper skills (project-tracking, project-documentation) which read config and dispatch to the configured backend.

### 12.2 Skill Categories

| Category | Purpose | Backend Implementations |
|----------|---------|-------------------------|
| **project-tracking** | Work item tracking, status, stories | `jira-atlassian-mcp`, `jira-sooperset-mcp`, `project-tracking-file`, `project-tracking-github` |
| **project-documentation** | Design docs, ADRs, decision records | `confluence-atlassian-mcp`, `confluence-sooperset-mcp`, `project-documentation-file`, `project-documentation-notion` |
| **agent-summary** | Standard output protocol for all agents | `agent-summary` |
| **git-workflow** | Worktrees for implementation isolation | `git-workflow` |
| **agent-catalog** | Agent discovery and metadata | `agent-catalog` |

### 12.3 Skill Structure

Each skill lives in a directory with these files:

```
src/skills/{skill-name}/
├── SKILL.md      # Main skill definition (operations, examples)
├── validate.md   # Validation checks for /scope validate
└── scripts/      # Optional: skill-specific helper scripts
    ├── *.sh      # Unix/Mac scripts
    └── *.ps1     # Windows PowerShell scripts
```

**SKILL.md** defines:
- Skill metadata (name, description)
- Operations with signatures and examples
- Environment variables required
- Anti-patterns to avoid

**validate.md** defines checks for `/scope validate`:
- API connectivity
- Authentication validity
- Required resources exist (project, space, etc.)

**scripts/** (optional):
- Helper scripts for skill operations
- Platform-specific implementations (.sh for Unix/Mac, .ps1 for Windows)
- Examples: HTTP wrappers, data transformers, CLI tools
- Script location resolution:
  1. `./.claude/skills/{skill-name}/scripts/` (project override)
  2. `~/.claude/skills/{skill-name}/scripts/` (user install)
  3. `{scope-install}/src/skills/{skill-name}/scripts/` (system default)

**Example with scripts:**

```
src/skills/project-tracking/
├── SKILL.md
├── validate.md
├── jira-atlassian-mcp.md
├── jira-sooperset-mcp.md
└── scripts/
    ├── jira-sooperset-mcp-http.sh   # HTTP wrapper for Jira MCP
    └── jira-sooperset-mcp-http.ps1  # Windows version
```

Scripts are co-located with skills for easier maintenance and distribution.

### 12.4 Core Operations Pattern

All management and documentation skills follow this pattern:

| Operation Type | Management Skill | Documentation Skill |
|----------------|------------------|---------------------|
| **Create** | `create_story(epic_id, title, criteria)` | `create_epic_page(epic_id, title, content)` |
| **Read** | `get_epic_status(epic_id)` | `get_epic_page(epic_id)` |
| **Update** | `transition_status(issue_id, status)` | `update_story_section(story_id, section, content)` |
| **Query** | `get_stories_by_epic(epic_id)` | `search_documents(query)` |
| **Comment** | `add_comment(issue_id, comment)` | N/A |

### 12.5 Git Workflow Skill

Manages worktrees for implementation isolation:

| Operation | Description |
|-----------|-------------|
| `create_worktree(epic_id, title)` | Create implementation worktree |
| `switch_to_worktree(epic_id)` | Change to worktree directory |
| `merge_worktree(epic_id)` | Merge back to main |
| `list_worktrees()` | List active worktrees |

### 12.6 Agent Catalog Skill

Discovers available agents for planner use:

| Operation | Description |
|-----------|-------------|
| `build_catalog()` | Scan agents, write to agents_catalog.json |
| `get_catalog()` | Return cached catalog |
| `get_agents(category?)` | Get agents, optionally filtered |

### 12.7 Creating New Skills

To add support for a new tool (e.g., GitHub Issues, Azure DevOps, Notion):

1. **Create skill directory:**
   ```
   src/skills/epic-tracking-github/
   ├── SKILL.md
   └── validate.md
   ```

2. **Implement required operations** in SKILL.md following the pattern of existing skills

3. **Add validation checks** in validate.md:
   - API/MCP connectivity
   - Authentication
   - Required resources exist

4. **Map native statuses** to standard values:

   | Standard Status | Description |
   |-----------------|-------------|
   | `backlog` | Not started |
   | `refinement` | Being planned |
   | `in_progress` | Being implemented |
   | `done` | Completed |

5. **Handle errors** with structured responses:
   ```yaml
   error:
     type: not_found | auth_failed | permission_denied
     message: "Human-readable message"
   ```

### 12.8 Skill Resolution Order

When loading a skill, SCOPE checks in order:

```
1. .scope/skills/{skill-name}/     (project override)
2. ~/.claude/skills/{skill-name}/  (user customization)
3. {scope-install}/src/skills/{skill-name}/  (system default)
```

This allows projects to override specific skills without modifying the installation.

### 12.9 Skill Variants for Token Efficiency

**Decision:** Skills can provide lightweight variants (`-ro` for read-only, `-lite` for minimal) to reduce token costs for agents that don't need full capabilities.

**Pattern:**

Skills with multiple variants use file naming conventions:

```
src/skills/project-documentation/
├── SKILL.md                              # Wrapper (dispatches to variants)
├── confluence-atlassian-mcp.md           # Full backend (8K tokens)
├── confluence-atlassian-mcp-ro.md        # Read-only variant (500 tokens)
├── project-documentation-file.md         # Full backend
├── project-documentation-file-ro.md      # Read-only variant
├── product-guide-atlassian.md            # Creation guide (4K tokens)
└── technical-guide-arc42-c4.md           # Architecture guide (4K tokens)
```

**Variant Types:**

| Variant | Suffix | Token Cost | Use Case | Example Agents |
|---------|--------|------------|----------|----------------|
| **Full** | (none) | ~8K | Create/update documentation, comprehensive workflows | Product Owner, Architect, Epic Housekeeping |
| **Read-only** | `-ro` | ~500 | Read existing documentation, no writes | Developer, SDET, Code Reviewer, DevOps |
| **Lite** | `-lite` | ~2K | Minimal operations, specific tasks | Quick lookups, validation checks |

**Variant Selection Logic:**

Agents determine which variant to load based on their task:

```python
# Agent self-awareness during skill loading
def load_documentation_skill(task_type):
    config = read_yaml(".scope/config.yaml")
    backend = config.documentation.skill  # e.g., "confluence-atlassian-mcp"

    if task_requires_write_operations(task_type):
        # Load full documentation with guide
        guide = load_guide(config.documentation.guide)  # 4K tokens
        backend_impl = load_backend(backend)             # 3.5K tokens
        return guide + backend_impl                       # ~8K total

    else:  # Read-only operations
        # Try to load read-only variant
        ro_backend = f"{backend}-ro"
        if exists(ro_backend):
            return load_backend(ro_backend)               # ~500 tokens
        else:
            # Fallback to full version
            return load_backend(backend)                  # 3.5K tokens
```

**Task Type Detection:**

Agents know their operation mode from phase or system prompt:

| Task Description | Variant | Reason |
|------------------|---------|---------|
| "Read architecture docs for implementation context" | `-ro` | No documentation changes |
| "Create ADR for API versioning strategy" | Full | Creates new documentation |
| "Review test strategy document" | `-ro` | Read-only review |
| "Update epic summary with implementation results" | Full | Updates documentation |

**Read-Only Backend Structure:**

`confluence-atlassian-mcp-ro.md` contains only read operations:

```markdown
# Confluence Read-Only Backend

**Operations:**
- `read(page_id)` - Read page content
- `search(query)` - Search documentation
- `get_metadata(page_id)` - Get page metadata
- `ai_search(query, token_limit)` - AI-powered context search

**NOT INCLUDED (full version only):**
- Write operations
- Page creation
- Section updates
- Label management
- Comprehensive guides

**Token cost: ~500 tokens vs ~8,000 for full version**
```

**Guide Loading (Full Version Only):**

Full documentation skill loads guides based on config:

```yaml
# .scope/config.yaml
documentation:
  skill: confluence-atlassian-mcp
  guide: product-guide-atlassian    # For product-owner
  # OR
  guide: technical-guide-arc42-c4   # For architect
```

Read-only variants skip guide loading entirely.

**Token Savings Calculation:**

10-step epic refinement plan:
- 6 read-only agents (Developer, SDET, 2× Reviewer)
- 4 read-write agents (Product Owner, Architect, 2× Epic Housekeeping)

**Without variants:**
- 10 agents × 8K tokens = 80K tokens

**With variants:**
- 6 agents × 500 tokens = 3K tokens (read-only)
- 4 agents × 8K tokens = 32K tokens (read-write)
- **Total:** 35K tokens
- **Savings:** 45K tokens (56% reduction)

**Fallback Behavior:**

If `-ro` variant not found:
1. Agent attempts to load `{backend}-ro.md`
2. File not found → Falls back to full `{backend}.md`
3. Agent continues with full version (graceful degradation)
4. No error, but logs warning for performance optimization

**When to Create Variants:**

Create variant when:
- Skill has >3K token full version
- Multiple agents use skill in read-only mode
- Backend operations separable (read vs write)
- Performance optimization needed

**Don't create variant if:**
- Full version already <1K tokens
- Only one agent uses skill
- Operations tightly coupled (can't separate read/write)

**Implementation Example:**

```bash
# Create read-only variant
cp src/skills/project-documentation/confluence-atlassian-mcp.md \
   src/skills/project-documentation/confluence-atlassian-mcp-ro.md

# Edit -ro version:
# 1. Remove write operations (create, update, delete)
# 2. Remove comprehensive workflow guides
# 3. Keep only: read, search, get_metadata, ai_search
# 4. Reduce to ~500 tokens
```

**Benefits:**

1. **Cost optimization** - 56% token reduction for read-heavy workflows
2. **Faster loading** - Agents load only what they need
3. **Clarity** - Read-only agents can't accidentally write
4. **Backward compatible** - Graceful fallback to full version
5. **Self-selecting** - Agents choose variant based on task

---

## 13. User Workflow

Example session using slash commands:

```bash
# Start Claude in project directory
$ cd ~/projects/myapp
$ claude

# Check what needs refinement (use epic-tracking skill)
> What epics need refinement?
  → EPIC-001: Payment Gateway (Ready for Refinement)
  → EPIC-002: Dashboard Redesign (Ready for Refinement)

# Start refinement with backend planner
> /scope backend EPIC-001
  → Planner creating .scope/EPIC-001/refine-plan.json...
  → Step 1: Spawning product-owner...
  → Step 2: Defining stories...
  → Step 3: Approval needed - "Review stories before architecture"

  Work impact: major
  Use /approve to proceed, /continue to re-engage agent, /preapprove to change settings

# Set pre-approval for minor changes
> /preapprove minor
  → Pre-approval set to: minor

# Approve current major change
> /approve
  → Approved. Moving to next step...
  → Step 4: Architecture design (work_impact: minor) - auto-approved
  → Step 5: Final approval needed

# Ask product-owner a question before approving
> /tell product-owner why did we choose OAuth instead of SAML?
  → product-owner: We chose OAuth because...

# Final approval
> /approve
  → Plan completed! Epic EPIC-001 refinement finished.
```

---

## 14. Build Order

### Phase 0: Infrastructure
- [x] Create docker-compose.memgraph.yaml
- [x] Create install.sh script
- [x] Create scope-init.sh script

### Phase 1: Core Skills
- [x] Create agent-catalog skill
- [x] Create skill-interface-contract.md
- [x] Create project-documentation wrapper + confluence implementation (v2.5)
- [x] Create project-tracking wrapper + jira implementation (v2.5)
- [x] Create git-workflow skill
- [x] Create project-documentation-file.md (v2.5)
- [x] Create project-tracking-file.md (v2.5)

### Phase 2: Core Agents
- [x] Create orchestrator agent
- [x] Create epic-backend-planner
- [x] Create test-first-planner

### Phase 3: Execution Agents
- [x] product-owner
- [x] software-architect
- [x] architect-reviewer
- [x] agent-summary skill (common protocol)

### Phase 4: Documentation
- [ ] Installation guide
- [ ] Usage guide
- [ ] Troubleshooting guide

### Phase 5: Integration Test
- [ ] End-to-end test with single epic
- [ ] Verify agent catalog survives compaction
- [ ] Verify resume from paused state

---

## 15. Summary

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Orchestrator** | Execute plans via commands (/scope, /continue, /tell) | `orchestrator.md` |
| **Planners** | Create directory, catalog, plan.json | `planners/**/*.md` |
| **Epic Documentation** | Design docs, ADRs (Confluence or file) | `.claude/skills/epic-documentation.md` |
| **Epic Management** | Status, stories (Jira or file) | `.claude/skills/epic-tracking.md` |
| **Agent Summary Protocol** | Standard output format for all agents | `src/skills/agent-summary-{core,complex,orchestrator}/SKILL.md` |
| **Git Skill** | Worktree management | `git-workflow.md` |
| **Agent Catalog** | Discover available agents | `agent-catalog.md` |
| **Plans** | Execution contracts with numbered steps | `.scope/{epic-id}/*-plan.json` |
| **Agent Summaries** | JSONL summaries with status, work_impact | `.scope/{epic-id}/*-agents-summaries.jsonl` |
| **Current State** | plan_file, current_step, preapproval | `.scope/{epic-id}/current_state.json` |

---

## Related Documents

**[Arc42 + C4 Documentation Standard](scope-doc-arc42-c4.md)** - Recommended documentation structure using Arc42 template with C4 diagrams, page templates, agent-page mapping, and documentation guidelines for SCOPE-managed projects.
