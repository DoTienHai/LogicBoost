# Setup local PostgreSQL for development (Optional)

If you want to test PostgreSQL locally before deploying:

## Option 1: Using Docker (Easiest)

```bash
# Start PostgreSQL container
docker run --name logicboost-postgres \
  -e POSTGRES_USER=logicboost \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=logicboost_dev \
  -p 5432:5432 \
  -d postgres:15
```

## Option 2: Install PostgreSQL Locally

### Windows (with WSL)
```bash
# In WSL terminal
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
sudo -u postgres psql
```

Then in psql:
```sql
CREATE USER logicboost WITH PASSWORD 'yourpassword';
CREATE DATABASE logicboost_dev OWNER logicboost;
```

### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
createuser logicboost
createdb -U logicboost logicboost_dev
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser logicboost
sudo -u postgres createdb -O logicboost logicboost_dev
```

## Setup Environment

Create `.env.local`:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-dev-secret-key
DATABASE_URL=postgresql://logicboost:yourpassword@localhost:5432/logicboost_dev
```

## Initialize Database

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Start app
python run.py
```

## Verify Connection

```bash
# Test database connection
python -c "from app import create_app, db; app = create_app(); db.create_all()"
```

If successful, no errors will appear!

## Switch Back to SQLite

Just remove the DATABASE_URL from .env:
```
# .env
FLASK_ENV=development
SECRET_KEY=your-dev-secret-key
# DATABASE_URL will default to SQLite
```

Then restart the app.
