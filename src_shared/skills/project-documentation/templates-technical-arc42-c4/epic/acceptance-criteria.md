# {epic-id}: Acceptance Criteria

This file is the canonical authority for observable product behavior. Use one
heading per independently provable promise. Replace every `{NNN}` placeholder
and remove unused sections.

## AC-{NNN}: [Observable successful outcome]

**Given:** [precondition]

**When:** [user or system action]

**Then:** [observable result]

**Success measure:** [threshold or exact condition]

## ERR-{NNN}: [Observable rejection, error, or recovery outcome]

**Given:** [invalid, unavailable, partial, or failed condition]

**When:** [action or failure]

**Then:** [rejection, error, rollback, retry, or recovery behavior]

## E2E-{NNN}: [Cross-boundary outcome]

**Path:** [entrypoint through observable result]

**Then:** [end-to-end evidence required]

## Deferred Behavior

List explicitly deferred behavior. Deferred statements are non-binding and must
not be presented as accepted implementation requirements.
