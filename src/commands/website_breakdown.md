---
name: website_breakdown
description: Break a website PRD into implementable epics with dependencies. WordPress-specific epic structure (Foundation, Custom Blocks, Pages, Integrations, Content, Launch). Output feeds /webepic_refine.
skills: project-documentation
---

# /website_breakdown

Convert an approved website PRD into a sequenced list of epics with dependencies. Assumes WordPress + child theme architecture.

**Syntax:** `/website_breakdown`

## Prerequisites

- `docs/website-strategy/website_prd.md` exists and passes PRD Readiness Self-Check
- Phase 1-7 deliverables in `docs/website-strategy/`
- MVP phasing defined (v1.0, v1.1, v1.2+)

---

## Workflow

```
Phase 1: Load PRD + Phase deliverables
Phase 2: Identify epic candidates (v1.0 scope)
Phase 3: Map dependencies
Phase 4: User validation + approval
Phase 5: Create epic documentation (docs/epics/{epic-id}/details.md)
Phase 6: Update PRD with epic map
```

---

## Epic Category Framework

Website projects typically have 6 epic categories. Use these as the starting point for epic identification:

| Category | Purpose | Typical deliverables |
|----------|---------|---------------------|
| **1. Foundation** | Baseline WordPress config + theme + plugins + global elements | Theme setup, plugin install/config, WPML, GA4, menus, header/footer, staging↔prod workflow |
| **2. Custom Blocks** | Custom Gutenberg blocks or block patterns that multiple pages depend on | Block patterns from Phase 7 capability mapping (lifecycle tabs, AI conversation, pricing table, counters, testimonials, etc.) |
| **3. Content Pages** | Individual page templates and structures | One epic per page group (e.g., "Homepage", "Product Pages", "Persona Pages", "Pricing", "About", etc.) |
| **4. CPTs & Templates** | Custom post types with archive + single templates | Case Study CPT, Knowledge Base CPT, blog customizations |
| **5. Integrations** | External service connections | Attio forms, Stripe redirect, Keycloak tracking, analytics |
| **6. Content Population** | Actual copy + translations + assets | Per-page content creation via `/content_refine` |
| **7. Quality & Launch** | Performance, a11y, cross-browser, SEO, launch prep | PageSpeed optimization, a11y audit, SEO setup, staging→prod push |

Not every project has all 7. Scope to what's actually in the PRD's v1.0.

---

## Phase 1: Load Context

Read:
- `docs/website-strategy/website_prd.md` (full PRD)
- `docs/website-strategy/phase-5-information-architecture.md` (sitemap, page specs, CTA strategy)
- `docs/website-strategy/phase-6-content-briefs.md` (content block structure per page)
- `docs/website-strategy/phase-7-capability-mapping.md` (custom work vs configuration)

Extract v1.0 scope from PRD's MVP Phasing section.

---

## Phase 2: Identify Epic Candidates

**Process:**

1. **Foundation epic** — always present. Pull from:
   - Technical Stack (plugins, hosting, theme)
   - Global elements (header, footer, nav, WPML setup)
   - Analytics (GA4)

2. **Custom Blocks epic(s)** — from Phase 7 capability mapping. Group related blocks:
   - If 3-5 blocks: single "Custom Blocks" epic
   - If 6+ blocks: split by theme (e.g., "Hero & Navigation Blocks", "Product & Pricing Blocks", "Social Proof Blocks")

3. **Content Pages epic(s)** — from v1.0 page list in PRD. Group logically:
   - "Homepage" (usually its own epic due to complexity)
   - "Product Pages" (if multiple products)
   - "Persona Pages" / "Solutions Pages"
   - "Pricing + About + Careers" (if smaller pages)
   - "Legal Pages" (Privacy, Terms)
   - "Blog archive" (empty or with 1-2 posts)

4. **CPTs & Templates epic** — only if v1.0 needs custom post types
5. **Integrations epic** — for Attio, Stripe, GA4, etc.
6. **Content Population epic** — per-page content via `/content_refine`
7. **Quality & Launch epic** — performance tuning, a11y, SEO, staging→prod push

**Size discipline:**
- Each epic should be completable in 1-3 days of focused work
- If an epic feels larger than 3 days, split it
- If an epic feels smaller than half a day, merge it

---

## Phase 3: Map Dependencies

**Standard dependency patterns:**

```
Foundation
    ↓
    ├─→ Custom Blocks (can start in parallel after Foundation basics)
    │       ↓
    │       ├─→ Content Pages (need custom blocks)
    │       │       ↓
    │       │       └─→ Content Population (need pages to populate)
    │       │               ↓
    │       │               └─→ Quality & Launch
    │       │
    │       └─→ Custom blocks also needed for CPT templates
    │
    ├─→ CPTs & Templates (can start in parallel after Foundation)
    │       ↓
    │       └─→ Content Pages (if pages reference CPT archives)
    │
    └─→ Integrations (can start in parallel, need to be done before Launch)
            ↓
            └─→ Quality & Launch
```

**Dependency rules:**
- Foundation blocks everything
- Custom Blocks block Content Pages that use them
- Content Pages block Content Population
- Integrations can run parallel to pages but must complete before Launch
- Quality & Launch is last

**Document dependencies per epic:**
```yaml
epic_id: content-pages-core
depends_on:
  - foundation
  - custom-blocks
```

---

## Phase 4: User Validation

Present to user:

```
Epic Breakdown for {project-name} v1.0:

Category 1: Foundation
  - E1: Foundation Setup
    Scope: Theme install, plugins, WPML, GA4, menus, header, footer
    Dependencies: none
    Size estimate: 1-2 days

Category 2: Custom Blocks
  - E2: Custom Block Patterns
    Scope: 6 block patterns from Phase 7
    Dependencies: E1 (Foundation)
    Size estimate: 2-3 days

Category 3: Content Pages
  - E3: Homepage
    ...
  - E4: Product Pages (Regulatory Intelligence + Deployment placeholder)
    ...
  ...

Total: {N} epics, ~{X} days estimated work
v1.0 target date: {date from PRD}

Does this breakdown match your expectations?
Any epics to merge, split, or reorder?
```

**Wait for user approval or revisions.**

---

## Phase 5: Create Epic Documentation

For each approved epic, create `docs/epics/{epic-id}/details.md`:

```markdown
---
epic_id: {epic-id}
title: {Epic Title}
status: ready-for-refinement
version: v1.0
target_date: {date}
depends_on: [{list of epic IDs}]
---

# {Epic Title}

## Intent
[What this epic accomplishes in 1-2 sentences]

## Scope

### In scope
- [Specific pages/components/features in this epic]

### Out of scope
- [Related work that belongs in OTHER epics]

## Key References
- PRD section: {section number}
- Phase 5 pages: {page paths}
- Phase 6 content: {content brief sections}
- Phase 7 capability: {capability mapping entries}

## Preliminary Risks
- [Risks specific to this epic]

## Acceptance Criteria (Placeholder)
To be refined via /webepic_refine {epic-id}
```

---

## Phase 6: Update PRD with Epic Map

Append an "Epic Map" section to `website_prd.md`:

```markdown
## Epic Map

### v1.0 Epics

| ID | Title | Category | Depends On | Size |
|----|-------|----------|------------|------|
| foundation | Foundation Setup | Foundation | — | 1-2d |
| custom-blocks | Custom Block Patterns | Custom Blocks | foundation | 2-3d |
| homepage | Homepage | Pages | custom-blocks | 2d |
| ... | ... | ... | ... | ... |

### Sequencing

Critical path: foundation → custom-blocks → homepage → content-population → launch

Parallel tracks after foundation:
- Track A: custom-blocks → content-pages → content-population
- Track B: integrations
- Track C: CPT-templates (if in v1.0)

All tracks converge at Quality & Launch.
```

---

## Output

After completion:

1. `docs/epics/{epic-id}/details.md` for each epic (ready for `/webepic_refine`)
2. Updated `website_prd.md` with Epic Map section
3. User can now run `/webepic_refine {epic-id}` on the first epic

Report summary:
- Number of epics created
- Critical path
- Estimated total work days
- First epic to refine (typically "foundation")

---

## Constraints

- **Epics align with v1.0 phasing only.** Defer v1.1 and v1.2+ epics until v1.0 is shipped.
- **Dependencies are non-negotiable.** Do not let user skip Foundation or start pages before custom blocks.
- **Size estimates inform sequencing, not absolute timelines.** They're t-shirt sizes, not commitments.
- **Content Population is always after Pages.** Never bundle content writing into page-building epics — it bloats scope.
- **Quality & Launch is always last.** No shipping to production before the final audit.
