import { useEffect, useState } from "react";
import { Award } from "lucide-react";
import { cn } from "@/lib/utils";
import { ACHIEVEMENTS, useUserProgress } from "@/contexts/UserProgressContext";

export default function AchievementToast() {
  const { progress } = useUserProgress();
  const [newAchievement, setNewAchievement] = useState<typeof ACHIEVEMENTS[0] | null>(null);
  const [previousAchievements, setPreviousAchievements] = useState<string[]>([]);

  useEffect(() => {
    // Find newly earned achievements
    const newlyEarned = progress.achievementsEarned.filter(
      id => !previousAchievements.includes(id)
    );

    if (newlyEarned.length > 0 && previousAchievements.length > 0) {
      const achievement = ACHIEVEMENTS.find(a => a.id === newlyEarned[0]);
      if (achievement) {
        setNewAchievement(achievement);
        setTimeout(() => setNewAchievement(null), 5000);
      }
    }

    setPreviousAchievements(progress.achievementsEarned);
  }, [progress.achievementsEarned]);

  if (!newAchievement) return null;

  return (
    <div className={cn(
      "fixed top-4 right-4 z-50",
      "p-4 rounded-xl bg-card border-2 border-neon-green shadow-2xl",
      "animate-slide-up neon-glow-cyan",
      "max-w-sm"
    )}>
      <div className="flex items-center gap-4">
        <div className="text-4xl">{newAchievement.icon}</div>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Award className="h-4 w-4 text-neon-green" />
            <span className="text-xs font-medium text-neon-green uppercase tracking-wider">
              Achievement Unlocked!
            </span>
          </div>
          <h3 className="font-cyber text-lg text-primary">{newAchievement.title}</h3>
          <p className="text-sm text-muted-foreground">{newAchievement.description}</p>
        </div>
      </div>
    </div>
  );
}
