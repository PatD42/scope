# Scope Repository Instructions

This repository contains prompt, command, agent, governance, and install assets for Scope.

## Mirrored Claude/Codex Prompt Rule

Treat Claude-specific and Codex-specific prompt files as behaviorally mirrored unless there is an explicit platform reason not to.

When updating any file under `src_claude/`:

- Check whether the matching path exists under `src_codex/`.
- If it exists, update the Codex file with the same behavioral rigor.
- Preserve only necessary platform differences, such as `.claude/...` paths versus `plugins/scope/...` paths, `CLAUDE.md` versus `AGENTS.md`, or Codex plugin scaffolding.
- If the change is intentionally Claude-only, state why in the final response and in the PR/commit context.

When reviewing Codex-specific changes, perform the same check in reverse for `src_claude/`.

## Shared-First Rule

If a command, agent behavior, governance rule, script, skill, or template should apply to both Claude and Codex, prefer placing it in `src_shared/` instead of duplicating it in both platform trees.

Use platform-specific files only for real platform differences.

## Validation

Before committing prompt or workflow changes, run:

```bash
git diff --check
```

For installable Scope changes, also run an install smoke test:

```bash
tmpdir=$(mktemp -d)
./install.sh "$tmpdir"
rm -rf "$tmpdir"
```

Check that changed Claude/Codex command files install to the expected destinations:

- Claude: `.claude/commands/...`
- Codex: `plugins/scope/commands/...`
