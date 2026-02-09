# Search and Filtering Guide

## Full-Text Search

### Basic Search
Search tasks by title or description:
```
GET /api/v1/users/{user_id}/tasks?search=python
```

**Features**:
- Case-insensitive
- Searches title and description
- Partial word matching
- PostgreSQL full-text search

**Examples**:
- `search=urgent` → Finds "Urgent task" and "This is urgent"
- `search=python programming` → Finds tasks with both words

---

## Filtering

### By Status
```
?status=todo
?status=done
?status=in_progress
```

### By Priority
```
?priority=high
?priority=urgent
```

### By Tags
```
?tags=work,urgent
```
Finds tasks with ANY of the specified tags.

### By Date Range
```
?due_after=2024-01-01T00:00:00Z
?due_before=2024-12-31T23:59:59Z
```

### By Completion
```
?completed=true   # Only completed tasks
?completed=false  # Only incomplete tasks
```

---

## Sorting

### Sort Options
```
?sort=due_date&order=asc
?sort=priority&order=desc
?sort=created_at&order=desc
?sort=updated_at&order=asc
```

**Sort Fields**:
- `due_date`: By due date
- `priority`: By priority level
- `created_at`: By creation date
- `updated_at`: By last update

**Order**:
- `asc`: Ascending (oldest/lowest first)
- `desc`: Descending (newest/highest first)

---

## Pagination

```
?page=1&limit=20
```

**Parameters**:
- `page`: Page number (starts at 1)
- `limit`: Items per page (max: 100)

**Response**:
```json
{
  "tasks": [...],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

---

## Combining Filters

Combine multiple filters for precise results:

```
?search=python&status=todo&priority=high&sort=due_date&order=asc&page=1&limit=20
```

This finds:
- Tasks containing "python"
- With status "todo"
- High priority
- Sorted by due date (earliest first)
- Page 1, 20 items

---

## Performance Tips

1. **Use Indexes**: Search uses GIN indexes for fast full-text search
2. **Limit Results**: Use pagination to avoid loading too many tasks
3. **Specific Filters**: More filters = faster queries
4. **Cache Results**: Results cached for 5 minutes

---

## Common Queries

**Overdue Tasks**:
```
?status=todo&due_before=2024-01-15T00:00:00Z&sort=due_date&order=asc
```

**This Week's Tasks**:
```
?due_after=2024-01-15T00:00:00Z&due_before=2024-01-22T00:00:00Z
```

**High Priority Incomplete**:
```
?priority=high&completed=false&sort=due_date&order=asc
```

**Recently Updated**:
```
?sort=updated_at&order=desc&limit=10
```
