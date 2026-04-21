# Common Issues & Resolutions

## Overview

Known operational issues, their symptoms, root causes, and resolutions. Updated as new issues are encountered and resolved.

## Issue Log

### {Issue Title}

**Symptoms**: {what the user or monitoring sees}
**Root Cause**: {what actually went wrong}
**Frequency**: {one-time / recurring / resolved permanently}
**Last Occurred**: {date}

**Resolution**:

```bash
# Step-by-step fix
{commands}
```

**Prevention**: {what was done to prevent recurrence, or what should be done}

---

### Application Returns 502/503

**Symptoms**: Users see "Bad Gateway" or "Service Unavailable"
**Root Cause**: Application crashed, health check failing, or deployment in progress

**Resolution**:

```bash
# 1. Check if service is running
{service status command}

# 2. Check recent logs for crash reason
{log query command}

# 3. Restart service if needed
{restart command}

# 4. If during deployment, wait for rollout to complete or rollback
{rollback command if needed}
```

**Prevention**: Improve health checks, add readiness probes, increase graceful shutdown timeout

---

### Database Connection Pool Exhausted

**Symptoms**: Application errors with "too many connections" or connection timeout
**Root Cause**: Connection leak, traffic spike, or pool misconfigured

**Resolution**:

```bash
# 1. Check active connections
{active connections query}

# 2. Kill idle connections if needed
{kill connections command}

# 3. Restart application to reset pool
{restart command}

# 4. Increase pool size if appropriate
{config change}
```

**Prevention**: Fix connection leaks, use connection pooler (PgBouncer), tune pool size

---

### Disk Space Full

**Symptoms**: Write errors, application crashes, database refusing writes
**Root Cause**: Log accumulation, temp files, data growth

**Resolution**:

```bash
# 1. Identify what's using space
du -sh /* | sort -rh | head -20

# 2. Clean logs / temp files
{cleanup command}

# 3. If database disk, increase storage
{increase storage command}
```

**Prevention**: Set up log rotation, disk usage alerts, auto-expanding storage

---

### High Memory Usage / OOM Kills

**Symptoms**: Service restarts, OOM errors in logs, degraded performance
**Root Cause**: Memory leak, undersized instance, traffic spike

**Resolution**:

```bash
# 1. Check memory usage
{memory check command}

# 2. Restart service (immediate relief)
{restart command}

# 3. Scale up if undersized
{scale command}
```

**Prevention**: Profile memory usage, fix leaks, set appropriate resource limits

---

## Template for New Issues

Copy this template when documenting a new issue:

```markdown
### {Issue Title}

**Symptoms**: {what is observed}
**Root Cause**: {why it happened}
**Frequency**: {one-time / recurring / resolved permanently}
**Last Occurred**: {date}

**Resolution**:

\```bash
# Steps to fix
{commands}
\```

**Prevention**: {how to prevent recurrence}
```
