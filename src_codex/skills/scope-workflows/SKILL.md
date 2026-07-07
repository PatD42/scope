---
name: scope-workflows
description: Run Scope-style product engineering workflows in Codex using command playbooks, role instructions, approval gates, docs, and worktrees.
---

# Scope Workflows for Codex

Use this skill when the user asks for Scope-like workflows in Codex, invokes `scope:<command>`, or asks to run a Scope command such as `prd_refine`, `epic_refine`, `implement`, `audit_epic`, `re_documentation`, or `sync_product`.

## Artifact Locations

Resolve paths from the current checkout only.

- Codex plugin root: `./plugins/scope/`

When running inside `./wip/{epic-id}`, use the `plugins/scope/` directory from that worktree checkout. Do not fall back to the main repo copy or any other checkout.
Do not read `.claude/` as a Codex command, role, governance, skill, template, or override source. `.claude/` belongs to the Claude installation only.

Within the current checkout:

- Commands: `commands/{command}.md`
- Role instructions: `agents/{role}.md`
- Governance: `governance/*.md`
- Documentation templates and tracking adapters: `skills/`
- Scope reference docs: `docs/`

If the same artifact exists in the current checkout's `plugins/scope/` directory, prefer that project copy because it may contain project-specific edits.

## Command Invocation

Treat these as equivalent user requests:

- `scope:epic_refine E1`
- `/epic_refine E1`
- `run epic_refine for E1`

Execution steps:

1. Read the matching command file.
2. Read referenced role files from `agents/`.
3. Read referenced skills from `skills/`.
4. Read governance files when the command or role requires them.
5. Execute the command as a Codex workflow, preserving approval gates.
6. Write or update project artifacts in `docs/`, `.scope/`, and `./wip/` as the command specifies.

### Nested Scope Command Execution

When a Scope command says to run another Scope command, Codex must execute the referenced command workflow from the current checkout's `plugins/scope/commands/{command}.md`.

Do not satisfy a nested command by producing similarly named artifacts, writing a local summary, or performing an informal equivalent workflow unless the referenced command file explicitly allows that substitution.

For every nested Scope command:

1. Read the referenced command file from the current checkout.
2. Execute its initialization, validation, artifact, reviewer, remediation, and output requirements as written.
3. Preserve the referenced command's proof requirements, including attempt directories, metadata files, ledgers, matrices, and status outputs.
4. Report the actual nested command evidence in the parent command result.

If the nested command cannot be executed, the parent command is not delivery-complete. Report it as blocked or incomplete with the concrete reason instead of fabricating the nested command's artifacts.

## Role Mapping

Codex should usually perform Scope roles sequentially in the main session:

- `product-owner`: validate business requirements, acceptance criteria, and product docs.
- `architect`: architecture, ADRs, specs, contracts, and implementation boundary plans.
- `developer`: implementation plus tests.
- `sdet`: test planning and test-first implementation when requested.
- `reverse-engineer-po`: code-to-product-documentation workflow.
- `reverse-engineer-architect`: code-to-architecture-documentation workflow.
- `reverse-engineer-ops`: operations/runbook reverse engineering.

Only spawn Codex sub-agents when the user explicitly asks for parallel agents or delegation. When spawned, pass the relevant Scope role file and a bounded task.

## Codex Adaptations

- Replace Claude `Read`, `Glob`, and `Grep` with local file reads and `rg`.
- Replace Claude `TaskCreate/TaskUpdate` with `.scope/` tracking files, Codex plans, or explicit checklists.
- Replace Claude `AskUserQuestion` with concise approval or clarification questions.
- Preserve approval gates. Stop at a gate and ask before continuing when the command says approval is required.
- Use git worktrees exactly as Scope specifies for implementation commands.
- For Codex, the implementation worktree root is `./wip/`.
- Keep implementation in the worktree once a command moves there.
- In a worktree, read `plugins/scope/` from that worktree only. No fallback to the main checkout.

## Context Sources

Use Obsidian MCP when available for prior decisions, lessons, and related product notes. If Obsidian MCP is unavailable, continue with local repo search and say that MCP was unavailable.

Use CodeGraph when it is present. Prefer CodeGraph MCP when available because it can provide relationship context directly to the agent. If CodeGraph MCP is unavailable or unhealthy, use the CodeGraph CLI instead.

### CodeGraph Working Directory Rule

CodeGraph is scoped to the current working directory.

- During refinement and planning, use the main repository root as the CodeGraph project path.
- During implementation and audit, after the workflow changes into `./wip/{epic-id}`, use that worktree as the CodeGraph project path.
- Do not query the main repo CodeGraph DB for implementation code that is being changed inside a worktree.
- When using the CLI fallback, ensure `./.codegraph` exists. If it does not, run `codegraph init .` followed by `codegraph index .`; `codegraph sync .` alone does not populate a brand-new index.
- Scope commands that launch audits own CodeGraph initialization, initial index, and sync before reviewers run. External reviewers are query-only and must not run `codegraph init`, `codegraph sync`, `codegraph sync-if-dirty`, or `codegraph unlock`.
- Outside external reviewer mode, before relying on CLI CodeGraph context, run `codegraph index .` after first-time initialization, otherwise run `codegraph sync-if-dirty .` or `codegraph sync .` from the active working directory.
- When CodeGraph MCP is available, use the MCP equivalent for relationship, dependency, caller/callee, or context queries before falling back to CLI commands.
- Use `codegraph status .`, `codegraph context "task description" --path .`, `codegraph query "SymbolName" --path .`, `codegraph files --path .`, and `codegraph affected --path . --stdin < changed-files.txt` for dependency, symbol, and impact context.
- After `scope:wrap_epic` merges the epic branch back to the main project root, return to the main project root and sync the root CodeGraph DB.

## Quality Bar

Follow repository instructions in `AGENTS.md` when present. Generated intelligence outputs must be read and judged as a product, not just mechanically produced files.
