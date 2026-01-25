# Quick Fix Guide

## Issue 1: Database Connection

Your database "Cyber-SenseiDB" is configured, but the password needs to be updated.

### Update Database Password in .env

1. Open `.env` file
2. Find this line:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/Cyber-SenseiDB
   ```
3. Replace `postgres` (the second one, which is the password) with your actual PostgreSQL password:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/Cyber-SenseiDB
   ```

### Initialize Database

After updating the password, run:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python scripts\init_db.py
alembic upgrade head
```

## Issue 2: Frontend vs API Docs

You're probably seeing the **API Documentation** page instead of the **Frontend UI**.

### Correct URLs:

- **Frontend (UI)**: http://localhost:5173
  - This shows the login page and application interface
  - Should show "Cyber Sensei" login form

- **API Docs**: http://localhost:8000/docs
  - This is the Swagger API documentation
  - Shows API endpoints and allows testing

### To See the Frontend:

1. Open your browser
2. Go to: **http://localhost:5173**
3. You should see a login page with:
   - "Cyber Sensei" title
   - "Adaptive Learning Platform" subtitle
   - Email and Password fields
   - "Sign in" button

### If Frontend Shows Errors:

The frontend might be showing API errors if:
- Database isn't connected (will show errors when trying to login)
- Backend isn't running (will show connection errors)

## Current Status

✅ Backend: Running on port 8000
✅ Frontend: Running on port 5173
✅ Celery: Running
⚠️ Database: Needs correct password in .env

## Next Steps

1. **Update `.env`** with your PostgreSQL password
2. **Restart backend** (already restarted)
3. **Initialize database**: `python scripts\init_db.py && alembic upgrade head`
4. **Access frontend**: http://localhost:5173
5. **Register/Login** to use the application
