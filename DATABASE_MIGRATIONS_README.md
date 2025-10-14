# Database Migrations - Quick Reference

## TL;DR

Run migrations (intelligent, safe to run anytime):
```bash
.venv/bin/python migrate_db.py
```

Create new migration after changing models:
```bash
.venv/bin/alembic revision --autogenerate -m "Your change description"
```

## What is this?

This project uses **Alembic** for database schema migrations. This means:

✅ Database schema changes are versioned
✅ Changes can be applied automatically
✅ Rollback is possible if needed
✅ CI/CD automatically applies migrations

## When do I need this?

You need to create a migration whenever you:

- Add a new table
- Add/remove a column
- Change a column type
- Add/remove an index
- Modify constraints

## Example Workflow

### 1. Change your model

Edit `core/db/models.py`:

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(20), nullable=True)  # NEW FIELD
```

### 2. Generate migration

```bash
.venv/bin/alembic revision --autogenerate -m "Add phone to users"
```

### 3. Review the generated file

Check `alembic/versions/XXXXX_add_phone_to_users.py`

### 4. Apply migration

```bash
.venv/bin/python migrate_db.py
```

Done! 🎉

## In CI/CD

Migrations run automatically during deployment:

1. Code is pushed
2. Tests run
3. Code is deployed
4. **Migrations run automatically** ← This step!
5. Services restart

## Full Documentation

See [MIGRATIONS.md](MIGRATIONS.md) for complete documentation.

## Emergency: Database Out of Sync?

```bash
# Generate a sync migration
.venv/bin/alembic revision --autogenerate -m "Sync database"

# Review it, then run
.venv/bin/python migrate_db.py
```

## Questions?

- **Q: Do I need to run migrations after pulling code?**
  A: Usually no - they run automatically in CI/CD. But you can run `migrate_db.py` to be sure.

- **Q: Can I safely run migrate_db.py multiple times?**
  A: Yes! It's intelligent and only runs if needed.

- **Q: What if a migration fails?**
  A: Check the error, fix the migration file, and try again. See MIGRATIONS.md for details.

- **Q: Can I undo a migration?**
  A: Yes, use `alembic downgrade -1` but be careful in production!
