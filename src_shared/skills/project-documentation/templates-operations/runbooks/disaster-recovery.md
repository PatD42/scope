# Disaster Recovery Runbook

## Overview

Disaster recovery plan and failover procedures. Covers RTO/RPO targets, backup strategy, failover procedures, and recovery validation.

## Prerequisites

- Required access/permissions: {infrastructure admin, database admin, DNS admin}
- Required tools: {cloud CLI, database tools, DNS management}
- Related docs: [Database Runbook](database.md), [Environments](../environments.md), [Deployment Runbook](deployment.md)

## Recovery Objectives

| Metric | Target | Current Capability | Notes |
|--------|--------|--------------------|-------|
| **RTO** (Recovery Time Objective) | {X hours} | {current estimate} | {max acceptable downtime} |
| **RPO** (Recovery Point Objective) | {X hours} | {current backup frequency} | {max acceptable data loss} |

## Backup Strategy

| Component | Method | Frequency | Retention | Location | Tested |
|-----------|--------|-----------|-----------|----------|--------|
| Database | {automated snapshot} | {daily} | {30 days} | {cross-region} | {date} |
| Object storage | {versioning/replication} | {continuous} | {90 days} | {cross-region} | {date} |
| Application config | {git repo} | {on change} | {indefinite} | {git remote} | {N/A} |
| Secrets | {secrets manager} | {on change} | {versioned} | {same provider} | {date} |
| Infrastructure code | {git repo} | {on change} | {indefinite} | {git remote} | {N/A} |

## Disaster Scenarios

### Scenario 1: Single Service Failure

**Impact**: {one service down, partial degradation}
**RTO**: {X minutes}

#### Steps

1. Identify failed service from monitoring alerts
2. Attempt restart
3. If restart fails, redeploy from last known good version
4. Verify service health

---

### Scenario 2: Database Failure

**Impact**: {full application down}
**RTO**: {X hours}

#### Steps

```bash
# 1. Assess the failure
{check database status command}

# 2. If recoverable (e.g., connection issue):
{restart/reconnect command}

# 3. If not recoverable — restore from backup:
{see Database Runbook — Restore Database section}

# 4. Point application to restored database
{update connection config}

# 5. Verify data integrity
{integrity check queries}
```

---

### Scenario 3: Region / Zone Outage

**Impact**: {full system down in affected region}
**RTO**: {X hours}

#### Steps

1. Confirm outage via cloud provider status page
2. Activate failover region/zone (if multi-region)
3. Update DNS to point to failover environment
4. Verify failover environment is healthy
5. Once primary region recovers, plan failback

```bash
# Failover DNS update
{DNS update command}

# Verify failover
{health check against failover endpoint}
```

---

### Scenario 4: Security Breach / Data Compromise

**Impact**: {varies — data exposure, system compromise}
**RTO**: {immediate containment, X hours full recovery}

#### Steps

1. **Contain**: Isolate affected systems, revoke compromised credentials
2. **Assess**: Determine scope of breach
3. **Recover**: Restore from pre-breach backup if needed
4. **Harden**: Patch vulnerability, rotate all credentials
5. **Report**: Notify stakeholders, legal, and (if required) regulators

See [Networking & Security Runbook](networking-security.md) — Respond to Security Incident.

---

## Failover Procedures

### DNS Failover

```bash
# Update DNS to failover target
{DNS update command}

# Verify DNS propagation
dig {domain}
```

### Database Failover (Promote Replica)

```bash
# Promote read replica to primary
{promote command}

# Update application connection string
{config update command}

# Verify application connects to new primary
{health check}
```

---

## DR Testing

**Frequency**: {quarterly / semi-annually}

### Test Plan

1. [ ] Tabletop exercise — walk through scenarios with team
2. [ ] Backup restore test — restore database backup to staging
3. [ ] Failover test — simulate region outage and failover
4. [ ] Full DR drill — simulate complete outage, measure actual RTO/RPO

### Last DR Test

| Test Type | Date | Result | RTO Achieved | RPO Achieved | Issues Found |
|-----------|------|--------|-------------|-------------|-------------|
| {type} | {date} | {Pass/Fail} | {actual time} | {actual data loss} | {issues} |

## Communication Plan

| Audience | Channel | When | Template |
|----------|---------|------|----------|
| Engineering team | {Slack #incidents} | {immediately} | {incident declared message} |
| Management | {email/Slack} | {within 15 min} | {brief impact summary} |
| Customers | {status page} | {within 30 min} | {customer-facing status update} |
| Post-incident | {meeting + doc} | {within 48 hours} | {postmortem template} |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Backup restore fails | Incompatible version, corrupt backup | Try older backup, verify backup integrity |
| DNS failover slow | High TTL on DNS records | Pre-lower TTL before planned DR tests |
| Failover region not ready | Data not replicated, infra not provisioned | Verify replication lag, check IaC state |
| Application errors after restore | Missing data from RPO gap | Identify gap, manually reconcile if possible |
