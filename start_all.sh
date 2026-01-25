#!/bin/bash
# Start all Cyber Sensei services

set -e

echo "🚀 Starting Cyber Sensei Platform"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Python found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    exit 1
fi
echo "✅ Node.js found"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found (database may not be accessible)"
else
    echo "✅ PostgreSQL client found"
fi

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis client not found (caching may not work)"
else
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running (start with: redis-server)"
    fi
fi

echo ""
echo "📋 Starting services in separate terminals..."
echo ""

# Start backend
echo "1️⃣  Starting Backend API..."
cd backend
if [ ! -d "venv" ]; then
    echo "   Setting up backend..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Run migrations
source venv/bin/activate
alembic upgrade head 2>/dev/null || echo "   ⚠️  Migration may have failed, continuing..."

# Start backend in background
echo "   Starting FastAPI on http://localhost:8000"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

cd ..

# Start Celery
echo "2️⃣  Starting Celery Worker..."
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info > ../logs/celery.log 2>&1 &
CELERY_PID=$!
echo "   Celery PID: $CELERY_PID"
cd ..

# Start frontend
echo "3️⃣  Starting Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "   Installing frontend dependencies..."
    npm install
fi

echo "   Starting Vite dev server on http://localhost:5173"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
cd ..

# Create logs directory
mkdir -p logs

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Service Status:"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Frontend:     http://localhost:5173"
echo ""
echo "📝 Logs:"
echo "   Backend:  logs/backend.log"
echo "   Celery:   logs/celery.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $CELERY_PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop this script (services will continue running)"
echo ""

# Wait for interrupt
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $CELERY_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
