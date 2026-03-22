---
name: re_ops
description: Reverse engineer infrastructure and operations documentation from an existing codebase using code scanning and structured interviews
skills: project-documentation
---

# /re_ops

Reverse engineer complete operations documentation from an existing codebase. Uses a specialized operations agent that scans infrastructure config, deployment pipelines, and IaC autonomously, then interviews you to fill gaps with actual procedures and tribal knowledge.

**Output:**
- Operations overview and environments (2 files)
- Runbooks (8 files) — deployment, secrets, identity, networking, database, monitoring, scaling, DR
- Troubleshooting (2 files) — common issues, escalation matrix
- Maintenance (2 files) — scheduled tasks, upgrade procedures

---

## Overview

```
Phase 1: Code Exploration (Autonomous)
  Scan Dockerfiles, CI/CD, IaC, config, scripts

Phase 2: Structured Interview
  Fill gaps with actual procedures, commands, contacts

Phase 3: Document Generation
  Create runbooks and operational docs

Phase 4: Review & Refinement
  Validate procedures, iterate until approved
```

Each phase has 4 steps:
1. **Infrastructure Scan** — Agent scans the codebase for deployment, infra, and ops artifacts (you wait)
2. **Operational Interview** — Agent asks you targeted questions about procedures (~60-90 min)
3. **Document Generation** — Agent creates documentation files (you wait)
4. **Review & Refinement** — You review procedures, provide feedback, approve

---

## Execution

### Step 0: Validate Prerequisites

```python
# Check that operations templates are available
templates_ops = Glob("**/skills/project-documentation/templates-operations/**/*.md")

if not templates_ops:
    print("ERROR: operations templates not found in project-documentation skill.")
    print("Run install.sh to install SCOPE to this project.")
    exit(1)

# Check for existing architecture docs (useful context for ops docs)
existing_arch = Glob("docs/architecture/**/*.md")
if existing_arch:
    print(f"Found {len(existing_arch)} architecture doc(s) — will use as context.")

# Check for existing operations docs — detect gaps
existing_overview = Glob("docs/operations/overview.md")
existing_envs = Glob("docs/operations/environments.md")
existing_runbooks = Glob("docs/operations/runbooks/*.md")
existing_troubleshooting = Glob("docs/operations/troubleshooting/*.md")
existing_maintenance = Glob("docs/operations/maintenance/*.md")

has_overview = len(existing_overview) >= 1
has_envs = len(existing_envs) >= 1
has_runbooks = len(existing_runbooks) >= 5
has_troubleshooting = len(existing_troubleshooting) >= 1
has_maintenance = len(existing_maintenance) >= 1

# Determine what needs to be done
if has_overview and has_envs and has_runbooks and has_troubleshooting and has_maintenance:
    print("All operations documentation already exists. Nothing to do.")
    print("Update individual runbooks as procedures change.")
    exit(0)

# Report what exists and what's missing
print("Operations documentation gap analysis:")
print(f"  Overview:          {'COMPLETE' if has_overview else 'MISSING'}")
print(f"  Environments:      {'COMPLETE' if has_envs else 'MISSING'}")
print(f"  Runbooks:          {'COMPLETE' if has_runbooks else 'MISSING'} ({len(existing_runbooks)} files)")
print(f"  Troubleshooting:   {'COMPLETE' if has_troubleshooting else 'MISSING'} ({len(existing_troubleshooting)} files)")
print(f"  Maintenance:       {'COMPLETE' if has_maintenance else 'MISSING'} ({len(existing_maintenance)} files)")
print("")

if existing_runbooks or existing_overview:
    print("Options:")
    print("  1. Create only missing documentation (recommended)")
    print("  2. Overwrite all documentation")
    print("  3. Cancel")
    # Wait for user choice — default is option 1
```

### Step 1: Create Output Directories

```bash
mkdir -p docs/operations/runbooks
mkdir -p docs/operations/troubleshooting
mkdir -p docs/operations/maintenance
```

---

## Operations Documentation

**Agent**: `reverse-engineer-ops`
**Duration**: ~1.5-2 hours (60-90 min interview)

### Launch Operations Agent

Tell the user:

```
Starting: Operations Documentation

I'll work as the Operations agent to reverse engineer your infrastructure
and operations documentation. This has 4 steps:

  1. Infrastructure Scan — I'll scan your codebase for deployment, infra,
     and ops artifacts (you wait, ~15-20 min)
  2. Operational Interview — I'll ask you about procedures, contacts,
     and tribal knowledge (~60-90 min)
  3. Document Generation — I'll create the runbooks and docs (you wait, ~10-15 min)
  4. Review — You review procedures and approve

Starting infrastructure scan now...
```

### Execute Operations Agent Process

Follow the full process defined in the `reverse-engineer-ops` agent:

1. **Phase 1 (Autonomous)**: Infrastructure discovery, environment/config, deployment pipeline, database/storage, identity/auth, networking/security, monitoring, operational scripts
2. **Phase 2 (Interview)**: 10 sections — Environments & Access, Deployment, Secrets, Identity, Networking, Database, Monitoring & Incidents, Scaling, DR & Maintenance, Known Issues
3. **Phase 3 (Generate)**: Create 14 operations documentation files
4. **Phase 4 (Review)**: Present to user, iterate until approved

**Important**: If architecture documentation exists (especially `07-deployment.md`, `08-cross-cutting/operations.md`, `08-cross-cutting/security.md`, `backend/`), read it as context — it provides architectural decisions and patterns that inform operational procedures.

### Operations Documentation Output

```
docs/operations/
├── overview.md
├── environments.md
├── runbooks/
│   ├── deployment.md
│   ├── secrets-management.md
│   ├── identity-access.md
│   ├── networking-security.md
│   ├── database.md
│   ├── monitoring-alerting.md
│   ├── scaling.md
│   └── disaster-recovery.md
├── troubleshooting/
│   ├── common-issues.md
│   └── escalation.md
└── maintenance/
    ├── scheduled.md
    └── upgrade-procedures.md
```

### Approval Gate

```
Operations Documentation Complete

Created 14 files in docs/operations/:
  - Overview & Environments:  2 files
  - Runbooks:                 8 files
  - Troubleshooting:          2 files
  - Maintenance:              2 files

Please review the runbooks and procedures.
  - Are the commands and URLs correct?
  - Are there procedures missing?
  - Is the escalation matrix accurate?
  - Would a new team member be able to follow these?

[approve / revise]
```

---

## Completion

```
Operations Documentation Complete

Overview & Environments:  2 files in docs/operations/
Runbooks:                 8 files in docs/operations/runbooks/
Troubleshooting:          2 files in docs/operations/troubleshooting/
Maintenance:              2 files in docs/operations/maintenance/

Total: 14 operations documentation files generated from code analysis + interview.

Next steps:
  - Update runbooks as procedures change
  - Schedule quarterly review of ops docs
  - Test runbooks with a new team member for clarity
  - Run DR test procedures at least semi-annually
```

---

## Tips for Effective Interview

**For Operations Questions:**
- Give actual commands, not just descriptions — "we run `gcloud run deploy...`" not "we deploy to Cloud Run"
- Be honest about gaps — undocumented procedures are the most valuable to capture
- Share tribal knowledge — the gotchas only you know about
- Include real URLs, project IDs, bucket names — these docs are for practitioners
- Mention what has gone wrong before — past incidents inform better runbooks

---

## Running Partial Documentation

You can run only specific sections:

- "Only create runbooks" — skips overview/environments/troubleshooting/maintenance
- "Only create deployment runbook" — creates a single runbook
- "Only create troubleshooting docs" — creates common-issues and escalation only

**Gap-aware execution**: The command automatically detects existing operations documentation and recommends creating only what's missing.

---

## Compaction Survival

If the conversation is compacted mid-execution, the agent must preserve:
- Current phase and section within the phase
- Files already generated
- Interview answers collected so far
- Pending approval gates
- Infrastructure inventory discovered in Phase 1
