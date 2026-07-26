<p align="center">
  <img src="assets/scope-banner.png" alt="SCOPE Banner" />
</p>

# SCOPE

**Simple Claude Orchestrator for Product Engineering**

SCOPE turns Claude Code into a structured product engineering environment. It gives you slash commands that take a product from PRD to implemented, tested, and audited epics — with approval gates at every step.

Idea → /prd_create → /prd_refine → /prd_breakdown → /epic_refine → /implement → merge

**Already have code but no docs?** Use `/re_documentation` to reverse engineer the product and architecture documentation from your existing codebase.

No custom tooling. No MCP servers. Just Claude Code slash commands, agents, skills, and documentation templates.

---

## What It Does

### Forward Engineering (PRD to Code)

- **`/prd_create`** — Interview the user to create a lightweight first-pass PRD before refinement
- **`/prd_refine`** — Interactively refine a product requirements document using a checklist-driven approach
- **`/prd_breakdown`** — Break the PRD into implementable epics with architecture and dependency analysis
- **`/epic_refine`** — Build a risk-appropriate product, architecture, native-contract, story, and proof handoff through four approval gates
- **`/implement`** — Deliver validated stories sequentially, including tests, runtime proof, and audit remediation
- **`/implement_tdd`** — Same as above, but SDET writes tests first, then developer implements to make them pass
- **`/audit_epic`** — Perform a read-only evidence audit and one targeted verification after remediation
- **`/sync_product`** — Update product documentation when implementation reveals scope changes

### Reverse Engineering (Code to Docs)

- **`/re_documentation`** — Reverse engineer product and architecture documentation from an existing codebase. Two agents scan your code, interview you about decisions and rationale, then generate 24 documentation files (9 product + 15 architecture)

### Session Continuity

- **`/session-handoff`** / **`scope:session-handoff`** — Create an ephemeral `session-handoff.md` at the active worktree or project root when a long session has become inefficient. The file captures enough durable context for a fresh agent to assess the state and recommend the next course of action without treating unconfirmed next steps as instructions. The file is overwritten on each run and should not be tracked by git.

Every command has user approval gates. Nothing is merged without your sign-off.

## How It Works

SCOPE uses Claude Code's built-in features:

- **Slash commands** (`.claude/commands/`) define multi-phase workflows with approval gates
- **Agent definitions** (`.claude/agents/`) give Claude specialized personas (architect, developer, SDET, product owner, reverse-engineer-po, reverse-engineer-architect)
- **Skills** (`.claude/skills/`) provide documentation templates (Arc42+C4 for technical, Atlassian Blueprint for product)
- **TaskCreate/TaskUpdate** manage story dependencies and sequencing
- **Git worktrees** isolate implementation from the main branch

When running inside `./wip/{epic-id}`, use the `plugins/scope/` directory from that worktree checkout. Do not fall back to the main checkout.

The v3 refinement validator and v2 audit validator require Python 3 and PyYAML.
Claude reviewer automation also uses `pexpect`. Scope has no persistent service
or database.

## Installation

```bash
git clone https://github.com/PatD42/scope.git
cd scope
python3 -m pip install -r requirements.txt
```

**Install to a project** (commands available only in that project):

```bash
./install.sh /path/to/your-project
```

**Install to user directory** (commands available in all projects):

```bash
./install.sh --user
```

**Install to current directory** (default):

```bash
./install.sh
```

The script copies commands, agents, skills, and a config template into `.claude/`. For project installs, it also creates `.scope/config.yaml` — edit it to set your project name and tracking preferences.

## Quick Start

**Starting from an idea or a PRD:**

```
1. /prd_create              → Create a first-pass PRD if you do not have one
2. /prd_refine              → Refine it interactively
3. /prd_breakdown           → Get epics with dependencies
4. /epic_refine EPIC-001    → Refine the first epic (4 approval gates)
5. /implement EPIC-001      → Implement it story-by-story in a worktree
6. Review and merge the worktree when satisfied
```

**Starting from existing code:**

```
1. /re_documentation        → Reverse engineer product + architecture docs
2. /prd_refine              → Refine/extend the PRD for new features
3. /prd_breakdown           → Break into epics
4. Continue as above
```

## Project Structure (Target Project)

After installation, your project will generate this structure as you work:

```
your-project/
├── .claude/
│   ├── commands/           # Slash commands
│   ├── agents/             # Agent definitions
│   └── skills/             # Documentation templates
├── .scope/
│   └── config.yaml         # Project configuration
├── docs/
│   ├── product/            # Product docs (strategy, definition, decisions)
│   ├── architecture/       # Technical docs (Arc42 sections 01-13)
│   ├── epics/{epic-id}/    # Per-epic contract, design, plans, and evidence
│   └── releases/           # Release documentation
├── ./wip/
│   └── {epic-id}/          # Git worktree per epic (implementation happens here)
└── src/                    # Your application code
```

## Key Concepts

**Native contracts** — `/epic_refine` uses project-appropriate contracts such
as OpenAPI, JSON Schema, SQL, language interfaces, and configuration schemas.
Python Protocols are optional.

**Implementation boundaries** — Each `file-plan-story-*.yaml` records binding
contracts, touchpoints, forbidden changes, and proof obligations. Candidate
files remain advisory.

**Bounded audit** — `/audit_epic` runs one full read-only audit. Implementation
remediates findings, then audit performs one targeted verification.

**Git worktrees** — Implementation happens in `./wip/{epic-id}` on branch `epic/{epic-id}`. Main branch stays clean. You merge when satisfied.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3 with `PyYAML>=6,<7` and `pexpect>=4.9,<5`
- Git

## License

MIT
