import { useState } from "react";
import { User, Camera, Trophy, Clock, Target, Trash2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { useUserProgress } from "@/contexts/UserProgressContext";
import { toast } from "@/hooks/use-toast";

const AVATAR_OPTIONS = [
  "🥷", "🦸", "🧙", "🤖", "👾", "🎮", "💀", "🔮", "⚡", "🛡️", "🔐", "💻"
];

interface UserProfile {
  username: string;
  avatar: string;
  bio: string;
  joinDate: string;
}

const PROFILE_STORAGE_KEY = "cyber_sensei_profile";

export default function UserProfileSettings() {
  const { progress, resetProgress, getAchievements } = useUserProgress();
  const achievements = getAchievements();
  const earnedCount = achievements.filter(a => a.earned).length;

  const [profile, setProfile] = useState<UserProfile>(() => {
    const saved = localStorage.getItem(PROFILE_STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        // Use defaults
      }
    }
    return {
      username: "Cyber Warrior",
      avatar: "🥷",
      bio: "Aspiring cybersecurity professional",
      joinDate: new Date().toISOString(),
    };
  });

  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState(profile);

  const saveProfile = () => {
    setProfile(editedProfile);
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(editedProfile));
    setIsEditing(false);
    toast({
      title: "Profile Saved",
      description: "Your profile has been updated successfully.",
    });
  };

  const handleResetProgress = () => {
    if (window.confirm("Are you sure you want to reset all your progress? This cannot be undone.")) {
      resetProgress();
      toast({
        title: "Progress Reset",
        description: "All your progress has been reset.",
        variant: "destructive",
      });
    }
  };

  const daysSinceJoin = Math.floor(
    (Date.now() - new Date(profile.joinDate).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <Card className="bg-card/50 border-border/50 overflow-hidden">
        <div className="h-24 bg-gradient-to-r from-primary/20 via-secondary/20 to-accent/20 animate-border-flow" />
        <CardContent className="relative pb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-end gap-4 -mt-12">
            <div className="relative group">
              <div className={cn(
                "w-24 h-24 rounded-xl bg-card border-4 border-card",
                "flex items-center justify-center text-5xl",
                "shadow-lg transition-all group-hover:scale-105"
              )}>
                {profile.avatar}
              </div>
              {isEditing && (
                <div className="absolute inset-0 bg-background/80 rounded-xl flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <Camera className="h-6 w-6 text-primary" />
                </div>
              )}
            </div>

            <div className="flex-1">
              {isEditing ? (
                <Input
                  value={editedProfile.username}
                  onChange={(e) => setEditedProfile({ ...editedProfile, username: e.target.value })}
                  className="font-cyber text-xl bg-muted/50 border-primary/30"
                  placeholder="Username"
                />
              ) : (
                <h2 className="font-cyber text-2xl text-primary">{profile.username}</h2>
              )}
              <div className="flex items-center gap-3 mt-1 text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {daysSinceJoin} days
                </span>
                <span className="flex items-center gap-1">
                  <Trophy className="h-4 w-4" />
                  {earnedCount} badges
                </span>
                <Badge className="bg-primary/20 text-primary">Level {progress.level}</Badge>
              </div>
            </div>

            <Button
              variant={isEditing ? "default" : "outline"}
              onClick={isEditing ? saveProfile : () => { setIsEditing(true); setEditedProfile(profile); }}
              className={isEditing ? "neon-glow-cyan" : ""}
            >
              {isEditing ? "Save Profile" : "Edit Profile"}
            </Button>
          </div>

          {/* Avatar Selection */}
          {isEditing && (
            <div className="mt-6 p-4 rounded-lg bg-muted/30 border border-border/50 animate-fade-in">
              <Label className="text-sm font-medium mb-3 block">Choose Avatar</Label>
              <div className="flex flex-wrap gap-2">
                {AVATAR_OPTIONS.map((emoji) => (
                  <button
                    key={emoji}
                    onClick={() => setEditedProfile({ ...editedProfile, avatar: emoji })}
                    className={cn(
                      "w-12 h-12 rounded-lg text-2xl transition-all hover:scale-110",
                      editedProfile.avatar === emoji
                        ? "bg-primary/20 border-2 border-primary"
                        : "bg-muted/50 border border-border/50 hover:border-primary/50"
                    )}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Bio */}
          <div className="mt-4">
            {isEditing ? (
              <div className="space-y-2">
                <Label className="text-sm font-medium">Bio</Label>
                <Input
                  value={editedProfile.bio}
                  onChange={(e) => setEditedProfile({ ...editedProfile, bio: e.target.value })}
                  className="bg-muted/50 border-primary/30"
                  placeholder="Tell us about yourself..."
                  maxLength={100}
                />
              </div>
            ) : (
              <p className="text-muted-foreground">{profile.bio}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Stats Summary */}
      <Card className="bg-card/50 border-border/50">
        <CardHeader>
          <CardTitle className="font-cyber text-lg text-primary">STATS SUMMARY</CardTitle>
          <CardDescription>Your learning journey at a glance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Total XP", value: progress.xp.toLocaleString(), icon: "⚡" },
              { label: "Current Level", value: progress.level.toString(), icon: "🎯" },
              { label: "Best Streak", value: `${progress.longestStreak} days`, icon: "🔥" },
              { label: "Lessons Done", value: progress.lessonsCompleted.filter(l => l.completed).length.toString(), icon: "📚" },
            ].map((stat) => (
              <div
                key={stat.label}
                className="p-4 rounded-lg bg-muted/30 border border-border/50 text-center hover-lift"
              >
                <div className="text-2xl mb-1">{stat.icon}</div>
                <div className="font-cyber text-xl text-primary">{stat.value}</div>
                <div className="text-xs text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="bg-destructive/5 border-destructive/30">
        <CardHeader>
          <CardTitle className="font-cyber text-lg text-destructive">DANGER ZONE</CardTitle>
          <CardDescription>Irreversible actions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 rounded-lg bg-destructive/10 border border-destructive/20">
            <div>
              <h4 className="font-medium text-destructive">Reset All Progress</h4>
              <p className="text-sm text-muted-foreground">
                This will delete all your XP, achievements, and learning history.
              </p>
            </div>
            <Button
              variant="destructive"
              onClick={handleResetProgress}
              className="gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Reset
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
