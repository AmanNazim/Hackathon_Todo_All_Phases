# Authentication Operations Runbook

## Overview

This runbook provides operational procedures for managing the authentication system, handling common issues, and responding to security incidents.

## Table of Contents

1. [Account Recovery](#account-recovery)
2. [Account Lockout Response](#account-lockout-response)
3. [Security Breach Protocol](#security-breach-protocol)
4. [Password Reset Issues](#password-reset-issues)
5. [Email Verification Issues](#email-verification-issues)
6. [Token Management](#token-management)
7. [Monitoring and Alerts](#monitoring-and-alerts)
8. [Database Operations](#database-operations)

---

## Account Recovery

### User Cannot Access Account

**Symptoms:**
- User reports inability to login
- User forgot password
- User lost access to email

**Diagnosis Steps:**

1. **Verify account exists:**
```sql
SELECT id, email, is_active, email_verified, failed_login_attempts, locked_until
FROM users
WHERE email = 'user@example.com';
```

2. **Check account status:**
   - Is account active? (`is_active = true`)
   - Is account locked? (`locked_until > NOW()`)
   - Failed login attempts count

3. **Check audit logs:**
```sql
SELECT event, timestamp, ip_address, metadata
FROM audit_logs
WHERE user_id = 'user_id'
ORDER BY timestamp DESC
LIMIT 20;
```

**Resolution:**

**Scenario 1: Forgot Password**
```bash
# User should use forgot password flow
# If email not working, manually generate reset token:
python scripts/generate_reset_token.py --email user@example.com
```

**Scenario 2: Account Locked**
```sql
-- Unlock account
UPDATE users
SET failed_login_attempts = 0,
    locked_until = NULL
WHERE email = 'user@example.com';
```

**Scenario 3: Email Not Verified**
```bash
# Manually verify email
python scripts/verify_email.py --email user@example.com
```

**Scenario 4: Account Inactive**
```sql
-- Reactivate account
UPDATE users
SET is_active = true
WHERE email = 'user@example.com';
```

---

## Account Lockout Response

### User Account Locked Due to Failed Attempts

**Symptoms:**
- User receives "Account temporarily locked" error
- Multiple failed login attempts in audit logs

**Automatic Resolution:**
- Lockout expires after 15 minutes
- User can try again after expiration

**Manual Unlock:**

1. **Verify user identity** (via support ticket, phone, etc.)

2. **Check for suspicious activity:**
```sql
SELECT timestamp, ip_address, user_agent
FROM audit_logs
WHERE user_id = 'user_id'
  AND event = 'login_failed'
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

3. **Unlock account if legitimate:**
```sql
UPDATE users
SET failed_login_attempts = 0,
    locked_until = NULL
WHERE id = 'user_id';
```

4. **If suspicious activity detected:**
   - Keep account locked
   - Require password reset
   - Notify user via email
   - Escalate to security team

**Prevention:**
- Educate users about password managers
- Implement CAPTCHA after 3 failed attempts
- Monitor for distributed brute force attacks

---

## Security Breach Protocol

### Suspected Account Compromise

**Indicators:**
- Login from unusual location
- Multiple failed login attempts followed by success
- Unusual API activity
- User reports unauthorized access

**Immediate Actions:**

1. **Lock the account:**
```sql
UPDATE users
SET is_active = false,
    locked_until = NOW() + INTERVAL '24 hours'
WHERE id = 'user_id';
```

2. **Invalidate all sessions** (if using stateful sessions):
```sql
DELETE FROM sessions
WHERE user_id = 'user_id';
```

3. **Review audit logs:**
```sql
SELECT *
FROM audit_logs
WHERE user_id = 'user_id'
  AND timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;
```

4. **Check for data access:**
```sql
SELECT *
FROM task_history
WHERE user_id = 'user_id'
  AND timestamp > NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;
```

5. **Notify user:**
   - Send security alert email
   - Require password reset
   - Recommend enabling 2FA (when available)

6. **Document incident:**
   - Create incident report
   - Record timeline of events
   - Note affected data
   - Document remediation steps

**Investigation:**

1. **Analyze access patterns:**
   - IP addresses
   - User agents
   - Geographic locations
   - Time patterns

2. **Check for credential stuffing:**
   - Compare with known breach databases
   - Check if password is common

3. **Review system logs:**
   - Application logs
   - Web server logs
   - Database logs

**Recovery:**

1. **Force password reset:**
```bash
python scripts/force_password_reset.py --user-id user_id
```

2. **Reactivate account after verification:**
```sql
UPDATE users
SET is_active = true,
    locked_until = NULL
WHERE id = 'user_id';
```

3. **Monitor account for 30 days:**
   - Set up alerts for unusual activity
   - Review logs weekly

---

## Password Reset Issues

### User Not Receiving Reset Email

**Diagnosis:**

1. **Check email service status:**
```bash
# Test SMTP connection
python scripts/test_email.py
```

2. **Check email logs:**
```bash
grep "password_reset" /var/log/app/email.log | tail -20
```

3. **Verify email address:**
```sql
SELECT email, email_verified
FROM users
WHERE email = 'user@example.com';
```

4. **Check spam folder** (instruct user)

**Resolution:**

1. **Resend reset email:**
```bash
python scripts/send_reset_email.py --email user@example.com
```

2. **If email service down:**
   - Generate reset token manually
   - Provide token to user via support ticket
   - User can use token at: `/reset-password?token=TOKEN`

3. **Check email provider blocklist:**
   - Verify sender reputation
   - Check SPF/DKIM/DMARC records
   - Contact email provider if blocked

### Reset Token Expired

**User reports:** "Reset link expired"

**Resolution:**

1. **Generate new token:**
```bash
# User should request new reset email
# Or manually generate:
python scripts/generate_reset_token.py --email user@example.com
```

2. **Extend token expiration** (emergency only):
```sql
UPDATE password_reset_tokens
SET expires_at = NOW() + INTERVAL '1 hour'
WHERE user_id = 'user_id'
  AND used = false
ORDER BY created_at DESC
LIMIT 1;
```

---

## Email Verification Issues

### User Not Receiving Verification Email

**Diagnosis:**

1. **Check if email already verified:**
```sql
SELECT email_verified
FROM users
WHERE email = 'user@example.com';
```

2. **Check email logs:**
```bash
grep "email_verification" /var/log/app/email.log | tail -20
```

3. **Verify token exists:**
```sql
SELECT *
FROM email_verification_tokens
WHERE user_id = 'user_id'
  AND used = false
ORDER BY created_at DESC
LIMIT 1;
```

**Resolution:**

1. **Resend verification email:**
```bash
python scripts/resend_verification.py --email user@example.com
```

2. **Manually verify email** (after identity verification):
```sql
UPDATE users
SET email_verified = true
WHERE email = 'user@example.com';

-- Mark token as used
UPDATE email_verification_tokens
SET used = true
WHERE user_id = 'user_id';
```

### Verification Link Not Working

**User reports:** "Link doesn't work" or "Invalid token"

**Diagnosis:**

1. **Check token validity:**
```sql
SELECT token_hash, expires_at, used
FROM email_verification_tokens
WHERE user_id = 'user_id'
ORDER BY created_at DESC
LIMIT 1;
```

2. **Check if token expired:**
   - Tokens expire after 24 hours

3. **Check if token already used:**
   - `used = true`

**Resolution:**

1. **Generate new verification token:**
```bash
python scripts/generate_verification_token.py --email user@example.com
```

2. **Send new verification email:**
```bash
python scripts/send_verification_email.py --email user@example.com
```

---

## Token Management

### JWT Secret Rotation

**When to rotate:**
- Every 90 days (scheduled)
- After security breach
- When employee with access leaves

**Procedure:**

1. **Generate new secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Update environment variable:**
```bash
# In production environment
export JWT_SECRET_KEY="new_secret_key"
```

3. **Restart application:**
```bash
systemctl restart todoapp
```

4. **Notify users:**
   - All existing tokens will be invalidated
   - Users need to login again
   - Send notification email

5. **Monitor for issues:**
   - Watch error logs
   - Monitor support tickets
   - Check login success rate

### Clean Up Expired Tokens

**Schedule:** Daily at 2 AM

**Manual cleanup:**

```sql
-- Delete expired password reset tokens
DELETE FROM password_reset_tokens
WHERE expires_at < NOW() - INTERVAL '7 days';

-- Delete expired verification tokens
DELETE FROM email_verification_tokens
WHERE expires_at < NOW() - INTERVAL '7 days';

-- Delete old audit logs (keep 90 days)
DELETE FROM audit_logs
WHERE timestamp < NOW() - INTERVAL '90 days';
```

**Automated cleanup script:**
```bash
python scripts/cleanup_tokens.py --dry-run
python scripts/cleanup_tokens.py --execute
```

---

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Authentication Success Rate:**
   - Target: > 95%
   - Alert if < 90%

2. **Failed Login Attempts:**
   - Alert if > 100 per minute (possible attack)

3. **Account Lockouts:**
   - Alert if > 10 per hour

4. **Password Reset Requests:**
   - Alert if > 50 per hour (possible enumeration attack)

5. **Email Delivery Rate:**
   - Target: > 98%
   - Alert if < 95%

### Alert Configuration

**High Priority Alerts:**

```yaml
# Prometheus alert rules
groups:
  - name: authentication
    rules:
      - alert: HighFailedLoginRate
        expr: rate(failed_logins_total[5m]) > 10
        for: 5m
        annotations:
          summary: "High rate of failed login attempts"

      - alert: MassAccountLockout
        expr: rate(account_lockouts_total[5m]) > 5
        for: 5m
        annotations:
          summary: "Multiple accounts being locked"

      - alert: EmailDeliveryFailure
        expr: rate(email_failures_total[5m]) > 1
        for: 10m
        annotations:
          summary: "Email delivery failures detected"
```

### Log Analysis

**Check for suspicious patterns:**

```bash
# Failed login attempts by IP
grep "login_failed" /var/log/app/audit.log | \
  awk '{print $5}' | sort | uniq -c | sort -rn | head -20

# Successful logins from new IPs
grep "login_success" /var/log/app/audit.log | \
  grep "new_ip" | tail -50

# Password reset requests
grep "password_reset_requested" /var/log/app/audit.log | \
  wc -l
```

---

## Database Operations

### Backup and Recovery

**Daily Backups:**
```bash
# Backup users table
pg_dump -h localhost -U postgres -t users todoapp > users_backup.sql

# Backup authentication tables
pg_dump -h localhost -U postgres \
  -t users \
  -t password_reset_tokens \
  -t email_verification_tokens \
  -t audit_logs \
  todoapp > auth_backup.sql
```

**Restore from Backup:**
```bash
psql -h localhost -U postgres todoapp < auth_backup.sql
```

### Database Maintenance

**Weekly maintenance:**

```sql
-- Vacuum and analyze
VACUUM ANALYZE users;
VACUUM ANALYZE password_reset_tokens;
VACUUM ANALYZE email_verification_tokens;
VACUUM ANALYZE audit_logs;

-- Reindex
REINDEX TABLE users;
REINDEX TABLE password_reset_tokens;
REINDEX TABLE email_verification_tokens;
```

### Performance Optimization

**Check slow queries:**
```sql
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%users%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Add missing indexes:**
```sql
-- Check for missing indexes
SELECT schemaname, tablename, attname
FROM pg_stats
WHERE schemaname = 'public'
  AND tablename IN ('users', 'password_reset_tokens', 'email_verification_tokens')
  AND n_distinct > 100
  AND correlation < 0.1;
```

---

## Emergency Contacts

**On-Call Rotation:**
- Primary: oncall-primary@todoapp.com
- Secondary: oncall-secondary@todoapp.com
- Manager: engineering-manager@todoapp.com

**Escalation Path:**
1. On-call engineer (respond within 15 minutes)
2. Senior engineer (respond within 30 minutes)
3. Engineering manager (respond within 1 hour)
4. CTO (for critical incidents)

**External Contacts:**
- Email Provider Support: support@emailprovider.com
- Database Provider Support: support@neon.tech
- Security Consultant: security@consultant.com

---

## Appendix

### Useful Scripts

All operational scripts located in: `/scripts/operations/`

- `generate_reset_token.py` - Generate password reset token
- `verify_email.py` - Manually verify user email
- `unlock_account.py` - Unlock locked account
- `cleanup_tokens.py` - Clean up expired tokens
- `test_email.py` - Test email service
- `audit_report.py` - Generate audit report

### Configuration Files

- `/config/production.py` - Production configuration
- `/config/email.yaml` - Email service configuration
- `/config/security.yaml` - Security settings
- `.env.production` - Environment variables

### Monitoring Dashboards

- Grafana: https://grafana.todoapp.com/d/auth
- Prometheus: https://prometheus.todoapp.com
- Logs: https://logs.todoapp.com

### Documentation

- API Docs: `/docs/api/authentication.md`
- Security: `/docs/security/authentication.md`
- User Guide: `/docs/user/authentication.md`
