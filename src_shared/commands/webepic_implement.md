---
name: webepic_implement
description: Implement website epic story-by-story. Writes PHP/CSS/block files, deploys to staging via SFTP, runs visual/functional verification.
args: "{epic-id}"
skills: project-documentation
---

# /webepic_implement

Implement a refined website epic story-by-story. Each story: write files → SFTP to staging → verify → commit → move to next.

**Syntax:** `/webepic_implement {epic-id}`

## Prerequisites

- `docs/epics/{epic-id}/acceptance-criteria.md` exists
- `docs/epics/{epic-id}/architecture.md` exists
- `docs/epics/{epic-id}/file-plan-story-*.yaml` exists
- Epic status: `ready-for-implementation`
- `.env` file contains SFTP credentials for staging
- Git repo is clean (no uncommitted changes) OR on a dedicated branch
- **Verification tooling installed locally:**
  - `php` (>= 8.0) for lint checks
  - `composer` + WordPress Coding Standards: `composer require --dev wp-coding-standards/wpcs dealerdirect/phpcodesniffer-composer-installer`
  - `stylelint` + config: `npm install --save-dev stylelint stylelint-config-standard`
  - `jq` for JSON validation
  - `curl` for runtime checks (standard)
  - (optional) Playwright for headless browser checks

On first run, the command will check for these tools and halt if any are missing, with install instructions.

---

## Execution Model

Sequential story implementation:

```
For each story in dependency order:
  1. Load file plan (YAML)
  2. Write/modify files locally in theme/aquaforge-child/
  3. SFTP deploy changed files to staging
  4. Run automated verification (lint, link check, curl)
  5. Present staging URL to user for visual review
  6. User approves → git commit → next story
  7. User flags issue → fix → re-deploy → re-verify
```

**No parallel stories.** One story at a time. Deployments are serialized.

---

## Per-Story Workflow

### Step 1: Load Story

Read `docs/epics/{epic-id}/file-plan-story-{NN}.yaml`.
Display to user: story title, files affected, acceptance criteria.

### Step 2: Write Files Locally

For each file in `files_to_create` or `files_to_modify`:
- Write the file to `theme/aquaforge-child/` (or wherever the file_plan specifies)
- Follow the intent as described in the file plan
- Respect positioning constraints from PRD (no regtech, no unsourced claims, etc.)

### Step 3: Deploy to Staging

Use SFTP to push changed files to staging:

```python
# Deploy script pattern (uses paramiko + .env)
import paramiko, os

env = load_env()
transport = paramiko.Transport((env['SFTP_HOST'], int(env['SFTP_PORT'])))
transport.connect(username=env['SFTP_USER'], password=env['SFTP_PASS'])
sftp = paramiko.SFTPClient.from_transport(transport)

# Only upload changed files (not full theme)
for file in changed_files:
    remote = f"{env['STAGING_FOLDER']}/wp-content/themes/aquaforge-child/{file}"
    sftp.put(f"theme/aquaforge-child/{file}", remote)

sftp.close()
transport.close()
```

### Step 4: Automated Verification

Run these checks in order before asking for user review. Failure at any layer blocks progression until fixed.

#### Layer A: Static Code Checks (before deploy)

| Check | Command | Must pass |
|-------|---------|-----------|
| **PHP lint** | `php -l {file}` on every modified PHP file | No syntax errors |
| **PHPCS (WordPress standards)** | `vendor/bin/phpcs --standard=WordPress {file}` | No errors (warnings allowed with justification) |
| **Stylelint** | `npx stylelint {file}.css` | No errors |
| **JSON validation** | `jq empty {file}.json` on block.json, theme.json | Valid JSON |
| **Security pattern scan** | grep for dangerous patterns (see below) | No matches |

**Dangerous pattern scan (fails build):**
```bash
# SQL injection risks
grep -rn "\$wpdb->query.*\$_\(GET\|POST\|REQUEST\)" theme/aquaforge-child/
# Direct superglobal output
grep -rn "echo.*\$_\(GET\|POST\|REQUEST\|COOKIE\)" theme/aquaforge-child/
# Dangerous eval
grep -rn "eval\s*(" theme/aquaforge-child/
# Unescaped URL output
grep -rn "echo.*\$.*url" theme/aquaforge-child/ | grep -v "esc_url"
# Missing nonce on form actions
grep -rn "wp_nonce" theme/aquaforge-child/ | wc -l  # should be > 0 if forms exist
```

#### Layer B: Deploy + Runtime Checks (after deploy to staging)

| Check | Command | Must pass |
|-------|---------|-----------|
| **Staging HTTP 200** | `curl -s -o /dev/null -w "%{http_code}" {STAGING_URL}/{affected-url}` | Returns 200 (or 404 intentionally) |
| **No PHP errors in output** | `curl -s {STAGING_URL}/{url} \| grep -iE "fatal error\|warning\|notice\|deprecated"` | No matches |
| **No console errors** | Playwright headless check | No console errors |
| **Link check** | Crawl internal links via `curl -sI`, check for 404s | No broken links |
| **Page weight** | `curl -s -w "%{size_download}" {STAGING_URL}/{url}` | < 500KB HTML |
| **Bilingual parity** | Verify both `/en/{url}/` and `/fr/{url}/` return 200 | Both load |

#### Layer C: Custom Block Snapshot Tests (for block stories)

When a story creates or modifies a custom block or block pattern:

| Check | Command | Must pass |
|-------|---------|-----------|
| **Block renders** | `curl -s {STAGING_URL}/en/{test-page}/ \| grep -A 20 "wp-block-aquaforge-{block-name}"` | Renders expected HTML structure |
| **Snapshot match** | Compare block output to `tests/snapshots/{block-name}.html` | Matches or documented diff |
| **Block attributes preserved** | Verify custom attributes render in output | Attributes present |

Snapshots are simple HTML files in `tests/snapshots/`. On first render, save output. On subsequent stories, diff against snapshot. User approves any diffs during Step 5 review.

#### Layer D: Accessibility Spot-Checks (for page stories)

| Check | Command | Must pass |
|-------|---------|-----------|
| **Headings structure** | Parse headings from curl output, verify no skips (h1→h3) | Proper hierarchy |
| **Alt text presence** | Count `<img>` without `alt=` | Zero |
| **Form labels** | Verify all `<input>` have associated `<label>` | All labeled |
| **Color contrast** | (manual or axe-core via Playwright on sample page) | WCAG AA pass |

#### Verification Summary

After all layers run, present to user:
```
Verification for story {NN}:
Layer A (Static): ✅ 5/5 passed
Layer B (Runtime): ✅ 6/6 passed
Layer C (Blocks): ✅ 2/2 passed (snapshot updated for {block})
Layer D (A11y): ⚠ 3/4 passed (color contrast: user review needed)

Ready for visual review on: {STAGING_URL}/{affected-urls}
```

### Step 5: User Visual Review

Present to user:
- Staging URL(s) to review
- Specific acceptance criteria from the story file plan
- "Please review on staging and confirm or flag issues"

### Step 6: Commit or Fix

**If user approves:**
```bash
git add theme/aquaforge-child/[changed-files]
git commit -m "feat({epic-id}): story {NN} — {title}

Story: {story description}

Acceptance criteria:
- {criterion 1}
- {criterion 2}

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

**If user flags issue:**
- Understand the issue
- Fix locally
- Re-deploy to staging
- Re-verify
- Re-present

### Step 7: Update Story Status

Update `docs/epics/{epic-id}/implementation-summary.md` with story completion.

Proceed to next story.

---

## Epic Completion

After all stories complete:

1. **Full epic verification:**
   - Crawl all affected pages on staging
   - Run PageSpeed on homepage + affected pages
   - Check accessibility (automated axe-core check if possible)
   - Verify bilingual parity (EN + FR pages both load)

2. **Summary report to user:**
   - Stories completed
   - Pages affected
   - Performance scores
   - Remaining issues (if any)

3. **User decision:**
   - Proceed to next epic, or
   - Push staging to production (manual via 10web dashboard)

---

## Failure Handling

**SFTP deploy fails:**
- Retry with exponential backoff (10web can rate-limit)
- If still failing after 3 attempts, report to user

**Automated verification fails:**
- Report specific failure (HTTP code, error message, broken link)
- Fix in local files
- Re-deploy
- Re-verify

**User rejects after visual review:**
- Understand specific feedback
- Update file(s)
- Re-deploy + re-verify
- Re-present
- Do not force-commit

**More than 3 rejection cycles on one story:**
- Stop. Ask user to clarify requirement.
- May indicate story scope or acceptance criteria need revision.

---

## Constraints

- **One story at a time.** No parallel deploys.
- **Commit per approved story.** Clean git history, easy rollback.
- **Never auto-push to production.** User triggers manual staging→prod push via 10web.
- **Respect positioning constraints.** Every content output checked against `docs/website-strategy/phase-6-content-briefs.md` supported claims table.
- **.env is never committed.** SFTP credentials stay local.
