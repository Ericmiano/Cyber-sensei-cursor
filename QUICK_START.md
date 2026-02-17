# Quick Start Guide 🚀

## Get Up and Running in 5 Minutes

### Step 1: Start Backend (2 minutes)

```bash
cd backend
venv\Scripts\activate
alembic upgrade head
python scripts\seed_training_data.py
start_local.bat
```

**Verify**: Visit http://localhost:8000/docs - You should see Swagger UI

### Step 2: Start Frontend (1 minute)

```bash
cd frontend
npm run dev
```

**Verify**: Visit http://localhost:8080 - You should see the app

### Step 3: Test Integration (2 minutes)

1. **Register a user** in the app
2. **Login** with your credentials
3. **Go to Training** page - You should see 7 modules from backend
4. **Complete a lesson** - You should earn XP
5. **Check Progress** page - You should see your stats

---

## Using the New Hooks

### In Your Components

```typescript
import { useTrainingModules, useLessonCompletion } from './hooks';

export const MyComponent = () => {
  const { modules, loading } = useTrainingModules();
  const { completeLesson } = useLessonCompletion();

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {modules.map(module => (
        <div key={module.id}>
          <h2>{module.title}</h2>
          <button onClick={() => completeLesson(module.lessons[0].id, 15)}>
            Complete First Lesson
          </button>
        </div>
      ))}
    </div>
  );
};
```

### Replace Old Pages

1. **Training Page**: Use `TrainingWithBackend.tsx` as reference
2. **Progress Page**: Use `ProgressWithBackend.tsx` as reference
3. **Achievements Page**: Use `AchievementsWithBackend.tsx` as reference

---

## Available Hooks

```typescript
// Authentication
const { login, register, logout } = useAuth();

// Training
const { modules, getModuleLessons } = useTrainingModules();
const { completeLesson } = useLessonCompletion();

// Progress
const { progress, addXP, updateStreak } = useProgress();

// Achievements
const { achievements, unlockAchievement } = useAchievements();

// Chat
const { messages, sendMessage } = useChatHistory();

// Auto-sync
useBackendSync(); // Add to App.tsx
```

---

## Testing Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 8080
- [ ] Can register new user
- [ ] Can login
- [ ] Can see 7 training modules
- [ ] Can complete a lesson
- [ ] XP increases after completion
- [ ] Progress page shows stats
- [ ] Achievements page shows 14 achievements

---

## Troubleshooting

**Backend not starting?**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend not connecting?**
- Check backend is running: `curl http://localhost:8000/health`
- Check API URL in `.env`: `VITE_API_URL=http://localhost:8000/api`

**401 Errors?**
- Login again to get fresh token
- Check token in localStorage: `localStorage.getItem('access_token')`

---

## Success!

If you can:
1. ✅ See training modules from backend
2. ✅ Complete a lesson and earn XP
3. ✅ See progress update in real-time

Then your integration is working perfectly! 🎉

---

## Next Steps

1. Replace old pages with new backend-integrated pages
2. Add error boundaries
3. Add loading skeletons
4. Add toast notifications
5. Test all user flows

---

## Documentation

- **Full Integration Guide**: `FRONTEND_INTEGRATION_COMPLETE.md`
- **Backend Setup**: `SETUP_INSTRUCTIONS.md`
- **API Documentation**: http://localhost:8000/docs

---

**Need Help?**
- Check `FRONTEND_INTEGRATION_COMPLETE.md` for detailed docs
- Check `SETUP_CHECKLIST.md` for step-by-step verification
- Check backend logs in `backend/logs/`

Happy coding! 🚀
