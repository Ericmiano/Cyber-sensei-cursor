# Cyber Sensei - Adaptive Learning Platform

An intelligent, self-evolving adaptive learning platform that generates personalized study materials, quizzes, and labs with AI-powered content generation.

## 🎯 Core Features

- **Personalized Curriculum**: Topological sort for prerequisites + Bloom's Taxonomy weighting
- **Adaptive Quizzes**: Computerized Adaptive Testing (CAT) with Bayesian Knowledge Tracing (BKT)
- **Spaced Repetition**: SM-2 algorithm for optimal review scheduling
- **Lab Orchestrator**: Containerized hands-on exercises with automated grading
- **Meta-Learning**: Self-evaluation and recursive content improvement
- **Explainable Recommendations**: AI-powered suggestions with explicit reasoning

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (async-first)
- **Database**: PostgreSQL 15+ with pgvector for embeddings
- **Task Queue**: Celery 5.3+ with Redis
- **AI/Vector**: LangChain + ChromaDB (MVP) / Qdrant (Production)

### Frontend
- **Framework**: React 18+ with Vite
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Rich Text**: TipTap

### Database Schema (18 Tables)

**Users & Auth** (4 tables)
- `users` - RBAC user accounts
- `user_profiles` - Learning preferences
- `sessions` - JWT session management
- `user_goals` - Learning goals with timeframes

**Sources & Ingestion** (3 tables)
- `sources` - Source metadata with reliability scoring
- `documents` - Document storage
- `chunks` - Text chunks with 1536-dim embeddings

**Topics & Knowledge** (4 tables)
- `topics` - Learning domains
- `concepts` - Atomic concepts with Bloom levels
- `concept_edges` - Prerequisite graph (DAG)
- `content_items` - AI-generated content

**Learning State** (4 tables)
- `user_progress` - Content progress tracking
- `user_concept_mastery` - BKT mastery estimates
- `spaced_repetition_schedule` - SM-2 scheduling
- `learning_events` - Immutable audit trail

**Moderation & Safety** (4 tables)
- `content_reviews` - Human moderation
- `flagged_items` - Flagged content
- `audit_logs` - Security audit trail
- `misconceptions` - Common error detection

**Performance & Feedback** (3 tables)
- `teaching_feedback` - AI efficacy scores
- `lab_sessions` - Container lifecycle
- `grading_rubrics` - Automated grading criteria

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and npm ([Download](https://nodejs.org/))
- **PostgreSQL 15+** with pgvector extension ([Installation Guide](https://github.com/pgvector/pgvector#installation))
- **Redis 7.0+** ([Download](https://redis.io/download))

### Local Development Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd cyber-sensei
```

2. **Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
# Edit ../.env with your database and Redis settings
alembic upgrade head
```

3. **Frontend Setup:**
```bash
cd frontend
npm install
```

4. **Start Services:**

   **Terminal 1 - Backend API:**
   ```bash
   cd backend
   source venv/bin/activate  # Windows: venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

   **Terminal 2 - Celery Worker:**
   ```bash
   cd backend
   source venv/bin/activate  # Windows: venv\Scripts\activate
   celery -A app.tasks.celery_app worker --loglevel=info
   ```

   **Terminal 3 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

5. **Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Using Setup Scripts

**Backend (macOS/Linux):**
```bash
cd backend
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

**Backend (Windows):**
```bash
cd backend
scripts\setup_local.bat
```

**Frontend (macOS/Linux):**
```bash
cd frontend
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

**Frontend (Windows):**
```bash
cd frontend
scripts\setup_local.bat
```

For detailed setup instructions, see:
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[LOCAL_SETUP.md](LOCAL_SETUP.md)** - Detailed local setup instructions

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Celery Worker
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

## 📚 Core Engines

### Curriculum Engine
- Generates personalized learning sequences
- Uses topological sort for prerequisite ordering
- Applies Bloom's Taxonomy weighting (levels 1-6)
- Skips concepts with high mastery (>80%)

### Quiz Engine
- **CAT (Computerized Adaptive Testing)**: Adjusts question difficulty based on performance
- **BKT (Bayesian Knowledge Tracing)**: Updates mastery probability after each answer
- **SM-2**: Spaced repetition scheduling
- **Actionable Critique**: Detailed feedback on incorrect answers

### Recommendation Engine
- Analyzes user mastery and progress
- Provides explainable recommendations
- Prioritizes due reviews, low mastery concepts, and incomplete content

### Lab Orchestrator
- Provisions isolated Docker environments
- Validates lab completion against rubrics
- Supports file existence, port listening, command output checks

### Meta-Learning Engine
- Calculates efficacy scores: `E = (ΔMastery / Time) × UserSatisfaction`
- Identifies content shortcomings
- Triggers automatic content revision

## 🔐 Security

- JWT-based authentication with refresh tokens
- RBAC (Role-Based Access Control)
- Immutable audit logging
- Human-in-the-loop content moderation
- Input validation with Pydantic v2

## 📊 Algorithms

### Bayesian Knowledge Tracing (BKT)
- Tracks mastery probability: P(know)
- Parameters: learn_rate, guess_rate, slip_rate
- Updates after each quiz attempt

### SM-2 Spaced Repetition
- Quality rating: 0-5
- Adjusts easiness factor and interval
- Optimal review scheduling

### Reliability Scoring
```
Score = (DomainAuthority × 0.4 + AgeBonus × 0.3 + PeerReview × 0.3) / 5
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## 📝 API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔄 Development Roadmap

- [x] Phase 1: Database models and migrations
- [x] Phase 2: Core engines (Curriculum, Quiz, Recommendation)
- [x] Phase 3: Lab Orchestrator and Meta-Learning
- [ ] Phase 4: Advanced AI content generation
- [ ] Phase 5: Production deployment (Kubernetes)
- [ ] Phase 6: Mobile app

## 📄 License

[Your License Here]

## 🤝 Contributing

[Contributing Guidelines]
