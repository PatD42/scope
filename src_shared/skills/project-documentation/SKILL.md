---
name: project-documentation
description: Project documentation structure and templates for product, architecture, epic and releases.
---

# Project Documentation

Local markdown files. The architecture documentation follows Arc42 methodology. The product documentation follows Atlassian Product Documentation Blueprints. The provided templates will complement your internal knowledge

---

## Configuration

```yaml
# .scope/config.yaml
documentation:
  root: ./docs
```

---

## Documentation folders and templates

### Templates

Templates are located in skills/project-documentation/ (try in ./.claude, and use ~/.claude as fallback):
- **Product:** `templates-product-atlassian/`
- **Technical:** `templates-technical-arc42-c4/`
- **Operations:** `templates-operations/`

Template names match the documentation structure below.

### Folder structure

Make sure the content is in the right folder.

```
docs/
├── product/
│   ├── overview.md
│   ├── strategy.md
│   ├── definition.md
│   ├── reference/
│   │   ├── feature-catalog.md
│   │   ├── use-case.md
│   │   ├── terminology.md
│   │   ├── ux-workflows.md
│   │   ├── terminology-data-model.md
│   │   └── apis-integrations.md 
│   └── decisions.md
├── architecture/
│   ├── 01-intro.md              # System-level (arc42)
│   ├── 02-constraints.md
│   ├── 03-context.md
│   ├── 04-strategy.md
│   ├── 05-building-blocks.md
│   ├── 06-runtime.md
│   ├── 07-deployment.md
│   ├── 08-cross-cutting/
│   │   ├── domain.md
│   │   ├── security.md
│   │   ├── operations.md
│   │   └── testing.md
│   ├── 09-adr-summary.md        # Roll-up of all ADRs (all scopes)
│   ├── 10-quality.md
│   ├── 11-risks.md
│   ├── 12-glossary.md
│   ├── adr/                      # System-level ADRs
│   │   └── adr-template.md       # Shared template (all scopes)
│   ├── backend/                  # Backend component architecture
│   │   ├── overview.md
│   │   ├── services.md
│   │   ├── data.md
│   │   ├── adr/                  # Backend-specific ADRs
│   │   └── specs/                # Backend specs (detailed designs)
│   └── frontend/                 # Frontend component architecture
│       ├── overview.md
│       ├── structure.md
│       ├── patterns.md
│       ├── adr/                  # Frontend-specific ADRs
│       └── specs/                # Frontend specs (detailed designs)
├── epics/{epic-id-with-filesafe-title}/
│   ├── details.md
│   ├── system-context.md
│   ├── acceptance-criteria.md
│   ├── acceptance-traceability.yaml
│   ├── test-strategy.md
│   ├── architecture.md
│   ├── adr.md
│   ├── pdr.md
│   ├── file-plan.yaml
│   └── implementation-summary.md
├── operations/
│   ├── overview.md                # System inventory, access points, contacts
│   ├── environments.md            # Environment matrix, infra details, access
│   ├── runbooks/
│   │   ├── deployment.md          # Build, deploy, rollback procedures
│   │   ├── secrets-management.md  # Key rotation, vault access, provisioning
│   │   ├── identity-access.md     # User provisioning, roles, SSO, auditing
│   │   ├── networking-security.md # WAF, firewall, TLS certs, DNS
│   │   ├── database.md            # Backup, restore, migration, scaling
│   │   ├── monitoring-alerting.md # Dashboards, alerts, on-call response
│   │   ├── scaling.md             # Horizontal/vertical scaling, auto-scaling
│   │   └── disaster-recovery.md   # DR plan, RTO/RPO, failover
│   ├── troubleshooting/
│   │   ├── common-issues.md       # Known issues and resolutions
│   │   └── escalation.md          # Escalation matrix, contacts, SLAs
│   └── maintenance/
│       ├── scheduled.md           # Regular maintenance tasks and schedules
│       └── upgrade-procedures.md  # OS, runtime, platform upgrade playbooks
├── lessons-learned/
│   ├── INDEX.md                   # One-liner per lesson, loaded on startup
│   └── {date}-{slug}.md           # Individual lessons (pattern/anti-pattern + RCA)
└── releases/{VERSION}/
    ├── record.md
    ├── notes.md
    └── postmortem.md
```

---

## Operations

### read(path)
```python
read(f"{root}/{path}")
```

### write(path, content, frontmatter=None)
```python
if frontmatter:
    content = f"---\n{yaml.dump(frontmatter)}\n---\n\n{content}"
write(f"{root}/{path}", content)
```

### search(pattern, path=None)
```python
grep(pattern, f"{root}/{path or ''}", recursive=True)
```

### list(path)
```python
glob(f"{root}/{path}/**/*.md")
```

---

## Product Documentation

### prd.md
**Template:** `templates-product-atlassian/prd.md`
**Content:** Starting Product Requirements Document with purpose, project posture, vision, users, problem, outcomes, scope, key features, workflows, product rules, acceptance criteria, constraints, success metrics, risks, launch plan, non-goals, and readiness checklist
**Owner:** Product Owner
**Readers:** Product Owner, Architect, SDET
**Trigger:** Before PRD refinement or when starting a new product from raw intent

### strategy.md
**Template:** `templates-product-atlassian/strategy.md`
**Content:** Vision, target markets, customer problems, scope boundaries, competitive landscape
**Owner:** Product Owner
**Readers:** Product Owner, Architect
**Trigger:** Quarterly, strategic shift

### definition.md
**Template:** `templates-product-atlassian/definition.md`
**Content:** Use cases (actor, goal, flow), capability map by theme
**Owner:** Product Owner
**Readers:** Product Owner, Architect, SDET
**Trigger:** Capabilities change

### reference/features.md
**Template:** `templates-product-atlassian/reference/features.md`
**Content:** Feature catalog with status, priority, release
**Owner:** Product Owner
**Readers:** All
**Trigger:** Features added/changed

### reference/terminology.md
**Template:** `templates-product-atlassian/reference/terminology.md`
**Content:** Terms, key entities, relationships, data lifecycle
**Owner:** Product Owner
**Readers:** Architect, SDET, Developer
**Trigger:** Data model changes

### reference/ui-workflows.md
**Template:** `templates-product-atlassian/reference/ux-workflows.md`
**Content:** Navigation, key screens, workflows
**Owner:** Product Owner
**Readers:** Architect, SDET
**Trigger:** UI changes

### reference/apis.md
**Template:** `templates-product-atlassian/reference/apis.md`
**Content:** External integrations, direction, data exchanged
**Owner:** Product Owner
**Readers:** Architect, Developer
**Trigger:** Integrations added

### decisions.md (PDR)
**Template:** `templates-product-atlassian/decisions.md`
**Format:** PDR-NNN with date, status, epic, context, decision, alternatives, consequences
**Owner:** Product Owner
**Trigger:** Per epic (Epic Housekeeping aggregates)

---

## Technical Documentation (Arc42)

### 01-intro.md
**Template:** `templates-technical-arc42-c4/architecture/01-intro.md`
**Content:** Purpose, stakeholders, top 3-5 quality goals
**Owner:** Architect

### 02-constraints.md
**Template:** `templates-technical-arc42-c4/architecture/02-constraints.md`
**Content:** Technical, organizational, conventions
**Owner:** Architect

### 03-context.md
**Template:** `templates-technical-arc42-c4/architecture/03-context.md`
**Content:** C4 L1 diagram, external interfaces, business/technical context
**Owner:** Architect | **Contributors:** DevOps

### 04-strategy.md
**Template:** `templates-technical-arc42-c4/architecture/04-strategy.md`
**Content:** High-level approach, patterns, technology decisions with rationale
**Owner:** Architect

### 05-building-blocks.md
**Template:** `templates-technical-arc42-c4/architecture/05-building-blocks.md`
**Content:** C4 L2/L3 diagrams, component responsibilities, interfaces
**Owner:** Architect

### 06-runtime.md
**Template:** `templates-technical-arc42-c4/architecture/06-runtime.md`
**Content:** Key scenarios, sequence diagrams, interaction flows
**Owner:** Architect | **Readers:** SDET (heavily)

### 07-deployment.md
**Template:** `templates-technical-arc42-c4/architecture/07-deployment.md`
**Content:** Infrastructure, deployment diagrams, strategies
**Owner:** Architect | **Contributors:** DevOps

### 08-cross-cutting/domain.md
**Template:** `templates-technical-arc42-c4/architecture/08-cross-cutting/domain.md`
**Content:** Domain entities, API conventions, transaction management
**Owner:** Architect | **Readers:** Developer (frequently)

### 08-cross-cutting/security.md
**Template:** `templates-technical-arc42-c4/architecture/08-cross-cutting/security.md`
**Content:** Auth, authz, data protection, compliance
**Owner:** Architect | **Contributors:** Security Reviewer

### 08-cross-cutting/operations.md
**Template:** `templates-technical-arc42-c4/architecture/08-cross-cutting/operations.md`
**Content:** Error handling, logging, caching, configuration
**Owner:** Architect | **Contributors:** DevOps

### 08-cross-cutting/testing.md
**Template:** `templates-technical-arc42-c4/architecture/08-cross-cutting/testing.md`
**Content:** Test levels, coverage targets, test data management
**Owner:** Architect | **Readers:** SDET, Developer

### 09-adr-summary.md
**Template:** `templates-technical-arc42-c4/architecture/09-adr-summary.md`
**Format:** ADR-NNN with date, epic, decision, context, consequences
**Owner:** Architect | **Trigger:** Per epic (Epic Housekeeping)

### 10-quality.md
**Template:** `templates-technical-arc42-c4/architecture/10-quality.md`
**Content:** Performance, scalability, availability, security, maintainability requirements
**Owner:** Architect | **Readers:** SDET, Developer

### 11-risks.md
**Template:** `templates-technical-arc42-c4/architecture/11-risks.md`
**Content:** Known risks, technical debt, mitigation strategies
**Owner:** Architect | **Contributors:** Developer, Security Reviewer

### 12-glossary.md
**Template:** `templates-technical-arc42-c4/architecture/12-glossary.md`
**Content:** Architecture terms, acronyms, patterns
**Owner:** Architect | **Readers:** All

---

## Architecture Decision Records (ADRs)

ADRs are scoped by component to keep decisions close to the code they affect.

### Scoping Rules

| Scope | Directory | When to Use | Prefix |
|-------|-----------|-------------|--------|
| **System** | `architecture/adr/` | Cross-cutting decisions (auth provider, deployment model, inter-service communication) | ADR- |
| **Backend** | `architecture/backend/adr/` | Backend-specific (database schema, queue strategy, LLM pipeline, Python patterns) | ADR- |
| **Frontend** | `architecture/frontend/adr/` | Frontend-specific (component library, state management, routing, testing framework) | ADR- |

**If in doubt:** Ask "does this decision affect only one component, or does it cross the boundary?" System-level if it crosses.

### Numbering — Single Global Sequence

**All ADRs share one global sequence** regardless of scope. This guarantees uniqueness and makes chronological ordering clear.

**Before creating a new ADR:**
1. Scan `09-adr-summary.md` for the highest existing ADR number
2. Also check epic-level `adr.md` files for inline ADRs (e.g., ADR-024 through ADR-036 exist in epic docs)
3. Assign the next number in sequence

**File naming:** `ADR-{NNN}-{kebab-title}.md` in the scope's `adr/` directory.

**Example:** If the highest existing ADR is ADR-036, the next ADR is ADR-037 regardless of whether it's system, backend, or frontend scope.

### ADR Template
**Template:** `templates-technical-arc42-c4/architecture/adr/adr-template.md`
**Format:** ADR-NNN with date, status, scope, epic, context, decision, alternatives, consequences
**Owner:** Architect
**Trigger:** Any significant technical decision during epic work

### 09-adr-summary.md (Roll-Up)
The existing `09-adr-summary.md` aggregates ADRs from **all scopes** with links to the source files. Epic Housekeeping updates this file after each epic.

**Format:**
```
## System ADRs
- [ADR-001: Logging](adr/ADR-001-logging.md) — Accepted, 2026-02-08

## Backend ADRs
- [ADR-037: Queue Strategy](backend/adr/ADR-037-queue-strategy.md) — Accepted, 2026-02-16

## Frontend ADRs
- [ADR-038: Component Library](frontend/adr/ADR-038-component-library.md) — Accepted, 2026-02-19
```

---

## Component Architecture — Backend

### backend/overview.md
**Template:** `templates-technical-arc42-c4/architecture/backend/overview.md`
**Content:** Service landscape, communication patterns, shared infrastructure, constraints
**Owner:** Architect
**Readers:** Developer, SDET
**Trigger:** Service added or architectural pattern changes

### backend/services.md
**Template:** `templates-technical-arc42-c4/architecture/backend/services.md`
**Content:** Detailed service catalog (responsibilities, interfaces, dependencies, config)
**Owner:** Architect
**Readers:** Developer, SDET
**Trigger:** Service added, interfaces change

### backend/data.md
**Template:** `templates-technical-arc42-c4/architecture/backend/data.md`
**Content:** Database schemas, S3 storage layout, data flows, migration strategy
**Owner:** Architect
**Readers:** Developer, SDET
**Trigger:** Schema changes, new storage patterns

---

## Component Architecture — Frontend

### frontend/overview.md
**Template:** `templates-technical-arc42-c4/architecture/frontend/overview.md`
**Content:** Tech stack, layout, design principles, auth flow, API communication
**Owner:** Architect
**Readers:** Developer (frontend), SDET
**Trigger:** Tech stack or architectural pattern changes

### frontend/structure.md
**Template:** `templates-technical-arc42-c4/architecture/frontend/structure.md`
**Content:** Directory layout, component hierarchy, route map, key components
**Owner:** Architect
**Readers:** Developer (frontend), SDET
**Trigger:** New pages, major component restructuring

### frontend/patterns.md
**Template:** `templates-technical-arc42-c4/architecture/frontend/patterns.md`
**Content:** Data fetching, state management, error handling, styling, testing, a11y conventions
**Owner:** Architect
**Readers:** Developer (frontend), SDET
**Trigger:** New patterns established, conventions change

---

## Epic Documentation

### Epic Required Files
Every epic folder must contain these required artifacts:
- `details.md`
- `acceptance-criteria.md`
- `acceptance-traceability.yaml`
- `system-context.md`
- `architecture.md`
- `adr.md`
- `pdr.md`
- `test-strategy.md`

During refinement, the epic folder must also contain one or more `file-plan-story-*.yaml` files before the epic can be marked ready-for-implementation.

### Epic Folder Hygiene
- Epic folders may contain only markdown and YAML files.
- Do not place source code, generated code, cache directories, binaries, or OS artifacts in `docs/epics/...`.
- `contracts.py` and any other implementation source files belong in the source package, not in epic docs.

### details.md
**Template:** `templates-technical-arc42-c4/epic/details.md`
**Content:** Intent, requirements, acceptance criteria, test scenarios, components, risks
**Frontmatter:** epic_id, title, status
**Owners:** Product Owner, Architect
**Readers:** SDET, Developer (rarely - use stories)

### system-context.md
**Template:** `templates-technical-arc42-c4/epic/system-context.md`
**Content:** Technical analysis, risks, constraints, initial architectural thoughts
**Owner:** Architect
**Readers:** Product Owner, SDET
**Trigger:** Before acceptance criteria definition

### acceptance-criteria.md
**Template:** `templates-technical-arc42-c4/epic/acceptance-criteria.md`
**Content:** Testable acceptance criteria in Given/When/Then format, edge cases
**Owner:** Product Owner
**Readers:** Architect, SDET
**Trigger:** After system context analysis, before test strategy

### acceptance-traceability.yaml
**Template:** `templates-technical-arc42-c4/epic/acceptance-traceability.yaml`
**Content:** Machine-readable matrix mapping acceptance criteria and story behaviors to expected implementation files, expected test files, required assertions, runtime evidence, status, and audit notes
**Owner:** Architect during refinement, Developer during implementation, Auditor during audit
**Readers:** Developer, Auditor, Epic Housekeeping
**Trigger:** Created during epic refinement with file plans; updated during implementation and audit

### test-strategy.md
**Template:** `templates-technical-arc42-c4/epic/test-strategy.md`
**Content:** Test approach, test levels, mocking strategy, test data requirements
**Owner:** Architect
**Readers:** SDET, Developer
**Trigger:** After acceptance criteria, before architecture design

### architecture.md
**Template:** `templates-technical-arc42-c4/epic/architecture.md`
**Content:** Affected building blocks, runtime scenarios, C4 diagrams, integration points
**Owner:** Architect
**Readers:** SDET, Developer

### adr.md
**Template:** `templates-technical-arc42-c4/epic/adr.md`
**Format:** ADR-NNN with date, status, scope, epic, context, decision, alternatives, consequences
**Owner:** Architect
**Readers:** Developer (when unclear), Epic Housekeeping

### pdr.md
**Template:** `templates-technical-arc42-c4/epic/pdr.md`
**Content:** Product decisions for this epic
**Owner:** Product Owner
**Readers:** Architect, Epic Housekeeping

### file-plan-story-NN.yaml
**Template:** None (format defined inline in architect agent, Phase 7)
**Format:** YAML with epic_id, story_id, story_title, files_to_create/modify, intent, public_interface, signature_changes
**Intent:** 600-1200 chars total, optimized for semantic RAG
**Owner:** Architect
**Usage:** One file per story in `docs/epics/{epic-dir}/`

### implementation-summary.md
**Template:** `templates-technical-arc42-c4/epic/implementation-summary.md`
**Content:** Per-story summaries, lessons learned, implementation outcomes
**Owner:** Epic Housekeeping
**Trigger:** After epic completion

---

## Release Documentation

### record.md
**Template:** `templates-technical-arc42-c4/release/record.md`
**Content:** Epic/story list, dates, links to summaries
**Owner:** Release Planner

### notes.md
**Template:** `templates-technical-arc42-c4/release/notes.md`
**Content:** Internal (technical), external (user-facing)
**Owner:** Release Documentation

### postmortem.md
**Template:** `templates-technical-arc42-c4/release/postmortem.md`
**Content:** Retrospective, lessons learned
**Owner:** User
**Trigger:** After release

---

## Operations Documentation

Practical runbook documentation for sysadmins and on-call engineers. Complements architecture docs (which describe **what** and **why**) with operational docs (which describe **how to**).

### overview.md
**Template:** `templates-operations/overview.md`
**Content:** System inventory, component map, access points, service dependencies, on-call contacts
**Owner:** Operations / DevOps
**Readers:** All ops staff, on-call engineers
**Trigger:** New components added, infrastructure changes

### environments.md
**Template:** `templates-operations/environments.md`
**Content:** Environment matrix (dev/staging/prod), infrastructure details, network config, access methods, cloud project mapping
**Owner:** Operations / DevOps
**Readers:** All ops staff, developers
**Trigger:** Environment added/changed, infrastructure migration

### runbooks/deployment.md
**Template:** `templates-operations/runbooks/deployment.md`
**Content:** Build, deploy, rollback procedures with actual commands. CI/CD pipeline description. Hotfix process.
**Owner:** Operations / DevOps
**Readers:** On-call engineers, developers
**Trigger:** Deployment process changes

### runbooks/secrets-management.md
**Template:** `templates-operations/runbooks/secrets-management.md`
**Content:** Secrets inventory, rotation schedule, create/rotate/revoke procedures, compromised secret response
**Owner:** Operations / Security
**Readers:** On-call engineers, security team
**Trigger:** New secrets added, rotation policy changes

### runbooks/identity-access.md
**Template:** `templates-operations/runbooks/identity-access.md`
**Content:** User provisioning, approval, deprovisioning, role matrix, SSO config, access audit
**Owner:** Operations / Security
**Readers:** On-call engineers, team leads
**Trigger:** IdP changes, role model changes

### runbooks/networking-security.md
**Template:** `templates-operations/runbooks/networking-security.md`
**Content:** WAF rules, firewall config, TLS certificate management, DNS procedures, security incident response
**Owner:** Operations / Security
**Readers:** On-call engineers, security team
**Trigger:** Network topology changes, security policy updates

### runbooks/database.md
**Template:** `templates-operations/runbooks/database.md`
**Content:** Database inventory, connection procedures, backup/restore, schema migration, scaling, performance investigation
**Owner:** Operations / DBA
**Readers:** On-call engineers, developers
**Trigger:** Database changes, migration process updates

### runbooks/monitoring-alerting.md
**Template:** `templates-operations/runbooks/monitoring-alerting.md`
**Content:** Monitoring stack, dashboards, alert definitions and response procedures, on-call procedures
**Owner:** Operations / SRE
**Readers:** On-call engineers
**Trigger:** New alerts, monitoring stack changes

### runbooks/scaling.md
**Template:** `templates-operations/runbooks/scaling.md`
**Content:** Current scaling config, horizontal/vertical scaling procedures, auto-scaling configuration
**Owner:** Operations / DevOps
**Readers:** On-call engineers
**Trigger:** Scaling policy changes, capacity planning

### runbooks/disaster-recovery.md
**Template:** `templates-operations/runbooks/disaster-recovery.md`
**Content:** RTO/RPO targets, backup strategy, disaster scenarios, failover procedures, DR testing plan
**Owner:** Operations / DevOps
**Readers:** All ops staff, management
**Trigger:** DR test results, infrastructure changes

### troubleshooting/common-issues.md
**Template:** `templates-operations/troubleshooting/common-issues.md`
**Content:** Known operational issues with symptoms, root causes, and step-by-step resolutions
**Owner:** Operations (updated by all who resolve issues)
**Readers:** On-call engineers
**Trigger:** After resolving any recurring issue

### troubleshooting/escalation.md
**Template:** `templates-operations/troubleshooting/escalation.md`
**Content:** Severity levels, escalation path, contact list, vendor support, communication plan
**Owner:** Operations / Engineering Manager
**Readers:** On-call engineers
**Trigger:** Team changes, vendor contract changes

### maintenance/scheduled.md
**Template:** `templates-operations/maintenance/scheduled.md`
**Content:** Maintenance calendar, regular task procedures, maintenance window process
**Owner:** Operations / DevOps
**Readers:** All ops staff
**Trigger:** Maintenance schedule changes

### maintenance/upgrade-procedures.md
**Template:** `templates-operations/maintenance/upgrade-procedures.md`
**Content:** Component upgrade inventory, per-component upgrade playbooks, dependency update policy
**Owner:** Operations / DevOps
**Readers:** All ops staff
**Trigger:** Major version upgrades planned

---

## Lessons Learned

Actionable patterns and anti-patterns captured from real work. Each lesson has a detection rule so Claude can recognize when it applies.

### INDEX.md
**Template:** `templates-operations/lessons-learned/INDEX.md`
**Content:** One-liner per lesson with detection rule summary and severity. Loaded on conversation start for context.
**Owner:** All (appended by `/lesson` and `/wrap_epic` commands)
**Readers:** All agents — read on startup
**Trigger:** After `/lesson` or `/wrap_epic`

### {date}-{slug}.md
**Template:** `templates-operations/lessons-learned/lesson-template.md`
**Content:** Pattern or anti-pattern with detection rule, root cause analysis, and resolution
**Owner:** Whoever captures the lesson
**Readers:** All agents
**Trigger:** Created by `/lesson` command (interview or auto-detect mode) or by `/wrap_epic`

### Lesson Structure

Each lesson contains:
- **Type**: Pattern (do this) or Anti-Pattern (avoid this)
- **Detection**: How Claude recognizes when this applies (code pattern, config state, error message, or situation)
- **Rule**: One actionable sentence
- **Root Cause**: Why it matters (2-4 sentences)
- **Resolution**: How to fix or implement correctly

### Context Loading

Projects should add to CLAUDE.md:
```
On conversation start, read docs/lessons-learned/INDEX.md for project-specific lessons.
```

---

## Agent Responsibilities

| Agent | Writes | Reads (Primary) |
|-------|--------|-----------------|
| **Product Owner** | product/*, epics/*/{details,acceptance-criteria,pdr}.md | architecture/10-quality.md |
| **Architect** | architecture/*, architecture/backend/*, architecture/frontend/*, architecture/{adr,backend/adr,frontend/adr}/*.md, epics/*/{details,system-context,test-strategy,architecture,adr,file-plan}.yaml | product/{strategy,definition}.md |
| **SDET** | - | product/definition.md, architecture/{06,10}*.md, architecture/08-cross-cutting/testing.md, architecture/{backend,frontend}/*.md, epics/*/{details,acceptance-criteria,test-strategy,architecture}.md |
| **Developer (backend)** | - | architecture/backend/*.md, architecture/backend/adr/*.md, architecture/08-cross-cutting/*.md, epics/*/{test-strategy,adr}.md |
| **Developer (frontend)** | - | architecture/frontend/*.md, architecture/frontend/adr/*.md, architecture/08-cross-cutting/*.md, epics/*/{test-strategy,adr}.md |
| **Epic Housekeeping** | product/decisions.md (summaries), architecture/09-adr-summary.md (roll-up from all scopes), epics/*/implementation-summary.md | `.scope/*/agents_summaries.jsonl`, epics/*/{adr,pdr}.md, architecture/{adr,backend/adr,frontend/adr}/*.md |
| **Security Reviewer** | epics/*/adr.md (security), architecture/08-cross-cutting/security.md | architecture/{03,04,08,10}*.md, architecture/{backend,frontend}/*.md, epics/*/{details,adr}.md |
| **DevOps** | architecture/{07,08}/operations.md | architecture/{03,07,08}*.md, architecture/backend/overview.md |
| **Operations (RE)** | operations/* | architecture/{07,08-cross-cutting}*.md, architecture/backend/*.md |

---

## Guidelines

**Templates:** Use templates from `templates-product-atlassian/`, `templates-technical-arc42-c4/`, and `templates-operations/` matching structure above

**File naming:**
- Lowercase with hyphens: `building-blocks.md`
- Epic folders: `epic-123/`
- Numbered Arc42: `01-` through `12-`

**Frontmatter (YAML):** Use for epic metadata only. Keep minimal.

**Intent format (file plans):**
- 5 parts: WHAT (100 chars), WHY (150-250), RESPONSIBILITIES (150-250), DEPENDENCIES (100-150), RELATED MODULES (100-150)
- Total: 600-1200 chars
- Use positive delegation: "Related modules: session encryption via SessionStore"
- Avoid negation: ~~"Does NOT handle session encryption"~~
- Optimizes semantic search routing

**Token efficiency:**
- Agents load only pages they need (use direct paths from epic docs)
- No need to load entire guide during read operations

**Progressive disclosure:**
- Main page: overview, links
- Child pages: details >300 words
