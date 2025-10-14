# Database Migrations Guide

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations with SQLAlchemy.

## Quick Start

### Running Migrations

To apply pending migrations:

```bash
.venv/bin/python migrate_db.py
```

The migration script is **intelligent** - it will:
- ✅ Check if migrations are needed
- ✅ Only run migrations if database is not up to date
- ✅ Handle both new and existing databases
- ✅ Provide detailed logging
- ✅ Exit gracefully if no migrations are needed

### Creating a New Migration

When you modify database models in `core/db/models.py`:

```bash
# Auto-generate migration from model changes
.venv/bin/alembic revision --autogenerate -m "Description of changes"

# Example:
.venv/bin/alembic revision --autogenerate -m "Add user preferences table"
```

This will create a new migration file in `alembic/versions/`.

**Important**: Always review the auto-generated migration before running it!

## Common Commands

### Check Current Database Version

```bash
.venv/bin/alembic current
```

### View Migration History

```bash
.venv/bin/alembic history
```

### Upgrade to Latest Version

```bash
.venv/bin/alembic upgrade head
```

### Downgrade One Version

```bash
.venv/bin/alembic downgrade -1
```

### Create Empty Migration

```bash
.venv/bin/alembic revision -m "Description"
```

## Migration Workflow

### 1. Modify Your Models

Edit `core/db/models.py`:

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255))
    # NEW FIELD:
    phone = Column(String(20), nullable=True)  # Add this
```

### 2. Generate Migration

```bash
.venv/bin/alembic revision --autogenerate -m "Add phone field to users"
```

This creates a file like: `alembic/versions/abc123_add_phone_field_to_users.py`

### 3. Review the Migration

Open the generated file and verify it's correct:

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone')
```

### 4. Run the Migration

```bash
.venv/bin/python migrate_db.py
```

Or manually:

```bash
.venv/bin/alembic upgrade head
```

## CI/CD Integration

Migrations are automatically run during deployment via GitHub Actions:

1. Code is deployed to the server
2. Dependencies are installed
3. **Migrations are run automatically** via `migrate_db.py`
4. Services are restarted

This ensures the database schema is always up to date with the deployed code.

## Directory Structure

```
.
├── alembic/                    # Alembic configuration
│   ├── versions/              # Migration files
│   │   └── 5ebc48e65e28_initial_baseline.py
│   ├── env.py                 # Alembic environment config
│   └── script.py.mako         # Migration template
├── alembic.ini                # Alembic configuration file
├── migrate_db.py              # Intelligent migration runner
└── core/db/
    ├── database.py            # Database configuration
    └── models.py              # SQLAlchemy models
```

## Troubleshooting

### Migration Fails

If a migration fails:

1. Check the error message carefully
2. Review the migration file for issues
3. Manually fix the database if needed
4. Update the migration file
5. Try again

### Database Out of Sync

If your database schema doesn't match the models:

```bash
# Generate a migration to sync them
.venv/bin/alembic revision --autogenerate -m "Sync database with models"

# Review and run
.venv/bin/python migrate_db.py
```

### Starting Fresh

To completely reset (⚠️ **DESTROYS ALL DATA**):

```bash
# Delete database file
rm slayflashcards.db

# Remove alembic version table tracking
.venv/bin/alembic stamp head

# Or recreate everything
.venv/bin/python -c "from core.db.database import reset_database; reset_database()"
.venv/bin/alembic stamp head
```

## Best Practices

1. **Always review** auto-generated migrations before running them
2. **Test migrations** on a copy of production data before deploying
3. **Keep migrations small** - one logical change per migration
4. **Never edit** existing migration files once they're committed
5. **Document complex migrations** with comments in the migration file
6. **Backup production database** before running migrations

## Environment Variables

The migration system uses the `DATABASE_URL` environment variable:

```bash
# SQLite (default)
export DATABASE_URL="sqlite:///./slayflashcards.db"

# PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

## How It Works

### migrate_db.py

This script intelligently handles migrations:

1. Connects to the database
2. Checks current migration version
3. Compares with latest migration
4. If different:
   - For new databases: Runs all migrations
   - For existing databases without Alembic: Stamps as current
   - For databases with pending migrations: Upgrades
5. Verifies success
6. Exits with appropriate status code

### Alembic env.py

The environment file:
- Imports all models from `core.db.models`
- Uses `DATABASE_URL` from environment
- Configures auto-generation to detect changes

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
