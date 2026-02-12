# Database Specifications

This directory contains database schemas for all database types used in the system.

## Structure

```
database/
├── sql/              # Relational databases (PostgreSQL, MySQL, SQLite)
│   ├── schema.sql    # Complete current schema
│   └── migrations/   # Versioned migrations
├── nosql/            # Document databases (MongoDB, DynamoDB, Firestore)
│   └── collections/  # Collection schemas
├── graph/            # Graph databases (Neo4j, Neptune, ArangoDB)
│   └── schema/       # Node and relationship definitions
└── vector/           # Vector databases (pgvector, Pinecone, Weaviate)
    └── indexes/      # Vector index definitions
```

## Conventions

### SQL (Relational)
- Use PostgreSQL syntax as baseline (most portable)
- Include indexes, constraints, and triggers
- Migrations follow `NNN-description.sql` format

### NoSQL (Document)
- Use JSON Schema to define document structure
- Include validation rules and indexes
- Document TTL and partitioning strategies

### Graph
- Define node labels with properties
- Define relationship types with properties
- Include Cypher/Gremlin query examples

### Vector
- Specify embedding dimensions
- Define distance metrics (cosine, euclidean, dot)
- Document chunking and indexing strategies

## Update Process

1. Epic refinement produces DB specs in `./doc/epics/{epic-id}/specs/database/`
2. `/update_spec` merges into appropriate subdirectory
3. For SQL: generates new migration file
4. Changelog in each file tracks epic origin
