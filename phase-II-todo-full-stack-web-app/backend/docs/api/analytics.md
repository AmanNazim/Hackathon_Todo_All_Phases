# Analytics API Documentation

## Overview

The Analytics API provides comprehensive insights into task management metrics, trends, and productivity scores. All endpoints require authentication and enforce user isolation.

**Base URL**: `/api/v1/users/{user_id}/analytics`

**Authentication**: Bearer token required in `Authorization` header

---

## Endpoints

### 1. Get Analytics Overview

Get a comprehensive overview of all analytics metrics.

**Endpoint**: `GET /api/v1/users/{user_id}/analytics/overview`

**Parameters**:
- `user_id` (path, required): UUID of the user

**Response** (200 OK):
```json
{
  "total": 150,
  "completed": 105,
  "pending": 30,
  "in_progress": 15,
  "completion_rate": 70.0,
  "overdue": 8,
  "by_priority": {
    "high": 25,
    "medium": 75,
    "low": 50
  },
  "by_status": {
    "todo": 30,
    "in_progress": 15,
    "done": 105
  },
  "productivity_score": 78.5
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User attempting to access another user's analytics
- `404 Not Found`: User not found

**Example**:
```bash
curl -X GET "https://api.example.com/api/v1/users/123e4567-e89b-12d3-a456-426614174000/analytics/overview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. Get Trends

Retrieve analytics trends over a specified time period.

**Endpoint**: `GET /api/v1/users/{user_id}/analytics/trends`

**Parameters**:
- `user_id` (path, required): UUID of the user
- `period` (query, required): Aggregation period - `daily`, `weekly`, or `monthly`
- `start_date` (query, required): Start date in ISO 8601 format (YYYY-MM-DD)
- `end_date` (query, required): End date in ISO 8601 format (YYYY-MM-DD)

**Response** (200 OK):
```json
[
  {
    "date": "2024-01-01",
    "tasks_created": 15,
    "tasks_completed": 12,
    "completion_rate": 80.0,
    "productivity_score": 75.5
  },
  {
    "date": "2024-01-02",
    "tasks_created": 20,
    "tasks_completed": 18,
    "completion_rate": 90.0,
    "productivity_score": 82.3
  }
]
```

**Error Responses**:
- `400 Bad Request`: Invalid period or date format, or end_date before start_date
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User attempting to access another user's analytics

**Example**:
```bash
curl -X GET "https://api.example.com/api/v1/users/123e4567-e89b-12d3-a456-426614174000/analytics/trends?period=daily&start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. Get Completion Rate

Get the overall task completion rate.

**Endpoint**: `GET /api/v1/users/{user_id}/analytics/completion-rate`

**Parameters**:
- `user_id` (path, required): UUID of the user

**Response** (200 OK):
```json
{
  "rate": 70.5,
  "total_tasks": 150,
  "completed_tasks": 105,
  "pending_tasks": 45
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User attempting to access another user's analytics

---

### 4. Get Priority Distribution

Get the distribution of tasks by priority level.

**Endpoint**: `GET /api/v1/users/{user_id}/analytics/priority-distribution`

**Parameters**:
- `user_id` (path, required): UUID of the user

**Response** (200 OK):
```json
{
  "high": 25,
  "medium": 75,
  "low": 50,
  "total": 150
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User attempting to access another user's analytics

---

### 5. Get Due Date Adherence

Get metrics on how well tasks are completed by their due dates.

**Endpoint**: `GET /api/v1/users/{user_id}/analytics/due-date-adherence`

**Parameters**:
- `user_id` (path, required): UUID of the user
- `period` (query, optional): Time period - `30days`, `90days`, or `year` (default: `30days`)

**Response** (200 OK):
```json
{
  "adherence_rate": 85.5,
  "on_time": 95,
  "late": 16,
  "total_with_due_dates": 111,
  "average_delay_days": 2.3
}
```

**Error Responses**:
- `400 Bad Request`: Invalid period parameter
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User attempting to access another user's analytics

---

### 6. Get Productivity Score

Get the calculated productivity score based on multiple metrics.

**Endpoint**: `GET /api/v1/users/{user_id}/analytics/productivity-score`

**Parameters**:
- `user_id` (path, required): UUID of the user

**Response** (200 OK):
```json
{
  "score": 78.5,
  "components": {
    "completion_rate": 70.0,
    "adherence_rate": 85.5,
    "velocity": 12.5,
    "consistency": 80.0
  },
  "trend": "up",
  "previous_score": 75.2
}
```

**Metric Breakdown**:
- `score`: Overall productivity score (0-100)
- `completion_rate`: Percentage of tasks completed
- `adherence_rate`: Percentage of tasks completed on time
- `velocity`: Average tasks completed per week
- `consistency`: Measure of consistent task completion over time
- `trend`: Direction of change - `up`, `down`, or `stable`

**Error Responses**:
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User attempting to access another user's analytics

---

### 7. Export Analytics Data

Export analytics data in CSV or JSON format.

**Endpoint**: `GET /api/v1/users/{user_id}/analytics/export`

**Parameters**:
- `user_id` (path, required): UUID of the user
- `format` (query, required): Export format - `csv` or `json`
- `start_date` (query, optional): Start date for filtering (ISO 8601)
- `end_date` (query, optional): End date for filtering (ISO 8601)

**Response** (200 OK):

For `format=json`:
```json
[
  {
    "id": "task-1",
    "title": "Complete project",
    "status": "done",
    "priority": "high",
    "created_at": "2024-01-01T10:00:00Z",
    "completed_at": "2024-01-05T15:30:00Z",
    "due_date": "2024-01-10T00:00:00Z",
    "completion_time_days": 4.23
  }
]
```

For `format=csv`:
```csv
id,title,status,priority,created_at,completed_at,due_date,completion_time_days
task-1,Complete project,done,high,2024-01-01T10:00:00Z,2024-01-05T15:30:00Z,2024-01-10T00:00:00Z,4.23
```

**Headers**:
- `Content-Type`: `application/json` or `text/csv`
- `Content-Disposition`: `attachment; filename="analytics-export-{timestamp}.{format}"`

**Error Responses**:
- `400 Bad Request`: Invalid format parameter
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User attempting to access another user's analytics

**Example**:
```bash
curl -X GET "https://api.example.com/api/v1/users/123e4567-e89b-12d3-a456-426614174000/analytics/export?format=csv&start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o analytics-export.csv
```

---

## Rate Limiting

All analytics endpoints are rate-limited to prevent abuse:

- **Overview, Completion Rate, Priority Distribution**: 60 requests per minute
- **Trends, Due Date Adherence, Productivity Score**: 30 requests per minute
- **Export**: 10 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

---

## Caching

Analytics data is cached to improve performance:

- **Overview metrics**: 5 minutes
- **Trends data**: 15 minutes
- **Productivity score**: 10 minutes
- **Export data**: Not cached

Cache headers are included in responses:
```
Cache-Control: public, max-age=300
ETag: "abc123def456"
```

Use `If-None-Match` header with ETag value to receive `304 Not Modified` for unchanged data.

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": "ErrorType",
  "detail": "Human-readable error message",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Common Error Types**:
- `AuthenticationError`: Invalid or missing authentication
- `AuthorizationError`: Insufficient permissions
- `ValidationError`: Invalid request parameters
- `NotFoundError`: Resource not found
- `RateLimitError`: Rate limit exceeded

---

## Performance Considerations

### Response Times

Expected response times under normal load:

- **Overview**: < 500ms
- **Trends**: < 1s (varies with date range)
- **Completion Rate**: < 200ms
- **Priority Distribution**: < 200ms
- **Due Date Adherence**: < 500ms
- **Productivity Score**: < 800ms
- **Export**: < 5s (varies with data volume)

### Large Datasets

For users with 10,000+ tasks:

- Use pagination where available
- Consider narrower date ranges for trends
- Export data in batches if needed
- Monitor response times and adjust queries

### Optimization Tips

1. **Use appropriate time periods**: Request only the data you need
2. **Leverage caching**: Reuse cached responses when possible
3. **Batch requests**: Combine multiple metrics in overview endpoint
4. **Monitor rate limits**: Implement exponential backoff for retries

---

## Webhooks (Future)

Analytics webhooks will be available in a future release to notify applications of:

- Significant productivity score changes
- Completion rate milestones
- Overdue task thresholds

---

## Support

For API support, contact:
- Email: api-support@example.com
- Documentation: https://docs.example.com/analytics
- Status Page: https://status.example.com
