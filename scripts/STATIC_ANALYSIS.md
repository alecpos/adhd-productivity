# Static Analysis Report

## Executive Summary

- Files analyzed: 2
- High complexity files: 2
- Files needing type hint improvements: 0
- Security hotspots: 1
- Test gaps: 0
- Code smells detected: 34
- Architectural coupling score: 0.00
- Architectural cohesion score: 0.00


## Priority Issues


### Severity 1 Issues

- [security] ./function_extractor.py: Potential hardcoded secret in variable: key
  - Suggested fix: Review and fix security vulnerability


### Severity 2 Issues

- [complexity] ./static_analysis.py: High cyclomatic complexity (363)
  - Suggested fix: Break down complex functions into smaller, focused methods

- [complexity] ./static_analysis.py: High cognitive complexity (863)
  - Suggested fix: Simplify complex logic and improve code readability

- [complexity] ./function_extractor.py: High cyclomatic complexity (83)
  - Suggested fix: Break down complex functions into smaller, focused methods

- [complexity] ./function_extractor.py: High cognitive complexity (278)
  - Suggested fix: Simplify complex logic and improve code readability


### Severity 3 Issues

- [maintainability] ./static_analysis.py: Low maintainability index (0.0)
  - Suggested fix: Improve code structure and reduce complexity

- [maintainability] ./function_extractor.py: Low maintainability index (7.2)
  - Suggested fix: Improve code structure and reduce complexity


## Architecture Analysis


### Dependency Analysis

- Coupling Score: 0.00
- Cohesion Score: 0.00

## Code Smells


### Hardcoded Path

- ./function_extractor.py::153: Hardcoded file path: lines = [line.rstrip() for line in docstring.split('\n')]
  - Suggestion: Move path to configuration file or environment variable

Refactoring steps:

1. Use configuration management
```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


Validation tests:

```python
import pytest
from pathlib import Path

def test_config_paths():
    assert isinstance(Config.BASE_DIR, Path)
    assert Config.DATA_DIR.parent == Config.BASE_DIR
    assert Config.CACHE_DIR.parent == Config.BASE_DIR
    assert Config.LOG_DIR.parent == Config.BASE_DIR

def test_setup_logging(tmp_path):
    with patch('config.Config.LOG_DIR', tmp_path):
        setup_logging()
        assert (tmp_path / 'app.log').exists()
```

- ./function_extractor.py::165: Hardcoded file path: return '\n'.join(lines)
  - Suggestion: Move path to configuration file or environment variable

Refactoring steps:

1. Use configuration management
```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


Validation tests:

```python
import pytest
from pathlib import Path

def test_config_paths():
    assert isinstance(Config.BASE_DIR, Path)
    assert Config.DATA_DIR.parent == Config.BASE_DIR
    assert Config.CACHE_DIR.parent == Config.BASE_DIR
    assert Config.LOG_DIR.parent == Config.BASE_DIR

def test_setup_logging(tmp_path):
    with patch('config.Config.LOG_DIR', tmp_path):
        setup_logging()
        assert (tmp_path / 'app.log').exists()
```

- ./function_extractor.py::179: Hardcoded file path: file_context = file_path.replace('/', '.').replace('\\', '.')
  - Suggestion: Move path to configuration file or environment variable

Refactoring steps:

1. Use configuration management
```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


Validation tests:

```python
import pytest
from pathlib import Path

def test_config_paths():
    assert isinstance(Config.BASE_DIR, Path)
    assert Config.DATA_DIR.parent == Config.BASE_DIR
    assert Config.CACHE_DIR.parent == Config.BASE_DIR
    assert Config.LOG_DIR.parent == Config.BASE_DIR

def test_setup_logging(tmp_path):
    with patch('config.Config.LOG_DIR', tmp_path):
        setup_logging()
        assert (tmp_path / 'app.log').exists()
```

- ./function_extractor.py::213: Hardcoded file path: content.append("\n---\n\n")
  - Suggestion: Move path to configuration file or environment variable

Refactoring steps:

1. Use configuration management
```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


Validation tests:

```python
import pytest
from pathlib import Path

def test_config_paths():
    assert isinstance(Config.BASE_DIR, Path)
    assert Config.DATA_DIR.parent == Config.BASE_DIR
    assert Config.CACHE_DIR.parent == Config.BASE_DIR
    assert Config.LOG_DIR.parent == Config.BASE_DIR

def test_setup_logging(tmp_path):
    with patch('config.Config.LOG_DIR', tmp_path):
        setup_logging()
        assert (tmp_path / 'app.log').exists()
```

- ./function_extractor.py::224: Hardcoded file path: content.append("\n")
  - Suggestion: Move path to configuration file or environment variable

Refactoring steps:

1. Use configuration management
```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


Validation tests:

```python
import pytest
from pathlib import Path

def test_config_paths():
    assert isinstance(Config.BASE_DIR, Path)
    assert Config.DATA_DIR.parent == Config.BASE_DIR
    assert Config.CACHE_DIR.parent == Config.BASE_DIR
    assert Config.LOG_DIR.parent == Config.BASE_DIR

def test_setup_logging(tmp_path):
    with patch('config.Config.LOG_DIR', tmp_path):
        setup_logging()
        assert (tmp_path / 'app.log').exists()
```

- ./function_extractor.py::229: Hardcoded file path: content.append("\n")
  - Suggestion: Move path to configuration file or environment variable

Refactoring steps:

1. Use configuration management
```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


Validation tests:

```python
import pytest
from pathlib import Path

def test_config_paths():
    assert isinstance(Config.BASE_DIR, Path)
    assert Config.DATA_DIR.parent == Config.BASE_DIR
    assert Config.CACHE_DIR.parent == Config.BASE_DIR
    assert Config.LOG_DIR.parent == Config.BASE_DIR

def test_setup_logging(tmp_path):
    with patch('config.Config.LOG_DIR', tmp_path):
        setup_logging()
        assert (tmp_path / 'app.log').exists()
```

- ./function_extractor.py::261: Hardcoded file path: content.append("\n---\n\n")
  - Suggestion: Move path to configuration file or environment variable

Refactoring steps:

1. Use configuration management
```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


Validation tests:

```python
import pytest
from pathlib import Path

def test_config_paths():
    assert isinstance(Config.BASE_DIR, Path)
    assert Config.DATA_DIR.parent == Config.BASE_DIR
    assert Config.CACHE_DIR.parent == Config.BASE_DIR
    assert Config.LOG_DIR.parent == Config.BASE_DIR

def test_setup_logging(tmp_path):
    with patch('config.Config.LOG_DIR', tmp_path):
        setup_logging()
        assert (tmp_path / 'app.log').exists()
```


### Complex Condition

- ./function_extractor.py::220: Complex conditional logic that's hard to understand
  - Suggestion: Extract conditions into well-named methods or use pattern matching

Refactoring steps:

1. Extract complex conditions into methods
```python
# Before
if user.is_active and user.has_permission('admin') and not user.is_blocked:
    # ... handle admin access ...

# After
def is_valid_admin(self, user: User) -> bool:
    return (
        user.is_active
        and user.has_permission('admin')
        and not user.is_blocked
    )

if self.is_valid_admin(user):
    # ... handle admin access ...
```

2. Use pattern matching (Python 3.10+)
```python
# Before
if isinstance(obj, dict) and 'type' in obj and obj['type'] == 'user':
    # ... handle user dict ...

# After
match obj:
    case {'type': 'user', **data}:
        # ... handle user dict ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class User:
    is_active: bool
    is_blocked: bool
    permissions: list[str]

    def has_permission(self, perm: str) -> bool:
        return perm in self.permissions

def test_is_valid_admin():
    # Test valid admin
    user = User(is_active=True, is_blocked=False, permissions=['admin'])
    assert is_valid_admin(user)

    # Test inactive user
    user = User(is_active=False, is_blocked=False, permissions=['admin'])
    assert not is_valid_admin(user)

    # Test blocked user
    user = User(is_active=True, is_blocked=True, permissions=['admin'])
    assert not is_valid_admin(user)

    # Test no admin permission
    user = User(is_active=True, is_blocked=False, permissions=[])
    assert not is_valid_admin(user)
```


### Nested Control

- ./function_extractor.py::52: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::62: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::71: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::116: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::148: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::156: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::178: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::187: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::197: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::205: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::211: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::232: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::235: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::243: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::253: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::259: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```

- ./function_extractor.py::282: Deeply nested control structure
  - Suggestion: Extract nested logic into separate methods or use early returns

Refactoring steps:

1. Use guard clauses
```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


Validation tests:

```python
import pytest
from dataclasses import dataclass

@dataclass
class Order:
    is_valid: bool
    has_items: bool
    can_be_fulfilled: bool

def test_process_order():
    # Test valid order
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=True)
    process_order(order)  # Should not raise

    # Test invalid order
    order = Order(is_valid=False, has_items=True, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="Invalid order"):
        process_order(order)

    # Test no items
    order = Order(is_valid=True, has_items=False, can_be_fulfilled=True)
    with pytest.raises(OrderError, match="No items in order"):
        process_order(order)

    # Test cannot fulfill
    order = Order(is_valid=True, has_items=True, can_be_fulfilled=False)
    with pytest.raises(OrderError, match="Cannot fulfill order"):
        process_order(order)
```


### Data Class

- ./function_extractor.py::FunctionInfo: Class appears to be a data holder with only getters/setters
  - Suggestion: Add behavior or convert to @dataclass with validation

Refactoring steps:

1. Convert to @dataclass with validation
```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        if not self.id:
            raise ValueError("id is required")
        if not self.name:
            raise ValueError("name is required")
```

2. Add domain-specific behavior
```python
@dataclass
class User:
    # ... existing fields ...

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        self.validate()

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            name=self.name,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat() if self.updated_at else None
        )
```


Validation tests:

```python
import pytest
from datetime import datetime

def test_FunctionInfo_validation():
    # Test valid creation
    user = User(id='123', name='Test User')
    assert user.id == '123'
    assert user.name == 'Test User'

    # Test invalid creation
    with pytest.raises(ValueError, match="id is required"):
        User(id='', name='Test User')

    with pytest.raises(ValueError, match="name is required"):
        User(id='123', name='')

def test_FunctionInfo_update():
    user = User(id='123', name='Test User')
    old_updated_at = user.updated_at

    user.update(name='New Name')
    assert user.name == 'New Name'
    assert user.updated_at > old_updated_at
```


### Long Method

- ./function_extractor.py::extract_imports: Method is too complex (lines: 12, complexity: 8, cognitive: 19)
  - Suggestion: Extract complex logic into smaller, focused methods

Refactoring steps:

1. Extract validation logic
```python
def validate_input(self, data: Dict[str, Any]) -> None:
    if not data:
        raise ValueError("Invalid data")
    required_fields = ['field1', 'field2']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
```

2. Extract transformation logic
```python
def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'transformed_field1': self._transform_field1(data['field1']),
        'transformed_field2': self._transform_field2(data['field2'])
    }
```


Validation tests:

```python
import pytest
from typing import Dict, Any

def test_extract_imports_validation():
    # Test input validation
    with pytest.raises(ValueError, match="Invalid data"):
        validate_input({})

    with pytest.raises(ValueError, match="Missing required field"):
        validate_input({'field1': 'value1'})

    # Test valid input
    data = {'field1': 'value1', 'field2': 'value2'}
    validate_input(data)  # Should not raise

def test_extract_imports_transformation():
    data = {'field1': 'raw1', 'field2': 'raw2'}
    result = transform_data(data)

    assert 'transformed_field1' in result
    assert 'transformed_field2' in result
```

- ./function_extractor.py::extract_functions: Method is too complex (lines: 37, complexity: 18, cognitive: 64)
  - Suggestion: Extract complex logic into smaller, focused methods

Refactoring steps:

1. Extract validation logic
```python
def validate_input(self, data: Dict[str, Any]) -> None:
    if not data:
        raise ValueError("Invalid data")
    required_fields = ['field1', 'field2']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
```

2. Extract transformation logic
```python
def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'transformed_field1': self._transform_field1(data['field1']),
        'transformed_field2': self._transform_field2(data['field2'])
    }
```


Validation tests:

```python
import pytest
from typing import Dict, Any

def test_extract_functions_validation():
    # Test input validation
    with pytest.raises(ValueError, match="Invalid data"):
        validate_input({})

    with pytest.raises(ValueError, match="Missing required field"):
        validate_input({'field1': 'value1'})

    # Test valid input
    data = {'field1': 'value1', 'field2': 'value2'}
    validate_input(data)  # Should not raise

def test_extract_functions_transformation():
    data = {'field1': 'raw1', 'field2': 'raw2'}
    result = transform_data(data)

    assert 'transformed_field1' in result
    assert 'transformed_field2' in result
```

- ./function_extractor.py::process_directories: Method is too complex (lines: 106, complexity: 47, cognitive: 183)
  - Suggestion: Extract complex logic into smaller, focused methods

Refactoring steps:

1. Extract validation logic
```python
def validate_input(self, data: Dict[str, Any]) -> None:
    if not data:
        raise ValueError("Invalid data")
    required_fields = ['field1', 'field2']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
```

2. Extract transformation logic
```python
def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'transformed_field1': self._transform_field1(data['field1']),
        'transformed_field2': self._transform_field2(data['field2'])
    }
```


Validation tests:

```python
import pytest
from typing import Dict, Any

def test_process_directories_validation():
    # Test input validation
    with pytest.raises(ValueError, match="Invalid data"):
        validate_input({})

    with pytest.raises(ValueError, match="Missing required field"):
        validate_input({'field1': 'value1'})

    # Test valid input
    data = {'field1': 'value1', 'field2': 'value2'}
    validate_input(data)  # Should not raise

def test_process_directories_transformation():
    data = {'field1': 'raw1', 'field2': 'raw2'}
    result = transform_data(data)

    assert 'transformed_field1' in result
    assert 'transformed_field2' in result
```


### Switch Statements

- ./function_extractor.py::anonymous: Complex conditional logic with 9 conditions
  - Suggestion: Replace with polymorphism or strategy pattern

Refactoring steps:

1. Replace with polymorphism
```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


Validation tests:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_payment_processing():
    # Test credit card payment
    await process_payment('credit_card', 100.0)

    # Test PayPal payment
    await process_payment('paypal', 100.0)

    # Test invalid payment method
    with pytest.raises(KeyError):
        await process_payment('invalid_method', 100.0)

@pytest.mark.asyncio
async def test_payment_method_polymorphism():
    # Test each payment method implements the interface
    for method in payment_methods.values():
        assert hasattr(method, 'process_payment')
        assert asyncio.iscoroutinefunction(method.process_payment)
```

- ./function_extractor.py::anonymous: Complex conditional logic with 9 conditions
  - Suggestion: Replace with polymorphism or strategy pattern

Refactoring steps:

1. Replace with polymorphism
```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


Validation tests:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_payment_processing():
    # Test credit card payment
    await process_payment('credit_card', 100.0)

    # Test PayPal payment
    await process_payment('paypal', 100.0)

    # Test invalid payment method
    with pytest.raises(KeyError):
        await process_payment('invalid_method', 100.0)

@pytest.mark.asyncio
async def test_payment_method_polymorphism():
    # Test each payment method implements the interface
    for method in payment_methods.values():
        assert hasattr(method, 'process_payment')
        assert asyncio.iscoroutinefunction(method.process_payment)
```

- ./function_extractor.py::anonymous: Complex conditional logic with 10 conditions
  - Suggestion: Replace with polymorphism or strategy pattern

Refactoring steps:

1. Replace with polymorphism
```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


Validation tests:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_payment_processing():
    # Test credit card payment
    await process_payment('credit_card', 100.0)

    # Test PayPal payment
    await process_payment('paypal', 100.0)

    # Test invalid payment method
    with pytest.raises(KeyError):
        await process_payment('invalid_method', 100.0)

@pytest.mark.asyncio
async def test_payment_method_polymorphism():
    # Test each payment method implements the interface
    for method in payment_methods.values():
        assert hasattr(method, 'process_payment')
        assert asyncio.iscoroutinefunction(method.process_payment)
```

- ./function_extractor.py::anonymous: Complex conditional logic with 8 conditions
  - Suggestion: Replace with polymorphism or strategy pattern

Refactoring steps:

1. Replace with polymorphism
```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


Validation tests:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_payment_processing():
    # Test credit card payment
    await process_payment('credit_card', 100.0)

    # Test PayPal payment
    await process_payment('paypal', 100.0)

    # Test invalid payment method
    with pytest.raises(KeyError):
        await process_payment('invalid_method', 100.0)

@pytest.mark.asyncio
async def test_payment_method_polymorphism():
    # Test each payment method implements the interface
    for method in payment_methods.values():
        assert hasattr(method, 'process_payment')
        assert asyncio.iscoroutinefunction(method.process_payment)
```

- ./function_extractor.py::anonymous: Complex conditional logic with 7 conditions
  - Suggestion: Replace with polymorphism or strategy pattern

Refactoring steps:

1. Replace with polymorphism
```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


Validation tests:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_payment_processing():
    # Test credit card payment
    await process_payment('credit_card', 100.0)

    # Test PayPal payment
    await process_payment('paypal', 100.0)

    # Test invalid payment method
    with pytest.raises(KeyError):
        await process_payment('invalid_method', 100.0)

@pytest.mark.asyncio
async def test_payment_method_polymorphism():
    # Test each payment method implements the interface
    for method in payment_methods.values():
        assert hasattr(method, 'process_payment')
        assert asyncio.iscoroutinefunction(method.process_payment)
```


## Code Metrics


### ./static_analysis.py

- Cyclomatic Complexity: 363
- Cognitive Complexity: 863
- Maintainability Index: 0.0
- Line Count: 2539
- Max Line Length: 179
- Average Line Length: 39.76
- Type Hint Coverage: 71.8%
- Dependency Count: 8

### ./function_extractor.py

- Cyclomatic Complexity: 83
- Cognitive Complexity: 278
- Maintainability Index: 7.2
- Line Count: 296
- Max Line Length: 150
- Average Line Length: 42.64
- Type Hint Coverage: 95.7%
- Dependency Count: 5

Security Issues:
- Potential hardcoded secret in variable: key

## Import Analysis


### ./static_analysis.py

- from dataclasses (dataclass, field)
- from typing (List, Optional, Dict, Set, Any)
- from collections (defaultdict, Counter)
- import ast
- import os
- from pathlib (Path)
- import re
- import math

### ./function_extractor.py

- import os
- import ast
- import sys
- from typing (List, NamedTuple, Optional, Set)
- import re

### Third-Party Dependencies


## Type Hint Coverage


Overall Type Hint Coverage: 83.7%

- ./static_analysis.py: 71.8%
- ./function_extractor.py: 95.7%

## Refactoring Suggestions


### complex_condition in ./function_extractor.py::220

> Complex conditional logic that's hard to understand

Steps to refactor:


1. Extract complex conditions into methods

```python
# Before
if user.is_active and user.has_permission('admin') and not user.is_blocked:
    # ... handle admin access ...

# After
def is_valid_admin(self, user: User) -> bool:
    return (
        user.is_active
        and user.has_permission('admin')
        and not user.is_blocked
    )

if self.is_valid_admin(user):
    # ... handle admin access ...
```


2. Use pattern matching (Python 3.10+)

```python
# Before
if isinstance(obj, dict) and 'type' in obj and obj['type'] == 'user':
    # ... handle user dict ...

# After
match obj:
    case {'type': 'user', **data}:
        # ... handle user dict ...
```


### hardcoded_path in ./function_extractor.py::153

> Hardcoded file path: lines = [line.rstrip() for line in docstring.split('\n')]

Steps to refactor:


1. Use configuration management

```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


### hardcoded_path in ./function_extractor.py::165

> Hardcoded file path: return '\n'.join(lines)

Steps to refactor:


1. Use configuration management

```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


### hardcoded_path in ./function_extractor.py::179

> Hardcoded file path: file_context = file_path.replace('/', '.').replace('\\', '.')

Steps to refactor:


1. Use configuration management

```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


### hardcoded_path in ./function_extractor.py::213

> Hardcoded file path: content.append("\n---\n\n")

Steps to refactor:


1. Use configuration management

```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


### hardcoded_path in ./function_extractor.py::224

> Hardcoded file path: content.append("\n")

Steps to refactor:


1. Use configuration management

```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


### hardcoded_path in ./function_extractor.py::229

> Hardcoded file path: content.append("\n")

Steps to refactor:


1. Use configuration management

```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


### hardcoded_path in ./function_extractor.py::261

> Hardcoded file path: content.append("\n---\n\n")

Steps to refactor:


1. Use configuration management

```python
from pathlib import Path
from typing import Final

# config.py
class Config:
    BASE_DIR: Final = Path(__file__).parent
    DATA_DIR: Final = BASE_DIR / 'data'
    CACHE_DIR: Final = BASE_DIR / 'cache'
    LOG_DIR: Final = BASE_DIR / 'logs'

# Usage
def setup_logging() -> None:
    log_file = Config.LOG_DIR / 'app.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # ... setup logging ...
```


### nested_control in ./function_extractor.py::52

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::62

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::71

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::116

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::148

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::156

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::178

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::187

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::197

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::205

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::211

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::232

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::235

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::243

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::253

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::259

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### nested_control in ./function_extractor.py::282

> Deeply nested control structure

Steps to refactor:


1. Use guard clauses

```python
# Before
def process_order(self, order: Order) -> None:
    if order.is_valid:
        if order.has_items:
            if order.can_be_fulfilled:
                # ... process order ...
            else:
                raise OrderError("Cannot fulfill order")
        else:
            raise OrderError("No items in order")
    else:
        raise OrderError("Invalid order")

# After
def process_order(self, order: Order) -> None:
    if not order.is_valid:
        raise OrderError("Invalid order")
    if not order.has_items:
        raise OrderError("No items in order")
    if not order.can_be_fulfilled:
        raise OrderError("Cannot fulfill order")
    # ... process order ...
```


### data_class in ./function_extractor.py::FunctionInfo

> Class appears to be a data holder with only getters/setters

Steps to refactor:


1. Convert to @dataclass with validation

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        if not self.id:
            raise ValueError("id is required")
        if not self.name:
            raise ValueError("name is required")
```


2. Add domain-specific behavior

```python
@dataclass
class User:
    # ... existing fields ...

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        self.validate()

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            name=self.name,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat() if self.updated_at else None
        )
```


### long_method in ./function_extractor.py::extract_imports

> Method is too complex (lines: 12, complexity: 8, cognitive: 19)

Steps to refactor:


1. Extract validation logic

```python
def validate_input(self, data: Dict[str, Any]) -> None:
    if not data:
        raise ValueError("Invalid data")
    required_fields = ['field1', 'field2']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
```


2. Extract transformation logic

```python
def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'transformed_field1': self._transform_field1(data['field1']),
        'transformed_field2': self._transform_field2(data['field2'])
    }
```


### long_method in ./function_extractor.py::extract_functions

> Method is too complex (lines: 37, complexity: 18, cognitive: 64)

Steps to refactor:


1. Extract validation logic

```python
def validate_input(self, data: Dict[str, Any]) -> None:
    if not data:
        raise ValueError("Invalid data")
    required_fields = ['field1', 'field2']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
```


2. Extract transformation logic

```python
def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'transformed_field1': self._transform_field1(data['field1']),
        'transformed_field2': self._transform_field2(data['field2'])
    }
```


### long_method in ./function_extractor.py::process_directories

> Method is too complex (lines: 106, complexity: 47, cognitive: 183)

Steps to refactor:


1. Extract validation logic

```python
def validate_input(self, data: Dict[str, Any]) -> None:
    if not data:
        raise ValueError("Invalid data")
    required_fields = ['field1', 'field2']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
```


2. Extract transformation logic

```python
def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'transformed_field1': self._transform_field1(data['field1']),
        'transformed_field2': self._transform_field2(data['field2'])
    }
```


### switch_statements in ./function_extractor.py::anonymous

> Complex conditional logic with 9 conditions

Steps to refactor:


1. Replace with polymorphism

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


### switch_statements in ./function_extractor.py::anonymous

> Complex conditional logic with 9 conditions

Steps to refactor:


1. Replace with polymorphism

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


### switch_statements in ./function_extractor.py::anonymous

> Complex conditional logic with 10 conditions

Steps to refactor:


1. Replace with polymorphism

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


### switch_statements in ./function_extractor.py::anonymous

> Complex conditional logic with 8 conditions

Steps to refactor:


1. Replace with polymorphism

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


### switch_statements in ./function_extractor.py::anonymous

> Complex conditional logic with 7 conditions

Steps to refactor:


1. Replace with polymorphism

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    async def process_payment(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process credit card payment ...

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> None:
        # ... process PayPal payment ...

# Usage
payment_methods = {
    'credit_card': CreditCardPayment(),
    'paypal': PayPalPayment()
}

async def process_payment(method: str, amount: float) -> None:
    await payment_methods[method].process_payment(amount)
```


## Package Analysis


### Interface Analysis


Abstraction Score: 0.00
