---
name: security-owasp
description: OWASP security best practices - input validation, authentication, authorization, XSS prevention, SQL injection prevention, CSRF protection, security headers, cryptography
---

# OWASP Security Best Practices

Security patterns and defenses against OWASP Top 10 vulnerabilities.

## Core Principles

1. **Defense in depth** - Multiple layers of security
2. **Fail securely** - Deny by default
3. **Least privilege** - Minimum necessary access
4. **Never trust input** - Validate everything
5. **Security by design** - Build it in, not bolt it on

## Input Validation

### Whitelist validation (preferred)

```python
from typing import Literal

def process_order(status: Literal["pending", "approved", "rejected"]):
    # Type system enforces valid values
    pass

def sanitize_filename(filename: str) -> str:
    # Allow only alphanumeric, dash, underscore, dot
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', filename)
```

### Length limits

```python
from pydantic import BaseModel, Field, validator

class UserInput(BaseModel):
    email: str = Field(..., max_length=255)
    comment: str = Field(..., max_length=1000)

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()
```

### Type validation

```python
from pydantic import BaseModel, EmailStr, HttpUrl

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    website: HttpUrl  # Validates URL format
    age: int  # Type enforced
```

## SQL Injection Prevention

### ❌ Vulnerable - String concatenation

```python
# NEVER DO THIS
def get_user(email: str):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)  # SQL injection!
```

### ✓ Parameterized queries

```python
# SQLAlchemy ORM (safest)
def get_user(email: str):
    return db.query(User).filter(User.email == email).first()

# Raw SQL with parameters
def get_user(email: str):
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    return cursor.fetchone()
```

### Query building with ORM

```python
from sqlalchemy import select

def search_users(name: str, role: str):
    stmt = select(User).where(
        User.name.like(f"%{name}%"),
        User.role == role
    )
    return db.execute(stmt).scalars().all()
```

## Cross-Site Scripting (XSS) Prevention

### HTML escaping

```python
from markupsafe import escape

def render_comment(comment: str) -> str:
    # Escape HTML entities
    return escape(comment)

# Template auto-escaping (Jinja2)
# {{ user.comment }}  - Auto-escaped
# {{ user.comment|safe }}  - NOT escaped (dangerous!)
```

### Content Security Policy (CSP)

```python
from fastapi import FastAPI
from fastapi.responses import Response

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://trusted-cdn.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:;"
    )
    return response
```

### Sanitize rich text

```python
import bleach

ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'a']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

def sanitize_html(html: str) -> str:
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
```

## Authentication & Authorization

### Password hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Never do this
def bad_hash(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()  # INSECURE!
```

### JWT tokens

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-from-env"  # Must be from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise AuthenticationError("Invalid token")
```

### Role-based access control

```python
from fastapi import Depends, HTTPException, status

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_role("admin"))
):
    await db.delete_user(user_id)
```

### Session management

```python
from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(SECRET_KEY)

def create_session_token(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})

def verify_session_token(token: str, max_age: int = 3600) -> dict:
    try:
        return serializer.loads(token, max_age=max_age)
    except Exception:
        raise AuthenticationError("Invalid or expired session")
```

## CSRF Protection

### Token-based CSRF

```python
import secrets
from fastapi import Cookie, Form, HTTPException

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)

@app.post("/submit")
async def submit_form(
    csrf_token: str = Form(...),
    session_token: str = Cookie(...),
    data: str = Form(...)
):
    # Verify CSRF token matches session
    session = get_session(session_token)
    if csrf_token != session.csrf_token:
        raise HTTPException(status_code=403, detail="CSRF validation failed")

    # Process form
    return {"status": "success"}
```

### Same-Site cookies

```python
from fastapi import Response

def set_secure_cookie(response: Response, name: str, value: str):
    response.set_cookie(
        key=name,
        value=value,
        httponly=True,  # Prevent JavaScript access
        secure=True,    # HTTPS only
        samesite="lax"  # CSRF protection
    )
```

## Security Headers

### Comprehensive headers

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    # Prevent MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Enable XSS filter
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Clickjacking protection
    response.headers["X-Frame-Options"] = "DENY"

    # HSTS - Force HTTPS
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'"
    )

    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response
```

### CORS configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted-domain.com"],  # Never use "*" in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600
)
```

## Cryptography

### Encryption

```python
from cryptography.fernet import Fernet

# Generate key (store in environment)
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(data: str) -> bytes:
    return cipher.encrypt(data.encode())

def decrypt_data(encrypted: bytes) -> str:
    return cipher.decrypt(encrypted).decode()
```

### Secure random generation

```python
import secrets

# For tokens, API keys
token = secrets.token_urlsafe(32)

# For passwords
password = secrets.token_urlsafe(16)

# For cryptographic operations
random_bytes = secrets.token_bytes(32)

# Never use random module for security
import random
bad_token = random.randint(0, 1000000)  # INSECURE!
```

### Hashing sensitive data

```python
import hashlib

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

# For passwords, use bcrypt/argon2, not plain SHA-256
```

## API Security

### Rate limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")  # 5 requests per minute
async def login(request: Request, credentials: Credentials):
    user = authenticate(credentials)
    return {"token": create_token(user)}
```

### API key validation

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def validate_api_key(api_key: str = Security(api_key_header)):
    hashed = hash_api_key(api_key)
    if not db.is_valid_api_key(hashed):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

### Request size limits

```python
from fastapi import Request, HTTPException

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    # Limit to 10MB
    max_size = 10 * 1024 * 1024

    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        raise HTTPException(status_code=413, detail="Request too large")

    return await call_next(request)
```

## File Upload Security

### Validate file types

```python
import mimetypes
from pathlib import Path

ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.gif'}
ALLOWED_MIMETYPES = {'application/pdf', 'image/png', 'image/jpeg', 'image/gif'}

def validate_file(filename: str, content: bytes) -> bool:
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Extension {ext} not allowed")

    # Check MIME type (magic number)
    import magic
    mime = magic.from_buffer(content, mime=True)
    if mime not in ALLOWED_MIMETYPES:
        raise ValueError(f"MIME type {mime} not allowed")

    return True
```

### Secure file storage

```python
import secrets
from pathlib import Path

def save_upload(file_content: bytes, original_filename: str) -> str:
    # Generate random filename to prevent path traversal
    random_name = secrets.token_hex(16)
    ext = Path(original_filename).suffix.lower()

    # Validate extension
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid file type")

    # Save with random name
    safe_filename = f"{random_name}{ext}"
    upload_dir = Path("/var/uploads")

    # Ensure no path traversal
    file_path = (upload_dir / safe_filename).resolve()
    if not file_path.is_relative_to(upload_dir):
        raise ValueError("Path traversal detected")

    file_path.write_bytes(file_content)
    return safe_filename
```

## Secrets Management

### Environment variables

```python
from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    database_url: SecretStr
    api_key: SecretStr
    jwt_secret: SecretStr

    class Config:
        env_file = ".env"

settings = Settings()

# Access secret value
db_url = settings.database_url.get_secret_value()

# Never log secrets
print(settings.api_key)  # Shows ***** in logs
```

### Vault integration

```python
import hvac

def get_secret(path: str) -> dict:
    client = hvac.Client(url='https://vault.example.com')
    client.token = os.getenv('VAULT_TOKEN')

    secret = client.secrets.kv.v2.read_secret_version(path=path)
    return secret['data']['data']
```

## Logging & Monitoring

### Secure logging

```python
import logging
import re

def sanitize_log(message: str) -> str:
    # Remove credit cards
    message = re.sub(r'\b\d{16}\b', '[CARD]', message)
    # Remove SSN
    message = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', message)
    # Remove emails
    message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', message)
    return message

def secure_log(level: str, message: str):
    sanitized = sanitize_log(message)
    logging.log(getattr(logging, level.upper()), sanitized)
```

### Security event monitoring

```python
from datetime import datetime
from typing import Optional

class SecurityEvent:
    def __init__(
        self,
        event_type: str,
        user_id: Optional[int],
        ip_address: str,
        details: dict
    ):
        self.timestamp = datetime.utcnow()
        self.event_type = event_type
        self.user_id = user_id
        self.ip_address = ip_address
        self.details = details

def log_security_event(event: SecurityEvent):
    # Log to security monitoring system
    logger.warning(f"Security event: {event.event_type}", extra={
        "user_id": event.user_id,
        "ip": event.ip_address,
        "details": event.details
    })

# Usage
log_security_event(SecurityEvent(
    event_type="failed_login",
    user_id=None,
    ip_address=request.client.host,
    details={"email": email, "reason": "invalid_password"}
))
```

## Anti-Patterns

### ❌ Storing passwords in plain text

```python
# NEVER DO THIS
class User:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password  # Plain text password!
```

**Fix:** Always hash passwords with bcrypt or argon2

### ❌ Using MD5/SHA1 for passwords

```python
# INSECURE
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()
```

**Fix:** Use bcrypt, argon2, or scrypt

### ❌ Exposing stack traces

```python
# BAD - Leaks internal information
@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "traceback": traceback.format_exc()}
    )
```

**Fix:** Log full error, return generic message to user

### ❌ SQL string concatenation

```python
# SQL INJECTION VULNERABILITY
query = f"SELECT * FROM users WHERE id = {user_id}"
```

**Fix:** Use parameterized queries or ORM

### ❌ Trusting client-side validation

```python
# BAD - Client can bypass
@app.post("/transfer")
async def transfer(amount: float):
    # No server-side validation!
    perform_transfer(amount)
```

**Fix:** Always validate on server

### ❌ Using predictable IDs

```python
# BAD - Sequential, guessable
GET /users/1
GET /users/2  # Can enumerate all users
```

**Fix:** Use UUIDs or non-sequential IDs

### ❌ Hardcoded secrets

```python
# NEVER DO THIS
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://admin:password@db.example.com/prod"
```

**Fix:** Use environment variables or secret management

### ❌ Insufficient authorization checks

```python
# BAD - Missing ownership check
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, user: User = Depends(get_current_user)):
    db.delete_post(post_id)  # Any authenticated user can delete any post!
```

**Fix:** Verify ownership or permissions

```python
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, user: User = Depends(get_current_user)):
    post = db.get_post(post_id)
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete_post(post_id)
```

## Testing Security

### SQL injection tests

```python
def test_sql_injection():
    # Try injection
    malicious_email = "admin'--"
    response = client.get(f"/users?email={malicious_email}")

    # Should not expose database error
    assert response.status_code != 500
    assert "SQL" not in response.text
```

### XSS tests

```python
def test_xss_prevention():
    xss_payload = "<script>alert('XSS')</script>"
    response = client.post("/comments", json={"text": xss_payload})

    # Script should be escaped
    comment = response.json()
    assert "<script>" not in comment["text"]
    assert "&lt;script&gt;" in comment["text"]
```

### CSRF tests

```python
def test_csrf_protection():
    # Request without CSRF token
    response = client.post("/submit", data={"field": "value"})
    assert response.status_code == 403
```

## Key Takeaways

1. **Never trust input** - Validate everything from users
2. **Use parameterized queries** - Prevent SQL injection
3. **Hash passwords with bcrypt** - Never plain text or MD5
4. **Escape output** - Prevent XSS attacks
5. **Add security headers** - CSP, HSTS, X-Frame-Options
6. **Use HTTPS everywhere** - Encrypt data in transit
7. **Rate limit APIs** - Prevent brute force
8. **Validate file uploads** - Check type and content
9. **Keep secrets in environment** - Never hardcode
10. **Defense in depth** - Multiple security layers
