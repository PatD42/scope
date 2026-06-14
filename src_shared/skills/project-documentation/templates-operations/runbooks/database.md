# Database Runbook

## Overview

Procedures for database administration including backups, restores, migrations, scaling, and performance management.

## Prerequisites

- Required access/permissions: {DBA role, cloud database admin}
- Required tools: {psql/mysql/mongosh CLI, migration tool, cloud CLI}
- Related docs: [Backend Database Specs](../../architecture/backend/13-specs/database/)

## Database Inventory

| Database | Engine | Version | Hosting | Environment | Size | Backup |
|----------|--------|---------|---------|-------------|------|--------|
| {name} | {PostgreSQL/MySQL/etc.} | {version} | {Cloud SQL/RDS/etc.} | {Prod/Staging} | {GB} | {schedule} |

## Connection Details

| Environment | Host | Port | Database | Connection Method |
|------------|------|------|----------|------------------|
| Production | {host or proxy} | {port} | {db name} | {direct/tunnel/proxy} |
| Staging | {host} | {port} | {db name} | {direct/tunnel} |

**Connection string pattern**: `{engine}://{user}:{password}@{host}:{port}/{database}`

**Credentials location**: {Secrets Manager path}

## Procedures

### Connect to Database

**Risk**: Low (read), Medium (write)

```bash
# Via cloud proxy (recommended for production)
{proxy start command}

# Direct connection
{direct connection command}

# Via bastion/tunnel
{tunnel command}
```

---

### Backup Database

**When**: Before migrations, on schedule, before risky operations
**Who**: {required role}
**Risk**: Low

#### Automated Backups

{Description of automated backup — cloud provider managed, cron job, etc.}

```bash
# Verify last backup
{check backup status command}
```

#### Manual Backup

```bash
# 1. Create manual backup/snapshot
{backup command}

# 2. Verify backup
{verify command}
```

---

### Restore Database

**When**: Data loss, corruption, migration rollback
**Who**: {required role}
**Risk**: High
**Estimated Duration**: {depends on size — X minutes per GB}

#### Steps

```bash
# 1. Identify backup to restore from
{list backups command}

# 2. Stop application traffic (if full restore)
{stop/drain command}

# 3. Restore from backup
{restore command}

# 4. Verify data integrity
{verification query}

# 5. Resume application traffic
{resume command}
```

#### Validation

```bash
# Check row counts on key tables
{count query}

# Check latest records
{latest records query}
```

---

### Run Schema Migration

**When**: Application release requires schema changes
**Who**: {required role}
**Risk**: High
**Estimated Duration**: {varies — check migration size}

#### Pre-Migration Checklist

- [ ] Backup taken
- [ ] Migration tested on staging
- [ ] Rollback migration prepared
- [ ] Maintenance window communicated (if needed)
- [ ] Application compatible with both old and new schema (if zero-downtime)

#### Steps

```bash
# 1. Check pending migrations
{pending migrations command}

# 2. Run migration
{run migration command}

# 3. Verify schema
{verify schema command}
```

#### Rollback

```bash
# Revert last migration
{rollback migration command}
```

---

### Scale Database

**When**: Performance degradation, capacity planning, traffic increase
**Who**: {required role}
**Risk**: Medium (may cause brief unavailability)

#### Vertical Scaling (More Resources)

```bash
# Resize instance
{resize command}
# Note: may cause brief restart
```

#### Horizontal Scaling (Read Replicas)

```bash
# Create read replica
{create replica command}

# Update application to use replica for reads
{config change}
```

---

### Performance Investigation

**When**: Slow queries, high CPU/memory, connection pool exhaustion
**Who**: {required role}
**Risk**: Low

#### Steps

```bash
# 1. Check active connections
{active connections query}

# 2. Find slow queries
{slow query log / pg_stat_statements query}

# 3. Check table sizes and bloat
{table size query}

# 4. Review index usage
{index usage query}

# 5. Analyze problematic query
EXPLAIN ANALYZE {query};
```

---

## Maintenance Tasks

| Task | Frequency | Automated | Procedure |
|------|-----------|-----------|-----------|
| Vacuum/Optimize | {daily/weekly} | {Yes/No} | {command} |
| Index rebuild | {monthly} | {Yes/No} | {command} |
| Log rotation | {daily} | {Yes/No} | {command} |
| Stats update | {daily} | {Yes/No} | {command} |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Connection refused | Max connections reached, instance down | Check connection count, restart if needed |
| Slow queries | Missing index, table bloat, lock contention | Run EXPLAIN, add index, vacuum |
| Disk full | Data growth, WAL/binlog accumulation | Increase storage, archive old data, clean logs |
| Replication lag | Heavy write load, network issues | Check replica status, scale up replica |
| Migration failed | Schema conflict, timeout, lock | Check error, fix schema, retry with lock timeout |
