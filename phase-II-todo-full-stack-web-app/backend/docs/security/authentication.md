# Authentication Security Best Practices

## Overview

This document outlines security best practices, policies, and implementation details for the Todo Application authentication system.

## Password Security

### Password Requirements

**Minimum Requirements:**
- Minimum length: 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

**Prohibited Passwords:**
- Common passwords (Password123, Welcome123, Admin123, etc.)
- Dictionary words
- Sequential characters (12345, abcde)
- Repeated characters (aaaa, 1111)

### Password Storage

**Hashing Algorithm:** bcrypt with cost factor 12

**Implementation:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = pwd_context.hash(plain_password)
```

**Security Properties:**
- Salt automatically generated per password
- Computationally expensive to prevent brute force
- Resistant to rainbow table attacks
- Industry-standard algorithm

**Never:**
- Store passwords in plain text
- Log passwords or password hashes
- Transmit passwords without HTTPS
- Use weak hashing algorithms (MD5, SHA1)

## Token Security

### JWT Token Configuration

**Token Type:** JSON Web Token (JWT)

**Algorithm:** HS256 (HMAC with SHA-256)

**Token Expiration:**
- Access tokens: 7 days
- Password reset tokens: 1 hour
- Email verification tokens: 24 hours

**Secret Key Requirements:**
- Minimum 32 characters
- Cryptographically random
- Stored in environment variables
- Never committed to version control
- Rotated periodically (every 90 days)

**Token Payload:**
```json
{
  "sub": "user_id",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Security Measures:**
- Tokens signed with secret key
- Expiration time enforced
- Signature verification on every request
- No sensitive data in payload

### Token Storage (Client-Side)

**Recommended Approaches:**

1. **HttpOnly Cookies (Most Secure):**
   - Not accessible via JavaScript
   - Automatic CSRF protection needed
   - Secure flag in production
   - SameSite attribute set

2. **Secure Storage APIs:**
   - Use browser's secure storage
   - Encrypt before storing
   - Clear on logout

**Avoid:**
- localStorage (vulnerable to XSS)
- sessionStorage (vulnerable to XSS)
- Cookies without HttpOnly flag

## Rate Limiting

### Implementation

**Rate Limit Configuration:**

| Endpoint | Limit | Window | Scope |
|----------|-------|--------|-------|
| POST /register | 5 requests | 1 hour | IP address |
| POST /login | 5 failed attempts | 15 minutes | IP + email |
| POST /forgot-password | 5 requests | 15 minutes | IP address |
| POST /resend-verification | 3 requests | 1 hour | User ID |

**Rate Limiting Strategy:**
- Token bucket algorithm
- Redis-backed for distributed systems
- Separate limits for success/failure
- Exponential backoff for repeated violations

**Response Headers:**
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1234567890
```

### Account Lockout

**Lockout Policy:**
- Triggered after 5 failed login attempts
- Lockout duration: 15 minutes
- Automatic unlock after duration
- Manual unlock by administrator

**Lockout Response:**
```json
{
  "detail": "Account temporarily locked due to multiple failed login attempts. Please try again in 15 minutes or reset your password.",
  "locked_until": "2024-01-20T15:30:00Z"
}
```

## Email Security

### Email Enumeration Prevention

**Strategy:** Always return success response for forgot password, regardless of email existence.

**Implementation:**
```python
# Always return 200, even if email doesn't exist
return {"message": "If an account exists with this email, a password reset link has been sent."}
```

**Benefits:**
- Prevents attackers from discovering valid email addresses
- Maintains user privacy
- Reduces reconnaissance attacks

### Email Verification

**Verification Token:**
- Cryptographically random (32 bytes)
- Hashed before storage (SHA-256)
- Single-use only
- Expires after 24 hours

**Verification Flow:**
1. User registers
2. Verification token generated and stored
3. Email sent with verification link
4. User clicks link
5. Token verified and marked as used
6. User's email_verified flag set to true

**Security Measures:**
- Token invalidated after use
- Old tokens cleaned up on new generation
- Rate limiting on resend requests

## Session Management

### Stateless JWT Approach

**Current Implementation:**
- Stateless JWT tokens
- No server-side session storage
- Client responsible for token storage
- Logout handled client-side (token discard)

**Advantages:**
- Scalable (no session storage)
- Simple implementation
- Works across distributed systems

**Limitations:**
- Cannot revoke tokens before expiration
- No centralized session management
- Requires short expiration times

### Future: Stateful Sessions

**For Enhanced Security:**
- Store session tokens in database
- Enable immediate revocation
- Track active sessions per user
- Support "logout all devices"

## Input Validation

### Email Validation

**Rules:**
- Valid email format (RFC 5322)
- Maximum length: 255 characters
- Normalized to lowercase
- Trimmed whitespace

**Implementation:**
```python
from pydantic import EmailStr

class UserCreate(BaseModel):
    email: EmailStr
```

### Name Validation

**Rules:**
- 2-100 characters
- Letters, spaces, hyphens, apostrophes only
- No numbers or special characters
- Trimmed and normalized whitespace

**Security Considerations:**
- Prevents XSS via name fields
- Blocks SQL injection attempts
- Maintains data integrity

## HTTPS/TLS

### Requirements

**Production Environment:**
- TLS 1.2 or higher required
- Strong cipher suites only
- Valid SSL certificate
- HSTS header enabled

**HSTS Header:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Certificate Management:**
- Use Let's Encrypt or commercial CA
- Automatic renewal
- Monitor expiration dates
- Use certificate pinning for mobile apps

## Security Headers

### Required Headers

**X-Content-Type-Options:**
```
X-Content-Type-Options: nosniff
```
Prevents MIME type sniffing attacks.

**X-Frame-Options:**
```
X-Frame-Options: DENY
```
Prevents clickjacking attacks.

**X-XSS-Protection:**
```
X-XSS-Protection: 1; mode=block
```
Enables browser XSS protection.

**Content-Security-Policy:**
```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
```
Prevents XSS and data injection attacks.

**Referrer-Policy:**
```
Referrer-Policy: strict-origin-when-cross-origin
```
Controls referrer information.

## CORS Configuration

### Production Settings

**Allowed Origins:**
```python
allow_origins=[
    "https://todoapp.com",
    "https://www.todoapp.com"
]
```

**Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://todoapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600
)
```

**Security Considerations:**
- Never use wildcard (*) in production
- Specify exact origins
- Enable credentials only when necessary
- Limit allowed methods and headers

## Audit Logging

### Events to Log

**Authentication Events:**
- Successful login (user_id, IP, timestamp)
- Failed login (email, IP, timestamp)
- Account lockout (user_id, IP, timestamp)
- Password change (user_id, timestamp)
- Password reset request (email, IP, timestamp)
- Password reset completion (user_id, timestamp)
- Email verification (user_id, timestamp)

**Log Format:**
```json
{
  "timestamp": "2024-01-20T14:30:00Z",
  "event": "login_success",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "metadata": {}
}
```

**Security Considerations:**
- Never log passwords or tokens
- Sanitize user input before logging
- Implement log rotation
- Secure log storage
- Monitor for suspicious patterns

## Vulnerability Prevention

### SQL Injection

**Prevention:**
- Use parameterized queries (SQLModel/SQLAlchemy)
- Never concatenate user input into SQL
- Validate and sanitize all inputs

**Example:**
```python
# Safe - parameterized query
statement = select(User).where(User.email == email)

# Unsafe - string concatenation (NEVER DO THIS)
query = f"SELECT * FROM users WHERE email = '{email}'"
```

### Cross-Site Scripting (XSS)

**Prevention:**
- Escape HTML in user-generated content
- Use Content-Security-Policy header
- Validate input on server side
- Sanitize output before rendering

**Implementation:**
```python
import html

def sanitize_html(text: str) -> str:
    return html.escape(text)
```

### Cross-Site Request Forgery (CSRF)

**Prevention (for stateful sessions):**
- CSRF tokens for state-changing operations
- SameSite cookie attribute
- Verify Origin/Referer headers

**Current Implementation:**
- Stateless JWT (CSRF not applicable)
- If implementing cookies, add CSRF protection

### Brute Force Attacks

**Prevention:**
- Rate limiting on authentication endpoints
- Account lockout after failed attempts
- CAPTCHA after multiple failures
- Monitor for distributed attacks

## Compliance

### GDPR Compliance

**User Rights:**
- Right to access (GET /me endpoint)
- Right to deletion (account deletion)
- Right to data portability (export data)
- Right to be forgotten (data cleanup)

**Data Handling:**
- Explicit consent for data collection
- Clear privacy policy
- Secure data storage
- Data retention policies

### OWASP Top 10

**Coverage:**

1. **Injection:** Parameterized queries, input validation
2. **Broken Authentication:** Strong password policy, MFA support
3. **Sensitive Data Exposure:** Encryption, HTTPS, secure storage
4. **XML External Entities:** Not applicable (JSON API)
5. **Broken Access Control:** User isolation, authorization checks
6. **Security Misconfiguration:** Security headers, secure defaults
7. **XSS:** Input sanitization, CSP headers
8. **Insecure Deserialization:** Pydantic validation
9. **Using Components with Known Vulnerabilities:** Dependency scanning
10. **Insufficient Logging:** Comprehensive audit logging

## Security Checklist

### Pre-Deployment

- [ ] All passwords hashed with bcrypt
- [ ] JWT secret key is strong and secure
- [ ] HTTPS enabled with valid certificate
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] Audit logging implemented
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies up to date
- [ ] Security testing completed
- [ ] Penetration testing performed

### Ongoing Maintenance

- [ ] Monitor failed login attempts
- [ ] Review audit logs regularly
- [ ] Update dependencies monthly
- [ ] Rotate JWT secret quarterly
- [ ] Review and update security policies
- [ ] Conduct security audits annually
- [ ] Train team on security best practices

## Incident Response

### Security Breach Protocol

1. **Detect:** Monitor logs for suspicious activity
2. **Contain:** Lock affected accounts, revoke tokens
3. **Investigate:** Analyze logs, identify scope
4. **Remediate:** Fix vulnerability, update systems
5. **Notify:** Inform affected users, report to authorities
6. **Review:** Post-mortem, update procedures

### Contact Information

**Security Team:**
- Email: security@todoapp.com
- Emergency: +1-555-SECURITY
- PGP Key: Available at https://todoapp.com/security.asc

## References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [GDPR Compliance Guide](https://gdpr.eu/)
