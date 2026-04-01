---
name: audit_epic
description: Audit epic implementation against original architecture and ADRs. Detects divergence and creates fix plan.
args: "{epic-id}"
skills: project-documentation
---

# /audit_epic

Audit an epic's implementation to detect divergence from original architecture, ADRs, and requirements. Produces a comprehensive audit report with prioritized fix plan.

**Syntax:** `/audit_epic {epic-id}`

**Output:** `docs/epics/{epic-dir}/epic_audit.md`

## When to Run

| Trigger | Use Case |
|---------|----------|
| After Auto Claude completes | Verify implementation matches design |
| Before merging to main | Gate check for architectural compliance |
| After discovering bugs | Determine if root cause is architectural drift |
| Periodic review | Quarterly audit of implemented epics |

---

## What Gets Audited

```
/audit_epic {epic-id}

SOURCES:
├── Our architecture: docs/epics/{epic-id}/architecture.md
├── Our ADRs: docs/epics/{epic-id}/adr.md
├── Acceptance criteria: docs/epics/{epic-id}/acceptance-criteria.md
├── Lint findings: docs/epics/{epic-id}/lint_findings.yaml (if exists)
├── Auto Claude spec: .auto-claude/specs/*/spec.md
└── Implemented code: .auto-claude/worktrees/tasks # The auto-claude ID is the same as the folder that has the relevant spec.md

AUDIT CHECKS:
├── 1. Architecture Compliance
│   ├── Components match design
│   ├── APIs match contracts
│   └── Data models match schemas
│
├── 2. ADR Compliance
│   ├── Technology decisions followed
│   ├── Patterns applied correctly
│   └── Constraints respected
│
├── 3. Acceptance Criteria
│   ├── All scenarios implemented
│   ├── Edge cases handled
│   └── Error scenarios covered
│
├── 4. Auto Claude Spec Alignment
│   ├── Spec matches our architecture
│   ├── Implementation matches spec
│   └── Test coverage as specified
│
├── 5. Code Quality
│   ├── Follows project patterns
│   ├── Error handling consistent
│   └── Documentation complete
│
├── 6. Stub/Placeholder Detection
│   ├── No placeholder/TODO/stub markers in production code
│   ├── Intent I/O verbs matched by real I/O in implementation
│   └── No functions returning literals without performing stated action
│
├── 7. Lint & Contract Compliance
│   ├── Ingest lint_findings.yaml (ruff + vulture + mypy from epic-wide check)
│   ├── Remaining ruff violations → MAJOR severity
│   ├── Dead code (vulture) → MAJOR severity
│   └── mypy --strict errors → CRITICAL severity (contract violations)
│
└── 8. Documentation Sync (Reverse Audit)
    ├── Do architecture docs reflect what was actually built?
    ├── Check: backend/data.md matches implemented schema
    ├── Check: backend/services.md matches implemented services
    ├── Check: 05-building-blocks.md includes new components
    ├── Check: 03-context.md reflects new external dependencies
    ├── Check: 08-cross-cutting/domain.md includes new domain entities
    ├── Check: 12-glossary.md includes new technical terms
    ├── Check: product/reference/terminology-data-model.md includes new terms
    ├── Check: product/decisions.md includes epic PDRs
    └── Check: 09-adr-summary.md includes epic ADRs

OUTPUT:
└── docs/epics/{epic-dir}/epic_audit.md
    ├── Executive summary
    ├── Findings by severity
    ├── Root cause analysis
    └── Prioritized fix plan
```

---

## Execution

### Step 0: Initialize

```bash
EPIC_ID="{epic-id}"
EPIC_DIR=$(ls docs/epics/ | grep -i "^${EPIC_ID}" | head -1)

if [ -z "$EPIC_DIR" ]; then
  echo "Epic not found in docs/epics/"
  exit 1
fi

AUDIT_FILE="docs/epics/${EPIC_DIR}/epic_audit.md"
```

### Step 1: Load Sources

```python
# Our design documents
architecture = Read(f"docs/epics/{epic_dir}/architecture.md")
adrs = Read(f"docs/epics/{epic_dir}/adr.md")
acceptance_criteria = Read(f"docs/epics/{epic_dir}/acceptance-criteria.md")

# Auto Claude spec
ac_spec = find_auto_claude_spec(epic_id)  # grep -l epic-id in .auto-claude/specs/*/spec.md

# Implementation
implemented_files = scan_implementation(epic_id)
```

---

## Audit Phase 1: Architecture Compliance

### 1.1 Component Verification

**Check:** Do implemented components match architecture design?

```python
# From architecture.md
designed_components = extract_components(architecture)
# Example: FileMapper, HierarchyBuilder, ConfigLoader

# From implementation
implemented_components = scan_src_structure()
# Example: file_mapper/, hierarchy/, config_manager/

# Compare
missing = designed_components - implemented_components
extra = implemented_components - designed_components
renamed = detect_renames(designed_components, implemented_components)
```

**Report:**
```markdown
### Component Compliance

✅ MATCHES (N components):
- FileMapper → src/file_mapper/ ✓
- HierarchyBuilder → src/hierarchy/ ✓

⚠️  DEVIATIONS (N issues):
- ConfigLoader → src/config_manager/ (renamed without ADR)
- Missing: FrontmatterHandler (designed but not implemented)
- Extra: src/utils/retry.py (implemented but not in design)
```

### 1.2 API Contract Verification

**Check:** Do APIs match architecture design?

```python
# From architecture.md API section
designed_apis = extract_api_endpoints(architecture)

# From implementation
implemented_apis = scan_api_routes(src_dir)

# From 13-specs
spec_apis = parse_openapi(f"docs/architecture/13-specs/api/")

# Three-way comparison
api_audit = compare_apis(designed_apis, spec_apis, implemented_apis)
```

**Report:**
```markdown
### API Contract Compliance

✅ MATCHES:
- GET /api/sync-status (design → spec → implementation) ✓

⚠️  DEVIATIONS:
- POST /api/force-sync: Missing required field "direction" (spec has it, code doesn't)
- GET /api/config: Returns 200 instead of designed 201 for new configs
```

### 1.3 Data Model Verification

**Check:** Do data models match schemas?

```python
# From architecture.md
designed_models = extract_data_models(architecture)

# From implementation
implemented_models = scan_dataclasses_and_models(src_dir)

# From docs/architecture/13-specs/schemas
spec_schemas = parse_json_schemas(f"docs/architecture/13-specs/schemas/domain/")

# Compare
model_audit = compare_models(designed_models, spec_schemas, implemented_models)
```

**Report:**
```markdown
### Data Model Compliance

✅ MATCHES:
- PageNode: All fields match schema ✓

⚠️  DEVIATIONS:
- SyncConfig: Added field "retry_count" (not in schema or design)
- LocalPage: Missing field "last_modified" (in schema, not in code)
```

---

## Audit Phase 2: ADR Compliance

### 2.1 Technology Decisions

**Check:** Were ADR technology selections followed?

```python
adrs_list = parse_adrs(adrs)

for adr in adrs_list:
    decision = adr['decision']
    # Check if decision was implemented correctly
    compliance = verify_adr_implementation(adr, src_dir)
```

**Report:**
```markdown
### ADR Compliance

✅ ADR-008: CQL-based page discovery
   Implementation: Using CQL queries ✓
   Limit: 100 pages enforced ✓

❌ ADR-010: Filesafe conversion with case preservation
   VIOLATION: Implementation converts to lowercase only
   Location: src/file_mapper/filesafe_converter.py:15
   Impact: CRITICAL - Data loss for case-sensitive titles

⚠️  ADR-011: Atomic file operations (two-phase commit)
   PARTIAL: Two-phase commit implemented, but no rollback on failure
   Location: src/file_mapper/file_mapper.py:45-60
   Impact: MAJOR - Could leave partial state on error
```

### 2.2 Pattern Compliance

**Check:** Were architectural patterns applied correctly?

```python
# From ADRs and cross-cutting docs
required_patterns = extract_patterns(adrs)
# Example: Exception hierarchy, dataclass pattern, module organization

# From implementation
implemented_patterns = analyze_code_patterns(src_dir)

# Compare
pattern_audit = verify_patterns(required_patterns, implemented_patterns)
```

**Report:**
```markdown
### Pattern Compliance

✅ Exception Hierarchy Pattern:
   All exceptions inherit from ConfluenceError ✓
   Typed exception parameters ✓

⚠️  Dataclass Pattern:
   DEVIATION: SyncConfig uses dict instead of @dataclass
   Location: src/file_mapper/models.py:25
   Impact: MINOR - Inconsistent with project pattern
```

---

## Audit Phase 3: Acceptance Criteria

### 3.1 Scenario Coverage

**Check:** Are all acceptance criteria scenarios implemented and tested?

```python
acceptance_scenarios = parse_acceptance_criteria(acceptance_criteria)

for scenario in acceptance_scenarios:
    # Check implementation
    implemented = find_implementation(scenario, src_dir)
    # Check tests
    tested = find_tests(scenario, tests_dir)

    scenario_audit.append({
        'scenario': scenario,
        'implemented': implemented,
        'tested': tested
    })
```

**Report:**
```markdown
### Acceptance Criteria Coverage

✅ AC-1: Filesafe Filename Conversion
   Implemented: ✓
   Tested: ✓
   Coverage: 95%

❌ AC-6: Initial Sync Direction
   Implemented: ✗ (forcePull/forcePush flags missing)
   Tested: ✗
   Impact: CRITICAL - Core requirement not implemented

⚠️  AC-8: Exclusion Patterns
   Implemented: ✓
   Tested: Partial (only unit tests, no E2E)
   Impact: MINOR - Missing E2E test coverage
```

### 3.2 Edge Case Handling

**Report:**
```markdown
### Edge Case Coverage

✅ Malformed frontmatter: Error handling implemented ✓
✅ Network failure: APIUnreachableError raised ✓
❌ 100 page limit: No error message, silent truncation
   Impact: MAJOR - Users won't know why pages missing
```

---

## Audit Phase 4: Auto Claude Spec Alignment

### 4.1 Spec vs Architecture

**Check:** Does Auto Claude's spec align with our architecture?

```python
ac_spec_components = extract_components_from_spec(ac_spec)
our_components = extract_components(architecture)

spec_alignment = compare_components(ac_spec_components, our_components)
```

**Report:**
```markdown
### Auto Claude Spec Alignment

✅ Auto Claude spec references our architecture ✓
✅ ADR references match (ADR-008 through ADR-015) ✓

⚠️  SPEC DEVIATION:
   Auto Claude spec added: DirectoryScanner
   Not in our architecture.md
   Reason: Auto Claude optimization for performance
   Impact: MINOR - Enhancement not breaking change
```

### 4.2 Spec vs Implementation

**Check:** Did implementation follow Auto Claude's spec?

```python
spec_requirements = extract_requirements(ac_spec)
implementation_features = scan_implementation_features(src_dir)

spec_compliance = verify_spec_implementation(spec_requirements, implementation_features)
```

**Report:**
```markdown
### Spec Implementation Compliance

✅ All "Files to Modify" created ✓
✅ All "Patterns to Follow" applied ✓

❌ SUCCESS CRITERIA NOT MET:
   Spec requires: Unit test coverage >90%
   Actual: 75% coverage
   Impact: MAJOR - Quality gate not met
```

---

## Audit Phase 5: Code Quality

### 5.1 Pattern Consistency

**Report:**
```markdown
### Code Quality

✅ Follows project structure ✓
✅ Error handling consistent ✓

⚠️  DEVIATIONS:
- Missing docstrings: 15 functions
- Hardcoded config values: 3 instances (should be in YAML)
  Impact: MINOR - Maintainability issue
```

---

## Audit Phase 6: Stub/Placeholder Detection

**Check:** Does every implementation file actually perform what its file plan intent describes?

```python
for story_plan in file_plans:
    for file_entry in story_plan["files_to_create"] + story_plan["files_to_modify"]:
        path = file_entry["path"]
        intent = file_entry["intent"]
        code = Read(path)

        # 1. Search for stub markers in production code
        stub_markers = ["# Placeholder", "# TODO", "# Stub", "# Mock",
                        "NotImplementedError", "pass  #", "hardcoded"]
        for marker in stub_markers:
            if marker.lower() in code.lower():
                report_finding(severity="CRITICAL", file=path, marker=marker)

        # 2. Check intent vs implementation for I/O verbs
        io_verbs = ["sends", "calls", "queries", "uploads", "downloads",
                    "writes to", "reads from", "posts", "fetches", "connects"]
        intent_has_io = any(verb in intent.lower() for verb in io_verbs)

        if intent_has_io:
            # Verify code contains actual I/O (HTTP client, DB driver, file ops)
            has_real_io = contains_io_operations(code)  # requests, httpx, aiohttp, fetch, db.execute, etc.
            if not has_real_io:
                report_finding(
                    severity="CRITICAL",
                    file=path,
                    issue=f"Intent says '{extract_io_verb(intent)}' but implementation contains no I/O code",
                    expected="Production code with real API/DB/network calls",
                    actual="Function returns hardcoded/literal values or delegates to mocks"
                )

        # 3. Check for functions that return literals without performing their stated purpose
        for func in extract_functions(code):
            if func.returns_literal and func.name_implies_action:
                report_finding(
                    severity="MAJOR",
                    file=path,
                    issue=f"Function {func.name}() returns literal value without performing action",
                    impact="Tests pass via mocks but production code does nothing"
                )
```

**Report:**
```markdown
### Stub/Placeholder Detection

❌ CRITICAL: src/classification/llm_classifier.py
   Intent: "Sends first excerpt_chars of markdown to configured LLM model"
   Issue: No HTTP/API client call found in _call_llm()
   Actual: Returns hardcoded ClassificationResult
   Impact: CRITICAL - Core functionality is a stub

❌ CRITICAL: src/ingestion/feed_fetcher.py
   Issue: Contains "# TODO: implement retry logic"
   Impact: CRITICAL - Incomplete implementation

✅ src/models/document.py - No stubs detected
✅ src/utils/parser.py - No stubs detected
```

**Key rule:** A stub found in production code is ALWAYS severity CRITICAL, never minor. If the file plan says the code should do something and it doesn't, that's a failed implementation.

---

## Audit Phase 7: Lint & Contract Compliance

**Check:** Ingest epic-wide lint and contract findings and include them in the audit report.

```python
lint_findings_path = f"docs/epics/{epic_dir}/lint_findings.yaml"
if file_exists(lint_findings_path):
    lint_report = read_yaml(lint_findings_path)

    # Ruff violations that couldn't be auto-fixed
    for violation in lint_report.get("ruff_violations", []):
        report_finding(
            severity="MAJOR",
            file=violation["file"],
            issue=f"ruff: {violation['code']} - {violation['message']} (line {violation['line']})",
            impact="Code quality violation that couldn't be auto-fixed"
        )

    # Vulture dead code findings
    for finding in lint_report.get("vulture_dead_code", []):
        report_finding(
            severity="MAJOR",
            file=finding["file"],
            issue=f"vulture: unused {finding['type']} '{finding['name']}' (line {finding['line']})",
            impact="Dead code increases maintenance burden and may indicate incomplete refactoring"
        )

    # mypy contract violations
    for error in lint_report.get("mypy_errors", []):
        report_finding(
            severity="CRITICAL",
            file=error["file"],
            issue=f"mypy: {error['message']} (line {error['line']})",
            impact="Contract violation — implementation does not match Protocol interface. Cross-story calls will fail at runtime."
        )
```

**Report:**
```markdown
### Lint & Contract Compliance

❌ CRITICAL: src/documentation/intel_aggregator.py:23
   mypy: Argument 1 to "aggregate_for_section" has incompatible type "int"; expected "str"
   Impact: Contract violation — cross-story calls will fail at runtime

❌ MAJOR: src/classification/classifier.py:45
   ruff: F841 - Local variable 'result' is assigned but never used
   Impact: Code quality violation

❌ MAJOR: src/ingestion/feed_parser.py:12
   vulture: unused function 'parse_legacy_format' (line 12)
   Impact: Dead code from incomplete refactoring

✅ No lint/contract findings (lint_findings.yaml not present or empty)
```

**Note:** If `lint_findings.yaml` does not exist, the epic-wide checks passed cleanly — skip this phase. mypy errors are CRITICAL because they indicate implementations that don't match the Protocol contracts — these will cause runtime failures when stories integrate.

---

## Audit Phase 8: Documentation Sync (Reverse Audit)

**Purpose:** Phases 1-7 check "does code match docs?" (code ← docs). Phase 8 checks the reverse: **"do docs match code?"** (docs ← code). This catches stale documentation — docs that were accurate before implementation but are now outdated because implementation changed things.

**CRITICAL GOVERNANCE RULE:** Phase 8 produces **recommendations only**. It does NOT auto-fix documentation and does NOT create fix stories for doc updates. The user must review each recommendation and approve before any documentation is changed.

**Why human-in-the-loop:** If implementation diverged from the design, auto-updating docs to match the code would launder the divergence — the docs would now say "we planned this" when actually the implementation drifted. Only the user can decide whether:
- The code is correct and docs should be updated to reflect reality
- The code drifted and should be fixed to match the original design
- The divergence is intentional and should be recorded as a new ADR

### 8.1 What to Check

For each category, compare what the code actually does against what the docs say:

| Category | Document | Compare Against |
|----------|----------|----------------|
| Database schema | `backend/data.md` | Migration files, CREATE TABLE, schema.sql, Pydantic DB models |
| Services | `backend/services.md` | FastAPI apps, CLI entry points, new routers, workers |
| Building blocks | `05-building-blocks.md` | New components from file plans vs. what's documented |
| External dependencies | `03-context.md` | New cloud SDKs, API clients, DB drivers, Docker services |
| Domain entities | `08-cross-cutting/domain.md` | New Pydantic models, dataclasses, named domain concepts |
| Terminology | `12-glossary.md`, `terminology-data-model.md` | New terms in code not in glossary |
| ADR roll-up | `09-adr-summary.md` | Epic ADRs not yet in system summary |
| PDR roll-up | `product/decisions.md` | Epic PDRs not yet in product decisions |

### 8.2 Classify Each Finding

For each divergence found, classify:

```python
for finding in doc_sync_findings:
    finding.category = classify_divergence(finding)
    # Categories:
    # "planned_not_documented" — architect designed it, Story 0 should have updated docs but didn't
    # "implementation_drift"  — code diverged from design, unclear if intentional
    # "missing_doc"           — doc file doesn't exist at all (e.g., backend/data.md never created)
    # "rollup_pending"        — epic ADRs/PDRs not yet rolled up to system level
```

### 8.3 Present Recommendations to User

**Do NOT auto-fix. Present each finding as a recommendation for user approval.**

```markdown
### Documentation Sync — Recommendations for User Approval

Phase 8 found {N} documentation gaps. Each requires your decision.

┌────┬──────────┬──────────────────────────────────────────────────────────┐
│ #  │ Severity │ Finding                                                  │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 1  │ MAJOR    │ backend/data.md does not exist                           │
│    │          │ Code has 5 new tables (organizations, persons, etc.)     │
│    │          │ Was this planned? Should docs be created to match code?  │
│    │          │ Action: [create docs / code should be fixed / defer]     │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 2  │ MAJOR    │ 05-building-blocks.md missing PostgresClient             │
│    │          │ Component exists in code but not in architecture diagram │
│    │          │ Was this an intentional addition?                        │
│    │          │ Action: [update docs / code should be fixed / defer]     │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 3  │ MEDIUM   │ 03-context.md still shows SQLite only                    │
│    │          │ Code now uses PostgreSQL as primary database              │
│    │          │ This appears intentional (per epic architecture.md)      │
│    │          │ Action: [update docs / defer]                            │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 4  │ MEDIUM   │ 09-adr-summary.md missing 4 epic ADRs                   │
│    │          │ Epic adr.md has ADRs not yet in system summary           │
│    │          │ Action: [roll up now / defer to /wrap_epic]              │
├────┼──────────┼──────────────────────────────────────────────────────────┤
│ 5  │ MINOR    │ 12-glossary.md missing 11 new terms                     │
│    │          │ New terms: RLS, sagara, heartbeat, ...                   │
│    │          │ Action: [update glossary / defer]                        │
└────┴──────────┴──────────────────────────────────────────────────────────┘

For each finding, choose:
  [update docs]      — Docs should reflect the code (implementation is correct)
  [code should fix]  — Code diverged and should be fixed to match design
  [new ADR needed]   — Divergence is intentional, record as a new decision
  [defer]            — Handle later (in /wrap_epic or next epic)
```

### 8.4 Record User Decisions

For each finding the user approves:
- **"update docs"** → Record in audit report as approved doc update. The user (or `/wrap_epic`) will execute it. Do NOT have the developer agent update docs — that bypasses the architect's design authority.
- **"code should fix"** → Create a fix story (same as Phases 1-7 findings). This IS a code problem, not a doc problem.
- **"new ADR needed"** → Flag for `/decision` or `/wrap_epic` to record formally.
- **"defer"** → Record as deferred in audit report. Will be caught again by next audit or `/wrap_epic`.

**Key rule:** Documentation sync findings are MAJOR severity (not CRITICAL) because they don't break functionality, but they degrade the project's ability to make informed decisions in future epics. Stale docs are a compounding problem — each unfixed gap makes the next epic's architecture design less accurate.

---

## Issue Classification

All findings are classified by severity:

| Severity | Definition | Examples |
|----------|------------|----------|
| **CRITICAL** | Breaks core functionality or violates key ADR | Missing acceptance criteria, ADR violations causing data loss, stubs in production code |
| **MAJOR** | Significant deviation from design, or stale documentation | Partial ADR implementation, missing edge case handling, test coverage gaps, backend/data.md missing or stale, backend/services.md missing or stale, building-blocks.md not updated |
| **MEDIUM** | Documentation or tracking gaps | ADRs/PDRs not rolled up, context diagram outdated, missing external dependencies in docs |
| **MINOR** | Cosmetic or consistency issues | Naming inconsistencies, missing glossary terms, pattern deviations |
| **ENHANCEMENT** | Improvements not in original design | Performance optimizations, additional features |

---

## Audit Report Output

Write to: `docs/epics/{epic-dir}/epic_audit.md`

### Report Template

```markdown
# Epic Audit Report: {epic-id}

**Date**: {date}
**Auditor**: Claude Code
**Status**: {PASS / FAIL / PASS WITH CONDITIONS}

---

## Executive Summary

{2-3 sentence summary of audit outcome}

**Overall Compliance**: {percentage}%

**Critical Issues**: {N}
**Major Issues**: {N}
**Minor Issues**: {N}
**Enhancements**: {N}

**Recommendation**: {APPROVE / FIX CRITICAL / FIX ALL}

---

## Findings

### Critical Issues (Blocking)

#### 1. {Issue Title}
- **Category**: {Architecture / ADR / Acceptance Criteria}
- **Location**: {file:line}
- **Description**: {what's wrong}
- **Impact**: {why it matters}
- **Expected**: {what should be}
- **Actual**: {what was implemented}

### Major Issues (Should Fix)

{...}

### Minor Issues (Nice to Fix)

{...}

### Enhancements (Unexpected Improvements)

{...}

---

## Root Cause Analysis

**Why did divergence occur?**

1. {Root cause 1 - e.g., Auto Claude misinterpreted ADR}
2. {Root cause 2 - e.g., Architecture ambiguous on edge case}
3. {Root cause 3 - e.g., Implementation added feature not in design}

---

## Fix Plan

### Priority 1: Critical Fixes (BLOCKING)

| # | Issue | Fix | Effort | Files |
|---|-------|-----|--------|-------|
| 1 | AC-6 not implemented | Add forcePull/forcePush flags | 4h | file_mapper.py, config_loader.py |
| 2 | ADR-010 violated | Fix case preservation in filesafe converter | 2h | filesafe_converter.py |

**Total Effort**: 6 hours

### Priority 2: Major Fixes (Should Address)

| # | Issue | Fix | Effort | Files |
|---|-------|-----|--------|-------|
| 3 | ADR-011 partial | Add rollback on failure | 3h | file_mapper.py |
| 4 | Test coverage gap | Add E2E tests for AC-8 | 4h | tests/e2e/ |

**Total Effort**: 7 hours

### Priority 3: Minor Fixes (Optional)

| # | Issue | Fix | Effort | Files |
|---|-------|-----|--------|-------|
| 5 | Missing docstrings | Add docstrings to 15 functions | 2h | Various |
| 6 | Hardcoded config | Move to YAML files | 1h | config_loader.py |

**Total Effort**: 3 hours

---

## Compliance Scorecard

| Area | Score | Status |
|------|-------|--------|
| Architecture Compliance | 85% | ⚠️  Issues found |
| ADR Compliance | 70% | ❌ Critical violations |
| Acceptance Criteria | 75% | ❌ Missing scenarios |
| Auto Claude Spec | 95% | ✅ Mostly aligned |
| Code Quality | 90% | ✅ Good |
| **OVERALL** | **83%** | ⚠️  **PASS WITH CONDITIONS** |

---

## Recommendations

1. **IMMEDIATE**: Fix Critical issues (Priority 1) before merging
2. **SHORT-TERM**: Address Major issues (Priority 2) within 1 week
3. **LONG-TERM**: Clean up Minor issues (Priority 3) when convenient
4. **DOCUMENT**: Update architecture.md to include enhancements

---

## Next Steps

After reviewing this audit:

1. Decide which fixes to implement
2. Run `/audit_epic {epic-id}` again after fixes to verify
3. Once CRITICAL issues resolved, run `/sync_architecture {epic-id}`
4. Mark epic as "audit-passed" in tracking system

---

## Appendix: Detailed Findings

{Full detailed findings with code snippets, comparisons, etc.}
```

---

## Completion Flow

After generating audit report:

```
Audit Complete: {epic-id}

Report saved to: docs/epics/{epic-dir}/epic_audit.md

Summary:
├── Status: {PASS / FAIL / PASS WITH CONDITIONS}
├── Overall Compliance: {percentage}%
├── Critical Issues: {N}
├── Major Issues: {N}
└── Minor Issues: {N}

{If CRITICAL issues exist:}
⚠️  CRITICAL ISSUES FOUND - Blocking issues must be fixed

Fix Plan Summary:
├── Priority 1 (Critical): {N} issues, {X} hours estimated
├── Priority 2 (Major): {N} issues, {X} hours estimated
└── Priority 3 (Minor): {N} issues, {X} hours estimated

Implement fixes now? [yes / review report first / skip]
```

**If user says "yes":**
1. Start with Priority 1 (Critical) fixes
2. Implement each fix from the plan
3. Re-run audit to verify fixes
4. Repeat until Critical issues resolved

**If user says "review report first":**
- Display report location
- Wait for further instructions

**If user says "skip":**
- End command, report remains for manual review

---

## Re-Audit After Fixes

After implementing fixes:

```bash
/audit_epic {epic-id}
```

The audit will update the existing `epic_audit.md` with new findings, showing progress:

```markdown
## Audit History

### Audit #2 - {date}
Status: PASS ✅
Critical: 0 (was 2)
Major: 1 (was 4)
Minor: 2 (was 6)

### Audit #1 - {date}
Status: FAIL ❌
Critical: 2
Major: 4
Minor: 6
```

---

## Example Session

```
User: /audit_epic {epic-id}