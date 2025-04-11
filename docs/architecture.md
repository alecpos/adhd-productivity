# ADHD Calendar Backend Architecture

## Directory Structure

```
app/
├── api/                    # API Layer
│   └── v1/                # API Version 1
│       └── routes/        # Route handlers and endpoints
├── core/                  # Core Framework Components
│   ├── config/           # Configuration management
│   ├── database/         # Database setup and connections
│   ├── security/         # Authentication and authorization
│   └── dependencies/     # FastAPI dependencies
├── models/               # Data Models
│   ├── domain/          # Business domain models
│   └── persistence/     # SQLAlchemy database models
├── schemas/             # Pydantic Schemas
│   ├── requests/        # Request validation schemas
│   └── responses/       # Response validation schemas
├── services/           # Business Logic
│   ├── auth/          # Authentication services
│   ├── user/          # User management
│   ├── task/          # Task management
│   ├── analytics/     # Analytics and reporting
│   ├── gamification/  # Gamification features
│   ├── scheduling/    # Calendar and scheduling
│   └── health/        # Health monitoring
├── utils/             # Utilities
│   ├── helpers/       # Helper functions
│   └── constants/     # Constants and enums
└── tests/            # Test Suite
    ├── unit/         # Unit tests
    ├── integration/  # Integration tests
    └── e2e/          # End-to-end tests
```

## Naming Conventions

### Files
- Models: `*_model.py`
- Schemas: `*_schema.py`
- Services: `*_service.py`
- Tests: `test_*.py`
- Routes: `*_routes.py`

### Classes
- Models: `class UserModel(Base):`
- Schemas: `class UserSchema(BaseModel):`
- Services: `class UserService(BaseService):`
- Route Handlers: `class UserRouter(BaseRouter):`

## Import Structure

### Models
```python
# Domain models
from app.models.domain.user import User

# Persistence models
from app.models.persistence.user_model import UserModel
```

### Schemas
```python
# Request schemas
from app.schemas.requests.user_create import UserCreateRequest

# Response schemas
from app.schemas.responses.user import UserResponse
```

### Services
```python
from app.services.user.user_service import UserService
from app.services.auth.auth_service import AuthService
```

### Routes
```python
from app.api.v1.routes.user import UserRouter
from app.api.v1.routes.auth import AuthRouter
```

## Layer Responsibilities

### API Layer (`app/api/`)
- Route definitions
- Request/response handling
- Input validation
- Authentication checks
- Response formatting

### Core Layer (`app/core/`)
- Framework configuration
- Database setup
- Security middleware
- Dependency injection
- Common middleware

### Models Layer (`app/models/`)
- Data structure definitions
- Database models (SQLAlchemy)
- Domain models
- Data validation rules

### Services Layer (`app/services/`)
- Business logic
- Data processing
- External service integration
- Transaction management

### Utils Layer (`app/utils/`)
- Helper functions
- Constants
- Common utilities
- Type definitions

## Testing Strategy

### Unit Tests (`tests/unit/`)
- Test individual components
- Mock external dependencies
- Focus on business logic

### Integration Tests (`tests/integration/`)
- Test component interactions
- Database integration
- API endpoint testing

### E2E Tests (`tests/e2e/`)
- Full system testing
- User flow testing
- External service integration

## Best Practices

1. **Dependency Injection**
   - Use FastAPI's dependency injection
   - Avoid global state
   - Make dependencies explicit

2. **Error Handling**
   - Use custom exceptions
   - Consistent error responses
   - Proper error logging

3. **Documentation**
   - Document all public functions
   - Include type hints
   - Use docstrings

4. **Testing**
   - Write tests for new features
   - Maintain test coverage
   - Use fixtures for common setup

5. **Code Organization**
   - One class per file
   - Group related functionality
   - Keep files focused and small

## Development Workflow

1. **Feature Development**
   - Create feature branch
   - Update tests
   - Implement feature
   - Update documentation

2. **Code Review**
   - Run linter
   - Run tests
   - Check documentation
   - Review changes

3. **Deployment**
   - Run integration tests
   - Update dependencies
   - Deploy to staging
   - Monitor metrics
