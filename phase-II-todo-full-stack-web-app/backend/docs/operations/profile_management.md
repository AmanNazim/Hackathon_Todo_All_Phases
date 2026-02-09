# Profile Management Operations Runbook

## Daily Operations

### Health Checks
```bash
# Check API health
curl https://api.example.com/health

# Check profile endpoint
curl -H "Authorization: Bearer $TOKEN" \
  https://api.example.com/api/v1/users/$USER_ID/profile

# Check database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM user_preferences;"
```

---

## Profile Recovery

### Recover User Profile Data
```sql
-- View user profile
SELECT id, email, display_name, bio, avatar_url, created_at, last_login_at
FROM users
WHERE id = 'user-uuid';

-- Check preferences
SELECT * FROM user_preferences
WHERE user_id = 'user-uuid';
```

### Restore Deleted Avatar
```bash
# If avatar was accidentally deleted, restore from backup
aws s3 cp s3://backups/avatars/user-uuid/avatar.jpg \
  s3://production/avatars/user-uuid/avatar.jpg
```

### Reset Privacy Settings
```sql
-- Reset to default privacy settings
UPDATE user_preferences
SET privacy = '{"profile_visibility": "public", "show_email": false, "show_activity": true}'::jsonb
WHERE user_id = 'user-uuid';
```

---

## Bulk Operations

### Update Multiple User Preferences
```sql
-- Set all users to dark theme
UPDATE user_preferences
SET theme = 'dark'
WHERE theme = 'light';

-- Enable email notifications for all users
UPDATE user_preferences
SET notifications = jsonb_set(notifications, '{email}', 'true')
WHERE notifications->>'email' = 'false';
```

### Cleanup Orphaned Data
```sql
-- Find preferences without users
SELECT up.user_id
FROM user_preferences up
LEFT JOIN users u ON up.user_id = u.id
WHERE u.id IS NULL;

-- Delete orphaned preferences
DELETE FROM user_preferences
WHERE user_id NOT IN (SELECT id FROM users);
```

---

## Avatar Management

### Check Avatar Storage Usage
```bash
# Check total storage used
aws s3 ls s3://production/avatars/ --recursive --summarize

# Check user's avatar files
aws s3 ls s3://production/avatars/user-uuid/
```

### Migrate Avatars to New Storage
```bash
# Migrate from old to new storage provider
for user_id in $(psql $DATABASE_URL -t -c "SELECT id FROM users WHERE avatar_url IS NOT NULL;"); do
  aws s3 cp s3://old-bucket/avatars/$user_id/ \
    s3://new-bucket/avatars/$user_id/ --recursive
done
```

### Regenerate Avatar Thumbnails
```python
# Script to regenerate thumbnails
from PIL import Image
import boto3

s3 = boto3.client('s3')

def regenerate_thumbnail(user_id):
    # Download original
    s3.download_file('bucket', f'avatars/{user_id}/original.jpg', 'temp.jpg')

    # Generate thumbnail
    img = Image.open('temp.jpg')
    img.thumbnail((200, 200))
    img.save('thumb.jpg')

    # Upload thumbnail
    s3.upload_file('thumb.jpg', 'bucket', f'avatars/{user_id}/thumbnail.jpg')
```

---

## Privacy Enforcement

### Verify Privacy Settings
```sql
-- Check users with private profiles
SELECT COUNT(*) FROM user_preferences
WHERE privacy->>'profile_visibility' = 'private';

-- Check users with public email
SELECT COUNT(*) FROM user_preferences
WHERE privacy->>'show_email' = 'true';

-- Find users with no privacy settings
SELECT u.id, u.email
FROM users u
LEFT JOIN user_preferences up ON u.id = up.user_id
WHERE up.user_id IS NULL;
```

### Audit Privacy Access
```sql
-- Check recent profile access attempts (if logging enabled)
SELECT user_id, target_user_id, action, result, timestamp
FROM audit_log
WHERE action = 'view_profile'
AND result = 'denied'
ORDER BY timestamp DESC
LIMIT 100;
```

---

## Performance Optimization

### Analyze Query Performance
```sql
-- Check slow profile queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%users%' OR query LIKE '%user_preferences%'
AND mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Update Statistics
```sql
ANALYZE users;
ANALYZE user_preferences;
```

### Check Index Usage
```sql
-- Verify indexes are being used
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename IN ('users', 'user_preferences')
ORDER BY idx_scan DESC;
```

---

## Troubleshooting

### Profile Not Loading
1. Check user exists: `SELECT * FROM users WHERE id = 'uuid';`
2. Check database connection
3. Verify API endpoint is responding
4. Check authentication token is valid
5. Review application logs

### Avatar Upload Failing
1. Check storage service status
2. Verify file size limits
3. Check file format validation
4. Review storage credentials
5. Check disk space/quota

### Privacy Settings Not Working
1. Verify settings saved: `SELECT privacy FROM user_preferences WHERE user_id = 'uuid';`
2. Check middleware is enabled
3. Review application logs
4. Test with different users
5. Clear cache if applicable

### Preferences Not Saving
1. Check database connection
2. Verify user_id exists
3. Check JSON format is valid
4. Review validation errors
5. Check database constraints

---

## Monitoring

### Key Metrics
- Profile view rate
- Profile update rate
- Avatar upload success rate
- Privacy setting changes
- API response time (p95 < 1.5s)

### Alerts
- Response time > 2s (warning)
- Response time > 5s (critical)
- Error rate > 1% (warning)
- Error rate > 5% (critical)
- Storage usage > 80% (warning)

### Dashboard Queries
```sql
-- Profile completion stats
SELECT
  CASE
    WHEN display_name IS NOT NULL AND bio IS NOT NULL AND avatar_url IS NOT NULL THEN 'complete'
    WHEN display_name IS NOT NULL OR bio IS NOT NULL OR avatar_url IS NOT NULL THEN 'partial'
    ELSE 'empty'
  END as completion,
  COUNT(*) as count
FROM users
GROUP BY completion;

-- Privacy distribution
SELECT
  privacy->>'profile_visibility' as visibility,
  COUNT(*) as count
FROM user_preferences
GROUP BY visibility;
```

---

## Backup & Recovery

### Backup User Data
```bash
# Backup users table
pg_dump $DATABASE_URL -t users > users_backup.sql

# Backup preferences
pg_dump $DATABASE_URL -t user_preferences > preferences_backup.sql

# Backup avatars
aws s3 sync s3://production/avatars/ ./avatars_backup/
```

### Restore User Data
```bash
# Restore users
psql $DATABASE_URL < users_backup.sql

# Restore preferences
psql $DATABASE_URL < preferences_backup.sql

# Restore avatars
aws s3 sync ./avatars_backup/ s3://production/avatars/
```

---

## Common Issues

**Issue**: User can't update profile
**Solution**: Check user_id matches token, verify permissions

**Issue**: Avatar not displaying
**Solution**: Check avatar_url is valid, verify storage access, check CDN

**Issue**: Privacy settings ignored
**Solution**: Verify middleware enabled, check settings saved, clear cache

**Issue**: Slow profile loading
**Solution**: Check database indexes, optimize queries, enable caching

---

## Emergency Procedures

### Mass Privacy Update
```sql
-- Emergency: Set all profiles to private
UPDATE user_preferences
SET privacy = jsonb_set(privacy, '{profile_visibility}', '"private"')
WHERE privacy->>'profile_visibility' != 'private';
```

### Disable Avatar Uploads
```python
# In application config
AVATAR_UPLOADS_ENABLED = False
```

### Clear Corrupted Data
```sql
-- Find and fix corrupted JSON
UPDATE user_preferences
SET privacy = '{"profile_visibility": "public", "show_email": false, "show_activity": true}'::jsonb
WHERE privacy IS NULL OR NOT jsonb_typeof(privacy) = 'object';
```
