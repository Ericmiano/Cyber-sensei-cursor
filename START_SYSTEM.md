# How to Start Cyber Sensei System

## Prerequisites Check

Before starting, ensure you have:
- ✅ PostgreSQL 15+ installed and running
- ✅ Redis 7.0+ installed and running
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ Ollama installed (optional, for AI features)

## Quick Start (All Services)

### Option 1: Manual Start (Recommended for Development)

Open **3 terminal windows**:

**Terminal 1 - Backend API:**
```powershell
cd "f:\Projects\Cyber-sensei- cursor\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker (Background Tasks):**
```powershell
cd "f:\Projects\Cyber-sensei- cursor\backend"
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Frontend (Web App):**
```powershell
cd "f:\Projects\Cyber-sensei- cursor\frontend"
npm run dev
```

### Option 2: Using Startup Scripts

**Windows:**
```powershell
# Backend
cd backend
.\scripts\start.bat

# Celery (in new terminal)
cd backend
.\scripts\start_celery.bat

# Frontend (in new terminal)
cd frontend
npm run dev
```

## Verify Services Are Running

1. **Backend API**: http://localhost:8000/docs
2. **Backend Health**: http://localhost:8000/health
3. **Frontend**: http://localhost:5173

## First Time Setup

If this is your first time running:

1. **Create .env file** (if not exists):
   ```powershell
   # Already created with default values
   ```

2. **Initialize Database**:
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python scripts\init_db.py
   alembic upgrade head
   ```

3. **Install Ollama** (for free AI features):
   - Download from: https://ollama.com
   - Install and run: `ollama pull nomic-embed-text`
   - Install LLM: `ollama pull llama2` (or your preferred model)

## Troubleshooting

### PostgreSQL Not Running
```powershell
# Check if PostgreSQL service is running
Get-Service -Name postgresql*

# Start PostgreSQL (if installed as service)
Start-Service postgresql-x64-15
```

### Redis Not Running
```powershell
# If Redis is installed as service
Get-Service -Name redis*

# Or start Redis manually (if in PATH)
redis-server
```

### Port Already in Use
If port 8000 or 5173 is already in use:
- **Backend**: Change port with `--port 8001`
- **Frontend**: Edit `vite.config.ts` and change port

### Database Connection Error
- Check PostgreSQL is running
- Verify credentials in `.env` file
- Ensure database `cyber_sensei` exists
- Run `python scripts\init_db.py` to create it

## Access the Application

Once all services are running:

- **Web App**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## Next Steps

1. Register a user account via the web interface
2. Create topics and concepts
3. Upload documents for processing
4. Generate a curriculum
5. Take adaptive quizzes

Enjoy using Cyber Sensei! 🎓
