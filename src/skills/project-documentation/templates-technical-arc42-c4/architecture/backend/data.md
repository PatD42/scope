# Backend Data Architecture

## Storage Systems

| System | Technology | Purpose | Owner Service |
|--------|-----------|---------|---------------|
| {name} | {PostgreSQL, MinIO, etc.} | {what it stores} | {which service manages it} |

## Database Schemas

### {Schema/Table Group Name}

**Database:** {database name}
**Schema file:** {path to migration or schema doc}

{Description of table group purpose.}

**Key Tables:**
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| {table} | {purpose} | {important columns} |

**Relationships:**
- {Entity A} → {Entity B}: {relationship type and meaning}

## Object Storage (S3)

**Bucket:** {bucket name}
**Key Pattern:** {how keys are structured}

| Object Type | Key Format | Content | Written By | Read By |
|-------------|-----------|---------|-----------|---------|
| {type} | {pattern} | {what it contains} | {service} | {service} |

## Data Flows

{How data moves through the system. Key pipelines and transformation steps.}

```
{Source} → {Service A} → {Storage} → {Service B} → {Output}
```

## Migration Strategy

{How schema changes are managed: Alembic, manual SQL, etc.}

## Related Documentation

- [Backend Overview](overview.md) — Architecture summary
- [Backend Services](services.md) — Service catalog
- [Cross-Cutting: Domain](../08-cross-cutting/domain.md) — Domain model
