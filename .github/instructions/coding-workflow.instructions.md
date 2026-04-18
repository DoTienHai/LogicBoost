---
description: Coding workflow and testing rules for LogicBoost development
applyTo: '**'
---

# LogicBoost — Coding Workflow & Testing Rules

## 🎯 Core Rule: Code + Tests Are One

**Every user request must produce:**
1. ✅ Implementation code (following `copilot-instructions.md`)
2. ✅ Unit/Integration tests (in `tests/test_[feature].py`)
3. ✅ Both must pass before considering the task done

**This applies to:**
- Initial feature implementation
- Bug fixes
- Code refactoring
- Any code update

---

## ✅ Definition of Done

A task is complete ONLY when ALL of the following are met:

| Requirement | Details |
|------------|---------|
| **Code implemented** | Follows spec in `copilot-instructions.md` + coding guidelines |
| **Tests written** | Unit tests cover main logic; integration tests for API routes |
| **Tests passing** | 100% test pass rate (no skip, no xfail) |
| **No hardcoded values** | Use `config.py` or constants only |
| **No scope creep** | Only features in MVP scope (see `copilot-instructions.md`) |
| **Error handling** | Server-side validation + proper HTTP status codes |
| **Code review ready** | Clean, well-commented, follows PEP 8 (Python) |

---

## 📝 Test-per-Feature Rule

**Golden Rule:** Tests are written **alongside the feature**, never after.

### Workflow
1. **User makes request** → "Implement feature X"
2. **Copilot generates:**
   - Implementation code
   - Test file (`tests/test_feature_x.py`)
3. **Both are delivered together**
4. **If code is updated later** → corresponding tests MUST also be updated
5. **Before completing update** → run all tests to ensure no regression

### Test Requirements
- **Coverage:** Minimum 80% for all services
- **Naming:** `test_[functionality_name]()` (descriptive, not `test_1`, `test_2`)
- **Mocking:** Mock external dependencies (database, file I/O)
- **Types:** Both unit tests (service logic) + integration tests (routes)

---

## 🔄 Update Workflow

### When Code is Changed
1. **Update the implementation file**
2. **Immediately update corresponding tests**
3. **Run test suite** to verify no regression
4. **If tests fail** → fix code, NOT tests (don't just skip failing tests)

### When Tests Fail After Update
**Never skip or xfail tests.** Instead:
1. Identify why test failed (read assertion message)
2. Fix the code to match the test's expectation, OR
3. If test is wrong, update test AND provide explanation

### Test Execution
```bash
# Run all tests with coverage report
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run single test file with coverage
pytest tests/test_daily_challenge_service.py -v --cov=app --cov-report=term

# Run single test with coverage
pytest tests/test_daily_challenge_service.py::test_get_daily_questions -v --cov=app --cov-report=term
```

**Note:** Coverage report will be generated in `htmlcov/index.html` (open in browser for detailed view)

---

## 💡 Best Practices

### Code Quality
- ✅ Use type hints: `def check_answer(question: Question, answer: str) -> bool:`
- ✅ Write docstrings: `"""Check if user answer matches correct answer."""`
- ✅ Keep functions < 20 lines
- ✅ Use constants: `MAX_QUESTIONS_PER_DAILY = 5`

### Testing
- ✅ Use descriptive test names: `test_check_multiple_choice_answer_case_insensitive()`
- ✅ Mock external dependencies (database, file I/O)
- ✅ Test both happy path and edge cases (empty input, None, invalid types)
- ✅ Use `pytest` fixtures for setup/teardown

### Database
- ✅ Use Flask-Migrate for schema changes
- ✅ Always validate user input before DB insert
- ✅ Never hardcode table names or column names

---

## 🚫 What NOT to Do

❌ Skip tests because they're "too complicated"
❌ Merge code without running test suite
❌ Leave failing tests unresolved (even if "just a warning")
❌ Hardcode values in code (e.g., `difficulty = 1`)
❌ Add features outside MVP scope
❌ Write tests without actually running them
❌ Update only code without updating tests, or vice versa