# PostgreSQL Database Setup Guide

This guide will help you set up PostgreSQL for the ANPR system.

## Option 1: Install PostgreSQL (Recommended for Production)

### macOS (using Homebrew)

1. **Install PostgreSQL:**
   ```bash
   brew install postgresql@15
   ```

2. **Start PostgreSQL service:**
   ```bash
   brew services start postgresql@15
   ```

3. **Verify installation:**
   ```bash
   psql --version
   ```

4. **Set up default user and password:**
   ```bash
   # Create a postgres user with password (if not exists)
   createuser -s postgres
   # Or set password:
   psql postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"
   ```

### Linux (Ubuntu/Debian)

1. **Install PostgreSQL:**
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. **Start PostgreSQL service:**
   ```bash
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

3. **Set up user:**
   ```bash
   sudo -u postgres psql
   # In psql prompt:
   ALTER USER postgres WITH PASSWORD 'postgres';
   \q
   ```

### Windows

1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer
3. Remember the password you set for the `postgres` user during installation

## Option 2: Use Docker (Easy Setup)

If you have Docker installed:

```bash
docker run --name anpr-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=anpr_db \
  -p 5432:5432 \
  -d postgres:15
```

## Configuration

1. **Create `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your database credentials:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/anpr_db
   ```

   Update if your setup differs:
   - Username: `postgres` (or your PostgreSQL username)
   - Password: `postgres` (or your PostgreSQL password)
   - Host: `localhost` (or your PostgreSQL host)
   - Port: `5432` (default PostgreSQL port)
   - Database: `anpr_db` (will be created automatically)

## Initialize Database

Once PostgreSQL is running:

```bash
python3.9 setup_database.py
```

This script will:
1. Check PostgreSQL connection
2. Create the `anpr_db` database (if it doesn't exist)
3. Create all necessary tables (vehicles, detections, events)

## Verify Setup

Test the database connection:

```bash
python3.9 -c "from src.database import engine; from sqlalchemy import text; engine.connect().execute(text('SELECT 1')); print('✅ Database connection successful!')"
```

## Troubleshooting

### Connection Refused
- Ensure PostgreSQL service is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)

### Authentication Failed
- Check username and password in `.env` file
- Reset password: `psql postgres -c "ALTER USER postgres WITH PASSWORD 'your_password';"`

### Database Already Exists
- The setup script will skip creation if database exists
- Or manually drop: `psql postgres -c "DROP DATABASE anpr_db;"`

### Permission Denied
- On macOS, you might need to start PostgreSQL: `brew services start postgresql@15`
- On Linux, check service: `sudo systemctl start postgresql`

## Quick Start (After Setup)

Once database is set up:

1. **Start the backend:**
   ```bash
   python3.9 run.py
   ```

2. **Access API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

3. **Start the frontend:**
   ```bash
   cd frontend/angular-ui
   npm install
   npm start
   ```
