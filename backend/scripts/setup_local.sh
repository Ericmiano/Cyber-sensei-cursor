#!/bin/bash
# Local setup script for Cyber Sensei backend

set -e

echo "🚀 Setting up Cyber Sensei Backend (Local Development)"

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version found"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Check PostgreSQL connection
echo "🗄️  Checking PostgreSQL connection..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client found"
    # Try to connect (will fail gracefully if DB doesn't exist)
    psql -U postgres -c "SELECT 1" > /dev/null 2>&1 && echo "✅ PostgreSQL connection successful" || echo "⚠️  PostgreSQL connection failed - make sure PostgreSQL is running"
else
    echo "⚠️  PostgreSQL client not found - please install PostgreSQL"
fi

# Check Redis connection
echo "🔴 Checking Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running - please start Redis"
    fi
else
    echo "⚠️  Redis client not found - please install Redis"
fi

# Check for .env file
echo "⚙️  Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    if [ -f "../.env.example" ]; then
        cp ../.env.example .env
        echo "✅ .env file created. Please edit it with your settings."
    else
        echo "❌ .env.example not found"
    fi
else
    echo "✅ .env file exists"
fi

# Run migrations
echo "🔄 Running database migrations..."
if [ -f "alembic.ini" ]; then
    read -p "Run database migrations? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        alembic upgrade head
        echo "✅ Migrations completed"
    else
        echo "⏭️  Skipping migrations"
    fi
else
    echo "⚠️  alembic.ini not found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start backend: uvicorn app.main:app --reload"
echo "3. Start Celery worker: celery -A app.tasks.celery_app worker --loglevel=info"
echo "4. Access API docs: http://localhost:8000/docs"
