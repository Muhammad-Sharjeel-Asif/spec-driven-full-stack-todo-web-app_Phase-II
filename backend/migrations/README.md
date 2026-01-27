# Alembic Migrations

This directory contains database migration files for the Todo Backend API.

## Migration Commands

### Generate a new migration
```bash
# Set the environment variable to avoid database connection during migration generation
RUNNING_ALEMBIC_MIGRATION=1 PYTHONPATH=./src python -m alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations to the database
```bash
python -m alembic upgrade head
```

### Downgrade to a previous version
```bash
python -m alembic downgrade -1  # Downgrade by one revision
# or
python -m alembic downgrade <revision_id>  # Downgrade to specific revision
```

### Check current migration status
```bash
python -m alembic current
```

### Show migration history
```bash
python -m alembic history --verbose
```

## Notes

- The `RUNNING_ALEMBIC_MIGRATION=1` environment variable is required when generating migrations to avoid connecting to the database during the process.
- All models are defined in `src/models/` and are automatically registered with SQLModel.
- The `env.py` file is configured to load settings from the application's configuration.
- Migration files are stored in the `versions/` directory and are executed in chronological order.
