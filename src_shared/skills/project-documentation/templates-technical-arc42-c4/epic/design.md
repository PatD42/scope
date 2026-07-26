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

## Capability Challenges

Create one section for every common and selected-capability challenge required
by `refinement-policy.yaml`.

### CHALLENGE-authority-and-ownership

Resolution:

Evidence: [EVIDENCE: src/path/file.py#symbol_name]

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
