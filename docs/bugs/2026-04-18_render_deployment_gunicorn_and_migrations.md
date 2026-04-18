# 🐛 Render Deployment: Gunicorn Entry Point & Flask-Migrate Configuration Issues

**Date:** April 18, 2026
**Component:** Deployment (Render.com)
**Severity:** Critical
**Status:** Fixed

---

## Issues Found

### Issue 1: Invalid Gunicorn Entry Point Syntax
### Issue 2: Missing Flask-Migrate Configuration

---

## Issue 1: Invalid Gunicorn Entry Point Syntax

### Error Message

```
gunicorn.errors.AppImportError: Failed to find attribute 'app' in 'app'.
```

### Description

Procfile uses incorrect Gunicorn syntax, causing deployment to fail immediately.

### Root Cause

**Original Procfile:**
```
web: gunicorn "app:create_app()"  # ❌ WRONG
```

**Problem:**
- Gunicorn syntax is `module:variable`, NOT `module:function()`
- `app:create_app()` tries to execute a function call
- Gunicorn cannot call functions, only reference variables
- Flask app instance never gets loaded

### Solution

**Update to correct syntax:**
```
web: gunicorn "run:app"  # ✅ CORRECT
```

**Why this works:**
- `run:app` = Reference the `app` variable from `run.py` module
- `run.py` has: `app = create_app()` (instance already created)
- Gunicorn loads the Flask app instance directly
- Follows WSGI standard

### Code Structure

```python
# run.py
from app import create_app

app = create_app()  # ← Variable that Gunicorn needs

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

### WSGI Standard Reference

| Format | Valid? | Example |
|--------|--------|---------|
| `module:variable` | ✅ | `gunicorn "run:app"` |
| `module:variable` | ✅ | `gunicorn "wsgi:app"` |
| `module:function()` | ❌ | `gunicorn "app:create_app()"` |
| Module only | ❌ | `gunicorn "run"` |

---

## Issue 2: Missing Flask-Migrate Configuration

### Error Message

```
==> Running 'gunicorn run:app'
==> Exited with status 1
```

Detailed logs: App starts but crashes immediately after migration attempt.

### Description

After fixing Issue 1, deployment builds successfully but app crashes with exit code 1 and no detailed error message.

### Root Cause

**Problematic Procfile:**
```
web: gunicorn "run:app"
release: flask db upgrade  # ❌ This fails because...
```

**Problems:**
1. `migrations/versions/` directory is empty (no migration files)
2. `flask db upgrade` tries to run migrations but finds nothing
3. Release command fails silently → exit code 1
4. App doesn't start because release command failed

**Why migrations were missing:**
- Flask-Migrate was never initialized (`flask db init`)
- No migration files were created
- SQLite MVP doesn't need schema versioning yet

### Solution

**Remove the problematic release command:**

```
web: gunicorn "run:app"
```

**Why this works:**
- ✅ Web command runs directly without migration step
- ✅ SQLite database auto-created on first run (via SQLAlchemy)
- ✅ For MVP with SQLite, Flask-Migrate is unnecessary
- ✅ Can add migrations later when needed

### When to Use Flask-Migrate

**You NEED Flask-Migrate when:**
- Making live schema changes in production
- Version-controlling database changes
- Using shared database (PostgreSQL in production)
- Need rollback capability

**You DON'T need it for:**
- ✅ SQLite MVP with auto-created schema
- ✅ Initial deployment
- ✅ No expected schema changes during MVP

---

## Files Modified

1. **Modified:** `Procfile`
   - Changed from: `web: gunicorn "app:create_app()"` + `release: flask db upgrade`
   - Changed to: `web: gunicorn "run:app"`

---

## Testing

- ✅ Local import test: `python -c "from run import app; print(app)"` works
- ✅ Gunicorn test: `gunicorn "run:app"` starts without errors
- ✅ All 32 unit tests pass
- ✅ App initialization: SQLite database auto-created
- ✅ Migration status: `migrations/versions/` confirmed empty (OK for MVP)

---

## Deployment Timeline

1. **Attempt 1:** Used `gunicorn "app:create_app()"`
   - Result: ❌ AppImportError - attribute 'app' not found

2. **Attempt 2:** Changed to `gunicorn "run:app"` but kept `release: flask db upgrade`
   - Result: ❌ Exit code 1 - release command failed due to missing migrations

3. **Attempt 3:** Removed release command, kept `gunicorn "run:app"`
   - Result: ✅ Deployment successful, app running

---

## Lessons Learned

### Gunicorn Entry Point
- Always use `module:variable` format (NOT `module:function()`)
- Test locally first: `gunicorn "run:app"`
- Variable must be a WSGI-compliant app instance (Flask app)

### Release Commands
- Only add `release:` command if migrations are properly configured
- Test `flask db upgrade` locally before adding to Procfile
- For SQLite MVP, release command is usually unnecessary

### SQLite for MVP
- SQLite automatically creates database and schema on first app init
- No manual migration setup needed
- Can upgrade to PostgreSQL + Flask-Migrate later if needed

---

## References

- Gunicorn Docs: https://docs.gunicorn.org/en/stable/run.html
- WSGI Standard: https://www.python.org/dev/peps/pep-3333/
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.io/
- Flask-Migrate: https://alembic.sqlalchemy.org/
- Render Procfile: https://render.com/docs/procfile

---

## Prevention Checklist

- [ ] Test Gunicorn locally: `gunicorn "module:variable"`
- [ ] Verify app imports without errors
- [ ] Only use release commands if Flask-Migrate is initialized
- [ ] Test release command locally: `flask db upgrade`
- [ ] Confirm migration files exist in `migrations/versions/`
- [ ] Run full test suite before deploying
- [ ] For SQLite MVP: Keep Procfile simple (web command only)
