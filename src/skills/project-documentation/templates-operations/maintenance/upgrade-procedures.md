# Upgrade Procedures

## Overview

Playbooks for upgrading major system components: OS, runtime, database engine, platform versions, and key dependencies.

## Upgrade Inventory

| Component | Current Version | Target Version | Upgrade Path | Risk | Last Upgraded |
|-----------|----------------|---------------|-------------|------|--------------|
| {OS / base image} | {version} | {version} | {in-place / rebuild} | {Medium} | {date} |
| {Runtime (Python/Node/etc.)} | {version} | {version} | {image update} | {Medium} | {date} |
| {Database engine} | {version} | {version} | {managed upgrade / dump-restore} | {High} | {date} |
| {Container platform} | {version} | {version} | {rolling update} | {Medium} | {date} |
| {Identity provider} | {version} | {version} | {managed / manual} | {High} | {date} |

## General Upgrade Process

### Pre-Upgrade Checklist

- [ ] Read release notes and changelog for breaking changes
- [ ] Check compatibility with current dependencies
- [ ] Test upgrade in staging environment
- [ ] Create backup / snapshot of current state
- [ ] Prepare rollback plan
- [ ] Schedule maintenance window (if downtime required)
- [ ] Notify team and stakeholders

### Post-Upgrade Checklist

- [ ] Run full test suite
- [ ] Verify all services healthy
- [ ] Check monitoring for anomalies
- [ ] Confirm no increase in error rate
- [ ] Update version in documentation
- [ ] Remove old version artifacts after grace period

---

## Specific Upgrade Procedures

### Runtime Version Upgrade (Python / Node.js / etc.)

**Risk**: Medium
**Estimated Duration**: {X hours including testing}

#### Steps

```bash
# 1. Update version in build configuration
{update Dockerfile / .python-version / .node-version / etc.}

# 2. Update dependencies for compatibility
{dependency update commands}

# 3. Build and test locally
{build and test commands}

# 4. Deploy to staging
{deploy to staging}

# 5. Run full test suite against staging
{test command}

# 6. Deploy to production
{deploy to production}
```

#### Rollback

```bash
# Revert to previous image/version
{rollback command}
```

---

### Database Engine Upgrade

**Risk**: High
**Estimated Duration**: {X hours}

#### Steps

```bash
# 1. Create full backup
{backup command}

# 2. Test upgrade in staging
{staging upgrade command}

# 3. Verify staging data integrity
{integrity checks}

# 4. Schedule maintenance window for production

# 5. Stop application traffic
{drain/stop command}

# 6. Perform upgrade
{upgrade command — depends on managed vs. self-hosted}

# 7. Verify database accessible and data intact
{verification queries}

# 8. Resume application traffic
{resume command}

# 9. Monitor for issues
{monitoring checks}
```

#### Rollback

```bash
# Restore from pre-upgrade backup
{restore command}
```

---

### Container / Platform Upgrade

**Risk**: Medium
**Estimated Duration**: {X hours}

#### Steps

```bash
# 1. Update platform version in infrastructure code
{IaC update}

# 2. Apply to staging
{apply to staging command}

# 3. Verify all workloads healthy on staging
{health check}

# 4. Apply to production (rolling update)
{apply to production command}

# 5. Monitor rollout
{monitoring command}
```

---

### Identity Provider Upgrade (Keycloak / Auth0 / etc.)

**Risk**: High (auth downtime = full outage)
**Estimated Duration**: {X hours}

#### Steps

```bash
# 1. Backup IdP configuration and database
{backup command}

# 2. Test upgrade in staging IdP instance
{staging upgrade}

# 3. Verify login flows work in staging
{test login, SSO, token refresh}

# 4. Schedule maintenance window

# 5. Upgrade production IdP
{upgrade command}

# 6. Verify all authentication flows
{test each auth flow}

# 7. Monitor for authentication errors
{log/metric check}
```

#### Rollback

```bash
# Restore from backup
{restore IdP backup}
```

---

## Dependency Update Policy

| Dependency Type | Update Frequency | Auto-Merge | Approval Required |
|----------------|-----------------|-----------|-------------------|
| Security patches | Immediately | {Yes if tests pass} | {No} |
| Minor versions | {Monthly} | {Yes if tests pass} | {No} |
| Major versions | {Quarterly review} | {No} | {Yes — tech lead} |

## Related Documentation

- [Deployment Runbook](../runbooks/deployment.md) — Deployment procedures
- [Database Runbook](../runbooks/database.md) — Database-specific operations
- [Disaster Recovery](../runbooks/disaster-recovery.md) — Backup and restore
