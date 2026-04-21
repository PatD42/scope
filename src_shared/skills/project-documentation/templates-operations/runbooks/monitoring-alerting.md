# Monitoring & Alerting Runbook

## Overview

Procedures for setting up, managing, and responding to monitoring and alerting. Covers dashboards, alert configuration, on-call response, and observability tooling.

## Prerequisites

- Required access/permissions: {monitoring platform admin, alert management}
- Required tools: {monitoring platform access, CLI tools}
- Related docs: [Architecture - Operations](../../architecture/08-cross-cutting/operations.md)

## Monitoring Stack

| Layer | Tool | URL | Purpose |
|-------|------|-----|---------|
| Metrics | {Prometheus/Datadog/CloudWatch/etc.} | {URL} | {system and app metrics} |
| Logs | {ELK/Loki/CloudWatch Logs/etc.} | {URL} | {log aggregation and search} |
| Traces | {Jaeger/Zipkin/Datadog APM/etc.} | {URL} | {distributed tracing} |
| Uptime | {Pingdom/UptimeRobot/etc.} | {URL} | {external health checks} |
| Alerting | {PagerDuty/OpsGenie/etc.} | {URL} | {alert routing and escalation} |

## Key Dashboards

| Dashboard | URL | Purpose | Key Metrics |
|-----------|-----|---------|-------------|
| {System Overview} | {URL} | {health at a glance} | {uptime, error rate, latency} |
| {Service X} | {URL} | {service detail} | {request rate, error rate, p99 latency} |
| {Infrastructure} | {URL} | {resource usage} | {CPU, memory, disk, network} |
| {Database} | {URL} | {DB performance} | {connections, query time, replication lag} |

## Alert Definitions

| Alert | Severity | Condition | Response Time | Runbook |
|-------|----------|-----------|--------------|---------|
| {High error rate} | {Critical} | {error_rate > 5% for 5m} | {15 min} | {link to procedure below} |
| {High latency} | {Warning} | {p99 > 2s for 10m} | {1 hour} | {link} |
| {Disk usage high} | {Warning} | {disk > 80%} | {4 hours} | {link} |
| {Service down} | {Critical} | {health check fails 3x} | {5 min} | {link} |
| {Certificate expiry} | {Warning} | {expires < 14 days} | {1 business day} | {link} |

## Procedures

### Respond to Alert

**When**: Alert fires
**Who**: On-call engineer
**Risk**: Varies by alert severity

#### General Response Flow

1. **Acknowledge** the alert in {alerting platform}
2. **Assess** — open the linked dashboard, check recent changes
3. **Diagnose** — follow alert-specific runbook section below
4. **Mitigate** — take action to restore service
5. **Communicate** — update status page / Slack channel
6. **Document** — note root cause and resolution in incident log

---

### High Error Rate

```bash
# 1. Check error logs for the pattern
{log query command for recent errors}

# 2. Check if a recent deployment caused it
{recent deployments query}

# 3. Check dependency health
{dependency health check commands}

# 4. If caused by bad deploy, rollback
{rollback command — see deployment runbook}
```

---

### High Latency

```bash
# 1. Check which endpoints are slow
{latency breakdown query}

# 2. Check database performance
{DB slow query check}

# 3. Check external service latency
{external dependency latency query}

# 4. Check resource utilization (CPU, memory)
{resource check command}
```

---

### Service Down

```bash
# 1. Check if service process is running
{service status command}

# 2. Check logs for crash reason
{recent log command}

# 3. Restart service
{restart command}

# 4. If restart doesn't help, check infrastructure
{infrastructure status command}
```

---

### Add a New Alert

**When**: New service, new SLO, or gap identified
**Who**: {required role}
**Risk**: Low

#### Steps

1. Define the alert condition (metric, threshold, duration)
2. Set severity and response time
3. Configure notification channel
4. Write runbook section for the alert
5. Test the alert (trigger condition in staging)

```bash
# Example: create alert (tool-specific)
{create alert command or config snippet}
```

---

### Add a New Dashboard

**When**: New service deployed, new metrics to track
**Who**: {required role}
**Risk**: Low

#### Steps

1. Identify key metrics for the service (RED method: Rate, Errors, Duration)
2. Create dashboard in monitoring platform
3. Add panels for each metric
4. Set appropriate time ranges and refresh intervals
5. Share dashboard link in team documentation

---

## On-Call Procedures

**Schedule**: {link to on-call schedule}
**Escalation**: {escalation policy — see troubleshooting/escalation.md}

| Severity | Response Time | Notification | Escalation After |
|----------|--------------|-------------|-----------------|
| Critical | {5-15 min} | {page + Slack} | {30 min} |
| Warning | {1-4 hours} | {Slack} | {next business day} |
| Info | {next business day} | {email/ticket} | {N/A} |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Alert not firing | Threshold too high, metric not collected | Verify metric exists, lower threshold |
| Too many false positives | Threshold too sensitive, noisy metric | Widen threshold, add dampening/hysteresis |
| Monitoring agent down | Agent crashed, config issue | Restart agent, check config |
| Dashboard shows no data | Data source misconfigured, retention expired | Check data source, verify metric name |
