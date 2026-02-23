# Backend Services

## Service Catalog

{Detailed description of each backend service.}

### {Service Name}

**Location:** `services/{name}/`
**Technology:** {Python, FastAPI, etc.}
**Status:** {Implemented | In Development | Planned}

**Responsibilities:**
- {Responsibility 1}
- {Responsibility 2}

**Interfaces:**
- {API endpoints or internal contracts}

**Dependencies:**
- {External: database, S3, LLM APIs}
- {Internal: shared modules}

**Configuration:**
- {Key config entries from config.yaml}

---

## Shared Modules

**Location:** `shared/`

### {Module Name}
**Path:** `shared/{path}/`
**Purpose:** {What it provides to services}
**Used By:** {Which services depend on it}

---

## Service Interaction Matrix

| From → To | {Service A} | {Service B} | {Shared} |
|-----------|-------------|-------------|----------|
| {Service A} | — | {interaction} | {usage} |
| {Service B} | {interaction} | — | {usage} |

## Related Documentation

- [Backend Overview](overview.md) — Architecture summary
- [Backend Data Architecture](data.md) — Database and storage
- [System Runtime](../06-runtime.md) — Cross-service interaction flows
