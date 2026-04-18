# Git: Diverged Branch Conflict When Pushing SubCategory Feature

**Date:** April 18, 2026  
**Status:** ✅ Resolved  
**Severity:** Medium  

---

## 🔴 Problem

When pushing SubCategory model feature (`feat: add SubCategory model...`), encountered diverged branch conflict:

```
error: failed to push some refs to 'https://github.com/DoTienHai/LogicBoost.git'
hint: Updates were rejected because the tip of your current branch is behind...
hint: your remote counterpart. Integrate the remote changes before pushing again.
```

### Root Cause

Timeline of events:
1. Initial commit `fddfc4a` pushed: "complete admin form fields and fix mini game answer normalization"
2. Created local commit `a46293d`: "SubCategory model..." (based on older state)
3. Attempted push → Git detected two different commits on same branch

**Branch state:**
```
GitHub (origin/main):    ... → fddfc4a (admin form complete)
Local branch (main):     ... → fddfc4a → a46293d (SubCategory)
                                  ↓
                         CONFLICT - Branches diverged!
```

---

## ✅ Solution Applied

Instead of complex merge/rebase, used reset + re-implement strategy:

### Step 1: Reset to Remote
```bash
git reset --hard origin/main
```
This discarded local commit and synced with GitHub's `fddfc4a`.

### Step 2: Re-implement SubCategory Changes
Manually re-applied all changes:
- Created `app/models/sub_category.py`
- Updated `app/models/question.py`: `sub_category` (TEXT) → `sub_category_id` (FK)
- Fixed `app/routes/admin.py`: lookup SubCategory by name, save FK
- Fixed `app/services/import_service.py`: resolve names to IDs
- Fixed `app/routes/real_world.py`: filter by `sub_category_id`
- Updated `copilot-instructions.md` with new schema

### Step 3: Commit and Push
```bash
git add -A
git commit -m "feat: add SubCategory model and migrate to sub_category_id FK"
git push
```

**Result:** Commit `1e5bd50` successfully pushed ✓

---

## 🧪 Testing

- ✅ All 65 tests passing (no failures)
- ✅ No code conflicts in implementation
- ✅ Clean working directory after push

---

## 📚 Lesson Learned

### Better Approach (for future)

Instead of reset, should use `git rebase`:

```bash
# Fetch latest from remote
git fetch origin

# Rebase local commits on top of remote
git rebase origin/main

# If conflicts occur → resolve manually
# Then continue rebase
git rebase --continue

# Finally push
git push
```

Or simpler one-liner:
```bash
git pull --rebase
git push
```

### When to Use Each Strategy

| Situation | Action | Pros | Cons |
|-----------|--------|------|------|
| Local commit not pushed yet | `git pull --rebase` | Clean, preserves history | Need to resolve conflicts |
| Complex conflicts | Reset + re-implement | Guaranteed to work | Tedious, manual |
| Multiple team members | Merge commit | Preserves both branches | Creates merge commit |

---

## 🎯 Key Takeaway

**Always sync before pushing new code:**
```bash
git fetch origin
git rebase origin/main  # or: git merge origin/main
git push
```

This prevents diverged branches and conflicts.
