@echo off
REM Local setup script for Cyber Sensei frontend (Windows)

echo 🚀 Setting up Cyber Sensei Frontend (Local Development)

REM Check Node.js
echo 📋 Checking Node.js version...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 18+
    exit /b 1
)
echo ✅ Node.js found

REM Check npm
echo 📋 Checking npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found
    exit /b 1
)
echo ✅ npm found

REM Install dependencies
echo 📥 Installing dependencies...
call npm install
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Start development server: npm run dev
echo 2. Access frontend: http://localhost:5173
echo 3. Make sure backend is running on http://localhost:8000

pause
