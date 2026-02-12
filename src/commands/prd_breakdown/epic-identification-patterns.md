# Epic Identification Patterns

Patterns for identifying epic boundaries from a capability map.

## What is an Epic?

An epic is a coherent unit of work that:
- Delivers standalone value to users
- Can be developed semi-independently
- Has clear technical boundaries
- Takes 2-8 weeks to complete (with a small team)

## Identification Strategies

### 1. Capability-Based Boundaries

Group related capabilities that serve a common user goal.

**Pattern:** Capabilities that share the same actor and domain context

**Example from AquaForge PRD:**
```
Epic: User Authentication
Capabilities:
- User Registration
- Login/Logout
- Password Reset
- Role-Based Access Control
- Session Management

Why: These capabilities all serve the goal "secure user access" and share auth domain
```

**When to use:**
- Capabilities are tightly coupled (hard to implement separately)
- Capabilities share the same data models
- User story flows span multiple capabilities

---

### 2. Component-Based Boundaries

Group capabilities that map to a single system component.

**Pattern:** Capabilities that would live in the same microservice/module

**Example:**
```
Epic: API Gateway Implementation
Capabilities:
- Request Routing
- Load Balancing
- Rate Limiting
- API Versioning
- Request/Response Transformation

Why: These all belong to the API Gateway component
```

**When to use:**
- System architecture has clear component boundaries
- Capabilities share infrastructure concerns
- Team structure aligns with components

---

### 3. Integration-Based Boundaries

Group capabilities around external system integration.

**Pattern:** Capabilities that interact with the same third-party service

**Example:**
```
Epic: Payment Integration (Stripe)
Capabilities:
- Process Payments
- Handle Refunds
- Manage Subscriptions
- Webhook Processing
- Payment Method Management

Why: All interact with Stripe API
```

**When to use:**
- Integration has significant complexity (auth, error handling, webhooks)
- Multiple capabilities depend on the same external service
- Integration failure affects multiple features

---

### 4. Data-Based Boundaries

Group capabilities around a core data entity lifecycle.

**Pattern:** CRUD + business operations for a key entity

**Example:**
```
Epic: Repository Management
Capabilities:
- Create/Delete Repository
- Update Repository Metadata
- Repository Permissions
- Repository Search
- Repository Statistics

Why: All operate on Repository entity
```

**When to use:**
- Entity has complex lifecycle or business rules
- Multiple user roles interact with the entity
- Entity is central to the domain model

---

### 5. Infrastructure-Based Boundaries

Group capabilities that provide foundational technical services.

**Pattern:** Cross-cutting concerns or platform capabilities

**Example:**
```
Epic: Monitoring & Observability
Capabilities:
- Logging Infrastructure
- Metrics Collection
- Distributed Tracing
- Alerting
- Performance Dashboard

Why: Foundational technical capabilities needed by all features
```

**When to use:**
- Capabilities are non-functional requirements
- Capabilities don't directly deliver user features
- Capabilities enable other epics

---

### 6. User Journey-Based Boundaries

Group capabilities that complete an end-to-end user workflow.

**Pattern:** Capabilities needed for a complete user story

**Example:**
```
Epic: Onboarding Experience
Capabilities:
- Account Setup
- Initial Project Creation
- Guided Tour
- Sample Data Import
- First Success Milestone

Why: These form a cohesive onboarding journey
```

**When to use:**
- User experience requires multiple capabilities to feel complete
- Capabilities are ordered in a sequence
- Marketing/product wants to launch a "complete" feature

---

## Anti-Patterns (What NOT to do)

### ❌ Too Broad: "Everything Epic"

```
Epic: Complete Application
Capabilities: [all 30 capabilities]
```

**Problem:** Not actionable, no prioritization possible, months of work

**Fix:** Break into 5-10 smaller epics using patterns above

---

### ❌ Too Granular: "Single Feature Epic"

```
Epic: Add Email Validation
Capabilities: Email Validation
```

**Problem:** Too small, creates overhead, should be a story not epic

**Fix:** Combine with related capabilities (e.g., "User Registration" epic)

---

### ❌ Implementation-Focused: "Tech Stack Epic"

```
Epic: Implement React Frontend
Capabilities: [all UI capabilities]
```

**Problem:** Organized by technology, not value; hard to prioritize

**Fix:** Organize by user value (e.g., "Dashboard UI", "Settings UI")

---

### ❌ Mixed Concerns: "Grab Bag Epic"

```
Epic: Miscellaneous Features
Capabilities: User Export, Admin Logs, Email Templates, API Docs
```

**Problem:** No coherent theme, hard to scope, no clear value story

**Fix:** Each capability becomes part of a themed epic

---

## Decision Framework

When identifying epics from a capability map:

### Step 1: Initial Grouping

Look for natural clusters using patterns 1-6 above. Ask:
- Which capabilities are tightly coupled?
- Which capabilities share data models?
- Which capabilities complete user workflows?

### Step 2: Validate Boundaries

For each proposed epic, check:
- ✅ Can it be developed semi-independently?
- ✅ Does it deliver standalone value?
- ✅ Is scope 2-8 weeks (roughly)?
- ✅ Has clear acceptance criteria?

### Step 3: Check Dependencies

Between epics, identify:
- **Foundation dependencies**: Epic A must complete before Epic B starts
- **Interface dependencies**: Epics need agreed contracts
- **Data dependencies**: Epics share data models

### Step 4: Prioritize

Consider:
- Customer pain points (from Product Strategy)
- Technical foundations (some epics unlock others)
- Risk mitigation (tackle unknowns early)
- Team capacity and skills

---

## Boundary Refinement

If an epic feels too large or too small:

**Too large (>8 weeks):**
- Split by user persona (admin vs user features)
- Split by phase (MVP vs enhancements)
- Split by dependency (foundation vs dependent features)

**Too small (<2 weeks):**
- Merge with related epic
- Expand scope with related capabilities
- Combine with tech debt or infrastructure work

**Uncertain scope:**
- Create a "spike" epic for investigation
- Break into "Phase 1" and "Phase 2" epics
- Use dependency analysis to clarify boundaries
