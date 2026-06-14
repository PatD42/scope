# Architecture - Security

**Parent**: [Architecture - Cross-cutting Concepts](cross-cutting.md)

**Technical Specifications**:
- Auth API: [13-specs/api/auth.yaml](../13-specs/api/)
- Error Codes: [13-specs/errors/by-domain/auth.yaml](../13-specs/errors/by-domain/)

---

## Authentication

<!-- How users and systems prove their identity. -->

### Method

**Primary Method**: [JWT / OAuth2 / Session-based / SAML / etc.]

**Rationale**: Why this method was chosen

### Implementation

**Flow**:
1. User submits credentials
2. System validates credentials
3. System issues authentication token/session
4. Client includes token in subsequent requests

**Token Format** (if using tokens):
- **Type**: [JWT / Opaque token]
- **Expiration**: [Duration]
- **Refresh Strategy**: [How tokens are refreshed]

**Session Management** (if using sessions):
- **Storage**: [Server-side / Database / Redis]
- **Expiration**: [Duration]
- **Renewal**: [How sessions are extended]

### Multi-Factor Authentication (MFA)

**Supported**: [Yes / No / Optional]

**Methods**: [SMS / TOTP / Email / Hardware tokens]

### Password Policy

**Requirements**:
- Minimum length: [X characters]
- Complexity: [Requirements]
- Expiration: [Yes/No, duration]
- History: [Prevent reuse of last N passwords]

**Storage**: Hashed with [Algorithm] (e.g., bcrypt, Argon2)

---

## Authorization

<!-- How system determines what authenticated users can do. -->

### Model

**Type**: [RBAC / ABAC / ACL / Custom]

**Rationale**: Why this model was chosen

### Roles

<!-- Role-Based Access Control roles -->

| Role | Description | Key Permissions |
|------|-------------|-----------------|
| Admin | Full system access | All |
| User | Standard user | Create, read, update own resources |
| Guest | Read-only access | Read public resources |

### Permissions

<!-- Granular permissions that can be assigned -->

| Permission | Resource | Actions | Granted To |
|-----------|----------|---------|------------|
| `users:read` | Users | View user list and details | Admin, User |
| `users:write` | Users | Create, update, delete users | Admin |
| `orders:read` | Orders | View orders | Admin, User (own) |

### Policy Rules

**Attribute-Based Rules** (if using ABAC):
- Rule 1: [Description]
- Rule 2: [Description]

**Hierarchical Rules**:
- Parent resource access implies child access
- Ownership rules (users can modify their own resources)

### Enforcement

**Enforcement Points**:
- API Gateway: Route-level authorization
- Service Layer: Business logic authorization
- Database: Row-level security (if applicable)

**Implementation**:
```
Request → Authentication → Authorization Check → Business Logic
```

---

## Data Protection

<!-- How sensitive data is protected at rest and in transit. -->

### Encryption at Rest

**Method**: [AES-256 / Database encryption / Filesystem encryption]

**Key Management**: [AWS KMS / Azure Key Vault / HashiCorp Vault / etc.]

**Encrypted Data Types**:
- Personally Identifiable Information (PII)
- Payment information
- Secrets and credentials
- [Other sensitive data]

### Encryption in Transit

**Protocol**: TLS 1.3 (minimum TLS 1.2)

**Certificate Management**:
- Provider: [Let's Encrypt / Enterprise CA]
- Renewal: [Automated / Manual]
- Monitoring: [Certificate expiration alerts]

**Internal Communication**:
- Service-to-service: [mTLS / TLS / VPN]
- Database connections: [TLS / Encrypted]

### Sensitive Data Handling

**Classification Levels**:
| Level | Definition | Examples | Handling |
|-------|------------|----------|----------|
| Public | Non-sensitive | Marketing content | No special handling |
| Internal | Internal use only | Business reports | Access control required |
| Confidential | Sensitive business data | Financial data, PII | Encryption + strict access |
| Restricted | Highest sensitivity | Credentials, secrets | Encryption + audit + MFA |

**Data Masking**:
- Logs: Mask PII and secrets
- UI: Mask sensitive fields (e.g., credit cards)
- Exports: Redact confidential data

**Data Retention**:
- [Retention policies by data type]
- Automated deletion after retention period
- Compliance requirements: [GDPR / CCPA / etc.]

---

## Security Headers

<!-- HTTP security headers applied across the system. -->

### Required Headers

**All Responses**:
```
Content-Security-Policy: [Policy]
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: no-referrer-when-downgrade
```

### Content Security Policy (CSP)

**Policy**:
```
default-src 'self';
script-src 'self' [trusted-cdn];
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
font-src 'self' [trusted-cdn];
```

**Rationale**: Prevent XSS and data injection attacks

### CORS Policy

**Allowed Origins**: [List of allowed origins]

**Allowed Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS

**Allowed Headers**: Content-Type, Authorization, [Others]

**Credentials**: [true / false]

---

## Security Best Practices

### Input Validation

- Validate all user input on server side
- Sanitize input to prevent injection attacks
- Use parameterized queries for database access
- Validate file uploads (type, size, content)

### Output Encoding

- Encode output based on context (HTML, JavaScript, URL)
- Use framework-provided encoding functions
- Prevent XSS through proper encoding

### Secret Management

**Never**:
- Commit secrets to version control
- Log secrets or sensitive data
- Hardcode secrets in code

**Always**:
- Use environment variables or secret management service
- Rotate secrets regularly
- Use least-privilege principle for secret access

### Security Monitoring

**Monitoring**:
- Failed authentication attempts
- Authorization failures
- Unusual access patterns
- Security header violations

**Alerting**:
- [Threshold] failed logins → Alert security team
- Repeated authorization failures → Investigate
- Certificate expiration approaching → Renew

---

## Compliance

**Applicable Regulations**: [GDPR / CCPA / HIPAA / SOC 2 / etc.]

**Key Requirements**:
- Data subject rights (access, deletion, portability)
- Audit logging
- Breach notification procedures
- Security assessments

**Audit Trail**:
- Log all access to sensitive data
- Retain logs for [Duration]
- Tamper-proof logging
