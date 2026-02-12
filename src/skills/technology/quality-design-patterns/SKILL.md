---
name: quality-design-patterns
description: Software design patterns and SOLID principles. Use when story requires refactoring, design pattern implementation, SOLID principles, code quality improvement, architectural patterns, or avoiding anti-patterns.
---

# Quality Design Patterns

Software design patterns, SOLID principles, and best practices for maintainable code.

## SOLID Principles

### Single Responsibility Principle (SRP)

A class should have one reason to change.

```python
# ❌ Bad - Multiple responsibilities
class User:
    def save_to_database(self):
        ...
    def send_email(self):
        ...
    def generate_report(self):
        ...

# ✅ Good - Single responsibility
class User:
    def __init__(self, data):
        self.data = data

class UserRepository:
    def save(self, user):
        ...

class EmailService:
    def send_welcome_email(self, user):
        ...

class ReportGenerator:
    def generate_user_report(self, user):
        ...
```

### Open/Closed Principle (OCP)

Open for extension, closed for modification.

```python
# ❌ Bad - Modifying existing code
class DiscountCalculator:
    def calculate(self, order, discount_type):
        if discount_type == "percentage":
            return order.total * 0.9
        elif discount_type == "fixed":
            return order.total - 10
        # Need to modify for new discount types

# ✅ Good - Extend without modifying
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order):
        pass

class PercentageDiscount(DiscountStrategy):
    def calculate(self, order):
        return order.total * 0.9

class FixedDiscount(DiscountStrategy):
    def calculate(self, order):
        return order.total - 10

class DiscountCalculator:
    def __init__(self, strategy: DiscountStrategy):
        self.strategy = strategy
    
    def calculate(self, order):
        return self.strategy.calculate(order)
```

### Liskov Substitution Principle (LSP)

Subtypes must be substitutable for base types.

```python
# ❌ Bad - Violates LSP
class Bird:
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def fly(self):
        raise Exception("Can't fly!")  # Breaks contract

# ✅ Good - Proper abstraction
class Bird:
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        return "Flying"
    
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def move(self):
        return "Swimming"
```

### Interface Segregation Principle (ISP)

Clients shouldn't depend on interfaces they don't use.

```python
# ❌ Bad - Fat interface
class Worker:
    def work(self):
        pass
    def eat(self):
        pass

class Robot(Worker):
    def work(self):
        return "Working"
    def eat(self):
        raise NotImplementedError("Robots don't eat!")

# ✅ Good - Segregated interfaces
class Workable:
    def work(self):
        pass

class Eatable:
    def eat(self):
        pass

class Human(Workable, Eatable):
    def work(self):
        return "Working"
    def eat(self):
        return "Eating"

class Robot(Workable):
    def work(self):
        return "Working"
```

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions.

```python
# ❌ Bad - Depends on concrete class
class EmailService:
    def send(self, message):
        # Send email
        pass

class Notification:
    def __init__(self):
        self.email = EmailService()  # Tight coupling
    
    def notify(self, message):
        self.email.send(message)

# ✅ Good - Depends on abstraction
class MessageService(ABC):
    @abstractmethod
    def send(self, message):
        pass

class EmailService(MessageService):
    def send(self, message):
        # Send email
        pass

class SMSService(MessageService):
    def send(self, message):
        # Send SMS
        pass

class Notification:
    def __init__(self, service: MessageService):
        self.service = service  # Depends on abstraction
    
    def notify(self, message):
        self.service.send(message)
```

## Creational Patterns

### Factory Method

```python
class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount):
        pass

class CreditCardProcessor(PaymentProcessor):
    def process(self, amount):
        return f"Processing ${amount} via credit card"

class PayPalProcessor(PaymentProcessor):
    def process(self, amount):
        return f"Processing ${amount} via PayPal"

class PaymentFactory:
    @staticmethod
    def create_processor(payment_type: str) -> PaymentProcessor:
        if payment_type == "credit_card":
            return CreditCardProcessor()
        elif payment_type == "paypal":
            return PayPalProcessor()
        raise ValueError(f"Unknown payment type: {payment_type}")

# Usage
processor = PaymentFactory.create_processor("credit_card")
processor.process(100)
```

### Singleton

```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        # Setup connection
        pass

# Usage
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # Same instance
```

### Builder

```python
class Pizza:
    def __init__(self):
        self.size = None
        self.cheese = False
        self.pepperoni = False
        self.mushrooms = False

class PizzaBuilder:
    def __init__(self):
        self.pizza = Pizza()
    
    def set_size(self, size):
        self.pizza.size = size
        return self
    
    def add_cheese(self):
        self.pizza.cheese = True
        return self
    
    def add_pepperoni(self):
        self.pizza.pepperoni = True
        return self
    
    def add_mushrooms(self):
        self.pizza.mushrooms = True
        return self
    
    def build(self):
        return self.pizza

# Usage
pizza = (PizzaBuilder()
    .set_size("large")
    .add_cheese()
    .add_pepperoni()
    .build())
```

## Structural Patterns

### Adapter

```python
# Legacy API
class LegacyPayment:
    def make_payment(self, amount):
        return f"Legacy payment: ${amount}"

# New interface
class ModernPayment(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass

# Adapter
class PaymentAdapter(ModernPayment):
    def __init__(self, legacy_payment: LegacyPayment):
        self.legacy = legacy_payment
    
    def process_payment(self, amount):
        return self.legacy.make_payment(amount)

# Usage
legacy = LegacyPayment()
adapter = PaymentAdapter(legacy)
adapter.process_payment(100)  # Uses modern interface
```

### Decorator

```python
from functools import wraps

def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

@log_execution
@measure_time
def process_data(data):
    # Processing logic
    pass
```

## Behavioral Patterns

### Strategy

```python
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

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy
    
    def sort_data(self, data):
        return self.strategy.sort(data)

# Usage
sorter = Sorter(QuickSort())
result = sorter.sort_data([3, 1, 4, 1, 5])
```

### Observer

```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class Observer(ABC):
    @abstractmethod
    def update(self, event):
        pass

class EmailNotifier(Observer):
    def update(self, event):
        print(f"Email sent for event: {event}")

class SMSNotifier(Observer):
    def update(self, event):
        print(f"SMS sent for event: {event}")

# Usage
subject = Subject()
subject.attach(EmailNotifier())
subject.attach(SMSNotifier())
subject.notify("User registered")
```

### Command

```python
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class CreateUserCommand(Command):
    def __init__(self, user_data):
        self.user_data = user_data
    
    def execute(self):
        print(f"Creating user: {self.user_data}")

class DeleteUserCommand(Command):
    def __init__(self, user_id):
        self.user_id = user_id
    
    def execute(self):
        print(f"Deleting user: {self.user_id}")

class CommandInvoker:
    def __init__(self):
        self.history = []
    
    def execute_command(self, command: Command):
        command.execute()
        self.history.append(command)

# Usage
invoker = CommandInvoker()
invoker.execute_command(CreateUserCommand({"email": "test@example.com"}))
```

## Anti-Patterns to Avoid

### God Object

```python
# ❌ Bad - God object does everything
class ApplicationManager:
    def manage_users(self): ...
    def process_payments(self): ...
    def send_emails(self): ...
    def generate_reports(self): ...
    def manage_database(self): ...
```

### Spaghetti Code

```python
# ❌ Bad - Complex, tangled logic
def process(data):
    if data:
        for item in data:
            if item.status == "active":
                if item.price > 100:
                    if item.category == "premium":
                        # Deep nesting continues...
                        pass
```

### Magic Numbers

```python
# ❌ Bad - Magic numbers
if user.age > 18:
    ...

# ✅ Good - Named constants
MIN_ADULT_AGE = 18
if user.age > MIN_ADULT_AGE:
    ...
```

## Best Practices

1. **Keep it simple**: Don't over-engineer
2. **DRY**: Don't Repeat Yourself
3. **YAGNI**: You Aren't Gonna Need It
4. **Composition over inheritance**: Favor composition
5. **Program to interfaces**: Not implementations
6. **Encapsulate what varies**: Isolate change
7. **Prefer immutability**: Reduce side effects
8. **Write testable code**: Dependency injection
9. **Name things well**: Clear, descriptive names
10. **Refactor continuously**: Improve gradually
