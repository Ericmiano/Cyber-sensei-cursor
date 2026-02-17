# Cyber Sensei

AI-powered cybersecurity training platform with adaptive learning, hands-on labs, and personalized content.

## Features

- 🔐 **Secure Authentication** - JWT + 2FA support
- 🎓 **Training Modules** - Interactive cybersecurity lessons
- 📊 **Progress Tracking** - Monitor learning progress
- 🏆 **Achievements** - Gamified learning experience
- 💬 **AI Chat** - LangChain-powered assistance
- 🔒 **Security First** - Rate limiting, XSS/CSRF protection
- ⚡ **High Performance** - Async operations, caching

## Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL + SQLAlchemy
- Redis
- LangChain + OpenAI/Anthropic

**Frontend:**
- React 18 + TypeScript
- Vite
- TailwindCSS
- React Query

## Quick Start

See `SETUP.md` for detailed setup instructions.

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python scripts/start.bat

# Frontend
cd frontend
npm install
npm run dev
```

## Documentation

- `SETUP.md` - Complete setup & deployment guide
- `QUICK_START.md` - Quick start guide
- `TESTING_GUIDE.md` - Testing procedures
- `HTTPS_SETUP_GUIDE.md` - SSL/HTTPS configuration

## License

MIT License - See LICENSE file for details

## Author

Eric Miano
