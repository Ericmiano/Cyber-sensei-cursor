import { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Home,
  MessageSquare,
  BookOpen,
  LayoutDashboard,
  BarChart3,
  Settings,
  Search,
  Moon,
  Sun,
  LogIn,
  Zap,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useTheme } from "@/contexts/ThemeContext";

interface CommandItem {
  id: string;
  label: string;
  icon: typeof Home;
  action: () => void;
  category: string;
  keywords?: string[];
}

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();
  const { theme, toggleMode } = useTheme();

  const commands: CommandItem[] = useMemo(() => [
    { id: "home", label: "Go to Home", icon: Home, action: () => navigate("/"), category: "Navigation", keywords: ["index", "landing"] },
    { id: "chat", label: "Open AI Chat", icon: MessageSquare, action: () => navigate("/chat"), category: "Navigation", keywords: ["sensei", "ask", "ai"] },
    { id: "training", label: "Training Modules", icon: BookOpen, action: () => navigate("/training"), category: "Navigation", keywords: ["learn", "course", "module"] },
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, action: () => navigate("/dashboard"), category: "Navigation", keywords: ["progress", "stats"] },
    { id: "analytics", label: "Analytics", icon: BarChart3, action: () => navigate("/analytics"), category: "Navigation", keywords: ["charts", "reports"] },
    { id: "settings", label: "Settings", icon: Settings, action: () => navigate("/settings"), category: "Navigation", keywords: ["config", "profile"] },
    { id: "auth", label: "Login / Sign Up", icon: LogIn, action: () => navigate("/auth"), category: "Actions", keywords: ["account", "register"] },
    { id: "theme", label: theme.mode === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode", icon: theme.mode === "dark" ? Sun : Moon, action: () => toggleMode(), category: "Actions", keywords: ["dark", "light", "theme"] },
  ], [navigate, theme.mode, toggleMode]);

  const filtered = useMemo(() => {
    if (!query.trim()) return commands;
    const q = query.toLowerCase();
    return commands.filter(c =>
      c.label.toLowerCase().includes(q) ||
      c.category.toLowerCase().includes(q) ||
      c.keywords?.some(k => k.includes(q))
    );
  }, [query, commands]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  const runCommand = useCallback((cmd: CommandItem) => {
    setOpen(false);
    setQuery("");
    cmd.action();
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen(prev => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex(i => (i + 1) % filtered.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex(i => (i - 1 + filtered.length) % filtered.length);
    } else if (e.key === "Enter" && filtered[selectedIndex]) {
      runCommand(filtered[selectedIndex]);
    }
  };

  const grouped = useMemo(() => {
    const map: Record<string, CommandItem[]> = {};
    filtered.forEach(c => {
      if (!map[c.category]) map[c.category] = [];
      map[c.category].push(c);
    });
    return map;
  }, [filtered]);

  let flatIndex = 0;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="p-0 gap-0 max-w-lg overflow-hidden bg-card/95 backdrop-blur-xl border-border/50 neon-border shadow-2xl [&>button]:hidden">
        {/* Search */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-border/30">
          <Search className="h-5 w-5 text-muted-foreground flex-shrink-0" />
          <Input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command or search..."
            className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-base placeholder:text-muted-foreground/50 h-auto p-0"
            autoFocus
          />
          <kbd className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-muted border border-border text-muted-foreground flex-shrink-0">
            ESC
          </kbd>
        </div>

        {/* Results */}
        <div className="max-h-[320px] overflow-y-auto p-2">
          {Object.entries(grouped).map(([category, items]) => (
            <div key={category}>
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground px-3 py-2 font-medium">
                {category}
              </p>
              {items.map(item => {
                const idx = flatIndex++;
                return (
                  <button
                    key={item.id}
                    onClick={() => runCommand(item)}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all",
                      idx === selectedIndex
                        ? "bg-primary/15 text-primary neon-border"
                        : "text-foreground hover:bg-muted/50"
                    )}
                  >
                    <item.icon className="h-4 w-4 flex-shrink-0" />
                    <span>{item.label}</span>
                    {idx === selectedIndex && (
                      <Zap className="h-3 w-3 ml-auto text-primary animate-electric-pulse" />
                    )}
                  </button>
                );
              })}
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Search className="h-8 w-8 mx-auto mb-2 opacity-40" />
              <p className="text-sm">No commands found</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center gap-4 px-4 py-2.5 border-t border-border/30 text-[10px] text-muted-foreground">
          <span className="flex items-center gap-1">
            <kbd className="px-1 py-0.5 rounded bg-muted border border-border font-mono">↑↓</kbd>
            Navigate
          </span>
          <span className="flex items-center gap-1">
            <kbd className="px-1 py-0.5 rounded bg-muted border border-border font-mono">↵</kbd>
            Select
          </span>
          <span className="flex items-center gap-1">
            <kbd className="px-1 py-0.5 rounded bg-muted border border-border font-mono">⌘K</kbd>
            Toggle
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
