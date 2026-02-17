import { 
  Shield, 
  TrendingUp, 
  Clock, 
  Award, 
  BookOpen, 
  MessageSquare,
  Target,
  Flame,
  Zap,
  Star,
  ChevronRight,
  Sparkles,
  Trophy
} from "lucide-react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useUserProgress, ACHIEVEMENTS } from "@/contexts/UserProgressContext";
import XPBar from "@/components/gamification/XPBar";
import StreakDisplay from "@/components/gamification/StreakDisplay";
import DailyChallenges from "@/components/gamification/DailyChallenges";
import Leaderboard from "@/components/gamification/Leaderboard";

export default function DashboardPage() {
  const { progress, getAchievements } = useUserProgress();
  
  const completedLessons = progress.lessonsCompleted.filter(l => l.completed).length;
  const achievements = getAchievements();
  const earnedAchievements = achievements.filter(a => a.earned);
  
  // Calculate skill levels based on completed lessons per module
  const skillLevels = [
    { skill: "Network Security", level: Math.min(100, completedLessons * 5), color: "neon-cyan" },
    { skill: "Cryptography", level: Math.min(100, progress.totalQuizzesPassed * 4), color: "neon-magenta" },
    { skill: "Ethical Hacking", level: Math.min(100, progress.totalExercisesCompleted * 6), color: "neon-purple" },
    { skill: "Secure Coding", level: Math.min(100, Math.floor(progress.xp / 100)), color: "neon-green" },
    { skill: "Incident Response", level: Math.min(100, progress.currentStreak * 3), color: "neon-orange" },
  ];

  const statsCards = [
    {
      title: "Lessons",
      fullTitle: "Lessons Completed",
      value: completedLessons.toString(),
      icon: BookOpen,
      color: "primary",
      change: `Level ${progress.level}`,
    },
    {
      title: "Sessions",
      fullTitle: "Chat Sessions",
      value: progress.totalChatMessages.toString(),
      icon: MessageSquare,
      color: "secondary",
      change: "AI Interactions",
    },
    {
      title: "Streak",
      fullTitle: "Learning Streak",
      value: progress.currentStreak.toString(),
      unit: "days",
      icon: Flame,
      color: "accent",
      change: progress.currentStreak >= progress.longestStreak ? "Best!" : `Best: ${progress.longestStreak}`,
    },
    {
      title: "XP",
      fullTitle: "Total XP",
      value: progress.xp.toString(),
      icon: Zap,
      color: "primary",
      change: `+${progress.totalQuizzesPassed * 100 + progress.totalExercisesCompleted * 75}`,
    },
  ];

  // Get recent activity from activity log
  const recentActivity = progress.activityLog.slice(0, 5).map(activity => ({
    type: activity.type,
    title: activity.title + (activity.description ? `: ${activity.description}` : ""),
    time: new Date(activity.timestamp).toLocaleDateString(),
    icon: activity.type === "lesson" ? BookOpen : 
          activity.type === "quiz" ? Target : 
          activity.type === "exercise" ? Target :
          activity.type === "achievement" ? Award : 
          activity.type === "xp" ? Zap : MessageSquare,
    xp: activity.xpEarned,
  }));

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6 sm:mb-8 animate-slide-up">
        <h1 className="font-cyber text-2xl sm:text-3xl font-bold mb-2 flex flex-wrap items-center gap-2 sm:gap-3">
          <span className="text-primary animate-text-glow">DASHBOARD</span>
          <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 text-secondary animate-pulse-glow" />
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground">
          Welcome back, Cyber Warrior. Here's your training progress.
        </p>
      </div>

      {/* XP Bar and Streak */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
        <Card className="bg-card/50 border-border/50 p-4 sm:p-6 interactive-card">
          <XPBar showDetails />
        </Card>
        <Card className="bg-card/50 border-border/50 p-4 sm:p-6 interactive-card">
          <StreakDisplay />
        </Card>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
        {statsCards.map((stat, index) => (
          <Card
            key={stat.fullTitle}
            className={cn(
              "bg-card/50 border-border/50",
              "interactive-card hover-lift",
              "animate-slide-up"
            )}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <CardContent className="p-3 sm:p-6">
              <div className="flex items-start justify-between mb-2 sm:mb-4 gap-1">
                <div
                  className={cn(
                    "w-8 h-8 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center flex-shrink-0",
                    "bg-primary/10 group-hover:bg-primary/20 transition-colors"
                  )}
                >
                  <stat.icon className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                </div>
                <Badge variant="outline" className="text-[10px] sm:text-xs text-neon-green border-neon-green/30 truncate">
                  {stat.change}
                </Badge>
              </div>
              <div className="space-y-0.5 sm:space-y-1">
                <h3 className="text-[10px] sm:text-sm text-muted-foreground">
                  <span className="sm:hidden">{stat.title}</span>
                  <span className="hidden sm:inline">{stat.fullTitle}</span>
                </h3>
                <div className="flex items-baseline gap-1">
                  <span className="font-cyber text-xl sm:text-3xl font-bold text-primary neon-text-cyan">
                    {stat.value}
                  </span>
                  {stat.unit && <span className="text-muted-foreground text-[10px] sm:text-sm">{stat.unit}</span>}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Daily Challenges & Leaderboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
        <DailyChallenges />
        <Leaderboard />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Skill Levels */}
        <Card className="lg:col-span-2 bg-card/50 border-border/50 interactive-card">
          <CardHeader className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <CardTitle className="font-cyber text-lg sm:text-xl text-primary">SKILL LEVELS</CardTitle>
                <CardDescription className="text-xs sm:text-sm">Your proficiency across cybersecurity domains</CardDescription>
              </div>
              <Button variant="ghost" size="sm" asChild className="gap-1 self-start">
                <Link to="/training">
                  Train More <ChevronRight className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0 space-y-4 sm:space-y-6">
            {skillLevels.map((skill, index) => (
              <div 
                key={skill.skill} 
                className="animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex justify-between text-xs sm:text-sm mb-1.5 sm:mb-2">
                  <span className="text-foreground font-medium">{skill.skill}</span>
                  <span className="text-primary">{skill.level}%</span>
                </div>
                <div className="relative">
                  <Progress value={skill.level} className="h-2 sm:h-3 bg-muted" />
                  {skill.level >= 50 && (
                    <div 
                      className="absolute top-1/2 -translate-y-1/2 text-[10px] sm:text-xs"
                      style={{ left: `${Math.max(10, skill.level - 5)}%` }}
                    >
                      ⭐
                    </div>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="bg-card/50 border-border/50 interactive-card">
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="font-cyber text-lg sm:text-xl text-primary">RECENT ACTIVITY</CardTitle>
            <CardDescription className="text-xs sm:text-sm">Your latest learning actions</CardDescription>
          </CardHeader>
          <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0">
            {recentActivity.length > 0 ? (
              <div className="space-y-3 sm:space-y-4">
                {recentActivity.map((activity, index) => (
                  <div
                    key={index}
                    className={cn(
                      "flex items-start gap-2 sm:gap-3 pb-3 sm:pb-4 border-b border-border/30 last:border-0 last:pb-0",
                      "animate-slide-up hover:bg-primary/5 -mx-2 px-2 py-1.5 sm:py-2 rounded-lg transition-colors"
                    )}
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <activity.icon className="h-3 w-3 sm:h-4 sm:w-4 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs sm:text-sm text-foreground truncate">{activity.title}</p>
                      <div className="flex items-center gap-1 sm:gap-2">
                        <p className="text-[10px] sm:text-xs text-muted-foreground">{activity.time}</p>
                        {activity.xp && (
                          <Badge variant="outline" className="text-[10px] sm:text-xs text-neon-orange border-neon-orange/30">
                            +{activity.xp} XP
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 sm:py-8 animate-fade-in">
                <div className="text-3xl sm:text-4xl mb-2">🎯</div>
                <p className="text-xs sm:text-sm text-muted-foreground">
                  No activity yet. Start learning to see your progress!
                </p>
                <Button asChild className="mt-3 sm:mt-4 neon-glow-cyan text-xs sm:text-sm">
                  <Link to="/training">Start Training</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Achievements */}
        <Card className="col-span-1 lg:col-span-3 bg-card/50 border-border/50 interactive-card overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-neon-cyan via-neon-purple to-neon-magenta animate-border-flow" />
          <CardHeader className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <CardTitle className="font-cyber text-lg sm:text-xl text-primary">
                  ACHIEVEMENTS ({earnedAchievements.length}/{achievements.length})
                </CardTitle>
                <CardDescription className="text-xs sm:text-sm">Badges earned through your cybersecurity journey</CardDescription>
              </div>
              <Badge variant="outline" className="text-neon-purple border-neon-purple/30 self-start">
                <Trophy className="h-3 w-3 mr-1" />
                {Math.round((earnedAchievements.length / achievements.length) * 100)}% Complete
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0">
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-7 gap-2 sm:gap-4">
              {achievements.map((achievement, index) => (
                <div
                  key={achievement.id}
                  className={cn(
                    "text-center p-2 sm:p-4 rounded-lg border transition-all duration-300",
                    "animate-slide-up hover-lift",
                    achievement.earned
                      ? "bg-primary/10 border-primary/30 hover:border-primary"
                      : "bg-muted/30 border-border/30 opacity-50 grayscale"
                  )}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className={cn(
                    "text-xl sm:text-3xl mb-1 sm:mb-2",
                    achievement.earned && "animate-float"
                  )}
                  style={{ animationDelay: `${index * 100}ms` }}
                  >
                    {achievement.icon}
                  </div>
                  <h4 className="font-medium text-[10px] sm:text-sm mb-0.5 sm:mb-1 line-clamp-1">{achievement.title}</h4>
                  <p className="text-[8px] sm:text-xs text-muted-foreground line-clamp-2 hidden sm:block">{achievement.description}</p>
                  {achievement.earned && (
                    <Badge className="mt-1 sm:mt-2 bg-neon-green/20 text-neon-green text-[8px] sm:text-xs animate-glow-pulse">
                      Earned
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
