# Testing Guide 🧪

## Quick Test

### Option 1: Test API Manually

```bash
# Make sure backend is running first
cd backend
python scripts/start.bat

# In another terminal, test the API
curl http://localhost:8000/health
# Or visit: http://localhost:8000/docs
```

### Option 2: Start Everything

```bash
# Start both backend and frontend
start_all.bat
```

This will:
1. Start backend on port 8000
2. Start frontend on port 8080
3. Open API docs at http://localhost:8000/docs

---
## Manual Testing Steps

### Step 1: Start Backend

```bash
cd backend
venv\Scripts\activate
alembic upgrade head
python scripts\seed_training_data.py
start_local.bat
```

**Verify**: Visit http://localhost:8000/docs

### Step 2: Test Backend APIs

#### Test 1: Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"healthy","version":"1.0.0"}`

#### Test 2: Register User
```bash
curl -X POST http://localhost:8000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"username\":\"testuser\",\"password\":\"Test123!@#\"}"
```

#### Test 3: Login
```bash
curl -X POST http://localhost:8000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"testuser\",\"password\":\"Test123!@#\"}"
```
Save the `access_token` from response.

#### Test 4: Get Training Modules
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" ^
  http://localhost:8000/api/training/modules
```
Expected: Array of 7 modules

#### Test 5: Get Progress
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" ^
  http://localhost:8000/api/progress
```
Expected: User progress with XP, level, streaks

#### Test 6: Get Achievements
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" ^
  http://localhost:8000/api/achievements
```
Expected: Array of 14 achievements

### Step 3: Start Frontend

```bash
cd frontend
npm run dev
```

**Verify**: Visit http://localhost:8080

### Step 4: Test Frontend Integration

1. **Open Browser**: http://localhost:8080
2. **Register**: Create a new account
3. **Login**: Login with your credentials
4. **Training Page**: 
   - Should see 7 modules from backend
   - Click on a module to see lessons
   - Complete a lesson
   - Verify XP increases
5. **Progress Page**:
   - Should see your level and XP
   - Should see streak counter
   - Should see activity log
6. **Achievements Page**:
   - Should see 14 achievements
   - Some may be unlocked if you completed lessons

---

## Manual API Testing

You can test the API endpoints manually using:

1. **Swagger UI**: http://localhost:8000/docs
2. **ReDoc**: http://localhost:8000/redoc
3. **curl** or **Postman**

### Example API Tests

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"Test123!@#"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123!@#"
```
2. ✅ User registration
3. ✅ User login
4. ✅ Fetch training modules (7 modules)
5. ✅ Fetch user progress
6. ✅ Fetch achievements (14 achievements)
7. ✅ Complete a lesson and earn XP

**Expected Output**:
```
============================================================
Cyber Sensei - Integration Test Suite
============================================================

ℹ️  Checking if backend is running...
✅ Backend is running

ℹ️  Testing backend health...
✅ Backend is healthy: {'status': 'healthy', 'version': '1.0.0'}

ℹ️  Testing user registration...
✅ User registered successfully

ℹ️  Testing user login...
✅ Login successful, token: eyJhbGciOiJIUzI1NiIs...

ℹ️  Testing training modules endpoint...
✅ Fetched 7 training modules
  - Cybersecurity Fundamentals (0/12)
  - Network Security (0/0)
  - Web Application Security (0/0)

ℹ️  Testing user progress endpoint...
✅ User progress: Level 1, 0 XP, 0 day streak

ℹ️  Testing achievements endpoint...
✅ Fetched 14 achievements (0 earned)

ℹ️  Testing lesson completion...
✅ Lesson completed! Earned 50 XP, now level 1

============================================================
Test Summary
============================================================
Health Check................................ ✅ PASS
User Registration........................... ✅ PASS
User Login.................................. ✅ PASS
Training Modules............................ ✅ PASS
User Progress............................... ✅ PASS
Achievements................................ ✅ PASS
Lesson Completion........................... ✅ PASS

Results: 7/7 tests passed

✅ 🎉 All tests passed! System is working correctly!
```

---

## Frontend Hook Testing

### Test useAuth Hook

```typescript
import { useAuth } from './hooks';

const TestAuth = () => {
  const { login, register, logout, loading, error } = useAuth();

  const handleLogin = async () => {
    try {
      await login({ username: 'testuser', password: 'Test123!@#' });
      console.log('Login successful!');
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return <button onClick={handleLogin}>Login</button>;
};
```

### Test useTrainingModules Hook

```typescript
import { useTrainingModules } from './hooks';

const TestModules = () => {
  const { modules, loading, error } = useTrainingModules();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Modules: {modules.length}</h1>
      {modules.map(m => (
        <div key={m.id}>{m.title}</div>
      ))}
    </div>
  );
};
```

### Test useLessonCompletion Hook

```typescript
import { useLessonCompletion } from './hooks';

const TestCompletion = () => {
  const { completeLesson, loading } = useLessonCompletion();

  const handleComplete = async (lessonId: string) => {
    const result = await completeLesson(lessonId, 15);
    if (result) {
      alert(`Earned ${result.xp_earned} XP!`);
    }
  };

  return <button onClick={() => handleComplete('lesson-id')}>Complete</button>;
};
```

---

## Database Verification

### Check Tables

```sql
-- Connect to database
psql -d Cyber-SenseiDB

-- Check modules
SELECT id, title, total_lessons FROM training_modules ORDER BY order_index;

-- Check lessons
SELECT l.title, m.title as module 
FROM lessons l 
JOIN training_modules m ON l.module_id = m.id 
ORDER BY m.order_index, l.order_index;

-- Check achievements
SELECT achievement_key, title, requirement_type, requirement_value 
FROM achievements;

-- Check user progress
SELECT u.username, p.xp, p.level, p.current_streak 
FROM user_training_progress p 
JOIN users u ON p.user_id = u.id;

-- Check lesson completions
SELECT u.username, l.title, lc.completed_at 
FROM lesson_completions lc
JOIN users u ON lc.user_id = u.id
JOIN lessons l ON lc.lesson_id = l.id
ORDER BY lc.completed_at DESC;
```

---

## Performance Testing

### Test API Response Times

```bash
# Health endpoint
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Training modules (with auth)
curl -w "@curl-format.txt" -o /dev/null -s \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/training/modules
```

Create `curl-format.txt`:
```
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
```

---

## Load Testing

### Using Apache Bench

```bash
# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test training modules (with auth)
ab -n 100 -c 5 -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/training/modules
```

---

## Troubleshooting Tests

### Backend Tests Fail

**Issue**: "Backend is not running"
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it
cd backend
start_local.bat
```

**Issue**: "Database connection failed"
```bash
# Check PostgreSQL is running
pg_ctl status

# Check database exists
psql -l | findstr Cyber-SenseiDB
```

**Issue**: "Migration failed"
```bash
# Reset and rerun migration
alembic downgrade base
alembic upgrade head
```

### Frontend Tests Fail

**Issue**: "Cannot connect to backend"
- Check backend is running on port 8000
- Check CORS is enabled (already configured)
- Check API URL in `.env`

**Issue**: "401 Unauthorized"
- Token expired, login again
- Token not stored, check localStorage
- Token format wrong, should be `Bearer TOKEN`

### Integration Tests Fail

**Issue**: "User already exists"
- This is OK, test will continue
- Or delete user and rerun

**Issue**: "No modules found"
- Run seed script: `python scripts/seed_training_data.py`
- Check database: `SELECT COUNT(*) FROM training_modules;`

---

## Success Criteria

### Backend
- [ ] Health endpoint returns 200
- [ ] Can register new user
- [ ] Can login and get token
- [ ] Can fetch 7 training modules
- [ ] Can fetch user progress
- [ ] Can fetch 14 achievements
- [ ] Can complete lesson and earn XP

### Frontend
- [ ] App loads without errors
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Training page shows 7 modules
- [ ] Can view lessons in a module
- [ ] Can complete a lesson
- [ ] XP increases after completion
- [ ] Progress page shows stats
- [ ] Achievements page shows 14 achievements

### Integration
- [ ] Frontend connects to backend
- [ ] Data flows from backend to frontend
- [ ] Actions in frontend update backend
- [ ] Real-time updates work
- [ ] Token refresh works
- [ ] Error handling works

---

## Test Coverage

### Backend Endpoints
- ✅ POST /api/auth/register
- ✅ POST /api/auth/login
- ✅ POST /api/auth/refresh
- ✅ POST /api/auth/logout
- ✅ GET /api/training/modules
- ✅ GET /api/training/modules/{id}
- ✅ GET /api/training/modules/{id}/lessons
- ✅ GET /api/training/lessons/{id}
- ✅ POST /api/training/lessons/{id}/complete
- ✅ GET /api/progress
- ✅ POST /api/progress/xp
- ✅ POST /api/progress/streak
- ✅ GET /api/progress/activity
- ✅ GET /api/achievements
- ✅ POST /api/achievements/{id}/unlock

### Frontend Hooks
- ✅ useAuth
- ✅ useTrainingModules
- ✅ useLessonCompletion
- ✅ useProgress
- ✅ useAchievements
- ✅ useChatHistory
- ✅ useBackendSync

---

## Automated Testing

### Run All Tests

```bash
# Backend tests
cd backend
python test_setup.py

# Run backend tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Frontend tests (if you add them)
cd frontend
npm test
```

---

## Continuous Testing

### Watch Mode

```bash
# Backend - watch for changes
cd backend
pytest --watch

# Frontend - watch for changes
cd frontend
npm test -- --watch
```

---

## Test Reports

After running tests, check:
- Console output for pass/fail
- Coverage report in `backend/htmlcov/index.html`
- Backend logs in `backend/logs/`
- Browser console for frontend errors

---

## Next Steps After Testing

1. ✅ All tests pass
2. ⏳ Add more test cases
3. ⏳ Add unit tests
4. ⏳ Add E2E tests with Playwright
5. ⏳ Add performance tests
6. ⏳ Add security tests
7. ⏳ Setup CI/CD pipeline

---

**Happy Testing!** 🧪🚀
