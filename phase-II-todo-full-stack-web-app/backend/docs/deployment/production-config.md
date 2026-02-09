# Analytics Production Deployment Configuration

## Overview

This document provides comprehensive configuration and deployment instructions for the Analytics system in production environments.

---

## Table of Contents

1. [Infrastructure Requirements](#infrastructure-requirements)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Application Configuration](#application-configuration)
5. [Cache Configuration](#cache-configuration)
6. [Security Configuration](#security-configuration)
7. [Monitoring Setup](#monitoring-setup)
8. [Deployment Process](#deployment-process)
9. [Scaling Configuration](#scaling-configuration)
10. [Disaster Recovery](#disaster-recovery)

---

## Infrastructure Requirements

### Minimum Requirements

**Application Server**:
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB SSD
- OS: Ubuntu 22.04 LTS or similar

**Database Server** (Neon PostgreSQL):
- Neon Serverless PostgreSQL
- Storage: 100 GB (auto-scaling)
- Compute: 2 vCPU, 8 GB RAM minimum
- Backup: Automated daily backups

**Cache Server** (Redis):
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB
- Version: Redis 7.0+

**Load Balancer**:
- Nginx or AWS ALB
- SSL/TLS termination
- Health check support

### Recommended Production Setup

**Application Tier**:
- 3+ application servers for high availability
- Auto-scaling group (min: 3, max: 10)
- Load balancer with health checks

**Database Tier**:
- Neon Serverless PostgreSQL (managed)
- Automatic scaling and backups
- Read replicas for analytics queries

**Cache Tier**:
- Redis Cluster (3 nodes minimum)
- Sentinel for automatic failover
- Persistence enabled (AOF + RDB)

**Monitoring**:
- Prometheus for metrics
- Grafana for dashboards
- ELK stack for logs
- PagerDuty for alerts

---

## Environment Configuration

### Environment Variables

Create `.env.production` file:

```bash
# Application
APP_ENV=production
APP_DEBUG=false
APP_NAME="Analytics API"
APP_VERSION=1.0.0

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
WORKER_CLASS=uvicorn.workers.UvicornWorker
TIMEOUT=30
KEEPALIVE=5

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.us-east-2.aws.neon.tech/analytics?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Redis Cache
REDIS_URL=redis://redis.production.internal:6379/0
REDIS_PASSWORD=your_redis_password
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5

# Authentication
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
ALLOWED_HOSTS=api.example.com,www.example.com
CORS_ORIGINS=https://app.example.com,https://www.example.com
CORS_CREDENTIALS=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/analytics/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# Background Jobs
ENABLE_DAILY_AGGREGATION=true
ENABLE_CACHE_WARMING=true
AGGREGATION_SCHEDULE="0 1 * * *"  # 1 AM daily
CACHE_WARMING_SCHEDULE="0 */6 * * *"  # Every 6 hours

# Performance
CACHE_TTL_OVERVIEW=300  # 5 minutes
CACHE_TTL_TRENDS=900  # 15 minutes
CACHE_TTL_PRODUCTIVITY=600  # 10 minutes
QUERY_TIMEOUT=30  # seconds
MAX_EXPORT_ROWS=100000

# Feature Flags
ENABLE_MATERIALIZED_VIEWS=true
ENABLE_QUERY_CACHE=true
ENABLE_RESPONSE_COMPRESSION=true
```

### Secrets Management

**Using AWS Secrets Manager**:

```bash
# Store secrets
aws secretsmanager create-secret \
  --name analytics/production/database \
  --secret-string '{"url":"postgresql://...","password":"..."}'

aws secretsmanager create-secret \
  --name analytics/production/jwt \
  --secret-string '{"secret_key":"...","algorithm":"HS256"}'

# Retrieve in application
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Load secrets
db_secrets = get_secret('analytics/production/database')
DATABASE_URL = db_secrets['url']
```

**Using HashiCorp Vault**:

```bash
# Store secrets
vault kv put secret/analytics/production \
  database_url="postgresql://..." \
  jwt_secret="..." \
  redis_password="..."

# Retrieve in application
import hvac

client = hvac.Client(url='https://vault.example.com')
client.token = os.getenv('VAULT_TOKEN')
secrets = client.secrets.kv.v2.read_secret_version(path='analytics/production')
DATABASE_URL = secrets['data']['data']['database_url']
```

---

## Database Setup

### Neon PostgreSQL Configuration

**Create Database**:

```bash
# Using Neon CLI
neonctl databases create analytics --project-id your-project-id

# Or via Neon Console
# 1. Go to https://console.neon.tech
# 2. Create new database "analytics"
# 3. Copy connection string
```

**Connection String Format**:
```
postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/analytics?sslmode=require
```

**Initialize Schema**:

```bash
# Run migrations
alembic upgrade head

# Verify schema
psql $DATABASE_URL -c "\dt"
```

**Create Indexes**:

```sql
-- Core indexes for performance
CREATE INDEX CONCURRENTLY idx_tasks_user_id ON tasks(user_id) WHERE deleted = FALSE;
CREATE INDEX CONCURRENTLY idx_tasks_user_status ON tasks(user_id, status) WHERE deleted = FALSE;
CREATE INDEX CONCURRENTLY idx_tasks_user_due_date ON tasks(user_id, due_date) WHERE deleted = FALSE AND status != 'done';
CREATE INDEX CONCURRENTLY idx_tasks_user_completed ON tasks(user_id, completed_at) WHERE status = 'done' AND deleted = FALSE;
CREATE INDEX CONCURRENTLY idx_tasks_user_priority ON tasks(user_id, priority) WHERE deleted = FALSE;
CREATE INDEX CONCURRENTLY idx_tasks_created_at ON tasks(user_id, created_at) WHERE deleted = FALSE;

-- Analytics indexes
CREATE INDEX CONCURRENTLY idx_daily_analytics_user_date ON daily_analytics(user_id, date);
CREATE INDEX CONCURRENTLY idx_daily_analytics_date ON daily_analytics(date);
```

**Create Materialized Views**:

```sql
-- User task stats
CREATE MATERIALIZED VIEW user_task_stats AS
SELECT
    user_id,
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE status = 'done') as completed_tasks,
    COUNT(*) FILTER (WHERE status = 'todo') as pending_tasks,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_tasks,
    COUNT(*) FILTER (WHERE status != 'done' AND due_date < CURRENT_DATE) as overdue_tasks,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'done')::numeric /
        NULLIF(COUNT(*), 0) * 100,
        1
    ) as completion_rate
FROM tasks
WHERE deleted = FALSE
GROUP BY user_id;

CREATE UNIQUE INDEX idx_user_task_stats_user_id ON user_task_stats(user_id);

-- Priority distribution
CREATE MATERIALIZED VIEW user_priority_distribution AS
SELECT
    user_id,
    COUNT(*) FILTER (WHERE priority = 'high') as high_priority,
    COUNT(*) FILTER (WHERE priority = 'medium') as medium_priority,
    COUNT(*) FILTER (WHERE priority = 'low') as low_priority
FROM tasks
WHERE deleted = FALSE
GROUP BY user_id;

CREATE UNIQUE INDEX idx_user_priority_dist_user_id ON user_priority_distribution(user_id);

-- Status distribution
CREATE MATERIALIZED VIEW user_status_distribution AS
SELECT
    user_id,
    COUNT(*) FILTER (WHERE status = 'todo') as todo_count,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_count,
    COUNT(*) FILTER (WHERE status = 'done') as done_count
FROM tasks
WHERE deleted = FALSE
GROUP BY user_id;

CREATE UNIQUE INDEX idx_user_status_dist_user_id ON user_status_distribution(user_id);

-- Monthly trends
CREATE MATERIALIZED VIEW user_monthly_trends AS
SELECT
    user_id,
    DATE_TRUNC('month', date) as month,
    SUM(tasks_created) as tasks_created,
    SUM(tasks_completed) as tasks_completed,
    AVG(completion_rate) as avg_completion_rate,
    AVG(productivity_score) as avg_productivity_score
FROM daily_analytics
GROUP BY user_id, DATE_TRUNC('month', date);

CREATE INDEX idx_user_monthly_trends_user_month ON user_monthly_trends(user_id, month);
```

**Configure Connection Pooling**:

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require",
        "server_settings": {
            "application_name": "analytics_api",
            "jit": "off"  # Disable JIT for consistent performance
        }
    }
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

---

## Application Configuration

### FastAPI Application Setup

**main.py**:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Analytics API...")

    # Initialize database
    from database import engine
    logger.info("Database connection established")

    # Initialize Redis
    from cache import redis_client
    await redis_client.ping()
    logger.info("Redis connection established")

    # Warm cache for active users
    if os.getenv("ENABLE_CACHE_WARMING") == "true":
        from jobs.cache_warming import warm_cache_for_active_users
        await warm_cache_for_active_users()
        logger.info("Cache warmed for active users")

    yield

    # Cleanup
    logger.info("Shutting down Analytics API...")
    await engine.dispose()
    await redis_client.close()

app = FastAPI(
    title="Analytics API",
    description="Task Analytics and Insights API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("APP_ENV") != "production" else None,
    redoc_url="/redoc" if os.getenv("APP_ENV") != "production" else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
from routes import analytics, auth, tasks
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Readiness check
@app.get("/ready")
async def readiness_check():
    try:
        # Check database
        from database import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")

        # Check Redis
        from cache import redis_client
        await redis_client.ping()

        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")
```

### Systemd Service Configuration

**`/etc/systemd/system/analytics-api.service`**:

```ini
[Unit]
Description=Analytics API Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=analytics
Group=analytics
WorkingDirectory=/opt/analytics
Environment="PATH=/opt/analytics/venv/bin"
EnvironmentFile=/opt/analytics/.env.production
ExecStart=/opt/analytics/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout-keep-alive 5 \
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/analytics /var/run/analytics

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

**Enable and start service**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable analytics-api
sudo systemctl start analytics-api
sudo systemctl status analytics-api
```

---

## Cache Configuration

### Redis Setup

**`/etc/redis/redis.conf`**:

```conf
# Network
bind 0.0.0.0
port 6379
protected-mode yes
requirepass your_redis_password

# Memory
maxmemory 4gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300
databases 16

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Slow log
slowlog-log-slower-than 10000
slowlog-max-len 128
```

**Redis Cluster Configuration** (for high availability):

```bash
# Create cluster with 3 masters and 3 replicas
redis-cli --cluster create \
  redis1:6379 redis2:6379 redis3:6379 \
  redis4:6379 redis5:6379 redis6:6379 \
  --cluster-replicas 1
```

---

## Security Configuration

### SSL/TLS Configuration

**Nginx SSL Configuration**:

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to application
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}
```

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Rate Limiting

**Application-level rate limiting**:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/users/{user_id}/analytics/overview")
@limiter.limit("60/minute")
async def get_overview(user_id: str):
    # ...
```

---

## Monitoring Setup

### Prometheus Configuration

**`prometheus.yml`**:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'analytics-api'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'

  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### Grafana Dashboards

**Import pre-built dashboards**:
- FastAPI Dashboard: ID 14280
- PostgreSQL Dashboard: ID 9628
- Redis Dashboard: ID 11835
- Node Exporter Dashboard: ID 1860

### Application Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter(
    'analytics_requests_total',
    'Total analytics requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'analytics_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Cache metrics
cache_hits = Counter('analytics_cache_hits_total', 'Total cache hits')
cache_misses = Counter('analytics_cache_misses_total', 'Total cache misses')

# Database metrics
db_query_duration = Histogram(
    'analytics_db_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

# Business metrics
active_users = Gauge('analytics_active_users', 'Number of active users')
tasks_total = Gauge('analytics_tasks_total', 'Total number of tasks')
```

---

## Deployment Process

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Secrets stored securely
- [ ] SSL certificates valid
- [ ] Monitoring configured
- [ ] Backup verified
- [ ] Rollback plan ready

### Deployment Steps

**1. Prepare Release**:

```bash
# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Build application
python -m build
```

**2. Database Migration**:

```bash
# Backup database
pg_dump $DATABASE_URL > backup_pre_deployment.sql

# Run migrations
alembic upgrade head

# Verify migration
alembic current
```

**3. Deploy Application**:

```bash
# Stop application
sudo systemctl stop analytics-api

# Update code
cd /opt/analytics
git pull origin main
git checkout v1.0.0

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Start application
sudo systemctl start analytics-api

# Verify
curl https://api.example.com/health
```

**4. Post-Deployment Verification**:

```bash
# Check service status
sudo systemctl status analytics-api

# Check logs
sudo journalctl -u analytics-api -n 100

# Run smoke tests
python -m pytest tests/smoke/

# Monitor metrics
# Check Grafana dashboard for anomalies
```

### Blue-Green Deployment

```bash
# Deploy to green environment
deploy_to_environment green

# Run tests on green
run_tests green

# Switch traffic to green
switch_traffic green

# Monitor for issues
monitor_environment green --duration=30m

# If successful, decommission blue
# If issues, rollback to blue
```

---

## Scaling Configuration

### Horizontal Scaling

**Auto-scaling policy**:

```yaml
# AWS Auto Scaling Group
min_size: 3
max_size: 10
desired_capacity: 3

scaling_policies:
  - name: scale_up
    metric: CPUUtilization
    threshold: 70
    adjustment: +2
    cooldown: 300

  - name: scale_down
    metric: CPUUtilization
    threshold: 30
    adjustment: -1
    cooldown: 300
```

### Database Scaling

**Neon PostgreSQL auto-scaling**:
- Automatically scales compute based on load
- Configure minimum and maximum compute units
- Enable autosuspend for cost optimization

```bash
# Configure via Neon CLI
neonctl branches set-default \
  --project-id your-project-id \
  --compute-min 0.25 \
  --compute-max 4
```

### Cache Scaling

**Redis Cluster scaling**:

```bash
# Add new nodes to cluster
redis-cli --cluster add-node new-node:6379 existing-node:6379

# Rebalance cluster
redis-cli --cluster rebalance existing-node:6379
```

---

## Disaster Recovery

### Backup Strategy

**Automated backups**:

```bash
#!/bin/bash
# /opt/analytics/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/analytics

# Database backup
pg_dump $DATABASE_URL | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://backups/analytics/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

**Schedule via cron**:

```cron
# Daily backup at 3 AM
0 3 * * * /opt/analytics/scripts/backup.sh
```

### Recovery Procedures

**Database recovery**:

```bash
# Download backup
aws s3 cp s3://backups/analytics/db_latest.sql.gz .

# Restore database
gunzip db_latest.sql.gz
psql $DATABASE_URL < db_latest.sql

# Verify restoration
psql $DATABASE_URL -c "SELECT COUNT(*) FROM tasks;"
```

---

## Appendix

### Deployment Checklist

```markdown
## Pre-Deployment
- [ ] Code freeze announced
- [ ] All tests passing
- [ ] Database backup completed
- [ ] Rollback plan documented
- [ ] Stakeholders notified

## Deployment
- [ ] Database migrations applied
- [ ] Application deployed
- [ ] Health checks passing
- [ ] Smoke tests completed
- [ ] Monitoring verified

## Post-Deployment
- [ ] Performance metrics normal
- [ ] Error rates acceptable
- [ ] User feedback collected
- [ ] Documentation updated
- [ ] Deployment report created
```

### Useful Commands

```bash
# Service management
sudo systemctl start analytics-api
sudo systemctl stop analytics-api
sudo systemctl restart analytics-api
sudo systemctl status analytics-api

# Logs
sudo journalctl -u analytics-api -f
tail -f /var/log/analytics/app.log

# Database
psql $DATABASE_URL
alembic upgrade head
alembic current

# Cache
redis-cli ping
redis-cli FLUSHDB
redis-cli INFO

# Monitoring
curl https://api.example.com/health
curl https://api.example.com/metrics
```
