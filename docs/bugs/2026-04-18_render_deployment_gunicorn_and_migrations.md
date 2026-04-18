# 🐛 Render Deployment: Gunicorn, Flask-Migrate & Filesystem Issues

**Date:** April 18, 2026
**Component:** Deployment (Render.com)
**Severity:** Critical
**Status:** Fixed

---

## Issues Found

### Issue 1: Invalid Gunicorn Entry Point Syntax
### Issue 2: Missing Flask-Migrate Configuration
### Issue 3: Read-only Filesystem Permission Error
### Issue 4: SQLite Database Path Format Error (Windows & Render)

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

## Issue 3: Read-only Filesystem Permission Error

### Error Message

```
==> Running 'gunicorn run:app'
==> Exited with status 1
```

No detailed error logs, but permission error occurs during initialization.

### Description

Even after fixing Issues 1 & 2, app crashes on Render with exit code 1. Render's filesystem is read-only, causing permission errors when app tries to create directories.

### Root Cause

**Two places tried to create `instance/` directory:**

1. **In `config.py` (line 14):**
```python
instance_dir.mkdir(parents=True, exist_ok=True)  # ❌ Permission error on Render
```

2. **In `app/__init__.py` (line 26-27):**
```python
os.makedirs(instance_path, exist_ok=True)  # ❌ Permission error on Render
```

**Problems:**
- Render has read-only filesystem → cannot create directories
- Initialization fails silently → exit code 1
- No error logged because it happens during boot, not in request handler

### Solution

**Wrap directory creation in try-except to handle read-only filesystem:**

**In `config.py`:**
```python
def _get_database_uri():
    """Get the database URI with absolute path."""
    base_dir = Path(__file__).resolve().parent
    instance_dir = base_dir / "instance"
    db_path = instance_dir / "logicboost.db"
    # Try to create instance directory (skip on read-only filesystem)
    try:
        instance_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        # Render or read-only filesystem - skip directory creation
        pass
    file_uri = db_path.as_uri()
    sqlite_uri = file_uri.replace("file://", "sqlite://")
    return sqlite_uri
```

**In `app/__init__.py`:**
```python
# Create instance directory if it doesn't exist (development only)
# On Render, filesystem is read-only, skip this
if config_name != "production":
    try:
        instance_path = os.path.join(...)
        os.makedirs(instance_path, exist_ok=True)
    except (OSError, PermissionError):
        # Render or read-only filesystem - skip
        pass
```

**Why this works:**
- ✅ Gracefully handles read-only filesystem (Render)
- ✅ Still creates directories in development (local)
- ✅ SQLite still works without explicit directory
- ✅ App initializes without crashing

### Why Render Has Read-only Filesystem

Render's free tier uses ephemeral storage:
- Files created during build persist
- Files created at runtime (new instances) are lost
- Filesystem is read-only for security/isolation
- Database needs to be created during initial build, not runtime

---

## Issue 4: SQLite Database Path Format Error (Windows & Render)

### Error Message

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

### Description

SQLite database URI uses incorrect path format on Windows and Render, causing database connection failures at runtime.

### Root Cause

**Original config.py:**
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///./instance/logicboost.db'  # ❌ WRONG (3 slashes)
# or
SQLALCHEMY_DATABASE_URI = 'sqlite:////instance/logicboost.db'   # ❌ WRONG (relative path)
```

**Problems:**
1. **3 slashes** (`sqlite:///`) = absolute path on UNIX, but incorrect format for Windows paths
2. **Relative path** without drive letter (`./instance/`) doesn't work reliably
3. SQLite cannot find database file on Windows or Render filesystem
4. Connection fails immediately when app tries to access database

### Solution

**Use absolute path built at module load time:**

```python
# config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DB_PATH = INSTANCE_DIR / "logicboost.db"

SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.as_posix()}"
# Result: sqlite:///D:/3_CODING/LogicBoost/instance/logicboost.db
```

**Why this works:**
- ✅ `Path(__file__).resolve()` works on Windows, macOS, Linux
- ✅ `.as_posix()` converts Windows backslashes to forward slashes
- ✅ Absolute path is always resolvable
- ✅ Works in development and production (Render)
- ✅ Database file location is deterministic

### SQLite URI Format Reference

| URI Format | Type | Use Case |
|---|---|---|
| `sqlite:///./instance/logicboost.db` | Relative (3 slashes) | ❌ Unreliable on Windows |
| `sqlite:////instance/logicboost.db` | Relative (4 slashes) | ❌ Not portable |
| `sqlite:///D:/path/to/logicboost.db` | Absolute (3 slashes + full path) | ✅ Best |
| `sqlite:///:memory:` | In-memory | ✅ Testing only |

**Correct Format:**
```
sqlite:///<absolute-path>
         ^^^
         3 slashes for absolute path
```

### Files Modified

1. **Modified:** `config.py` (lines 8-20)
   - Built absolute path using `Path(__file__).resolve()`
   - Use `DB_PATH.as_posix()` to ensure forward slashes
   - Generate SQLite URI with 3 slashes + full path
   
2. **Modified:** `DevelopmentConfig` (line 34-36)
   - Removed hardcoded relative path
   - Inherit `SQLALCHEMY_DATABASE_URI` from `Config` base class
   
3. **Modified:** `ProductionConfig` (line 42-44)
   - Removed hardcoded relative path
   - Inherit `SQLALCHEMY_DATABASE_URI` from `Config` base class

---

## Files Modified

1. **Modified:** `Procfile`
   - Changed from: `web: gunicorn "app:create_app()"` + `release: flask db upgrade`
   - Changed to: `web: gunicorn "run:app"`

2. **Modified:** `config.py`
   - Lines 8-20: Built absolute path using `Path` module
   - Lines 27-28: Added `SQLALCHEMY_DATABASE_URI` to Config base class
   - Removed hardcoded path strings from DevelopmentConfig and ProductionConfig
   
3. **Modified:** `app/__init__.py` (line 25-32)
   - Added config_name check and try-except around `os.makedirs()`

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
   - Result: ❌ Build successful, but exit code 1 - permission error during init

4. **Attempt 4:** Wrapped directory creation in try-except for Render read-only filesystem
   - Result: ❌ Build successful, but local tests fail - SQLite path format error

5. **Attempt 5:** Fixed SQLite database path to use absolute path format
   - Changed from: `sqlite:///./instance/logicboost.db` (relative)
   - Changed to: `sqlite:///D:/3_CODING/LogicBoost/instance/logicboost.db` (absolute)
   - Result: ✅ All 32 tests pass locally, deployment ready

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

### Deployment to Render
- Render filesystem is **read-only** → wrap directory creation in try-except
- Always gracefully handle permission errors during initialization
- Test with `FLASK_ENV=production` locally before deploying
- App must not assume it can write to filesystem on startup

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
- [ ] Test with `FLASK_ENV=production` locally
- [ ] Wrap all file I/O in try-except (handle read-only filesystem)
- [ ] For SQLite MVP: Keep Procfile simple (web command only)
- [ ] Test on Render free tier to verify read-only filesystem handling
