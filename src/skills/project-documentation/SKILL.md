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
│   ├── 01-intro.md
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
│   ├── 09-adr-summary.md
│   ├── 10-quality.md
│   ├── 11-risks.md
│   └── 12-glossary.md
├── epics/{epic-id-with-filesafe-title}/
│   ├── details.md
│   ├── system-context.md
│   ├── acceptance-criteria.md
│   ├── test-strategy.md
│   ├── architecture.md
│   ├── adr.md
│   ├── pdr.md
│   ├── file-plan.yaml
│   └── implementation-summary.md
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

## Epic Documentation

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
**Format:** Decision title, context, options, decision, consequences
**Owner:** Architect
**Readers:** Developer (when unclear), Epic Housekeeping

### pdr.md
**Template:** `templates-technical-arc42-c4/epic/pdr.md`
**Content:** Product decisions for this epic
**Owner:** Product Owner
**Readers:** Architect, Epic Housekeeping

### file-plan.yaml
**Template:** `templates-technical-arc42-c4/epic/file-plan.yaml`
**Format:** YAML with epic_id, stories, files_to_create/modify, intent (5-part: WHAT, WHY, RESPONSIBILITIES, DEPENDENCIES, RELATED MODULES)
**Intent:** 600-1200 chars total, optimized for semantic RAG
**Owner:** Architect
**Usage:** Cached locally in `.scope/{epic-id}/file_plan.json`

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

## Agent Responsibilities

| Agent | Writes | Reads (Primary) |
|-------|--------|-----------------|
| **Product Owner** | product/*, epics/*/{details,acceptance-criteria,pdr}.md | architecture/10-quality.md |
| **Architect** | architecture/*, epics/*/{details,system-context,test-strategy,architecture,adr,file-plan}.yaml | product/{strategy,definition}.md |
| **SDET** | - | product/definition.md, architecture/{06,10}*.md, architecture/08-cross-cutting/testing.md, epics/*/{details,acceptance-criteria,test-strategy,architecture}.md |
| **Developer** | - | architecture/08-cross-cutting/*.md, epics/*/{test-strategy,adr}.md (if unclear) |
| **Epic Housekeeping** | product/decisions.md (summaries), architecture/09-adr-summary.md (summaries), epics/*/implementation-summary.md | `.scope/*/agents_summaries.jsonl`, epics/*/{adr,pdr}.md |
| **Security Reviewer** | epics/*/adr.md (security), architecture/08-cross-cutting/security.md | architecture/{03,04,08,10}*.md, epics/*/{details,adr}.md |
| **DevOps** | architecture/{07,08}/operations.md | architecture/{03,07,08}*.md |

---

## Guidelines

**Templates:** Use templates from `templates-product-atlassian/` and `templates-technical-arc42-c4/` matching structure above

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
