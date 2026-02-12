---
name: quality-design-patterns
description: Software design patterns and principles - GoF patterns, SOLID principles, DRY, YAGNI, composition over inheritance, dependency injection
---

# Quality Design Patterns

Proven design patterns and principles for writing maintainable, extensible software.

## SOLID Principles

### S - Single Responsibility Principle

A class should have one, and only one, reason to change.

**❌ Bad - Multiple responsibilities:**
```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save_to_database(self):
        # Database logic
        db.save(self)

    def send_welcome_email(self):
        # Email logic
        smtp.send(...)
```

**✓ Good - Single responsibility:**
```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    def save(self, user):
        db.save(user)

class EmailService:
    def send_welcome(self, user):
        smtp.send(...)
```

### O - Open/Closed Principle

Software entities should be open for extension, but closed for modification.

**✓ Using strategy pattern:**
```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount):
        pass

class CreditCardProcessor(PaymentProcessor):
    def process(self, amount):
        # Credit card logic
        pass

class PayPalProcessor(PaymentProcessor):
    def process(self, amount):
        # PayPal logic
        pass

# Add new payment method without modifying existing code
class BitcoinProcessor(PaymentProcessor):
    def process(self, amount):
        # Bitcoin logic
        pass
```

### L - Liskov Substitution Principle

Subtypes must be substitutable for their base types.

**❌ Bad - Violates LSP:**
```python
class Rectangle:
    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width  # Violates LSP!

    def set_height(self, height):
        self.width = height
        self.height = height
```

**✓ Good - Composition over inheritance:**
```python
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side
```

### I - Interface Segregation Principle

Clients should not be forced to depend on interfaces they don't use.

**❌ Bad - Fat interface:**
```python
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

class Robot(Worker):
    def work(self):
        # Work logic
        pass

    def eat(self):
        # Robots don't eat! Forced to implement
        raise NotImplementedError()
```

**✓ Good - Segregated interfaces:**
```python
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Human(Workable, Eatable):
    def work(self):
        pass

    def eat(self):
        pass

class Robot(Workable):
    def work(self):
        pass
```

### D - Dependency Inversion Principle

Depend on abstractions, not concretions.

**❌ Bad - Depends on concrete class:**
```python
class EmailService:
    def send(self, to, message):
        # SMTP logic
        pass

class UserService:
    def __init__(self):
        self.email_service = EmailService()  # Concrete dependency

    def register_user(self, user):
        self.email_service.send(user.email, "Welcome!")
```

**✓ Good - Depends on abstraction:**
```python
class NotificationService(ABC):
    @abstractmethod
    def send(self, to, message):
        pass

class EmailService(NotificationService):
    def send(self, to, message):
        # SMTP logic
        pass

class UserService:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def register_user(self, user):
        self.notification_service.send(user.email, "Welcome!")
```

## Creational Patterns

### Factory Pattern

Create objects without specifying exact class.

```python
class DocumentFactory:
    @staticmethod
    def create(doc_type: str):
        if doc_type == "pdf":
            return PDFDocument()
        elif doc_type == "word":
            return WordDocument()
        elif doc_type == "html":
            return HTMLDocument()
        else:
            raise ValueError(f"Unknown type: {doc_type}")

# Usage
doc = DocumentFactory.create("pdf")
```

### Builder Pattern

Construct complex objects step by step.

```python
class QueryBuilder:
    def __init__(self):
        self._query = ""
        self._params = []

    def select(self, *fields):
        self._query += f"SELECT {', '.join(fields)} "
        return self

    def from_(self, table):
        self._query += f"FROM {table} "
        return self

    def where(self, condition, *params):
        self._query += f"WHERE {condition} "
        self._params.extend(params)
        return self

    def build(self):
        return self._query, self._params

# Usage
query, params = (QueryBuilder()
                 .select("id", "name", "email")
                 .from_("users")
                 .where("age > ?", 18)
                 .build())
```

### Singleton Pattern

Ensure class has only one instance.

```python
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = create_connection()
        return cls._instance

# Usage
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # Same instance
```

**Better approach in Python - Module-level singleton:**
```python
# database.py
_connection = create_connection()

def get_connection():
    return _connection
```

## Structural Patterns

### Adapter Pattern

Convert interface of class to another interface.

```python
class LegacyUser:
    def get_name(self):
        return f"{self.first_name} {self.last_name}"

class ModernUser:
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class LegacyUserAdapter:
    def __init__(self, legacy_user):
        self.legacy_user = legacy_user

    @property
    def full_name(self):
        return self.legacy_user.get_name()

# Usage - both work with modern interface
def greet(user: ModernUser):
    print(f"Hello, {user.full_name}")

greet(ModernUser(...))
greet(LegacyUserAdapter(LegacyUser(...)))
```

### Decorator Pattern

Add behavior to objects dynamically.

```python
from functools import wraps
import time

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

def cache_decorator(func):
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return wrapper

@timing_decorator
@cache_decorator
def expensive_computation(n):
    return sum(range(n))
```

### Facade Pattern

Provide simplified interface to complex subsystem.

```python
class VideoFile:
    def __init__(self, filename):
        self.filename = filename

class VideoCodec:
    def extract(self, file):
        pass

class AudioMixer:
    def mix(self, audio):
        pass

# Facade
class VideoConverter:
    def convert(self, filename, format):
        file = VideoFile(filename)
        codec = VideoCodec()
        audio = codec.extract(file)

        mixer = AudioMixer()
        result = mixer.mix(audio)

        # Many more steps...
        return result

# Usage - Simple interface
converter = VideoConverter()
converter.convert("video.mp4", "avi")
```

## Behavioral Patterns

### Strategy Pattern

Define family of algorithms, make them interchangeable.

```python
from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data):
        pass

class QuickSort(SortStrategy):
    def sort(self, data):
        # Quick sort implementation
        return sorted(data)

class MergeSort(SortStrategy):
    def sort(self, data):
        # Merge sort implementation
        return sorted(data)

class DataProcessor:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def process(self, data):
        return self.strategy.sort(data)

# Usage
processor = DataProcessor(QuickSort())
result = processor.process([3, 1, 4, 1, 5])
```

### Observer Pattern

Define one-to-many dependency between objects.

```python
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class Observer(ABC):
    @abstractmethod
    def update(self, message):
        pass

class EmailObserver(Observer):
    def update(self, message):
        print(f"Sending email: {message}")

class LogObserver(Observer):
    def update(self, message):
        print(f"Logging: {message}")

# Usage
subject = Subject()
subject.attach(EmailObserver())
subject.attach(LogObserver())
subject.notify("User registered")
```

### Command Pattern

Encapsulate request as object.

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class CreateFileCommand(Command):
    def __init__(self, filename):
        self.filename = filename

    def execute(self):
        with open(self.filename, 'w') as f:
            f.write("")

    def undo(self):
        os.remove(self.filename)

class CommandInvoker:
    def __init__(self):
        self.history = []

    def execute(self, command):
        command.execute()
        self.history.append(command)

    def undo(self):
        if self.history:
            command = self.history.pop()
            command.undo()

# Usage
invoker = CommandInvoker()
invoker.execute(CreateFileCommand("test.txt"))
invoker.undo()  # Removes file
```

## Additional Principles

### DRY (Don't Repeat Yourself)

**❌ Bad:**
```python
def calculate_order_total(order):
    total = 0
    for item in order.items:
        total += item.price * item.quantity
    tax = total * 0.1
    return total + tax

def calculate_invoice_total(invoice):
    total = 0
    for item in invoice.items:
        total += item.price * item.quantity  # Duplicate
    tax = total * 0.1  # Duplicate
    return total + tax
```

**✓ Good:**
```python
def calculate_subtotal(items):
    return sum(item.price * item.quantity for item in items)

def calculate_total(items, tax_rate=0.1):
    subtotal = calculate_subtotal(items)
    tax = subtotal * tax_rate
    return subtotal + tax
```

### YAGNI (You Aren't Gonna Need It)

Don't add functionality until it's needed.

**❌ Bad - Speculative generality:**
```python
class User:
    def __init__(self, name):
        self.name = name
        self.preferences = {}  # Might need later?
        self.settings = {}     # Maybe useful?
        self.metadata = {}     # Just in case?
```

**✓ Good - Add when needed:**
```python
class User:
    def __init__(self, name):
        self.name = name
```

### Composition Over Inheritance

**❌ Bad - Inheritance:**
```python
class Animal:
    def eat(self):
        pass

class FlyingAnimal(Animal):
    def fly(self):
        pass

class SwimmingAnimal(Animal):
    def swim(self):
        pass

# Problem: What about duck (flies AND swims)?
class Duck(FlyingAnimal, SwimmingAnimal):  # Multiple inheritance issues
    pass
```

**✓ Good - Composition:**
```python
class Animal:
    def __init__(self):
        self.abilities = []

    def add_ability(self, ability):
        self.abilities.append(ability)

class Flying:
    def fly(self):
        print("Flying")

class Swimming:
    def swim(self):
        print("Swimming")

# Usage
duck = Animal()
duck.add_ability(Flying())
duck.add_ability(Swimming())
```

### Dependency Injection

**❌ Bad - Hard-coded dependency:**
```python
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hard-coded
        self.email = SMTPEmailService()  # Hard-coded
```

**✓ Good - Injected dependencies:**
```python
class UserService:
    def __init__(self, db: Database, email: EmailService):
        self.db = db
        self.email = email

# Usage - Easy to test and swap implementations
service = UserService(
    db=PostgresDatabase(),
    email=SMTPEmailService()
)

# In tests
test_service = UserService(
    db=InMemoryDatabase(),
    email=MockEmailService()
)
```

## Anti-Patterns

### ❌ God Object

One class does everything:
```python
class Application:
    def handle_http_request(self):
        pass

    def query_database(self):
        pass

    def send_email(self):
        pass

    def generate_report(self):
        pass
```

**Fix:** Split into separate classes with single responsibilities

### ❌ Premature Optimization

Optimizing before measuring:
```python
# Writing complex, hard-to-read code for "performance"
# before profiling shows it's a bottleneck
```

**Fix:** Make it work, make it right, make it fast (in that order)

### ❌ Magic Numbers

Hard-coded values without explanation:
```python
if user.age > 18 and balance > 1000:
    ...
```

**Fix:** Named constants
```python
MINIMUM_AGE = 18
MINIMUM_BALANCE = 1000

if user.age > MINIMUM_AGE and balance > MINIMUM_BALANCE:
    ...
```

## Key Takeaways

1. **SOLID principles** - Foundation of good OO design
2. **Single Responsibility** - One class, one reason to change
3. **Dependency Injection** - Pass dependencies, don't create them
4. **Composition > Inheritance** - Favor has-a over is-a
5. **Factory pattern** - Decouple creation from usage
6. **Strategy pattern** - Make algorithms interchangeable
7. **Observer pattern** - Decouple publishers from subscribers
8. **DRY principle** - Extract common logic
9. **YAGNI principle** - Don't build what you don't need
10. **Design patterns are tools** - Use when appropriate, not everywhere
