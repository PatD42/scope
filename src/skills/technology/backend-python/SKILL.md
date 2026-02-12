---
name: backend-python
description: Python best practices, patterns, and idioms for backend development. Use when story requires Python code, async/await patterns, decorators, context managers, type hints, error handling, testing patterns, virtual environments, or Python project structure.
---

# Backend Python

Python best practices, common patterns, and idioms for building robust backend applications.

## Project Structure

```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── main.py
│       ├── models/
│       ├── services/
│       ├── utils/
│       └── config.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## Virtual Environments

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Freeze dependencies
pip freeze > requirements.txt
```

## Type Hints

```python
from typing import List, Dict, Optional, Union, Callable

def process_users(
    users: List[Dict[str, str]],
    filter_fn: Optional[Callable[[Dict], bool]] = None
) -> List[str]:
    """Process users and return names."""
    filtered = users if filter_fn is None else [u for u in users if filter_fn(u)]
    return [u["name"] for u in filtered]

# Generic types
from typing import TypeVar, Generic

T = TypeVar('T')

class Repository(Generic[T]):
    def get(self, id: str) -> Optional[T]:
        ...
```

## Async/Await

```python
import asyncio
import aiohttp

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()

async def fetch_all(urls: List[str]) -> List[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# Run async function
results = asyncio.run(fetch_all(urls))
```

## Context Managers

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(name: str):
    """Time a block of code."""
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"{name}: {elapsed:.2f}s")

# Usage
with timer("Database query"):
    # Your code here
    pass

# Async context managers
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_connection():
    conn = await create_connection()
    try:
        yield conn
    finally:
        await conn.close()
```

## Decorators

```python
from functools import wraps
import time

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def fetch_data():
    # May fail and will retry
    pass

# Property decorators
class User:
    def __init__(self, email: str):
        self._email = email

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError("Invalid email")
        self._email = value
```

## Error Handling

```python
# Custom exceptions
class ValidationError(Exception):
    """Raised when validation fails."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

# Exception handling
try:
    result = risky_operation()
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error")
    raise
finally:
    cleanup()

# Context manager for exceptions
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("file.txt")  # Ignores if file doesn't exist
```

## Dataclasses

```python
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate after initialization."""
        if "@" not in self.email:
            raise ValueError("Invalid email")

# Immutable dataclass
@dataclass(frozen=True)
class Config:
    api_key: str
    timeout: int = 30
```

## Enums

```python
from enum import Enum, auto

class Status(str, Enum):
    """User status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class Permission(Enum):
    """Permission flags."""
    READ = auto()
    WRITE = auto()
    DELETE = auto()

# Usage
user.status = Status.ACTIVE
if user.status == Status.ACTIVE:
    print("User is active")
```

## Comprehensions

```python
# List comprehension
squares = [x**2 for x in range(10) if x % 2 == 0]

# Dict comprehension
user_map = {user.id: user.name for user in users}

# Set comprehension
unique_tags = {tag.lower() for user in users for tag in user.tags}

# Generator expression (memory efficient)
total = sum(x**2 for x in range(1000000))
```

## Itertools

```python
from itertools import chain, groupby, islice, cycle

# Chain iterables
all_items = chain(list1, list2, list3)

# Group by key
from operator import itemgetter
users_by_status = {k: list(v) for k, v in groupby(
    sorted(users, key=itemgetter("status")),
    key=itemgetter("status")
)}

# Take first N items
first_ten = list(islice(infinite_generator(), 10))

# Cycle through values
colors = cycle(["red", "green", "blue"])
```

## Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)

# Structured logging with extra fields
logger.info("User logged in", extra={
    "user_id": "123",
    "ip": "192.168.1.1"
})
```

## Testing with Pytest

```python
import pytest
from myapp.services import UserService

@pytest.fixture
def user_service():
    """Create user service fixture."""
    return UserService(db_url="sqlite:///:memory:")

def test_create_user(user_service):
    """Test user creation."""
    user = user_service.create(email="test@example.com")
    assert user.email == "test@example.com"

def test_create_duplicate_user(user_service):
    """Test duplicate email raises error."""
    user_service.create(email="test@example.com")
    with pytest.raises(ValueError):
        user_service.create(email="test@example.com")

# Parametrized tests
@pytest.mark.parametrize("email,valid", [
    ("test@example.com", True),
    ("invalid", False),
    ("@example.com", False),
])
def test_email_validation(email, valid):
    if valid:
        assert validate_email(email)
    else:
        with pytest.raises(ValueError):
            validate_email(email)

# Async tests
@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data()
    assert result is not None
```

## Dependency Injection

```python
from typing import Protocol

class UserRepository(Protocol):
    """User repository interface."""
    def get(self, id: str) -> Optional[User]: ...
    def save(self, user: User) -> None: ...

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def activate_user(self, id: str) -> User:
        user = self.repo.get(id)
        if not user:
            raise ValueError("User not found")
        user.status = Status.ACTIVE
        self.repo.save(user)
        return user

# Usage
repo = SqlUserRepository(db)
service = UserService(repo)
```

## Configuration Management

```python
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings."""
    database_url: str
    api_key: str
    debug: bool = False
    max_connections: int = Field(default=10, ge=1, le=100)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Load settings
settings = Settings()
```

## Best Practices

1. **Use pathlib for file paths**: `from pathlib import Path`
2. **Prefer f-strings**: `f"Hello {name}"` over `"Hello %s" % name`
3. **Use `in` for membership**: `if x in collection:` not `if collection.count(x) > 0:`
4. **Avoid mutable default arguments**: Use `None` and initialize in function
5. **Use `with` for resources**: Files, connections, locks
6. **Follow PEP 8**: Use `black` for formatting, `flake8` for linting
7. **Type hints everywhere**: Helps IDEs and catches errors
8. **Use `logging`, not `print`**: For production code
9. **Write docstrings**: For modules, classes, functions
10. **Test thoroughly**: Unit, integration, and e2e tests
