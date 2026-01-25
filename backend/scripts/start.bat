@echo off
REM Startup script for Cyber Sensei backend (Windows)

echo 🚀 Starting Cyber Sensei Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup first.
    echo    Run: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist "..\.env" (
    echo ⚠️  .env file not found. Creating from .env.example...
    if exist "..\.env.example" (
        copy ..\.env.example ..\.env
        echo ✅ .env file created. Please edit it with your settings.
        echo    IMPORTANT: Set SECRET_KEY in .env file!
    ) else (
        echo ❌ .env.example not found
        exit /b 1
    )
)

echo.
echo ✅ Setup complete!
echo.
echo Starting FastAPI server...
echo    API will be available at: http://localhost:8000
echo    API docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

REM Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
