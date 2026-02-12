---
name: security-owasp
description: Security best practices and OWASP Top 10. Use when story requires security review, vulnerability prevention, authentication/authorization, input validation, SQL injection prevention, XSS protection, CSRF protection, or secure coding practices.
---

# Security OWASP

Security best practices and OWASP Top 10 vulnerability prevention.

## OWASP Top 10 (2021)

1. **Broken Access Control**
2. **Cryptographic Failures**
3. **Injection**
4. **Insecure Design**
5. **Security Misconfiguration**
6. **Vulnerable and Outdated Components**
7. **Identification and Authentication Failures**
8. **Software and Data Integrity Failures**
9. **Security Logging and Monitoring Failures**
10. **Server-Side Request Forgery (SSRF)**

## 1. Broken Access Control

**Vulnerability**: Users accessing unauthorized resources.

```python
# ❌ Bad - No authorization check
@app.route('/users/<user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    return jsonify(user)

# ✅ Good - Check ownership
@app.route('/users/<user_id>')
@login_required
def get_user(user_id):
    user = User.query.get(user_id)
    if user.id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden
    return jsonify(user)
```

## 2. Cryptographic Failures

**Vulnerability**: Sensitive data exposed due to weak encryption.

```python
# ❌ Bad - Plain text passwords
user.password = request.form['password']

# ✅ Good - Hashed passwords
from werkzeug.security import generate_password_hash, check_password_hash

user.password_hash = generate_password_hash(request.form['password'])

# Verify
if check_password_hash(user.password_hash, password):
    login_user(user)

# ✅ Good - Encrypt sensitive data at rest
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)
encrypted_ssn = cipher.encrypt(ssn.encode())
```

## 3. Injection (SQL, Command, etc.)

### SQL Injection

```python
# ❌ Bad - String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)  # Vulnerable to: ' OR '1'='1

# ✅ Good - Parameterized queries
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# ✅ Good - ORM
user = User.query.filter_by(email=email).first()
```

### Command Injection

```python
# ❌ Bad - Shell injection
os.system(f"ping {user_input}")

# ✅ Good - Use subprocess with list
import subprocess
subprocess.run(["ping", "-c", "1", user_input], check=True)
```

## 4. Cross-Site Scripting (XSS)

```python
# ❌ Bad - Unescaped user input
@app.route('/search')
def search():
    query = request.args.get('q')
    return f"<h1>Results for: {query}</h1>"  # XSS!

# ✅ Good - Escape output
from markupsafe import escape
return f"<h1>Results for: {escape(query)}</h1>"

# ✅ Good - Use templates (auto-escapes)
return render_template('search.html', query=query)

# Content Security Policy header
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

## 5. Cross-Site Request Forgery (CSRF)

```python
# ✅ CSRF protection with tokens
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Form includes CSRF token
<form method="POST">
    {{ csrf_token() }}
    <input name="email">
</form>

# SameSite cookie attribute
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
```

## 6. Authentication & Session Management

```python
# ✅ Secure password requirements
import re

def validate_password(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*]', password):
        return False
    return True

# ✅ Secure session configuration
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JS access
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# ✅ Rate limiting for login attempts
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    ...
```

## 7. Security Misconfigurations

```python
# ❌ Bad - Debug mode in production
app.run(debug=True)

# ✅ Good - Disable debug in production
app.config['DEBUG'] = False

# ✅ Hide server version
@app.after_request
def remove_header(response):
    response.headers.pop('Server', None)
    return response

# ✅ Security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## 8. Input Validation

```python
from pydantic import BaseModel, validator, EmailStr

class UserInput(BaseModel):
    email: EmailStr  # Validates email format
    age: int
    username: str

    @validator('age')
    def age_must_be_valid(cls, v):
        if v < 18 or v > 120:
            raise ValueError('Age must be between 18 and 120')
        return v

    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

# Validate input
try:
    user = UserInput(**request.json)
except ValidationError as e:
    return jsonify({'error': e.errors()}), 400
```

## 9. Server-Side Request Forgery (SSRF)

```python
# ❌ Bad - Unrestricted URL fetching
import requests

url = request.args.get('url')
response = requests.get(url)  # SSRF!

# ✅ Good - Whitelist allowed domains
ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']

from urllib.parse import urlparse

def is_safe_url(url):
    parsed = urlparse(url)
    return parsed.netloc in ALLOWED_DOMAINS

if is_safe_url(url):
    response = requests.get(url)
else:
    abort(400, 'Invalid URL')
```

## 10. Secure File Uploads

```python
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file', 400
    
    file = request.files['file']
    
    # Validate filename
    if not allowed_file(file.filename):
        return 'Invalid file type', 400
    
    # Secure filename (remove path traversal)
    filename = secure_filename(file.filename)
    
    # Validate file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    if size > MAX_FILE_SIZE:
        return 'File too large', 400
    file.seek(0)
    
    # Save outside webroot
    upload_path = os.path.join('/secure/uploads', filename)
    file.save(upload_path)
    
    return 'File uploaded', 200
```

## 11. Secrets Management

```python
# ❌ Bad - Hardcoded secrets
API_KEY = "sk-1234567890abcdef"

# ✅ Good - Environment variables
import os
API_KEY = os.getenv('API_KEY')

# ✅ Good - Secrets manager (AWS)
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

API_KEY = get_secret('prod/api-key')
```

## 12. Logging & Monitoring

```python
import logging

# ✅ Log security events
logger = logging.getLogger(__name__)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    
    user = User.query.filter_by(email=email).first()
    if not user or not check_password(user, request.form['password']):
        logger.warning(f"Failed login attempt for {email} from {request.remote_addr}")
        return 'Invalid credentials', 401
    
    logger.info(f"Successful login for {email}")
    return 'Logged in', 200

# ❌ Don't log sensitive data
logger.info(f"User password: {password}")  # Never!

# ✅ Log sanitized data
logger.info(f"Password reset for user {user.id}")
```

## Security Checklist

- [ ] **Authentication**: Strong passwords, rate limiting
- [ ] **Authorization**: Check permissions on every request
- [ ] **Input validation**: Validate and sanitize all inputs
- [ ] **Output encoding**: Escape user data in responses
- [ ] **CSRF protection**: Use CSRF tokens
- [ ] **SQL injection**: Use parameterized queries
- [ ] **XSS protection**: Escape output, use CSP
- [ ] **Secure cookies**: HttpOnly, Secure, SameSite
- [ ] **HTTPS only**: Redirect HTTP to HTTPS
- [ ] **Security headers**: X-Frame-Options, CSP, HSTS
- [ ] **Rate limiting**: Prevent brute force
- [ ] **File uploads**: Validate type and size
- [ ] **Secrets**: Use environment variables or secrets manager
- [ ] **Logging**: Log security events (no sensitive data)
- [ ] **Dependencies**: Keep packages updated
- [ ] **Error messages**: Don't leak implementation details

## Best Practices

1. **Principle of least privilege**: Minimum necessary permissions
2. **Defense in depth**: Multiple security layers
3. **Fail securely**: Deny access on error
4. **Don't trust user input**: Validate everything
5. **Keep secrets secret**: Never commit to version control
6. **Update dependencies**: Patch security vulnerabilities
7. **Use HTTPS everywhere**: Encrypt data in transit
8. **Hash passwords**: Never store plaintext
9. **Log security events**: Detect and respond to attacks
10. **Security headers**: Protect against common attacks
