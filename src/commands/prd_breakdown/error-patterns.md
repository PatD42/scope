# Error Handling Patterns

Use these patterns when encountering errors during PRD breakdown.

## PRD Incomplete

```
Cannot break down PRD: Product Definition missing capability map.

Please run '/prd_refine' to complete:
- [ ] Use cases
- [ ] Capability map

Then return to '/prd_breakdown'.
```

## Capability Map Too Sparse

```
Capability map only has [N] capabilities. Expected 12-30 for meaningful epic breakdown.

Options:
1. Continue with [N] capabilities (will create [M] small epics)
2. Return to '/prd_refine' to expand capability map
3. Cancel breakdown

Which would you like?
```

## User Rejects All Epic Proposals

```
All epic proposals rejected. Let's refine the approach.

What would make the epic breakdown more useful?
- Different grouping strategy? (e.g., by user journey instead of components)
- Different epic sizes? (larger/smaller)
- Different focus? (prioritize specific customer problems)

Please describe your ideal epic structure.
```
