import { HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useTutorial } from "@/contexts/TutorialContext";

export default function TutorialTrigger() {
  const { startTutorial, hasCompletedTutorial, resetTutorial } = useTutorial();

  const handleClick = () => {
    if (hasCompletedTutorial) {
      resetTutorial();
    }
    startTutorial();
  };

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          onClick={handleClick}
          className="h-9 w-9 text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors"
        >
          <HelpCircle className="h-5 w-5" />
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <p>Start Tutorial</p>
      </TooltipContent>
    </Tooltip>
  );
}
