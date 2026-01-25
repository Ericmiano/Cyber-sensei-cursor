# Multi-Platform Setup Guide

Cyber Sensei now supports multiple platforms:
- 🌐 **Web App** (React + Vite)
- 💻 **Desktop App** (Electron - Windows, macOS, Linux)
- 📱 **Mobile App** (Capacitor - iOS, Android)

## Prerequisites

### All Platforms
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+ (with pgvector)
- Redis 7.0+
- Ollama (for free AI features)

### Desktop (Electron)
- No additional requirements

### Mobile (Capacitor)
- **Android**: Android Studio, JDK 11+
- **iOS**: Xcode, CocoaPods (macOS only)

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env` file in project root:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cyber_sensei
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

### 3. Initialize Database

```bash
cd backend
python scripts/init_db.py
alembic upgrade head
```

### 4. Start Services

**Terminal 1 - Backend API:**
```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
venv\Scripts\activate  # Windows
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Frontend (Web):**
```bash
cd frontend
npm run dev
```

## Platform-Specific Builds

### Web App

**Development:**
```bash
cd frontend
npm run dev
```
Access at: http://localhost:5173

**Production Build:**
```bash
cd frontend
npm run build:web
```
Output in `frontend/dist/`

### Desktop App (Electron)

**Development:**
```bash
cd frontend
npm run electron:dev
```

**Build for Current Platform:**
```bash
cd frontend
npm run build:electron
```

**Build for Specific Platform:**
```bash
# Windows
npm run build:electron -- --win

# macOS
npm run build:electron -- --mac

# Linux
npm run build:electron -- --linux
```

Output in `frontend/dist-electron/`

### Mobile App (Capacitor)

**Initialize Capacitor (first time only):**
```bash
cd frontend
npm run build
npx cap add android  # For Android
npx cap add ios        # For iOS (macOS only)
npx cap sync
```

**Android:**
```bash
cd frontend
npm run build
npm run build:android
# Opens Android Studio
```

**iOS (macOS only):**
```bash
cd frontend
npm run build
npm run build:ios
# Opens Xcode
```

**Sync Changes:**
```bash
cd frontend
npm run build
npm run capacitor:sync
```

## Configuration

### API URL Configuration

For mobile apps, set the backend API URL in `frontend/.env`:
```env
VITE_API_URL=http://your-backend-ip:8000
```

For local development on mobile:
- Android Emulator: Use `http://10.0.2.2:8000`
- iOS Simulator: Use `http://localhost:8000`
- Physical Device: Use your computer's local IP (e.g., `http://192.168.1.100:8000`)

### CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:5173` (Web dev)
- `http://localhost:3000` (Alternative port)
- `capacitor://localhost` (Mobile)
- `http://localhost` (Electron)

Update `backend/app/core/config.py` if needed.

## Platform-Specific Notes

### Electron (Desktop)

- Uses Chromium-based rendering
- File system access available via Electron APIs
- Native OS integration possible
- Auto-updater support available

### Capacitor (Mobile)

- Native device features available (camera, GPS, etc.)
- Push notifications supported
- App store distribution ready
- Offline support possible

### Web

- Progressive Web App (PWA) ready
- Service worker support available
- Responsive design for all screen sizes

## Troubleshooting

### Electron Issues

**App won't start:**
- Ensure `npm run build` completed successfully
- Check `electron/main.js` exists
- Verify Node.js version is 18+

### Capacitor Issues

**Android build fails:**
- Ensure Android Studio is installed
- Check JDK version (11+)
- Run `npx cap sync` after changes

**iOS build fails:**
- Ensure Xcode is installed (macOS only)
- Run `pod install` in `ios/App` directory
- Check CocoaPods is installed

### API Connection Issues

**Mobile can't connect to backend:**
- Check backend is running on `0.0.0.0` not `127.0.0.1`
- Verify firewall allows port 8000
- Use correct IP address for your network
- Check CORS settings in backend

## Build Scripts Reference

```bash
# Web
npm run dev              # Development server
npm run build:web        # Production build

# Electron
npm run electron:dev     # Dev with hot reload
npm run build:electron   # Build desktop app

# Capacitor
npm run capacitor:sync   # Sync web code to native
npm run build:android   # Build Android app
npm run build:ios       # Build iOS app
```

## Next Steps

1. **Test Web App**: Start with `npm run dev` in frontend
2. **Test Desktop**: Run `npm run electron:dev`
3. **Test Mobile**: Build and run on device/emulator
4. **Customize**: Update app icons, splash screens, etc.

For detailed platform-specific guides, see:
- [Electron Documentation](https://www.electronjs.org/docs)
- [Capacitor Documentation](https://capacitorjs.com/docs)
