# Database Indexes for Todo Backend API

This document outlines the required database indexes for optimal performance of the Todo Backend API.

## Required Indexes

### Primary Indexes
- `idx_tasks_user_id` - Index on `user_id` column in `tasks` table for efficient user-scoped queries
- `idx_tasks_completed` - Index on `is_completed` column in `tasks` table for filtering by completion status
- `idx_tasks_priority` - Index on `priority` column in `tasks` table for filtering by priority level
- `idx_tasks_due_date` - Index on `due_date` column in `tasks` table for due date filtering and sorting
- `idx_tasks_deleted_at` - Index on `deleted_at` column in `tasks` table for excluding soft-deleted records

### Composite Indexes
- `idx_tasks_user_completed` - Composite index on `(user_id, is_completed)` for efficient user-scoped completion queries
- `idx_tasks_user_priority` - Composite index on `(user_id, priority)` for efficient user-scoped priority queries
- `idx_tasks_user_due_date` - Composite index on `(user_id, due_date)` for efficient user-scoped due date queries
- `idx_tasks_user_deleted` - Composite index on `(user_id, deleted_at)` for efficient user-scoped queries excluding soft-deleted tasks

## SQL Commands

```sql
-- Primary indexes
CREATE INDEX idx_tasks_user_id ON tasks (user_id);
CREATE INDEX idx_tasks_completed ON tasks (is_completed);
CREATE INDEX idx_tasks_priority ON tasks (priority);
CREATE INDEX idx_tasks_due_date ON tasks (due_date);
CREATE INDEX idx_tasks_deleted_at ON tasks (deleted_at);

-- Composite indexes
CREATE INDEX idx_tasks_user_completed ON tasks (user_id, is_completed);
CREATE INDEX idx_tasks_user_priority ON tasks (user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks (user_id, due_date);
CREATE INDEX idx_tasks_user_deleted ON tasks (user_id, deleted_at);
```

## Alembic Migration

To add these indexes via Alembic, create a new migration:

```bash
alembic revision --autogenerate -m "add performance indexes"
```

Then update the generated migration file to include the required indexes.

## Performance Monitoring

Monitor query performance using:
- PostgreSQL's `EXPLAIN ANALYZE` to verify index usage
- Slow query logs to identify queries that need optimization
- Application metrics to track database query times