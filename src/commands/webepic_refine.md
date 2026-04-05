---
name: webepic_refine
description: Refine a website epic into stories and file plans. Lightweight adaptation of epic_refine for WordPress/theme work (PHP templates, CSS, block patterns, WPML strings).
args: "{epic-id}"
skills: project-documentation
---

# /webepic_refine

Refine a website epic into implementable stories with file plans. No Python contracts, no mypy — staging is the integration test.

**Syntax:** `/webepic_refine {epic-id}`

## Prerequisites

- `docs/epics/{epic-id}/details.md` exists (epic brief with scope)
- PRD approved: `docs/website-strategy/website_prd.md`
- Phase 5-7 deliverables in `docs/website-strategy/`

---

## Workflow (3 Approval Gates)

```
Phase 1: Acceptance Criteria         → GATE #1 (user approves)
Phase 2: Architecture & File Layout   → GATE #2 (user approves)
Phase 3: Story Breakdown + File Plans → GATE #3 (user approves)
Mark epic "ready-for-implementation"
```

---

## Phase 1: Acceptance Criteria

**Goal:** Define testable acceptance criteria for the epic. Acceptance criteria for website work are **visual + functional**, not unit-test-based.

**Inputs:**
- `docs/epics/{epic-id}/details.md`
- Referenced pages from Phase 5 IA (sitemap, page specs)
- Referenced content briefs from Phase 6
- Capability mapping from Phase 7 (what's native vs custom)

**Process:**
1. Load epic details
2. Identify affected pages and components from Phase 5/6
3. Draft acceptance criteria in the form:
   - **Visual:** "Homepage hero displays 4 lifecycle tabs (Bid, Comply, Design, Build) on desktop and mobile"
   - **Functional:** "Clicking 'Subscribe' button on Pricing page navigates to app.aquaforge.ai/subscribe?tier=quick-check"
   - **Bilingual:** "EN and FR versions of page load with correct URLs and translated content"
   - **Performance:** "Page scores 85+ on PageSpeed mobile"
   - **Accessibility:** "All interactive elements reachable via keyboard; images have alt text"
4. Include positioning constraint checks where applicable: "Hero does not use 'regtech' framing"

**Deliverable:** `docs/epics/{epic-id}/acceptance-criteria.md`

```markdown
# {Epic Title} — Acceptance Criteria

## Scope
[Pages/components in this epic]

## Visual Criteria
- [ ] [Specific visual requirement]

## Functional Criteria
- [ ] [Specific behavior requirement]

## Bilingual Criteria
- [ ] [EN/FR parity requirement]

## Performance Criteria
- [ ] PageSpeed mobile ≥ 85
- [ ] LCP < 2.5s

## Accessibility Criteria
- [ ] Keyboard navigation works
- [ ] Alt text on all images
- [ ] WCAG 2.1 AA color contrast

## Positioning Constraint Checks
- [ ] No "regtech" framing
- [ ] No unsourced claims
- [ ] No internal acronyms (RIA, GDA)
- [ ] Descriptive (not prescriptive) tone

## Code Quality Criteria (for epics with PHP/CSS/JS)
- [ ] PHP files pass WordPress Coding Standards (WPCS via PHPCS)
- [ ] No PHP notices, warnings, or deprecated function calls
- [ ] CSS passes stylelint (no !important abuse, no undefined variables)
- [ ] All user input sanitized, all output escaped
- [ ] Nonces used on all form submissions and state-changing actions
- [ ] Capability checks (`current_user_can()`) on all admin actions

## Security Criteria (for epics with user-facing forms or dynamic content)
- [ ] No `eval()`, no `unserialize()` on untrusted data
- [ ] No direct `$_GET`/`$_POST` usage without sanitization
- [ ] No SQL built via string concatenation (use `$wpdb->prepare()`)
- [ ] External URLs escaped with `esc_url()`
- [ ] HTML attributes escaped with `esc_attr()`, output with `esc_html()` or `wp_kses()`

## Custom Block Criteria (for epics that add custom blocks or block patterns)
- [ ] Block JSON validates against `block.json` schema
- [ ] Block PHP render function returns valid HTML without errors
- [ ] Block renders correctly via `curl` snapshot test against staging
- [ ] Block variations for EN + FR (if applicable) use WPML translation functions
```

**Approval gate:** User validates acceptance criteria.

---

## Phase 2: Architecture & File Layout

**Goal:** Define the files (theme templates, CSS, block patterns, WPML strings) this epic will create or modify.

**Inputs:**
- Approved acceptance criteria from Phase 1
- Phase 7 capability mapping (what needs custom work vs configuration)

**Process:**
1. For each acceptance criterion, identify which file(s) implement it
2. Categorize work:
   - **Config only:** Blocksy Customizer settings (no files)
   - **Child theme CSS:** Additions to `theme/aquaforge-child/style.css` or new CSS files
   - **Child theme templates:** New or modified PHP files in `theme/aquaforge-child/`
   - **Block patterns:** New block pattern JSON/HTML files
   - **Custom Gutenberg blocks:** `theme/aquaforge-child/blocks/{name}/` with block.json + index.js + render.php
   - **WPML strings:** String registrations for translations
   - **Plugin config:** WP admin configuration steps
3. List external integrations touched (Attio, Stripe, GA4, Keycloak)

**Deliverable:** `docs/epics/{epic-id}/architecture.md`

```markdown
# {Epic Title} — Architecture

## Files to Create

### Child Theme Templates (PHP)
- `theme/aquaforge-child/{file}.php` — [purpose]

### CSS
- `theme/aquaforge-child/assets/css/{file}.css` — [purpose]

### Block Patterns
- `theme/aquaforge-child/patterns/{name}.php` — [purpose]

### Custom Blocks
- `theme/aquaforge-child/blocks/{name}/` — [purpose]

## Files to Modify
- `theme/aquaforge-child/functions.php` — [what's being added]
- `theme/aquaforge-child/style.css` — [what's being added]

## Configuration Steps (manual in WP admin)
- [Plugin/Customizer settings to configure]

## WPML String Registrations
- [Strings to register for translation]

## External Integrations
- [Attio form embed URL, Stripe redirect URL, GA4 event, etc.]
```

**Approval gate:** User validates architecture.

---

## Phase 3: Story Breakdown + File Plans

**Goal:** Break the epic into sequenced stories with file plans and acceptance criteria per story.

**Process:**
1. Group related files into stories (typical story = 1-4 files, 1-4 hours of work)
2. Define dependency order (e.g., "block pattern before page that uses it")
3. Per story, produce a file plan with:
   - Story ID and title
   - Files to create/modify
   - Intent (what the story accomplishes)
   - Dependencies on other stories
   - Acceptance criteria subset
   - Verification steps (visual review on staging, curl checks, etc.)

**Deliverable:** One YAML file per story in `docs/epics/{epic-id}/file-plan-story-{NN}.yaml`

```yaml
story_id: 01
story_title: "Register Case Study custom post type"
epic_id: "{epic-id}"
files_to_create:
  - path: theme/aquaforge-child/inc/cpt-case-study.php
    intent: "Register case-study CPT with product and segment taxonomies"
files_to_modify:
  - path: theme/aquaforge-child/functions.php
    intent: "Include cpt-case-study.php"
dependencies: []
acceptance_criteria:
  - "WP admin shows 'Case Studies' menu item"
  - "Taxonomies Product and Segment appear on edit screen"
  - "URLs follow /en/resources/case-studies/{slug}/ format"
verification:
  - "Visit WP admin → Case Studies menu appears"
  - "Create test case study → verify URL"
  - "Delete test case study after verification"
```

**Approval gate:** User validates story breakdown.

---

## Output

After all 3 gates approved, mark epic ready:

1. Update `docs/epics/{epic-id}/details.md` front matter: `status: ready-for-implementation`
2. Report summary to user: epic is ready for `/webepic_implement {epic-id}`

---

## Constraints

- **No code ceremony.** No Python contracts, no mypy, no TDD. Visual + functional verification only.
- **Staging is the integration test.** Every story verifies on `driving-firefly-dev.10web.cloud` (or equivalent).
- **Stories are small.** Prefer more small stories over fewer large ones. Rollback is easier.
- **Bilingual verification.** Every user-facing story must verify BOTH EN and FR output.
- **Respect positioning constraints.** Check before each story output.
