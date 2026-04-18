# Render Environment Variables Setup Guide

This file explains how to set environment variables on Render for LogicBoost deployment.

## Quick Setup

1. Go to your Render Service Dashboard
2. Click **Environment** in the left sidebar
3. Click **Add Environment Variable**
4. Add each variable below

## Required Variables

### FLASK_APP
- **Value**: `run.py`
- **Purpose**: Tells Flask which file is the app entry point

### FLASK_ENV
- **Value**: `production`
- **Purpose**: Runs Flask in production mode (no debug, optimized)

### SECRET_KEY
- **Value**: Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- **Purpose**: Django/Flask security key for sessions and CSRF
- **Important**: Never share this value, keep it secret!

### DATABASE_URL
- **Value**: Copy from your Render PostgreSQL instance
- **Where to find it**:
  1. Go to Render Dashboard
  2. Click on your PostgreSQL instance
  3. Copy the **External Database URL** under **Connections**
  4. It should look like: `postgresql://user:pass@host:port/dbname`
- **Purpose**: Connection string for your database

## Example Configuration

After adding all variables, your Environment tab should show:

```
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z
DATABASE_URL=postgresql://myuser:mypassword@pg-xxxxx.render-postgres.com:5432/logicboost
```

## Generating SECRET_KEY

### On Windows (Command Prompt):
```cmd
python -c "import secrets; print(secrets.token_hex(32))"
```

### On Mac/Linux:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (looks like: `abc123def456...`) and paste into SECRET_KEY

## Database URL Format

Render provides PostgreSQL URLs in this format:
```
postgresql://username:password@host.render-postgres.com:5432/database_name
```

- **username**: Default is usually your account email
- **password**: Generated password
- **host**: Render's PostgreSQL host
- **port**: Always 5432
- **database_name**: Your database name

## Optional Variables

### DEBUG (not recommended)
- **Value**: `False`
- Only set this if you know what you're doing

### WORKERS (for production scaling)
- **Value**: `4`
- Number of Gunicorn worker processes
- Leave as default if unsure

## Verifying Variables Are Set

After deployment, check logs:

1. Go to your Service dashboard
2. Click **Logs** 
3. Look for messages like "Using production database..." or "SECRET_KEY configured"

If you see errors about missing DATABASE_URL, the variable wasn't set correctly.

## Updating Variables

After deployment, if you need to change environment variables:

1. Click **Environment** on your Service page
2. Edit the variable
3. Click **Save**
4. Service will automatically redeploy with new variables

## Security Best Practices

- ✅ Change SECRET_KEY for each environment
- ✅ Never commit .env files to GitHub
- ✅ Use strong, random SECRET_KEY (32+ characters)
- ✅ Don't share DATABASE_URL publicly
- ✅ Review Render's security documentation
- ❌ Never put secrets in code
- ❌ Never share SECRET_KEY or DATABASE_URL

## Troubleshooting

### "Error: No DATABASE_URL" on startup
- Check Environment variables tab - is DATABASE_URL set?
- Verify DATABASE_URL value is complete (has postgresql://)
- Restart service after adding variable

### "Connection refused" to database
- Is PostgreSQL instance running? (check Render dashboard)
- Is DATABASE_URL correct? (copy again from PostgreSQL instance)
- Are both web service and database in same region?

### "Invalid SECRET_KEY"
- Ensure SECRET_KEY has no spaces
- Ensure it's valid hex (only 0-9, a-f characters)
- Try generating a new one with the command above

## Support

- Render Docs: https://render.com/docs
- Render Support: https://render.com/contact
- PostgreSQL Docs: https://www.postgresql.org/docs/
