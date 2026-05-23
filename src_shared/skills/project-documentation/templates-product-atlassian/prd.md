# Product Requirements Document

Use this PRD as the starting point for Scope refinement. Write enough product intent that the Product Owner can refine requirements without guessing, and the Architect can later design the system without inventing business decisions.

---

## 1. Purpose

**Why this matters:** Purpose explains why the product should exist. It anchors every later scope, priority, and tradeoff decision.

Describe the product in 2-4 sentences.

```markdown
[What are we building?]
[Why does it matter?]
[What change should exist in the world after this product succeeds?]
```

---

## 2. Project Type And Success Posture

**Why this matters:** Commercial products, sideline tools, internal tools, and community projects optimize for different outcomes. Scope needs this context to avoid applying the wrong product strategy.

Select the primary posture and add any nuance.

- **Commercial revenue:** The product should generate meaningful revenue or support a business model.
- **Sideline / lifestyle:** The product should be useful, bounded, low-maintenance, and not overbuilt.
- **Open source / community:** The product should maximize usefulness, trust, adoption, contributor clarity, or social impact.
- **Internal / operational:** The product should improve team efficiency, reliability, quality, or cost.
- **Other:** [Describe]

Primary posture:

```markdown
[Commercial revenue / Sideline / Open source or community / Internal / Other]
```

Implications:

```markdown
[What tradeoffs should this posture create? Example: prioritize revenue, minimize maintenance, optimize self-hosting, reduce manual work.]
```

---

## 3. Vision

**Why this matters:** Vision gives the product a direction beyond the first feature set. It helps Scope avoid refining isolated features that do not add up to a coherent product.

Write a short vision statement.

```markdown
[For target users], [product name] helps [primary outcome] by [core approach], while [important constraint or differentiation].
```

Example:

```markdown
For small nonprofit teams, VolunteerFlow helps coordinate volunteer availability without spreadsheets by providing lightweight scheduling, conflict prevention, and reminders while staying simple enough for non-technical administrators.
```

---

## 4. Target Users And Stakeholders

**Why this matters:** Requirements are only meaningful when tied to the people who need them. This section prevents Scope from designing for an abstract "user."

Primary users:

- [User type]: [What they need, their skill level, and the context they operate in]

Secondary users:

- [User type]: [What they need]

Stakeholders:

- [Stakeholder]: [What they care about]

Explicitly not serving:

- [User or segment]: [Why not]

---

## 5. Problem Statement

**Why this matters:** A clear problem statement keeps the PRD from jumping directly to implementation ideas. Scope can refine better solutions when the pain is explicit.

Current situation:

```markdown
[How users handle this today]
```

Problems or pain points:

1. [Pain point]
2. [Pain point]
3. [Pain point]

Why existing alternatives are insufficient:

```markdown
[Describe gaps in current tools, processes, or competitors]
```

---

## 6. Desired Outcomes

**Why this matters:** Outcomes define what should improve. They are more stable than features and help Scope challenge unnecessary scope.

User outcomes:

- [Outcome users should experience]

Business / project outcomes:

- [Revenue, adoption, efficiency, community impact, maintenance reduction, or other project-specific outcome]

Operational outcomes:

- [Reliability, support burden, cost, maintainability, deployment, or governance outcome]

---

## 7. Scope

**Why this matters:** Scope boundaries prevent uncontrolled expansion during refinement and implementation.

In scope:

- [Capability, workflow, or behavior that must be included]

Out of scope:

- [Capability, workflow, market, platform, or behavior intentionally excluded]

Future possibilities:

- [Useful idea that should not affect current design unless explicitly approved]

---

## 8. Key Features

**Why this matters:** Key features translate vision into product capability. Prioritization helps Scope separate what must be designed now from what should wait.

### Must Have

- **[Feature name]:** [What it does and why users need it]

### Should Have

- **[Feature name]:** [Useful but not essential for first release]

### Could Have

- **[Feature name]:** [Nice-to-have if cheap]

### Not Now

- **[Feature name]:** [Explicitly deferred or excluded]

---

## 9. Core Workflows

**Why this matters:** Workflows reveal missing requirements, edge cases, permissions, and data transitions that feature lists often hide.

Describe the primary workflows step by step.

### Workflow 1: [Name]

Actor:

```markdown
[Who performs the workflow]
```

Steps:

1. [Step]
2. [Step]
3. [Step]

Expected result:

```markdown
[What should be true when the workflow completes]
```

Failure or edge cases:

- [What can go wrong and what should happen]

---

## 10. Product Rules And Policy Decisions

**Why this matters:** These are the decisions downstream roles must not invent. If the Architect or Developer would need to choose correct business behavior, the PRD is incomplete.

Permissions and roles:

- [Who can do what]

Business rules:

- [Rule that determines correct behavior]

Conflict rules:

- [What happens when data, users, timing, or states conflict]

Failure rules:

- [What happens when an external dependency, payment, email, job, import, or workflow fails]

Audit, compliance, or transparency rules:

- [What must be recorded, explainable, exportable, or reviewable]

---

## 11. Acceptance Criteria

**Why this matters:** Acceptance criteria define observable correctness. They give Scope the raw material for epic refinement, tests, and audit.

Use Given / When / Then where possible.

```gherkin
Given [initial context]
When [user action or system event]
Then [observable expected result]
And [additional expected result]
```

Required acceptance criteria:

1. [Criterion]
2. [Criterion]
3. [Criterion]

Important edge cases:

1. [Edge case]
2. [Edge case]

---

## 12. Constraints

**Why this matters:** Constraints shape architecture and delivery. Missing constraints often cause rework after implementation starts.

Timeline:

```markdown
[Deadline, milestone, or no fixed deadline]
```

Budget or operating cost:

```markdown
[Budget, hosting limit, API spend tolerance, or none]
```

Technology constraints:

```markdown
[Required stack, forbidden stack, existing systems, hosting requirements]
```

Security, privacy, compliance:

```markdown
[Sensitive data, access control, auditability, regulatory expectations]
```

Maintenance tolerance:

```markdown
[How much ongoing care the project can realistically receive]
```

---

## 13. Success Metrics

**Why this matters:** Metrics define whether the product is working after release. The right metrics depend on the project posture.

Commercial metrics:

- [Revenue, conversion, retention, activation, churn, support cost]

Sideline metrics:

- [Hours saved, monthly maintenance time, hosting cost, manual steps removed]

Community / open source metrics:

- [Adoption, self-host success, contributor activity, issue health, documentation completeness]

Internal metrics:

- [Cycle time reduction, error reduction, support tickets avoided, reliability improvement]

Primary success metric:

```markdown
[The most important metric for this product]
```

---

## 14. Assumptions, Risks, And Open Questions

**Why this matters:** Scope can refine known uncertainty, but hidden uncertainty becomes design churn. This section makes uncertainty explicit.

Assumptions:

- [What must be true for the product to succeed]

Risks:

- [What could make the product fail or become expensive]

Open questions:

- [Question that needs user, market, technical, legal, or operational input]

Decisions needed before refinement:

- [Decision]

---

## 15. Launch Or Adoption Plan

**Why this matters:** A product can be correctly built and still fail if no one knows how to adopt it. This section keeps delivery connected to rollout.

Initial audience:

```markdown
[Who gets the product first]
```

Launch approach:

```markdown
[Private beta, public launch, internal rollout, open source release, community announcement, etc.]
```

Support and feedback loop:

```markdown
[How users report problems and how feedback will be reviewed]
```

Documentation or onboarding needed:

- [Guide, example, tutorial, migration notes, API docs, contributor guide]

---

## 16. Non-Goals Summary

**Why this matters:** Repeating non-goals at the end makes them visible during refinement and prevents accidental inclusion in epics.

This PRD does not include:

- [Non-goal]
- [Non-goal]
- [Non-goal]

---

## 17. Readiness Checklist

**Why this matters:** This checklist helps the user judge whether Scope can start refinement productively.

- [ ] The target users are clear.
- [ ] The project posture is clear.
- [ ] The problem is described without relying only on a proposed solution.
- [ ] The key features are prioritized.
- [ ] The main workflows are described.
- [ ] Business rules and policy decisions are explicit.
- [ ] Acceptance criteria describe observable behavior.
- [ ] Scope and non-goals are explicit.
- [ ] Constraints are listed.
- [ ] Success metrics match the project posture.
- [ ] Open questions are listed.

