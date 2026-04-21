# Scope for Codex

Scope for Codex adapts the Scope product engineering workflow from Claude Code to Codex.

The original Scope model uses Claude slash commands, Claude agents, Claude skills, and task tools. Codex does not load those exact primitives the same way, so this plugin keeps the Scope artifacts as command playbooks and role instructions, then adds Codex-facing guidance.

## Invocation

Ask Codex to run a Scope command by name:

```text
scope:prd_refine docs/prd.md
scope:prd_breakdown docs/prd.md
scope:epic_refine E1
scope:implement E1
scope:audit_epic E1
scope:re_documentation
scope:sync_product
```

Codex should read the matching file in `commands/`, load any referenced role file in `agents/`, and follow the workflow with approval gates.

When running inside `wip/{epic-id}`, Codex should use the `plugins/scope/` directory from that worktree checkout. Do not fall back to the main checkout's plugin copy.

## Porting Model

- `commands/` contains the original Scope command playbooks.
- `agents/` contains Scope role definitions. Codex should role-play these sequentially unless the user explicitly asks for sub-agents.
- `skills/` contains reusable documentation and tracking skills.
- `governance/` contains quality and lifecycle rules.
- `docs/` contains Scope reference documentation.

## Differences From Claude Code

- Claude slash commands are not native Codex commands. They are invoked by natural language, usually `scope:<command>`.
- Claude custom agents are not auto-registered. Codex uses the role files as instructions; when sub-agents are explicitly requested, map Scope roles to Codex `worker` or `explorer` agents.
- Claude task tools are replaced by `.scope/` tracking files and Codex task plans where practical.
- MCP servers must be configured in Codex separately. This plugin includes an empty `.mcp.json` until codegraph and Obsidian server commands are known.
