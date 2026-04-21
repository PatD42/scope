# Product Management Frameworks

Reference guide for product strategy and definition techniques.

## Jobs-to-be-Done (JTBD)

Framework for understanding customer motivation through the "job" they're trying to accomplish.

**Structure:**
```
When [situation], I want to [motivation], so I can [outcome].
```

**Example:**
```
When reviewing pull requests, I want to understand the intent behind code changes,
so I can provide meaningful feedback without reading every line.
```

**Use in PRD:**
- Product Strategy: Customer problems section
- Product Definition: Use case descriptions

## Value Proposition Canvas

Maps product features to customer pains and gains.

**Customer Profile:**
- Customer Jobs (what they're trying to accomplish)
- Pains (obstacles, risks, frustrations)
- Gains (desired outcomes, benefits)

**Value Map:**
- Products & Services (what you offer)
- Pain Relievers (how you address pains)
- Gain Creators (how you create gains)

**Use in PRD:**
- Product Strategy: Vision and customer problems
- Product Definition: Capability map aligned to pains/gains

## Capability Mapping

Functional capabilities organized by theme, independent of implementation.

**Capability = What the system can do (not how)**

**Example Structure:**
```
Authentication & Authorization
├─ User Registration
├─ Login/Logout
├─ Role-based Access Control
└─ Session Management

Data Management
├─ CRUD Operations
├─ Search & Filter
├─ Import/Export
└─ Version Control
```

**Guidelines:**
- Group by business capability theme
- Use verb-noun format (e.g., "Manage Users", not "User Management")
- Keep implementation-agnostic (don't specify "OAuth" or "JWT")
- Each capability should map to user value

**Use in PRD:**
- Product Definition: Capability map section

## Use Case Definition

Describes user interaction with the system to achieve a goal.

**Structure:**
```
Title: [Actor] [Action] [Object]
Actor: [User role]
Goal: [What they want to accomplish]
Preconditions: [Required state before use case]
Main Flow:
  1. [Step 1]
  2. [Step 2]
  ...
Postconditions: [State after successful completion]
```

**Example:**
```
Title: Developer Searches Code by Intent
Actor: Software Developer
Goal: Find code sections related to authentication without knowing exact file names
Preconditions: Codebase has been indexed
Main Flow:
  1. Developer enters natural language query: "how does login work?"
  2. System computes query embedding
  3. System retrieves code sections with similar embeddings
  4. System displays ranked results with context
Postconditions: Developer has relevant code sections to review
```

**Use in PRD:**
- Product Definition: Use cases section

## Market Segmentation

Identify distinct customer groups with different needs.

**Segmentation Dimensions:**
- Industry/Domain (e.g., SaaS, Healthcare, Finance)
- Company Size (e.g., Startup, SMB, Enterprise)
- Use Case (e.g., Code Review, Onboarding, Documentation)
- Technical Maturity (e.g., Early Adopters, Pragmatists)

**Use in PRD:**
- Product Strategy: Target markets section

## Competitive Analysis Framework

**Analysis Dimensions:**
1. **Feature Comparison**: What capabilities do competitors offer?
2. **Positioning**: How do they describe their value proposition?
3. **Pricing**: What's their pricing model and tiers?
4. **Differentiation**: What makes them unique?
5. **Weaknesses**: What gaps or complaints exist?

**Research Sources:**
- Competitor websites (product pages, pricing)
- Customer reviews (G2, Capterra, Reddit)
- Product Hunt comments
- GitHub repos (if open source)
- Documentation quality

**Use in PRD:**
- Product Strategy: Competitive landscape section
- Product Definition: Capability map (identify gaps to fill)

## Glossary Development

Domain terminology with clear definitions.

**Term Structure:**
```
**[Term]**: [Concise definition in one sentence]

[Optional: Extended explanation, context, or examples]

Related terms: [Links to related glossary entries]
```

**Guidelines:**
- Define acronyms on first use
- Avoid circular definitions
- Include examples for ambiguous terms
- Link related concepts

**Use in PRD:**
- Product Reference: Glossary section

## Entity Modeling (High-Level)

Core data concepts without implementation details.

**Entity Structure:**
```
**[Entity Name]**
Purpose: [Why this entity exists]
Key attributes: [3-7 essential properties]
Relationships:
  - [Relationship type] with [Other Entity]
```

**Example:**
```
**Code Fragment**
Purpose: Represents a semantically meaningful section of code (function, class, module)
Key attributes: File path, line range, language, embedding vector, summary
Relationships:
  - Belongs to Repository
  - References other Code Fragments (via imports/calls)
  - Has many Annotations (comments, docs)
```

**Guidelines:**
- High-level only (not database schema)
- Focus on relationships between concepts
- Avoid implementation details (no "VARCHAR(255)")

**Use in PRD:**
- Product Reference: Data entities section
