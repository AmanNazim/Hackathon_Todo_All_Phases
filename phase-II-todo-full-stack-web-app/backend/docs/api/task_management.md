# Task Management API Documentation

## Overview
Task management endpoints for creating, organizing, and tracking tasks.

**Base URL**: `/api/v1/users/{user_id}/tasks`
**Authentication**: Required (Bearer token)

---

## Endpoints

### Create Task
```
POST /api/v1/users/{user_id}/tasks
```

**Request Body**:
```json
{
  "title": "Task title (required)",
  "description": "Task description",
  "priority": "low|medium|high|urgent",
  "status": "todo|in_progress|review|done|blocked",
  "due_date": "2024-12-31T23:59:59Z"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "title": "Task title",
  "status": "todo",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### List Tasks
```
GET /api/v1/users/{user_id}/tasks
```

**Query Parameters**:
- `search`: Search in title/description
- `status`: Filter by status
- `priority`: Filter by priority
- `tags`: Filter by tags (comma-separated)
- `sort`: Sort field (due_date, priority, created_at)
- `order`: asc or desc
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response** (200):
```json
{
  "tasks": [...],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

---

### Get Task
```
GET /api/v1/users/{user_id}/tasks/{task_id}
```

**Response** (200): Task object with all fields

---

### Update Task
```
PUT /api/v1/users/{user_id}/tasks/{task_id}
```

**Request Body**: Any task fields to update

---

### Delete Task
```
DELETE /api/v1/users/{user_id}/tasks/{task_id}
```

**Response** (204): No content (soft delete)

---

### Complete Task
```
PATCH /api/v1/users/{user_id}/tasks/{task_id}/complete
```

**Response** (200): Updated task with `completed_at` timestamp

---

### Batch Operations
```
POST /api/v1/users/{user_id}/tasks/batch
```

**Request Body**:
```json
{
  "task_ids": ["uuid1", "uuid2"],
  "operation": "update_status|delete|add_tags|remove_tags",
  "status": "done",
  "tags": ["urgent", "work"]
}
```

**Response** (200):
```json
{
  "updated": 10,
  "failed": 0,
  "errors": []
}
```

---

## Tag Management

### Add Tags
```
POST /api/v1/users/{user_id}/tasks/{task_id}/tags
```

**Request**: `{"tags": ["work", "urgent"]}`

### Remove Tag
```
DELETE /api/v1/users/{user_id}/tasks/{task_id}/tags
```

**Request**: `{"tag": "urgent"}`

### Tag Statistics
```
GET /api/v1/users/{user_id}/tags/statistics
```

**Response**: Tag usage counts

### Tag Autocomplete
```
GET /api/v1/users/{user_id}/tags/autocomplete?q=wor
```

**Response**: Matching tag suggestions

---

## Task History
```
GET /api/v1/users/{user_id}/tasks/{task_id}/history
```

**Response**: List of changes with timestamps

---

## Error Codes

- `400`: Bad request (invalid parameters)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (accessing other user's tasks)
- `404`: Task not found
- `422`: Validation error
- `500`: Server error

---

## Rate Limits

- Standard endpoints: 100 requests/minute
- Batch operations: 20 requests/minute
- Search: 60 requests/minute

---

## Best Practices

1. **Pagination**: Always use pagination for large result sets
2. **Search**: Use full-text search for better performance than client-side filtering
3. **Batch Operations**: Use batch endpoints for multiple updates
4. **Caching**: Results are cached for 5 minutes
5. **Soft Delete**: Deleted tasks can be recovered within 30 days
