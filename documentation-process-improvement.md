# Documentation Process Improvement

**Date**: 2026-01-31
**Status**: Analysis Complete

---

## Problem Statement

The documentation process is **open loop** - epics generate documentation during refinement, but permanent architecture docs (`docs/architecture/`) are not updated to reflect implementation reality.

---

## Current Tooling

### What `/update_spec` Covers

| Covered | Directory | Description |
|---------|-----------|-------------|
| ✅ | `13-specs/api/` | OpenAPI contracts |
| ✅ | `13-specs/schemas/domain/` | JSON Schema entities |
| ✅ | `13-specs/database/` | DB schema definitions |
| ✅ | `13-specs/errors/` | Error codes and taxonomy |

### Related Skills

- `spec-merger` - Proposes error taxonomy merges (with approval)
- `spec-validator` - Validates specs for correctness

---

## What's NOT Covered (The Gap)

| Not Covered | Files | Problem |
|-------------|-------|---------|
| **Arc42 docs** | `01-intro.md` through `12-glossary.md` | Never updated after initial creation |
| **ADR migration** | Epic ADRs → `docs/architecture/ADR/` | ADRs stay in epic folder, never merged |
| **Component docs** | `05-building-blocks.md` | References deleted modules |
| **Data models** | `DATA-MODELS.md` | Shows outdated field counts |
| **Cross-cutting** | `08-cross-cutting/*.md` | May reference old patterns |
| **Redundant files** | `ARCHITECTURE.md`, `DATA-MODELS.md`, `ERROR-HANDLING.md` | Duplicate info, drift separately |

---

## Document Classification

### Permanent (Canonical)

| Location | Purpose | Update Frequency |
|----------|---------|------------------|
| `docs/product/` | PRD, business requirements | When product scope changes |
| `docs/architecture/` | Arc42 structure, ADRs, specs | After each epic completes |

### Temporary (Working Documents)

| Location | Purpose | Lifecycle |
|----------|---------|-----------|
| `docs/epics/` | Epic refinement, acceptance criteria | Created during refinement, archived after completion |

---

## Recommendations to Close the Loop

### 1. New Command: `/update_architecture`

```bash
/update_architecture {section} {action}

# Examples:
/update_architecture adr merge {epic_id}     # Merge epic ADRs to ADR/
/update_architecture building-blocks sync    # Update 05-building-blocks.md from src/
/update_architecture models sync             # Update DATA-MODELS.md from dataclasses
```

**Sections to support:**
- `adr` - Merge ADRs from completed epics
- `building-blocks` - Sync component descriptions with `src/` structure
- `models` - Sync data models with actual dataclasses
- `intro` - Update capabilities and stakeholders

### 2. ADR Migration Step in Epic Completion

When epic status changes to `completed`:

1. Read `docs/epics/{epic}/adr.md`
2. Extract individual ADRs
3. Assign next ADR numbers (continue from last in `ADR/`)
4. Create files in `docs/architecture/ADR/ADR-NNN-*.md`
5. Update `ADR/README.md` index table
6. Update `09-adr-summary.md` with summaries

### 3. Delete Redundant Files

| Delete | Reason |
|--------|--------|
| `ARCHITECTURE.md` | Duplicates arc42 structure (01-12 files) |
| `DATA-MODELS.md` | Duplicates `13-specs/schemas/` |
| `ERROR-HANDLING.md` | Duplicates `13-specs/errors/` |

Keep only arc42 numbered files as canonical source.

### 4. Doc Drift Detection

Add validation script (can be run manually or in CI):

```bash
#!/bin/bash
# Check for module references in docs that don't exist in src/

echo "Checking for documentation drift..."

# Extract Python module references from docs
grep -roh "src/[a-z_/]*\.py" docs/architecture/ 2>/dev/null | sort -u | while read ref; do
    if [ ! -f "$ref" ]; then
        echo "DRIFT: $ref referenced in docs but not found"
    fi
done

# Check for class references
grep -roh "class [A-Z][a-zA-Z]*" docs/architecture/*.md 2>/dev/null | \
    sed 's/class //' | sort -u | while read class; do
    if ! grep -rq "class $class" src/; then
        echo "DRIFT: class $class referenced in docs but not found in src/"
    fi
done
```

---

## Residual Improvements for This Project

| Priority | Task | Files Affected |
|----------|------|----------------|
| 1 | Delete redundant docs | `ARCHITECTURE.md`, `DATA-MODELS.md`, `ERROR-HANDLING.md` |
| 2 | Update `05-building-blocks.md` | Remove deleted modules, add current structure |
| 3 | Merge ADRs 008-024 from epics | Create `ADR-008.md` through `ADR-024.md` in `ADR/` |
| 4 | Update `09-adr-summary.md` | Add all merged ADRs |
| 5 | Fix `01-intro.md` | Update stakeholders, capabilities for current state |
| 6 | Add Epic-006 ADRs | ADR-025 through ADR-032 when epic completes |

---

## Process Changes

### Before (Open Loop)

```
Epic Refinement → Epic Docs Created → Implementation → Code Changes
                                                            ↓
                                              (docs/architecture unchanged)
```

### After (Closed Loop)

```
Epic Refinement → Epic Docs Created → Implementation → Code Changes
                                                            ↓
                                              Epic Completion Trigger
                                                            ↓
                                              /update_architecture adr merge
                                                            ↓
                                              /update_architecture building-blocks sync
                                                            ↓
                                              docs/architecture updated
```

---

## Implementation Priority

1. **Immediate**: Delete redundant files (prevents further drift)
2. **Short-term**: Manual update of building-blocks and ADRs for past epics
3. **Medium-term**: Create `/update_architecture` command
4. **Long-term**: Add drift detection to CI pipeline
