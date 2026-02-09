# Task Management Production Configuration

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Search
ENABLE_FULL_TEXT_SEARCH=true
SEARCH_RESULTS_LIMIT=100

# Batch Operations
BATCH_OPERATION_MAX_SIZE=100
BATCH_OPERATION_TIMEOUT=30

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Performance
QUERY_TIMEOUT=30
ENABLE_QUERY_CACHE=true
CACHE_TTL=300

# History
HISTORY_RETENTION_DAYS=90
DELETED_TASK_RETENTION_DAYS=30

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
BATCH_RATE_LIMIT_PER_MINUTE=20
```

---

## Database Setup

### Required Indexes
```sql
-- Core indexes (already in migrations)
CREATE INDEX idx_tasks_user_id ON tasks(user_id) WHERE deleted = false;
CREATE INDEX idx_tasks_search_vector ON tasks USING gin(search_vector);
CREATE INDEX idx_tasks_user_status_priority ON tasks(user_id, status, priority);
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag ON task_tags(tag);
CREATE INDEX idx_task_history_task_id ON task_history(task_id);
```

### Run Migrations
```bash
alembic upgrade head
```

---

## Application Configuration

### Uvicorn Production Settings
```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --timeout-keep-alive 5 \
  --log-level info
```

### Systemd Service
```ini
[Unit]
Description=Task Management API
After=network.target postgresql.service

[Service]
Type=notify
User=app
WorkingDirectory=/opt/app
EnvironmentFile=/opt/app/.env.production
ExecStart=/opt/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Monitoring

### Key Metrics
- Task creation rate
- Search query performance
- Batch operation success rate
- Database query time
- API response time (p95 < 500ms)

### Health Checks
```bash
# API health
curl https://api.example.com/health

# Database health
curl https://api.example.com/ready
```

### Alerts
- Response time > 1s (warning)
- Response time > 2s (critical)
- Error rate > 1% (warning)
- Error rate > 5% (critical)
- Database connections > 80% (warning)

---

## Security

### Rate Limiting
- Standard endpoints: 100 req/min
- Batch operations: 20 req/min
- Search: 60 req/min

### Input Validation
- Title: max 200 chars
- Description: max 2000 chars
- Tags: max 50 chars each, max 10 per task
- Batch size: max 100 tasks

### User Isolation
- All queries filtered by user_id
- Authorization checks on all endpoints
- No cross-user data access

---

## Backup Strategy

### Daily Backups
```bash
# Backup tasks
pg_dump $DATABASE_URL -t tasks -t task_tags -t task_history > backup.sql

# Upload to S3
aws s3 cp backup.sql s3://backups/tasks/$(date +%Y%m%d).sql
```

### Retention
- Daily backups: 30 days
- Weekly backups: 90 days
- Monthly backups: 1 year

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Indexes created and verified
- [ ] Search indexes built
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Backups configured
- [ ] Rate limiting enabled
- [ ] Load testing completed
- [ ] Documentation updated
