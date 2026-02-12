---
name: git-workflow
description: Manage git worktrees for epic implementation isolation. Use when starting implementation (create worktree), switching contexts, or merging completed work.
---

# Git Workflow

## Phase → Directory

| Phase | Directory | Branch |
|-------|-----------|--------|
| Planning | `./` (main) | main |
| Implementation | `./wip/{epic-slug}/` | {epic-id}-impl |

## Operations

### create_worktree(epic_id, epic_title)
```bash
slug=$(echo "$epic_id-$epic_title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | cut -c1-40)
mkdir -p ./wip
git branch "${epic_id}-impl" 2>/dev/null || true
git worktree add "./wip/$slug" "${epic_id}-impl"
cp -r ".scope/$epic_id" "./wip/$slug/.scope/" 2>/dev/null || true
```

### worktree_exists(epic_id)
```bash
epic_lower=$(echo "$epic_id" | tr '[:upper:]' '[:lower:]')
find ./wip -maxdepth 1 -type d -name "${epic_lower}*" 2>/dev/null | head -1
```

### merge_worktree(epic_id, delete_after)
```bash
git checkout main
git merge "${epic_id}-impl" --no-edit
if [ "$delete_after" = "true" ]; then
  git worktree remove "./wip/${epic_slug}"
  git branch -d "${epic_id}-impl"
fi
```

### list_worktrees()
```bash
git worktree list --porcelain
```

## Prerequisites
- Must be on main with clean working tree before creating worktree
- All tests must pass before merging
