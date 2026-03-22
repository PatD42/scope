# Networking & Security Runbook

## Overview

Procedures for managing network configuration, firewalls, WAF rules, TLS certificates, and DNS. Covers both routine configuration and incident response for security events.

## Prerequisites

- Required access/permissions: {network admin role, DNS admin, WAF admin}
- Required tools: {cloud CLI, DNS management tool, certificate tools}
- Related docs: [Environments](../environments.md), [Architecture - Security](../../architecture/08-cross-cutting/security.md)

## Network Topology

| Component | Type | CIDR / Config | Purpose |
|-----------|------|--------------|---------|
| {VPC/VNet} | {network} | {CIDR block} | {main network} |
| {public subnet} | {subnet} | {CIDR block} | {load balancers, bastion} |
| {private subnet} | {subnet} | {CIDR block} | {application, database} |

## Procedures

### WAF Configuration

**Provider**: {Cloudflare / AWS WAF / Cloud Armor / Azure WAF}
**Console**: {URL}

#### View Current Rules

```bash
{command to list WAF rules}
```

#### Add a WAF Rule

**When**: New threat pattern, compliance requirement, or IP block needed
**Who**: {required role}
**Risk**: Medium (can block legitimate traffic)

##### Steps

```bash
# 1. Create the rule
{create rule command}

# 2. Set to monitoring/log-only mode first
{set mode command}

# 3. Monitor for false positives (wait X hours/days)
# 4. Switch to blocking mode
{enable blocking command}
```

##### Validation

- [ ] Rule appears in rule list
- [ ] Monitoring shows expected matches
- [ ] No false positives on legitimate traffic

##### Rollback

```bash
# Disable or delete the rule
{disable/delete rule command}
```

---

### TLS Certificate Management

**Provider**: {Let's Encrypt / ACM / Cloud-managed / Manual}
**Auto-Renew**: {Yes/No}

#### Renew / Replace Certificate

**When**: Certificate expiring, domain change, or compromise
**Who**: {required role}
**Risk**: High (downtime if misconfigured)

##### Steps

```bash
# 1. Generate or request new certificate
{cert generation/request command}

# 2. Install certificate
{install command}

# 3. Verify certificate
{verification command — openssl s_client, curl, etc.}

# 4. Restart / reload service to pick up new cert
{reload command}
```

##### Validation

```bash
# Check certificate expiry and chain
openssl s_client -connect {domain}:443 -servername {domain} </dev/null 2>/dev/null | openssl x509 -noout -dates -subject
```

---

### DNS Management

**Provider**: {Route53 / Cloud DNS / Cloudflare / etc.}
**Zone**: {domain name}

#### Add / Update DNS Record

**When**: New service, domain change, migration
**Who**: {required role}
**Risk**: Medium (propagation delay, can break routing)

##### Steps

```bash
# 1. Add or update record
{DNS update command}

# 2. Verify propagation
dig {domain} {record_type}
# or
nslookup {domain}
```

---

### Firewall Rules

#### View Current Rules

```bash
{command to list firewall/security group rules}
```

#### Add Firewall Rule

**When**: New service needs access, vendor IP allowlisting
**Who**: {required role}
**Risk**: Medium

##### Steps

```bash
# 1. Create rule
{create firewall rule command}

# 2. Verify rule is active
{list rules command}

# 3. Test connectivity
{test command — telnet, curl, nc}
```

##### Rollback

```bash
# Delete the rule
{delete rule command}
```

---

### Respond to Security Incident

**When**: Detected attack, breach, or suspicious activity
**Who**: {security team + on-call}
**Risk**: Critical

#### Steps

1. **Contain**: Block attacker IP(s) via WAF or firewall
2. **Assess**: Review logs for scope of impact
3. **Notify**: Alert security team and stakeholders per escalation matrix
4. **Mitigate**: Rotate compromised credentials, patch vulnerabilities
5. **Recover**: Restore from clean backup if needed
6. **Document**: Create incident report with timeline and root cause

---

## Security Checklist (Periodic Review)

- [ ] WAF rules up to date
- [ ] TLS certificates not expiring within 30 days
- [ ] Firewall rules reviewed — no unnecessary open ports
- [ ] DNS records accurate — no stale entries
- [ ] Security group rules follow least-privilege
- [ ] VPN/bastion access list current

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Certificate expired | Auto-renew failed, DNS validation issue | Manually renew, check DNS challenge config |
| WAF blocking legitimate traffic | Overly broad rule | Review WAF logs, adjust rule or add exception |
| Can't reach service | Firewall rule missing, security group too restrictive | Check inbound rules, verify port/protocol |
| DNS not resolving | Propagation delay, wrong record | Wait for TTL, verify record in DNS console |
