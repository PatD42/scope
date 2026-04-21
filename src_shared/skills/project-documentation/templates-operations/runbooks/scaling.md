# Scaling Runbook

## Overview

Procedures for scaling application and infrastructure components horizontally and vertically. Covers both reactive scaling (responding to load) and proactive scaling (planned events).

## Prerequisites

- Required access/permissions: {cloud admin, container orchestration admin}
- Required tools: {cloud CLI, kubectl, terraform}
- Related docs: [Architecture - Deployment](../../architecture/07-deployment.md), [Environments](../environments.md)

## Current Scaling Configuration

| Component | Current Scale | Min | Max | Auto-Scale | Scaling Metric |
|-----------|-------------|-----|-----|-----------|---------------|
| {app service} | {2 instances} | {1} | {10} | {Yes/No} | {CPU 70%} |
| {worker} | {1 instance} | {1} | {5} | {Yes/No} | {queue depth} |
| {database} | {1 instance} | {N/A} | {N/A} | {No} | {manual} |
| {cache} | {1 node} | {N/A} | {N/A} | {No} | {manual} |

## Procedures

### Scale Application Horizontally (Add Instances)

**When**: High traffic, increased load, planned event
**Who**: {required role}
**Risk**: Low

#### Steps

```bash
# 1. Check current instance count
{check instances command}

# 2. Scale up
{scale up command}

# 3. Verify new instances are healthy
{health check command}

# 4. Monitor load distribution
{monitoring command}
```

#### Scale Down (After Load Subsides)

```bash
# Scale back to normal
{scale down command}
```

---

### Scale Application Vertically (More Resources)

**When**: Single-instance performance bottleneck
**Who**: {required role}
**Risk**: Medium (may cause brief restart)

#### Steps

```bash
# 1. Check current resource allocation
{resource check command}

# 2. Update resource limits
{update resources command}

# 3. Monitor after change
{monitoring command}
```

---

### Configure Auto-Scaling

**When**: Setting up or adjusting auto-scaling policies
**Who**: {required role}
**Risk**: Medium

#### Steps

```bash
# 1. Define scaling policy
{create/update autoscaling policy command}

# 2. Set min/max bounds
{set bounds command}

# 3. Configure scaling metric and threshold
{configure metric command}

# 4. Test by generating load (staging only)
{load test command}
```

---

### Scale Database

**When**: Storage limits, performance degradation, connection limits
**Who**: {required role}
**Risk**: Medium-High (may cause brief downtime)

See [Database Runbook](database.md) — Scale Database section.

---

### Prepare for Planned Event

**When**: Expected traffic spike (launch, sale, marketing campaign)
**Who**: {required role}
**Risk**: Low (if done in advance)

#### Pre-Event Checklist

- [ ] Scale up application instances
- [ ] Increase database connection pool
- [ ] Warm up caches
- [ ] Increase auto-scaling max limits
- [ ] Verify CDN capacity
- [ ] Set up additional monitoring/alerting
- [ ] Notify team and on-call

#### Post-Event

- [ ] Scale back to normal levels
- [ ] Reset auto-scaling limits
- [ ] Review performance data
- [ ] Document lessons learned

---

## Scaling Limits & Constraints

| Component | Hard Limit | Bottleneck | Mitigation |
|-----------|-----------|-----------|------------|
| {app instances} | {provider limit} | {load balancer connections} | {request quota increase} |
| {database connections} | {max_connections setting} | {connection pool size} | {connection pooler (PgBouncer)} |
| {API rate limits} | {provider limit} | {external API calls} | {caching, request batching} |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| New instances not receiving traffic | Health check failing, LB not updated | Check health endpoint, verify LB target group |
| Auto-scaling not triggering | Wrong metric, threshold too high | Verify metric collection, adjust threshold |
| Scaling hits quota limit | Cloud provider quota | Request quota increase |
| Scale-up causes errors | Cold start issues, cache miss storm | Pre-warm caches, implement gradual traffic shift |
