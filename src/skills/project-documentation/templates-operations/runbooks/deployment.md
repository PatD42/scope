# Deployment Runbook

## Overview

Procedures for building, deploying, and rolling back application releases across all environments.

## Prerequisites

- Required access/permissions: {list IAM roles, CLI tools, VPN}
- Required tools: {Docker, gcloud/aws/az CLI, kubectl, terraform, etc.}
- Related docs: [Environments](../environments.md), [Architecture - Deployment](../../architecture/07-deployment.md)

## Component Inventory

| Component | Build Tool | Registry | Runtime | Deploy Method |
|-----------|-----------|----------|---------|---------------|
| {service} | {Docker/npm/pip} | {registry URL} | {Cloud Run/K8s/etc.} | {CLI/CI-CD/Terraform} |

## Procedures

### Build & Push Image

**When**: Every release
**Who**: Developer or CI/CD pipeline
**Risk**: Low

#### Steps

```bash
# 1. Build the container image
{build command}

# 2. Tag the image
{tag command}

# 3. Push to registry
{push command}
```

#### Validation

```bash
# Verify image in registry
{verify command}
```

---

### Deploy to Staging

**When**: After successful build
**Who**: Developer or CI/CD pipeline
**Risk**: Low

#### Steps

```bash
# 1. Deploy to staging
{deploy command for staging}

# 2. Run smoke tests
{smoke test command}
```

#### Validation

- [ ] Application is accessible at staging URL
- [ ] Health check endpoint returns 200
- [ ] Smoke tests pass
- [ ] Logs show clean startup

---

### Deploy to Production

**When**: After staging validation, during maintenance window if applicable
**Who**: {required role}
**Risk**: Medium
**Estimated Duration**: {X minutes}

#### Pre-Deployment Checklist

- [ ] Staging deployment validated
- [ ] Database migrations applied (if any)
- [ ] Feature flags configured
- [ ] Monitoring dashboards open
- [ ] Rollback plan reviewed
- [ ] Team notified in {channel}

#### Steps

```bash
# 1. Deploy to production
{deploy command for production}

# 2. Monitor deployment progress
{monitoring command}

# 3. Verify health
{health check command}
```

#### Validation

- [ ] Health check returns 200
- [ ] Error rate unchanged in monitoring
- [ ] Key user flows working (manual or automated check)
- [ ] No increase in error logs

#### Rollback

```bash
# Rollback to previous version
{rollback command}

# Verify rollback
{health check command}
```

---

### Database Migration

**When**: Schema changes required before/during deployment
**Who**: {required role}
**Risk**: High

#### Steps

```bash
# 1. Backup current database
{backup command}

# 2. Run migration
{migration command}

# 3. Verify migration
{verification command}
```

#### Rollback

```bash
# Revert migration
{rollback migration command}
```

---

### Hotfix Deployment

**When**: Critical production issue requires immediate fix
**Who**: {required role}
**Risk**: Medium-High

#### Steps

1. Create hotfix branch from production tag
2. Apply fix, run tests
3. Build and push image
4. Deploy directly to production (skip staging if emergency)
5. Backmerge to main branch

---

## CI/CD Pipeline

**Platform**: {GitHub Actions / GitLab CI / Jenkins / etc.}
**Config location**: {path to pipeline config}

| Stage | Trigger | Actions | Duration |
|-------|---------|---------|----------|
| Build | {push to main} | {build, test, lint} | {X min} |
| Deploy Staging | {build success} | {deploy to staging} | {X min} |
| Deploy Prod | {manual approval} | {deploy to production} | {X min} |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Deployment times out | {resource limits, health check} | {increase timeout, fix health check} |
| Container fails to start | {missing env vars, bad config} | {check logs, verify config} |
| Health check fails after deploy | {dependency down, port mismatch} | {check dependencies, verify port config} |
