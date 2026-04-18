#!/bin/bash
# Quick deployment preparation for Render
# This script helps prepare your app for Render deployment

set -e

echo "🚀 LogicBoost Render Deployment Preparation"
echo "============================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env - Please update SECRET_KEY and DATABASE_URL"
fi

# Check requirements.txt
if [ ! -f requirements.txt ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo "✅ requirements.txt found"

# Check Procfile
if [ ! -f Procfile ]; then
    echo "❌ Procfile not found!"
    exit 1
fi

echo "✅ Procfile found"

# Check runtime.txt
if [ ! -f runtime.txt ]; then
    echo "❌ runtime.txt not found!"
    exit 1
fi

echo "✅ runtime.txt found"

# Check config.py
if [ ! -f config.py ]; then
    echo "❌ config.py not found!"
    exit 1
fi

echo "✅ config.py found"

# Test imports
echo ""
echo "🧪 Testing imports..."
python -c "from app import create_app; print('✅ App imports successfully')"

# Check if git is initialized
if [ ! -d .git ]; then
    echo ""
    echo "⚠️  Git repository not initialized"
    echo "Run: git init && git add . && git commit -m 'Initial commit'"
else
    echo "✅ Git repository found"
fi

echo ""
echo "📋 Deployment Checklist:"
echo "========================"
echo "✅ Procfile configured"
echo "✅ requirements.txt updated with gunicorn + psycopg2"
echo "✅ runtime.txt set to python-3.12.4"
echo "✅ config.py updated for PostgreSQL"
echo ""
echo "📝 Next Steps:"
echo "1. Update SECRET_KEY in .env:"
echo "   python -c \"import secrets; print(secrets.token_hex(32))\""
echo ""
echo "2. Create PostgreSQL database on Render.com"
echo ""
echo "3. Update DATABASE_URL in .env with PostgreSQL URL"
echo ""
echo "4. Push to GitHub:"
echo "   git add ."
echo "   git commit -m \"Prepare for Render deployment\""
echo "   git push origin main"
echo ""
echo "5. Create web service on Render:"
echo "   - Repository: LogicBoost"
echo "   - Build: pip install -r requirements.txt && flask db upgrade"
echo "   - Start: gunicorn \"app:create_app()\""
echo ""
echo "6. Set environment variables on Render:"
echo "   - FLASK_APP=run.py"
echo "   - FLASK_ENV=production"
echo "   - SECRET_KEY=<generated key>"
echo "   - DATABASE_URL=<PostgreSQL URL>"
echo ""
echo "7. Deploy and monitor logs"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
