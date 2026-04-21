# Scheduled Maintenance

## Overview

Regular maintenance tasks, their schedules, and procedures. Keeps the system healthy and prevents issues from accumulating.

## Maintenance Calendar

| Task | Frequency | Window | Duration | Owner | Automated | Impact |
|------|-----------|--------|----------|-------|-----------|--------|
| {Database vacuum} | {Weekly} | {Sunday 02:00 UTC} | {30 min} | {DBA} | {Yes} | {None} |
| {Log rotation} | {Daily} | {00:00 UTC} | {5 min} | {Ops} | {Yes} | {None} |
| {Certificate renewal check} | {Weekly} | {Monday 09:00} | {5 min} | {Ops} | {Yes} | {None} |
| {Dependency update review} | {Monthly} | {First Monday} | {2-4 hours} | {Dev} | {No} | {None} |
| {Backup verification} | {Monthly} | {First Sunday} | {1-2 hours} | {DBA} | {No} | {None} |
| {Access audit} | {Quarterly} | {Quarter start} | {2-4 hours} | {Security} | {No} | {None} |
| {DR test} | {Semi-annually} | {Planned} | {4-8 hours} | {All} | {No} | {Possible downtime} |

## Procedures

### Database Maintenance

**Frequency**: {weekly}
**Automated**: {Yes/No}

```bash
# Vacuum and analyze (PostgreSQL)
{vacuum command}

# Check for unused indexes
{index usage query}

# Review table bloat
{bloat query}
```

---

### Log Cleanup

**Frequency**: {daily/weekly}
**Automated**: {Yes/No}

```bash
# Rotate and compress logs
{log rotation command}

# Archive old logs to cold storage
{archive command}

# Verify log disk usage
df -h {log partition}
```

---

### Certificate Renewal Check

**Frequency**: {weekly}
**Automated**: {Yes/No}

```bash
# Check all certificate expiry dates
{cert check command}

# Alert if any expire within 30 days
{alert check}
```

---

### Dependency Updates

**Frequency**: {monthly}
**Automated**: {Dependabot/Renovate for PRs, manual merge}

1. Review automated PRs for dependency updates
2. Check for security advisories
3. Update and test in staging
4. Merge and deploy

---

### Backup Verification

**Frequency**: {monthly}
**Automated**: {No — manual verification}

1. Select a recent backup
2. Restore to isolated environment
3. Verify data integrity (row counts, checksums)
4. Test application against restored data
5. Document result

---

### Access Audit

**Frequency**: {quarterly}
**Automated**: {No}

See [Identity & Access Management](../runbooks/identity-access.md) — Audit Access section.

---

## Maintenance Windows

**Standard window**: {day/time UTC}
**Communication**: Notify in {channel} at least {X hours/days} before
**Approval required**: {Yes for production / No for staging}

### Requesting a Maintenance Window

1. Create request in {ticket system}
2. Include: scope, duration, impact, rollback plan
3. Get approval from {required approver}
4. Announce in {channel} with schedule
5. Execute during window
6. Confirm completion and all-clear
