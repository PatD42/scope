# Frontend Structure

## Directory Layout

```
services/frontend/
├── src/
│   ├── components/     # Reusable UI components
│   │   ├── ui/         # Base components (shadcn/ui)
│   │   └── {feature}/  # Feature-specific components
│   ├── pages/          # Route-level page components
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API client and data fetching
│   ├── stores/         # State management
│   ├── utils/          # Utility functions
│   ├── types/          # TypeScript type definitions
│   └── assets/         # Static assets (icons, images)
├── public/             # Static public files
├── tests/              # Test files (mirrors src/ structure)
└── {config files}      # vite.config, tsconfig, tailwind, etc.
```

## Component Hierarchy

{Tree view showing how major components nest. Start from App → Layout → Pages → Feature Components.}

```
App
├── AuthProvider
│   └── Layout
│       ├── {Navigation}
│       └── {Page Routes}
│           ├── {Page A}
│           │   ├── {Component 1}
│           │   └── {Component 2}
│           └── {Page B}
```

## Route Map

| Route | Page Component | Purpose | Auth Required |
|-------|---------------|---------|---------------|
| {path} | {Component} | {what user sees} | {Yes/No} |

## Key Components

### {Component Name}
**Location:** `src/components/{path}`
**Props:** {key props}
**State:** {what state it manages}
**API Calls:** {which endpoints it uses}

## Related Documentation

- [Frontend Overview](overview.md) — Technology stack and principles
- [Frontend Patterns](patterns.md) — Coding conventions
- [UX Workflows](../../product/reference/ux-workflows.md) — User flows this implements
