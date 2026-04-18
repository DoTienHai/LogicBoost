# 🐛 Database Path Issues on Windows

**Date:** 2026-04-18  
**Component:** config  
**Severity:** CRITICAL ⛔  
**Status:** ✅ FIXED (Commit: 95631cf)

---

## Problem

When running `python run.py`, the app crashed with:

```
sqlite3.OperationalError: unable to open database file
```

### Error Details

```
File "D:\3_CODING\LogicBoost\app\__init__.py", line 56, in create_app
    db.create_all()
...
sqlite3.OperationalError: unable to open database file
```

---

## Root Cause

The database URI was using **relative paths**:
- `.env` file had: `DATABASE_URL=sqlite:///instance/logicboost.db`
- SQLite couldn't find the path when app ran from different working directories
- Windows file path handling issues with forward slashes

---

## Steps to Reproduce

1. Clone LogicBoost repo
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python run.py`
5. **Result:** App crashes with database error

---

## Expected Behavior

✅ App should:
- Start Flask development server on localhost:5000
- Create database file at `instance/logicboost.db`
- Initialize tables automatically
- Ready for requests

---

## Solution Implemented

### Change 1: Updated `config.py`

```python
from pathlib import Path

def _get_database_uri():
    """Get the database URI with absolute path."""
    base_dir = Path(__file__).resolve().parent
    instance_dir = base_dir / "instance"
    db_path = instance_dir / "logicboost.db"
    instance_dir.mkdir(parents=True, exist_ok=True)
    
    file_uri = db_path.as_uri()  # file:///D:/3_CODING/...
    return file_uri.replace("file://", "sqlite://")
```

**Key improvements:**
- Use `Path(__file__).resolve()` for absolute path
- Auto-create `instance/` directory
- Convert file:// URI to sqlite:// format
- Windows-compatible path handling

### Change 2: Updated `.env`

**Before:**
```
DATABASE_URL=sqlite:///instance/logicboost.db
```

**After:**
```
# DATABASE_URL removed - config.py auto-generates absolute path
```

### Change 3: Fixed `app/__init__.py`

Added auto-creation of instance directory in app factory:

```python
instance_dir.mkdir(parents=True, exist_ok=True)
```

---

## Verification

✅ **All tests passing:**
- Model tests: 12/12 ✅
- Route tests: 20/20 ✅
- Total: 32/32 ✅

✅ **Database working:**
- `instance/logicboost.db` created successfully
- All tables initialized
- App starts without errors

✅ **Commit:** 95631cf - "fix: resolve database path issues"

---

## Files Changed

- `config.py` - Added `_get_database_uri()` function with absolute paths
- `.env` - Removed hardcoded `DATABASE_URL`
- `app/__init__.py` - Already has directory creation logic

---

## Related

- Issue Type: Bug
- Severity: CRITICAL (app won't start)
- Component: Configuration
- Platform: Windows, Python 3.12.4
- Status: CLOSED ✔️

---

## Lessons Learned

✅ Always use **absolute paths** for file operations in production  
✅ Use `Path.resolve()` for reliable absolute path resolution  
✅ Don't commit relative paths in config files  
✅ Test on different operating systems early

---

## Follow-up

None - issue fully resolved.
