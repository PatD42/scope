---
name: backend-rest-api
description: RESTful API design patterns and best practices. Use when story requires building or modifying REST APIs, HTTP endpoints, API versioning, request/response patterns, status codes, authentication, pagination, filtering, sorting, rate limiting, CORS, caching, idempotency, or OpenAPI documentation.
---

# Backend REST API

RESTful API design patterns, best practices, and common implementation patterns for building robust HTTP APIs.

## REST Principles

**REST (Representational State Transfer)** is an architectural style for distributed systems.

### Core Constraints

1. **Client-Server** - Separation of concerns (UI vs data storage)
2. **Stateless** - Each request contains all necessary information
3. **Cacheable** - Responses explicitly state if they can be cached
4. **Uniform Interface** - Consistent resource identifiers and HTTP methods
5. **Layered System** - Client doesn't know if connected directly to server or intermediary

### Resource-Oriented Design

```
Good (Resource-oriented):
GET    /users           - List users
GET    /users/123       - Get specific user
POST   /users           - Create user
PUT    /users/123       - Replace user
PATCH  /users/123       - Update user
DELETE /users/123       - Delete user

Bad (RPC-style):
POST   /getUser
POST   /createUser
POST   /updateUser
POST   /deleteUser
```

## HTTP Methods

| Method | Purpose | Idempotent | Safe | Request Body | Response Body |
|--------|---------|------------|------|--------------|---------------|
| GET | Retrieve resource | ✅ | ✅ | ❌ | ✅ |
| POST | Create resource | ❌ | ❌ | ✅ | ✅ |
| PUT | Replace resource | ✅ | ❌ | ✅ | ✅ |
| PATCH | Update resource | ❌ | ❌ | ✅ | ✅ |
| DELETE | Remove resource | ✅ | ❌ | ❌ | ✅ |
| HEAD | Get headers only | ✅ | ✅ | ❌ | ❌ |
| OPTIONS | Get allowed methods | ✅ | ✅ | ❌ | ✅ |

**Idempotent**: Same request multiple times = same result
**Safe**: Read-only, doesn't modify server state

### Method Selection

```python
# List collection
GET /products?category=electronics&limit=20

# Get single resource
GET /products/123

# Create new resource (server generates ID)
POST /products
Body: {"name": "Laptop", "price": 999}
Response: 201 Created, Location: /products/456

# Replace entire resource (client knows ID)
PUT /products/456
Body: {"name": "Laptop", "price": 899, "stock": 10}

# Partial update
PATCH /products/456
Body: {"price": 849}

# Delete resource
DELETE /products/456
Response: 204 No Content
```

## HTTP Status Codes

### Success (2xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 OK | Request succeeded | GET, PATCH returns data |
| 201 Created | Resource created | POST with Location header |
| 202 Accepted | Async processing | Long-running operation queued |
| 204 No Content | Success, no body | DELETE, PUT without response |

### Client Errors (4xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| 400 Bad Request | Invalid syntax/data | Validation errors |
| 401 Unauthorized | Missing/invalid auth | No credentials or expired token |
| 403 Forbidden | Insufficient permissions | Valid auth but not allowed |
| 404 Not Found | Resource doesn't exist | Wrong ID or deleted resource |
| 405 Method Not Allowed | HTTP method unsupported | POST on read-only endpoint |
| 409 Conflict | Resource state conflict | Duplicate email, version mismatch |
| 422 Unprocessable Entity | Semantic errors | Valid JSON but business logic fails |
| 429 Too Many Requests | Rate limit exceeded | Client hitting rate limit |

### Server Errors (5xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| 500 Internal Server Error | Unexpected error | Unhandled exception |
| 502 Bad Gateway | Upstream error | Dependency service failed |
| 503 Service Unavailable | Temporarily down | Maintenance, overload |
| 504 Gateway Timeout | Upstream timeout | Slow dependency |

### Status Code Selection

```python
# Success cases
GET /users/123           → 200 OK + user data
POST /users              → 201 Created + Location: /users/456
DELETE /users/123        → 204 No Content
PATCH /users/123         → 200 OK + updated user

# Client errors
GET /users/999           → 404 Not Found
POST /users (no email)   → 400 Bad Request
POST /users (duplicate)  → 409 Conflict
GET /users (no auth)     → 401 Unauthorized
DELETE /admin (not admin)→ 403 Forbidden

# Server errors
GET /users (DB down)     → 503 Service Unavailable
GET /users (timeout)     → 504 Gateway Timeout
```

## Request/Response Patterns

### Request Structure

```http
POST /api/v1/users HTTP/1.1
Host: example.com
Content-Type: application/json
Authorization: Bearer eyJhbGc...
Accept: application/json

{
  "email": "user@example.com",
  "name": "John Doe"
}
```

### Response Structure

```json
{
  "data": {
    "id": "123",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-01-15T10:30:00Z"
  },
  "meta": {
    "request_id": "abc-123",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### Error Response Format

```json
{
  "error": {
    "code": "validation_failed",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters"
      }
    ]
  },
  "meta": {
    "request_id": "abc-123",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

## Pagination

### Offset-Based (Traditional)

```http
GET /products?limit=20&offset=40
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "offset": 40,
    "total": 150,
    "has_more": true
  }
}
```

**Pros**: Can jump to any page, shows total count
**Cons**: Slow on large datasets, inconsistent if data changes during pagination

### Cursor-Based (Modern)

```http
GET /products?limit=20&cursor=eyJpZCI6MTIzfQ
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTQzfQ",
    "has_more": true
  }
}
```

**Pros**: Fast, consistent results, handles real-time data
**Cons**: Can't jump to arbitrary page, no total count

## Filtering and Sorting

```http
# Filtering
GET /products?category=electronics&price_min=100&price_max=500&in_stock=true

# Sorting
GET /products?sort=price:asc
GET /products?sort=-created_at        # Minus = descending

# Field selection (sparse fieldsets)
GET /products?fields=id,name,price

# Multiple filters
GET /products?tags=laptop,gaming&brand=dell
```

## Versioning

### URL Versioning (Recommended)

```http
GET /api/v1/users
GET /api/v2/users
```

**Pros**: Clear, explicit, easy to route
**Cons**: URL changes with version

### Header Versioning

```http
GET /api/users
Accept: application/vnd.company.v2+json
```

**Pros**: Clean URLs
**Cons**: Less visible, requires header inspection

### Version Strategy

- **v1, v2, v3** - Major versions only
- **Deprecation**: Announce 6-12 months ahead, provide migration guide
- **Breaking changes**: New version required
- **Non-breaking**: Same version (add fields, new optional params)

## Authentication Patterns

### Bearer Token (JWT)

```http
GET /api/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Use for**: Stateless auth, microservices, mobile apps

### API Key

```http
GET /api/users
X-API-Key: ak_live_1234567890abcdef
```

**Use for**: Server-to-server, rate limiting per client

### OAuth 2.0

```http
GET /api/users
Authorization: Bearer {access_token}
```

**Use for**: Third-party access, delegated authorization

### Basic Auth

```http
GET /api/users
Authorization: Basic dXNlcjpwYXNzd29yZA==
```

**Use for**: Simple internal APIs, development (HTTPS only!)

## Rate Limiting

### Response Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 456
X-RateLimit-Reset: 1640000000
Retry-After: 60
```

### Rate Limit Exceeded

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit of 1000 requests per hour exceeded",
    "retry_after": 60
  }
}
```

### Strategies

- **Fixed window**: 1000 req/hour (simple, burst-prone)
- **Sliding window**: More accurate, smoother
- **Token bucket**: Allows bursts, refills over time

## CORS (Cross-Origin Resource Sharing)

```http
# Preflight request
OPTIONS /api/users
Origin: https://app.example.com
Access-Control-Request-Method: POST

# Preflight response
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400

# Actual request
POST /api/users
Origin: https://app.example.com

# Response
HTTP/1.1 201 Created
Access-Control-Allow-Origin: https://app.example.com
```

## Idempotency

### Idempotency Keys (POST requests)

```http
POST /api/orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{
  "product_id": "123",
  "quantity": 2
}
```

Server behavior:
- First request with key → Process and store result
- Duplicate request with same key → Return stored result (no side effects)
- Different request with same key → 409 Conflict

**Use for**: Payment processing, order creation, critical operations

## Content Negotiation

```http
# Client requests JSON
GET /api/users
Accept: application/json

# Client requests XML
GET /api/users
Accept: application/xml

# Client requests CSV
GET /api/users/export
Accept: text/csv

# Response
HTTP/1.1 200 OK
Content-Type: application/json
```

## Caching

### Cache-Control Headers

```http
# Public cache, 1 hour
Cache-Control: public, max-age=3600

# Private cache (user-specific)
Cache-Control: private, max-age=3600

# No cache
Cache-Control: no-store

# Revalidate before use
Cache-Control: no-cache, must-revalidate
```

### ETags (Entity Tags)

```http
# First request
GET /api/users/123

# Response
HTTP/1.1 200 OK
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# Subsequent request
GET /api/users/123
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# Not modified response
HTTP/1.1 304 Not Modified
```

## API Documentation (OpenAPI)

```yaml
openapi: 3.0.0
info:
  title: Users API
  version: 1.0.0

paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'

    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: Created
          headers:
            Location:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
        name:
          type: string
```

## Common Patterns

### Bulk Operations

```http
# Bulk create
POST /api/users/bulk
[
  {"email": "user1@example.com"},
  {"email": "user2@example.com"}
]

Response: 207 Multi-Status
{
  "results": [
    {"status": 201, "id": "123"},
    {"status": 409, "error": "Duplicate email"}
  ]
}
```

### Batch Requests

```http
POST /api/batch
{
  "requests": [
    {"method": "GET", "url": "/users/123"},
    {"method": "GET", "url": "/products/456"}
  ]
}

Response:
{
  "responses": [
    {"status": 200, "body": {...}},
    {"status": 404, "body": {...}}
  ]
}
```

### Soft Delete

```http
DELETE /api/users/123        # Soft delete (mark as deleted)
DELETE /api/users/123?hard=true  # Hard delete (permanent)

# Restore
POST /api/users/123/restore
```

### Partial Response

```http
# Request only needed fields
GET /api/users/123?fields=id,name,email

Response:
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com"
}
```

## Best Practices

1. **Use nouns for resources**: `/users`, not `/getUsers`
2. **Use plural nouns**: `/users`, not `/user`
3. **Nest resources logically**: `/users/123/orders` (user's orders)
4. **Keep URLs shallow**: Max 2-3 levels deep
5. **Use hyphens, not underscores**: `/user-profiles`, not `/user_profiles`
6. **Lowercase URLs**: `/users`, not `/Users`
7. **Version from day one**: Start with `/api/v1`
8. **Return resource after POST/PUT**: Client gets updated state
9. **Use ISO-8601 for dates**: `2025-01-15T10:30:00Z`
10. **Provide request IDs**: For debugging and support
