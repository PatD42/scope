---
name: prd_refine
description: Guided PRD refinement through interactive conversation. Checklist-driven workflow with discovery-driven updates.
args: "[product-name]"
skills: project-documentation
---

# /prd_refine

Interactive PRD refinement with guided checklist and discovery-driven updates.

**Syntax:** `/prd_refine [product-name]`

## Workflow Overview

**Execution Pattern:** Checklist-driven with side updates and mandatory assessment

```
1. Load existing PRD state (if any)
2. Execute checklist in order:
   ├─ Setup: Create Parent Pages (Product Overview, Product Reference)
   ├─ Product Strategy (with scope boundaries, parentId, labels)
   ├─ Product Definition (with user validation, parentId, labels)
   ├─ Product Reference (4 child pages with parentId, labels)
   ├─ Product Decisions (MVP, KPIs, NFRs, constraints, parentId, labels)
   └─ Competitive Research (with user validation)
3. Discovery triggers side updates (e.g., Definition → Reference glossary)
4. **MANDATORY: Assess readiness against completeness criteria**
   ├─ Check ALL required items from each section
   ├─ Identify gaps (critical/important/nice-to-have)
   └─ Assign readiness level (Ready/Needs Refinement/Incomplete)
5. Present assessment to user with specific findings
6. If gaps exist: address gaps → re-assess → repeat until ready
7. Only if "✅ Ready": recommend /prd_breakdown
```

## Checklist (North Star)

Execute in this order. Check off as completed.

### ☐ Setup: Create Parent Pages

**Required:**
- Product Overview (root parent for all product pages)
- Product Reference (parent for 4 reference children)

**Process:**
1. Create "Product Overview" page (no parentId, use template)
2. Store page_id as `product_overview_id`
3. Create "Product Reference" page (parentId=product_overview_id, use template)
4. Store page_id as `product_reference_id`
5. Mark complete, move to Product Strategy

**Note:** These parent pages are created first, then all other product pages are created as their children.

---

### ☐ Product Strategy

**Required:**
- Vision statement (what we're building, why it matters)
- Target markets (2-4 market segments)
- Customer problems (3-7 key pain points)
- Scope boundaries (2-5 explicit non-goals)

**Process:**
1. Ask user about vision and target customers
2. Ask user about customer problems
3. **Ask: "What is explicitly OUT OF SCOPE for this product?" (non-goals, excluded features, unsupported use cases)**
4. Draft strategy content including non-goals
5. Present draft to user and validate
6. Write to documentation with `parentId=product_overview_id` (see [Documentation Operations](#documentation-operations))
7. Apply labels: `["product", "strategy"]`
8. Mark complete, move to next

---

### ☐ Product Definition

**Required:**
- Use cases (5-12 primary use cases)
- Capability map (15-30 capabilities grouped by theme)

**Optional:**
- User personas (2-4 archetypes)
- User journeys (end-to-end workflows)

**Process:**
1. Extract use cases from strategy
2. **Draft use cases and PRESENT TO USER**
3. **Ask: "Do these use cases capture the key workflows? Any missing scenarios?"**
4. **Wait for user validation on use cases**
5. Map capabilities needed for each use case (see [Product Management Frameworks](prd_refine/product-management-frameworks.md))
6. **PRESENT capability map to user**
7. **Ask: "Does this capability map cover all functionality? Any capabilities missing or incorrectly grouped?"**
8. **Wait for user validation on capability map**
9. After validation, write to documentation with `parentId=product_overview_id`
10. Apply labels: `["product", "definition"]`
11. **🔄 Discovery:** Extract domain terms → Update Reference (glossary)
12. Mark complete, move to next

---

### ☐ Product Reference

**Required (4 child pages):**
- Feature Catalog (comprehensive feature list with status and priority)
- Terminology & Data Model (domain terms and key entities)
- UI & Workflows (navigation, screens, business processes)
- APIs & Integrations (external systems and interfaces)

**Process:**
1. Review terms from Definition → Draft Terminology & Data Model
2. Extract features from capabilities → Draft Feature Catalog
3. Identify user interface structure → Draft UI & Workflows
4. Identify external systems → Draft APIs & Integrations
5. Present all 4 reference pages to user
6. Validate with user
7. Write 4 child pages to documentation with `parentId=product_reference_id` (see [Documentation Operations](#documentation-operations)):
   - Feature Catalog → Apply labels: `["product", "reference", "feature-catalog"]`
   - Terminology & Data Model → Apply labels: `["product", "reference", "terminology"]`
   - UI & Workflows → Apply labels: `["product", "reference", "ui"]`
   - APIs & Integrations → Apply labels: `["product", "reference", "apis"]`
8. **🔄 Discovery:** Missing capabilities identified → Update Definition
9. Mark complete, move to next

---

### ☐ Product Decisions

**Required:**
- MVP / phased release approach (what's in v1.0, v2.0, future)
- Success criteria and KPIs (measurable outcomes)
- Non-functional requirements (performance, security, scalability)
- Technical constraints (budget, timeline, technology)
- Key dependencies and assumptions

**Process:**
1. **Ask: "Can all capabilities fit in MVP, or should we phase them into v1.0, v2.0, etc.?"**
2. Draft prioritization showing MVP vs future phases
3. **Ask: "How will you measure success? What are the key metrics or KPIs?"**
4. **Ask: "Any non-functional requirements? Performance SLAs, security compliance, scalability targets?"**
5. **Ask: "Any technical constraints? Budget, timeline, must-use technologies, team limitations?"**
6. **Ask: "Any external dependencies or key assumptions we're making?"**
7. Present all decisions for validation
8. Wait for user validation
9. Write to documentation with `parentId=product_overview_id` (Product Decisions Record page)
10. Apply labels: `["product", "pdr"]`
11. **🔄 Discovery:** Prioritization affects capability grouping → Update Definition
12. Mark complete, move to next

---

### ☐ Competitive Research

**Required:**
- Competitor analysis (3-5 competitors)
- Feature comparison
- Positioning insights

**Process:**
1. Use WebSearch to find competitors
2. Use WebFetch to analyze features, positioning
3. **Draft competitive summary and PRESENT TO USER**
4. **Ask: "Does this capture the competitive landscape? Any competitors I missed or mischaracterized?"**
5. **Wait for user validation**
6. After validation, write competitive landscape to Strategy documentation
7. **🔄 Discovery:** Competitor strength affects vision → Update Strategy
8. Mark complete, move to assessment

---

## Discovery-Driven Updates

While working on any section, if insight affects another section, immediately update it.

**Announce format:**
```
🔄 Discovery Update: [Target Section]

While working on [current section], I noticed [insight].
Updating [target section] to reflect this.

[Brief description of update]

Continuing with [current section]...
```

**Common triggers:**
- Definition use cases → Reference glossary terms
- Reference entity modeling → Definition missing capabilities
- Research competitor features → Strategy vision refinement
- Strategy customer problems → Definition new use cases

---

## Documentation Operations

Use the `project-documentation` skill to write PRD content. The skill is backend-agnostic and works with Confluence, file-based, SharePoint, or Notion backends.

**Important - Parent Pages First:**
1. Create parent pages FIRST (Setup step in checklist):
   - Product Overview (no parentId)
   - Product Reference (parentId=product_overview_id)
2. Create all other pages as children with appropriate parentId
3. Apply labels after each page creation

**Title Format:** Use simple titles from templates (e.g., "Product Strategy" not "ProjectName: Product Strategy"). Confluence space provides project context.

**Labels:** Apply after creating each page using backend-specific method (see backend implementation guide).

### Write Product Strategy

```
Title: "Product Strategy"
ParentId: product_overview_id (from Setup step)
Labels: ["product", "strategy"]

Content:

## Vision
[1-3 sentences describing what we're building and why it matters]

## Target Markets
1. [Market segment 1]
2. [Market segment 2]
...

## Customer Problems
1. [Problem 1]
2. [Problem 2]
...

## Scope & Non-Goals

**In Scope:**
- [Core features and use cases we're building]

**Out of Scope / Non-Goals:**
- [Explicitly excluded features to prevent scope creep]
- [Use cases we're intentionally NOT supporting]
- [Functionality deferred to future versions]

## Competitive Landscape
[Summary of 3-5 competitors, positioning, differentiation]
```

### Write Product Definition

```
Title: "Product Definition"
ParentId: product_overview_id (from Setup step)
Labels: ["product", "definition"]

Content:

## Use Cases
### [Use Case 1]
**Actor:** [User role]
**Goal:** [What they want to accomplish]
**Flow:**
1. [Step 1]
2. [Step 2]
...

## Capability Map
### [Theme 1]
- [Capability 1]
- [Capability 2]
...

### [Theme 2]
...
```

### Write Product Reference

**Structure:** Product Reference has 4 required child pages. Create all 4 as children of Product Reference parent.

Use project-documentation skill to create/update these 4 child pages:

**1. Feature Catalog**
```
Title: "Feature Catalog"
ParentId: product_reference_id (from Setup step)
Labels: ["product", "reference", "feature-catalog"]

Content:
## Overview
[Brief description of feature organization]

## Core Features

| Feature | Description | Status | Priority | Release |
|---------|-------------|--------|----------|---------|
| [Feature 1] | [What it does] | Planned/In Dev/Released | High/Med/Low | v1.0 |

## Enhanced Features
[Similar table for non-core features]

## Feature Details
### Feature 1: [Name]
**Description:** [Detailed description]
**User Value:** [Why this matters to users]
**Use Cases:** [Which use cases this supports]
```

**2. Terminology & Data Model**
```
Title: "Terminology & Data Model"
ParentId: product_reference_id (from Setup step)
Labels: ["product", "reference", "terminology"]

Content:

## Terminology

| Term | Definition | Usage Example |
|------|------------|---------------|
| [Term 1] | [Clear definition] | [How it's used in product context] |

## Key Entities
### Entity 1: [Name]
**Description:** [What this entity represents]
**Attributes:**
- [Key attribute 1]
- [Key attribute 2]

**Relationships:**
- [Relationship to other entities]
```

**3. UI & Workflows**
```
Title: "UI & Workflows"
ParentId: product_reference_id (from Setup step)
Labels: ["product", "reference", "ui"]

Content:

## Navigation Structure
### Primary Navigation
- **[Section 1]**: [Purpose and key functions]

## Key Screens

| Screen | Purpose | Key Elements | Access |
|--------|---------|--------------|--------|
| [Screen 1] | [What user does here] | [Important UI components] | [How user gets here] |

## Workflows
### Workflow 1: [Name]
**Trigger:** [What starts this workflow]
**Steps:**
1. **[Screen 1]**: [What user does]
2. **[Screen 2]**: [What user does]
```

**4. APIs & Integrations**
```
Title: "APIs & Integrations"
ParentId: product_reference_id (from Setup step)
Labels: ["product", "reference", "apis"]

Content:

## Overview
[Summary of external systems]

## External Integrations

| Integration | Purpose | Direction | Status | Owner |
|-------------|---------|-----------|--------|-------|
| [System 1] | [Why we integrate] | In/Out/Both | Active/Planned | [Team] |

## Integration Details
### Integration 1: [System Name]
**Purpose:** [Why this integration exists]
**Direction:** [Inbound / Outbound / Bidirectional]
**Method:** [REST API / Webhook / File Transfer]
**Data Exchanged:**
- **To [System]**: [What data we send]
- **From [System]**: [What data we receive]
```

### Write Product Decisions

```
Title: "Product Decisions Record"
ParentId: product_overview_id (from Setup step)
Labels: ["product", "pdr"]

Content:

## MVP & Phased Release Approach

**MVP / v1.0:**
- [Minimum viable capabilities]
- [Core features that must be in first release]

**Phase 2 / v2.0:**
- [Next priority features]
- [Enhancements deferred from MVP]

**Phase 3 / Future:**
- [Nice-to-have features]
- [Long-term vision items]

## Success Criteria

**Key Performance Indicators (KPIs):**
- [Metric 1]: [Target value]
- [Metric 2]: [Target value]
- [Metric 3]: [Target value]

**Acceptance Criteria:**
- [How we'll know the product is "done"]
- [Definition of success]

## Non-Functional Requirements

**Performance:**
- [Response time requirements]
- [Throughput expectations]
- [Latency targets]

**Security:**
- [Authentication requirements]
- [Authorization model]
- [Compliance needs (GDPR, SOC2, etc.)]

**Scalability:**
- [Expected load]
- [Growth projections]
- [Scaling strategy]

**Availability:**
- [Uptime requirements]
- [Disaster recovery needs]

## Technical Constraints

- **Budget:** [Budget limitations if applicable]
- **Timeline:** [Timeline constraints]
- **Technology Stack:** [Must-use or must-avoid technologies]
- **Team:** [Team size, skills, availability]
- **Integration:** [Required integrations with existing systems]

## Dependencies & Assumptions

**External Dependencies:**
- [Third-party APIs]
- [External systems or services]
- [Data sources]

**Key Assumptions:**
- [Assumptions that, if wrong, would significantly change approach]
- [Technology assumptions]
- [Business assumptions]
```

---

## Readiness Assessment

**MANDATORY:** After completing all 5 checklist sections, you MUST perform readiness assessment before recommending epic breakdown.

Evaluate completeness using criteria from [Completeness Criteria](prd_refine/completeness-criteria.md).

### Assessment Process

1. **Review each section** against completeness criteria
2. **Check ALL requirements** from completeness-criteria.md:
   - Product Strategy: Vision, markets, problems, non-goals, competitive research
   - Product Definition: Use cases (5-12), capability map (15-30 capabilities)
   - Product Reference: All 4 children (Feature Catalog, Terminology & Data Model, UI & Workflows, APIs & Integrations)
   - Product Decisions: MVP/phasing, KPIs (2-5), NFRs, constraints, dependencies
   - Competitive Research: 3-5 competitors analyzed
3. **Identify gaps** (critical, important, nice-to-have)
4. **Assign readiness level**:
   - ✅ **Ready**: All required items complete, quality acceptable
   - ⚠️ **Needs Refinement**: Complete but quality issues that could cause confusion
   - ❌ **Incomplete**: Missing required items (cannot proceed)

### Present Assessment to User

```
PRD Completeness Assessment:

✅ Product Strategy
   Vision: [Clear/Vague/Missing]
   Markets: [N segments identified]
   Problems: [N pain points documented]
   Non-Goals: [N explicit exclusions / Not defined]
   Research: [N competitors analyzed]

[Status] Product Definition
   Use Cases: [N use cases covering [scope]]
   Capability Map: [N capabilities across [M] themes]

[Status] Product Reference (4 required children)
   Feature Catalog: [Defined with N features / Missing]
   Terminology & Data Model: [N terms, N entities / Missing]
   UI & Workflows: [Defined / Missing]
   APIs & Integrations: [N integrations documented / Missing]

[Status] Product Decisions
   MVP/Phasing: [Defined / Not defined]
   Success Criteria: [N KPIs defined / Missing]
   Non-Functional Requirements: [Performance, Security, Scalability defined / Missing]
   Technical Constraints: [Documented / Not defined]
   Dependencies: [N dependencies identified / None identified]

Overall: [Ready/Needs Refinement/Incomplete]
[Gap details if applicable]

Ready to proceed with /prd_breakdown? [yes/refine/what's missing?]
```

### User Response Handling

**IMPORTANT:** Only recommend `/prd_breakdown` if assessment shows "✅ Ready".

**If assessment shows "✅ Ready" and user says "yes"**:
- Announce PRD complete
- Recommend: `/prd_breakdown`

**If assessment shows "⚠️ Needs Refinement"**:
- **DO NOT recommend breakdown yet**
- Present specific quality issues
- Ask: "Would you like to refine these issues, or proceed with current quality?"
- If user says "proceed": Warn about potential confusion during breakdown, then allow
- If user says "refine": Address issues, then re-assess

**If assessment shows "❌ Incomplete"**:
- **DO NOT recommend breakdown** - missing required items
- Present gap analysis clearly
- Ask user which gap to address first
- Work on gaps until assessment shows "Ready" or "Needs Refinement"

**"refine" or "what's missing?"**:
1. Provide detailed gap analysis from completeness criteria
2. Ask user which gap to address first
3. Work on that gap
4. **Re-assess** (repeat assessment process)

**User requests specific addition**:
1. Update relevant section
2. Apply discovery updates if needed
3. **Re-assess** (repeat assessment process)

---

## Compaction Survival

**Before each major action:**
1. Check if documentation exists (via project-documentation skill)
2. If exists, load current state
3. Check which checklist items are complete
4. Resume from where left off

**State tracking:**
- Documentation is source of truth (not conversation memory)
- Can resume even after compaction
- User sees continuous progress in Confluence/files

---

## Communication Style

**Progress indicators:**
- "Working on Product Strategy (1/5)"
- "✅ Product Strategy complete (1/5)"
- "Working on Product Definition (2/5)"
- "✅ Product Reference complete (3/5)"
- "Working on Product Decisions (4/5)"
- "Working on Competitive Research (5/5)"

**Discovery updates:**
- Always announce with "🔄 Discovery Update: [Section]"
- Brief explanation of what changed

**User interaction:**
- Ask specific questions (not open-ended "what next?")
- Validate understanding before writing docs
- Present assessment with clear options

**Readiness decisions:**
- Provide concrete assessment (not subjective)
- Explain why gaps matter
- Let user decide if "good enough"

---

## Cost Tracking

Track costs for this command using the agent summaries format.

### Baseline Entry (Start of Command)

At the start of the command, write a baseline entry to the tracking file:

```bash
# Create tracking file in .scope/tracking/commands/
TRACKING_DIR=".scope/tracking/commands"
mkdir -p "$TRACKING_DIR"
TRACKING_FILE="$TRACKING_DIR/prd_refine-$(date +%Y%m%d-%H%M%S).jsonl"

# Write baseline entry
echo '{"agent":"baseline","completed_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}' > "$TRACKING_FILE"
```

### Summary Entry (End of Command)

At the end of the command, write a summary entry and calculate costs:

```bash
# Write command summary entry
echo '{"agent":"prd_refine","session_id":"'"$CLAUDE_SESSION_ID"'","completed_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}' >> "$TRACKING_FILE"

# Calculate and store costs
src/commands/scripts/agents-tokens.sh --aggregate "$TRACKING_FILE" --storeInSummaries
```

### Output

The cost summary is appended to the tracking file and output to console:

```json
{
  "baseline": "2025-01-26T10:00:00Z",
  "file": ".scope/tracking/commands/prd_refine-20250126-100000.jsonl",
  "agents": [
    {"agent": "prd_refine", "session_id": "abc123", "cost_usd": 0.0523}
  ],
  "total_cost_usd": 0.0523
}
```

---

## Example Session

```
User: /prd_refine AquaForge
Assistant: Starting PRD refinement for AquaForge. Checklist: Strategy, Definition, Reference, Research.
   What problem does AquaForge solve?

User: Developers waste time understanding code intent during PR reviews
```