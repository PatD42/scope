## L-001: Subagent launch prompts drop critical instructions

**Date:** 2026-03-31
**Epic:** General (affects all /implement runs)
**Domain:** agent orchestration, /implement
**Severity:** Critical

### Pattern / Anti-Pattern

**Type:** Anti-Pattern (avoid this)

**Detection:** When /implement (or any command) spawns a subagent using the Agent/Task tool, check whether the launch prompt includes ALL critical constraints from the command's skill file — especially checklists, governance rules, and quality gates. If the launch prompt is shorter than 10 lines and the skill file has mandatory checklists, instructions are being dropped.

**Rule:** Never summarize governance rules in subagent launch prompts. Reference a file on disk that the subagent must READ — the file survives compaction and cannot be accidentally summarized away.

### Root Cause

The /implement command embeds a 10-item pre-completion checklist in the developer task description. However, the agent launch prompt (the actual text passed to the Agent/Task tool) was only 7 lines — a condensed "process tasks sequentially" instruction that omitted the checklist entirely. The subagent followed its launch prompt, not the task description. Result: 43 unit tests with mocks, zero live smoke tests, despite the checklist explicitly requiring them.

The root cause is architectural: critical instructions embedded in long skill files (~600 lines) get summarized when Claude writes a subagent prompt. The subagent never sees the original skill file — it only sees what the orchestrator tells it.

### Resolution

1. Extract critical checklists to standalone governance files on disk (e.g., `.claude/governance/developer-checklist.md`)
2. In the subagent launch prompt, include an explicit step: "READ .claude/governance/developer-checklist.md before marking any task complete"
3. In the governance file, include "Do NOT rely on memory — READ THE FILE from disk every time"
4. The file reference is short enough to survive any summarization — it's one line, not 10 items
