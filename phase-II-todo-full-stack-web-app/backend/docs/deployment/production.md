# Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Todo Application authentication system to production.

## Prerequisites

### Required Services

1. **Database:** Neon PostgreSQL (or compatible PostgreSQL 14+)
2. **Email Service:** SendGrid, AWS SES, or SMTP server
3. **Redis:** For rate limiting (optional but recommended)
4. **Domain:** SSL certificate for HTTPS

### Required Tools

- Python 3.11+
- Git
- Docker (optional)
- systemd (for service management)

## Pre-Deployment Checklist

### Security Review

- [ ] JWT secret key is cryptographically random (32+ characters)
- [ ] All environment variables configured
- [ ] HTTPS enabled with valid SSL certificate
- [ ] CORS origins restricted to production domains
- [ ] Debug mode disabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Password requirements enforced
- [ ] Audit logging enabled
- [ ] Error messages don't leak sensitive information

### Infrastructure

- [ ] Database provisioned and accessible
- [ ] Database backups configured
- [ ] Email service configured and tested
- [ ] Redis instance provisioned (if using rate limiting)
- [ ] Monitoring and alerting configured
- [ ] Log aggregation configured

### Code Quality

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Dependencies up to date
- [ ] No known security vulnerabilities
- [ ] Documentation complete

## Deployment Steps

### Step 1: Provision Infrastructure

**1.1 Database Setup (Neon)**

```bash
# Create Neon project
# Visit: https://console.neon.tech

# Get connection string
# Format: postgresql://user:password@host/database?sslmode=require
```

**1.2 Email Service Setup (SendGrid)**

```bash
# Create SendGrid account
# Visit: https://app.sendgrid.com

# Create API key with Mail Send permissions
# Save API key securely
```

**1.3 Redis Setup (Optional)**

```bash
# Option 1: Redis Cloud
# Visit: https://redis.com/try-free

# Option 2: Self-hosted
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

### Step 2: Prepare Application

**2.1 Clone Repository**

```bash
git clone https://github.com/yourorg/todoapp.git
cd todoapp/backend
```

**2.2 Create Virtual Environment**

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**2.3 Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**2.4 Configure Environment**

```bash
# Copy example environment file
cp .env.production.example .env.production

# Edit with production values
nano .env.production
```

**Required Environment Variables:**

```bash
# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# JWT Secret (generate new)
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=YOUR_SENDGRID_API_KEY
SMTP_FROM_EMAIL=noreply@todoapp.com

# Frontend
FRONTEND_URL=https://todoapp.com

# Redis (if using)
REDIS_URL=redis://default:password@host:6379/0

# CORS
ALLOWED_ORIGINS=https://todoapp.com,https://www.todoapp.com
```

### Step 3: Database Migration

**3.1 Run Migrations**

```bash
# Set environment
export $(cat .env.production | xargs)

# Run Alembic migrations
alembic upgrade head
```

**3.2 Verify Database**

```bash
# Connect to database
psql $DATABASE_URL

# Check tables
\dt

# Verify users table
\d users

# Exit
\q
```

### Step 4: Test Configuration

**4.1 Test Database Connection**

```bash
python -c "
from database import engine
from sqlmodel import Session
with Session(engine) as session:
    print('Database connection successful')
"
```

**4.2 Test Email Service**

```bash
python scripts/test_email.py --to test@example.com
```

**4.3 Run Health Check**

```bash
# Start application temporarily
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Test health endpoint
curl http://localhost:8000/api/v1/health

# Stop application
pkill -f uvicorn
```

### Step 5: Deploy Application

**Option A: Systemd Service (Recommended)**

**5.1 Create Service File**

```bash
sudo nano /etc/systemd/system/todoapp.service
```

```ini
[Unit]
Description=Todo Application API
After=network.target

[Service]
Type=notify
User=todoapp
Group=todoapp
WorkingDirectory=/opt/todoapp/backend
Environment="PATH=/opt/todoapp/backend/venv/bin"
EnvironmentFile=/opt/todoapp/backend/.env.production
ExecStart=/opt/todoapp/backend/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**5.2 Start Service**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable todoapp

# Start service
sudo systemctl start todoapp

# Check status
sudo systemctl status todoapp

# View logs
sudo journalctl -u todoapp -f
```

**Option B: Docker Deployment**

**5.1 Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 todoapp && \
    chown -R todoapp:todoapp /app
USER todoapp

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**5.2 Build and Run**

```bash
# Build image
docker build -t todoapp-api:latest .

# Run container
docker run -d \
  --name todoapp-api \
  -p 8000:8000 \
  --env-file .env.production \
  --restart unless-stopped \
  todoapp-api:latest

# Check logs
docker logs -f todoapp-api
```

**Option C: Docker Compose**

**5.1 Create docker-compose.yml**

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    restart: unless-stopped
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

**5.2 Deploy**

```bash
docker-compose up -d
docker-compose logs -f
```

### Step 6: Configure Reverse Proxy

**6.1 Nginx Configuration**

```bash
sudo nano /etc/nginx/sites-available/todoapp
```

```nginx
upstream todoapp_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.todoapp.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.todoapp.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.todoapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.todoapp.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy Configuration
    location / {
        proxy_pass http://todoapp_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Logging
    access_log /var/log/nginx/todoapp_access.log;
    error_log /var/log/nginx/todoapp_error.log;
}
```

**6.2 Enable Site**

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/todoapp /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 7: SSL Certificate

**7.1 Install Certbot**

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

**7.2 Obtain Certificate**

```bash
sudo certbot --nginx -d api.todoapp.com
```

**7.3 Auto-Renewal**

```bash
# Test renewal
sudo certbot renew --dry-run

# Renewal runs automatically via cron
```

### Step 8: Monitoring Setup

**8.1 Application Monitoring**

```bash
# Install monitoring agent (example: Datadog)
DD_API_KEY=your_api_key bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

# Configure application metrics
# Add to .env.production:
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

**8.2 Log Monitoring**

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/todoapp
```

```
/var/log/todoapp/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 todoapp todoapp
    sharedscripts
    postrotate
        systemctl reload todoapp
    endscript
}
```

**8.3 Health Checks**

```bash
# Create health check script
cat > /opt/todoapp/scripts/health_check.sh << 'EOF'
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)
if [ $response -ne 200 ]; then
    echo "Health check failed with status $response"
    systemctl restart todoapp
fi
EOF

chmod +x /opt/todoapp/scripts/health_check.sh

# Add to crontab
crontab -e
# Add: */5 * * * * /opt/todoapp/scripts/health_check.sh
```

### Step 9: Backup Configuration

**9.1 Database Backups**

```bash
# Create backup script
cat > /opt/todoapp/scripts/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/todoapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/todoapp/scripts/backup_db.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /opt/todoapp/scripts/backup_db.sh
```

### Step 10: Verification

**10.1 Smoke Tests**

```bash
# Test registration
curl -X POST https://api.todoapp.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@Password123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Test login
curl -X POST https://api.todoapp.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@Password123"
  }'

# Test health check
curl https://api.todoapp.com/api/v1/health
```

**10.2 Load Testing**

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 https://api.todoapp.com/api/v1/health
```

## Post-Deployment

### Monitoring Checklist

- [ ] Application is running
- [ ] Health checks passing
- [ ] Logs are being collected
- [ ] Metrics are being reported
- [ ] Alerts are configured
- [ ] SSL certificate valid
- [ ] Database backups running
- [ ] Email delivery working

### Documentation

- [ ] Update deployment documentation
- [ ] Document any issues encountered
- [ ] Update runbooks if needed
- [ ] Share access credentials securely

### Team Notification

- [ ] Notify team of deployment
- [ ] Share monitoring dashboard links
- [ ] Provide on-call contact information
- [ ] Schedule post-deployment review

## Rollback Procedure

If issues are encountered:

```bash
# Stop application
sudo systemctl stop todoapp

# Restore previous version
git checkout previous-tag
pip install -r requirements.txt

# Rollback database (if needed)
alembic downgrade -1

# Restart application
sudo systemctl start todoapp
```

## Troubleshooting

### Application Won't Start

```bash
# Check logs
sudo journalctl -u todoapp -n 50

# Check configuration
python -c "from config.production import settings; print('Config OK')"

# Check database connection
python -c "from database import engine; print('DB OK')"
```

### High Error Rate

```bash
# Check application logs
tail -f /var/log/todoapp/app.log

# Check Nginx logs
tail -f /var/log/nginx/todoapp_error.log

# Check system resources
htop
df -h
```

### Email Not Sending

```bash
# Test SMTP connection
python scripts/test_email.py

# Check email service status
# Visit provider dashboard

# Check logs for email errors
grep "email" /var/log/todoapp/app.log
```

## Support

For deployment issues:
- Email: devops@todoapp.com
- Slack: #deployments
- On-call: +1-555-ONCALL

## References

- [Neon Documentation](https://neon.tech/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/docs/)
