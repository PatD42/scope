# Architecture - Operations

**Parent**: [Architecture - Cross-cutting Concepts](cross-cutting.md)

---

## Error Handling

<!-- Standard approach to error handling across the system. -->

### Error Classification

| Error Type | HTTP Status | User Message | Logging Level | Retry |
|-----------|-------------|--------------|---------------|-------|
| Validation Error | 400 | Specific validation issue | WARN | No |
| Authentication Error | 401 | "Authentication required" | WARN | No |
| Authorization Error | 403 | "Insufficient permissions" | WARN | No |
| Not Found | 404 | "Resource not found" | INFO | No |
| Conflict | 409 | "Resource already exists" | WARN | No |
| Rate Limited | 429 | "Too many requests" | INFO | Yes (backoff) |
| Server Error | 500 | "An error occurred" | ERROR | Yes (limited) |
| Service Unavailable | 503 | "Service temporarily unavailable" | ERROR | Yes (backoff) |

### Error Response Format

**Standard Format**:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly message",
    "details": {
      "field": "Specific field error",
      "constraint": "Which constraint was violated"
    },
    "request_id": "unique-request-id",
    "timestamp": "ISO-8601"
  }
}
```

**Example - Validation Error**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": "Email format is invalid",
      "age": "Must be at least 18"
    },
    "request_id": "req-12345",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Handling Strategy

**Client Errors (4xx)**:
- Log at WARN or INFO level
- Return specific error details to client
- Do not retry automatically
- Track for analytics (repeated validation errors may indicate UX issues)

**Server Errors (5xx)**:
- Log at ERROR level with full stack trace
- Return generic message to client (don't expose internals)
- Consider retry with exponential backoff
- Alert on-call engineer if sustained

**Third-Party Service Errors**:
- Implement circuit breaker pattern
- Fallback to cached data or degraded functionality
- Log external service failures
- Monitor third-party service health

### Error Logging

**Required Information**:
- Error message and type
- Stack trace
- Request ID (for correlation)
- User ID (if authenticated)
- Request path and method
- Request parameters (sanitized)
- Timestamp

**Sensitive Data**:
- Never log passwords, tokens, or secrets
- Mask PII in logs (emails, phone numbers, etc.)
- Redact sensitive request/response bodies

---

## Logging

<!-- Logging strategy across the system. -->

### Logging Framework

**Framework**: [Winston / Pino / Log4j / Serilog / etc.]

**Rationale**: Why this framework was chosen

### Log Levels

**Standard Levels** (in order of severity):

| Level | Usage | Examples |
|-------|-------|----------|
| **ERROR** | Errors that require immediate attention | Application crashes, unhandled exceptions, critical service failures |
| **WARN** | Warnings about potential issues | Deprecated API usage, retry attempts, degraded performance |
| **INFO** | Important business events | User login, order placed, configuration loaded |
| **DEBUG** | Detailed diagnostic information | Function entry/exit, variable values, query parameters |
| **TRACE** | Very detailed diagnostic information | Loop iterations, detailed flow tracking |

**Environment Defaults**:
- Production: INFO
- Staging: DEBUG
- Development: DEBUG or TRACE

### Structured Logging

**Format**: JSON

**Standard Fields**:
```json
{
  "timestamp": "ISO-8601",
  "level": "INFO",
  "service": "service-name",
  "request_id": "correlation-id",
  "user_id": "user-identifier",
  "message": "Log message",
  "context": {
    "key": "value"
  }
}
```

**Benefits**:
- Machine-readable for aggregation
- Easy to query and filter
- Consistent structure across services

### Log Aggregation

**Platform**: [ELK Stack / Splunk / Datadog / CloudWatch / etc.]

**Retention**:
- Recent logs (last 7 days): Full detail, high availability
- Historical logs (8-90 days): Compressed, searchable
- Archive (90+ days): Cold storage, compliance retention

**Access**:
- Developers: Development and staging logs
- Operations: All environments
- Security team: Security and audit logs

### What to Log

**DO Log**:
- Application startup/shutdown
- User authentication events
- Important business events
- API requests/responses (sanitized)
- External service calls
- Configuration changes
- Performance metrics
- Security events

**DON'T Log**:
- Passwords, tokens, API keys
- Credit card numbers, SSNs
- Full PII without masking
- Sensitive business data in plaintext

### Correlation

**Request ID**:
- Generate unique ID for each request
- Include in all logs for that request
- Return in response headers: `X-Request-ID`
- Use for distributed tracing across services

---

## Caching

<!-- Caching strategy across the system. -->

### Cache Layers

| Cache Layer | Technology | Location | TTL | Use Case |
|------------|-----------|----------|-----|----------|
| Browser | HTTP Cache | Client | Varies | Static assets, public data |
| CDN | [CloudFront / Cloudflare] | Edge | [Duration] | Static files, media |
| Application | [Redis / Memcached] | Server-side | [Duration] | Session data, API responses |
| Database | Query cache | Database | [Duration] | Frequent queries |

### Caching Strategy

**Cache-Aside (Lazy Loading)**:
```
1. Check cache
2. If cache miss:
   a. Fetch from database
   b. Store in cache
   c. Return data
3. If cache hit:
   a. Return cached data
```

**Write-Through**:
```
1. Write to cache
2. Write to database
3. Return success
```

**Write-Behind**:
```
1. Write to cache
2. Async write to database
3. Return success (eventually consistent)
```

### Cache Invalidation

**Strategies**:
- **TTL-based**: Cache expires after fixed duration
- **Event-based**: Invalidate on data modification
- **Manual**: Explicit cache clear on deployment

**Invalidation Patterns**:
- Single item: Delete specific cache key
- Related items: Delete keys matching pattern
- Full flush: Clear entire cache (use sparingly)

### Cache Keys

**Naming Convention**: `{namespace}:{resource}:{id}:{version}`

**Examples**:
- `api:user:123:v1`
- `api:order:456:v1`
- `session:abc123`

### Monitoring

**Metrics**:
- Cache hit rate (target: >80%)
- Cache miss rate
- Cache eviction rate
- Average cache retrieval time

**Alerts**:
- Hit rate drops below threshold
- Cache unavailable
- Memory usage high

---

## Configuration Management

<!-- How configuration is handled across environments. -->

### Configuration Sources

**Precedence Order** (highest to lowest):
1. Environment variables (runtime)
2. Configuration file (environment-specific)
3. Configuration file (default)
4. Application defaults (hardcoded)

### Configuration Structure

**File Format**: [YAML / JSON / TOML / etc.]

**Organization**:
```yaml
# config/production.yaml
app:
  name: my-service
  version: 1.2.3
  port: 8080

database:
  host: ${DB_HOST}
  port: ${DB_PORT}
  name: ${DB_NAME}

cache:
  enabled: true
  ttl: 3600

features:
  new_ui: true
  beta_feature: false
```

### Environment-Specific Configuration

**Environments**:
- **Development**: Local development settings
- **Staging**: Production-like for testing
- **Production**: Live environment settings

**Differences**:
- Database connections
- External service endpoints
- Feature flags
- Log levels
- Cache TTLs

### Secrets Management

**Never in Configuration Files**:
- Database passwords
- API keys
- Encryption keys
- OAuth secrets

**Secrets Storage**: [AWS Secrets Manager / Azure Key Vault / HashiCorp Vault / etc.]

**Access Pattern**:
1. Application requests secret at startup
2. Secret manager validates identity
3. Secret returned and cached (if appropriate)
4. Application uses secret

**Rotation**:
- Secrets rotated on [Schedule]
- Application handles rotation gracefully (reload on signal)

### Feature Flags

**Purpose**: Enable/disable features without deployment

**Implementation**: [LaunchDarkly / Custom / Configuration-based]

**Use Cases**:
- Gradual rollout (canary releases)
- A/B testing
- Emergency kill switch
- Environment-specific features

```yaml
features:
  new_checkout: true
  payment_v2: false
  experimental_dashboard: false
```

### Configuration Validation

**On Startup**:
- Validate all required configuration present
- Validate data types and formats
- Validate constraint ranges
- Fail fast if invalid (don't start with bad config)

**Validation Rules**:
```yaml
database:
  host: required, string
  port: required, integer, range: 1-65535
  connection_pool_size: optional, integer, min: 1, max: 100
```

### Configuration Changes

**Hot Reload**: [Yes / No / Partial]

**Reload Mechanism**:
- Signal-based (SIGHUP)
- File watcher
- Admin API endpoint
- Requires restart

**Testing**:
- Configuration changes tested in staging first
- Validated before deployment
- Rollback plan for bad configuration
