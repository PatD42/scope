# Secrets Management Runbook

## Overview

Procedures for managing secrets, API keys, encryption keys, and credentials across all environments. Covers provisioning, rotation, access control, and incident response for compromised secrets.

## Prerequisites

- Required access/permissions: {Secrets Manager admin role, KMS access}
- Required tools: {gcloud/aws/az CLI, vault CLI, etc.}
- Related docs: [Architecture - Security](../../architecture/08-cross-cutting/security.md)

## Secrets Inventory

| Secret | Type | Storage | Rotation | Environments | Owner |
|--------|------|---------|----------|-------------|-------|
| {DB password} | {credential} | {Secrets Manager} | {90 days} | {all} | {team} |
| {API key - provider X} | {API key} | {Secrets Manager} | {yearly} | {all} | {team} |
| {TLS certificate} | {certificate} | {Certificate Manager} | {auto-renew} | {prod, staging} | {team} |
| {Signing key} | {encryption key} | {KMS} | {yearly} | {all} | {team} |

## Secrets Storage

**Primary store**: {Google Secret Manager / AWS Secrets Manager / Azure Key Vault / HashiCorp Vault}
**Access pattern**: {how application reads secrets — env injection, SDK, sidecar}
**Encryption**: {KMS key used, encryption at rest details}

## Procedures

### Create a New Secret

**When**: New service or integration requires credentials
**Who**: {required role}
**Risk**: Low

#### Steps

```bash
# 1. Create the secret
{create secret command}

# 2. Set the secret value
{set value command}

# 3. Grant access to the service account / role
{grant access command}

# 4. Reference in application config
{how to reference — env var name, mount path, etc.}
```

#### Validation

```bash
# Verify secret is accessible by the application
{verification command}
```

---

### Rotate a Secret

**When**: Scheduled rotation or after suspected compromise
**Who**: {required role}
**Risk**: Medium
**Estimated Duration**: {X minutes}

#### Steps

```bash
# 1. Generate new credential at the source (e.g., new DB password, new API key)
{regenerate command}

# 2. Add new version to secrets store
{update secret command}

# 3. Deploy application to pick up new secret (or trigger reload)
{reload/deploy command}

# 4. Verify application works with new secret
{health check command}

# 5. Revoke / disable old credential at the source
{revoke old credential command}
```

#### Validation

- [ ] Application healthy after rotation
- [ ] Old credential no longer works
- [ ] No errors in logs related to authentication

#### Rollback

```bash
# Revert to previous secret version
{rollback secret version command}

# Redeploy or trigger reload
{reload command}
```

---

### Respond to Compromised Secret

**When**: Secret exposed in logs, repo, or reported breach
**Who**: {required role}
**Risk**: Critical

#### Steps

1. **Immediately** revoke the compromised credential at the source
2. Generate a new credential
3. Update the secrets store with the new value
4. Deploy or reload the application
5. Audit access logs for unauthorized use of the compromised secret
6. Document the incident and root cause

---

### Manage Service Account Keys

**When**: Service-to-service authentication setup or rotation
**Who**: {required role}
**Risk**: Medium

#### Steps

```bash
# 1. Create / rotate service account key
{create key command}

# 2. Store in secrets manager
{store command}

# 3. Update application reference
{update reference}
```

---

## Rotation Schedule

| Secret | Rotation Period | Last Rotated | Next Rotation | Auto-Rotate |
|--------|---------------|-------------|--------------|-------------|
| {secret} | {90 days} | {date} | {date} | {Yes/No} |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Application can't read secret | IAM permissions, wrong secret name | Check IAM bindings, verify secret path |
| Secret rotation broke app | App cached old secret, no reload mechanism | Restart/redeploy app, implement hot-reload |
| Secret not found in env | Injection not configured, deploy config mismatch | Check deployment config, verify env var mapping |
