# User Profile Production Configuration

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Storage (S3/Cloudinary)
STORAGE_PROVIDER=s3  # or cloudinary
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_BUCKET_NAME=production-avatars
CLOUDINARY_URL=cloudinary://key:secret@cloud_name

# Image Processing
MAX_AVATAR_SIZE_MB=5
AVATAR_FORMATS=jpeg,png,webp
AVATAR_OPTIMIZED_SIZE=800
AVATAR_THUMBNAIL_SIZE=200
IMAGE_QUALITY=85

# Profile Settings
MAX_DISPLAY_NAME_LENGTH=100
MAX_BIO_LENGTH=500
PROFILE_CACHE_TTL=300

# Privacy
DEFAULT_PROFILE_VISIBILITY=public
DEFAULT_SHOW_EMAIL=false
DEFAULT_SHOW_ACTIVITY=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
PROFILE_UPDATE_RATE_LIMIT=60  # per minute
AVATAR_UPLOAD_RATE_LIMIT=10   # per hour

# Security
ENABLE_XSS_PROTECTION=true
ENABLE_INPUT_SANITIZATION=true
```

---

## Database Setup

### Required Tables
```sql
-- Users table (should already exist from auth)
-- Add profile fields if not present
ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_thumbnail_url TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en',
    notifications JSONB DEFAULT '{"email": true, "push": false, "task_reminders": true, "task_assignments": true}'::jsonb,
    privacy JSONB DEFAULT '{"profile_visibility": "public", "show_email": false, "show_activity": true}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_display_name ON users(display_name);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_privacy ON user_preferences USING gin(privacy);
```

### Run Migrations
```bash
alembic upgrade head
```

---

## Storage Configuration

### AWS S3 Setup
```bash
# Create S3 bucket
aws s3 mb s3://production-avatars

# Set bucket policy
aws s3api put-bucket-policy --bucket production-avatars --policy file://bucket-policy.json

# Enable CORS
aws s3api put-bucket-cors --bucket production-avatars --cors-configuration file://cors.json
```

**bucket-policy.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::production-avatars/*"
    }
  ]
}
```

**cors.json:**
```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://yourdomain.com"],
      "AllowedMethods": ["GET", "PUT", "POST"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

### Cloudinary Setup
```bash
# Set environment variable
export CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Configure upload preset (in Cloudinary dashboard)
# - Folder: avatars
# - Format: auto
# - Quality: auto:good
# - Transformations: c_fill,g_face,h_800,w_800
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
  --log-level info \
  --access-log
```

### Systemd Service
```ini
[Unit]
Description=Profile Management API
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

## CDN Configuration

### CloudFront Setup (for S3)
```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name production-avatars.s3.amazonaws.com \
  --default-root-object index.html

# Update avatar URLs to use CDN
# https://d1234567890.cloudfront.net/avatars/user-uuid/avatar.jpg
```

### Cache Settings
- **Avatars**: Cache for 1 year (immutable)
- **Thumbnails**: Cache for 1 year (immutable)
- **Profile data**: Cache for 5 minutes

---

## Monitoring

### Key Metrics
- Profile view rate
- Profile update success rate
- Avatar upload success rate
- Avatar processing time
- Privacy setting changes
- API response time (p95 < 1.5s)
- Storage usage

### Health Checks
```bash
# API health
curl https://api.example.com/health

# Profile endpoint
curl -H "Authorization: Bearer $TOKEN" \
  https://api.example.com/api/v1/users/$USER_ID/profile

# Database health
curl https://api.example.com/ready
```

### Alerts
- Response time > 2s (warning)
- Response time > 5s (critical)
- Error rate > 1% (warning)
- Error rate > 5% (critical)
- Storage usage > 80% (warning)
- Avatar upload failures > 10% (critical)

---

## Security

### Input Validation
- Display name: max 100 chars, XSS sanitization
- Bio: max 500 chars, XSS sanitization
- Avatar: max 5MB, format validation, content validation

### Rate Limiting
- Profile updates: 60 req/min
- Avatar uploads: 10 req/hour
- Preference updates: 60 req/min

### Privacy Enforcement
- Server-side validation
- Middleware enforcement
- No client-side bypass possible

### File Upload Security
- File type validation (magic bytes)
- File size limits
- Virus scanning (optional)
- Content validation
- Secure storage with signed URLs

---

## Backup Strategy

### Daily Backups
```bash
# Backup users and preferences
pg_dump $DATABASE_URL -t users -t user_preferences > backup.sql

# Backup avatars
aws s3 sync s3://production-avatars/ s3://backups/avatars/$(date +%Y%m%d)/

# Upload to backup storage
aws s3 cp backup.sql s3://backups/database/$(date +%Y%m%d).sql
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
- [ ] Storage provider configured (S3/Cloudinary)
- [ ] CDN configured for avatars
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Backups configured
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] CORS configured
- [ ] Load testing completed
- [ ] Documentation updated

---

## Performance Tuning

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login_at);

-- Analyze tables
ANALYZE users;
ANALYZE user_preferences;
```

### Caching Strategy
- Profile data: 5 minutes
- Preferences: 5 minutes
- Avatar URLs: 1 year (immutable)
- Privacy settings: No cache (immediate enforcement)

### Connection Pooling
```python
# SQLAlchemy settings
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 10
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 3600
```

---

## Scaling Considerations

### Horizontal Scaling
- Stateless application servers
- Load balancer distribution
- Session management via JWT
- Shared storage (S3/Cloudinary)

### Database Scaling
- Read replicas for profile reads
- Connection pooling
- Query optimization
- Proper indexing

### Storage Scaling
- CDN for avatar delivery
- Multiple regions for S3
- Cloudinary auto-scaling
- Image optimization

---

## Rollback Procedures

### Application Rollback
```bash
# Rollback to previous version
git checkout previous-tag
docker build -t app:rollback .
kubectl set image deployment/app app=app:rollback
```

### Database Rollback
```bash
# Rollback migration
alembic downgrade -1

# Restore from backup
psql $DATABASE_URL < backup.sql
```

### Storage Rollback
```bash
# Restore avatars from backup
aws s3 sync s3://backups/avatars/20240115/ s3://production-avatars/
```
