# Epic File Plan: [Epic Title]

---

## Meta: Phase & Agent Information

**Phase**: Phase 2 - Architecture
**Agent Role**: Architect
**Created During**: Architecture Phase - After Architecture and ADR
**Prerequisites**: Architecture, ADR, System Context

---

## Context Dependencies

**Required Context (must exist before this document)**:
- [{epic-id}: Architecture](link) - Components, data model, APIs inform file structure
- [{epic-id}: ADR](link) - Technology decisions determine file patterns
- [{epic-id}: System Context](link) - Technology stack determines file types
- Product Reference: Existing codebase structure and conventions

**Provides Context For (documents that depend on this)**:
- Development Phase: Developers create/modify files per this plan
- [{epic-id}: Test Strategy](link) - Test files align with implementation files
- [{epic-id}: Implementation Summary](link) - Actual files created vs. planned

---

## Overview

<!-- This page maps out all files and directories affected by this epic. -->

<!-- Helps Developer understand the complete scope of file changes. -->

## New Files

<!-- Files that will be created by this epic. -->

| File Path | Purpose | Owner Story |
|-----------|---------|-------------|
| `src/` | | {story-id} |

### `src/path/to/file.ts`

**Purpose**:

**Key Components**:
-

**Dependencies**:
-

**Tests**: `tests/path/to/file.test.ts`

## Modified Files

<!-- Existing files that will be changed by this epic. -->

| File Path | Changes | Owner Story |
|-----------|---------|-------------|
| `src/` | | {story-id} |

### `src/path/to/existing-file.ts`

**Current State**:

**Planned Changes**:
-

**Affected Components**:
-

**Impact**:
-

## Deleted Files

<!-- Files that will be removed by this epic. -->

| File Path | Reason | Owner Story | Migration |
|-----------|--------|-------------|-----------|
| `src/` | | {story-id} | |

## Directory Structure

<!-- New or modified directory structure. -->

```
src/
├── feature/
│   ├── components/
│   │   ├── Component1.tsx
│   │   └── Component2.tsx
│   ├── services/
│   │   └── FeatureService.ts
│   ├── types/
│   │   └── types.ts
│   └── index.ts
└── ...
```

## Configuration Files

<!-- Configuration files affected by this epic. -->

| File | Changes | Environment |
|------|---------|-------------|
| `.env.example` | | All |
| `config/production.yaml` | | Production |

## Database Migrations

<!-- Database migration files for this epic. -->

| Migration File | Description | Applied To |
|---------------|-------------|------------|
| `migrations/YYYYMMDD_description.sql` | | Dev/Staging/Prod |

## Test Files

<!-- Test files for this epic. -->

| Test File | Covers | Type |
|-----------|--------|------|
| `tests/unit/` | | Unit |
| `tests/integration/` | | Integration |
| `tests/e2e/` | | E2E |

## Documentation Files

<!-- Documentation files affected by this epic. -->

| File | Changes |
|------|---------|
| `README.md` | |
| `docs/` | |

---

