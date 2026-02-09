# Analytics Metric Calculations

## Overview

This document provides detailed technical specifications for all analytics metrics, including calculation formulas, data sources, edge cases, and implementation notes.

---

## Core Metrics

### 1. Task Totals

#### Total Tasks

**Description**: Count of all active tasks for a user.

**Formula**:
```sql
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND deleted = FALSE
```

**Data Source**: `tasks` table

**Edge Cases**:
- Excludes soft-deleted tasks (`deleted = TRUE`)
- Includes tasks in all statuses (todo, in_progress, done)

**Performance**: O(1) with proper indexing on `user_id` and `deleted`

**Cache TTL**: 5 minutes

---

#### Completed Tasks

**Description**: Count of tasks marked as done.

**Formula**:
```sql
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND status = 'done'
  AND deleted = FALSE
```

**Data Source**: `tasks` table

**Edge Cases**:
- Only counts tasks with `status = 'done'`
- Excludes deleted tasks
- Includes tasks completed at any time

**Performance**: O(1) with composite index on `(user_id, status, deleted)`

**Cache TTL**: 5 minutes

---

#### Pending Tasks

**Description**: Count of tasks not yet started.

**Formula**:
```sql
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND status = 'todo'
  AND deleted = FALSE
```

**Data Source**: `tasks` table

**Edge Cases**:
- Only counts tasks with `status = 'todo'`
- Does not include `in_progress` tasks

**Performance**: O(1) with composite index

**Cache TTL**: 5 minutes

---

#### In Progress Tasks

**Description**: Count of tasks currently being worked on.

**Formula**:
```sql
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND status = 'in_progress'
  AND deleted = FALSE
```

**Data Source**: `tasks` table

**Edge Cases**:
- Only counts tasks with `status = 'in_progress'`
- No time-based filtering

**Performance**: O(1) with composite index

**Cache TTL**: 5 minutes

---

#### Overdue Tasks

**Description**: Count of incomplete tasks past their due date.

**Formula**:
```sql
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND status != 'done'
  AND due_date < CURRENT_DATE
  AND deleted = FALSE
```

**Data Source**: `tasks` table

**Edge Cases**:
- Only counts incomplete tasks (todo or in_progress)
- Compares due_date to current date (not datetime)
- Tasks without due_date are not counted as overdue
- Timezone: Uses UTC for consistency

**Performance**: O(n) where n = tasks with due dates; optimized with index on `(user_id, status, due_date)`

**Cache TTL**: 5 minutes

---

### 2. Completion Rate

**Description**: Percentage of tasks completed out of total active tasks.

**Formula**:
```python
def calculate_completion_rate(completed_tasks: int, total_tasks: int) -> float:
    """
    Calculate completion rate as a percentage.

    Args:
        completed_tasks: Number of completed tasks
        total_tasks: Total number of active tasks

    Returns:
        Completion rate as percentage (0-100)
    """
    if total_tasks == 0:
        return 0.0

    return (completed_tasks / total_tasks) * 100
```

**Mathematical Formula**:
```
Completion Rate = (Completed Tasks / Total Active Tasks) × 100
```

**Data Sources**:
- Completed Tasks: `COUNT(*) WHERE status = 'done'`
- Total Active Tasks: `COUNT(*) WHERE deleted = FALSE`

**Edge Cases**:
- Returns 0.0 when total_tasks = 0 (no division by zero)
- Result is always between 0.0 and 100.0
- Rounded to 1 decimal place for display

**Validation**:
```python
assert 0.0 <= completion_rate <= 100.0
```

**Performance**: O(1) - uses pre-calculated counts

**Cache TTL**: 5 minutes

---

### 3. Priority Distribution

**Description**: Count of tasks grouped by priority level.

**Formula**:
```sql
SELECT
    priority,
    COUNT(*) as count
FROM tasks
WHERE user_id = :user_id
  AND deleted = FALSE
GROUP BY priority
```

**Data Source**: `tasks` table

**Response Format**:
```json
{
  "high": 25,
  "medium": 75,
  "low": 50,
  "total": 150
}
```

**Edge Cases**:
- Missing priorities default to 0 in response
- Total is sum of all priorities
- Excludes deleted tasks

**Validation**:
```python
assert response["total"] == sum([response["high"], response["medium"], response["low"]])
```

**Performance**: O(n) with GROUP BY; optimized with index on `(user_id, priority, deleted)`

**Cache TTL**: 5 minutes

---

### 4. Status Distribution

**Description**: Count of tasks grouped by status.

**Formula**:
```sql
SELECT
    status,
    COUNT(*) as count
FROM tasks
WHERE user_id = :user_id
  AND deleted = FALSE
GROUP BY status
```

**Data Source**: `tasks` table

**Response Format**:
```json
{
  "todo": 30,
  "in_progress": 15,
  "done": 105,
  "total": 150
}
```

**Edge Cases**:
- All statuses included in response (even if count = 0)
- Total is sum of all statuses
- Excludes deleted tasks

**Validation**:
```python
assert response["total"] == sum([response["todo"], response["in_progress"], response["done"]])
```

**Performance**: O(n) with GROUP BY; optimized with index

**Cache TTL**: 5 minutes

---

### 5. Task Velocity

**Description**: Average number of tasks completed per week.

**Formula**:
```python
def calculate_task_velocity(completed_tasks: int, days: int) -> float:
    """
    Calculate task velocity (tasks per week).

    Args:
        completed_tasks: Number of tasks completed in period
        days: Number of days in period

    Returns:
        Tasks completed per week
    """
    if days == 0:
        return 0.0

    weeks = days / 7.0
    return completed_tasks / weeks if weeks > 0 else 0.0
```

**Mathematical Formula**:
```
Task Velocity = Completed Tasks / (Days / 7)
```

**Data Source**:
```sql
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND status = 'done'
  AND completed_at >= :start_date
  AND completed_at <= :end_date
  AND deleted = FALSE
```

**Edge Cases**:
- Returns 0.0 when days = 0 or weeks = 0
- Partial weeks are included (e.g., 10 days = 1.43 weeks)
- Only counts tasks completed in the specified period

**Typical Periods**:
- 7 days (1 week)
- 30 days (~4.3 weeks)
- 90 days (~12.9 weeks)

**Performance**: O(1) with index on `(user_id, status, completed_at)`

**Cache TTL**: 10 minutes

---

### 6. Due Date Adherence Rate

**Description**: Percentage of tasks completed on or before their due date.

**Formula**:
```python
def calculate_adherence_rate(on_time_tasks: int, total_tasks_with_due_dates: int) -> float:
    """
    Calculate due date adherence rate.

    Args:
        on_time_tasks: Number of tasks completed on or before due date
        total_tasks_with_due_dates: Total tasks with due dates

    Returns:
        Adherence rate as percentage (0-100)
    """
    if total_tasks_with_due_dates == 0:
        return 0.0

    return (on_time_tasks / total_tasks_with_due_dates) * 100
```

**Mathematical Formula**:
```
Adherence Rate = (On-Time Tasks / Tasks with Due Dates) × 100
```

**Data Sources**:

On-Time Tasks:
```sql
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND status = 'done'
  AND due_date IS NOT NULL
  AND completed_at <= due_date
  AND deleted = FALSE
```

Total Tasks with Due Dates:
```sql
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND status = 'done'
  AND due_date IS NOT NULL
  AND deleted = FALSE
```

**Edge Cases**:
- Returns 0.0 when no tasks have due dates
- Only considers completed tasks
- Tasks without due dates are excluded
- Comparison uses date portion only (ignores time)

**Timezone Handling**:
- All dates stored in UTC
- Comparison done in UTC
- Client-side conversion for display

**Performance**: O(n) where n = tasks with due dates; optimized with index on `(user_id, status, due_date, completed_at)`

**Cache TTL**: 10 minutes

---

### 7. Average Completion Time

**Description**: Average time (in days) from task creation to completion.

**Formula**:
```python
def calculate_average_completion_time(tasks: List[Task]) -> float:
    """
    Calculate average completion time in days.

    Args:
        tasks: List of completed tasks with created_at and completed_at

    Returns:
        Average completion time in days
    """
    if not tasks:
        return 0.0

    total_days = sum([
        (task.completed_at - task.created_at).total_seconds() / 86400
        for task in tasks
    ])

    return total_days / len(tasks)
```

**Mathematical Formula**:
```
Average Completion Time = Σ(Completed Date - Created Date) / Number of Completed Tasks
```

**Data Source**:
```sql
SELECT
    created_at,
    completed_at
FROM tasks
WHERE user_id = :user_id
  AND status = 'done'
  AND completed_at IS NOT NULL
  AND deleted = FALSE
```

**Edge Cases**:
- Returns 0.0 when no completed tasks
- Only includes tasks with both created_at and completed_at
- Result in days (can be fractional, e.g., 2.5 days)
- Negative values should not occur (validation required)

**Validation**:
```python
assert average_completion_time >= 0.0
```

**Performance**: O(n) where n = completed tasks

**Cache TTL**: 10 minutes

---

### 8. Average Delay

**Description**: Average number of days tasks are completed late (for late tasks only).

**Formula**:
```python
def calculate_average_delay(tasks: List[Task]) -> float:
    """
    Calculate average delay for late tasks.

    Args:
        tasks: List of late tasks with due_date and completed_at

    Returns:
        Average delay in days
    """
    late_tasks = [
        task for task in tasks
        if task.completed_at > task.due_date
    ]

    if not late_tasks:
        return 0.0

    total_delay = sum([
        (task.completed_at - task.due_date).total_seconds() / 86400
        for task in late_tasks
    ])

    return total_delay / len(late_tasks)
```

**Mathematical Formula**:
```
Average Delay = Σ(Completed Date - Due Date) / Number of Late Tasks
where Late Tasks = Tasks where Completed Date > Due Date
```

**Data Source**:
```sql
SELECT
    due_date,
    completed_at
FROM tasks
WHERE user_id = :user_id
  AND status = 'done'
  AND due_date IS NOT NULL
  AND completed_at > due_date
  AND deleted = FALSE
```

**Edge Cases**:
- Returns 0.0 when no late tasks
- Only includes tasks completed after due date
- Result in days (can be fractional)
- Always positive (by definition)

**Validation**:
```python
assert average_delay >= 0.0
```

**Performance**: O(n) where n = late tasks

**Cache TTL**: 10 minutes

---

### 9. Productivity Score

**Description**: Composite score (0-100) based on multiple productivity factors.

**Formula**:
```python
def calculate_productivity_score(
    completion_rate: float,
    adherence_rate: float,
    velocity: float,
    consistency: float
) -> float:
    """
    Calculate overall productivity score.

    Args:
        completion_rate: Percentage of tasks completed (0-100)
        adherence_rate: Percentage of tasks on time (0-100)
        velocity: Tasks per week (normalized to 0-100)
        consistency: Consistency score (0-100)

    Returns:
        Productivity score (0-100)
    """
    # Normalize velocity to 0-100 scale
    # Assume 10 tasks/week = 100, linear scaling
    normalized_velocity = min(velocity * 10, 100)

    # Weighted average
    score = (
        completion_rate * 0.30 +
        adherence_rate * 0.30 +
        normalized_velocity * 0.25 +
        consistency * 0.15
    )

    return round(score, 1)
```

**Component Weights**:
- Completion Rate: 30%
- Adherence Rate: 30%
- Velocity: 25%
- Consistency: 15%

**Velocity Normalization**:
```python
def normalize_velocity(velocity: float) -> float:
    """
    Normalize velocity to 0-100 scale.

    Assumes:
    - 0 tasks/week = 0
    - 10 tasks/week = 100
    - Linear scaling
    """
    return min(velocity * 10, 100)
```

**Consistency Calculation**:
```python
def calculate_consistency(weekly_completions: List[int]) -> float:
    """
    Calculate consistency score based on standard deviation.

    Args:
        weekly_completions: List of tasks completed each week

    Returns:
        Consistency score (0-100)
    """
    if len(weekly_completions) < 2:
        return 100.0  # Perfect consistency with insufficient data

    mean = sum(weekly_completions) / len(weekly_completions)

    if mean == 0:
        return 0.0

    variance = sum((x - mean) ** 2 for x in weekly_completions) / len(weekly_completions)
    std_dev = variance ** 0.5

    # Coefficient of variation (lower is better)
    cv = std_dev / mean if mean > 0 else 0

    # Convert to 0-100 scale (inverse relationship)
    # CV of 0 = 100, CV of 1 = 0
    consistency = max(0, 100 - (cv * 100))

    return round(consistency, 1)
```

**Edge Cases**:
- Returns 0.0 when all components are 0
- Maximum score is 100.0
- Minimum score is 0.0
- Requires at least 2 weeks of data for consistency

**Validation**:
```python
assert 0.0 <= productivity_score <= 100.0
```

**Performance**: O(n) where n = weeks for consistency calculation

**Cache TTL**: 10 minutes

---

## Aggregated Metrics

### 10. Daily Analytics

**Description**: Aggregated statistics for a specific date.

**Schema**:
```python
class DailyAnalytics:
    user_id: UUID
    date: date
    tasks_created: int
    tasks_completed: int
    tasks_deleted: int
    completion_rate: float
    productivity_score: float
```

**Calculation**:
```sql
-- Tasks created on date
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND DATE(created_at) = :date

-- Tasks completed on date
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND DATE(completed_at) = :date

-- Tasks deleted on date
SELECT COUNT(*)
FROM tasks
WHERE user_id = :user_id
  AND DATE(deleted_at) = :date
  AND deleted = TRUE
```

**Aggregation Job**:
- Runs daily at midnight UTC
- Processes previous day's data
- Updates existing records if re-run
- Stores in `daily_analytics` table

**Performance**: O(n) where n = tasks for user; runs as background job

**Storage**: Permanent (not cached)

---

### 11. Trends

**Description**: Time-series data aggregated by period.

**Periods**:
- **Daily**: One data point per day
- **Weekly**: One data point per week (Monday-Sunday)
- **Monthly**: One data point per month

**Formula**:
```python
def aggregate_by_period(
    daily_analytics: List[DailyAnalytics],
    period: str
) -> List[TrendPoint]:
    """
    Aggregate daily analytics by period.

    Args:
        daily_analytics: List of daily analytics records
        period: 'daily', 'weekly', or 'monthly'

    Returns:
        List of aggregated trend points
    """
    if period == 'daily':
        return daily_analytics

    elif period == 'weekly':
        # Group by ISO week
        weeks = {}
        for record in daily_analytics:
            week_key = record.date.isocalendar()[:2]  # (year, week)
            if week_key not in weeks:
                weeks[week_key] = []
            weeks[week_key].append(record)

        return [aggregate_week(records) for records in weeks.values()]

    elif period == 'monthly':
        # Group by year-month
        months = {}
        for record in daily_analytics:
            month_key = (record.date.year, record.date.month)
            if month_key not in months:
                months[month_key] = []
            months[month_key].append(record)

        return [aggregate_month(records) for records in months.values()]
```

**Aggregation Functions**:
```python
def aggregate_week(records: List[DailyAnalytics]) -> TrendPoint:
    """Aggregate daily records into weekly trend point."""
    return TrendPoint(
        date=min(r.date for r in records),  # Week start date
        tasks_created=sum(r.tasks_created for r in records),
        tasks_completed=sum(r.tasks_completed for r in records),
        completion_rate=calculate_completion_rate(
            sum(r.tasks_completed for r in records),
            sum(r.tasks_created for r in records)
        ),
        productivity_score=sum(r.productivity_score for r in records) / len(records)
    )
```

**Edge Cases**:
- Partial weeks/months included
- Missing days filled with zeros
- Empty periods excluded from results

**Performance**: O(n) where n = daily records in range

**Cache TTL**: 15 minutes

---

## Materialized Views

### User Task Stats View

**Purpose**: Pre-aggregated task statistics per user for fast queries.

**Definition**:
```sql
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
```

**Refresh Strategy**:
- Refreshed every 5 minutes via cron job
- Can be refreshed on-demand for specific users
- Concurrent refresh to avoid blocking

**Usage**:
```sql
SELECT * FROM user_task_stats WHERE user_id = :user_id;
```

**Performance**: O(1) lookup after materialization

---

### User Priority Distribution View

**Purpose**: Pre-aggregated priority distribution per user.

**Definition**:
```sql
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
```

**Refresh Strategy**: Same as user_task_stats

---

## Performance Optimization

### Indexing Strategy

**Required Indexes**:
```sql
-- Primary lookups
CREATE INDEX idx_tasks_user_id ON tasks(user_id) WHERE deleted = FALSE;

-- Status queries
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status) WHERE deleted = FALSE;

-- Due date queries
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date) WHERE deleted = FALSE AND status != 'done';

-- Completion queries
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed_at) WHERE status = 'done' AND deleted = FALSE;

-- Priority distribution
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority) WHERE deleted = FALSE;

-- Daily aggregation
CREATE INDEX idx_tasks_created_at ON tasks(user_id, created_at) WHERE deleted = FALSE;
```

### Caching Strategy

**Cache Layers**:
1. **Application Cache** (Redis): 5-15 minute TTL
2. **Materialized Views**: 5 minute refresh
3. **Database Query Cache**: Automatic

**Cache Keys**:
```python
CACHE_KEY_OVERVIEW = "analytics:overview:{user_id}"
CACHE_KEY_TRENDS = "analytics:trends:{user_id}:{period}:{start}:{end}"
CACHE_KEY_ADHERENCE = "analytics:adherence:{user_id}:{period}"
CACHE_KEY_PRODUCTIVITY = "analytics:productivity:{user_id}"
```

**Cache Invalidation**:
- On task creation: Invalidate overview, trends
- On task completion: Invalidate all metrics
- On task deletion: Invalidate overview, trends
- On task update: Invalidate relevant metrics

### Query Optimization

**Best Practices**:
1. Use materialized views for frequently accessed aggregations
2. Leverage partial indexes with WHERE clauses
3. Use FILTER clause instead of CASE for conditional aggregation
4. Batch queries when possible
5. Use connection pooling
6. Monitor slow query log

**Query Limits**:
- Maximum date range for trends: 1 year
- Maximum tasks per export: 100,000
- Query timeout: 30 seconds

---

## Data Quality

### Validation Rules

**Task Data**:
```python
# Timestamps
assert task.created_at <= task.completed_at if task.completed_at else True
assert task.created_at <= task.updated_at

# Status
assert task.status in ['todo', 'in_progress', 'done']

# Priority
assert task.priority in ['low', 'medium', 'high']

# Completion
assert (task.status == 'done') == (task.completed_at is not None)
```

**Metric Ranges**:
```python
# Percentages
assert 0.0 <= completion_rate <= 100.0
assert 0.0 <= adherence_rate <= 100.0
assert 0.0 <= productivity_score <= 100.0

# Counts
assert total_tasks >= 0
assert completed_tasks >= 0
assert completed_tasks <= total_tasks

# Time
assert average_completion_time >= 0.0
assert average_delay >= 0.0
```

### Data Integrity

**Consistency Checks**:
```sql
-- Total tasks should equal sum of statuses
SELECT user_id
FROM user_task_stats
WHERE total_tasks != (completed_tasks + pending_tasks + in_progress_tasks);

-- Completion rate should match calculation
SELECT user_id
FROM user_task_stats
WHERE ABS(completion_rate - (completed_tasks::numeric / NULLIF(total_tasks, 0) * 100)) > 0.1;
```

**Automated Monitoring**:
- Run consistency checks daily
- Alert on data anomalies
- Log validation failures
- Automatic correction where possible

---

## Testing

### Unit Tests

Test each metric calculation independently:

```python
def test_completion_rate_calculation():
    assert calculate_completion_rate(70, 100) == 70.0
    assert calculate_completion_rate(0, 100) == 0.0
    assert calculate_completion_rate(0, 0) == 0.0
    assert calculate_completion_rate(100, 100) == 100.0
```

### Integration Tests

Test with real database queries:

```python
async def test_overview_metrics(session, test_user):
    # Create test data
    create_test_tasks(session, test_user, completed=7, pending=3)

    # Calculate metrics
    overview = await get_analytics_overview(session, test_user.id)

    # Verify
    assert overview.total == 10
    assert overview.completed == 7
    assert overview.completion_rate == 70.0
```

### Performance Tests

Test with large datasets:

```python
async def test_large_dataset_performance(session, test_user):
    # Create 10,000 tasks
    create_large_dataset(session, test_user, count=10000)

    # Measure query time
    start = time.time()
    overview = await get_analytics_overview(session, test_user.id)
    duration = time.time() - start

    # Verify performance
    assert duration < 1.0  # Should complete in < 1 second
```

---

## Appendix: SQL Queries

### Complete Overview Query

```sql
WITH task_counts AS (
    SELECT
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE status = 'done') as completed,
        COUNT(*) FILTER (WHERE status = 'todo') as pending,
        COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
        COUNT(*) FILTER (WHERE status != 'done' AND due_date < CURRENT_DATE) as overdue
    FROM tasks
    WHERE user_id = :user_id AND deleted = FALSE
),
priority_dist AS (
    SELECT
        COUNT(*) FILTER (WHERE priority = 'high') as high,
        COUNT(*) FILTER (WHERE priority = 'medium') as medium,
        COUNT(*) FILTER (WHERE priority = 'low') as low
    FROM tasks
    WHERE user_id = :user_id AND deleted = FALSE
)
SELECT
    tc.*,
    ROUND(tc.completed::numeric / NULLIF(tc.total, 0) * 100, 1) as completion_rate,
    pd.high as high_priority,
    pd.medium as medium_priority,
    pd.low as low_priority
FROM task_counts tc
CROSS JOIN priority_dist pd;
```

### Complete Trends Query

```sql
SELECT
    date,
    tasks_created,
    tasks_completed,
    completion_rate,
    productivity_score
FROM daily_analytics
WHERE user_id = :user_id
  AND date BETWEEN :start_date AND :end_date
ORDER BY date ASC;
```
