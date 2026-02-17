import { useState, useEffect } from "react";
import { Target, Clock, Zap, CheckCircle2, Lock, RefreshCw, Trophy, Flame } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { useUserProgress } from "@/contexts/UserProgressContext";

interface Challenge {
  id: string;
  title: string;
  description: string;
  type: "lesson" | "quiz" | "exercise" | "streak" | "chat";
  requirement: number;
  xpReward: number;
  difficulty: "easy" | "medium" | "hard";
  icon: typeof Target;
}

const DAILY_CHALLENGES: Challenge[] = [
  {
    id: "complete_lesson",
    title: "Knowledge Seeker",
    description: "Complete 2 lessons today",
    type: "lesson",
    requirement: 2,
    xpReward: 100,
    difficulty: "easy",
    icon: Target,
  },
  {
    id: "pass_quiz",
    title: "Quiz Champion",
    description: "Pass a quiz with 80%+ score",
    type: "quiz",
    requirement: 1,
    xpReward: 150,
    difficulty: "medium",
    icon: Trophy,
  },
  {
    id: "complete_exercise",
    title: "Hands-On Hacker",
    description: "Complete 2 interactive exercises",
    type: "exercise",
    requirement: 2,
    xpReward: 200,
    difficulty: "medium",
    icon: Zap,
  },
  {
    id: "maintain_streak",
    title: "Consistency King",
    description: "Maintain your learning streak",
    type: "streak",
    requirement: 1,
    xpReward: 75,
    difficulty: "easy",
    icon: Flame,
  },
  {
    id: "chat_ai",
    title: "Curious Mind",
    description: "Ask the AI Sensei 5 questions",
    type: "chat",
    requirement: 5,
    xpReward: 50,
    difficulty: "easy",
    icon: Target,
  },
];

const difficultyColors = {
  easy: "bg-neon-green/20 text-neon-green border-neon-green/30",
  medium: "bg-neon-orange/20 text-neon-orange border-neon-orange/30",
  hard: "bg-neon-magenta/20 text-neon-magenta border-neon-magenta/30",
};

interface DailyProgress {
  date: string;
  completedChallenges: string[];
  lessonsToday: number;
  quizzesToday: number;
  exercisesToday: number;
  chatToday: number;
}

const STORAGE_KEY = "cyber_sensei_daily_progress";

export default function DailyChallenges() {
  const { progress, addXP } = useUserProgress();
  const [dailyProgress, setDailyProgress] = useState<DailyProgress>(() => {
    const today = new Date().toDateString();
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.date === today) {
          return parsed;
        }
      } catch {
        // Reset on parse error
      }
    }
    return {
      date: today,
      completedChallenges: [],
      lessonsToday: 0,
      quizzesToday: 0,
      exercisesToday: 0,
      chatToday: 0,
    };
  });

  const [timeRemaining, setTimeRemaining] = useState("");

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dailyProgress));
  }, [dailyProgress]);

  useEffect(() => {
    const updateTimer = () => {
      const now = new Date();
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(0, 0, 0, 0);
      
      const diff = tomorrow.getTime() - now.getTime();
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      
      setTimeRemaining(`${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, []);

  const getChallengeProgress = (challenge: Challenge): number => {
    switch (challenge.type) {
      case "lesson":
        return dailyProgress.lessonsToday;
      case "quiz":
        return dailyProgress.quizzesToday;
      case "exercise":
        return dailyProgress.exercisesToday;
      case "streak":
        return progress.currentStreak > 0 ? 1 : 0;
      case "chat":
        return dailyProgress.chatToday;
      default:
        return 0;
    }
  };

  const isChallengeComplete = (challenge: Challenge): boolean => {
    return dailyProgress.completedChallenges.includes(challenge.id);
  };

  const canClaimReward = (challenge: Challenge): boolean => {
    return getChallengeProgress(challenge) >= challenge.requirement && !isChallengeComplete(challenge);
  };

  const claimReward = (challenge: Challenge) => {
    if (!canClaimReward(challenge)) return;
    
    addXP(challenge.xpReward, `Daily Challenge: ${challenge.title}`);
    setDailyProgress(prev => ({
      ...prev,
      completedChallenges: [...prev.completedChallenges, challenge.id],
    }));
  };

  const todaysChallenges = DAILY_CHALLENGES.slice(0, 3); // Show 3 daily challenges
  const completedCount = todaysChallenges.filter(c => isChallengeComplete(c)).length;
  const totalXP = todaysChallenges.reduce((acc, c) => acc + c.xpReward, 0);
  const earnedXP = todaysChallenges
    .filter(c => isChallengeComplete(c))
    .reduce((acc, c) => acc + c.xpReward, 0);

  return (
    <Card className="bg-card/50 border-border/50 interactive-card overflow-hidden">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-neon-orange/20 to-neon-magenta/20 flex items-center justify-center animate-glow-pulse">
              <Target className="h-5 w-5 text-neon-orange" />
            </div>
            <div>
              <CardTitle className="font-cyber text-xl text-primary">DAILY CHALLENGES</CardTitle>
              <CardDescription className="flex items-center gap-2">
                <Clock className="h-3 w-3" />
                Resets in {timeRemaining}
              </CardDescription>
            </div>
          </div>
          <Badge variant="outline" className="text-neon-cyan border-neon-cyan/30">
            {completedCount}/{todaysChallenges.length} Complete
          </Badge>
        </div>
        
        {/* Overall Progress */}
        <div className="mt-4">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-muted-foreground">Daily XP Progress</span>
            <span className="text-neon-green font-medium">{earnedXP}/{totalXP} XP</span>
          </div>
          <Progress value={(earnedXP / totalXP) * 100} className="h-2 bg-muted" />
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {todaysChallenges.map((challenge, index) => {
          const currentProgress = getChallengeProgress(challenge);
          const isComplete = isChallengeComplete(challenge);
          const canClaim = canClaimReward(challenge);
          const progressPercent = Math.min((currentProgress / challenge.requirement) * 100, 100);

          return (
            <div
              key={challenge.id}
              className={cn(
                "p-4 rounded-lg border transition-all duration-300",
                "animate-slide-up",
                isComplete 
                  ? "bg-neon-green/5 border-neon-green/30" 
                  : canClaim
                  ? "bg-neon-orange/5 border-neon-orange/30 hover:border-neon-orange animate-glow-pulse"
                  : "bg-muted/30 border-border/50 hover:border-primary/30"
              )}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-start gap-4">
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center transition-all",
                  isComplete 
                    ? "bg-neon-green/20" 
                    : canClaim
                    ? "bg-neon-orange/20"
                    : "bg-primary/10"
                )}>
                  {isComplete ? (
                    <CheckCircle2 className="h-5 w-5 text-neon-green" />
                  ) : (
                    <challenge.icon className={cn(
                      "h-5 w-5",
                      canClaim ? "text-neon-orange" : "text-primary"
                    )} />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className={cn(
                      "font-medium",
                      isComplete && "text-neon-green"
                    )}>
                      {challenge.title}
                    </h4>
                    <Badge 
                      variant="outline" 
                      className={cn("text-xs", difficultyColors[challenge.difficulty])}
                    >
                      {challenge.difficulty}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{challenge.description}</p>
                  
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <Progress value={progressPercent} className="h-2 bg-muted" />
                    </div>
                    <span className="text-xs text-muted-foreground whitespace-nowrap">
                      {currentProgress}/{challenge.requirement}
                    </span>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-2">
                  <Badge variant="outline" className="text-neon-orange border-neon-orange/30">
                    <Zap className="h-3 w-3 mr-1" />
                    {challenge.xpReward} XP
                  </Badge>
                  {canClaim && (
                    <Button 
                      size="sm" 
                      onClick={() => claimReward(challenge)}
                      className="neon-glow-cyan text-xs"
                    >
                      Claim
                    </Button>
                  )}
                  {isComplete && (
                    <span className="text-xs text-neon-green">Claimed!</span>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {completedCount === todaysChallenges.length && (
          <div className="text-center py-4 animate-fade-in">
            <div className="text-4xl mb-2">🎉</div>
            <p className="text-neon-green font-cyber">ALL CHALLENGES COMPLETE!</p>
            <p className="text-sm text-muted-foreground">Come back tomorrow for new challenges</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Export function to update daily progress from other components
export function useDailyChallenges() {
  const today = new Date().toDateString();
  
  const incrementProgress = (type: "lesson" | "quiz" | "exercise" | "chat") => {
    const saved = localStorage.getItem(STORAGE_KEY);
    let current: DailyProgress = {
      date: today,
      completedChallenges: [],
      lessonsToday: 0,
      quizzesToday: 0,
      exercisesToday: 0,
      chatToday: 0,
    };
    
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.date === today) {
          current = parsed;
        }
      } catch {
        // Use default
      }
    }

    switch (type) {
      case "lesson":
        current.lessonsToday += 1;
        break;
      case "quiz":
        current.quizzesToday += 1;
        break;
      case "exercise":
        current.exercisesToday += 1;
        break;
      case "chat":
        current.chatToday += 1;
        break;
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
  };

  return { incrementProgress };
}
