# Authentication API Documentation

## Overview

The Todo Application provides a comprehensive authentication system with user registration, login, password management, and email verification. All authentication endpoints use JWT (JSON Web Tokens) for secure session management.

## Base URL

```
Production: https://api.todoapp.com/api/v1/auth
Development: http://localhost:8000/api/v1/auth
```

## Authentication

Most endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. User Registration

**Endpoint:** `POST /register`

**Description:** Register a new user account. Sends a verification email upon successful registration.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
- Not a common password

**Name Requirements:**
- 2-100 characters
- Letters, spaces, hyphens, and apostrophes only
- No numbers or special characters (except - and ')

**Success Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "email_verified": false,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**

- **400 Bad Request:** Email already registered, weak password, or invalid name
```json
{
  "detail": "Email already registered"
}
```

- **422 Unprocessable Entity:** Invalid email format or missing required fields
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

### 2. User Login

**Endpoint:** `POST /login`

**Description:** Authenticate a user and receive an access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": true
  }
}
```

**Error Responses:**

- **401 Unauthorized:** Invalid credentials
```json
{
  "detail": "Invalid email or password"
}
```

- **403 Forbidden:** Account locked due to failed login attempts
```json
{
  "detail": "Account temporarily locked due to multiple failed login attempts. Please try again in 15 minutes."
}
```

- **429 Too Many Requests:** Rate limit exceeded
```json
{
  "detail": "Too many login attempts. Please try again later."
}
```

---

### 3. Get Current User

**Endpoint:** `GET /me`

**Description:** Retrieve the authenticated user's profile information.

**Authentication:** Required

**Success Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "email_verified": true,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "last_login_at": "2024-01-20T14:25:00Z"
}
```

**Error Responses:**

- **401 Unauthorized:** Missing or invalid token
```json
{
  "detail": "Not authenticated"
}
```

---

### 4. Logout

**Endpoint:** `POST /logout`

**Description:** Logout the current user (stateless JWT approach - client should discard token).

**Authentication:** Required

**Success Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

---

### 5. Forgot Password

**Endpoint:** `POST /forgot-password`

**Description:** Request a password reset email. Returns success even for non-existent emails to prevent email enumeration.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "message": "If an account exists with this email, a password reset link has been sent."
}
```

**Rate Limiting:** 5 requests per 15 minutes per IP address

---

### 6. Reset Password

**Endpoint:** `POST /reset-password`

**Description:** Reset password using a valid reset token.

**Request Body:**
```json
{
  "token": "abc123def456...",
  "new_password": "NewSecurePassword123!"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

**Error Responses:**

- **400 Bad Request:** Invalid, expired, or already used token
```json
{
  "detail": "Invalid or expired reset token"
}
```

- **400 Bad Request:** Weak password
```json
{
  "detail": "Password must contain at least 8 characters, including uppercase, lowercase, digit, and special character"
}
```

**Token Expiration:** 1 hour

---

### 7. Change Password

**Endpoint:** `POST /change-password`

**Description:** Change password for authenticated user.

**Authentication:** Required (verified email)

**Request Body:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword123!"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**

- **400 Bad Request:** Incorrect current password
```json
{
  "detail": "Current password is incorrect"
}
```

- **403 Forbidden:** Email not verified
```json
{
  "detail": "Email verification required for this operation"
}
```

---

### 8. Verify Email

**Endpoint:** `POST /verify-email`

**Description:** Verify user's email address using verification token.

**Request Body:**
```json
{
  "token": "xyz789abc123..."
}
```

**Success Response (200 OK):**
```json
{
  "message": "Email verified successfully"
}
```

**Error Responses:**

- **400 Bad Request:** Invalid or expired token
```json
{
  "detail": "Invalid or expired verification token"
}
```

**Token Expiration:** 24 hours

---

### 9. Resend Verification Email

**Endpoint:** `POST /resend-verification`

**Description:** Resend email verification link to authenticated user.

**Authentication:** Required

**Success Response (200 OK):**
```json
{
  "message": "Verification email sent successfully"
}
```

**Error Responses:**

- **400 Bad Request:** Email already verified
```json
{
  "detail": "Email is already verified"
}
```

**Rate Limiting:** 3 requests per hour per user

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (422):
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

## HTTP Status Codes

- **200 OK:** Request succeeded
- **201 Created:** Resource created successfully
- **400 Bad Request:** Invalid request data or business logic error
- **401 Unauthorized:** Authentication required or invalid credentials
- **403 Forbidden:** Authenticated but not authorized (e.g., account locked, email not verified)
- **404 Not Found:** Resource not found
- **422 Unprocessable Entity:** Validation error
- **429 Too Many Requests:** Rate limit exceeded
- **500 Internal Server Error:** Server error

## Rate Limiting

Rate limits are applied per IP address or per user (when authenticated):

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /register | 5 requests | 1 hour |
| POST /login | 5 failed attempts | 15 minutes |
| POST /forgot-password | 5 requests | 15 minutes |
| POST /resend-verification | 3 requests | 1 hour |

When rate limit is exceeded, the API returns 429 status with:
```json
{
  "detail": "Too many requests. Please try again later."
}
```

## Security Headers

All responses include security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

## JWT Token Details

**Token Expiration:** 7 days

**Token Payload:**
```json
{
  "sub": "user_id",
  "exp": 1234567890
}
```

**Token Usage:**
Include in Authorization header for all protected endpoints:
```
Authorization: Bearer <access_token>
```

## Email Templates

The system sends the following automated emails:

1. **Welcome Email:** Sent upon registration with verification link
2. **Email Verification:** Contains verification link (expires in 24 hours)
3. **Password Reset:** Contains reset link (expires in 1 hour)
4. **Password Changed:** Confirmation email after successful password change

## Best Practices

1. **Store tokens securely:** Use httpOnly cookies or secure storage
2. **Handle token expiration:** Implement token refresh logic
3. **Validate on client side:** Check password strength before submission
4. **Handle errors gracefully:** Display user-friendly error messages
5. **Implement CSRF protection:** For web applications
6. **Use HTTPS:** Always use HTTPS in production
7. **Log security events:** Monitor failed login attempts and suspicious activity

## Example Usage

### Registration Flow

```javascript
// 1. Register user
const response = await fetch('https://api.todoapp.com/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePassword123!',
    first_name: 'John',
    last_name: 'Doe'
  })
});

const user = await response.json();

// 2. User receives verification email and clicks link
// 3. Verify email with token from email
await fetch('https://api.todoapp.com/api/v1/auth/verify-email', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token: 'verification_token_from_email' })
});
```

### Login Flow

```javascript
// 1. Login
const response = await fetch('https://api.todoapp.com/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePassword123!'
  })
});

const { access_token } = await response.json();

// 2. Store token securely
localStorage.setItem('access_token', access_token);

// 3. Use token for authenticated requests
const userResponse = await fetch('https://api.todoapp.com/api/v1/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

### Password Reset Flow

```javascript
// 1. Request password reset
await fetch('https://api.todoapp.com/api/v1/auth/forgot-password', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com' })
});

// 2. User receives email with reset link
// 3. Reset password with token from email
await fetch('https://api.todoapp.com/api/v1/auth/reset-password', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    token: 'reset_token_from_email',
    new_password: 'NewSecurePassword123!'
  })
});
```

## Support

For API support or to report security issues:
- Email: security@todoapp.com
- Documentation: https://docs.todoapp.com
- Status Page: https://status.todoapp.com
