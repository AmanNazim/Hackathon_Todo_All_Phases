# User Profile API Documentation

## Overview
RESTful API endpoints for user profile management, preferences, and privacy settings.

---

## Authentication
All endpoints require JWT authentication via Bearer token:
```
Authorization: Bearer <jwt_token>
```

---

## Profile Endpoints

### Get User Profile
```
GET /api/v1/users/{user_id}/profile
```

**Parameters:**
- `user_id` (path): User UUID

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "John Doe",
  "bio": "Software developer",
  "avatar_url": "https://...",
  "avatar_thumbnail_url": "https://...",
  "completion_percentage": 75,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (private profile)
- `404`: User not found

---

### Update User Profile
```
PUT /api/v1/users/{user_id}/profile
```

**Request Body:**
```json
{
  "display_name": "John Doe",
  "bio": "Software developer passionate about building great products"
}
```

**Validation:**
- `display_name`: Max 100 characters
- `bio`: Max 500 characters
- XSS prevention applied

**Response (200):**
```json
{
  "id": "uuid",
  "display_name": "John Doe",
  "bio": "Software developer...",
  "completion_percentage": 80
}
```

**Errors:**
- `401`: Unauthorized
- `403`: Forbidden (not profile owner)
- `422`: Validation error

---

## Preferences Endpoints

### Get User Preferences
```
GET /api/v1/users/{user_id}/preferences
```

**Response (200):**
```json
{
  "theme": "dark",
  "language": "en",
  "notifications": {
    "email": true,
    "push": false,
    "task_reminders": true,
    "task_assignments": true
  },
  "privacy": {
    "profile_visibility": "public",
    "show_email": false,
    "show_activity": true
  }
}
```

**Errors:**
- `401`: Unauthorized
- `403`: Forbidden (not preference owner)

---

### Update User Preferences
```
PUT /api/v1/users/{user_id}/preferences
```

**Request Body:**
```json
{
  "theme": "dark",
  "language": "es",
  "notifications": {
    "email": false,
    "push": true,
    "task_reminders": true,
    "task_assignments": false
  },
  "privacy": {
    "profile_visibility": "private",
    "show_email": false,
    "show_activity": false
  }
}
```

**Valid Values:**
- `theme`: "light", "dark", "system"
- `language`: "en", "es", "fr", "de", "ja", "zh"
- `profile_visibility`: "private", "contacts", "public"
- Notification/privacy booleans: true/false

**Response (200):**
```json
{
  "theme": "dark",
  "language": "es",
  "notifications": {...},
  "privacy": {...}
}
```

**Errors:**
- `401`: Unauthorized
- `403`: Forbidden
- `422`: Invalid values

---

## Privacy Settings

### Profile Visibility Levels

**Private:**
- Only the user can view their profile
- Blocks all other users

**Contacts:**
- Only user's contacts can view profile
- Blocks non-contacts

**Public:**
- Anyone can view profile
- Respects field-level privacy settings

### Field-Level Privacy

**show_email:**
- `true`: Email visible to others (if profile is public/contacts)
- `false`: Email hidden from others

**show_activity:**
- `true`: Created/login timestamps visible
- `false`: Activity timestamps hidden

---

## Profile Completion

Profile completion percentage based on:
- Display name set: 33%
- Bio added: 33%
- Avatar uploaded: 34%

Total: 100% for complete profile

---

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Common HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Missing/invalid authentication
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Rate Limiting

- Standard endpoints: 100 requests/minute
- Profile updates: 60 requests/minute
- Preference updates: 60 requests/minute

Exceeded limits return `429` with retry-after header.

---

## Best Practices

1. **Cache profile data** client-side to reduce API calls
2. **Update incrementally** - only send changed fields
3. **Handle 403 errors** gracefully for private profiles
4. **Respect privacy settings** in UI display
5. **Validate input** client-side before submission
6. **Show completion percentage** to encourage profile setup
