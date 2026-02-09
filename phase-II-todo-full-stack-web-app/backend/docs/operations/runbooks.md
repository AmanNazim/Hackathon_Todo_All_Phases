# Analytics Operational Runbooks

## Overview

This document provides operational procedures, troubleshooting guides, and maintenance tasks for the Analytics system. Use these runbooks for day-to-day operations, incident response, and system maintenance.

---

## Table of Contents

1. [System Health Checks](#system-health-checks)
2. [Daily Operations](#daily-operations)
3. [Incident Response](#incident-response)
4. [Performance Tuning](#performance-tuning)
5. [Database Maintenance](#database-maintenance)
6. [Cache Management](#cache-management)
7. [Monitoring and Alerting](#monitoring-and-alerting)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Emergency Procedures](#emergency-procedures)

---

## System Health Checks

### Daily Health Check

**Frequency**: Every morning before business hours

**Procedure**:

1. **Check System Status**
   ```bash
   # Check API health endpoint
   curl https://api.example.com/health

   # Expected response: {"status": "healthy"}
   ```

2. **Verify Database Connectivity**
   ```bash
   # Connect to database
   psql $DATABASE_URL -c "SELECT 1;"

   # Check active connections
   psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
   ```

3. **Check Cache Status**
   ```bash
   # Connect to Redis
   redis-cli ping

   # Check memory usage
   redis-cli info memory
   ```

4. **Review Error Logs**
   ```bash
   # Check application logs for errors
   tail -n 100 /var/log/app/error.log | grep ERROR

   # Check for rate limit violations
   grep "RateLimitExceeded" /var/log/app/access.log | wc -l
   ```

5. **Verify Background Jobs**
   ```bash
   # Check daily aggregation job status
   python -m jobs.check_job_status --job=daily_aggregation

   # Check cache warming job status
   python -m jobs.check_job_status --job=cache_warming
   ```

**Success Criteria**:
- All health checks return 200 OK
- Database connections < 80% of max
- Redis memory usage < 75%
- No critical errors in logs
- All background jobs completed successfully

**Escalation**: If any check fails, follow [Incident Response](#incident-response) procedures.

---

### Weekly Health Check

**Frequency**: Every Monday morning

**Procedure**:

1. **Review Performance Metrics**
   ```bash
   # Check average response times
   python -m scripts.analytics_performance_report --days=7
   ```

2. **Analyze Slow Queries**
   ```sql
   -- Check slow queries from past week
   SELECT
       query,
       mean_exec_time,
       calls
   FROM pg_stat_statements
   WHERE mean_exec_time > 1000  -- > 1 second
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   ```

3. **Review Cache Hit Rates**
   ```bash
   # Check Redis cache statistics
   redis-cli info stats | grep keyspace_hits
   redis-cli info stats | grep keyspace_misses
   ```

4. **Check Disk Space**
   ```bash
   # Check database disk usage
   df -h /var/lib/postgresql

   # Check log disk usage
   df -h /var/log
   ```

5. **Review User Growth**
   ```sql
   -- Check new users this week
   SELECT COUNT(*) FROM users
   WHERE created_at >= NOW() - INTERVAL '7 days';
   ```

**Action Items**:
- Document any performance degradation
- Plan optimization if response times > 2s
- Clean up old logs if disk > 80%
- Scale resources if user growth > 20%

---

## Daily Operations

### Morning Routine

**Time**: 8:00 AM UTC

**Tasks**:

1. **Run Daily Health Check** (see above)

2. **Review Overnight Alerts**
   ```bash
   # Check alert history
   python -m scripts.check_alerts --since="24 hours ago"
   ```

3. **Verify Data Aggregation**
   ```sql
   -- Check yesterday's aggregation completed
   SELECT COUNT(*) FROM daily_analytics
   WHERE date = CURRENT_DATE - INTERVAL '1 day';
   ```

4. **Check for Anomalies**
   ```sql
   -- Check for unusual metric values
   SELECT user_id, completion_rate
   FROM daily_analytics
   WHERE date = CURRENT_DATE - INTERVAL '1 day'
     AND (completion_rate > 100 OR completion_rate < 0);
   ```

**Duration**: 15-20 minutes

---

### Evening Routine

**Time**: 6:00 PM UTC

**Tasks**:

1. **Refresh Materialized Views**
   ```sql
   REFRESH MATERIALIZED VIEW CONCURRENTLY user_task_stats;
   REFRESH MATERIALIZED VIEW CONCURRENTLY user_priority_distribution;
   REFRESH MATERIALIZED VIEW CONCURRENTLY user_status_distribution;
   REFRESH MATERIALIZED VIEW CONCURRENTLY user_monthly_trends;
   ```

2. **Warm Cache for Active Users**
   ```bash
   python -m jobs.cache_warming
   ```

3. **Review Day's Performance**
   ```bash
   python -m scripts.daily_performance_summary
   ```

4. **Backup Critical Data**
   ```bash
   # Trigger backup job
   python -m scripts.backup_analytics_data
   ```

**Duration**: 10-15 minutes

---

## Incident Response

### Severity Levels

**P0 - Critical**
- Complete system outage
- Data loss or corruption
- Security breach
- Response time: Immediate

**P1 - High**
- Partial system outage
- Severe performance degradation (>10s response times)
- Background jobs failing
- Response time: Within 1 hour

**P2 - Medium**
- Minor performance issues
- Non-critical feature unavailable
- Cache failures
- Response time: Within 4 hours

**P3 - Low**
- Cosmetic issues
- Documentation errors
- Minor bugs
- Response time: Next business day

---

### P0: Complete System Outage

**Symptoms**:
- Health endpoint returns 500 or times out
- All analytics endpoints failing
- Database unreachable

**Immediate Actions**:

1. **Declare Incident**
   ```bash
   # Create incident ticket
   python -m scripts.create_incident --severity=P0 --title="Analytics System Outage"
   ```

2. **Check System Status**
   ```bash
   # Check if application is running
   systemctl status analytics-api

   # Check database status
   systemctl status postgresql

   # Check Redis status
   systemctl status redis
   ```

3. **Review Recent Changes**
   ```bash
   # Check recent deployments
   git log --since="2 hours ago" --oneline

   # Check recent configuration changes
   diff /etc/analytics/config.yml /etc/analytics/config.yml.backup
   ```

4. **Attempt Quick Recovery**
   ```bash
   # Restart application
   systemctl restart analytics-api

   # If database issue, check connections
   psql $DATABASE_URL -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction';"
   ```

5. **Rollback if Needed**
   ```bash
   # Rollback to previous version
   git checkout <previous-stable-commit>
   systemctl restart analytics-api
   ```

**Communication**:
- Post status update immediately
- Update every 15 minutes
- Notify all stakeholders

**Post-Incident**:
- Write incident report
- Schedule post-mortem
- Implement preventive measures

---

### P1: Severe Performance Degradation

**Symptoms**:
- Response times > 10 seconds
- Timeout errors
- High CPU or memory usage

**Investigation Steps**:

1. **Check Resource Usage**
   ```bash
   # Check CPU and memory
   top -b -n 1 | head -20

   # Check database connections
   psql $DATABASE_URL -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"
   ```

2. **Identify Slow Queries**
   ```sql
   -- Find currently running slow queries
   SELECT
       pid,
       now() - query_start as duration,
       query
   FROM pg_stat_activity
   WHERE state = 'active'
     AND now() - query_start > interval '5 seconds'
   ORDER BY duration DESC;
   ```

3. **Check Cache Status**
   ```bash
   # Check Redis memory
   redis-cli info memory

   # Check cache hit rate
   redis-cli info stats | grep keyspace
   ```

4. **Review Recent Traffic**
   ```bash
   # Check request volume
   tail -n 1000 /var/log/app/access.log | wc -l

   # Check for unusual patterns
   tail -n 1000 /var/log/app/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10
   ```

**Mitigation Actions**:

1. **Kill Long-Running Queries**
   ```sql
   -- Terminate specific query
   SELECT pg_terminate_backend(<pid>);
   ```

2. **Clear Cache if Corrupted**
   ```bash
   redis-cli FLUSHDB
   python -m jobs.cache_warming
   ```

3. **Scale Resources**
   ```bash
   # Increase worker processes
   export WORKERS=8
   systemctl restart analytics-api
   ```

4. **Enable Rate Limiting**
   ```python
   # Temporarily reduce rate limits
   # Edit config and restart
   ```

---

### P2: Background Job Failure

**Symptoms**:
- Daily aggregation not completing
- Cache warming failing
- Materialized views not refreshing

**Investigation**:

1. **Check Job Logs**
   ```bash
   # Check aggregation job logs
   tail -n 100 /var/log/jobs/daily_aggregation.log

   # Check for errors
   grep ERROR /var/log/jobs/*.log
   ```

2. **Verify Database Access**
   ```bash
   # Test database connection
   python -c "from database import engine; engine.connect()"
   ```

3. **Check Job Schedule**
   ```bash
   # Verify cron jobs
   crontab -l

   # Check systemd timers
   systemctl list-timers
   ```

**Resolution**:

1. **Manually Run Failed Job**
   ```bash
   # Run aggregation for specific date
   python -m jobs.daily_aggregation --date=2024-01-15

   # Run cache warming
   python -m jobs.cache_warming
   ```

2. **Fix Underlying Issue**
   - Review error messages
   - Fix code or configuration
   - Test manually before scheduling

3. **Verify Completion**
   ```sql
   -- Check aggregation data
   SELECT * FROM daily_analytics
   WHERE date = '2024-01-15'
   LIMIT 10;
   ```

---

## Performance Tuning

### Slow Query Optimization

**Identify Slow Queries**:

```sql
-- Enable pg_stat_statements if not already
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slowest queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- > 100ms
ORDER BY mean_exec_time DESC
LIMIT 20;
```

**Optimization Steps**:

1. **Analyze Query Plan**
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM tasks
   WHERE user_id = 'xxx' AND status = 'done';
   ```

2. **Add Missing Indexes**
   ```sql
   -- Example: Add composite index
   CREATE INDEX CONCURRENTLY idx_tasks_user_status
   ON tasks(user_id, status)
   WHERE deleted = FALSE;
   ```

3. **Update Statistics**
   ```sql
   ANALYZE tasks;
   ANALYZE daily_analytics;
   ```

4. **Rewrite Query**
   - Use CTEs for complex queries
   - Avoid N+1 queries
   - Use appropriate JOINs

---

### Cache Optimization

**Monitor Cache Performance**:

```bash
# Check hit rate
redis-cli info stats | grep keyspace_hits
redis-cli info stats | grep keyspace_misses

# Calculate hit rate
python -c "
import redis
r = redis.Redis()
info = r.info('stats')
hits = info['keyspace_hits']
misses = info['keyspace_misses']
rate = hits / (hits + misses) * 100 if (hits + misses) > 0 else 0
print(f'Cache hit rate: {rate:.2f}%')
"
```

**Target**: Cache hit rate > 80%

**Optimization Actions**:

1. **Increase TTL for Stable Data**
   ```python
   # Increase cache TTL for rarely changing metrics
   CACHE_TTL_OVERVIEW = 600  # 10 minutes instead of 5
   ```

2. **Implement Cache Warming**
   ```bash
   # Warm cache for top users
   python -m jobs.cache_warming --top-users=1000
   ```

3. **Add Cache Layers**
   ```python
   # Add application-level cache
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def get_user_stats(user_id):
       # ...
   ```

4. **Optimize Cache Keys**
   ```python
   # Use consistent, predictable keys
   CACHE_KEY = f"analytics:overview:{user_id}:{date}"
   ```

---

### Database Optimization

**Regular Maintenance**:

```sql
-- Vacuum and analyze
VACUUM ANALYZE tasks;
VACUUM ANALYZE daily_analytics;

-- Reindex if needed
REINDEX TABLE CONCURRENTLY tasks;

-- Update statistics
ANALYZE;
```

**Connection Pooling**:

```python
# Configure connection pool
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**Query Optimization**:

1. Use prepared statements
2. Batch operations where possible
3. Use appropriate isolation levels
4. Avoid long-running transactions

---

## Database Maintenance

### Weekly Maintenance

**Schedule**: Every Sunday at 2:00 AM UTC

**Tasks**:

1. **Vacuum and Analyze**
   ```sql
   VACUUM ANALYZE;
   ```

2. **Reindex if Bloated**
   ```sql
   -- Check index bloat
   SELECT
       schemaname,
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

   -- Reindex if needed
   REINDEX TABLE CONCURRENTLY tasks;
   ```

3. **Update Statistics**
   ```sql
   ANALYZE;
   ```

4. **Check for Deadlocks**
   ```sql
   SELECT * FROM pg_stat_database WHERE datname = 'analytics';
   ```

---

### Monthly Maintenance

**Schedule**: First Sunday of month at 2:00 AM UTC

**Tasks**:

1. **Archive Old Data**
   ```sql
   -- Archive analytics older than 2 years
   INSERT INTO daily_analytics_archive
   SELECT * FROM daily_analytics
   WHERE date < CURRENT_DATE - INTERVAL '2 years';

   DELETE FROM daily_analytics
   WHERE date < CURRENT_DATE - INTERVAL '2 years';
   ```

2. **Rebuild Indexes**
   ```sql
   REINDEX DATABASE CONCURRENTLY analytics;
   ```

3. **Check Table Bloat**
   ```sql
   SELECT
       schemaname,
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
       pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   ```

4. **Review and Optimize Queries**
   ```sql
   -- Reset statistics
   SELECT pg_stat_statements_reset();
   ```

---

## Cache Management

### Cache Warming

**Purpose**: Pre-populate cache for active users to improve response times.

**Schedule**: Every 6 hours

**Procedure**:

```bash
# Run cache warming job
python -m jobs.cache_warming

# Monitor progress
tail -f /var/log/jobs/cache_warming.log

# Verify completion
redis-cli DBSIZE
```

**Configuration**:

```python
# jobs/cache_warming.py
ACTIVE_USER_THRESHOLD_DAYS = 7  # Users active in last 7 days
BATCH_SIZE = 10  # Process 10 users at a time
METRICS_TO_CACHE = [
    'task_totals',
    'completion_rate',
    'priority_distribution',
    'status_distribution',
    'productivity_score'
]
```

---

### Cache Invalidation

**When to Invalidate**:

1. **Task Created/Updated/Deleted**
   ```python
   # Invalidate user's cache
   invalidate_user_cache(user_id)
   ```

2. **Manual Invalidation**
   ```bash
   # Invalidate specific user
   redis-cli DEL "analytics:overview:{user_id}"

   # Invalidate all analytics cache
   redis-cli KEYS "analytics:*" | xargs redis-cli DEL
   ```

3. **Scheduled Invalidation**
   ```bash
   # Clear old cache entries (TTL expired)
   redis-cli --scan --pattern "analytics:*" | while read key; do
       ttl=$(redis-cli TTL "$key")
       if [ "$ttl" -eq "-1" ]; then
           redis-cli DEL "$key"
       fi
   done
   ```

---

### Cache Monitoring

**Metrics to Track**:

```bash
# Hit rate
redis-cli info stats | grep keyspace_hits
redis-cli info stats | grep keyspace_misses

# Memory usage
redis-cli info memory | grep used_memory_human

# Key count
redis-cli DBSIZE

# Evicted keys
redis-cli info stats | grep evicted_keys
```

**Alerts**:
- Hit rate < 70%: Investigate cache strategy
- Memory > 80%: Increase memory or reduce TTL
- Evicted keys > 1000/hour: Increase memory

---

## Monitoring and Alerting

### Key Metrics

**Application Metrics**:
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (errors/second)
- Cache hit rate (%)

**Database Metrics**:
- Active connections
- Query execution time
- Deadlocks
- Disk usage

**System Metrics**:
- CPU usage (%)
- Memory usage (%)
- Disk I/O
- Network traffic

---

### Alert Thresholds

**Critical Alerts** (P0):
```yaml
- name: API Down
  condition: health_check_failed for 2 minutes
  action: Page on-call engineer

- name: Database Unreachable
  condition: db_connection_failed for 1 minute
  action: Page on-call engineer

- name: High Error Rate
  condition: error_rate > 10% for 5 minutes
  action: Page on-call engineer
```

**Warning Alerts** (P1):
```yaml
- name: Slow Response Time
  condition: p95_response_time > 5s for 10 minutes
  action: Notify team channel

- name: High CPU Usage
  condition: cpu_usage > 80% for 15 minutes
  action: Notify team channel

- name: Low Cache Hit Rate
  condition: cache_hit_rate < 70% for 30 minutes
  action: Notify team channel
```

**Info Alerts** (P2):
```yaml
- name: Background Job Failed
  condition: job_failed
  action: Create ticket

- name: Disk Space Low
  condition: disk_usage > 80%
  action: Create ticket
```

---

### Monitoring Dashboard

**Key Panels**:

1. **Overview**
   - Request rate
   - Error rate
   - Response time (p95)
   - Active users

2. **Performance**
   - Response time distribution
   - Slow queries
   - Cache hit rate
   - Database query time

3. **Resources**
   - CPU usage
   - Memory usage
   - Database connections
   - Disk I/O

4. **Business Metrics**
   - Analytics requests per user
   - Export requests
   - Most accessed endpoints
   - User growth

---

## Backup and Recovery

### Backup Strategy

**Database Backups**:

```bash
# Daily full backup
pg_dump $DATABASE_URL > /backups/analytics_$(date +%Y%m%d).sql

# Compress backup
gzip /backups/analytics_$(date +%Y%m%d).sql

# Upload to S3
aws s3 cp /backups/analytics_$(date +%Y%m%d).sql.gz s3://backups/analytics/
```

**Schedule**:
- Full backup: Daily at 3:00 AM UTC
- Incremental backup: Every 6 hours
- Retention: 30 days

**Verification**:

```bash
# Test restore on staging
pg_restore -d staging_db /backups/analytics_latest.sql

# Verify data integrity
psql staging_db -c "SELECT COUNT(*) FROM tasks;"
```

---

### Recovery Procedures

**Scenario 1: Data Corruption**

1. **Identify Scope**
   ```sql
   -- Check for corrupted data
   SELECT * FROM daily_analytics
   WHERE completion_rate > 100 OR completion_rate < 0;
   ```

2. **Restore from Backup**
   ```bash
   # Stop application
   systemctl stop analytics-api

   # Restore database
   pg_restore -d analytics_db /backups/analytics_latest.sql

   # Restart application
   systemctl start analytics-api
   ```

3. **Verify Recovery**
   ```sql
   -- Check data integrity
   SELECT COUNT(*) FROM tasks;
   SELECT COUNT(*) FROM daily_analytics;
   ```

**Scenario 2: Accidental Deletion**

1. **Identify Deleted Data**
   ```sql
   -- Check audit logs
   SELECT * FROM audit_log
   WHERE action = 'DELETE'
     AND timestamp > NOW() - INTERVAL '1 hour';
   ```

2. **Restore Specific Data**
   ```bash
   # Extract specific table from backup
   pg_restore -t tasks /backups/analytics_latest.sql > tasks_backup.sql

   # Restore deleted records
   psql analytics_db < tasks_backup.sql
   ```

---

## Troubleshooting Guide

### Issue: Slow Analytics Queries

**Symptoms**:
- Response times > 5 seconds
- Timeout errors
- High database CPU

**Diagnosis**:

```sql
-- Check for missing indexes
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public';

-- Check query plans
EXPLAIN ANALYZE
SELECT * FROM tasks WHERE user_id = 'xxx';
```

**Solutions**:

1. Add missing indexes
2. Refresh materialized views
3. Update statistics
4. Optimize query

---

### Issue: Cache Not Working

**Symptoms**:
- Low cache hit rate
- Repeated database queries
- Slow response times

**Diagnosis**:

```bash
# Check Redis status
redis-cli ping

# Check cache keys
redis-cli KEYS "analytics:*"

# Check TTL
redis-cli TTL "analytics:overview:user123"
```

**Solutions**:

1. Restart Redis if down
2. Verify cache key format
3. Check TTL configuration
4. Warm cache manually

---

### Issue: Background Jobs Not Running

**Symptoms**:
- Missing daily analytics data
- Stale materialized views
- Empty cache

**Diagnosis**:

```bash
# Check cron jobs
crontab -l

# Check job logs
tail -n 100 /var/log/jobs/*.log

# Check for errors
grep ERROR /var/log/jobs/*.log
```

**Solutions**:

1. Verify cron schedule
2. Check job permissions
3. Run job manually
4. Fix underlying errors

---

## Emergency Procedures

### Emergency Contacts

**On-Call Engineer**: +1-XXX-XXX-XXXX
**Team Lead**: +1-XXX-XXX-XXXX
**Database Admin**: +1-XXX-XXX-XXXX

### Emergency Rollback

```bash
# Stop application
systemctl stop analytics-api

# Rollback code
git checkout <previous-stable-commit>

# Rollback database
psql $DATABASE_URL < /backups/pre_deployment.sql

# Restart application
systemctl start analytics-api

# Verify
curl https://api.example.com/health
```

### Emergency Shutdown

```bash
# Stop all services
systemctl stop analytics-api
systemctl stop redis
systemctl stop postgresql

# Notify stakeholders
python -m scripts.send_emergency_notification --message="System shutdown for emergency maintenance"
```

---

## Appendix

### Useful Commands

```bash
# Check system status
systemctl status analytics-api

# View logs
journalctl -u analytics-api -f

# Database connection
psql $DATABASE_URL

# Redis connection
redis-cli

# Run background job
python -m jobs.daily_aggregation

# Clear cache
redis-cli FLUSHDB

# Restart services
systemctl restart analytics-api
```

### Configuration Files

- Application: `/etc/analytics/config.yml`
- Database: `/etc/postgresql/postgresql.conf`
- Redis: `/etc/redis/redis.conf`
- Nginx: `/etc/nginx/sites-available/analytics`

### Log Locations

- Application: `/var/log/app/analytics.log`
- Error: `/var/log/app/error.log`
- Access: `/var/log/app/access.log`
- Jobs: `/var/log/jobs/*.log`
- Database: `/var/log/postgresql/postgresql.log`
