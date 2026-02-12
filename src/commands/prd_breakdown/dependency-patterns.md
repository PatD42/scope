# Epic Dependency Patterns

Common technical dependency patterns between epics.

## Dependency Types

### 1. Foundation Dependencies (Must-Have-First)

**Pattern:** Epic B cannot start until Epic A is complete

**Example:**
```
Epic A: User Authentication
Epic B: User Profile Management

Dependency: Profile features require authenticated users
Type: Foundation
```

**Identification:**
- Epic B assumes infrastructure/capabilities from Epic A exist
- Epic B's acceptance criteria reference Epic A's deliverables
- No workaround possible (truly blocking)

---

### 2. Interface Dependencies (Contract-First)

**Pattern:** Epics can proceed in parallel if interface contracts are agreed

**Example:**
```
Epic A: API Gateway
Epic B: Microservices (User Service, Order Service)

Dependency: API Gateway needs to route to services
Type: Interface (contracts: API endpoints, auth headers, error format)
```

**Identification:**
- Epics interact at runtime
- Both sides need to agree on data format, protocols
- Can develop in parallel with mocks/stubs after contract defined

---

### 3. Data Dependencies (Schema-First)

**Pattern:** Epics share data models; schema must be defined first

**Example:**
```
Epic A: Repository Management (creates/updates Repository entity)
Epic B: Code Indexing (reads Repository entity)

Dependency: Indexing needs Repository schema (id, url, language, etc)
Type: Data (shared schema)
```

**Identification:**
- Epics read/write the same database tables or entities
- Data model changes in one epic affect the other
- Schema evolution needs coordination

---

### 4. Integration Dependencies (External-First)

**Pattern:** Epic B extends/uses external integration from Epic A

**Example:**
```
Epic A: Stripe Payment Integration (basic payment processing)
Epic B: Subscription Management (recurring payments)

Dependency: Subscriptions require Stripe integration
Type: Integration
```

**Identification:**
- Epic B builds on top of Epic A's external service integration
- Epic A establishes auth, webhook handling, error patterns
- Epic B adds domain-specific workflows

---

### 5. Infrastructure Dependencies (Platform-First)

**Pattern:** Application epics require platform/infrastructure epics

**Example:**
```
Epic A: Monitoring & Logging Infrastructure
Epic B: All feature epics

Dependency: Features need logging/metrics for observability
Type: Infrastructure
```

**Identification:**
- Epic A provides cross-cutting technical capability
- Multiple epics depend on Epic A
- Without Epic A, debugging/operations are difficult

---

### 6. UI/UX Dependencies (Design-First)

**Pattern:** Feature epics require UI framework/design system

**Example:**
```
Epic A: Component Library & Design System
Epic B: Dashboard UI, Settings UI (feature UIs)

Dependency: Feature UIs use design system components
Type: UI/UX
```

**Identification:**
- Epic A establishes visual language, reusable components
- Epic B implements features using Epic A's components
- Consistency and development speed depend on Epic A

---

## Dependency Analysis Process

### Step 1: List All Epic Pairs

For each pair of epics (A, B), ask:
- Does B need anything from A?
- Does A need anything from B?
- Can they proceed in parallel?

### Step 2: Classify Dependencies

For each dependency found:
- **Type**: Foundation, Interface, Data, Integration, Infrastructure, or UI
- **Direction**: A → B (A blocks B) or A ↔ B (mutual)
- **Strength**: Hard blocker vs soft preference

### Step 3: Create Dependency Graph

```
┌─────────────────────────────────┐
│  Authentication (Epic 1)        │
└────────┬───────────┬────────────┘
         │           │
         ▼           ▼
┌────────────┐  ┌─────────────┐
│ Profile    │  │ Dashboard   │
│ (Epic 2)   │  │ (Epic 3)    │
└────────────┘  └──────┬──────┘
                       │
                       ▼
              ┌────────────────┐
              │ Notifications  │
              │ (Epic 4)       │
              └────────────────┘
```

**Foundation dependencies** create this ordering constraint.

---

## Resolving Dependencies

### Strategy 1: Sequence Epics

**When:** Hard foundation dependencies exist

**Action:**
- Epic A must complete before Epic B starts
- Update epic ordering/prioritization
- Communicate dependency to team

**Example:**
```
Sprint 1-2: Authentication
Sprint 3-4: Profile Management (depends on Auth)
Sprint 5-6: Dashboard (depends on Auth + Profile)
```

---

### Strategy 2: Define Contracts Early

**When:** Interface or data dependencies exist

**Action:**
- Define API contracts, data schemas first
- Document in Architecture Decision Records (ADRs)
- Both epics reference contract
- Develop in parallel using mocks/stubs

**Example:**
```
Week 1: Define User API contract (REST endpoints, schemas)
Week 2-4: Frontend epic uses mock API, Backend epic implements contract
Week 5: Integration
```

---

### Strategy 3: Extract Shared Epic

**When:** Multiple epics depend on same capability

**Action:**
- Create new "foundation" epic for shared capability
- Make it highest priority
- Dependent epics wait or use temporary solution

**Example:**
```
Original:
- Epic A: Dashboard (needs auth)
- Epic B: Settings (needs auth)
- Epic C: Reports (needs auth)

Refactored:
- Epic 0: Authentication (NEW - foundation)
- Epic A, B, C: Depend on Epic 0
```

---

### Strategy 4: Simplify/Remove Dependency

**When:** Dependency is soft or creates bottleneck

**Action:**
- Question if dependency is truly necessary
- Find alternative approach that removes dependency
- Simplify Epic B's scope to not need Epic A

**Example:**
```
Epic A: Advanced Search (complex Elasticsearch integration)
Epic B: Product Catalog (wants search)

Simplification: Epic B implements basic SQL search initially
Later: Epic C (Search Enhancement) replaces with Epic A's solution
```

---

### Strategy 5: Stub/Mock Dependencies

**When:** Testing requires completed dependencies

**Action:**
- Create test stubs/mocks for Epic A's outputs
- Epic B can develop and test without waiting
- Integration happens when Epic A completes

**Example:**
```
Epic A: Payment Processing (Stripe integration)
Epic B: Order Checkout (needs payment)

Solution: Epic B uses mock payment service during development
```

---

## Common Dependency Anti-Patterns

### ❌ Circular Dependencies

```
Epic A: User Service (calls Order Service for user's orders)
Epic B: Order Service (calls User Service for user details)
```

**Problem:** Neither can complete without the other

**Fix:**
- Extract shared data to Epic C (User-Order relationship)
- Use eventual consistency (async events)
- Denormalize data (each service stores what it needs)

---

### ❌ Hidden Dependencies

```
Epic A: Frontend Dashboard
Epic B: Backend API

Hidden: Dashboard assumes specific error format, auth headers (undocumented)
```

**Problem:** Integration fails due to mismatched assumptions

**Fix:** Explicitly document interface contracts in ADRs

---

### ❌ Over-Coupled Epics

```
Epic A: User Registration (creates user, sends email, logs event, updates analytics)
Epic B: Email Service
Epic C: Analytics Service

Problem: Epic A tightly coupled to B and C
```

**Fix:**
- Use event-driven architecture (Epic A publishes "UserRegistered" event)
- B and C subscribe independently
- A doesn't depend on B or C

---

### ❌ Assumed Foundations

```
Epic: Machine Learning Model Training

Assumed (but not documented):
- Data pipeline exists
- GPU infrastructure provisioned
- Model registry available
```

**Problem:** Epic blocked by undocumented dependencies

**Fix:**
- Create explicit foundation epics
- Document infrastructure prerequisites
- Validate assumptions during epic refinement

---

## Dependency Documentation

For each dependency, document:

```yaml
dependency:
  from_epic: Authentication (SCOPE-001)
  to_epic: Profile Management (SCOPE-002)
  type: foundation
  description: Profile features require authenticated users
  contract: |
    Authentication provides:
    - JWT token with user_id claim
    - /api/v1/auth/validate endpoint
    - User session middleware
  resolution: Sequential (Auth must complete first)
  risk: High (Profile completely blocked without Auth)
```

Store in:
- Epic documentation (documentation backend)
- Product Definition page (epic dependency map)
- Architecture documentation (system integration view)

---

## Dependency Visualization

### Simple Dependency List

```
Epic 1: Authentication
  ↓ (foundation)
Epic 2: Profile Management
  ↓ (foundation)
Epic 3: Dashboard
  ↓ (interface contract)
Epic 4: Notifications
```

### Dependency Matrix

|          | Epic 1 | Epic 2 | Epic 3 | Epic 4 |
|----------|--------|--------|--------|--------|
| Epic 1   | -      | ✓      | ✓      | -      |
| Epic 2   | -      | -      | ✓      | -      |
| Epic 3   | -      | -      | -      | ✓      |
| Epic 4   | -      | -      | -      | -      |

✓ = Row depends on Column

### Parallel Tracks

```
Track 1 (Sequential):        Track 2 (Parallel):
┌─────────────┐             ┌──────────────┐
│ Auth        │             │ Design System│
└──────┬──────┘             └──────┬───────┘
       │                           │
       ▼                           ▼
┌─────────────┐             ┌──────────────┐
│ Profile     │             │ Component Lib│
└──────┬──────┘             └──────┬───────┘
       │                           │
       └────────┬──────────────────┘
                ▼
         ┌─────────────┐
         │ Dashboard   │
         └─────────────┘
```

Shows epics that can run in parallel vs must be sequential.
