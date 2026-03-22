# Escalation Matrix

## Overview

Escalation procedures, contact list, and severity definitions for operational incidents.

## Severity Levels

| Severity | Definition | Examples | Response Time | Resolution Target |
|----------|-----------|----------|--------------|-------------------|
| **SEV-1** Critical | System down, data loss, security breach | Full outage, data corruption, active breach | {15 min} | {1 hour} |
| **SEV-2** High | Major feature broken, significant degradation | Key workflow broken, high error rate, performance severely degraded | {30 min} | {4 hours} |
| **SEV-3** Medium | Minor feature broken, workaround available | Non-critical feature down, intermittent errors | {4 hours} | {1 business day} |
| **SEV-4** Low | Cosmetic, minor inconvenience | UI glitch, non-blocking warning | {1 business day} | {1 week} |

## Escalation Path

```
Level 0: On-call engineer (first responder)
    ↓ (if unresolved after 30 min for SEV-1, 1 hour for SEV-2)
Level 1: Team lead / senior engineer
    ↓ (if unresolved after 1 hour for SEV-1, 4 hours for SEV-2)
Level 2: Engineering manager + architect
    ↓ (if unresolved after 2 hours for SEV-1)
Level 3: VP Engineering / CTO + vendor support
```

## Contact List

| Role | Name | Slack | Phone | Email | Hours |
|------|------|-------|-------|-------|-------|
| On-call (primary) | {see rotation} | {handle} | {number} | {email} | {24/7} |
| On-call (secondary) | {see rotation} | {handle} | {number} | {email} | {24/7} |
| Team lead | {name} | {handle} | {number} | {email} | {business hours} |
| Engineering manager | {name} | {handle} | {number} | {email} | {business hours} |
| Database admin | {name} | {handle} | {number} | {email} | {business hours} |
| Security lead | {name} | {handle} | {number} | {email} | {business hours} |

## Vendor Support Contacts

| Vendor | Service | Support Channel | SLA | Account/Contract |
|--------|---------|----------------|-----|-----------------|
| {cloud provider} | {infrastructure} | {support portal URL} | {response time} | {account ID} |
| {IdP provider} | {authentication} | {support email/portal} | {response time} | {tenant ID} |
| {monitoring vendor} | {monitoring} | {support channel} | {response time} | {account ID} |

## Incident Communication

### Internal

| Audience | Channel | When | Who Notifies |
|----------|---------|------|-------------|
| Engineering team | {#incidents Slack channel} | Immediately | On-call |
| Management | {#leadership Slack / email} | SEV-1/SEV-2 within 15 min | Team lead |
| All-hands | {#general / email} | Extended outage (>1 hour) | Engineering manager |

### External

| Audience | Channel | When | Who Notifies |
|----------|---------|------|-------------|
| Customers | {status page} | SEV-1/SEV-2 within 30 min | On-call / comms |
| Partners | {email / Slack connect} | SEV-1 impacting partners | Team lead |

### Status Update Frequency

| Severity | Update Frequency | Channel |
|----------|-----------------|---------|
| SEV-1 | Every 15-30 min | Slack + status page |
| SEV-2 | Every 1 hour | Slack |
| SEV-3 | On resolution | Ticket |

## Post-Incident

1. **Incident report**: Document timeline, root cause, resolution within 48 hours
2. **Postmortem meeting**: Schedule for SEV-1 and SEV-2 within 1 week
3. **Action items**: Track in {ticket system} with owners and due dates
4. **Process improvement**: Update runbooks with lessons learned

## Related Documentation

- [Monitoring & Alerting](../runbooks/monitoring-alerting.md) — Alert definitions and response
- [Disaster Recovery](../runbooks/disaster-recovery.md) — DR procedures
