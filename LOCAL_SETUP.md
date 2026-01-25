# Local Development Setup Guide

This guide provides step-by-step instructions for setting up Cyber Sensei locally without Docker.

## Prerequisites Installation

### 1. Python 3.11+

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation
- Verify: `python --version`

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip
```

### 2. Node.js 18+

**Windows/macOS:**
- Download from [nodejs.org](https://nodejs.org/)

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Verify: `node --version` and `npm --version`

### 3. PostgreSQL 15+ with pgvector

**Windows:**
1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Install pgvector:
   - Download from [pgvector releases](https://github.com/pgvector/pgvector/releases)
   - Copy `pgvector.dll` to `C:\Program Files\PostgreSQL\15\lib\`
   - Copy `pgvector.control` and `pgvector--*.sql` to `C:\Program Files\PostgreSQL\15\share\extension\`

**macOS:**
```bash
brew install postgresql@15
brew install pgvector
brew services start postgresql@15
```

**Linux:**
```bash
# Install PostgreSQL
sudo apt-get install postgresql-15 postgresql-contrib

# Install pgvector
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 4. Redis 7.0+

**Windows:**
- Option 1: Use WSL (Windows Subsystem for Linux)
- Option 2: Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
- Option 3: Use Docker: `docker run -d -p 6379:6379 redis:7-alpine`

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

Verify: `redis-cli ping` (should return `PONG`)

## Quick Setup (Using Scripts)

### Backend Setup

**macOS/Linux:**
```bash
cd backend
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

**Windows:**
```bash
cd backend
scripts\setup_local.bat
```

### Frontend Setup

**macOS/Linux:**
```bash
cd frontend
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

**Windows:**
```bash
cd frontend
scripts\setup_local.bat
```

## Manual Setup

### Step 1: Database Setup

```bash
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL shell:
CREATE DATABASE cyber_sensei;
\c cyber_sensei
CREATE EXTENSION vector;
\q
```

Or use the Python script:
```bash
cd backend
python scripts/init_db.py
```

### Step 2: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Windows: notepad .env
# macOS/Linux: nano .env
```

Key settings to update:
```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/cyber_sensei
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
alembic upgrade head
```

### Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### Step 5: Start Services

You need **3 terminal windows**:

**Terminal 1 - Backend API:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 6: Verify Installation

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy"}`

2. **API Documentation:**
   Open http://localhost:8000/docs in your browser

3. **Frontend:**
   Open http://localhost:5173 in your browser

## Common Issues & Solutions

### PostgreSQL Connection Failed

**Error:** `could not connect to server`

**Solutions:**
1. Check if PostgreSQL is running:
   ```bash
   # Windows
   sc query postgresql-x64-15
   
   # macOS/Linux
   sudo systemctl status postgresql
   ```

2. Check PostgreSQL authentication:
   - Edit `pg_hba.conf` (location varies by OS)
   - Ensure `trust` or `md5` authentication for local connections

3. Verify connection string in `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/cyber_sensei
   ```

### pgvector Extension Not Found

**Error:** `extension "vector" does not exist`

**Solutions:**
1. Verify pgvector is installed:
   ```bash
   # In PostgreSQL
   \dx vector
   ```

2. Install pgvector (see Prerequisites section)

3. Manually enable extension:
   ```sql
   CREATE EXTENSION vector;
   ```

### Redis Connection Failed

**Error:** `Error 111 connecting to localhost:6379`

**Solutions:**
1. Check if Redis is running:
   ```bash
   redis-cli ping
   ```

2. Start Redis:
   ```bash
   # macOS
   brew services start redis
   
   # Linux
   sudo systemctl start redis
   
   # Windows (if installed)
   redis-server
   ```

### Port Already in Use

**Error:** `Address already in use`

**Solutions:**
1. Find process using the port:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # macOS/Linux
   lsof -i :8000
   ```

2. Kill the process or change port:
   ```bash
   # Change backend port
   uvicorn app.main:app --reload --port 8001
   
   # Change frontend port (edit vite.config.ts)
   ```

### Python Virtual Environment Issues

**Error:** `No module named 'app'`

**Solutions:**
1. Ensure virtual environment is activated:
   ```bash
   # Check activation
   which python  # Should show venv path
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Migration Errors

**Error:** `Target database is not up to date`

**Solutions:**
1. Check current migration:
   ```bash
   alembic current
   ```

2. Upgrade to latest:
   ```bash
   alembic upgrade head
   ```

3. If issues persist, reset (WARNING: deletes data):
   ```bash
   alembic downgrade base
   alembic upgrade head
   ```

## Development Workflow

### Making Changes

1. **Backend Changes:**
   - Edit files in `backend/app/`
   - Server auto-reloads (if using `--reload` flag)
   - Test at http://localhost:8000/docs

2. **Frontend Changes:**
   - Edit files in `frontend/src/`
   - Vite hot-reloads automatically
   - Changes visible at http://localhost:5173

3. **Database Changes:**
   ```bash
   # Create migration
   alembic revision --autogenerate -m "Description"
   
   # Apply migration
   alembic upgrade head
   ```

### Running Tests

```bash
cd backend
source venv/bin/activate
pytest
pytest --cov=app  # With coverage
```

### Debugging

**Backend:**
- Add breakpoints in VS Code or PyCharm
- Use `print()` statements (removed in production)
- Check logs in terminal

**Frontend:**
- Use browser DevTools (F12)
- React DevTools extension
- Check console for errors

## Next Steps

1. Register a user via API or frontend
2. Create topics and concepts
3. Upload documents for processing
4. Generate a curriculum
5. Take adaptive quizzes
6. Review recommendations

For API usage examples, see [QUICKSTART.md](QUICKSTART.md).
