@echo off
REM Check if PostgreSQL and Redis services are running

echo ========================================
echo Checking Required Services
echo ========================================
echo.

REM Check PostgreSQL
echo [1/2] Checking PostgreSQL...
sc query postgresql-x64-15 >nul 2>&1
if %errorlevel% equ 0 (
    sc query postgresql-x64-15 | find "RUNNING" >nul
    if %errorlevel% equ 0 (
        echo [OK] PostgreSQL is running
    ) else (
        echo [WARN] PostgreSQL service exists but is not running
        echo To start: net start postgresql-x64-15
    )
) else (
    echo [WARN] PostgreSQL service not found
    echo Please install PostgreSQL 15+ from: https://www.postgresql.org/download/windows/
)
echo.

REM Check Redis
echo [2/2] Checking Redis...
redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis is running
) else (
    echo [WARN] Redis is not running
    echo.
    echo To install Redis on Windows:
    echo   1. Download from: https://github.com/microsoftarchive/redis/releases
    echo   2. Or use WSL: wsl -d Ubuntu redis-server
    echo   3. Or use Docker: docker run -d -p 6379:6379 redis:latest
    echo.
    echo To start Redis (if installed):
    echo   redis-server
)
echo.

echo ========================================
echo Service Check Complete
echo ========================================
pause
