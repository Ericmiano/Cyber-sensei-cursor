@echo off
echo ========================================
echo Starting Cyber Sensei System
echo ========================================
echo.

echo Starting Backend...
start "Cyber Sensei Backend" cmd /k "cd backend && venv\Scripts\activate && start_local.bat"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting Frontend...
start "Cyber Sensei Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo System Started Successfully!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8080
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C in the terminal windows to stop the servers
echo.
pause
