---
name: content_refine
description: Refine AND publish page content (EN + FR) from Phase 6 content briefs. Applies positioning constraints, validates claims, translates, identifies assets, publishes to WordPress.
args: "{page-slug}"
skills: project-documentation
---

# /content_refine

Generate final publishable content for a page from its Phase 6 brief. Runs end-to-end: draft → validate → translate → publish. No separate implementation step — content IS the implementation.

**Syntax:** `/content_refine {page-slug}`

Example: `/content_refine homepage`, `/content_refine regulatory-intelligence`, `/content_refine pricing`

## Prerequisites

- Phase 6 content briefs: `docs/website-strategy/phase-6-content-briefs.md`
- Positioning constraints defined in PRD
- Supported/unsupported claims table (Phase 6)
- Page exists in WordPress staging (created via `/webepic_implement`)
- WP application password OR SFTP access in `.env`

---

## Workflow

```
Phase 1: Brief extraction         → load page content blocks
Phase 2: EN content drafting       → generate final copy
Phase 3: Positioning validation    → check constraints + claims
           → GATE #1 (user reviews EN)
Phase 4: FR translation            → Quebec-aware French
           → GATE #2 (user reviews FR)
Phase 5: Asset list                → identify required images/media
Phase 6: Publish to WordPress      → via REST API or file output
           → GATE #3 (user visual review on staging)
```

---

## Phase 1: Brief Extraction

**Process:**
1. Read `docs/website-strategy/phase-6-content-briefs.md`
2. Locate the section for `{page-slug}`
3. Extract:
   - Headline options
   - Subheadline
   - Each content block with its description
   - CTAs (button copy + destinations)
   - Data points with sources
   - SEO targets
   - Required assets

If no matching section is found, report to user and halt.

---

## Phase 2: EN Content Drafting

**Goal:** Produce ready-to-publish English copy for every content block on the page.

**Process:**
1. For each content block in the brief:
   - Choose the best headline option (or compose from the 2-3 options)
   - Expand body copy from the description + key message
   - Include specific data points with sources inline
   - Match tone to the page's primary persona
2. Apply voice consistency:
   - **Descriptive, not prescriptive** — show reasoning, invite engineer judgment
   - **Confident, not boastful** — state facts with sources
   - **Precise, not vague** — specific numbers, specific jurisdictions, specific products
3. Length discipline:
   - Hero headlines: ≤ 12 words
   - Section headlines: ≤ 8 words
   - Body paragraphs: ≤ 3 sentences per block

**Output:** Draft EN content, organized by content block, saved to `docs/content/{page-slug}.en.md`

---

## Phase 3: Positioning Validation

**This phase is automated and MUST be run before user review.**

**Checks to perform:**

### Positioning Constraints
Scan the drafted EN content for:
- ❌ "regtech" — not regtech positioning
- ❌ "compliance software" framing as primary identity — not regtech
- ❌ Internal acronyms: "RIA", "GDA" — use full product names
- ❌ Prescriptive language: "you must", "you should" without reasoning
- ❌ Outdated tech references: "WooCommerce", "cart", "checkout" in WP context

### Claim Validation
For each data point used:
1. Is it in the "Supported claims" table from Phase 6?
2. If yes: continue
3. If unlisted: flag as **Unverified** and ask user
4. Explicitly forbid: "Regulatory gaps are the most expensive mistakes" (unsupported claim)

### Terminology Check
- Product names spelled correctly: "Regulatory Intelligence" (not "Regulatory Intelligence Assistant"), "Generative Design", "Deployment Assistant"
- AquaForge is one word (not "Aqua Forge")

**Output:** Validation report — flags all issues. Fix issues before presenting to user.

**Approval gate:** User reviews EN content + validation report. User approves or requests revisions.

---

## Phase 4: FR Translation

**Goal:** Quebec-aware French translation for all EN content.

**Process:**
1. Translate each EN content block to French
2. **Quebec-specific adaptations:**
   - Use Quebec French conventions (not European French) where there are differences
   - Prefer Quebec regulatory references where relevant (MDDELCC, MELCCFP)
   - Avoid anglicisms where clean French alternatives exist
3. Keep these in English in both versions:
   - "AquaForge" (brand name)
   - "Regulatory Intelligence", "Generative Design", "Deployment Assistant" (product names)
4. Match EN length discipline in French (adjust word count for French verbosity)
5. Preserve data points verbatim (numbers, sources)

**Output:** `docs/content/{page-slug}.fr.md`

**Approval gate:** User reviews FR content. User approves or requests revisions.

---

## Phase 5: Asset List

**Process:**
For each content block, identify required media assets:
- Photos (facilities, advisors, etc.)
- Screenshots (product UI)
- Schematics (process flow diagrams)
- Icons
- Custom illustrations

For each asset:
- Description
- Sourcing method (stock library, AI-generated, LinkedIn profile, custom)
- Status (needed, available, uploaded)

**Output:** `docs/content/{page-slug}.assets.md`

---

## Phase 6: Publish to WordPress

**Two methods:**

### Method A: WP REST API (preferred if WP app password available)

```python
import requests
from requests.auth import HTTPBasicAuth

env = load_env()
wp_url = env['STAGING_URL']
auth = HTTPBasicAuth(env['WP_USER'], env['WP_APP_PASSWORD'])

# Update EN page
page_data = {
    'content': render_blocks_to_html('docs/content/{page-slug}.en.md'),
    'status': 'publish'
}
requests.post(f"{wp_url}/wp-json/wp/v2/pages/{page_id}", json=page_data, auth=auth)

# Update FR translation via WPML API
# ... (WPML-specific endpoint)
```

### Method B: Output Files for Manual Paste

If no WP app password:
1. Generate HTML-formatted content files: `docs/content/{page-slug}.en.html`, `docs/content/{page-slug}.fr.html`
2. Provide clear instructions to user for pasting into WP admin

**Approval gate:** User visually reviews staging:
- `{STAGING_URL}/en/{page-path}/`
- `{STAGING_URL}/fr/{page-path-fr}/`

User approves or requests revisions.

---

## Output Summary

After completion:

1. `docs/content/{page-slug}.en.md` — Final EN content
2. `docs/content/{page-slug}.fr.md` — Final FR content
3. `docs/content/{page-slug}.assets.md` — Asset checklist
4. WordPress pages updated on staging (both EN + FR)
5. Git commit: `content({page-slug}): EN + FR content published`

---

## Constraints

- **Bilingual parity.** EN and FR must contain the same data points, the same CTAs, the same structure. Only language differs.
- **Never invent data.** Every number, percentage, dollar amount must trace to a source in the supported claims table.
- **Tone consistency.** The same voice runs across every page: confident, precise, pragmatic, descriptive.
- **Respect asset sourcing.** Do not add placeholder images that imply the product has features it doesn't.
- **Translate, don't localize deeply.** Quebec nuance is about language, not repositioning — the product, personas, and value proposition stay consistent EN/FR.
