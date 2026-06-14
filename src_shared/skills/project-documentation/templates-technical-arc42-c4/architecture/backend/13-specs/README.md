# Architecture - Technical Specifications

This directory contains living technical contracts that evolve across epics.

## Structure

```
13-specs/
├── api/                    # OpenAPI specifications per service
│   └── {service}.yaml
├── schemas/                # JSON Schema type definitions
│   ├── domain/             # Business domain types
│   └── common/             # Shared types (error, pagination, etc.)
├── database/               # Database schemas (all DB types)
│   ├── sql/                # Relational (PostgreSQL, MySQL)
│   ├── nosql/              # Document (MongoDB, DynamoDB)
│   ├── graph/              # Graph (Neo4j, Neptune)
│   └── vector/             # Vector (pgvector, Pinecone)
└── errors/                 # Error taxonomy and codes
```

## Relationship to Arc42

| Arc42 Section | Specs Reference |
|---------------|-----------------|
| 05-building-blocks | `api/` - Service contracts |
| 06-runtime | `schemas/` - Message types |
| 08-cross-cutting | `errors/` - Error handling |

## Update Process

1. **Epic refinement** generates specs in `./doc/epics/{epic-id}/specs/`
2. **`/update_spec`** merges epic specs into this directory
3. **Changelog** at bottom of each file tracks which epic added what

## Format Standards

- **API**: OpenAPI 3.0.3+
- **Schemas**: JSON Schema Draft 2020-12
- **Database**: Native DDL/schema format per DB type
- **Errors**: YAML taxonomy

## For Claude Flow

This directory is the source of truth for implementation. All specs are in standard formats consumable by autonomous agents.
