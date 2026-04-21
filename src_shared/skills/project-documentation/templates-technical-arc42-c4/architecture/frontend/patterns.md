# Frontend Patterns & Conventions

## Data Fetching

{How data is fetched: React Query, SWR, custom hooks, etc. Caching strategy. Error/loading state handling.}

## State Management

{Local state vs. global state. When to use each. State libraries if any.}

## Error Handling

{How errors are displayed to users. Global error boundary. API error mapping.}

## Authentication

{Token storage. Request interceptors. Protected routes. Logout flow.}

## Styling Conventions

{Tailwind class ordering. Component variants. Theme tokens. Responsive breakpoints.}

## TypeScript Conventions

{Strict mode settings. Type vs interface preference. API response typing. Enum usage.}

## Testing Approach

{Test framework (Vitest, Jest). What to test at each level. Component testing patterns. Mock strategy.}

| Test Level | Framework | What to Test | Location |
|-----------|-----------|-------------|----------|
| Unit | {framework} | {utilities, hooks} | `tests/unit/` |
| Component | {framework} | {rendering, interaction} | `tests/component/` |
| E2E | {framework} | {user workflows} | `tests/e2e/` |

## Performance

{Lazy loading. Code splitting. Image optimization. Bundle size monitoring.}

## Accessibility

{ARIA requirements. Keyboard navigation. Color contrast. Screen reader support.}

## Related Documentation

- [Frontend Overview](overview.md) — Technology stack
- [Frontend Structure](structure.md) — File organization
- [Cross-Cutting: Testing](../08-cross-cutting/testing.md) — System-wide test strategy
