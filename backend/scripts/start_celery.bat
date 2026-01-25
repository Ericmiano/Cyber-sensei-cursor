@echo off
REM Start Celery worker (Windows)

echo 🔄 Starting Celery Worker...

if not exist "venv" (
    echo ❌ Virtual environment not found
    exit /b 1
)

call venv\Scripts\activate.bat

echo ✅ Celery worker starting...
echo    Tasks will be processed from Redis queue
echo.
echo Press Ctrl+C to stop
echo.

celery -A app.tasks.celery_app worker --loglevel=info
