#!/bin/bash
# Startup script for Cyber Sensei backend

set -e

echo "🚀 Starting Cyber Sensei Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "   Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f "../.env.example" ]; then
        cp ../.env.example ../.env
        echo "✅ .env file created. Please edit it with your settings."
        echo "   IMPORTANT: Set SECRET_KEY in .env file!"
    else
        echo "❌ .env.example not found"
        exit 1
    fi
fi

# Check if SECRET_KEY is set
if grep -q "your-secret-key-change-in-production" ../.env || ! grep -q "SECRET_KEY=" ../.env; then
    echo "⚠️  SECRET_KEY not properly set in .env"
    echo "   Generating a secure key..."
    SECRET_KEY=$(openssl rand -hex 32)
    if grep -q "SECRET_KEY=" ../.env; then
        sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" ../.env
    else
        echo "SECRET_KEY=$SECRET_KEY" >> ../.env
    fi
    echo "✅ SECRET_KEY generated and added to .env"
fi

# Check database connection
echo "🔍 Checking database connection..."
python -c "
import asyncio
from app.core.database import engine
async def check():
    try:
        async with engine.connect() as conn:
            await conn.execute('SELECT 1')
        print('✅ Database connection successful')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        print('   Make sure PostgreSQL is running and DATABASE_URL is correct in .env')
        exit(1)
asyncio.run(check())
" || exit 1

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head || {
    echo "⚠️  Migration failed. Trying to initialize database..."
    python scripts/init_db.py
    alembic upgrade head
}

# Check Redis
echo "🔍 Checking Redis connection..."
python -c "
import redis
from app.core.config import settings
try:
    r = redis.from_url(settings.REDIS_URL)
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'⚠️  Redis connection failed: {e}')
    print('   Make sure Redis is running')
" || echo "⚠️  Redis not available (caching will be disabled)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting FastAPI server..."
echo "   API will be available at: http://localhost:8000"
echo "   API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
