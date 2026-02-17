import { useState, useEffect } from "react";
import { Keyboard, Command, Search, Home, MessageSquare, BookOpen, Settings as SettingsIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { useNavigate } from "react-router-dom";

interface Shortcut {
  keys: string[];
  description: string;
  action: string;
  icon: typeof Home;
}

const shortcuts: Shortcut[] = [
  { keys: ["Ctrl/⌘", "K"], description: "Open command palette", action: "palette", icon: Command },
  { keys: ["Ctrl/⌘", "/"], description: "Open search", action: "search", icon: Search },
  { keys: ["G", "H"], description: "Go to Home", action: "/", icon: Home },
  { keys: ["G", "C"], description: "Go to Chat", action: "/chat", icon: MessageSquare },
  { keys: ["G", "T"], description: "Go to Training", action: "/training", icon: BookOpen },
  { keys: ["G", "S"], description: "Go to Settings", action: "/settings", icon: SettingsIcon },
];

const STORAGE_KEY = "cyber_sensei_keyboard_shortcuts";

export default function KeyboardShortcuts() {
  const navigate = useNavigate();
  const [enabled, setEnabled] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : true;
  });

  const [lastKey, setLastKey] = useState<string | null>(null);
  const [showPalette, setShowPalette] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(enabled));
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return;

    let lastKeyTime = 0;

    const handleKeyDown = (e: KeyboardEvent) => {
      const now = Date.now();
      const target = e.target as HTMLElement;
      
      // Ignore if typing in input
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;

      // Command palette
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setShowPalette(prev => !prev);
        return;
      }

      // Search
      if ((e.metaKey || e.ctrlKey) && e.key === "/") {
        e.preventDefault();
        navigate("/chat");
        return;
      }

      // G + key navigation
      if (lastKey === "g" && now - lastKeyTime < 500) {
        switch (e.key.toLowerCase()) {
          case "h":
            navigate("/");
            break;
          case "c":
            navigate("/chat");
            break;
          case "t":
            navigate("/training");
            break;
          case "s":
            navigate("/settings");
            break;
        }
        setLastKey(null);
        return;
      }

      if (e.key.toLowerCase() === "g") {
        setLastKey("g");
        lastKeyTime = now;
        return;
      }

      setLastKey(null);
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [enabled, lastKey, navigate]);

  return (
    <Card className="bg-card/50 border-border/50">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Keyboard className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="font-cyber text-xl text-primary">
                KEYBOARD SHORTCUTS
              </CardTitle>
              <CardDescription>
                Navigate Cyber Sensei like a pro
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Label className="text-sm text-muted-foreground">Enable</Label>
            <Switch checked={enabled} onCheckedChange={setEnabled} />
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className={cn(
          "space-y-3 transition-opacity",
          !enabled && "opacity-50 pointer-events-none"
        )}>
          {shortcuts.map((shortcut, index) => (
            <div
              key={shortcut.action}
              className={cn(
                "flex items-center justify-between p-3 rounded-lg",
                "bg-muted/30 border border-border/50",
                "hover:border-primary/30 transition-all",
                "animate-slide-up"
              )}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex items-center gap-3">
                <shortcut.icon className="h-4 w-4 text-primary" />
                <span className="text-sm">{shortcut.description}</span>
              </div>
              <div className="flex items-center gap-1">
                {shortcut.keys.map((key, i) => (
                  <span key={i} className="flex items-center">
                    <kbd className={cn(
                      "px-2 py-1 text-xs font-mono rounded",
                      "bg-muted border border-border",
                      "text-muted-foreground"
                    )}>
                      {key}
                    </kbd>
                    {i < shortcut.keys.length - 1 && (
                      <span className="mx-1 text-muted-foreground">+</span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-4 rounded-lg bg-primary/5 border border-primary/20">
          <p className="text-sm text-muted-foreground">
            <span className="text-primary font-medium">Pro tip:</span> Press{" "}
            <kbd className="px-1.5 py-0.5 text-xs font-mono rounded bg-muted border">G</kbd>{" "}
            followed by a letter to quickly navigate between pages.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
