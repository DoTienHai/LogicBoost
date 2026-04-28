# LogicBoost — Copilot Instructions

## � Table of Contents

1. [📌 Project Overview](#-project-overview)
2. [🎯 Core Concept](#-core-concept)
3. [🛠️ Tech Stack](#-tech-stack)
4. [📁 Project Structure](#-project-structure)
5. [🗄️ Database Schema](#-database-schema)
6. [� Authentication & Authorization](#-authentication--authorization)
7. [🖼️ Image Handling](#-image-handling)
8. [📝 Markdown + LaTeX Rendering](#-markdown--latex-rendering)
9. [🌐 Bilingual Support (EN / VI)](#-bilingual-support-en--vi)
10. [🎨 Rendering by `question_type`](#-rendering-by-question_type)
11. [✅ Answer Checking](#-answer-checking)
12. [🛠️ Admin Panel](#-admin-panel)
13. [🎮 Feature Specifications](#-feature-specifications)
14. [🌐 API Routing Rules](#-api-routing-rules)
15. [📐 Coding Guidelines](#-coding-guidelines)
16. [🔧 Environment Variables (.env)](#-environment-variables-env)
17. [❌ Out of Scope for MVP](#-out-of-scope-for-mvp)
18. [✅ Code Quality Rules](#-code-quality-rules)

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
│   │   ├── auth.py                         # Authentication routes (login, register, logout)
│   │   ├── daily_challenge.py              # Daily Challenge routes
│   │   ├── mini_game.py                    # Quick Mini Game routes
│   │   ├── real_world.py                   # Real-world Problem routes
│   │   ├── admin_questions.py              # Admin question management routes
│   │   └── admin_users.py                  # Admin user management routes
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                         # User model with password hashing
│   │   ├── role.py                         # Role model (admin, content_creator, user)
│   │   ├── permission.py                   # Permission model
│   │   ├── question.py                     # Question model
│   │   ├── user_answer.py                  # User answer model
│   │   ├── difficulty.py                   # Difficulty enum
│   │   ├── stats.py                        # Stats model
│   │   └── sub_category.py                 # SubCategory model
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py                 # Authentication & user management
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
│   │   ├── auth/
│   │   │   ├── login.html                  # Login page
│   │   │   ├── register.html               # User registration page
│   │   │   └── profile.html                # User profile & settings
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
│   │   │   ├── index.html                  # Admin dashboard (question list)
│   │   │   ├── question_form.html          # Add / edit single question
│   │   │   ├── import_excel.html           # Upload Excel file
│   │   │   ├── users.html                  # User management list
│   │   │   ├── user_form.html              # Add / edit user and assign roles
│   │   │   └── roles.html                  # Role & permission management
│   │   └── error.html
│   │
│   └── static/
│       ├── css/
│       │   ├── main.css
│       │   ├── auth.css
│       │   ├── daily_challenge.css
│       │   ├── mini_game.css
│       │   ├── real_world.css
│       │   └── admin.css
│       ├── js/
│       │   ├── main.js
│       │   ├── auth.js
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

### Table: `users`
> Stores user account information with secure password hashing.

```sql
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,           -- Unique login identifier
    email           TEXT NOT NULL UNIQUE,           -- Email for contact
    password_hash   TEXT NOT NULL,                  -- Hashed password (bcrypt)
    first_name      TEXT,                           -- User's first name
    last_name       TEXT,                           -- User's last name
    is_active       BOOLEAN DEFAULT 1,              -- Account enabled/disabled
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `roles`
> Stores user roles with permissions. Three default roles: admin, content_creator, user.

```sql
CREATE TABLE roles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,          -- 'admin', 'content_creator', 'user'
    display_name    TEXT NOT NULL,                 -- Display label
    description     TEXT,                          -- Role purpose
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Seed Data:**
```python
# Default roles
Role.create(name='admin', display_name='Administrator', description='Full access to all features and user management')
Role.create(name='content_creator', display_name='Content Creator', description='Can manage questions and import Excel')
Role.create(name='user', display_name='User', description='Can only play games and view questions')
```

### Table: `permissions`
> Stores individual permissions that can be assigned to roles.

```sql
CREATE TABLE permissions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,          -- 'view_questions', 'edit_questions', 'manage_users'
    display_name    TEXT NOT NULL,                 -- Human readable
    description     TEXT,                          -- What this permission allows
    category        TEXT,                          -- 'content', 'user_management', 'system'
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Seed Data:**
```python
# Content Permissions
Permission.create(name='view_questions', display_name='View Questions', category='content')
Permission.create(name='create_questions', display_name='Create Questions', category='content')
Permission.create(name='edit_questions', display_name='Edit Questions', category='content')
Permission.create(name='delete_questions', display_name='Delete Questions', category='content')
Permission.create(name='import_excel', display_name='Import Excel', category='content')

# User Management Permissions
Permission.create(name='view_users', display_name='View Users', category='user_management')
Permission.create(name='create_users', display_name='Create Users', category='user_management')
Permission.create(name='edit_users', display_name='Edit Users', category='user_management')
Permission.create(name='delete_users', display_name='Delete Users', category='user_management')
Permission.create(name='assign_roles', display_name='Assign Roles', category='user_management')

# System Permissions
Permission.create(name='manage_roles', display_name='Manage Roles', category='system')
Permission.create(name='manage_permissions', display_name='Manage Permissions', category='system')
```

### Table: `role_permissions` (Junction)
> Many-to-many relationship between roles and permissions.

```sql
CREATE TABLE role_permissions (
    role_id         INTEGER NOT NULL,
    permission_id   INTEGER NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);
```

### Table: `user_roles` (Junction)
> Many-to-many relationship between users and roles. A user can have multiple roles.

```sql
CREATE TABLE user_roles (
    user_id         INTEGER NOT NULL,
    role_id         INTEGER NOT NULL,
    assigned_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);
```

### Table: `sub_categories`
> Stores categorization options for real-world questions. Allows admin to manage categories flexibly.

```sql
CREATE TABLE sub_categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,   -- 'finance', 'career', 'business'
    display_name    TEXT NOT NULL,          -- '💰 Finance', '📈 Career', '🏢 Business'
    description     TEXT,                   -- Optional description
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Seed Data:**
```python
# Default categories
SubCategory.create(name='finance', display_name='💰 Finance', description='Personal finance, investments, loans')
SubCategory.create(name='career', display_name='📈 Career', description='Career decisions, job negotiations, skills')
SubCategory.create(name='business', display_name='🏢 Business', description='Business strategies, management, entrepreneurship')
```

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

    -- Answer options (optional - for future use)
    option_a              TEXT,                   -- Optional (leave null for free-text)
    option_b              TEXT,                   -- Optional (leave null for free-text)
    option_c              TEXT,                   -- Optional (leave null for free-text)
    option_d              TEXT,                   -- Optional (leave null for free-text)

    -- Correct answer (FREE-TEXT OR MULTIPLE CHOICE)
    -- For multiple choice: 'a', 'b', 'c', or 'd'
    -- For free-text: exact text user must enter (case-insensitive, punctuation-normalized)
    answer                TEXT NOT NULL,

    -- Metadata
    mode                  TEXT NOT NULL,          -- 'daily_challenge', 'mini_game', 'real_world'
    sub_category_id       INTEGER,                -- FK → sub_categories.id (only for real_world mode)
    difficulty            INTEGER DEFAULT 1,      -- 1-5: Very Easy, Easy, Medium, Hard, Very Hard
    time_limit            INTEGER,                -- Seconds (mini_game only, null = no limit)

    created_at            DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sub_category_id) REFERENCES sub_categories(id) ON DELETE SET NULL
);
```

### Difficulty Level Enum

**Location:** `app/models/difficulty.py`

Difficulty levels are defined as an enum with 5 levels (1-5). The `difficulty` column in `questions` table stores integer values 1-5:

| Value | Name | Emoji | Description |
|-------|------|-------|-------------|
| 1 | VERY_EASY | 🟢 | Basic concept, obvious solution |
| 2 | EASY | 🟡 | Straightforward problem, minor calculation |
| 3 | MEDIUM | 🟠 | Requires some thought, multiple steps |
| 4 | HARD | 🔴 | Complex logic, advanced concepts |
| 5 | VERY_HARD | ⚫ | Expert level, tricky edge cases |

**Usage in Code:**
```python
from app.models import DifficultyLevel

# Create question with difficulty
question = Question(
    title="...",
    difficulty=DifficultyLevel.MEDIUM.value,  # or just 3
    ...
)

# Convert to readable string
level = DifficultyLevel.from_value(3)
print(level)           # "Medium"
print(level.emoji)     # "🟠"
print(int(level))      # 3
```

### Table: `user_answers`
> Stores the user's answer history, including the question type used.

```sql
CREATE TABLE user_answers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,       -- FK → users.id (WHO answered)
    question_id     INTEGER NOT NULL,       -- FK → questions.id (WHAT question)
    question_type   TEXT NOT NULL,          -- 'multiple_choice' or 'free_text'
    mode            TEXT NOT NULL,          -- 'daily_challenge', 'mini_game', 'real_world' (WHERE answered)
    chosen          TEXT NOT NULL,          -- 'a','b','c','d' or free text input
    is_correct      BOOLEAN NOT NULL,
    time_taken      INTEGER,                -- Seconds taken to answer
    answered_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);
```

### Table: `stats`
> Tracks total correct/incorrect answers per mode per user.

```sql
CREATE TABLE stats (
    user_id       INTEGER NOT NULL,        -- FK → users.id (Whose stats)
    mode          TEXT NOT NULL,           -- 'daily_challenge', 'mini_game', 'real_world'
    correct       INTEGER DEFAULT 0,       -- Total correct answers
    incorrect     INTEGER DEFAULT 0,       -- Total incorrect answers
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (user_id, mode),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## � Authentication & Authorization

### User Registration & Login
- Users self-register with **email** and **password**
- Passwords hashed with **bcrypt** (not stored plain text)
- Session-based authentication using Flask-Login
- Login required for all features except viewing home page

### Default Admin User
On first app startup, create a default admin account:
```python
# app/__init__.py
if not User.query.filter_by(username='admin').first():
    admin_user = User(
        username='admin',
        email='admin@logicboost.local',
        password='admin123',  # Must be changed in production!
        first_name='Admin',
        is_active=True
    )
    admin_role = Role.query.filter_by(name='admin').first()
    admin_user.roles.append(admin_role)
    db.session.add(admin_user)
    db.session.commit()
```

### Role-Based Access Control (RBAC)
Three default roles with different permission levels:

| Role | Description | Can Do |
|------|-------------|--------|
| **Admin** | Full system access | Manage users, roles, permissions, content, all game features |
| **Content Creator** | Question management | Create/edit/delete questions, import Excel, play games |
| **User** | Player only | Play daily challenges, mini games, real-world problems |

### Permission System
Permissions are granular and assigned to roles:
- **Content:** view_questions, create_questions, edit_questions, delete_questions, import_excel
- **User Management:** view_users, create_users, edit_users, delete_users, assign_roles
- **System:** manage_roles, manage_permissions

### Decorators & Route Protection
```python
# Use Flask-Login decorators
from flask_login import login_required, current_user

# Protect routes
@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

# Check specific permissions
def require_permission(permission_name):
    def decorator(f):
        @functools.wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission_name):
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@admin_bp.route('/admin/users')
@require_permission('view_users')
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)
```

### Authentication Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/auth/login` | Login page |
| POST | `/auth/login` | Process login |
| GET | `/auth/register` | Registration page |
| POST | `/auth/register` | Create new user |
| GET | `/auth/logout` | Logout & destroy session |
| GET | `/auth/profile` | View/edit own profile |
| POST | `/auth/profile` | Update profile |

### User Management Routes (Admin Only)
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/admin/users` | List all users |
| GET | `/admin/users/<id>` | View user details |
| GET | `/admin/users/<id>/edit` | Edit user form |
| POST | `/admin/users/<id>/edit` | Update user |
| DELETE | `/admin/users/<id>` | Delete user |
| POST | `/admin/users/<id>/assign-role` | Add role to user |
| DELETE | `/admin/users/<id>/remove-role/<role_id>` | Remove role from user |

### Auth Service (`services/auth_service.py`)
```python
class AuthService:
    @staticmethod
    def register_user(username, email, password, first_name='', last_name=''):
        """Register a new user with default 'user' role"""
        # Validate username/email unique
        # Hash password
        # Create user
        # Assign default 'user' role
        
    @staticmethod
    def login_user(username, password):
        """Authenticate user and return user object or None"""
        # Find user by username
        # Verify password
        # Return user if valid
        
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password"""
        
    @staticmethod
    def assign_role(user_id, role_id):
        """Assign a role to a user"""
        
    @staticmethod
    def revoke_role(user_id, role_id):
        """Remove a role from a user"""
```

---

## �🖼️ Image Handling

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

---

## 🎫 Frontend Permission System

### Permission Check in Templates

All templates must verify user permissions before displaying admin features:

```html
<!-- Navigation link - only show to admin users -->
{% if current_user.is_authenticated and current_user.has_permission('view_questions') %}
    <li><a href="{{ url_for('admin_questions.index') }}">⚙️ Admin</a></li>
{% endif %}

<!-- Admin buttons - only show if user can create -->
{% if current_user.has_permission('create_questions') %}
    <a href="{{ url_for('admin_questions.add_question_get') }}" class="btn btn-primary">
        Add New Question
    </a>
{% endif %}

<!-- Edit/Delete actions - verify permission -->
{% if current_user.has_permission('edit_questions') %}
    <a href="{{ url_for('admin_questions.edit_question_get', question_id=q.id) }}" class="btn btn-sm">
        Edit
    </a>
{% endif %}

{% if current_user.has_permission('delete_questions') %}
    <form method="POST" action="{{ url_for('admin_questions.delete_question', question_id=q.id) }}">
        <button type="submit" class="btn btn-sm btn-danger">Delete</button>
    </form>
{% endif %}
```

### User Model - Permission Check Method

```python
# In app/models/user.py
class User(UserMixin, db.Model):
    ...
    def has_permission(self, permission_name):
        """Check if user has a specific permission."""
        for role in self.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        return False
```

### Backend Route Protection

All admin routes have `@require_permission` decorators:

```python
# In app/routes/admin_questions.py
@admin_questions_bp.route("/question/new", methods=["GET"])
@login_required
@require_permission("create_questions")
def add_question_get():
    """Display add question form."""
    return render_template("admin/question_form.html")
```

### Permission Hierarchy

| Permission | Required Role | Used For |
|-----------|---------------|----------|
| `view_questions` | User+ | View admin dashboard |
| `create_questions` | Content Creator+ | Add new questions |
| `edit_questions` | Content Creator+ | Edit questions |
| `delete_questions` | Admin | Delete questions |
| `import_excel` | Content Creator+ | Import Excel file |
| `view_users` | Admin | View user list |
| `create_users` | Admin | Create new users |
| `edit_users` | Admin | Edit user details |
| `delete_users` | Admin | Delete users |
| `assign_roles` | Admin | Manage user roles |
| `manage_roles` | Admin | Create/edit roles |
| `manage_permissions` | Admin | Create/edit permissions |

### Frontend - Unauthorized Access Handling

If user navigates directly to an admin URL without permission:
1. Backend `@require_permission` decorator returns **403 Forbidden**
2. User sees error page
3. Backend logs unauthorized access attempt

---

## 🛠️ Admin Panel

### Separated Blueprints

Admin functionality is split into two blueprints for better organization:

#### **Question Management** (`routes/admin_questions.py`)
- Dashboard: `/admin/` - List all questions
- Add question: `/admin/question/new` - Create new questions
- Edit question: `/admin/question/<id>/edit` - Modify questions
- Delete question: `/admin/question/<id>/delete` - Remove questions
- Import Excel: `/admin/import` - Bulk import from Excel file
- Download template: `/admin/import/template` - Get Excel template

**Permissions Required:**
- `view_questions` - Dashboard access
- `create_questions` - Add/import questions
- `edit_questions` - Modify questions
- `delete_questions` - Delete questions
- `import_excel` - Import Excel files

#### **User Management** (`routes/admin_users.py`)
- List users: `/admin/users` - View all users
- View user: `/admin/users/<id>` - User details & roles
- Create user: `/admin/users/create` - Register new user
- Edit user: `/admin/users/<id>/edit` - Update user info
- Delete user: `/admin/users/<id>/delete` - Remove user
- Assign role: `/admin/users/<id>/assign-role` - Add role to user
- Remove role: `/admin/users/<id>/remove-role/<role_id>` - Remove role

**Permissions Required:**
- `view_users` - List users
- `create_users` - Create users
- `edit_users` - Edit user details
- `delete_users` - Delete users
- `assign_roles` - Manage user roles

### Admin Panel Routes

#### Question Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/admin` | Dashboard — question list |
| GET | `/admin/question/new` | Form to add a new question |
| POST | `/admin/question/new` | Save new question to DB |
| GET | `/admin/question/<id>/edit` | Form to edit a question |
| POST | `/admin/question/<id>/edit` | Update question |
| POST | `/admin/question/<id>/delete` | Delete question |
| GET | `/admin/import` | Excel upload page |
| POST | `/admin/import` | Process Excel file → import to DB |
| GET | `/admin/import/template` | Download Excel template |

#### User Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/admin/users` | List all users |
| GET | `/admin/users/<id>` | View user details |
| GET | `/admin/users/create` | Create user form |
| POST | `/admin/users/create` | Save new user |
| GET | `/admin/users/<id>/edit` | Edit user form |
| POST | `/admin/users/<id>/edit` | Update user |
| POST | `/admin/users/<id>/delete` | Delete user |
| POST | `/admin/users/<id>/assign-role` | Assign role to user |
| POST | `/admin/users/<id>/remove-role/<role_id>` | Remove role from user |

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
| `difficulty` | | 1 / 2 / 3 / 4 / 5 |
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

## 🌐 API Routing Rules

### Golden Rule: Separate GET and POST

**NEVER combine GET and POST in a single route handler.**

❌ **WRONG:**
```python
@bp.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        # Process form
    return render_template("form.html")
```

✅ **CORRECT:**
```python
@bp.route("/form", methods=["GET"])
def form_get():
    """Display form."""
    return render_template("form.html")

@bp.route("/form", methods=["POST"])
def form_post():
    """Process form submission."""
    # Process form
    return redirect(url_for("bp.form_get"))
```

### Naming Convention for Split Routes

**Pattern:** `{resource}_{method_name}()`

| Purpose | Naming | Example |
|---------|--------|---------|
| Display form/page | `{resource}_get()` | `question_form_get()` |
| Process submission | `{resource}_post()` | `question_form_post()` |
| Show detail page | `{resource}_detail()` | `user_detail()` |
| List items | `list_{resources}()` | `list_users()` |
| Show edit form | `{resource}_edit_get()` | `user_edit_get()` |
| Process edit | `{resource}_edit_post()` | `user_edit_post()` |

### Benefits of Separation

| Aspect | Benefit |
|--------|---------|
| **Readability** | Each function has single purpose (GET or POST) |
| **Testability** | Can test GET and POST flows independently |
| **Maintainability** | Easier to locate and modify GET/POST logic |
| **Error Handling** | Form display errors separate from submission errors |
| **Performance** | Can cache GET responses separately from POST |

### URL Routing with Multiple Decorators

For routes that handle both create and edit on the same URL, use defaults:

```python
@bp.route("/items/", defaults={"item_id": None}, methods=["GET"])
@bp.route("/items/<int:item_id>/", methods=["GET"])
def item_get(item_id=None):
    """Display form for creating or editing item."""
    item = None
    if item_id:
        item = Item.query.get_or_404(item_id)
    return render_template("item_form.html", item=item)

@bp.route("/items/", defaults={"item_id": None}, methods=["POST"])
@bp.route("/items/<int:item_id>/", methods=["POST"])
def item_post(item_id=None):
    """Process form for creating or editing item."""
    item = None
    if item_id:
        item = Item.query.get_or_404(item_id)
    
    # ... process form ...
    
    if item_id:
        return redirect(url_for("bp.list_items"))
    else:
        return redirect(url_for("bp.item_get", item_id=new_item.id))
```

### Redirect Pattern

When POST completes successfully, redirect to GET route:

```python
# In POST handler
if success:
    flash("Success message", "success")
    return redirect(url_for("bp.resource_get", resource_id=id))  # ← Use GET route name
```

### Form Handling Pattern

Clean approach: **One function = One HTTP method**

```python
# GET: Display form
@bp.route("/form", methods=["GET"])
def form_get():
    """Display the form."""
    return render_template("form.html", form_data={})


# POST: Process form submission
@bp.route("/form", methods=["POST"])
def form_post():
    """Process form submission."""
    # Validate
    is_valid, errors = validate_data(request.form)
    
    if not is_valid:
        return render_template("form.html", errors=errors, form_data=request.form.to_dict()), 400
    
    # Process...
    
    flash("Success!", "success")
    return redirect(url_for("bp.form_get"))  # Redirect to display version
```

In templates, use specific endpoints:
```html
<!-- Form with specific action -->
<form method="POST" action="{{ url_for('bp.form_post') }}" novalidate>
    ...
</form>

<!-- Links to form -->
<a href="{{ url_for('bp.form_get') }}">Edit</a>
```

**Why no delegation wrapper?**
- ❌ Adds unnecessary indirection
- ❌ Makes debugging harder
- ✅ Each function has clear single purpose
- ✅ Simpler for testing
- ✅ Easier to read and maintain

### Current Status & Implementation

✅ **auth.py** - Fully implemented (clean pattern):
```python
# Each function handles ONE HTTP method only
@auth_bp.route("/login", methods=["GET"])
def login_get():
    return render_template("auth/login.html")

@auth_bp.route("/login", methods=["POST"])
def login_post():
    # Process login
    return redirect(url_for("auth.profile_get"))
```

- `login_get()` (GET) / `login_post()` (POST) ✅
- `profile_get()` (GET) / `profile_post()` (POST) ✅
- `change_password_get()` (GET) / `change_password_post()` (POST) ✅
- `register()` (GET) / `register_submit()` (POST) ✅

✅ **Templates** - Updated:
- All `url_for()` calls use specific endpoints: `url_for('auth.login_get')` not `url_for('auth.login')`
- Form actions specify POST endpoint: `action="{{ url_for('auth.login_post') }}"`

✅ **Configuration** - Updated:
- Flask-Login `login_view` set to `"auth.login_get"` (not `"auth.login"`)

🟡 **admin.py** - Partially implemented:
- `add_question_get()` / `add_question_post()` ✅
- `edit_question_get()` / `edit_question_post()` ✅
- `import_page_get()` / `import_page_post()` ✅
- `user_form()` - Split needed: `user_create_get/post()` and `user_edit_get/post()`

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
- **API Routing**: Always separate GET and POST handlers (see [🌐 API Routing Rules](#-api-routing-rules))

### Frontend
- Mobile-first responsive design
- Vanilla JavaScript only — no heavy frameworks for MVP
- Show loading state when fetching data
- CSS animations for answer feedback (correct = green flash, wrong = red shake)
- Mini game timer must be visually prominent and accurate

---

## 🛑 Error Handling & Error Codes

### Error Constants Location
**File:** `app/constants/error_codes.py`

All error messages must be defined as constants in the `AuthError` class. Never hardcode error strings in services or routes.

### Error Code Format
```python
class AuthError:
    """Authentication error codes and messages."""
    
    USERNAME_EXISTS = {
        "code": "USERNAME_EXISTS",           # Error code (used by frontend)
        "status": 409,                       # HTTP status code
        "message": "Username already exists" # User-facing message
    }
```

### Error Code Categories

| Status | Category | When to Use |
|--------|----------|------------|
| **400** | Bad Request | Validation errors (too short, invalid format, missing field) |
| **401** | Unauthorized | Authentication errors (wrong password, account disabled) |
| **403** | Forbidden | Authorization errors (already logged in, no permission) |
| **404** | Not Found | Resource not found (user, role) |
| **409** | Conflict | Conflict errors (duplicate username, email, role already assigned) |
| **500** | Server Error | Unexpected exceptions during processing |

### Backend — Using Error Constants

**Services** (`app/services/auth_service.py`):
```python
from app.constants.error_codes import AuthError

def register_user(...):
    if User.query.filter_by(username=username).first():
        return None, AuthError.USERNAME_EXISTS["message"]  # Use message
    
    try:
        # ... process
    except Exception as e:
        db.session.rollback()
        return None, AuthError.REGISTRATION_FAILED["message"]
```

**Routes** (`app/routes/auth.py`):
```python
from app.constants.error_codes import AuthError

@auth_bp.route("/register", methods=["POST"])
def register_submit():
    user, error = AuthService.register_user(...)
    
    if error:
        # Find error details by message
        error_detail = AuthError.find_error_by_message(error)
        return jsonify({
            "success": False,
            "error": error_detail["message"],
            "code": error_detail["code"]     # Include error code
        }), error_detail["status"]           # Use appropriate status code
```

### Frontend — Handling Error Codes

```javascript
fetch('/auth/register', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(data => {
    if (data.success) {
        showToast('✓ Success', 'success');
    } else {
        // Handle by error code for better UX
        switch(data.code) {
            case 'USERNAME_EXISTS':
                showToast('Username already taken', 'error');
                break;
            case 'EMAIL_EXISTS':
                showToast('Email already registered', 'error');
                break;
            case 'PASSWORD_TOO_SHORT':
                showToast('Password too short (min 6 chars)', 'error');
                break;
            default:
                showToast(data.error, 'error');
        }
    }
});
```

### Adding New Error Codes

When adding a new error:
1. Add constant to `AuthError` class in `app/constants/error_codes.py`
2. Include: `code`, `status`, `message`
3. Update service to return error message
4. Update route to include error code in JSON response
5. Update tests to check for error code
6. Add frontend handler if needed

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

- **Leaderboard & Social Features** — Displays a ranked list of top-performing users based on score, speed, or accuracy. Includes social interactions such as following other users, comparing results with friends, and sharing achievements. Depends on tracking user stats across sessions and requires real-time or near-real-time data updates.

- **Streak Tracking & Push Notifications** — Tracks how many consecutive days a user has completed a daily challenge and rewards consistency. Push notifications remind users to return each day to maintain their streak. Requires a background job scheduler and integration with a notification service (e.g. Firebase Cloud Messaging).

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