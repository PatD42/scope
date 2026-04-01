## L-002: Audit was unidirectional — checked code against docs but not docs against code

**Date:** 2026-04-01
**Epic:** General (affects all epics with schema/service/component changes)
**Domain:** audit, documentation, architecture
**Severity:** Critical

### Pattern / Anti-Pattern

**Type:** Anti-Pattern (avoid this)

**Detection:** When /audit_epic completes and reports PASS, check: did the epic introduce new database tables, new services, new external dependencies, new domain entities, or new terminology? If yes, and the audit didn't flag any documentation gaps, the audit is missing Phase 8 (Documentation Sync).

**Rule:** Architecture audits must be bidirectional — verify code matches docs (Phases 1-7) AND docs match code (Phase 8). A passing audit with stale docs is a false positive.

### Root Cause

The /audit_epic command checked 7 areas (architecture compliance, ADR compliance, acceptance criteria, spec alignment, code quality, stub detection, lint compliance) but all were unidirectional: "does the code match what the docs say?" It never asked the reverse: "do the docs reflect what the code actually does?"

Result: An epic that added 5 new database tables, 4 new repositories, new external dependencies (PostgreSQL, Cloud Run), and 13 new domain terms passed the audit with zero documentation findings. The architect created docs during /epic_refine (before implementation) but nobody updated them after implementation diverged from the plan.

### Resolution

Three-part fix across the pipeline:

**1. /epic_refine (prevention):** Architect now produces a "Documentation Update Plan" during Phase 2 — a list of which architecture docs must be updated and what changes are needed. This is reviewed and approved by the user before implementation starts.

**2. /implement Story 0 (execution):** The architect's scaffolding story now includes executing the documentation update plan — updating product-level architecture docs (backend/data.md, 05-building-blocks.md, etc.) to reflect the DESIGNED architecture, BEFORE developer implementation begins. The developer must NOT update these docs to avoid laundering divergence.

**3. /audit_epic Phase 8 (detection):** New "Documentation Sync" audit phase checks if docs match code. But critically, it only produces RECOMMENDATIONS — it does NOT auto-fix docs. The user must decide for each finding:
- "update docs" — implementation is correct, docs should change
- "code should fix" — code diverged from design, fix the code
- "new ADR needed" — divergence is intentional, record as decision
- "defer" — handle later in /wrap_epic

This prevents the catch-22 of auto-updating docs to match divergent code, which would launder the drift and make it invisible.
