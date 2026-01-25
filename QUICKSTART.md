# Quick Start Guide - Local Development

## Prerequisites

### Required Software
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and npm ([Download](https://nodejs.org/))
- **PostgreSQL 15+** with pgvector extension ([Installation Guide](https://github.com/pgvector/pgvector#installation))
- **Redis 7.0+** ([Download](https://redis.io/download))

### Verify Installation
```bash
python --version  # Should be 3.11+
node --version    # Should be 18+
npm --version
psql --version    # PostgreSQL client
redis-cli --version
```

## Setup Steps

### 1. Clone and Navigate
```bash
cd cyber-sensei
```

### 2. Environment Configuration
```bash
cp .env.example .env
```

Edit `.env` file with your local settings:
```env
# Database - Update if your PostgreSQL is on different port/credentials
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cyber_sensei

# Redis - Update if Redis is on different port
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# JWT - Generate a secure secret key
SECRET_KEY=your-secret-key-here-use-openssl-rand-hex-32
```

### 3. Install PostgreSQL and Enable pgvector

#### On Windows:
1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Install pgvector extension:
   ```powershell
   # Download pgvector from https://github.com/pgvector/pgvector/releases
   # Copy pgvector.dll to PostgreSQL lib folder
   # Copy pgvector.control and pgvector--*.sql to PostgreSQL share/extension folder
   ```

#### On macOS:
```bash
brew install postgresql@15
brew install pgvector
```

#### On Linux (Ubuntu/Debian):
```bash
sudo apt-get install postgresql-15 postgresql-contrib
# Install pgvector
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 4. Create Database and Enable pgvector

```bash
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL shell:
CREATE DATABASE cyber_sensei;
\c cyber_sensei
CREATE EXTENSION vector;
\q
```

Or use the initialization script:
```bash
cd backend
python scripts/init_db.py
```

### 5. Install Redis

#### On Windows:
- Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases) or use WSL
- Or use Docker: `docker run -d -p 6379:6379 redis:7-alpine`

#### On macOS:
```bash
brew install redis
brew services start redis
```

#### On Linux:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### 6. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Verify database connection
python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### 7. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

### 8. Start Services

You'll need **4 terminal windows**:

#### Terminal 1: Backend API
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2: Celery Worker
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
celery -A app.tasks.celery_app worker --loglevel=info
```

#### Terminal 3: Frontend (Development Server)
```bash
cd frontend
npm run dev
```

#### Terminal 4: (Optional) Celery Flower (Task Monitor)
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install flower
celery -A app.tasks.celery_app flower
```

### 9. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Celery Flower** (if running): http://localhost:5555

## First Steps

### 1. Register a User

Via API:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123"
  }'
```

Or use the frontend at http://localhost:5173/login

### 2. Login

Via API:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

Save the `access_token` from the response.

### 3. Test API Endpoints

```bash
# Get recommendations (replace YOUR_TOKEN)
curl -X GET "http://localhost:8000/api/recommendations/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Health check
curl http://localhost:8000/health
```

## Development Workflow

### Backend Development

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest
pytest --cov=app  # With coverage

# Create new migration
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend Development

```bash
cd frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## Database Management

### Create Migration
```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```

### Access PostgreSQL
```bash
psql -U postgres -d cyber_sensei
```

### Common SQL Commands
```sql
-- List all tables
\dt

-- Describe a table
\d users

-- View data
SELECT * FROM users LIMIT 10;

-- Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## Troubleshooting

### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
# Windows:
sc query postgresql-x64-15
# macOS/Linux:
sudo systemctl status postgresql

# Test connection
psql -U postgres -h localhost

# If authentication fails, check pg_hba.conf
# Location: C:\Program Files\PostgreSQL\15\data\pg_hba.conf (Windows)
# Or: /etc/postgresql/15/main/pg_hba.conf (Linux)
```

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping

# Start Redis manually
# Windows: redis-server
# macOS: brew services start redis
# Linux: sudo systemctl start redis
```

### Port Conflicts
If ports are already in use:
- **8000** (Backend): Change in `backend/app/main.py` or use `--port` flag
- **5173** (Frontend): Change in `frontend/vite.config.ts`
- **5432** (PostgreSQL): Change in `.env` DATABASE_URL
- **6379** (Redis): Change in `.env` REDIS_URL

### Python Virtual Environment Issues
```bash
# Recreate virtual environment
cd backend
rm -rf venv  # Windows: rmdir /s venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Migration Issues
```bash
# Reset database (WARNING: Deletes all data)
cd backend
source venv/bin/activate
alembic downgrade base
alembic upgrade head

# Or manually in PostgreSQL:
DROP DATABASE cyber_sensei;
CREATE DATABASE cyber_sensei;
\c cyber_sensei
CREATE EXTENSION vector;
```

### Frontend Build Issues
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Environment Variables Reference

Key variables in `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cyber_sensei

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI/LLM (Optional for now)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_LLM_PROVIDER=ollama
```

## Next Steps

1. **Create Topics and Concepts**: Use API endpoints or admin interface
2. **Upload Documents**: Use ingestion API to process PDFs/URLs
3. **Generate Curriculum**: Test the curriculum engine with a topic
4. **Take Quizzes**: Test adaptive quiz functionality
5. **Review Recommendations**: Check AI-powered recommendations

## Useful Commands Cheat Sheet

```bash
# Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload
celery -A app.tasks.celery_app worker --loglevel=info
alembic upgrade head
pytest

# Frontend
cd frontend
npm run dev
npm run build

# Database
psql -U postgres -d cyber_sensei
CREATE EXTENSION vector;

# Redis
redis-cli ping
redis-cli flushall  # Clear all data (careful!)

# System
python --version
node --version
psql --version
redis-cli --version
```
