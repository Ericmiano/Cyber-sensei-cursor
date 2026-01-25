# Database Connection Setup

## Your Database Configuration

You've configured a PostgreSQL database server named **"Cyber-SenseiDB"**.

## Current Configuration

The `.env` file has been updated to use your database:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/Cyber-SenseiDB
```

## ⚠️ Password Issue

The connection is failing because the password "postgres" is incorrect for your database.

## How to Fix

### Option 1: Update .env with Correct Password

1. Open `.env` file
2. Find the line: `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/Cyber-SenseiDB`
3. Replace `postgres` (the password part) with your actual PostgreSQL password:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:YOUR_ACTUAL_PASSWORD@localhost:5432/Cyber-SenseiDB
   ```

### Option 2: If You Don't Know the Password

1. Open PostgreSQL command line or pgAdmin
2. Connect to your "Cyber-SenseiDB" server
3. Reset the postgres user password:
   ```sql
   ALTER USER postgres WITH PASSWORD 'newpassword';
   ```
4. Update `.env` with the new password

### Option 3: Use Different User

If you have a different PostgreSQL user:
```
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/Cyber-SenseiDB
```

## After Updating Password

1. **Restart Backend** (if it's running):
   - Stop the current backend process
   - Restart: `uvicorn app.main:app --reload`

2. **Initialize Database**:
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python scripts\init_db.py
   alembic upgrade head
   ```

3. **Verify Connection**:
   ```powershell
   curl http://localhost:8000/health
   ```

## Database Name

The script will now automatically:
- Detect the database name from `.env` (Cyber-SenseiDB)
- Create it if it doesn't exist
- Enable pgvector extension

## Frontend Access

The frontend should be accessible at:
- **http://localhost:5173** - Should show the login page
- If you see API docs, you're on the wrong URL (that's http://localhost:8000/docs)

The frontend routes:
- `/` → Redirects to `/login` (if not authenticated) or `/dashboard` (if authenticated)
- `/login` → Login page
- `/dashboard` → Main dashboard (requires authentication)
