# Epic Design: [Epic Title]

## Current State and Evidence

Describe only the current behavior relevant to this epic. Support material
claims with repository-relative markers:

```text
[EVIDENCE: src/path/file.py#symbol_name]
```

For corrective work, use:

| Confirmed defect | Current evidence | Intended behavior | Smallest correction | Proof |
|---|---|---|---|---|
| | | | | |

## Product and Architecture Decisions

Record accepted decisions with stable identifiers.

### PDR {NNN}: [Product Decision]

**Status:** Accepted

**Context:**

**Decision:**

**Alternatives considered:**

**Consequences:**

### ADR {NNN}: [Architecture Decision]

**Status:** Accepted

**Scope:** System | Backend | Frontend

**Context:**

**Decision:**

**Alternatives considered:**

**Consequences:**

## Architecture and Ownership

Describe changed boundaries, interface shapes, state ownership, integration
touchpoints, and applicable native contracts.

For each high/critical implementation requirement:

### FLOW-AC-NNN

Authority:

Producer:

Boundary:

State owner:

Consumer:

Failure policy:

Proof:

## Failure and Partial States

Define rejection, retry, rollback, partial-success, terminal-state, and
fail-closed behavior where applicable.

## Capability-Specific Risks and Constraints

For each selected capability, record only the risks, constraints, failure
modes, or proof requirements that materially affect this epic. Omit generic
checklist sections that add no design information.

## Hostile Cases

For each high/critical implementation requirement:

### HOSTILE-AC-NNN

Invalid case:

Rejection mechanism:

Evidence: [EVIDENCE: tests/path/test_file.py#test_name]

## Verification Strategy

Name the exact native contract checks, focused tests, integration/E2E coverage,
runtime proof, migration validation, and operational evidence required by the
design. Record commands only when they are executable in the project.

## Documentation Obligations

Record only durable product, architecture, or operations documentation that the
implementation must create or align before audit. Give each requirement a stable
`DOC-NNN` heading. The delivery manifest assigns its repository-relative target
path and owning implementation story. Use `None` when implementation does not
change durable documentation.

### DOC-NNN: [Required documentation alignment]

State the exact product, architecture, or operational fact that the target
documentation must contain after implementation.
