# 🐛 Bug Reports

This directory stores all documented bugs and issues for LogicBoost.

## Format

Bug reports are saved as:
```
YYYY-MM-DD_component_issue-title.md
```

Example:
- `2026-04-18_database_path_issues.md`
- `2026-04-20_admin_form_crash.md`
- `2026-04-22_timer_accuracy_problem.md`

## Components

- `backend` — Flask routes, services, logic
- `frontend` — HTML, CSS, JavaScript, templates
- `database` — SQLAlchemy models, migrations
- `testing` — Pytest, fixtures, coverage
- `config` — Environment, settings, paths
- `security` — Input validation, authentication
- `performance` — Speed, optimization
- `docs` — Documentation

## Status

- 🔴 **CRITICAL** — Fix immediately
- 🟡 **HIGH** — Fix before next release
- 🟠 **MEDIUM** — Fix in current sprint
- 🟢 **LOW** — Fix when time permits

## Tracking

| Status | Description |
|--------|-------------|
| 🆕 NEW | Just reported, not yet started |
| 🔍 INVESTIGATING | Developer looking at it |
| 🔧 IN PROGRESS | Developer working on fix |
| ✅ FIXED | Fix committed, waiting for verification |
| ✔️ VERIFIED | Fix tested and confirmed working |
| 📋 CLOSED | Issue resolved and closed |

## Example Bug Report

```markdown
# 🐛 Database Path Issues on Windows

**Date:** 2026-04-18
**Component:** config
**Severity:** CRITICAL ⛔
**Status:** ✅ FIXED

## Problem

When running `python run.py`, the app crashes with:
```
sqlite3.OperationalError: unable to open database file
```

## Cause

The database URI in `.env` was using a relative path `sqlite:///instance/logicboost.db`, which doesn't work on Windows when app runs from different directories.

## Solution

Updated `config.py` to:
1. Use absolute paths with `Path(__file__).resolve().parent`
2. Removed `DATABASE_URL` from `.env` so config auto-generates absolute path
3. Convert file URI to SQLite URI format: `file://` → `sqlite://`

## Verification

✅ App starts without database errors
✅ Database file created at correct location
✅ All tests pass (32/32)

## Related

- Commit: 95631cf
- Issue: N/A
```

## How to Report a Bug

See: [bug-report.instructions.md](../ instructions/bug-report.instructions.md)

Start your message with:
- `bug ...` — Report a bug
- `issue ...` — Report an issue
- `error ...` — Report an error

---

**Total Bugs:** [check directory for count]
