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
│ - Deliverable: Content Brief per Page                        │
│ ──────────────────────────────────────────────────────────── │
│ → USER APPROVAL GATE #6                                      │
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

**Deliverable:** `{output_dir}/phase-6-content-briefs.md`

One section per page. Content should be specific enough that a copywriter or the user can write final copy directly from the brief.

**Approval gate:** User validates content direction. This is the final deliverable — approved briefs feed into design and development.

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
