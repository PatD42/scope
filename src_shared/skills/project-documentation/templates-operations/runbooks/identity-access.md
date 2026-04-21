# Identity & Access Management Runbook

## Overview

Procedures for managing user accounts, roles, permissions, and authentication across the system. Covers identity provider administration, user lifecycle, and access auditing.

## Prerequisites

- Required access/permissions: {IdP admin role, cloud IAM admin}
- Required tools: {admin console access, CLI tools}
- Related docs: [Architecture - Security](../../architecture/08-cross-cutting/security.md)

## Identity Provider

**Provider**: {Keycloak / Auth0 / Okta / AWS Cognito / Google Identity / Azure AD}
**Admin Console**: {URL}
**Realm / Tenant**: {name}

## Role Matrix

| Role | Description | Permissions | Assigned To |
|------|-----------|-------------|-------------|
| {admin} | {full system access} | {all} | {named individuals} |
| {operator} | {operational access} | {deploy, monitor, restart} | {ops team} |
| {user} | {standard user} | {use application} | {all users} |
| {read-only} | {view only} | {view dashboards, logs} | {stakeholders} |

## Procedures

### Provision a New User

**When**: New team member or customer onboarding
**Who**: {required role}
**Risk**: Low

#### Steps

```bash
# 1. Create user account in identity provider
{create user command or admin console steps}

# 2. Assign roles
{assign role command}

# 3. Set up MFA (if required)
{MFA setup steps}

# 4. Send welcome / credentials notification
{notification method}
```

#### Validation

- [ ] User can log in
- [ ] Correct roles assigned
- [ ] MFA configured (if required)

---

### Approve a User / Access Request

**When**: User requests elevated access or new account requires approval
**Who**: {approver role}
**Risk**: Low

#### Steps

1. Review access request in {system — ticketing, admin console, email}
2. Verify requester identity and business justification
3. Approve or reject in {system}
4. If approved, assign requested role(s)
5. Notify requester

---

### Deprovision a User

**When**: Employee departure, role change, account cleanup
**Who**: {required role}
**Risk**: Medium

#### Steps

```bash
# 1. Disable user account (don't delete immediately)
{disable command}

# 2. Revoke active sessions
{revoke sessions command}

# 3. Remove from groups/roles
{remove roles command}

# 4. Revoke any personal API keys or service credentials
{revoke keys command}

# 5. After retention period, delete account
{delete command — after X days}
```

---

### Reset User Password / Unlock Account

**When**: User locked out or forgot password
**Who**: {required role or self-service}
**Risk**: Low

#### Steps

```bash
# Option A: Self-service reset
{self-service flow description}

# Option B: Admin reset
{admin reset command}
```

---

### Configure SSO / Federation

**When**: Integrating new identity source or application
**Who**: {required role}
**Risk**: Medium

#### Steps

1. Configure identity provider (SAML / OIDC settings)
2. Register application as a client
3. Map attributes / claims
4. Test login flow
5. Enable for users

---

### Audit Access

**When**: Periodic review (quarterly), security incident, compliance requirement
**Who**: {required role}
**Risk**: Low

#### Steps

```bash
# 1. Export current user list and roles
{export command}

# 2. Review against approved access list
# 3. Identify stale accounts (no login in X days)
{query for inactive users}

# 4. Remove unauthorized or stale access
# 5. Document audit results
```

---

## Cloud IAM

### Cloud Console / CLI Access

| Principal | Type | Role | Scope | Purpose |
|-----------|------|------|-------|---------|
| {user/sa} | {User/Service Account} | {role} | {project/resource} | {why} |

### Service Accounts

| Service Account | Purpose | Key Type | Bound To |
|----------------|---------|----------|----------|
| {sa-name} | {what it does} | {key/workload identity} | {service} |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| User can't log in | Account disabled, wrong password, MFA issue | Check account status, reset password, verify MFA |
| Missing permissions | Role not assigned, wrong realm/tenant | Check role assignments, verify correct IdP realm |
| SSO loop / redirect error | Misconfigured callback URL, expired cert | Check OIDC/SAML config, renew certificates |
| Stale sessions after deprovision | Sessions not revoked | Force session revocation in IdP |
