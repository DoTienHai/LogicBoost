# LogicBoost — Copilot Instructions

## � Table of Contents

1. [📌 Project Overview](#-project-overview)
2. [🎯 Core Concept](#-core-concept)
3. [🛠️ Tech Stack](#-tech-stack)
4. [📁 Project Structure](#-project-structure)
5. [🗄️ Database Schema](#-database-schema)
6. [🖼️ Image Handling](#-image-handling)
7. [📝 Markdown + LaTeX Rendering](#-markdown--latex-rendering)
8. [🌐 Bilingual Support (EN / VI)](#-bilingual-support-en--vi)
9. [🎨 Rendering by `question_type`](#-rendering-by-question_type)
10. [✅ Answer Checking](#-answer-checking)
11. [🛠️ Admin Panel](#-admin-panel)
12. [🎮 Feature Specifications](#-feature-specifications)
13. [📐 Coding Guidelines](#-coding-guidelines)
14. [🔧 Environment Variables (.env)](#-environment-variables-env)
15. [❌ Out of Scope for MVP](#-out-of-scope-for-mvp)
16. [✅ Code Quality Rules](#-code-quality-rules)

---

## �📌 Project Overview
LogicBoost is a web app that helps working adults (22-35 years old) stay mentally sharp
through daily math and strategy challenges based on real-life scenarios.
Users spend only 5-10 minutes per day solving problems related to personal finance,
game theory, and real-world decision-making.

## 🎯 Core Concept
- Real-life math problems with concrete numbers that can be calculated
- Game theory and strategic thinking challenges
- Short daily sessions: 5-10 minutes
- Every question includes a step-by-step explanation after answering
- Questions can be presented as multiple choice or free text input
- Admin UI to add questions manually or import from Excel

## 🛠️ Tech Stack
- **Backend:** Python / Flask
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Database:** SQLite (MVP) → PostgreSQL (production)
- **Deploy:** Render.com
- **Excel parsing:** openpyxl

## 📁 Project Structure
```
LogicBoost/
│
├── .github/
│   └── copilot-instructions.md
│
├── app/
│   ├── __init__.py                         # App factory (create_app)
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py                         # Home page routes
│   │   ├── daily_challenge.py              # Daily Challenge routes
│   │   ├── mini_game.py                    # Quick Mini Game routes
│   │   ├── real_world.py                   # Real-world Problem routes
│   │   └── admin.py                        # Admin panel routes
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── question.py                     # Question model
│   │   └── user_answer.py                  # User answer model
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── daily_challenge_service.py      # Daily challenge logic
│   │   ├── mini_game_service.py            # Mini game logic
│   │   ├── real_world_service.py           # Real-world scenario logic
│   │   ├── score_service.py                # Score checking & stats tracking
│   │   ├── import_service.py               # Excel import logic
│   │   └── calculator.py                   # Financial & math helpers
│   │
│   ├── templates/
│   │   ├── base.html                       # Base layout
│   │   ├── index.html                      # Home page
│   │   ├── daily_challenge/
│   │   │   ├── index.html                  # Daily challenge lobby
│   │   │   ├── question.html               # Question display
│   │   │   └── summary.html                # End of session summary
│   │   ├── mini_game/
│   │   │   ├── index.html                  # Mini game lobby
│   │   │   ├── play.html                   # Game screen with timer
│   │   │   └── result.html                 # Game result
│   │   ├── real_world/
│   │   │   ├── index.html                  # Scenario list
│   │   │   ├── scenario.html               # Scenario + question
│   │   │   └── explanation.html            # Step-by-step explanation
│   │   ├── admin/
│   │   │   │   ├── index.html                  # Admin dashboard (question list)
│   │   │   ├── question_form.html          # Add / edit single question
│   │   │   └── import_excel.html           # Upload Excel file
│   │   └── error.html
│   │
│   └── static/
│       ├── css/
│       │   ├── main.css
│       │   ├── daily_challenge.css
│       │   ├── mini_game.css
│       │   ├── real_world.css
│       │   └── admin.css
│       ├── js/
│       │   ├── main.js
│       │   ├── daily_challenge.js
│       │   ├── mini_game.js
│       │   ├── real_world.js
│       │   └── admin.js
│       ├── templates/
│       │   └── questions_template.xlsx     # Excel template for download
│       └── images/
│           └── questions/                  # All question-related images
│               ├── 1_q.png                 # Question id=1, question image
│               ├── 1_e.png                 # Question id=1, explanation image
│               ├── 2_q.png
│               └── ...
│
├── migrations/
├── instance/
│   └── logicboost.db
│
├── .env
├── .env.example
├── .gitignore
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

## 🗄️ Database Schema

### Table: `questions`
> Stores pure question content. Independent of how it is displayed.
> English is the default language. Vietnamese fields are optional — falls back to English if null.

```sql
CREATE TABLE questions (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,

    -- English content (required)
    title                 TEXT NOT NULL,          -- Short title (English)
    question              TEXT NOT NULL,          -- Full question body (English, Markdown + LaTeX)
    explanation           TEXT NOT NULL,          -- Step-by-step explanation (English, Markdown + LaTeX)

    -- Vietnamese content (optional, fallback to English if null)
    title_vi              TEXT,                   -- Short title (Vietnamese)
    question_vi           TEXT,                   -- Full question body (Vietnamese, Markdown + LaTeX)
    explanation_vi        TEXT,                   -- Step-by-step explanation (Vietnamese, Markdown + LaTeX)

    -- Images (shared across languages)
    -- Naming convention: {id}_q.png / {id}_e.png
    question_image        TEXT,                   -- Image shown in the question body
    explanation_image     TEXT,                   -- Image shown in the explanation

    -- Answer options (shared across languages)
    -- Leave null if question is used as free_text
    option_a              TEXT,
    option_b              TEXT,
    option_c              TEXT,
    option_d              TEXT,

    -- Correct answer
    -- multiple_choice → 'a', 'b', 'c', or 'd'
    -- free_text       → exact text string to compare against
    answer                TEXT NOT NULL,

    -- Metadata
    mode                  TEXT NOT NULL,          -- 'daily_challenge', 'mini_game', 'real_world'
    sub_category          TEXT,                   -- 'finance', 'career', 'business' (real_world only)
    difficulty            INTEGER DEFAULT 1,      -- 1 (easy) → 3 (hard)
    time_limit            INTEGER,                -- Seconds (mini_game only, null = no limit)

    created_at            DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `user_answers`
> Stores the user's answer history, including the question type used.

```sql
CREATE TABLE user_answers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id     INTEGER NOT NULL,       -- FK → questions.id
    question_type   TEXT NOT NULL,          -- 'multiple_choice' or 'free_text'
    chosen          TEXT NOT NULL,          -- 'a','b','c','d' or free text input
    is_correct      BOOLEAN NOT NULL,
    time_taken      INTEGER,                -- Seconds taken to answer
    answered_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `stats`
> Tracks total correct/incorrect answers per mode.

```sql
CREATE TABLE stats (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    mode          TEXT NOT NULL UNIQUE,     -- 'daily_challenge', 'mini_game', 'real_world'
    correct       INTEGER DEFAULT 0,        -- Total correct answers
    incorrect     INTEGER DEFAULT 0,        -- Total incorrect answers
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🖼️ Image Handling

### Naming Convention
```
Format:  {id}_{type}.{ext}

{id}   → question ID in the database (e.g. 1, 2, 42)
{type} → q (question image) or e (explanation image)
{ext}  → png or webp

Examples:
  1_q.png    → Question id=1, image shown in question body
  1_e.png    → Question id=1, image shown in explanation
  42_q.png   → Question id=42, image shown in question body
```

### Image Fields — When to Use
| Field | Position | Use when |
|-------|----------|----------|
| `question_image` | Inside question body | Chart/table the user must read to answer |
| `explanation_image` | Inside explanation | Diagram that helps illustrate the solution |

> Images are **shared across languages** — no need to duplicate per language.

### Generating Image Filenames in Code
```python
question_image    = f"{question.id}_q.png"
explanation_image = f"{question.id}_e.png"
```

### Rendering Images in Templates
```html
{% if question.question_image %}
<div class="question-image">
    <img src="{{ url_for('static', filename='images/questions/' + question.question_image) }}"
         alt="Question diagram">
</div>
{% endif %}

{% if question.explanation_image %}
<div class="explanation-image">
    <img src="{{ url_for('static', filename='images/questions/' + question.explanation_image) }}"
         alt="Explanation diagram">
</div>
{% endif %}
```

### Image Rules
```
✅ Format: PNG or WebP
✅ Max width: 800px
✅ Max file size: 200KB
✅ Filename must follow {id}_{type}.png convention
❌ No spaces or special characters in filename
❌ Do not use images for content that can be written in Markdown
```

---

## 📝 Markdown + LaTeX Rendering

All text fields (`question`, `question_vi`, `explanation`, `explanation_vi`) support **Markdown** and **LaTeX math expressions**.

- **Markdown** (via `marked.js`) — handles text formatting: bold, lists, tables, headings
- **LaTeX** (via `KaTeX`) — handles math symbols and formulas

### Syntax Rules

| Purpose | Syntax | Example |
|---------|--------|---------|
| Bold text | `**text**` | `**10,000,000 VNĐ**` |
| Italic | `*text*` | `*note*` |
| Bullet list | `- item` | `- $r$ = interest rate` |
| Table | `\| col \|` | Bank comparison table |
| Inline math | `$...$` | `$r = 0.06$` |
| Block math (centered) | `$$...$$` | `$$FV = PV \times (1+r)^n$$` |
| Text inside math | `\text{}` | `$$\text{Số tiền} = PV \times r$$` |

> **Note:** When writing Vietnamese inside a math expression (`$...$` or `$$...$$`), always wrap it in `\text{...}`. Outside math expressions, Vietnamese can be typed normally.

### Example Content Stored in DB

```
You have **10,000,000 VNĐ** deposited at a **compound interest rate of 6%/year**.

The compound interest formula is:

$$FV = PV \times (1 + r)^n$$

Where:
- $PV$ = Initial principal
- $r$ = Annual interest rate
- $n$ = Number of years

**After 3 years**, how much total money will you receive?
```

### Setup in Templates

```html
<!-- base.html — load both libraries once -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex/dist/contrib/auto-render.min.js"></script>
```

```html
<!-- question.html — render Markdown first, then KaTeX -->
<script>
    const el = document.getElementById('question');

    // Step 1: Render Markdown → HTML
    el.innerHTML = marked.parse(`{{ question_content | safe }}`);

    // Step 2: Render LaTeX math inside the rendered HTML
    renderMathInElement(el, {
        delimiters: [
            { left: "$$", right: "$$", display: true  },  // block formula
            { left: "$",  right: "$",  display: false }   // inline formula
        ]
    });
</script>
```

---

## 🌐 Bilingual Support (EN / VI)

### Language Fallback Logic

If a Vietnamese translation is not provided, the system automatically falls back to English.

```python
# services/question_service.py

def get_question_by_lang(question, lang='en'):
    """
    Return question content in the requested language.
    Falls back to English if the Vietnamese translation is not available.
    """
    if lang == 'vi':
        return {
            'title':       question.title_vi or question.title,
            'question':    question.question_vi or question.question,
            'explanation': question.explanation_vi or question.explanation,
        }
    return {
        'title':       question.title,
        'question':    question.question,
        'explanation': question.explanation,
    }
```

### Language Switch on Frontend

```html
<!-- Language toggle buttons -->
<button onclick="switchLang('en')">EN</button>
<button onclick="switchLang('vi')">VI</button>
```

```javascript
// Fetch and re-render question content in the selected language
function switchLang(lang) {
    fetch(`/api/question/${questionId}?lang=${lang}`)
        .then(res => res.json())
        .then(data => {
            const el = document.getElementById('question');

            // Step 1: Render Markdown
            el.innerHTML = marked.parse(data.question);

            // Step 2: Render LaTeX
            renderMathInElement(el, {
                delimiters: [
                    { left: "$$", right: "$$", display: true  },
                    { left: "$",  right: "$",  display: false }
                ]
            });
        });
}
```

---

## 🎨 Rendering by `question_type`

Same question, different `question_type` → different UI:

```html
{% if question_type == 'multiple_choice' %}
    <div class="options">
        <button onclick="selectAnswer('a')">A. {{ question.option_a }}</button>
        <button onclick="selectAnswer('b')">B. {{ question.option_b }}</button>
        <button onclick="selectAnswer('c')">C. {{ question.option_c }}</button>
        <button onclick="selectAnswer('d')">D. {{ question.option_d }}</button>
    </div>

{% elif question_type == 'free_text' %}
    <div class="free-text-input">
        <input type="text" id="user-answer" placeholder="Type your answer here...">
        <button onclick="submitAnswer()">Submit</button>
    </div>
{% endif %}
```

---

## ✅ Answer Checking

```python
# services/score_service.py

def check_answer(question, user_input, question_type):
    if question_type == 'multiple_choice':
        return user_input.lower() == question.answer.lower()

    elif question_type == 'free_text':
        def normalize(text):
            return text.replace(',', '').replace(' ', '').replace('.', '').lower()
        return normalize(user_input) == normalize(question.answer)

def update_stats(mode, is_correct):
    # UPDATE stats SET correct/incorrect += 1 WHERE mode = ?
    pass
```

---

## 🛠️ Admin Panel

### Routes (`routes/admin.py`)
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/admin` | Dashboard — question list |
| GET | `/admin/question/new` | Form to add a new question |
| POST | `/admin/question/new` | Save new question to DB |
| GET | `/admin/question/<id>/edit` | Form to edit a question |
| POST | `/admin/question/<id>/edit` | Update question |
| GET | `/admin/question/<id>/delete` | Delete question |
| GET | `/admin/import` | Excel upload page |
| POST | `/admin/import` | Process Excel file → import to DB |
| GET | `/admin/import/template` | Download Excel template |

### Add Question Form (`admin/question_form.html`)
```
# ── English (required) ──────────────────────────
Title (EN)          : [                    ]
Question (EN)       : [                    ] ← Markdown + LaTeX editor
Explanation (EN)    : [                    ] ← Markdown + LaTeX editor

# ── Vietnamese (optional) ────────────────────────
Title (VI)          : [                    ]
Question (VI)       : [                    ] ← Markdown + LaTeX editor
Explanation (VI)    : [                    ] ← Markdown + LaTeX editor

# ── Shared fields ────────────────────────────────
Question img        : [ Choose file ]
Option A            : [          ]
Option B            : [          ]
Option C            : [          ]
Option D            : [          ]  ← Leave blank for free_text
Answer              : [          ]  ← 'a/b/c/d' or exact text
Explanation img     : [ Choose file ]
Mode                : [ daily_challenge ▼ ]
Sub-category        : [ finance ▼ ]
Difficulty          : [ 1 ▼ ]
Time limit          : [    ] seconds
```

### Import Excel (`admin/import_excel.html`)
```
1. Download template   → [ Download Template ]
2. Fill in questions in the template file
3. Upload file         → [ Choose .xlsx file ] [ Import ]
4. View results        → "✅ 10 questions imported, ❌ 2 errors"
```

### Excel Template Format
Columns in `questions_template.xlsx`:

| Column | Required | Notes |
|--------|----------|-------|
| `title` | ✅ | English |
| `title_vi` | | Vietnamese, fallback to `title` if empty |
| `question` | ✅ | English, Markdown + LaTeX supported |
| `question_vi` | | Vietnamese, Markdown + LaTeX supported |
| `option_a` | | Leave blank for free_text |
| `option_b` | | Leave blank for free_text |
| `option_c` | | Leave blank for free_text |
| `option_d` | | Leave blank for free_text |
| `answer` | ✅ | a/b/c/d or exact text |
| `explanation` | ✅ | English, Markdown + LaTeX supported |
| `explanation_vi` | | Vietnamese, Markdown + LaTeX supported |
| `mode` | ✅ | daily_challenge / mini_game / real_world |
| `sub_category` | | finance / career / business |
| `difficulty` | | 1 / 2 / 3 |
| `time_limit` | | Seconds; leave blank for no limit |

> **Note:** `question_image` and `explanation_image` are **not included in the Excel file**.
> Upload images manually to `/static/images/questions/` after importing, following the `{id}_q.png` / `{id}_e.png` naming convention.

### Import Service (`services/import_service.py`)
```python
import openpyxl

def import_from_excel(filepath):
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active

    results = {'success': 0, 'errors': []}

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        title, title_vi, question, question_vi, \
        option_a, option_b, option_c, option_d, \
        answer, explanation, explanation_vi, \
        mode, sub_category, difficulty, time_limit = row

        # Validate required fields
        if not all([title, question, answer, explanation, mode]):
            results['errors'].append(f"Row {row_idx}: Missing required fields")
            continue

        # Validate mode
        if mode not in ['daily_challenge', 'mini_game', 'real_world']:
            results['errors'].append(f"Row {row_idx}: Invalid mode '{mode}'")
            continue

        # Insert into DB
        db.execute('''
            INSERT INTO questions (
                title, title_vi,
                question, question_vi,
                option_a, option_b, option_c, option_d,
                answer,
                explanation, explanation_vi,
                mode, sub_category, difficulty, time_limit
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (title, title_vi,
              question, question_vi,
              option_a, option_b, option_c, option_d,
              answer,
              explanation, explanation_vi,
              mode, sub_category, difficulty or 1, time_limit))

        results['success'] += 1

    return results
```

---

## 🎮 Feature Specifications

### 1. 📅 Daily Challenges
- Exactly **5 questions** per daily set
- Difficulty increases: Easy → Medium → Hard
- Estimated completion time: **7–10 minutes**
- New question set every day
- Summary screen: score, time taken, wrong answer review

### 2. ⚡ Quick Mini Games
- Each problem solvable in **30–60 seconds**
- Answer questions continuously until you get one wrong (Sudden Death mode)
- Score = number of correct answers in a row
- Large countdown timer, instant visual feedback
- Immediate game over on first wrong answer

### 3. 🌍 Real-world Problems
- Sub-categories: **Finance / Career / Business**
- Every question has real numbers that can be calculated
- Explanation shows step-by-step calculation
- Scenarios relatable to Vietnamese working adults

---

## 📐 Coding Guidelines

### General
- Write all comments in English
- Keep functions small and single-purpose
- Always validate user input before processing
- Never hardcode values — use constants or config files

### Flask
- Use **Blueprints** — one Blueprint per feature
- API routes return JSON; page routes return HTML
- Handle all errors with proper HTTP status codes
- Use Flask-Migrate for all database schema changes

### Frontend
- Mobile-first responsive design
- Vanilla JavaScript only — no heavy frameworks for MVP
- Show loading state when fetching data
- CSS animations for answer feedback (correct = green flash, wrong = red shake)
- Mini game timer must be visually prominent and accurate

---

## 🔧 Environment Variables (.env)
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/logicboost.db
```

---

## ❌ Out of Scope for MVP

- **User Authentication / Accounts** — Allows users to register and log in with a personal account. Enables saving personal progress, answer history, and preferences across sessions. Requires secure password handling, session management, and potentially OAuth (e.g. Google login). Adds significant complexity to the data model and security requirements.

- **Leaderboard & Social Features** — Displays a ranked list of top-performing users based on score, speed, or accuracy. Includes social interactions such as following other users, comparing results with friends, and sharing achievements. Depends on user accounts being implemented first and requires real-time or near-real-time data updates.

- **Streak Tracking & Push Notifications** — Tracks how many consecutive days a user has completed a daily challenge and rewards consistency. Push notifications remind users to return each day to maintain their streak. Requires a user account system, a background job scheduler, and integration with a notification service (e.g. Firebase Cloud Messaging).

- **Payment / Subscription Model** — Introduces a paywall for premium content or an ad-free experience. Requires integration with a payment gateway (e.g. Stripe), subscription lifecycle management, and enforcement of access tiers across the app. Significant legal, financial, and UX complexity.

- **Community Sharing (Moderated)** — Allows users to submit their own problems for others to solve. All submissions must be reviewed and approved by an admin before being published. Ensures content quality, accuracy, and relevance while enabling community-driven contributions and collaborative learning.

- **Game Theory Lite** — Introduces simplified strategic challenges inspired by game theory, enabling users to practice decision-making and strategic thinking in an intuitive and accessible way. Scenarios may include classic concepts such as the Prisoner's Dilemma, Nash Equilibrium, and zero-sum games, presented in relatable real-life contexts. Requires a dedicated question type, custom UI for multi-agent decision trees, and more complex answer evaluation logic beyond simple right/wrong comparisons.

---

## ✅ Code Quality Rules
- No hardcoded values — use config.py or constants
- All calculation logic must live in `services/calculator.py`
- All Excel import logic must live in `services/import_service.py`
- Every Blueprint must have its own error handler
- All tests must pass before committing