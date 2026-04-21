# Frontend Architecture Overview

## Purpose

{High-level description of the frontend application. What it does, who it serves, design philosophy.}

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | {React, Vue, etc.} | {UI rendering} |
| Build Tool | {Vite, Webpack, etc.} | {bundling, dev server} |
| Styling | {Tailwind, CSS Modules, etc.} | {styling approach} |
| Components | {shadcn/ui, MUI, etc.} | {component library} |
| State | {React Query, Redux, etc.} | {state management} |
| Routing | {React Router, etc.} | {client-side routing} |

## Application Layout

{High-level layout description: panels, navigation, responsive behavior.}

## Key Design Principles

- {Principle 1: e.g., Thin UI / thick API — minimal business logic in frontend}
- {Principle 2: e.g., engineer-friendly — clean, data-dense, no visual clutter}
- {Principle 3}

## Authentication Flow

{How auth works from the frontend perspective: OIDC redirect, token storage, API header injection.}

## API Communication

{How frontend communicates with the API gateway: fetch, axios, React Query, etc.}

## Related Documentation

- [System Architecture](../05-building-blocks.md) — Where frontend fits in the system
- [Frontend Structure](structure.md) — Component hierarchy and file organization
- [Frontend Patterns](patterns.md) — Coding patterns and conventions
- [Frontend ADRs](adr/) — Frontend-specific architecture decisions
- [UX Workflows](../../product/reference/ux-workflows.md) — User-facing workflows
- [APIs & Integrations](../../product/reference/apis-integrations.md) — API contract
