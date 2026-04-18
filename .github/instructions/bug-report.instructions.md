---
description: Bug report and issue tracking for LogicBoost development
applyTo: 'khi người dùng bắt đầu message với "bug ..." hoặc "issue ..."'
---

# LogicBoost — Bug Report & Issue Tracking

## 🐛 How to Report a Bug

Start your message with one of these keywords:
- `bug ...` - Report a bug you found
- `issue ...` - Report an issue or problem
- `error ...` - Report an error

### Format

```
bug [component]: [short description]

Error/Symptom:
- [What went wrong]

Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. ...

Expected Behavior:
- [What should happen]

Actual Behavior:
- [What actually happened]

Environment:
- Browser/Platform: [e.g., Windows, Chrome]
- Version: [if applicable]

Severity: [critical | high | medium | low]
```

---

## 📋 Bug Report Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Backend** | Flask routes, database, services | "Route /daily-challenge/ returns 500 error" |
| **Frontend** | Templates, CSS, JavaScript | "Button color not matching design on mobile" |
| **Database** | SQLAlchemy, migrations, queries | "Question model missing Vietnamese field" |
| **Testing** | Test failures, coverage issues | "Test test_routes.py::TestMainRoutes fails randomly" |
| **Config** | Environment, settings, paths | "Database path issues on Windows" |
| **Security** | Input validation, XSS, SQL injection | "User input not sanitized in admin form" |
| **Performance** | Slow queries, memory leaks | "Page loading takes 5+ seconds" |
| **Documentation** | Missing or incorrect docs | "API endpoint not documented" |

---

## 🎯 Severity Levels

- **CRITICAL** ⛔
  - App crashes or won't start
  - Data loss or corruption
  - Security vulnerability
  - Essential feature broken
  - *Action:* Fix ASAP, top priority

- **HIGH** 🔴
  - Major feature not working
  - Incorrect calculation/logic
  - Memory leak
  - User data at risk
  - *Action:* Fix before next release

- **MEDIUM** 🟡
  - Feature partially working
  - UI misalignment
  - Slow performance
  - Error handling missing
  - *Action:* Fix in current sprint

- **LOW** 🟢
  - Minor UI issue
  - Typo/grammar
  - Code quality improvement
  - Nice-to-have feature
  - *Action:* Fix when time permits

---

## 📝 Bug Report Template

```markdown
**Bug:** [Short title]

**Component:** [backend | frontend | database | testing | config | security | performance | docs]

**Severity:** [critical | high | medium | low]

**Error:**
```
[Paste error message/traceback]
```

**Steps to Reproduce:**
1. ...
2. ...

**Expected:** 
[What should happen]

**Actual:** 
[What actually happened]

**Environment:**
- OS: [Windows | macOS | Linux]
- Python: [version]
- Browser: [if frontend issue]
- Branch: [branch name]

**Suggested Fix:**
[If you have an idea how to fix it]

**Related Issues:**
- Closes #123 (if fixing another issue)
- Relates to #456
```

---

## 🔍 Bug Report File Location

All bug reports saved to: **`docs/bugs/`**

Format: `YYYY-MM-DD_component_issue-title.md`

Example:
```
docs/bugs/2026-04-18_database_path_issues.md
docs/bugs/2026-04-18_admin_form_crash.md
docs/bugs/2026-04-20_timer_accuracy.md
```

---

## 📊 Bug Report Tracking

After reporting a bug, it will be:
1. ✅ Documented in `docs/bugs/`
2. 📌 Added to GitHub Issues (if critical/high)
3. 🏷️ Tagged by component and severity
4. ✔️ Assigned to developer
5. 📝 Linked to fix commit

---

## 🚀 Bug Fix Workflow

Once a bug is reported:

1. **Investigate**
   - Reproduce the issue
   - Check error logs
   - Review related code

2. **Create Fix**
   - Write code to fix
   - Add/update tests
   - Ensure tests pass

3. **Commit**
   ```bash
   git commit -m "fix(component): brief description
   
   Fixes #bug-issue-id
   
   Changes:
   - Change 1
   - Change 2"
   ```

4. **Test**
   - Run full test suite
   - Verify fix works
   - Check for regressions

5. **Update Bug Report**
   - Mark as FIXED
   - Link to commit
   - Add fix date

---

## 📌 Common Bugs & Quick Fixes

| Bug | Cause | Fix |
|-----|-------|-----|
| `unable to open database file` | Database path issue | Use absolute path in config |
| Route returns 404 | Blueprint not registered | Check app/__init__.py registrations |
| Tests fail | Import errors | Add sys.path.insert to conftest.py |
| CSS not loading | Static folder path wrong | Check Flask() constructor template_folder |
| Template not found | Folder structure mismatch | Verify templates/ directory layout |

---

## 💡 Tips

✅ **Good bug report:**
- Clear, specific title
- Reproducible steps
- Expected vs actual behavior
- Environment details
- Error messages/logs

❌ **Bad bug report:**
- "Something is broken"
- No error details
- Can't reproduce
- No environment info
- Just a screenshot

---

## 🔗 How to Reference Bugs

In commits/PRs:
```
Fixes #123          → Auto-closes issue #123
Closes #bug-id
Relates to #456     → Links but doesn't close
See #789
```

In code comments:
```python
# TODO: Fix #123 - timer accuracy issue
# HACK: Workaround for #456 until we refactor
```

---

## 📞 Need Help?

For questions about bug reporting:
- Ask in the message with `bug: question about reporting`
- Reference the issue number
- Describe what you need help with
