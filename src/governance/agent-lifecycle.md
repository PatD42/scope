# Agent Lifecycle (Shared Protocol)

All agents follow this lifecycle. READ this file — do not duplicate its contents in your agent definition.

---

## On Startup: Find Your Task

```python
# 1. Set tab title
TITLE_SCRIPT_DIR = Bash: find ./.claude/commands/scripts ~/.claude/commands/scripts -name "tab_title.sh" -exec dirname {} \; 2>/dev/null | head -1
Bash: $TITLE_SCRIPT_DIR/tab_title.sh "🟢 {agent_name}"

# 2. Find your task
# NOTE: Filter by your agent name. Architect must ALSO exclude "reviewer"
#       from matches to avoid claiming architect-reviewer tasks.
tasks = TaskList()
my_task = None
for task in tasks:
    if "{agent_name}" in task.subject and task.status == "pending" and not task.blockedBy:
        # Architect-specific: skip if "reviewer" in subject
        if "{agent_name}" == "architect" and "reviewer" in task.subject:
            continue
        my_task = task
        break

if not my_task:
    Output: "[WAIT] {agent_name} - No task found. Entering polling loop..."
    Bash: sleep 15
    # Go to Polling Mode below

# 3. Claim the task
TaskUpdate(taskId=my_task.id, status="in_progress", owner="{agent_name}")
Bash: $TITLE_SCRIPT_DIR/tab_title.sh "⚠️ {agent_name} - {task_id}"

# 4. Get full task details and parse context
task_details = TaskGet(taskId=my_task.id)
context = parse_yaml(task_details.description)
```

---

## On Completion: Write Summary, Then Mark Done

**Order matters: summary FIRST, mark complete LAST.**

```python
# 1. Get session ID
session_id = get_session_id()  # Use session-id-finder skill

# 2. Build result following agent-summary schema
result = {
    "agent": "{agent_name}",
    "task_id": my_task.id,
    "session_id": session_id,
    "completed_at": datetime.utcnow().isoformat() + "Z",
    "status": "success",  # or "failure" or "user_input"
    "phase": phase,
    "deliverables": {...},
    "handoff": {...},
    "error": None
}

# 3. Append to agent_summaries file FIRST
with open(agent_summaries, "a") as f:
    f.write(json.dumps(result) + "\n")

# 4. Mark task complete LAST
TaskUpdate(taskId=my_task.id, status="completed")
```

---

## Polling Mode

After completing a task, immediately check for more. Only exit when no work remains.

```python
while True:
    tasks = TaskList()
    my_task = None
    for t in tasks:
        if "{agent_name}" in t.subject and t.status == "pending" and not t.blockedBy:
            # Architect-specific: skip architect-reviewer tasks
            if "{agent_name}" == "architect" and "reviewer" in t.subject:
                continue
            my_task = t
            break

    if my_task:
        TaskUpdate(taskId=my_task.id, status="in_progress", owner="{agent_name}")
        execute_phase(...)
        write_agent_summary(...)
        TaskUpdate(taskId=my_task.id, status="completed")
        Output: "[CONTINUE] Task done. Checking for more..."
        # DO NOT BREAK — loop continues
    else:
        pending = [t for t in tasks if t.status == "pending"]
        in_progress = [t for t in tasks if t.status == "in_progress"]
        if not pending and not in_progress:
            Output: "[EXIT] {agent_name} - No tasks remain. Exiting."
            break
        else:
            Output: f"[WAIT] {agent_name} - {len(pending)} pending. Polling..."
            Bash: sleep 15  # ACTUAL Bash command
```

**Rules:**
- Use `Bash: sleep 15` — the actual command, not pseudocode
- Never output explanations or summaries during polling — just `[WAIT]` markers
- Never exit while tasks remain pending or in_progress

---

## Approval Handling

If `approval_required` is set in the task context:

```python
if approval_required:
    while True:
        response = AskUserQuestion(questions=[{
            "question": f"Approve {phase} for {epic_id}?",
            "options": [
                {"label": "Approve", "description": "Work is complete"},
                {"label": "Feedback", "description": "Changes needed"}
            ]
        }])
        if response == "Approve":
            break
        else:
            # Address user's feedback, make changes, then loop back to ask again
            # Do NOT mark complete until explicitly approved
            continue
```

## Terminate Upon Completion

If `terminate_upon_completion: yes` in task context, skip polling mode after completing the task — exit immediately after writing agent summary. If `no` (default), enter polling mode to pick up additional tasks.

---

## Compaction Recovery

If your context has been summarized, re-read these from disk before continuing:

1. **Your task**: `TaskList()` / `TaskGet(taskId)`
2. **Agent summaries**: `.scope/{epic-id}/agent_summaries.jsonl`
3. **Epic context**: `docs/epics/{epic-dir}/` (architecture, AC, ADRs, file plans)
4. **Governance files**: `.claude/governance/` (your checklist, production rules)
5. **Lessons learned**: `docs/lessons-learned/INDEX.md`

Do NOT rely on what you "remember." Read the files.
