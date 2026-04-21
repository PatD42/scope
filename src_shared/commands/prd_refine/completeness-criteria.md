# PRD Completeness Criteria

Guidelines for assessing when a PRD is "complete enough" for epic breakdown.

## Readiness Levels

### ✅ Ready for Breakdown
PRD has sufficient detail to identify implementable epics with clear boundaries and dependencies.

### ⚠️ Needs Refinement
PRD has all sections but quality/clarity issues that would cause confusion during epic breakdown.

### ❌ Incomplete
PRD is missing required sections or has insufficient detail.

## Section-by-Section Criteria

### Product Strategy

**Required Elements:**
- [ ] **Vision Statement**: 1-3 sentences describing what you're building and why it matters
- [ ] **Target Markets**: 2-4 distinct customer segments or use contexts
- [ ] **Customer Problems**: 3-7 specific pain points the product addresses
- [ ] **Scope Boundaries**: 2-5 explicit non-goals or out-of-scope items

**Quality Indicators:**
- ✅ Vision is aspirational but grounded (not generic platitudes)
- ✅ Markets are specific enough to guide prioritization
- ✅ Problems are described from customer perspective (not solution-focused)
- ✅ Non-goals are explicit and prevent scope creep
- ✅ Competitive landscape understood (3-5 competitors analyzed)

**Common Issues:**
- ⚠️ Vision too vague: "We're building a better developer tool"
- ⚠️ Problems are solutions in disguise: "Need a React dashboard" (should be "Need visibility into system health")
- ⚠️ No competitive context (building in vacuum)
- ⚠️ No explicit non-goals (risk of scope creep)

**Minimum for Breakdown:**
- Vision clear enough to make scope decisions
- At least 2 target markets identified
- At least 3 customer problems articulated
- At least 2 explicit non-goals defined

---

### Product Definition

**Required Elements:**
- [ ] **Use Cases**: 5-12 primary use cases (actor + goal + outcome)
- [ ] **Capability Map**: 15-30 capabilities grouped by theme

**Optional but Recommended:**
- [ ] User Personas (2-4 archetypes)
- [ ] User Journeys (end-to-end workflows)

**Quality Indicators:**
- ✅ Use cases are specific and actionable
- ✅ Use cases cover different user types and scenarios
- ✅ Capability map is comprehensive (not just "happy path")
- ✅ Capabilities are implementation-agnostic
- ✅ Each capability maps to user value

**Common Issues:**
- ⚠️ Use cases too high-level: "User manages data" (should be "User imports CSV with validation")
- ⚠️ Capability map includes implementation: "JWT Authentication" (should be "User Authentication")
- ⚠️ Missing edge cases: Only covers successful flows, not errors/exceptions

**Minimum for Breakdown:**
- At least 5 use cases covering core functionality
- Capability map with at least 12 capabilities
- Capabilities grouped into logical themes (3-6 themes)

---

### Product Reference

**Required Elements (4 children):**
- [ ] **Feature Catalog**: Comprehensive feature list with status and priority
- [ ] **Terminology & Data Model**: Domain terms and key entities
- [ ] **UI & Workflows**: Navigation, screens, and business processes
- [ ] **APIs & Integrations**: External systems and interfaces

**Quality Indicators:**
- ✅ Feature Catalog covers all planned functionality with clear status
- ✅ Terminology covers domain-specific terms with clear definitions
- ✅ Entities describe "what" not "how" (conceptual, not technical)
- ✅ Entity relationships are documented
- ✅ UI & Workflows describe navigation and key screens
- ✅ APIs & Integrations identify all external systems

**Common Issues:**
- ⚠️ Terminology too sparse: Only 3-5 terms for complex domain
- ⚠️ Terminology too generic: Defines "user", "system" (assume basics known)
- ⚠️ Entities are database tables: "User table with columns..." (too detailed)
- ⚠️ Missing UI structure for user-facing products
- ⚠️ Missing integration details for systems with external dependencies

**Minimum for Breakdown:**
- Feature Catalog with initial feature list (can be refined during epic breakdown)
- Terminology & Data Model with 8-20 terms (varies by domain complexity) and 3-8 key entities
- UI & Workflows defined for user-facing products
- APIs & Integrations documented if product has external dependencies

---

### Product Decisions

**Required Elements:**
- [ ] **MVP & Phasing**: Clear definition of what's in v1.0 vs future phases
- [ ] **Success Criteria**: 2-5 measurable KPIs with target values
- [ ] **Non-Functional Requirements**: Performance, security, and scalability targets
- [ ] **Technical Constraints**: Budget, timeline, technology, team limitations
- [ ] **Dependencies & Assumptions**: External dependencies and key assumptions identified

**Quality Indicators:**
- ✅ MVP is truly minimum viable (not "everything we want")
- ✅ KPIs are specific and measurable (not vague goals)
- ✅ NFRs have concrete targets (not "should be fast")
- ✅ Constraints are realistic and documented
- ✅ Dependencies identified early (not discovered during implementation)
- ✅ Assumptions are explicit and testable

**Common Issues:**
- ⚠️ MVP too large: Includes all nice-to-have features
- ⚠️ Vague KPIs: "Improve developer productivity" (should be "Reduce PR review time by 30%")
- ⚠️ Missing NFRs: No performance, security, or scalability requirements
- ⚠️ Undocumented constraints: Assumes unlimited time/budget
- ⚠️ Hidden dependencies: Assumes external systems will cooperate
- ⚠️ Implicit assumptions: "Users will have Python installed" (not stated)

**Minimum for Breakdown:**
- MVP features clearly separated from future phases
- At least 2 KPIs with measurable targets
- Critical NFRs identified (at minimum: performance OR security OR scalability)
- Major constraints documented (timeline, budget, or technology stack)
- External dependencies listed (if any)
- 2-3 key assumptions documented

---

### Competitive Research

**Required Elements:**
- [ ] **Competitor Analysis**: 3-5 competitors with feature comparison
- [ ] **Positioning Insights**: How competitors differentiate
- [ ] **Gap Identification**: What competitors don't do well

**Quality Indicators:**
- ✅ Analysis covers direct and adjacent competitors
- ✅ Features compared at capability level (not just UI)
- ✅ Customer feedback reviewed (not just marketing claims)
- ✅ Gaps identified inform our differentiation

**Common Issues:**
- ⚠️ Only analyzed 1-2 competitors
- ⚠️ Analysis is superficial: "They have feature X"
- ⚠️ No gap analysis (just feature list)

**Minimum for Breakdown:**
- At least 3 competitors analyzed
- Feature comparison at capability level
- Identified 2-3 differentiation opportunities

---

## Holistic Completeness Checks

### Consistency Checks
- ✅ Capabilities in Definition support Problems in Strategy
- ✅ Use cases leverage Capabilities
- ✅ Terminology terms appear in Strategy/Definition
- ✅ Feature Catalog aligns with Capability Map
- ✅ Competitive gaps inform Capabilities

### Sufficiency Checks
- ✅ Can identify 5-15 epics from capability map
- ✅ Epic boundaries are clear (not too broad, not too granular)
- ✅ Technical dependencies between epics are identifiable
- ✅ Prioritization is possible (based on problems and markets)

### Clarity Checks
- ✅ Engineers can understand what to build
- ✅ Product team can understand value proposition
- ✅ Leadership can understand market opportunity
- ✅ New team members can onboard from PRD

---

## Assessment Heuristics

### Expected Volumes (Rough Guidelines)

| Section | Typical Range |
|---------|---------------|
| Vision | 1-3 sentences |
| Target Markets | 2-4 segments |
| Customer Problems | 3-7 problems |
| Non-Goals | 2-5 explicit exclusions |
| Use Cases | 5-12 use cases |
| Capabilities | 15-30 capabilities |
| Capability Themes | 3-6 themes |
| Feature Catalog | Initial list (refined during breakdown) |
| Terminology & Data Model | 8-20 terms, 3-8 entities |
| UI & Workflows | Key screens and navigation (if user-facing) |
| APIs & Integrations | 0-10 external systems |
| KPIs | 2-5 measurable metrics |
| MVP Features | 40-70% of total capabilities |
| Phase 2 Features | 20-40% of total capabilities |
| NFRs | 3-5 specific requirements |
| Dependencies | 0-5 external dependencies |
| Competitors Analyzed | 3-5 competitors |

**Note:** These are guidelines, not rules. A simple product might have fewer; a complex platform might have more.

### Red Flags

**Incomplete:**
- ❌ Missing entire section (e.g., no use cases)
- ❌ Placeholder text: "TBD", "[To be filled in]"
- ❌ Only 1-2 use cases for complex product
- ❌ Capability map has <10 capabilities
- ❌ No MVP definition or phasing strategy
- ❌ No success criteria or KPIs defined
- ❌ Missing non-functional requirements
- ❌ No scope boundaries (no explicit non-goals)

**Needs Refinement:**
- ⚠️ Vague language: "various features", "flexible system"
- ⚠️ Implementation details in Definition: "React dashboard with Redux"
- ⚠️ No competitive context (built in vacuum)
- ⚠️ Capabilities don't align with problems
- ⚠️ MVP too large (includes all nice-to-have features)
- ⚠️ Vague KPIs: "Improve developer productivity" (should be "Reduce PR review time by 30%")
- ⚠️ Undocumented constraints: Assumes unlimited time/budget
- ⚠️ Hidden dependencies: Assumes external systems will cooperate

**Over-Specified:**
- ⚠️ Technical architecture in Strategy (too early)
- ⚠️ Database schema in Reference (too detailed)
- ⚠️ UI wireframes (not needed for PRD)

---

## Readiness Decision Framework

### Questions to Answer

**For Epic Breakdown to Succeed:**
1. Can you identify 5-15 epics from the capability map?
2. Are epic boundaries clear (cohesive capabilities that can be developed semi-independently)?
3. Can you identify technical dependencies between epics?
4. Can you prioritize epics based on customer problems and markets?
5. Is there a clear MVP definition that separates must-have from nice-to-have capabilities?
6. Are success criteria measurable and specific enough to validate the product?
7. Are critical non-functional requirements (performance, security, or scalability) identified?

**If YES to all 7:** ✅ Ready for breakdown

**If NO to 1-3:** ⚠️ Refine specific sections (identify gaps)

**If NO to 4-7:** ❌ Incomplete (need more work)

### Gap Severity

**Critical (Must Fix):**
- Missing use cases or capability map
- Vision so vague it can't guide decisions
- No understanding of competitive landscape
- No MVP definition or phasing strategy
- No success criteria or KPIs
- Missing non-functional requirements entirely
- No scope boundaries (no explicit non-goals)

**Important (Should Fix):**
- Sparse terminology for complex domain
- Missing entity relationships
- Missing UI structure for user-facing products
- Missing integration documentation for systems with dependencies
- Inconsistencies between sections
- Undocumented technical constraints
- Missing dependencies or assumptions
- Vague or unmeasurable KPIs

**Nice-to-Have (Optional):**
- User personas
- Detailed user journeys
- Extended competitive analysis (beyond 3-5 competitors)
- Comprehensive list of all assumptions
- Detailed availability requirements

---

## Presentation Format

When presenting readiness assessment to user:

```
PRD Completeness Assessment:

✅ Product Strategy
   Vision: Clear and actionable
   Markets: 3 segments identified
   Problems: 5 customer pain points documented
   Non-Goals: 3 explicit exclusions defined
   Research: 4 competitors analyzed

✅ Product Definition
   Use Cases: 9 use cases covering core workflows
   Capability Map: 24 capabilities across 5 themes

⚠️ Product Reference (4 required children)
   Feature Catalog: Defined with 25 features
   Terminology & Data Model: 8 terms (expected 12-15 for this complexity), 4 entities with relationships
   UI & Workflows: Defined
   APIs & Integrations: 2 integrations documented

✅ Product Decisions
   MVP/Phasing: Defined (15 capabilities in MVP, 9 in Phase 2)
   Success Criteria: 3 KPIs defined
   Non-Functional Requirements: Performance, Security, Scalability defined
   Technical Constraints: Documented
   Dependencies: 2 dependencies identified

✅ Competitive Research
   Competitors: 4 analyzed
   Differentiation: Clear positioning identified

Overall: Ready with minor gaps
  - Consider expanding glossary with technical terms
  - Otherwise sufficient for epic breakdown

Ready to proceed with /prd_breakdown? [yes/refine/what's missing?]
```
