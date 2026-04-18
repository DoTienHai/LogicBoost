# Deploying LogicBoost to Render

This guide explains how to deploy the LogicBoost application to Render.com

## Prerequisites
- GitHub account with LogicBoost repository
- Render account (free tier available at render.com)
- PostgreSQL database (Render provides this)

## Step 1: Prepare the Repository

All necessary files for deployment are already in place:
- ✅ `Procfile` - Tells Render how to start the app
- ✅ `runtime.txt` - Specifies Python version
- ✅ `requirements.txt` - All dependencies including gunicorn
- ✅ `config.py` - Production configuration

## Step 2: Create PostgreSQL Database on Render

1. Go to **Render Dashboard** → **New** → **PostgreSQL**
2. Name: `logicboost-db`
3. Region: Choose closest to your users
4. PostgreSQL Version: 15 (or latest)
5. Click **Create Database**
6. **Copy the External Database URL** (you'll need this)

## Step 3: Deploy to Render

1. Go to **Render Dashboard** → **New** → **Web Service**
2. Select **Deploy from GitHub repository**
3. Connect your GitHub account if needed
4. Select `LogicBoost` repository
5. Fill in settings:
   - **Name**: `logicboost`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
   - **Start Command**: `gunicorn "app:create_app()"`
   - **Region**: Same as database
   - **Plan**: Free (or paid if preferred)

## Step 4: Set Environment Variables

In the Render dashboard, add these environment variables:

```
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=<generate-a-random-secret-key-here>
DATABASE_URL=<paste-the-PostgreSQL-URL-from-step-2>
```

### How to generate SECRET_KEY:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 5: Deploy

1. Click **Deploy Service**
2. Wait for build to complete (3-5 minutes)
3. Once live, you'll get a URL: `https://logicboost-xxxxx.onrender.com`

## Step 6: Verify Deployment

Visit your app:
```
https://logicboost-xxxxx.onrender.com/
```

Check logs if there are issues:
- Go to **Service** → **Logs**
- Look for error messages

## Database Migrations

The `Procfile` includes `release: flask db upgrade` which runs migrations automatically.

If you add new migrations locally:
```bash
flask db migrate -m "Description"
flask db upgrade
```

Commit and push to GitHub - Render will apply migrations automatically on next deploy.

## Troubleshooting

### Application Error / 500 error
- Check **Logs** tab in Render dashboard
- Verify DATABASE_URL environment variable is correct
- Ensure FLASK_ENV is set to `production`

### Database Connection Failed
- Verify DATABASE_URL is from PostgreSQL instance
- Check if database is in same region as web service
- Wait a few minutes - PostgreSQL may still be starting

### Static Files Not Loading
- Ensure `static/` folder exists in repository
- Check file paths in templates use `{{ url_for() }}` correctly

### Import errors
- Check `requirements.txt` has all dependencies
- Verify Python version matches `runtime.txt`

## Production Checklist

Before deploying to production:
- [ ] Change SECRET_KEY to a strong random value
- [ ] Set FLASK_ENV=production
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set appropriate SECRET_KEY in environment
- [ ] Test locally: `FLASK_ENV=production python run.py`
- [ ] Monitor logs after deployment

## Further Optimizations

### Optional: Add Cron Job for Cleanup
If you add user data, you might want periodic cleanup:
- Render supports cron jobs
- Useful for archiving old logs, cleaning up expired data

### Optional: Custom Domain
1. Go to **Settings** → **Custom Domains**
2. Add your domain
3. Update DNS records as instructed
4. Enable auto-renewal for SSL certificate

### Optional: Connect Database Management Tool
- Use DBeaver, pgAdmin, or similar
- Use the PostgreSQL External Database URL
- This lets you manage data directly

## Useful Commands

### Local Testing with PostgreSQL
```bash
# Create .env with PostgreSQL URL
echo "DATABASE_URL=postgresql://..." >> .env

# Install dependencies
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Start app
python run.py
```

### View Live Logs
```bash
# Via Render Dashboard Logs tab
# Or use Render CLI (if installed)
render logs --service logicboost
```

## Support
- Render docs: https://render.com/docs
- Flask Migrate: https://flask-migrate.readthedocs.io/
- SQLAlchemy: https://docs.sqlalchemy.org/
