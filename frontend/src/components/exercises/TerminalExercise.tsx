import { useState, useRef, useEffect } from "react";
import { Terminal, CheckCircle2, XCircle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useUserProgress } from "@/contexts/UserProgressContext";
import { toast } from "@/hooks/use-toast";

interface TerminalLine {
  type: "prompt" | "output" | "error" | "success";
  content: string;
}

interface TerminalExerciseProps {
  lessonId: string;
  title: string;
  description: string;
  objectives: string[];
  commands: {
    command: string;
    output: string;
    isRequired?: boolean;
  }[];
  hints?: string[];
}

export default function TerminalExercise({
  lessonId,
  title,
  description,
  objectives,
  commands,
  hints = [],
}: TerminalExerciseProps) {
  const { completeExercise, progress } = useUserProgress();
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<TerminalLine[]>([
    { type: "output", content: "Welcome to the Cyber Terminal. Type 'help' for available commands." },
  ]);
  const [completedCommands, setCompletedCommands] = useState<Set<string>>(new Set());
  const terminalRef = useRef<HTMLDivElement>(null);
  
  const isCompleted = progress.lessonsCompleted.find(
    l => l.lessonId === lessonId
  )?.exerciseCompleted;
  
  const requiredCommands = commands.filter(c => c.isRequired !== false);
  const allRequiredCompleted = requiredCommands.every(c => completedCommands.has(c.command));

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  useEffect(() => {
    if (allRequiredCompleted && !isCompleted) {
      completeExercise(lessonId);
      toast({
        title: "Exercise Completed! 🎉",
        description: "+75 XP earned!",
      });
      setHistory(prev => [...prev, {
        type: "success",
        content: "🎉 Congratulations! You've completed all required commands!",
      }]);
    }
  }, [allRequiredCompleted, isCompleted]);

  const handleCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const cmd = input.trim().toLowerCase();
    setHistory(prev => [...prev, { type: "prompt", content: `$ ${input}` }]);
    setInput("");

    // Handle built-in commands
    if (cmd === "help") {
      setHistory(prev => [...prev, {
        type: "output",
        content: `Available commands:\n${commands.map(c => `  ${c.command}`).join("\n")}\n\nType 'objectives' to see your tasks.`,
      }]);
      return;
    }

    if (cmd === "objectives") {
      const objectivesList = objectives.map((obj, i) => {
        const isComplete = requiredCommands[i] ? completedCommands.has(requiredCommands[i].command) : false;
        return `  ${isComplete ? "✓" : "○"} ${obj}`;
      }).join("\n");
      setHistory(prev => [...prev, {
        type: "output",
        content: `Objectives:\n${objectivesList}`,
      }]);
      return;
    }

    if (cmd === "hint" && hints.length > 0) {
      const randomHint = hints[Math.floor(Math.random() * hints.length)];
      setHistory(prev => [...prev, {
        type: "output",
        content: `💡 Hint: ${randomHint}`,
      }]);
      return;
    }

    if (cmd === "clear") {
      setHistory([{ type: "output", content: "Terminal cleared." }]);
      return;
    }

    // Check against exercise commands
    const matchedCommand = commands.find(c => c.command.toLowerCase() === cmd);
    if (matchedCommand) {
      setCompletedCommands(prev => new Set([...prev, matchedCommand.command]));
      setHistory(prev => [...prev, { type: "output", content: matchedCommand.output }]);
    } else {
      setHistory(prev => [...prev, { 
        type: "error", 
        content: `Command not found: ${cmd}. Type 'help' for available commands.` 
      }]);
    }
  };

  const handleReset = () => {
    setHistory([{ type: "output", content: "Terminal reset. Type 'help' for available commands." }]);
    setCompletedCommands(new Set());
    setInput("");
  };

  return (
    <Card className="bg-black border-neon-green/30 overflow-hidden">
      <CardHeader className="py-3 px-4 bg-black border-b border-neon-green/20">
        <div className="flex items-center justify-between">
          <CardTitle className="font-cyber text-lg text-neon-green flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            {title}
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-xs text-neon-green/70">
              {completedCommands.size}/{requiredCommands.length} completed
            </span>
            {isCompleted && (
              <CheckCircle2 className="h-4 w-4 text-neon-green" />
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="p-4 border-b border-neon-green/20">
          <p className="text-sm text-muted-foreground mb-3">{description}</p>
          <div className="space-y-1">
            {objectives.map((obj, i) => {
              const isComplete = requiredCommands[i] ? completedCommands.has(requiredCommands[i].command) : false;
              return (
                <div key={i} className="flex items-center gap-2 text-sm">
                  {isComplete ? (
                    <CheckCircle2 className="h-4 w-4 text-neon-green" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border border-muted-foreground" />
                  )}
                  <span className={cn(isComplete && "text-neon-green line-through")}>
                    {obj}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div 
          ref={terminalRef}
          className="h-[300px] overflow-y-auto p-4 font-mono text-sm"
        >
          {history.map((line, i) => (
            <div 
              key={i} 
              className={cn(
                "mb-1 whitespace-pre-wrap",
                line.type === "prompt" && "text-primary",
                line.type === "output" && "text-neon-green/80",
                line.type === "error" && "text-destructive",
                line.type === "success" && "text-neon-green font-bold"
              )}
            >
              {line.content}
            </div>
          ))}
        </div>

        <form onSubmit={handleCommand} className="border-t border-neon-green/20 p-3 flex gap-2">
          <span className="text-neon-green font-mono">$</span>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-transparent border-none text-neon-green font-mono focus-visible:ring-0 focus-visible:ring-offset-0 px-0"
            placeholder="Enter command..."
            autoFocus
          />
          <Button 
            type="button" 
            variant="ghost" 
            size="sm"
            onClick={handleReset}
            className="text-neon-green/50 hover:text-neon-green"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
