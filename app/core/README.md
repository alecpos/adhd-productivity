# Core Directory

This directory contains core configurations and settings for the ADHD Calendar backend.

## Overview

The core directory houses foundational components that are used throughout the application, including configuration management, environment settings, security policies, and application-wide constants.

## Components

- **config.py**: Application configuration including environment-specific settings
- **security.py**: Security-related utilities and configurations
- **constants.py**: Application-wide constants and enumerations
- **logging.py**: Logging configuration and utilities
- **errors.py**: Core error definitions and handling utilities
- **startup.py**: Application startup and initialization logic

## Configuration Management

The configuration system supports multiple environments:
- Development
- Testing
- Staging
- Production

Configuration is loaded from environment variables and/or configuration files based on the active environment.

## Security Features

Security components include:
- Password hashing and verification
- Token generation and validation
- Rate limiting
- CORS configuration
- Content security policies

## Usage Example

```python
from app.core.config import get_settings
from app.core.security import get_password_hash, verify_password

# Get application settings
settings = get_settings()

# Use security utilities
password_hash = get_password_hash("user_password")
is_valid = verify_password("user_password", password_hash)
```

## Development Guidelines

When modifying core components:
1. Ensure backward compatibility when possible
2. Update all affected components when making changes
3. Document any configuration changes
4. Add appropriate test coverage
5. Consider performance implications

## Related Documentation

- [Application Configuration Guide](../../docs/configuration_guide.md)
- [Security Architecture](../../docs/security_architecture.md) 