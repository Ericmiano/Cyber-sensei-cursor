# Cyber Sensei - Setup & Deployment Guide

## Quick Start (Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_training_data_simple.py

# Start server
python scripts/start.bat  # Windows
# python scripts/start.sh  # Linux/Mac
```

Backend runs at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env
# Edit .env if needed (default: http://localhost:8000/api)

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:8080`

---

## Production Deployment

### 1. Backend (with HTTPS)

See `HTTPS_SETUP_GUIDE.md` for detailed SSL configuration.

**Quick production start:**
```bash
cd backend

# Set production environment
set ENVIRONMENT=production

# With SSL certificates
set SSL_CERT_PATH=/path/to/cert.pem
set SSL_KEY_PATH=/path/to/key.pem
python start_https.py

# Or use Nginx reverse proxy (recommended)
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Frontend (Production Build)

```bash
cd frontend

# Build for production
npm run build

# Output in: frontend/dist/
# Deploy to: Nginx, Vercel, Netlify, etc.
```

### 3. Database Setup

```bash
# Create database
python backend/scripts/create_database.py

# Run migrations
cd backend
alembic upgrade head

# Seed training data
python scripts/seed_training_data.py
```

---

## Essential Scripts

### Backend Scripts

- `scripts/start.bat` / `start.sh` - Start development server
- `scripts/create_database.py` - Create PostgreSQL database
- `scripts/init_db.py` - Initialize database schema
- `scripts/reset_db.py` - Reset database (WARNING: deletes all data)
- `scripts/seed_training_data.py` - Seed training modules
- `scripts/seed_training_data_simple.py` - Seed basic data
- `scripts/test_db_connection.py` - Test database connection
- `scripts/start_celery.bat` / `.sh` - Start Celery worker

### Root Scripts

- `start_all.bat` / `start_all.sh` - Start both backend and frontend

---

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/Cyber-SenseiDB

# Security
SECRET_KEY=your-secret-key-min-32-chars
ENVIRONMENT=development

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://localhost:8080,http://localhost:3000

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_AUTH_PER_MINUTE=5

# SSL (Production)
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api
```

---

## Testing

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
```

---

## Key Features Implemented

✅ **Authentication & Security**
- JWT-based authentication
- Two-Factor Authentication (2FA)
- Password hashing (bcrypt)
- Rate limiting
- CSRF protection
- XSS/SQL injection prevention

✅ **Training System**
- Training modules & lessons
- Progress tracking
- Achievements system
- User activity logging

✅ **AI Integration**
- LangChain integration
- OpenAI & Anthropic support
- Chat history
- Document processing

✅ **Performance**
- Async operations
- Database connection pooling
- Response caching
- Code splitting
- Lazy loading

✅ **Production Ready**
- HTTPS support
- Nginx configuration
- Health check endpoints
- Comprehensive logging
- Error handling

---

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
python backend/scripts/test_db_connection.py

# Check PostgreSQL is running
# Windows: services.msc -> PostgreSQL
# Linux: sudo systemctl status postgresql
```

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Kill process
taskkill /PID <PID> /F  # Windows
kill -9 <PID>  # Linux/Mac
```

### Frontend Build Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## Documentation

- `README.md` - Project overview
- `QUICK_START.md` - Quick start guide
- `TESTING_GUIDE.md` - Testing procedures
- `HTTPS_SETUP_GUIDE.md` - SSL/HTTPS configuration
- `SETUP.md` - This file

---

## Support

For issues or questions:
1. Check documentation files
2. Review error logs
3. Check database connection
4. Verify environment variables

---

**Last Updated**: February 2026
**Status**: Production Ready ✅
