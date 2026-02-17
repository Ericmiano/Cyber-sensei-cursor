import { useState, useEffect } from "react";
import { Bell, Clock, Flame, Trophy, MessageSquare, BookOpen, Volume2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

interface NotificationSettings {
  dailyReminder: boolean;
  reminderTime: string;
  streakAlerts: boolean;
  achievementPopups: boolean;
  challengeNotifications: boolean;
  soundEnabled: boolean;
  learningTips: boolean;
}

const STORAGE_KEY = "cyber_sensei_notifications";

const defaultSettings: NotificationSettings = {
  dailyReminder: true,
  reminderTime: "18:00",
  streakAlerts: true,
  achievementPopups: true,
  challengeNotifications: true,
  soundEnabled: false,
  learningTips: true,
};

export default function NotificationSettings() {
  const [settings, setSettings] = useState<NotificationSettings>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        return { ...defaultSettings, ...JSON.parse(saved) };
      } catch {
        return defaultSettings;
      }
    }
    return defaultSettings;
  });

  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      setHasChanges(JSON.stringify(settings) !== JSON.stringify(parsed));
    }
  }, [settings]);

  const updateSetting = <K extends keyof NotificationSettings>(
    key: K,
    value: NotificationSettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const saveSettings = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    setHasChanges(false);
    toast({
      title: "Settings Saved",
      description: "Your notification preferences have been updated.",
    });
  };

  const notificationTypes = [
    {
      key: "dailyReminder" as const,
      title: "Daily Learning Reminder",
      description: "Get reminded to continue your learning streak",
      icon: Clock,
      hasTimeSelect: true,
    },
    {
      key: "streakAlerts" as const,
      title: "Streak Alerts",
      description: "Notifications when your streak is at risk",
      icon: Flame,
    },
    {
      key: "achievementPopups" as const,
      title: "Achievement Celebrations",
      description: "Celebrate when you earn new badges",
      icon: Trophy,
    },
    {
      key: "challengeNotifications" as const,
      title: "Challenge Updates",
      description: "Daily challenge reminders and completion alerts",
      icon: BookOpen,
    },
    {
      key: "learningTips" as const,
      title: "Learning Tips",
      description: "Helpful tips and cybersecurity facts",
      icon: MessageSquare,
    },
    {
      key: "soundEnabled" as const,
      title: "Sound Effects",
      description: "Play sounds for interactions and achievements",
      icon: Volume2,
    },
  ];

  return (
    <Card className="bg-card/50 border-border/50">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Bell className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="font-cyber text-xl text-primary">
                NOTIFICATIONS
              </CardTitle>
              <CardDescription>
                Manage how Cyber Sensei keeps you informed
              </CardDescription>
            </div>
          </div>
          {hasChanges && (
            <Button onClick={saveSettings} className="neon-glow-cyan animate-fade-in">
              Save Changes
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {notificationTypes.map(({ key, title, description, icon: Icon, hasTimeSelect }) => (
          <div
            key={key}
            className={cn(
              "p-4 rounded-lg border transition-all duration-300",
              settings[key]
                ? "bg-primary/5 border-primary/30"
                : "bg-muted/30 border-border/50"
            )}
          >
            <div className="flex items-start gap-4">
              <div className={cn(
                "w-10 h-10 rounded-lg flex items-center justify-center transition-colors",
                settings[key] ? "bg-primary/20" : "bg-muted/50"
              )}>
                <Icon className={cn(
                  "h-5 w-5 transition-colors",
                  settings[key] ? "text-primary" : "text-muted-foreground"
                )} />
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-base font-medium">{title}</Label>
                    <p className="text-sm text-muted-foreground">{description}</p>
                  </div>
                  <Switch
                    checked={settings[key]}
                    onCheckedChange={(checked) => updateSetting(key, checked)}
                  />
                </div>

                {hasTimeSelect && settings[key] && (
                  <div className="mt-4 flex items-center gap-3 animate-fade-in">
                    <Label className="text-sm text-muted-foreground">Remind me at:</Label>
                    <Select
                      value={settings.reminderTime}
                      onValueChange={(value) => updateSetting("reminderTime", value)}
                    >
                      <SelectTrigger className="w-32 bg-muted/50">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {["08:00", "09:00", "12:00", "15:00", "18:00", "20:00", "21:00"].map((time) => (
                          <SelectItem key={time} value={time}>
                            {time}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        <div className="p-4 rounded-lg bg-muted/30 border border-dashed border-border text-center">
          <p className="text-sm text-muted-foreground">
            💡 Browser notification permissions are required for push notifications.
            <br />
            <span className="text-primary">This is a frontend preview - backend integration needed for real notifications.</span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
