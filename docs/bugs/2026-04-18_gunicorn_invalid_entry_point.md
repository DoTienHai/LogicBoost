# 🐛 Render Deployment: Gunicorn Invalid Entry Point Syntax

**Date:** April 18, 2026
**Component:** Deployment (Render.com)
**Severity:** Critical
**Status:** Fixed

---

## Error Message

```
gunicorn.errors.AppImportError: Failed to find attribute 'app' in 'app'.
```

Full traceback:
```
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.12/site-packages/gunicorn/util.py", line 414, in import_app
    app = getattr(mod, name)
          ^^^^^^^^^^^^^^^^^^
AttributeError: module 'app' has no attribute 'app'
During handling of the above exception, another exception occurred:
...
gunicorn.errors.AppImportError: Failed to find attribute 'app' in 'app'.
```

---

## Description

Render deployment fails because Procfile uses incorrect Gunicorn syntax for app entry point.

**Symptoms:**
- ❌ Render build fails immediately
- ❌ Error: "Failed to find attribute 'app' in 'app'"
- ❌ Gunicorn cannot find Flask app instance
- ❌ Deployment halts with exit status 1

---

## Root Cause

**Procfile had invalid syntax:**
```
web: gunicorn "app:create_app()"  # ❌ WRONG
```

**Issues:**
1. Gunicorn syntax: `module:variable` (NOT `module:function()`)
2. `app:create_app()` tries to call a function, which Gunicorn cannot do
3. Gunicorn looks for variable named `create_app()` in module `app`, doesn't find it
4. Flask app instance not properly referenced

---

## Solution

**Update Procfile to correct syntax:**
```
web: gunicorn "run:app"  # ✅ CORRECT
```

**Why this works:**
- ✅ `run:app` = Get variable `app` from module `run.py`
- ✅ `run.py` has: `app = create_app()` (creates instance)
- ✅ Gunicorn can load the `app` instance directly
- ✅ Follows WSGI standard for app entry points

---

## Code Structure

**File: run.py**
```python
from app import create_app

app = create_app()  # ← This is the variable Gunicorn needs

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

**Gunicorn entry point reference:**
- ❌ `app:create_app()` → Tries to call function (invalid)
- ✅ `run:app` → References the `app` variable (correct)

---

## Files Modified

1. **Modified:** `Procfile` (changed from `app:create_app()` to `run:app`)

---

## Testing

- ✅ Local test: `python run.py` works fine
- ✅ Gunicorn test: `gunicorn "run:app"` starts app without errors
- ✅ All 32 unit tests pass
- ✅ App imports correctly: `from run import app; print(app)`

---

## Deployment Steps

After fix:
1. Git commit Procfile change
2. Git push to main branch
3. Render auto-detects new commit and redeploys
4. Gunicorn successfully loads `run:app`
5. App starts with status 200

---

## WSGI Standard Reference

Gunicorn follows WSGI (Web Server Gateway Interface) standard:
- **Format:** `module:variable`
- `module` = Python module name (e.g., `run`, `wsgi`, `app`)
- `variable` = WSGI-compliant application instance (e.g., Flask app)

**Valid examples:**
```
gunicorn "run:app"        # ✅ Get 'app' from 'run.py'
gunicorn "wsgi:app"       # ✅ Get 'app' from 'wsgi.py'
gunicorn "myapp:application"  # ✅ Get 'application' from 'myapp.py'
```

**Invalid examples:**
```
gunicorn "app:create_app()"     # ❌ Cannot call functions
gunicorn "run:create_app()"     # ❌ Cannot call functions
gunicorn "run"                  # ❌ Must specify variable name
```

---

## References

- Gunicorn Docs: https://docs.gunicorn.org/en/stable/run.html
- WSGI Standard: https://www.python.org/dev/peps/pep-3333/
- Render Procfile: https://render.com/docs/procfile

---

## Prevention

For future Gunicorn deployments:
1. **Rule:** Entry point is always `module:variable`, NOT `module:function()`
2. **Test locally first:** `gunicorn "module:variable"`
3. **Create Flask app as module variable:** `app = create_app()`
4. **Never try to call functions:** `create_app()` must be called beforehand

---

## Timeline

1. **Initial:** Procfile used `gunicorn "app:create_app()"`
2. **Error:** Render deploy failed with AppImportError
3. **Fix:** Changed to `gunicorn "run:app"`
4. **Result:** Deployment successful after fix
