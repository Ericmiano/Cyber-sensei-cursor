import { Trophy, Medal, Crown, TrendingUp } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useUserProgress } from "@/contexts/UserProgressContext";

// Simulated leaderboard data (frontend-only)
const MOCK_USERS = [
  { name: "ShadowByte", xp: 4850, level: 12, avatar: "🥷", streak: 15 },
  { name: "NullPointer", xp: 4200, level: 11, avatar: "💀", streak: 9 },
  { name: "CipherQueen", xp: 3800, level: 10, avatar: "👾", streak: 22 },
  { name: "ZeroDayDan", xp: 3100, level: 9, avatar: "🤖", streak: 7 },
  { name: "FirewallFox", xp: 2650, level: 8, avatar: "🦸", streak: 12 },
  { name: "PacketStorm", xp: 2200, level: 7, avatar: "⚡", streak: 5 },
  { name: "RootKit99", xp: 1800, level: 6, avatar: "🔮", streak: 3 },
];

const rankIcons = [
  <Crown key="1" className="h-5 w-5 text-neon-orange" />,
  <Medal key="2" className="h-5 w-5 text-primary" />,
  <Medal key="3" className="h-5 w-5 text-neon-green" />,
];

export default function Leaderboard() {
  const { progress } = useUserProgress();

  // Insert current user into leaderboard
  const allUsers = [...MOCK_USERS, {
    name: "You",
    xp: progress.xp,
    level: progress.level,
    avatar: "🎮",
    streak: progress.currentStreak,
  }].sort((a, b) => b.xp - a.xp);

  const userRank = allUsers.findIndex(u => u.name === "You") + 1;

  return (
    <Card className="bg-card/50 border-border/50 interactive-card overflow-hidden">
      <div className="h-1 animate-border-flow" />
      <CardHeader className="p-4 sm:p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neon-orange/10 flex items-center justify-center animate-glow-pulse">
              <Trophy className="h-5 w-5 text-neon-orange" />
            </div>
            <div>
              <CardTitle className="font-cyber text-xl text-primary">LEADERBOARD</CardTitle>
              <CardDescription className="text-xs sm:text-sm">Top cyber warriors this week</CardDescription>
            </div>
          </div>
          <Badge variant="outline" className="text-neon-green border-neon-green/30">
            <TrendingUp className="h-3 w-3 mr-1" />
            Rank #{userRank}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-4 sm:p-6 pt-0 sm:pt-0">
        <div className="space-y-2">
          {allUsers.slice(0, 8).map((user, index) => {
            const isCurrentUser = user.name === "You";
            return (
              <div
                key={user.name}
                className={cn(
                  "flex items-center gap-3 p-3 rounded-lg transition-all animate-slide-up",
                  isCurrentUser
                    ? "bg-primary/10 border border-primary/30 neon-border"
                    : "bg-muted/20 border border-transparent hover:border-border/50",
                )}
                style={{ animationDelay: `${index * 60}ms` }}
              >
                {/* Rank */}
                <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0">
                  {index < 3 ? rankIcons[index] : (
                    <span className="font-cyber text-sm text-muted-foreground">{index + 1}</span>
                  )}
                </div>

                {/* Avatar */}
                <span className="text-2xl flex-shrink-0">{user.avatar}</span>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      "font-medium text-sm truncate",
                      isCurrentUser && "text-primary font-cyber"
                    )}>
                      {user.name}
                    </span>
                    {isCurrentUser && (
                      <Badge className="bg-primary/20 text-primary text-[10px]">You</Badge>
                    )}
                  </div>
                  <span className="text-[10px] text-muted-foreground">
                    Level {user.level} • {user.streak}d streak
                  </span>
                </div>

                {/* XP */}
                <span className="font-cyber text-sm text-primary flex-shrink-0">
                  {user.xp.toLocaleString()} XP
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
