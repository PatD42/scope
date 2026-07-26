# Epic Workflow

Scope turns an approved epic into an evidence-backed implementation handoff,
then implements and audits that handoff in a worktree.

## Lifecycle

```text
prd_breakdown
    |
epic_refine
    |
implement or implement_tdd
    |
audit_epic
    |
wrap_epic
```

`epic_refine` is the point where product intent, architecture, story ownership,
and proof obligations become binding. Implementation must not invent missing
behavior or silently change those boundaries.

## Refinement Contract

Each v3 epic has one lean, fixed artifact contract.

Authored truth:

```text
docs/epics/{epic-id}/
├── details.md
├── acceptance-criteria.md
├── design.md
├── file-plan-story-01.yaml
├── file-plan-story-02.yaml
└── {project-native contracts when applicable}
```

Generated or review-owned indexes:

```text
├── refinement-profile.yaml
├── refinement-manifest.yaml
├── acceptance-traceability.yaml
├── refinement-findings.yaml
├── refinement-review.md
└── reviews/refine-v3-001/
```

The responsibilities are deliberately narrow:

- `details.md`: goal, scope, non-goals, and lifecycle status.
- `acceptance-criteria.md`: canonical observable behavior with stable IDs.
- `design.md`: repository evidence, PDRs/ADRs, boundaries, ownership, failures,
  adversarial challenges, hostile cases, and verification strategy.
- `file-plan-story-*.yaml`: required contracts, touchpoints, protected surfaces,
  candidate files, and proof obligations for one story.
- `refinement-manifest.yaml`: reconciled requirement and decision ownership.
- `acceptance-traceability.yaml`: generated requirement-to-story/proof view;
  implementation later records actual evidence.

The previous split epic architecture, context, ADR, PDR, and test-strategy
documents are not part of v3.

## Refinement Phases

### Phase 0: Intent and Profile

Confirm outcome, scope, risk, selected capabilities, author provider, and the
required independent review assignments.

Review topology:

| Risk | Independent review |
|---|---|
| Low | One semantic-core reviewer using the provider opposite the author |
| Medium | Claude and Codex semantic-core reviewers |
| High/Critical | Both semantic-core reviewers plus one capability specialist |

The user approves this profile before product or architecture work proceeds.

### Phase 1: Product Contract

Refine observable behavior, rejection and recovery cases, success measures,
and accepted product decisions. `acceptance-criteria.md` remains the only
authority for product behavior.

### Phase 2: Adversarial Design

Inspect source, consumers, tests, schemas, configuration, and runtime
entrypoints. Current-state claims cite stable repository anchors:

```text
[EVIDENCE: src/path/file.py#symbol_name]
```

Resolve capability-specific challenges while designing. High and critical
requirements also receive explicit material flows and hostile cases. Validate
project-native contracts with their actual parser, compiler, or checker.

### Phase 3: Handoff and Reconciliation

Create the fewest independently verifiable stories. Every implementation
requirement must have exactly one story owner and at least one meaningful proof
obligation.

The v3 validator scaffolds and reconciles the manifest and traceability index.
It rejects missing IDs, owners, proofs, challenge sections, evidence anchors,
invalid dependencies, and stale generated rows.

### Phase 4: Independent Review

Launch all required assignments concurrently in fresh processes. Claude and
Codex both perform the semantic-core mission for medium and higher risk because
their findings are complementary. A specialist is added only when risk
justifies it.

Reviewers focus on semantic defects. They do not repeat deterministic checks.
All evidence-backed findings survive merge; providers do not vote findings
away.

Corrections receive targeted verification from the named assignments. A second
full review requires material redesign or explicit user approval.

### Final Handoff

When reconciliation passes, required reviews complete, findings are terminal,
and the user approves, `details.md` becomes `ready-for-implementation`.

## Resume Behavior

`epic_refine` validates the existing v3 artifacts in phase order and resumes at
the first failing phase. It does not infer or migrate older schemas.

To update an already refined epic, run `epic_refine` again. The command decides
which phase must be revisited from the changed durable artifacts; the user does
not need to name a step number.

## Implementation

`implement` creates or reuses `wip/{epic-id}` and executes stories in dependency
order. For each story it:

1. reads the canonical acceptance rows, design, manifest, and boundary plan;
2. implements required contracts and touchpoints;
3. avoids forbidden changes unless refinement is reopened;
4. runs each proof obligation and project-native quality gate;
5. records actual files, tests, commands, and evidence in traceability.

`implement_tdd` adds an SDET test-first pass before the same implementation and
proof workflow.

## Audit

`audit_epic` is read-only. It derives verification from the v3 handoff and
implementation evidence, runs project-native gates, and uses independent
reviewers according to its audit policy.

The normal loop is bounded:

1. one full audit;
2. implementation remediates named findings;
3. one targeted verification.

Another full audit requires a material boundary change or explicit approval.

## Wrap

`wrap_epic` verifies final evidence, merges the implementation branch, updates
system documentation from accepted decisions in `design.md`, archives the epic,
and synchronizes CodeGraph at the main project root.
