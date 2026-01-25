# How to Run Cyber Sensei

## Quick Start

### Prerequisites Check
Make sure you have:
- ✅ PostgreSQL 15+ running
- ✅ Redis running (optional, for caching and Celery)
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed (for frontend)

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up .env file (copy from .env.example if exists, or create one)
# IMPORTANT: Set SECRET_KEY in .env

# Initialize database (if needed)
python scripts/init_db.py

# Run migrations
alembic upgrade head
```

### Step 2: Start Backend Server

```bash
cd backend
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 3: Start Celery Worker (Optional, for background tasks)

Open a **new terminal**:

```bash
cd backend
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

celery -A app.tasks.celery_app worker --loglevel=info
```

### Step 4: Start Frontend

Open a **new terminal**:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## Using Startup Scripts

### Windows

**Backend:**
```cmd
cd backend
scripts\start.bat
```

**Celery:**
```cmd
cd backend
scripts\start_celery.bat
```

### macOS/Linux

**Backend:**
```bash
cd backend
chmod +x scripts/start.sh
./scripts/start.sh
```

**Celery:**
```bash
cd backend
chmod +x scripts/start_celery.sh
./scripts/start_celery.sh
```

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env` matches your PostgreSQL setup
- Verify database `cyber_sensei` exists
- Run: `python scripts/init_db.py`

### Migration Errors
- Make sure pgvector extension is installed: `CREATE EXTENSION vector;`
- Check database connection
- Try: `alembic downgrade base` then `alembic upgrade head`

### Port Already in Use
- Change port in command: `--port 8001`
- Or kill process using port 8000

### SECRET_KEY Warning
- Set `SECRET_KEY` in `.env` file
- Generate one: `openssl rand -hex 32`

## Verify Installation

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **API Documentation:**
   Open http://localhost:8000/docs in browser

3. **Test Registration:**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","username":"testuser","password":"TestPass123!"}'
   ```

## Services Running

You should have **3 terminals** running:
1. **Backend API** (uvicorn) - Port 8000
2. **Celery Worker** (optional) - Background tasks
3. **Frontend** (npm run dev) - Port 5173

## Next Steps

1. Register a user via API or frontend
2. Create topics and concepts
3. Upload documents for processing
4. Generate curriculum
5. Take quizzes
6. View recommendations
