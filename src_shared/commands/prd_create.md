---
name: prd_create
description: Lightweight interview to create a first-pass Product Requirements Document for Scope refinement.
args: "[product-name]"
skills: project-documentation
---

# /prd_create

Create a first-pass Product Requirements Document through a lightweight user interview.

**Syntax:** `/prd_create [product-name]`

**Output:** `docs/product/prd.md`

## Purpose

`prd_create` is for users who have an idea but do not yet have a PRD. It should
feel like a focused interview, not a full product workshop. Keep the process
short enough that users can complete it in one sitting, especially ADHD users or
users who are still exploring the product direction.

This command creates the raw PRD artifact that `/prd_refine` will later turn
into structured product documentation: strategy, definition, reference pages,
product decisions, and competitive research.

## Boundary With `/prd_refine`

`prd_create` should not exhaustively refine the product. Leave these for
`/prd_refine`:

- full capability mapping
- competitive research
- detailed product decision records
- complete acceptance criteria
- exhaustive workflows
- feature catalog normalization
- terminology/data-model normalization
- product documentation page creation

`prd_create` should capture enough intent that `/prd_refine` can proceed
without guessing.

## Interview Style

Ask concise questions in small batches. Prefer 2-4 questions at a time. After
each phase, summarize what you heard and ask the user to correct anything
important before proceeding.

Do not force the user to answer every optional detail. If a detail is unknown,
record it under `Open Questions` instead of blocking progress.

When the user gives a broad or ambiguous answer, ask one follow-up question only
if the ambiguity would affect product direction, scope, or correct behavior.

## Workflow Overview

```
1. Phase 1: Project Intent
2. Phase 2: Users, Problem, And Outcomes
3. Phase 3: Scope And Key Features
4. Phase 4: Core Workflows And Rules
5. Phase 5: Review And PRD Draft
```

---

## Phase 1: Project Intent

**Goal:** Establish what this is and why it matters.

Ask about:

- product/project name
- project type: commercial, sideline, open source/community, internal, other
- purpose in plain language
- high-level vision
- success posture: revenue, usefulness, adoption, time saved, community value,
  reduced maintenance, or another outcome

### Phase 1 Checklist

- Product/project name captured.
- Project type captured.
- Purpose captured in plain language.
- Vision captured at a high level.
- Success posture captured.

### Phase 1 Complete When

- You can explain the project in 3-5 sentences.
- The project type and main success direction are clear.

---

## Phase 2: Users, Problem, And Outcomes

**Goal:** Understand who has the problem and what should improve.

Ask about:

- primary users
- secondary users or stakeholders
- current pain, opportunity, or motivation
- current workaround, alternative, or competitor
- desired user outcomes
- desired project outcomes

### Phase 2 Checklist

- Primary users identified.
- Secondary users or stakeholders identified if relevant.
- Current pain or opportunity described.
- Current workaround or alternative described.
- Desired user outcomes captured.
- Desired project outcomes captured.

### Phase 2 Complete When

- It is clear who the product serves.
- It is clear what problem or opportunity justifies building it.
- It is clear what should be better after the product exists.

---

## Phase 3: Scope And Key Features

**Goal:** Identify the product shape without designing everything.

Ask about:

- must-have features
- nice-to-have or future features
- explicit non-goals
- first useful version or MVP
- major constraints: budget, time, maintenance tolerance, required stack,
  privacy/security, integrations

### Phase 3 Checklist

- Must-have features listed.
- Nice-to-have or future features listed.
- Explicit non-goals listed.
- MVP or first useful version roughly described.
- Major constraints captured.

### Phase 3 Complete When

- The first useful version is understandable.
- The biggest boundaries are explicit.
- Obvious scope creep is separated from current scope.

---

## Phase 4: Core Workflows And Rules

**Goal:** Capture the behavior that would be costly to guess later.

Ask about:

- 2-5 core workflows
- main actors for each workflow
- important product or business rules
- conflict behavior where known
- failure behavior where known
- unclear behavior that needs future refinement

### Phase 4 Checklist

- 2-5 core workflows described at a high level.
- Main actors identified.
- Important business/product rules captured.
- Conflict or failure behavior captured where known.
- Open questions listed where behavior is unclear.

### Phase 4 Complete When

- The most important user journeys are understandable.
- The Product Owner has enough material to turn the workflows into acceptance
  criteria during `/prd_refine`.
- Known ambiguities are visible instead of hidden.

---

## Phase 5: Review And PRD Draft

**Goal:** Confirm the user's intent and write the PRD.

Create a draft PRD using the template at:

`skills/project-documentation/templates-product-atlassian/prd.md`

Write the final PRD to:

`docs/product/prd.md`

If `docs/product/prd.md` already exists:

1. Ask the user whether to replace it or create a timestamped draft under
   `docs/product/prd-drafts/`.
2. Do not overwrite an existing PRD without explicit user confirmation.

### Phase 5 Checklist

- Draft PRD generated.
- User confirms project intent.
- User confirms users/problem/outcomes.
- User confirms scope/non-goals.
- User confirms key workflows/rules.
- Open questions are listed clearly.
- `docs/product/prd.md` exists, or a timestamped draft exists by user choice.

### Phase 5 Complete When

- The user agrees the PRD reflects their intent.
- The PRD is good enough for `/prd_refine` to continue with structured product
  documentation.

---

## Definition Of Complete

`prd_create` is complete when the PRD answers these questions well enough for
refinement:

- What are we building?
- Why does it matter?
- Who is it for?
- What problem or opportunity does it address?
- What does success look like?
- What is in scope for the first useful version?
- What is explicitly out of scope?
- What are the key features?
- What are the most important workflows?
- What product rules or constraints are already known?
- What remains unclear?

The PRD does **not** need to fully define:

- detailed acceptance criteria
- complete capability maps
- competitive landscape
- detailed product decisions
- exhaustive workflows
- final release plan

Those belong in `/prd_refine`.

## Output Format

The PRD should use the section structure from the PRD template, but completed at
the appropriate level of detail for an initial draft:

```markdown
# Product Requirements Document

## 1. Purpose
...

## 2. Project Type And Success Posture
...

## 3. Vision
...

## 4. Target Users And Stakeholders
...

## 5. Problem Statement
...

## 6. Desired Outcomes
...

## 7. Scope
...

## 8. Key Features
...

## 9. Core Workflows
...

## 10. Product Rules And Policy Decisions
...

## 11. Acceptance Criteria
Initial high-level acceptance notes only. Detailed acceptance criteria are for
`/prd_refine`.

## 12. Constraints
...

## 13. Success Metrics
...

## 14. Assumptions, Risks, And Open Questions
...

## 15. Launch Or Adoption Plan
...

## 16. Non-Goals Summary
...

## 17. Readiness Checklist
...
```

## Handoff

At the end, tell the user:

```text
PRD draft created at docs/product/prd.md.
Next recommended command: /prd_refine [product-name]
Codex: run scope:prd_refine [product-name]
```
