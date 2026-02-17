import { useState } from "react";
import { CheckCircle2, XCircle, Play, RotateCcw, Lightbulb } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useUserProgress } from "@/contexts/UserProgressContext";
import { toast } from "@/hooks/use-toast";

interface CodeExerciseProps {
  lessonId: string;
  title: string;
  description: string;
  initialCode: string;
  expectedOutput?: string;
  validationFn: (code: string) => { success: boolean; message: string };
  hints: string[];
  difficulty: "easy" | "medium" | "hard";
}

export default function CodeExercise({
  lessonId,
  title,
  description,
  initialCode,
  expectedOutput,
  validationFn,
  hints,
  difficulty,
}: CodeExerciseProps) {
  const { completeExercise, progress } = useUserProgress();
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [currentHint, setCurrentHint] = useState(0);
  
  const isCompleted = progress.lessonsCompleted.find(
    l => l.lessonId === lessonId
  )?.exerciseCompleted;

  const difficultyColors = {
    easy: "text-neon-green border-neon-green/30",
    medium: "text-neon-orange border-neon-orange/30",
    hard: "text-neon-magenta border-neon-magenta/30",
  };

  const handleRun = () => {
    const result = validationFn(code);
    setOutput(result.message);
    setIsCorrect(result.success);
    
    if (result.success && !isCompleted) {
      completeExercise(lessonId);
      toast({
        title: "Exercise Completed! 🎉",
        description: "+75 XP earned!",
      });
    }
  };

  const handleReset = () => {
    setCode(initialCode);
    setOutput(null);
    setIsCorrect(null);
    setShowHint(false);
    setCurrentHint(0);
  };

  const handleShowHint = () => {
    if (!showHint) {
      setShowHint(true);
    } else if (currentHint < hints.length - 1) {
      setCurrentHint(prev => prev + 1);
    }
  };

  return (
    <Card className="bg-card/50 border-primary/30 neon-border">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="font-cyber text-xl text-primary flex items-center gap-2">
            <Play className="h-5 w-5" />
            CODING EXERCISE
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className={cn(
              "text-xs font-medium px-2 py-1 rounded border",
              difficultyColors[difficulty]
            )}>
              {difficulty.toUpperCase()}
            </span>
            {isCompleted && (
              <span className="text-xs font-medium px-2 py-1 rounded bg-neon-green/20 text-neon-green">
                COMPLETED
              </span>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h3 className="font-medium text-lg mb-2">{title}</h3>
          <p className="text-muted-foreground">{description}</p>
        </div>

        {expectedOutput && (
          <div className="p-3 bg-muted/30 rounded-lg border border-border/50">
            <p className="text-sm text-muted-foreground mb-1">Expected Output:</p>
            <code className="text-sm font-mono text-neon-green">{expectedOutput}</code>
          </div>
        )}

        <div className="space-y-2">
          <label className="text-sm font-medium">Your Code:</label>
          <Textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className={cn(
              "font-mono text-sm min-h-[200px] bg-black/50 border-border/50",
              "focus:border-primary focus:ring-primary/20"
            )}
            placeholder="Write your code here..."
          />
        </div>

        {output && (
          <div className={cn(
            "p-4 rounded-lg border",
            isCorrect 
              ? "bg-neon-green/10 border-neon-green/30" 
              : "bg-destructive/10 border-destructive/30"
          )}>
            <div className="flex items-start gap-2">
              {isCorrect ? (
                <CheckCircle2 className="h-5 w-5 text-neon-green flex-shrink-0 mt-0.5" />
              ) : (
                <XCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
              )}
              <div>
                <p className={cn(
                  "font-medium",
                  isCorrect ? "text-neon-green" : "text-destructive"
                )}>
                  {isCorrect ? "Correct!" : "Not quite right"}
                </p>
                <p className="text-sm text-foreground mt-1">{output}</p>
              </div>
            </div>
          </div>
        )}

        {showHint && (
          <div className="p-4 bg-neon-orange/10 border border-neon-orange/30 rounded-lg">
            <div className="flex items-start gap-2">
              <Lightbulb className="h-5 w-5 text-neon-orange flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-neon-orange">
                  Hint {currentHint + 1}/{hints.length}
                </p>
                <p className="text-sm text-foreground mt-1">{hints[currentHint]}</p>
              </div>
            </div>
          </div>
        )}

        <div className="flex gap-3">
          <Button onClick={handleRun} className="flex-1 neon-glow-cyan">
            <Play className="h-4 w-4 mr-2" />
            Run Code
          </Button>
          <Button variant="outline" onClick={handleReset}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button 
            variant="ghost" 
            onClick={handleShowHint}
            disabled={showHint && currentHint >= hints.length - 1}
          >
            <Lightbulb className="h-4 w-4 mr-2" />
            {showHint ? "Next Hint" : "Show Hint"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
