# Backend Architecture Overview

## Purpose

{High-level description of the backend system. What it does, who it serves, how it fits into the overall system.}

## Service Landscape

{Summary of all backend services and their roles.}

| Service | Purpose | Technology | Status |
|---------|---------|-----------|--------|
| {service_name} | {what it does} | {tech stack} | {Implemented/Planned} |

## Communication Patterns

{How services communicate: REST, message queues, shared database, etc.}

## Shared Infrastructure

{Shared components used across services: database, S3, embedding service, etc.}

## Key Constraints

{Backend-specific constraints: Python version, async requirements, deployment model, etc.}

## Related Documentation

- [System Architecture](../05-building-blocks.md) — C4 L2/L3 component view
- [Backend Services](services.md) — Detailed service catalog
- [Backend Data Architecture](data.md) — Database schemas and data flows
- [Backend ADRs](adr/) — Backend-specific architecture decisions
