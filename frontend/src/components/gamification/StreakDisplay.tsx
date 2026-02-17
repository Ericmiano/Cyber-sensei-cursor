import { useUserProgress } from "@/contexts/UserProgressContext";
import { Flame, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

interface StreakDisplayProps {
  variant?: "compact" | "full";
  className?: string;
}

export default function StreakDisplay({ variant = "full", className }: StreakDisplayProps) {
  const { progress } = useUserProgress();
  
  const isActiveToday = progress.lastActiveDate === new Date().toDateString();
  
  if (variant === "compact") {
    return (
      <div className={cn("flex items-center gap-1.5", className)}>
        <Flame className={cn(
          "h-5 w-5",
          progress.currentStreak > 0 ? "text-neon-orange animate-pulse" : "text-muted-foreground"
        )} />
        <span className={cn(
          "font-cyber text-lg",
          progress.currentStreak > 0 ? "text-neon-orange" : "text-muted-foreground"
        )}>
          {progress.currentStreak}
        </span>
      </div>
    );
  }

  return (
    <div className={cn("flex items-center gap-4", className)}>
      <div className="flex items-center gap-2">
        <div className={cn(
          "w-12 h-12 rounded-xl flex items-center justify-center",
          progress.currentStreak > 0 
            ? "bg-neon-orange/20 neon-glow-magenta" 
            : "bg-muted"
        )}>
          <Flame className={cn(
            "h-6 w-6",
            progress.currentStreak > 0 ? "text-neon-orange" : "text-muted-foreground"
          )} />
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Current Streak</p>
          <p className={cn(
            "font-cyber text-2xl",
            progress.currentStreak > 0 ? "text-neon-orange" : "text-muted-foreground"
          )}>
            {progress.currentStreak} days
          </p>
        </div>
      </div>
      
      <div className="h-10 w-px bg-border/50" />
      
      <div className="flex items-center gap-2">
        <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
          <Calendar className="h-6 w-6 text-primary" />
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Longest Streak</p>
          <p className="font-cyber text-2xl text-primary">
            {progress.longestStreak} days
          </p>
        </div>
      </div>
      
      {!isActiveToday && progress.currentStreak > 0 && (
        <div className="ml-auto px-3 py-1.5 bg-neon-orange/10 border border-neon-orange/30 rounded-lg">
          <p className="text-xs text-neon-orange font-medium">
            Complete a lesson today to keep your streak!
          </p>
        </div>
      )}
    </div>
  );
}
