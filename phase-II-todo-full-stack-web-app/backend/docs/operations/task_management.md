# Task Management Operations Runbook

## Daily Operations

### Health Checks
```bash
# Check API health
curl https://api.example.com/health

# Check database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM tasks;"

# Check search indexes
psql $DATABASE_URL -c "SELECT schemaname, tablename, indexname FROM pg_indexes WHERE tablename='tasks';"
```

---

## Task Recovery

### Recover Soft-Deleted Tasks
```sql
-- View deleted tasks (within 30 days)
SELECT id, title, deleted_at FROM tasks
WHERE deleted = true AND deleted_at > NOW() - INTERVAL '30 days';

-- Restore task
UPDATE tasks SET deleted = false, deleted_at = NULL
WHERE id = 'task-uuid';
```

---

## Bulk Operations

### Cleanup Old Deleted Tasks
```sql
-- Delete tasks older than 30 days
DELETE FROM tasks
WHERE deleted = true AND deleted_at < NOW() - INTERVAL '30 days';
```

### Cleanup Old History
```sql
-- Delete history older than 90 days
DELETE FROM task_history
WHERE created_at < NOW() - INTERVAL '90 days';
```

---

## Performance Optimization

### Rebuild Search Indexes
```sql
REINDEX INDEX CONCURRENTLY idx_tasks_search_vector;
```

### Update Statistics
```sql
ANALYZE tasks;
ANALYZE task_tags;
ANALYZE task_history;
```

### Check Slow Queries
```sql
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%tasks%' AND mean_exec_time > 100
ORDER BY mean_exec_time DESC LIMIT 10;
```

---

## Troubleshooting

### Search Not Working
1. Check search_vector column exists
2. Rebuild search index
3. Update table statistics

### Slow Queries
1. Check index usage: `EXPLAIN ANALYZE SELECT ...`
2. Verify indexes exist
3. Update statistics
4. Consider adding indexes

### High Database Load
1. Check active connections
2. Identify slow queries
3. Enable connection pooling
4. Scale database if needed

---

## Monitoring

### Key Metrics
- Task creation rate
- Search query time
- Database connections
- API response time

### Alerts
- Response time > 1s
- Error rate > 1%
- Database connections > 80%
- Disk usage > 80%

---

## Backup & Recovery

### Backup Tasks
```bash
# Backup tasks table
pg_dump $DATABASE_URL -t tasks > tasks_backup.sql

# Restore
psql $DATABASE_URL < tasks_backup.sql
```

---

## Common Issues

**Issue**: Search returns no results
**Solution**: Rebuild search index, check search_vector column

**Issue**: Batch operations timeout
**Solution**: Reduce batch size, increase timeout

**Issue**: Tags not appearing
**Solution**: Check task_tags table, verify foreign keys

**Issue**: History not tracking
**Solution**: Check triggers, verify task_history table
