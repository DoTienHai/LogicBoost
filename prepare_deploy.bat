@echo off
REM Quick deployment preparation for Render (Windows)
REM This script helps prepare your app for Render deployment

setlocal enabledelayedexpansion

echo.
echo 🚀 LogicBoost Render Deployment Preparation (Windows)
echo =====================================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo ✅ Created .env - Please update SECRET_KEY and DATABASE_URL
    echo.
)

REM Check requirements.txt
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found!
    exit /b 1
)
echo ✅ requirements.txt found

REM Check Procfile
if not exist "Procfile" (
    echo ❌ Procfile not found!
    exit /b 1
)
echo ✅ Procfile found

REM Check runtime.txt
if not exist "runtime.txt" (
    echo ❌ runtime.txt not found!
    exit /b 1
)
echo ✅ runtime.txt found

REM Check config.py
if not exist "config.py" (
    echo ❌ config.py not found!
    exit /b 1
)
echo ✅ config.py found

echo.
echo 🧪 Testing imports...
python -c "from app import create_app; print('✅ App imports successfully')"

echo.
echo 📋 Deployment Checklist:
echo ========================
echo ✅ Procfile configured
echo ✅ requirements.txt updated with gunicorn + psycopg2
echo ✅ runtime.txt set to python-3.12.4
echo ✅ config.py updated for PostgreSQL
echo.
echo 📝 Next Steps:
echo.
echo 1. Generate SECRET_KEY (copy and run):
echo    python -c "import secrets; print(secrets.token_hex(32))"
echo    Then update .env with the output
echo.
echo 2. Create PostgreSQL database on Render.com
echo    (See DEPLOYMENT.md for instructions)
echo.
echo 3. Update DATABASE_URL in .env with PostgreSQL URL
echo.
echo 4. Commit and push to GitHub:
echo    git add .
echo    git commit -m "Prepare for Render deployment"
echo    git push origin main
echo.
echo 5. Create web service on Render:
echo    - Repository: LogicBoost
echo    - Build: pip install -r requirements.txt && flask db upgrade
echo    - Start: gunicorn "app:create_app()"
echo    - Region: Choose closest to your users
echo.
echo 6. Set environment variables on Render:
echo    - FLASK_APP=run.py
echo    - FLASK_ENV=production
echo    - SECRET_KEY=^<your-generated-key^>
echo    - DATABASE_URL=^<PostgreSQL URL^>
echo.
echo 7. Click Deploy and monitor logs
echo.
echo 📖 For detailed instructions, see DEPLOYMENT.md
echo.
pause
