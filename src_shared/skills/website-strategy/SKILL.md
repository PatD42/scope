---
name: website-strategy
description: Research-driven website strategy for B2B SaaS. Competitive analysis, persona mapping, information architecture, mood board, and content recommendations through phased discovery with user approval gates.
---

# Website Strategy Skill

Structured methodology for designing a professional B2B SaaS website through competitive research, persona-driven analysis, and phased deliverables. Each phase requires user approval before proceeding.

---

## Configuration

```yaml
# .scope/config.yaml
website_strategy:
  product_name: ""                    # e.g., "AquaForge"
  current_site_url: ""                # e.g., "https://aquaforge.ai"
  materials_path: ""                  # path to product docs, pitch decks, etc.
  price_range: ""                     # e.g., "$6K-$24K/year"
  language: "en"                      # "en" | "fr" | "bilingual"
  competitor: ""                      # primary competitor name/URL
  output_dir: "./docs/website-strategy"  # where deliverables go
  tech_stack: ""                      # e.g., "wordpress" | "nextjs" | "static"
  hosting: ""                         # e.g., "10web.io", "vercel", "netlify"
  theme_source: ""                    # e.g., "themeforest", "custom", "template"
```

---

## Personas

The skill operates on a **ranked persona list** provided by the user. Each persona entry must include:

| Field | Description |
|-------|-------------|
| **Name** | Short label (e.g., "Design Engineer") |
| **Role in buying process** | User, decision-maker, influencer, gatekeeper, partner |
| **Primary need from the website** | What they must understand or feel |
| **Desired action** | What the website should get them to do (e.g., request demo, purchase, contact partnerships) |
| **Priority** | Primary, secondary, tertiary |

### Use-Case Decomposition (per persona)

Each persona may have **multiple use cases** with different triggers, products, and value propositions. The agent must probe for this. A single persona row is insufficient when the same person interacts with different products at different stages.

| Field | Description |
|-------|-------------|
| **Use case name** | Short label (e.g., "RFP Response") |
| **Trigger** | What event causes this person to need the product now |
| **Product/tier** | Which specific product or tier addresses this use case |
| **Pain** | The specific problem in this use case context |
| **Value delivered** | What the product does for them in this context |
| **Quantified impact** | Time saved, cost avoided, risk reduced — with source if available |

The user defines personas before Phase 2. If the user provides an unstructured list, the agent must ask clarifying questions to fill all fields before proceeding.

---

## Positioning Constraints

Captured during Phase 1 as explicit inputs. These are strategic guardrails that prevent messaging drift across all phases.

| Field | Description | Example |
|-------|-------------|---------|
| **Identity** | What the company IS | "End-to-end water treatment platform" |
| **Anti-identity** | What the company must NOT be perceived as | "Not a regtech play" |
| **Supported claims** | Claims backed by research or data, with source | "6-11% budget overruns (industry research)" |
| **Unsupported claims** | Claims that sound true but lack citation — must NOT be stated as fact | "Regulatory gaps are the most expensive mistake" |
| **Philosophy** | Core product philosophy that must be reflected in messaging | "Descriptive, not prescriptive" |

These constraints are checked before every deliverable. If a phase output contradicts a positioning constraint, it must be corrected before presenting to the user.

---

## Corrections Log

Maintained as a running list throughout the engagement. When the user corrects a factual claim, positioning assumption, or strategic direction:

1. Log the correction with: what was wrong, what is right, which phases are affected
2. Immediately update all affected deliverables (do not defer)
3. Reference the corrections log before starting each new phase

Format: `{output_dir}/corrections-log.md`

```markdown
# Corrections Log

| # | Phase | What was wrong | Correction | Affected deliverables |
|---|-------|---------------|------------|----------------------|
| 1 | P3 | Hero leading with regulatory uncertainty alone | Lead with combined cost of regulatory + design mistakes. Not a regtech company. | phase-1, phase-3 |
```

---

## Workflow Overview

```
┌──────────────────────────────────────────────────────────────┐
│ Phase 1: Product & Industry Immersion                        │
│ - Read all materials in materials_path                       │
│ - Visit current_site_url (assess, do NOT use as baseline)    │
│ - Capture positioning constraints                            │
│ - Deliverable: Understanding Brief                           │
│ ──────────────────────────────────────────────────────────── │
│ → USER APPROVAL GATE #1                                      │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ Phase 2: Competitive & Industry Website Analysis             │
│ - Input: User provides company names/URLs                    │
│ - 2.0: Categorize references into clusters                   │
│ - 2.1: Triage list → shortlist per cluster                   │
│ - 2.2: Deep analysis per site (structured matrix)            │
│ - 2.3: Differentiation matrix validation with user           │
│ - Deliverable: Comparison Matrix + Shortlist Rationale       │
│ ──────────────────────────────────────────────────────────── │
│ → USER APPROVAL GATE #2                                      │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ Phase 3: Reusable Patterns Extraction                        │
│ - Extract patterns from shortlisted sites                    │
│ - Deliverable: Categorized Pattern Library                   │
│ ──────────────────────────────────────────────────────────── │
│ → USER APPROVAL GATE #3                                      │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ Phase 4: Visual Direction & Mood Board                       │
│ - Deliverable: Visual mood board (HTML → PDF/PNG)            │
│ - Supporting: Brand direction spec (markdown)                │
│ ──────────────────────────────────────────────────────────── │
│ → USER APPROVAL GATE #4                                      │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ Phase 5: Information Architecture                            │
│ - Sitemap, page hierarchy, navigation model                  │
│ - Purchase/e-commerce flows (if applicable)                  │
│ - Tech stack constraints applied                             │
│ - Deliverable: Sitemap + Page Wireframe Descriptions         │
│ ──────────────────────────────────────────────────────────── │
│ → USER APPROVAL GATE #5                                      │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ Phase 6: Content Strategy                                    │
│ - Per-page content with persona targeting                    │
│ - Deliverable: Content Brief per Page + PRD wrapper          │
│ ──────────────────────────────────────────────────────────── │
│ → USER APPROVAL GATE #6                                      │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ Phase 7: Theme Selection                                     │
│ - Build evaluation criteria from Phases 4+5                  │
│ - Research candidate themes                                  │
│ - Evaluate shortlist against criteria                        │
│ - User purchases and installs on staging                     │
│ - Document theme capabilities and constraints                │
│ - Deliverable: Theme Selection Report + updated PRD          │
│ ──────────────────────────────────────────────────────────── │
│ → USER APPROVAL GATE #7                                      │
│ → PRD ready for /prd_breakdown                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Phase Details

### Phase 1: Product & Industry Immersion

**Goal:** Build deep understanding of the product, market, competitive landscape, AND positioning constraints before analyzing external websites.

**Inputs:**
- All documents in `materials_path` (pitch decks, product strategy, messaging docs, competitive intelligence)
- Current website at `current_site_url`

**Process:**
1. Read all materials in `materials_path`. Parse PDFs, markdown, images.
2. Visit `current_site_url` using browser tools. Take screenshots of key pages.
3. Document: what the product does, who it's for, how it's differentiated, pricing model, current stage.
4. Note what the current site gets wrong or right (for reference only — not as a design baseline).
5. **Capture positioning constraints** by asking the user explicitly:
   - "What should the company NOT be perceived as?"
   - "Are there claims you've seen used that are NOT backed by research?"
   - "What is the core product philosophy that messaging must reflect?"

**Deliverable:** `{output_dir}/phase-1-understanding-brief.md`

```markdown
# Understanding Brief

## Product Summary
- What it does (2-3 sentences)
- Key modules/features
- Pricing model
- Current stage (pre-MVP, beta, GA)

## Market Context
- Industry and segment
- Key market drivers (regulatory, demographic, technological)
- Market size indicators

## Target Audiences
- Per persona: need, pain points, buying triggers
- Per persona: use-case decomposition (trigger → product → value)

## Positioning Constraints
- Identity and anti-identity
- Supported vs unsupported claims
- Core philosophy

## Competitive Landscape
- Primary competitor(s) and differentiation
- Positioning gaps/opportunities

## Current Site Assessment
- What exists today (page inventory)
- What works (if anything)
- What must change

## Open Questions
- Questions for user before proceeding
```

**Approval gate:** User validates understanding. Corrects any misunderstandings. Answers open questions. **Positioning constraints are confirmed explicitly** — these become immutable guardrails for all subsequent phases.

---

### Phase 2: Competitive & Industry Website Analysis

**Goal:** Analyze how industry players and the primary competitor present themselves online, specifically through the lens of the defined personas.

**Inputs:**
- User provides a list of company names and/or URLs
- Persona list (must be finalized before this phase)
- Positioning constraints from Phase 1

**Process:**

**Step 2.0 — Categorize References**

Before triaging, ask the user to categorize (or categorize and confirm) the reference list into clusters:

| Cluster | Purpose | Example |
|---------|---------|---------|
| **Direct competitors** | Must analyze. Head-to-head comparison. | Transcend |
| **Industry incumbents** | What the ICP considers "normal" for this space. Sets credibility bar. | Veolia, Xylem |
| **Product-model analogues** | Different industry, similar product model (software assisting engineers). Shows how to sell the product type. | Solibri, Autodesk Forma |
| **UX references** | Sites with specific UX patterns worth studying, regardless of industry. | (user-nominated) |

Different clusters serve different analysis purposes. Industry incumbents inform credibility expectations; product analogues inform conversion strategy; UX references inform specific patterns.

**Step 2.1 — Triage (quick research)**
For each company on the list:
- Identify their relevant division
- Assess website quality and relevance to the analysis
- Recommend a shortlist: **3-4 from the combined clusters + competitor**
- Present shortlist with rationale for user approval before deep analysis

**Step 2.2 — Deep Analysis (per shortlisted site)**
For each site, analyze using browser tools (WebFetch as primary, WebSearch for context, Playwright for screenshots when available — see Tools section for fallback strategy):

| Dimension | What to capture |
|-----------|-----------------|
| **Overview** | Company positioning, size, market segment |
| **Primary audience** | Who the site is really built for (may differ from stated) |
| **Per-persona analysis** | For each defined persona: narrative used, value proposition, CTA, content depth |
| **Trust signals** | Certifications, case studies, client logos, testimonials, data points |
| **Content strategy** | Blog, whitepapers, webinars, tools, calculators |
| **Navigation & IA** | Site structure, menu hierarchy, key page types |
| **Visual treatment** | Color palette, typography, imagery style, density |
| **Strengths** | What they do well that is relevant to our positioning |
| **Weaknesses** | Gaps, missed opportunities, poor execution |

**Step 2.3 — Differentiation Matrix Validation**
Before finalizing, present a structured differentiation table to the user for each claimed differentiator:

| Differentiator | Our claim | Competitor reality | Source/confidence |
|---------------|-----------|-------------------|-------------------|
| (feature) | (what we say) | (what they actually do) | (verified / user-stated / assumed) |

The user must confirm or correct each row. Validated differentiators propagate into Phases 3-6. Unvalidated ones are flagged as assumptions.

**Deliverable:** `{output_dir}/phase-2-competitive-matrix.md`

Format as a structured comparison matrix with:
1. Cluster categorization and shortlist rationale
2. Per-site analysis cards (all dimensions above)
3. Cross-site comparison table (strengths/weaknesses at a glance)
4. Per-persona effectiveness ranking across all sites
5. Validated differentiation matrix

**Approval gate:** User validates analysis and differentiation matrix. May request deeper dive on specific sites or add/remove from shortlist.

---

### Phase 3: Reusable Patterns Extraction

**Goal:** Extract specific, actionable design and UX patterns from the analyzed sites that could inform the new website.

**Inputs:**
- Phase 2 analysis
- Screenshots/observations from site visits
- Positioning constraints (to filter out patterns that conflict)

**Process:**
Categorize findings into:

| Category | What to capture |
|----------|-----------------|
| **Hero sections** | Headline approach, imagery, CTA placement, value prop framing |
| **Navigation** | Menu structure, mega-menus, utility nav, mobile patterns |
| **Social proof** | Logo bars, testimonials, case study formats, data callouts |
| **Product presentation** | How they show software/platform (screenshots, diagrams, animations, video) |
| **Persona routing** | How they direct different audiences (tabs, landing pages, nav splits) |
| **CTAs** | Placement, copy patterns, primary vs secondary actions |
| **Content formats** | Blog layouts, resource centers, gated vs ungated, interactive tools |
| **Trust & credibility** | Certification badges, team pages, partner ecosystems, awards |
| **Technical depth** | How they balance technical detail with accessibility |
| **Visual patterns** | Color usage, whitespace, icon systems, photography vs illustration |
| **E-commerce / purchase** | Pricing pages, cart flows, tier comparison, self-service vs sales |

For each pattern:
- Source site and page
- Description of the pattern
- Why it works (or doesn't)
- Applicability to our product and personas (high/medium/low)
- Adaptation notes (what to change for our context)

**Content strategy reality check:** Before recommending a blog or content cadence, ask:
- How often can the team realistically produce content?
- Is the subject domain fast-moving (weekly news) or slow-moving (yearly regulatory changes)?
- Is content jurisdiction-specific (limiting audience per piece)?
- What format matches the team's capacity (long-form quarterly vs short-form weekly)?

**Deliverable:** `{output_dir}/phase-3-pattern-library.md`

Must include a **priority-ranked top 10 patterns** summary table at the end, with each pattern tagged as: SOURCE (from analyzed site), UNIQUE (unoccupied by competitors), or ADAPTED (inspired by but modified from source).

**Approval gate:** User reviews patterns. Flags any they specifically like or dislike. May add patterns from other sites they've seen.

---

### Phase 4: Visual Direction & Mood Board

**Goal:** Define the visual and emotional direction for the website before structuring content. The primary deliverable is a **visual artifact** (PDF/PNG), not a markdown document.

**Inputs:**
- Existing brand assets (logo, current color palette if any)
- Brand pillars and tone from product materials
- Pattern library from Phase 3
- User preferences expressed during previous phases
- Positioning constraints

**Process:**
1. Analyze existing logo and brand elements for color, style, and personality cues
2. Analyze competitor color palettes to identify differentiation space
3. Ask the user for visual preferences before designing:
   - Light vs dark aesthetic
   - Color preferences/constraints beyond the logo
   - Imagery preferences (photography vs illustration vs product-forward)
   - Any sites they've seen and liked visually
4. Produce a visual mood board as an HTML file rendered to PDF/PNG via Playwright (or equivalent), containing:
   - **Cover page:** Logo, brand name, tagline, imagery collage
   - **Brand direction page:** Color palette swatches (with hex codes), typography samples, component library (buttons, badges, tags)
   - **Imagery direction page:** Visual examples organized by tier/category showing the kind of imagery to use
   - **Persona page:** Visual persona cards with role, description, and CTA
   - **Closing page:** Brand statement, product lifecycle bar
5. Produce a supporting markdown spec with the detailed rationale

**Asset sourcing plan:** The mood board will contain placeholder imagery unless the user provides real assets. For each imagery tier, specify:
- What kind of images are needed (facility photos, schematics, screenshots)
- Where to source them (stock libraries, client facilities, AI-generated, custom illustration)
- What NOT to use (stock water drops, abstract AI visuals, etc.)

**Deliverables:**
- `{output_dir}/moodboard.html` — Editable source
- `{output_dir}/AquaForge_Moodboard_2026.pdf` — Visual artifact (rendered from HTML)
- `{output_dir}/moodboard-page-{N}.png` — Individual page renders
- `{output_dir}/phase-4-mood-board.md` — Supporting spec with rationale, hex codes, font choices, and asset sourcing plan

**Note:** Phase 4 will produce layout patterns (e.g., lifecycle tabs, persona cards, hero structure) that are effectively IA decisions. These should be captured and fed into Phase 5 as confirmed layout commitments, not re-decided.

**Approval gate:** User selects or modifies a direction. This becomes the visual foundation for Phases 5 and 6.

---

### Phase 5: Information Architecture

**Goal:** Define the site structure, page hierarchy, navigation model, and purchase flows.

**Inputs:**
- Approved visual direction (including layout patterns committed in Phase 4)
- Persona list with priorities and use-case decomposition
- Product modules and their maturity stages
- Competitive patterns from Phase 3
- **Tech stack constraints** from config (WordPress, hosting, theme capabilities)
- **E-commerce requirements** (if any: what can be purchased, pricing transparency, cart flow)

**Process:**
1. Define primary navigation (max 5-7 top-level items)
2. Map full sitemap with page hierarchy
3. Define user flows per persona (entry → exploration → conversion)
4. **Define purchase flow** (if e-commerce is required):
   - Pricing page structure (transparent vs gated, tier comparison)
   - Cart → checkout → account creation → onboarding sequence
   - Which products are self-service vs sales-assisted
5. **Apply tech constraints:**
   - WordPress: pages vs posts vs custom post types
   - Plugin requirements (multilingual, e-commerce, forms, SEO)
   - What Claude Code will maintain (templates, CSS, shortcodes) vs what plugins handle
   - Theme constraints (what's feasible with a purchased theme vs custom development)
6. **Define multilingual URL strategy** (if bilingual/multilingual):
   - Present WPML (or equivalent) URL format options to the user with trade-offs:
     - `/{lang}/{path}/` (directory per language — both languages treated equally)
     - Default language without code, translated with prefix (asymmetric)
     - Subdomains (`en.site.com`, `fr.site.com`)
     - Domains per language
     - Query parameter (`?lang=fr`)
   - User must select one. This affects all URLs in the sitemap.
   - Map translated slugs for all pages (e.g., `/platform/` → `/plateforme/`)
6. For each page, describe:
   - Purpose (why this page exists)
   - Primary persona served
   - Key content blocks (ordered)
   - Primary CTA
   - Secondary CTA (if any)
   - Internal links to/from

**Deliverable:** `{output_dir}/phase-5-information-architecture.md`

```markdown
# Information Architecture

## Sitemap
[Tree structure of all pages]

## Navigation Model
- Primary nav items + dropdowns
- Utility nav (login, language, contact)
- Footer structure
- Mobile navigation approach

## User Flows
### [Persona 1] Flow
Entry point → Page sequence → Conversion action

### [Persona 2] Flow
...

## CTA Strategy

A consolidated matrix of ALL conversion actions across the site. Defined here (not scattered per-page) because CTAs are structural decisions that affect navigation, layout, and user flows.

### CTA Inventory

For each CTA:

| Field | Description |
|-------|-------------|
| **CTA name** | Short label (e.g., "Start Free Trial") |
| **Target persona** | Which persona this is designed for |
| **Funnel stage** | Awareness → Consideration → Decision → Retention |
| **Action type** | Self-service purchase, sales-assisted, email capture, contact form, external redirect |
| **Button copy** | Exact text (EN + FR) |
| **Destination** | Where the click goes (URL or form) |
| **Visual treatment** | Primary (filled), secondary (outline), tertiary (text link) |
| **Appears on** | List of pages where this CTA is used |

### CTA Hierarchy

When multiple CTAs compete for the same page or section, define the priority:
- **Header persistent CTAs** — which 1-2 CTAs are always visible in the nav bar
- **Hero CTAs** — primary + secondary per page
- **Section CTAs** — contextual CTAs within content blocks
- **Exit CTAs** — bottom-of-page final conversion prompts

### CTA-to-Persona Mapping

Matrix showing which CTAs serve which persona at which funnel stage:

```
                    Engineer    CFO/COO    OEM
Awareness           [CTA]       [CTA]     [CTA]
Consideration       [CTA]       [CTA]     [CTA]
Decision            [CTA]       [CTA]     [CTA]
```

This ensures every persona has a clear conversion path and no persona hits a dead end.

## Purchase Flow (if applicable)
- Pricing page layout
- Tier comparison structure
- Cart → checkout → onboarding sequence
- Self-service vs sales-assisted boundaries

## Multilingual URL Strategy
- Selected URL format with rationale
- Full sitemap in each language with translated slugs
- Root URL redirect behavior
- SEO: hreflang tags, per-language meta

## Tech Stack Mapping
- WordPress page types (page, post, custom post type)
- Required plugins (with purpose)
- Template structure (what Claude Code maintains)
- Theme requirements/constraints

## Page Specifications
### [Page Name]
- URL path
- WordPress page type
- Purpose
- Primary persona
- Content blocks (ordered):
  1. [Block name] — description
  2. ...
- Primary CTA
- Secondary CTA
- Links to/from
```

**Approval gate:** User validates sitemap, purchase flow, and page specs. May add/remove pages or restructure navigation.

---

### Phase 6: Content Strategy

**Goal:** Define the actual content for each page, targeted to the appropriate personas.

**Inputs:**
- Approved IA from Phase 5
- Product messaging from Phase 1
- Visual direction from Phase 4
- Positioning constraints (checked before every claim)
- Corrections log (checked before every deliverable)

**Process:**
For each page defined in Phase 5, create a content brief:

| Element | Description |
|---------|-------------|
| **Headline** | Primary headline copy (2-3 options) |
| **Subheadline** | Supporting message |
| **Body sections** | Per content block: key message, supporting points, tone |
| **Data points** | Specific numbers, stats, claims to include — **must reference source and be in the "supported claims" list** |
| **Social proof** | Which trust signals appear on this page |
| **CTAs** | Button copy, destination, urgency framing |
| **SEO** | Target keywords, meta description |
| **Assets needed** | Screenshots, diagrams, videos, illustrations to create — **with sourcing plan** |
| **Persona targeting** | Which persona(s) this content addresses and how |
| **Language** | If bilingual: flag content that differs between EN/FR vs content that is a direct translation |

**Deliverables:**
- `{output_dir}/phase-6-content-briefs.md` — One section per page. Content should be specific enough that a copywriter or the user can write final copy directly from the brief.
- `{output_dir}/website_prd.md` — PRD wrapper document (see below)

**Before producing the PRD wrapper, the agent MUST gather the following from the user.** These are required for `/prd_breakdown` to scope epics correctly — do not defer them to PRD refinement:

1. **MVP phasing.** Ask: "Which pages/features MUST ship for launch vs can come later?" Propose a v1.0/v1.1/v1.2+ split based on the page list from Phase 5, then confirm. Rule of thumb: v1.0 is the minimum set that enables the primary business goal (e.g., selling, lead capture). Defer anything that requires custom post types, external integrations beyond payment, or content that doesn't exist yet.

2. **Non-functional requirements.** Ask the user about each category explicitly:
   - **Performance:** LCP target, PageSpeed minimum
   - **Accessibility:** WCAG compliance level (AA, AAA)
   - **Browser support:** Which browsers/versions, any to exclude
   - **Mobile:** Responsive tested on which devices
   - **SEO:** Indexing rules, structured data needs, hreflang
   - **Security:** HTTPS, update cadence, security plugin

3. **External dependencies & risks.** For each plugin, external service, theme, or integration in the tech stack, identify: what breaks if it fails/expires/changes pricing, and what's the mitigation/fallback?

4. **Success criteria sanity-check.** Review success metrics against current tech stack — if a technology was removed during planning (e.g., WooCommerce), update metrics that reference it.

**Approval gate:** User validates content direction AND approves MVP phasing, NFRs, and dependency risks. After approval, generate the PRD wrapper.

### PRD Wrapper Document

After Phase 6 approval, produce a single `website_prd.md` file at `{output_dir}/website_prd.md` that serves as the entry point for `/prd_breakdown`. This file:

- Provides project context (purpose, business context, personas, philosophy)
- References all phase deliverables with their paths and purpose
- Defines the technical stack (CMS, plugins, hosting, auth integration)
- Summarizes key functional requirements
- Lists positioning constraints as immutable rules
- **Defines MVP phasing** (v1.0, v1.1, v1.2+)
- **Defines non-functional requirements** (performance, accessibility, browser support, security)
- **Documents external dependencies with risks and mitigations**
- Defines success criteria
- Defines out-of-scope items

The PRD wrapper does NOT duplicate the phase deliverables — it references them. `/prd_breakdown` reads the PRD, then loads referenced documents as needed.

**The PRD must be directly assessable for readiness** (ready for epic breakdown) without requiring refinement. Do not skip the sections below — they are required for `/prd_breakdown` to scope epics correctly.

```markdown
# Website PRD

## Purpose
[Why this website exists]

## Business Context
[Company stage, what the product is, what it is NOT]

## Target Personas
[Summary table with link to Phase 1 for details]

## Product Philosophy
[Core philosophy that must be reflected in all messaging]

## Strategy Documents (Reference)
| Document | Path | Purpose |
|----------|------|---------|
| Understanding Brief | phase-1... | ... |
| Competitive Matrix | phase-2... | ... |
| Pattern Library | phase-3... | ... |
| Mood Board | phase-4... | ... |
| Information Architecture | phase-5... | ... |
| Content Briefs | phase-6... | ... |
| Theme Selection | phase-7... | ... |

## Technical Stack
[CMS, plugins, hosting, auth, maintenance model]

## Key Functional Requirements
[Payment flow, bilingual, case studies, blog, knowledge base, forms, navigation]

## Positioning Constraints (Immutable)
[Rules that apply to ALL content during implementation]

## MVP Phasing

### v1.0 (Launch Minimum)
[Which pages, global elements, and integrations must ship for launch — the minimum set that enables the primary business goal]

### v1.1 (Post-Launch)
[Pages and features planned for ~4-8 weeks after v1.0]

### v1.2+ (Later)
[Deferred pages and features]

**This section is REQUIRED.** Epic sequencing depends on it. Ask the user explicitly:
- "Which pages MUST ship for launch vs can come later?"
- "What's the minimum set that enables selling?"
- Propose a default split and confirm with user.

## Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Performance | [LCP targets, PageSpeed minimums] |
| Accessibility | [WCAG compliance level] |
| Browser support | [Specific versions, no IE, etc.] |
| Mobile | [Responsive requirements, tested devices] |
| SEO | [Indexing, structured data, hreflang] |
| Security | [HTTPS, update cadence, security plugin] |

**This section is REQUIRED.** Ask the user about each category — do not leave NFRs implicit.

## External Dependencies & Risks

| Dependency | Risk | Mitigation |
|-----------|------|-----------|
| [Plugin/service with license or vendor risk] | [What breaks if it fails] | [Fallback or renewal plan] |

**This section is REQUIRED.** Every external dependency from the tech stack should have an entry. Ask the user about license lifecycles and vendor lock-in.

## Success Criteria
[Measurable targets — do NOT reference tech that was removed from scope]

## Out of Scope
[What this PRD does NOT cover]
```

### PRD Readiness Self-Check (before handoff)

After generating the PRD wrapper, the agent MUST run a readiness self-check before declaring Phase 6 complete. Present this checklist to the user:

```
PRD Readiness Check:

□ Purpose / Vision is clear (1-3 sentences)
□ Business context describes what the product IS and IS NOT
□ Target Personas documented with priority and desired action
□ Product Philosophy captured (if applicable)
□ All phase deliverables referenced with correct paths
□ Technical Stack complete (CMS, plugins, hosting, integrations)
□ Key Functional Requirements documented
□ Positioning Constraints listed as immutable rules
□ MVP Phasing defined (v1.0, v1.1, v1.2+)
□ Non-Functional Requirements documented (Performance, A11y, Browser, Mobile, SEO, Security)
□ External Dependencies & Risks documented (every tech stack item that could fail/lapse)
□ Success Criteria are measurable AND reference only current tech (no references to removed components)
□ Out of Scope items listed
```

If ANY item is unchecked:
1. Return to the user with the gap
2. Gather the missing information
3. Update the PRD
4. Re-run the check

Only when ALL items are checked is the PRD ready. The PRD must be directly assessable for epic breakdown WITHOUT requiring `/prd_refine` to catch gaps.

---

### Phase 7: Theme Selection

**Goal:** Select and evaluate a WordPress theme that supports the IA, visual direction, and plugin requirements — before `/prd_breakdown` scopes the epics.

**Why this is a separate phase:** Theme choice constrains every implementation epic. "Customize existing mega-menu" is a fundamentally different task than "build mega-menu from scratch." `/prd_breakdown` needs to know what the theme provides out of the box.

**Inputs:**
- Mood board and visual direction (Phase 4) — color compatibility, typography, density, emotional tone
- Information architecture (Phase 5) — navigation model, page types, content blocks, purchase flow
- Tech stack requirements (Phase 5) — WPML, WooCommerce, WooCommerce Subscriptions compatibility
- Content briefs (Phase 6) — specific content blocks that need theme support (tabbed sections, comparison tables, testimonial carousels, counter animations)

**Process:**

**Step 7.1 — Build Evaluation Criteria**

Generate a weighted checklist from the phase deliverables:

| Category | Criteria | Weight | Source |
|----------|----------|--------|--------|
| **Plugin compatibility** | WPML compatible | Must-have | Phase 5 tech stack |
| | WooCommerce + Subscriptions compatible | Must-have | Phase 5 e-commerce |
| | Contact Form 7 or WPForms compatible | Must-have | Phase 5 forms |
| **Navigation** | Mega-menu or advanced dropdown support | Must-have | Phase 5 nav model |
| | Mobile hamburger with accordion dropdowns | Must-have | Phase 5 mobile nav |
| | Sticky header support | Should-have | Phase 5 mobile nav |
| **Layout components** | Tabbed content sections | Must-have | Phase 3 Pattern 1.3 (lifecycle tabs) |
| | Comparison/pricing table | Must-have | Phase 5 pricing page |
| | Testimonial carousel/slider | Should-have | Phase 6 social proof |
| | Animated counter/metrics | Should-have | Phase 3 Pattern 3.1 |
| | Side-by-side content (image + text) | Must-have | Phase 6 multiple pages |
| | Full-width hero with overlay text | Must-have | Phase 6 homepage |
| **Visual fit** | Clean, minimal design (not over-decorated) | Must-have | Phase 4 "Engineered Clarity" |
| | Customizable color scheme | Must-have | Phase 4 palette |
| | Google Fonts support (IBM Plex Sans) | Must-have | Phase 4 typography |
| | Light/white backgrounds as default | Should-have | Phase 4 density |
| **Performance** | PageSpeed score 85+ on demo | Should-have | General |
| | Lightweight CSS/JS (not bloated) | Should-have | General |
| **Maintenance** | Well-documented child theme support | Must-have | Claude Code maintenance |
| | Regular updates (last update < 6 months) | Must-have | Security |
| | Good support/documentation | Should-have | General |
| **Page builder** | Elementor, WPBakery, or Gutenberg-native | Preference | Note trade-offs |

**Step 7.2 — Research Candidates**

Search theme marketplaces (ThemeForest, ThemeIsle, Flavor Theme, or others) for themes matching "must-have" criteria. Use WebSearch and WebFetch to:
- Find WordPress themes for SaaS / technology / corporate sites
- Check demo sites for visual fit
- Read reviews and changelogs
- Verify plugin compatibility claims

**Shortlist 3-5 candidate themes.** For each candidate:
- Theme name, author, marketplace, price
- Link to live demo
- Score against evaluation criteria (pass/fail for must-haves, score for should-haves)
- Screenshots of relevant demo pages (homepage, pricing, blog)
- Known limitations or risks

**Step 7.3 — Evaluate Shortlist with User**

Present the shortlist as a comparison table. Include:
- Scores per category
- Visual screenshots from demos
- Price and licensing terms
- Recommendation with rationale

User selects a theme (may want to browse demos independently before deciding).

**Step 7.4 — Document Theme Capabilities**

After user purchases and installs the theme on 10web staging:
- Install and activate the theme on staging
- Document what the theme provides out of the box vs what needs custom development:

| Need (from IA/content briefs) | Theme provides? | Custom work required? |
|-------------------------------|----------------|----------------------|
| Mega-menu dropdown | Yes — built-in | Configure only |
| Lifecycle tabs (homepage hero) | Partial — has tabs component but needs custom styling | Child theme CSS |
| Pricing comparison table | No | Custom template or plugin |
| AI conversation mockup | No | Custom HTML/CSS block |
| ... | ... | ... |

This capability-vs-gap table becomes a critical input to `/prd_breakdown` — it determines epic scope.

**Deliverables:**
- `{output_dir}/phase-7-theme-selection.md` — Evaluation criteria, candidate shortlist, comparison, recommendation, and post-install capability mapping
- Updated `{output_dir}/website_prd.md` — Add theme selection to the tech stack section and reference the capability mapping

**Approval gate:** User confirms theme choice. Capability mapping reviewed. PRD is now complete and ready for `/prd_breakdown`.

---

## Questioning Protocol

Before each phase, the agent MUST:

1. **Check the corrections log** and positioning constraints before producing any output
2. **State what it needs** from the user to proceed (inputs, decisions, preferences)
3. **Ask specific questions** — not open-ended "anything else?" but targeted: "Which of these 3 personas should the homepage hero prioritize?"
4. **Propose defaults** when asking — "I'd recommend X because Y. Should I proceed with that, or do you prefer Z?"
5. **Limit questions to 3-5 per phase** — batch them, don't drip-feed

The agent must NOT:
- Proceed past an approval gate without explicit user confirmation
- Make persona priority decisions without user input
- Assume language/market preferences
- Use the current site as a design baseline (assess it, don't emulate it)
- State claims as fact without checking the "supported claims" list
- Recommend content cadence without asking about realistic production capacity

---

## Output Format

**Markdown deliverables:** All strategy documents are markdown files in `{output_dir}/`. Name format: `phase-{N}-{slug}.md`.

Within each deliverable:
- Use tables for comparison data
- Use bullet points for lists of attributes
- Use headers for clear section breaks
- Include source references (which site, which page) for all competitive observations
- Flag assumptions explicitly with `**Assumption:**` prefix
- Flag unsupported claims with `**Unverified:**` prefix

**Visual deliverables:** Phase 4 mood board is an HTML file rendered to PDF/PNG. The HTML source is the editable artifact; the PDF/PNG is the presentation artifact.

---

## Tools & Fallback Strategy

Web research tooling is fragile. Browser sessions die, sites block bots, and subagents may lack browser access. Use this fallback chain:

| Priority | Tool | Best for | Limitations |
|----------|------|----------|-------------|
| 1 | **WebFetch** | Fetching specific URLs, analyzing page content | Blocked by 403s, bot detection, JS-heavy sites |
| 2 | **WebSearch** | Finding correct URLs, getting context about companies | Returns summaries, not full page analysis |
| 3 | **Playwright** | Screenshots, interactive navigation, full page rendering | Sessions die, subagents can't use it, resource-heavy |
| 4 | **User-provided screenshots** | Last resort when all tools fail | Requires user action |

**Rules:**
- Start with WebFetch for page analysis. Fall back to WebSearch if 403/404.
- Use Playwright for screenshots only from the main agent (not subagents).
- If a critical site is inaccessible, ask the user for screenshots rather than guessing.
- Never present training-data knowledge about a website as current fact — sites change. If you can't verify, say so.

---

## Constraints

- **No speculative design.** Every recommendation must trace back to: competitive evidence (Phase 2-3), persona needs, or product positioning. No "I think this would look nice."
- **No premature implementation.** This skill produces strategy and content briefs, not code. Implementation is a separate concern (feeds into PRD breakdown).
- **Respect the phase order.** Visual direction before IA. IA before content. Skipping phases produces shallow work.
- **Current site is context, not baseline.** Assess it to understand what exists. Do not carry forward its structure, copy, or design choices unless they are independently justified.
- **No unsourced claims as fact.** Every data point in content briefs must reference a source. If the source is "user stated" vs "industry research," note the difference. If a claim sounds plausible but has no citation, flag it as **Unverified** and ask the user.
- **Corrections propagate immediately.** When the user corrects a fact or direction, update ALL affected prior deliverables before proceeding. Do not defer corrections.
- **Tech constraints inform IA.** Phase 5 must account for the actual tech stack (WordPress capabilities, plugin ecosystem, theme limitations). Do not design an IA that requires custom development if the user specified a ThemeForest theme.
