# Architecture - Context & Scope

---

## System Context (C4 Level 1)

<!-- Diagram and description showing the system and its external dependencies. -->

### Context Diagram

<!-- Insert C4 Context diagram here (Level 1) using Mermaid -->

```mermaid
graph LR
    User[User]
    Admin[Administrator]

    subgraph "System Boundary"
        System[Your System]
    end

    ExtAPI[External API]
    DB[(External Database)]
    EmailSvc[Email Service]

    User -->|Uses| System
    Admin -->|Manages| System
    System -->|Queries| ExtAPI
    System -->|Stores| DB
    System -->|Sends| EmailSvc

    classDef actor fill:#f9f,stroke:#333,stroke-width:2px
    classDef system fill:#9cf,stroke:#333,stroke-width:3px
    classDef external fill:#fcf,stroke:#333,stroke-width:2px

    class User,Admin actor
    class System system
    class ExtAPI,DB,EmailSvc external
```

### External Interfaces

<!-- What external systems, users, and services does this system interact with? -->

| External Entity | Type | Relationship | Protocol/Interface |
|----------------|------|--------------|-------------------|
| | User/System | Sends/Receives | HTTP/API/etc. |

## Business Context

<!-- What business processes does this system support? -->

### Input/Output

**Inputs**:
-

**Outputs**:
-

## Technical Context

<!-- What are the technical communication channels and protocols? -->

| Channel | Protocol | Data Format | Security |
|---------|----------|-------------|----------|
|         | REST API | JSON        | TLS 1.3  |

---

