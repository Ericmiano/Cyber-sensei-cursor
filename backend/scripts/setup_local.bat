@echo off
REM Local setup script for Cyber Sensei backend (Windows)

echo 🚀 Setting up Cyber Sensei Backend (Local Development)

REM Check Python
echo 📋 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+
    exit /b 1
)
echo ✅ Python found

REM Create virtual environment
echo 📦 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ℹ️  Virtual environment already exists
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt
echo ✅ Dependencies installed

REM Check PostgreSQL
echo 🗄️  Checking PostgreSQL...
where psql >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PostgreSQL client not found
) else (
    echo ✅ PostgreSQL client found
)

REM Check Redis
echo 🔴 Checking Redis...
where redis-cli >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Redis client not found
) else (
    redis-cli ping >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Redis is not running
    ) else (
        echo ✅ Redis is running
    )
)

REM Check .env file
echo ⚙️  Checking configuration...
if not exist ".env" (
    echo ⚠️  .env file not found
    if exist "..\.env.example" (
        copy ..\.env.example .env
        echo ✅ .env file created. Please edit it with your settings.
    )
) else (
    echo ✅ .env file exists
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Start backend: uvicorn app.main:app --reload
echo 3. Start Celery worker: celery -A app.tasks.celery_app worker --loglevel=info
echo 4. Access API docs: http://localhost:8000/docs

pause
