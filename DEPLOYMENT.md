# Deploying LogicBoost to Render

This guide explains how to deploy the LogicBoost application to Render.com

## Quick Option: SQLite (Simplest)

Using SQLite is easiest for getting started:

1. Deploy to Render
2. No database setup needed
3. App uses `instance/logicboost.db` by default
4. **Note**: Data won't persist between restarts (Render's filesystem is ephemeral)

### Deploy with SQLite (3 steps):

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to Render"
git push origin main

# 2. Create Web Service on Render:
# - Repository: LogicBoost
# - Build: pip install -r requirements.txt && flask db upgrade
# - Start: gunicorn "app:create_app()"
# - Set environment: FLASK_ENV=production, SECRET_KEY=<generated>

# 3. Done! Your app will be live at: https://logicboost-xxxxx.onrender.com
```

## Prerequisites
- GitHub account with LogicBoost repository
- Render account (free tier available at render.com)

## Deploy with SQLite

1. Go to **Render Dashboard** → **New** → **Web Service**
2. Select **Deploy from GitHub repository**
3. Select `LogicBoost` repository
4. Settings:
   - **Name**: `logicboost`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
   - **Start Command**: `gunicorn "app:create_app()"`
   - **Region**: Choose closest to you
   - **Plan**: Free

5. **Set Environment Variables**:
   - `FLASK_APP=run.py`
   - `FLASK_ENV=production`
   - `SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">`
   - **Note**: No DATABASE_URL needed - defaults to SQLite

6. Click **Deploy Service**
7. Wait 3-5 minutes
8. Visit your app at the provided URL

## Verify Deployment

Visit your app:
```
https://logicboost-xxxxx.onrender.com/
```

Test the features:
- 📅 Daily Challenge
- ⚡ Mini Game  
- 🌍 Real-world Problems
- ⚙️ Admin Panel

## Database Migrations

The `Procfile` includes `release: flask db upgrade` which runs migrations on every deploy.

If you add new migrations locally:
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

Commit and push - Render will apply migrations automatically.

**Note**: Data in SQLite won't persist between Render restarts. If you need persistent data, you can upgrade to PostgreSQL later.

## Troubleshooting

### Application Error / 500 error
- Check **Logs** tab in Render dashboard
- Verify FLASK_ENV=production is set
- Verify SECRET_KEY is set

### "Error: Unable to locate .py file"
- Ensure `Procfile` is in root directory
- Ensure `runtime.txt` exists
- Check file names match exactly

### Static Files Not Loading
- They're in `/static` folder by default
- Templates use `{{ url_for('static', ...) }}` correctly
- This is handled automatically

## Production Checklist

Before going live:
- [ ] Change SECRET_KEY to a strong random value
- [ ] Set FLASK_ENV=production
- [ ] Test app works at Render URL
- [ ] Monitor logs for errors
- [ ] Remember: SQLite data resets on Render restart
- [ ] Optional: Add custom domain
- [ ] Optional: Upgrade to PostgreSQL for persistent data (in the future)

## Future Upgrade to PostgreSQL

If you later need persistent data storage:
1. Create PostgreSQL on Render
2. Add DATABASE_URL environment variable
3. Restart service
4. Schema will be automatically created

## Useful Links

- Render Docs: https://render.com/docs
- Flask: https://flask.palletsprojects.com/
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.io/
