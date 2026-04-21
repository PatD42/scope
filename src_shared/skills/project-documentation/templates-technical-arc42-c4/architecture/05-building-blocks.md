# Architecture - Building Block View

---

## Container View (C4 Level 2)

<!-- Show the high-level shape of the software architecture and how responsibilities are distributed. -->

### Container Diagram

<!-- Insert C4 Container diagram here (Level 2) using Mermaid -->

```mermaid
graph TB
    User[User/Client]

    subgraph "Application Layer"
        WebApp[Web Application]
        API[API Service]
    end

    subgraph "Data Layer"
        DB[(Database)]
        Cache[(Cache)]
    end

    User -->|HTTPS| WebApp
    User -->|HTTPS| API
    WebApp -->|REST| API
    API -->|SQL| DB
    API -->|Read/Write| Cache

    classDef client fill:#f9f,stroke:#333,stroke-width:2px
    classDef app fill:#9cf,stroke:#333,stroke-width:2px
    classDef data fill:#fcf,stroke:#333,stroke-width:2px

    class User client
    class WebApp,API app
    class DB,Cache data
```

### Containers

| Container | Technology | Responsibility |
|-----------|-----------|----------------|
| | | |

## Component View (C4 Level 3)

<!-- Decompose each container to show major structural building blocks. -->

### [Container Name] Components

<!-- Insert C4 Component diagram for this container (Level 3) using Mermaid -->

```mermaid
graph TD
    subgraph "API Service"
        Controller[API Controller]
        Service[Business Logic]
        Repository[Data Repository]
    end

    Controller -->|Uses| Service
    Service -->|Uses| Repository
    Repository -->|Queries| DB[(Database)]

    classDef component fill:#9cf,stroke:#333,stroke-width:2px
    classDef data fill:#fcf,stroke:#333,stroke-width:2px

    class Controller,Service,Repository component
    class DB data
```

#### Component: [Component Name]

**Responsibility**:

**Dependencies**:
-

**Interfaces**:
-

**Technical Specifications**: <!-- Link to detailed specs -->
- API Contract: [13-specs/api/{service}.yaml](./13-specs/api/)
- Data Schema: [13-specs/schemas/domain/{entity}.yaml](./13-specs/schemas/domain/)
- Database: [13-specs/database/](./13-specs/database/)
- Error Codes: [13-specs/errors/by-domain/{domain}.yaml](./13-specs/errors/by-domain/)

## Whitebox View

<!-- Detailed view of key components. Create child pages if exceeding 300 words per component. -->

### [Component Name] Internals

**Structure**:

**Key Classes/Modules**:
-

**Important Patterns**:
-

---

