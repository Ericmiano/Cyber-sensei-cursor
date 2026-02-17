import { useUserProgress } from "@/contexts/UserProgressContext";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { Zap, Star } from "lucide-react";

interface XPBarProps {
  showDetails?: boolean;
  className?: string;
}

export default function XPBar({ showDetails = true, className }: XPBarProps) {
  const { progress, getXPForNextLevel, getCurrentLevelXP } = useUserProgress();
  
  const xpForNext = getXPForNextLevel();
  const currentLevelXP = getCurrentLevelXP();
  const progressPercent = (currentLevelXP / xpForNext) * 100;

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 neon-glow-cyan">
            <Star className="h-4 w-4 text-primary" />
          </div>
          <span className="font-cyber text-lg text-primary">LVL {progress.level}</span>
        </div>
        {showDetails && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Zap className="h-4 w-4 text-neon-orange" />
            <span className="font-mono">{progress.xp.toLocaleString()} XP</span>
          </div>
        )}
      </div>
      
      <div className="space-y-1">
        <Progress 
          value={progressPercent} 
          className="h-3 bg-muted neon-glow-cyan"
        />
        {showDetails && (
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{currentLevelXP} XP</span>
            <span>{xpForNext} XP to Level {progress.level + 1}</span>
          </div>
        )}
      </div>
    </div>
  );
}
