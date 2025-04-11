# Authentication Flow

This document describes the authentication flow used in the ADHD Calendar application.

## Overview

The ADHD Calendar uses JWT (JSON Web Token) based authentication to secure API endpoints. The authentication flow includes:

- User registration
- Login and token issuance
- Token validation
- Token refresh
- Password management

## Authentication Process

### 1. User Registration

The registration process creates a new user account in the system.

Request:

```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password123",
    "full_name": "Test User"
}
```

Response:

```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "Test User",
    "created_at": "2023-04-01T12:00:00Z"
}
```

Registration Security Measures:
- Password strength validation
- Email verification
- Rate limiting to prevent brute force attempts
- CAPTCHA for bot prevention

### 2. Login and Token Issuance

Once registered, users can log in to obtain an access token.

Request:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password123"
}
```

Response:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "user@example.com",
        "full_name": "Test User"
    }
}
```

Token Details:
- Access tokens are valid for 1 hour (3600 seconds)
- Refresh tokens are valid for 7 days
- Tokens are signed with a secret key using HMAC SHA-256

### 3. Authenticating Requests

Once an access token is obtained, it should be included in the `Authorization` header of subsequent requests.

```http
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Token Refresh

When an access token expires, the refresh token can be used to obtain a new access token without requiring the user to log in again.

Request:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", // New access token
    "token_type": "bearer",
    "expires_in": 3600
}
```

Security measures:
- Refresh tokens are single-use
- When a refresh token is used, a new refresh token is issued
- Refresh tokens can be revoked by the server

### 5. Password Management

#### Change Password

Users can change their password if they know their current password.

Request:

```http
POST /api/v1/auth/change-password
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
    "current_password": "secure_password123",
    "new_password": "even_more_secure_password456"
}
```

Response:

```json
{
    "message": "Password successfully changed"
}
```

#### Forgot Password

If a user forgets their password, they can request a password reset link.

Request:

```http
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
    "email": "user@example.com"
}
```

Response:

```json
{
    "message": "If your email is registered, you will receive a password reset link"
}
```

#### Reset Password

After receiving the password reset link, users can set a new password.

Request:

```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
    "token": "reset_token_from_email",
    "new_password": "new_secure_password789"
}
```

Response:

```json
{
    "message": "Password successfully reset"
}
```

### 6. Logout

To securely log out, the client should invalidate the refresh token.

Request:

```http
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
{
    "message": "Successfully logged out"
}
```

## JWT Token Structure

### Access Token Payload

```json
{
    "sub": "123e4567-e89b-12d3-a456-426614174000", // User ID
    "email": "user@example.com",
    "name": "Test User",
    "role": "user",
    "permissions": ["read:own", "write:own"],
    "iat": 1680350400, // Issued at timestamp
    "exp": 1680354000, // Expiration timestamp
    "iss": "adhd-calendar-api" // Issuer
}
```

### Refresh Token Payload

```json
{
    "sub": "123e4567-e89b-12d3-a456-426614174000", // User ID
    "jti": "unique-token-id", // Unique token ID for revocation
    "iat": 1680350400, // Issued at timestamp
    "exp": 1680955200, // Expiration timestamp (7 days)
    "iss": "adhd-calendar-api" // Issuer
}
```

## Token Validation Process

When a request with an access token is received:

1. Extract the token from the `Authorization` header
2. Verify the token signature using the secret key
3. Check if the token has expired
4. Verify the issuer is valid
5. Extract the user ID and permissions from the token
6. Check if the token has been revoked
7. If validation passes, process the request

## Security Considerations

### Token Storage

- Access tokens should be stored in memory (not in local storage or cookies)
- Refresh tokens can be stored in an HTTP-only secure cookie or secure storage
- Mobile apps should use secure storage mechanisms provided by the platform

### Additional Security Measures

- All authentication endpoints use HTTPS
- Tokens have a short lifespan to minimize risk if compromised
- Rate limiting is applied to authentication endpoints
- Suspicious activity triggers additional verification
- Failed login attempts are logged and monitored
- IP-based blocking after multiple failed attempts

### Multi-Factor Authentication (MFA)

MFA is supported for added security:

Request (after successful password validation):

```http
POST /api/v1/auth/mfa/verify
Content-Type: application/json

{
    "mfa_code": "123456" // Code from authenticator app or SMS
}
```

Response:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## OAuth Integration

The system supports OAuth for authentication with third-party providers:

1. Google
2. Apple
3. Microsoft

Request:

```http
GET /api/v1/auth/oauth/google
```

This redirects to the OAuth provider's authentication page. After successful authentication, the user is redirected back to the application with an authorization code, which is then exchanged for tokens.

## Implementing Authentication

### Backend Implementation

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.models.user import User
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(user_id)
    if user is None:
        raise credentials_exception
    return user
```

### Frontend Implementation

```typescript
// auth.service.ts
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

export class AuthService {
  private static instance: AuthService;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiration: Date | null = null;

  private constructor() {
    // Load tokens from secure storage if available
    this.loadTokens();
  }

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  async login(email: string, password: string): Promise<void> {
    try {
      const response = await axios.post('/api/v1/auth/login', {
        email,
        password
      });

      this.setTokens(
        response.data.access_token,
        response.data.refresh_token
      );

      return response.data.user;
    } catch (error) {
      throw new Error('Authentication failed');
    }
  }

  async refreshAccessToken(): Promise<void> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post('/api/v1/auth/refresh', {
        refresh_token: this.refreshToken
      });

      this.setTokens(
        response.data.access_token,
        response.data.refresh_token || this.refreshToken
      );
    } catch (error) {
      this.logout();
      throw new Error('Token refresh failed');
    }
  }

  getAuthHeader(): { Authorization: string } | undefined {
    if (!this.accessToken) {
      return undefined;
    }

    // Check if token is about to expire and refresh if needed
    if (this.tokenExpiration && this.tokenExpiration.getTime() - Date.now() < 60000) {
      this.refreshAccessToken();
    }

    return {
      Authorization: `Bearer ${this.accessToken}`
    };
  }

  isAuthenticated(): boolean {
    return !!this.accessToken && !!this.tokenExpiration && this.tokenExpiration > new Date();
  }

  logout(): void {
    // Call logout API to invalidate refresh token
    if (this.accessToken) {
      axios.post('/api/v1/auth/logout', {}, {
        headers: this.getAuthHeader()
      }).catch(() => {
        // Ignore errors during logout
      });
    }

    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiration = null;
    // Clear tokens from secure storage
    this.clearTokens();
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;

    // Decode the token to get expiration
    const decoded = jwtDecode(accessToken);
    if (decoded.exp) {
      this.tokenExpiration = new Date(decoded.exp * 1000);
    }

    // Save tokens to secure storage
    this.saveTokens();
  }

  // Methods for secure storage of tokens
  private saveTokens(): void {
    // Implementation depends on platform (browser, React Native, etc.)
  }

  private loadTokens(): void {
    // Implementation depends on platform
  }

  private clearTokens(): void {
    // Implementation depends on platform
  }
}
```

## Related Resources

- [API Documentation](./api_documentation.md)
- [Error Handling Guide](./error_handling_guide.md)
- [Security Best Practices](./security_best_practices.md)
