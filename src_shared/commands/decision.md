---
name: decision
description: Record architectural (ADR) or product (PDR) decisions with intent and rationale. With args, interviews the user. Without args, auto-detects decisions since last /implement or /decision.
args: "[decision description]"
skills: project-documentation
---

# /decision

Capture decisions and their rationale so they survive beyond the conversation. Works in two modes:

**With argument:** `/decision Use SQLite instead of PostgreSQL for local-first simplicity`
- Interviews you to understand the full intent and "why"
- Challenges you if the decision could create issues
- Saves only the decision and rationale (not the full conversation)

**Without argument:** `/decision`
- Auto-detects all decisions made since last `/implement` or `/decision`
- Presents candidates for discussion, refinement, and approval
- You choose which to keep, edit, or discard

---

## Mode 1: Interview (With Argument)

**Trigger:** `/decision {description}`

### Step 1: Classify

Determine whether this is an ADR or PDR using this decision tree:

```
Does this change what the user sees or can do?
  → Yes → PDR
  → No  → Does this change how the system is built or operated?
            → Yes → ADR
            → No  → Probably not worth recording
  → Both → ADR with product consequences noted in Consequences section
```

**Core test:** "Would a non-technical stakeholder care about this decision?"
- Yes → PDR (or both)
- No → ADR

| | ADR (Architecture) | PDR (Product) |
|---|---|---|
| **Answers** | _How_ do we build it? | _What_ do we build and _for whom_? |
| **Stakeholder** | Developer, architect, ops | Product owner, user, business |
| **User impact** | Invisible to user (or indirect) | Directly changes user experience |
| **Examples** | PostgreSQL vs SQLite, async vs sync, Alembic for migrations, retry strategy, caching layer | Remove export from MVP, require email verification, support Canada only, free tier limits, change onboarding flow |

**Edge cases:** Some decisions are both technical and product-facing. For example, "Use Gemini Flash instead of Pro for synthesis" is a technology choice but affects output quality the user sees. In that case, **record as ADR and note the product consequence in the Consequences section.** Don't duplicate as two entries.

| Type | Destination |
|------|-------------|
| **ADR** | `docs/epics/{epic}/adr.md` or `docs/architecture/adr/` |
| **PDR** | `docs/epics/{epic}/pdr.md` or `docs/product/decisions.md` |

If still unclear after applying the decision tree, ask: "Does this decision change what the user experiences, or how the system is built?"

### Step 2: Identify Scope

```python
# Determine which epic this belongs to (if any)
active_epics = Glob("docs/epics/*/details.md")
# Exclude _implemented/ and _deferred_superseded/
active_epics = [e for e in active_epics if "/_" not in e]

if len(active_epics) == 1:
    epic_dir = active_epics[0].split("/")[-2]
    # Confirm with user
elif len(active_epics) > 1:
    # Ask user which epic, or "system-level"
else:
    # System-level decision
```

### Step 3: Interview for Intent and "Why"

Ask the user these questions (adapt based on what the initial description already covers):

**For the intent:**
1. "What exactly are you deciding?" — Get the precise decision statement
2. "What problem does this solve?" — The context/trigger

**For the "why":**
3. "Why this approach over alternatives?" — Rationale
4. "What alternatives did you consider (even briefly)?" — At least one alternative

**Challenge if necessary:**
5. Review the decision against:
   - Existing ADRs in the epic/system — does it contradict any?
   - Architecture constraints (`docs/architecture/02-constraints.md`)
   - Known risks (`docs/architecture/11-risks.md`)

6. If you see potential issues, raise them:
   - "This contradicts ADR-{N} which decided {X}. Are you superseding it?"
   - "This could create a problem with {X} because {Y}. Are you aware?"
   - "Have you considered {alternative} which would avoid {tradeoff}?"

7. If the user confirms after your challenge, proceed. If they change their mind, re-interview.

### Step 4: Save

**Save ONLY the structured decision** — not the interview conversation.

**For ADR** — append to the appropriate adr.md:

```markdown
## ADR-{NNN}: {Title}

**Date:** {today}
**Status:** Accepted
**Scope:** {System | Backend | Frontend}
**Epic:** {epic-id or "System-level"}

### Context

{Problem statement from interview — 2-4 sentences}

### Decision

{What was decided and why — 2-4 sentences}

### Alternatives Considered

- **{Alternative 1}**: {Why rejected — 1 sentence}
- **{Alternative 2}**: {Why rejected — 1 sentence}

### Consequences

{Key tradeoffs — 2-3 bullet points}
```

**For PDR** — append to the appropriate pdr.md or decisions.md:

```markdown
## PDR-{NNN}: {Title}

**Date:** {today}
**Status:** Accepted

### Context

{Product question or tradeoff — 2-4 sentences}

### Decision

{What product direction was chosen and why — 2-4 sentences}

### Alternatives Considered

- **{Alternative 1}**: {Why rejected — 1 sentence}

### Consequences

**User Impact:** {1-2 sentences}
**Business Impact:** {1-2 sentences}
```

### Step 5: ADR/PDR Numbering

**Epic-level**: Read existing ADR/PDR entries in the file, find highest number, increment.

**System-level**:
- ADR: Read `docs/architecture/09-adr-summary.md` for highest number. Also scan epic `adr.md` files for inline ADRs. Use next global number.
- PDR: Read `docs/product/decisions.md` for highest number.

### Step 6: Cross-Post (if available)

```python
# If Obsidian MCP is available, cross-post
if mcp_available("obsidian"):
    # Create or append to relevant note in vault
    obsidian.write(f"decisions/{decision_type}-{number}-{slug}.md", content)
```

### Step 7: Confirm

Tell the user:
```
Saved {ADR|PDR}-{NNN}: {Title}
  Location: {file path}
  Epic: {epic-id or "System-level"}
  Type: {Architecture | Product}
```

---

## Mode 2: Auto-Detect (Without Argument)

**Trigger:** `/decision` (no args)

### Step 1: Determine Time Window

```python
# Find the last /decision, /implement, or /wrap_epic marker
decision_markers = Glob(".scope/tracking/commands/decision-*.jsonl")
implement_markers = Glob(".scope/tracking/commands/implement-*.jsonl")
wrap_markers = Glob(".scope/tracking/commands/wrap_epic-*.jsonl")

# Use the most recent marker as the "since" timestamp
all_markers = sorted(decision_markers + implement_markers + wrap_markers)

if all_markers:
    last_marker = Read(all_markers[-1])
    since_date = json.loads(last_marker)["completed_at"]
else:
    # NO MARKERS EXIST — scan the entire epic context
    # This happens on first run, after compaction, or in fresh sessions
    # Fall back to: beginning of the active epic, or last 30 days, whichever is shorter
    epic_first_commit = Bash("git log --reverse --oneline -- docs/epics/{EPIC_DIR}/ | head -1")
    if epic_first_commit:
        since_date = Bash(f"git log --format='%aI' {epic_first_commit.split()[0]}")
    else:
        since_date = "30 days ago"
    print(f"No tracking markers found. Scanning full epic history since {since_date}.")
```

**Important:** Already-recorded decisions (those already in `adr.md` / `pdr.md` / `decisions.md`) must be filtered out. Read existing decision files and exclude any candidates that match existing entries by title or content.

### Step 2: Scan for Decision Candidates

Analyze the following sources for decisions made in the time window:

**Source 1: Git history**
```bash
# Commits since last marker
git log --oneline --since="{since_date}"

# File changes (what was modified)
git diff --stat HEAD~{N}..HEAD
```

Look for signals in commit messages and diffs:
- New dependencies added (package.json, requirements.txt, pyproject.toml)
- New configuration entries (config/*.yaml)
- Schema changes (migrations, new tables/columns)
- New patterns introduced (new base classes, utilities, middleware)
- Infrastructure changes (Dockerfile, CI/CD, IaC)

**Source 2: Agent summaries**
```python
# Check agent summaries for architectural choices
summaries = Glob(".scope/*/agent_summaries.jsonl")
# Look for "developer_discovered_files", "concerns", "decisions" fields
```

**Source 3: Code patterns**
```python
# Scan for technology introductions
new_imports = Grep("^import |^from ", glob="*.py", recent_only=True)
new_packages = Grep("new dependency", glob="requirements*.txt")

# Scan for ADR-worthy patterns
# New base classes, protocols, abstract classes
# New config sections
# New error types
# New API endpoints
```

**Source 4: Existing docs gap**
```python
# Compare what's documented vs. what's in code
existing_adrs = Read("docs/epics/{active-epic}/adr.md")
# Are there technologies/patterns in code not covered by ADRs?
```

### Step 3: Classify and Present Candidates

For each candidate, apply the classification heuristic:
- "Does this change what the user sees or can do?" → PDR
- "Does this change how the system is built or operated?" → ADR
- Both → ADR with product consequences noted

Present discovered decisions to the user as a numbered list:

```
Decisions detected since {date}:

  1. [ADR] Added Redis for session caching
     Signal: redis added to requirements.txt, new RedisStore class
     Why (inferred): Performance — avoid DB round-trips for sessions

  2. [ADR] Switched from sync to async HTTP client
     Signal: httpx replaced requests in 4 files
     Why (inferred): Non-blocking I/O for concurrent API calls

  3. [PDR] Removed user export feature from MVP scope
     Signal: export/ directory deleted, AC updated
     Why (inferred): Scope reduction for timeline

  4. [ADR] Used Alembic for migrations (instead of raw SQL)
     Signal: alembic/ directory created, alembic.ini added
     Why (inferred): Repeatable migrations across environments

  5. [ADR+Product] Switched from Gemini Pro to Flash for synthesis
     Signal: model config changed, cost-per-entity dropped
     Why (inferred): Cost reduction — but may affect output quality
     Note: Recording as ADR with product consequences

Actions for each:
  [keep] — Record as-is (or edit the "why")
  [edit] — Discuss and refine before recording
  [skip] — Not a decision worth recording
  [add]  — I missed a decision, let me add it
```

### Step 4: Interview Each Kept Decision

For each decision the user keeps or wants to edit:
- Confirm or refine the "why"
- Challenge if necessary (same as Mode 1, Step 3)
- If user edits, update the description

For `[add]`, switch to Mode 1 interview for that decision.

### Step 5: Save All Approved Decisions

Save each approved decision using the same format as Mode 1, Step 4.

### Step 6: Write Tracking Marker

```bash
# Record that /decision was run (for next auto-detect window)
mkdir -p .scope/tracking/commands
echo '{"command":"decision","completed_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","decisions_recorded":{N}}' >> ".scope/tracking/commands/decision-$(date +%Y%m%d-%H%M%S).jsonl"
```

### Step 7: Summary

```
Recorded {N} decisions:
  - ADR-{NNN}: {Title} → {file}
  - PDR-{NNN}: {Title} → {file}
  - ...

Skipped {M} candidates.
```

---

## Key Principles

1. **Capture intent and "why" only** — not the deliberation process, not the conversation
2. **Challenge the user** — if a decision contradicts existing ADRs, introduces risk, or has a better alternative, say so
3. **Lightweight** — this should take 2-5 minutes per decision, not 30 minutes
4. **Auto-detect is best-effort** — it's OK to miss some; the user can always add manually
5. **Numbering is global** — ADRs share a single sequence across system/backend/frontend/epic scopes
