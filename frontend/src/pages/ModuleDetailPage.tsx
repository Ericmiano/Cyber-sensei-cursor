import { useParams, useNavigate, Link } from "react-router-dom";
import { 
  ArrowLeft, 
  Shield, 
  Network, 
  Lock, 
  Bug, 
  Code, 
  AlertTriangle, 
  Server,
  Clock,
  CheckCircle2,
  PlayCircle,
  ChevronRight,
  BookOpen
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useBackendTraining } from "@/hooks/useBackendTraining";

const iconMap: Record<string, typeof Shield> = {
  Shield,
  Network,
  Lock,
  Bug,
  Code,
  AlertTriangle,
  Server,
};

const difficultyColors = {
  beginner: "bg-neon-green/20 text-neon-green border-neon-green/30",
  intermediate: "bg-neon-orange/20 text-neon-orange border-neon-orange/30",
  advanced: "bg-neon-magenta/20 text-neon-magenta border-neon-magenta/30",
};

export default function ModuleDetailPage() {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();
  const { modules, lessons, loading } = useBackendTraining();
  
  const module = modules.find(m => m.id === moduleId);
  const moduleLessons = lessons.filter(l => l.moduleId === moduleId);
  
  if (loading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-muted rounded w-32" />
          <div className="h-48 bg-muted rounded" />
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-20 bg-muted rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }
  
  if (!module) {
    return (
      <div className="p-6 max-w-4xl mx-auto text-center">
        <h1 className="font-cyber text-3xl text-primary mb-4">MODULE NOT FOUND</h1>
        <p className="text-muted-foreground mb-6">The requested module does not exist.</p>
        <Button onClick={() => navigate("/training")} variant="outline">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Training
        </Button>
      </div>
    );
  }

  const completedLessons = moduleLessons.filter(l => l.completed).length;
  const progress = moduleLessons.length > 0 ? (completedLessons / moduleLessons.length) * 100 : 0;
  const nextLesson = moduleLessons.find(l => !l.completed);
  const Icon = iconMap[module.icon] || Shield;
  const status = completedLessons === 0 ? "locked" : completedLessons === moduleLessons.length ? "completed" : "in-progress";

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Back Button */}
      <Button
        variant="ghost"
        onClick={() => navigate("/training")}
        className="mb-6 hover:bg-primary/10"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Training
      </Button>

      {/* Module Header */}
      <Card className="mb-8 bg-card/50 border-border/50 neon-border overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5" />
        <CardHeader className="relative">
          <div className="flex items-start gap-4">
            <div className={cn(
              "w-16 h-16 rounded-xl flex items-center justify-center",
              "bg-primary/10"
            )}>
              <Icon className="h-8 w-8 text-primary" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline" className={cn("text-xs", difficultyColors[module.difficulty as keyof typeof difficultyColors])}>
                  {module.difficulty}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  <Clock className="h-3 w-3 mr-1" />
                  {module.estimatedHours}h
                </Badge>
                {status === "completed" && (
                  <Badge className="bg-neon-green/20 text-neon-green text-xs">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Completed
                  </Badge>
                )}
              </div>
              <CardTitle className="font-cyber text-2xl text-primary mb-2">
                {module.title}
              </CardTitle>
              <CardDescription className="text-base">
                {module.description}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="relative">
          {/* Progress */}
          <div className="mb-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-muted-foreground">Progress</span>
              <span className="text-primary font-medium">
                {completedLessons}/{moduleLessons.length} lessons completed
              </span>
            </div>
            <Progress value={progress} className="h-3 bg-muted" />
          </div>

          {/* Continue Button */}
          {nextLesson && status !== "locked" && (
            <Button
              asChild
              className="w-full neon-glow-cyan font-medium"
            >
              <Link to={`/training/${module.id}/lesson/${nextLesson.id}`}>
                <PlayCircle className="h-4 w-4 mr-2" />
                Continue: {nextLesson.title}
              </Link>
            </Button>
          )}
          {status === "completed" && moduleLessons.length > 0 && (
            <Button
              asChild
              className="w-full bg-neon-green/20 text-neon-green hover:bg-neon-green/30"
            >
              <Link to={`/training/${module.id}/lesson/${moduleLessons[0].id}`}>
                <BookOpen className="h-4 w-4 mr-2" />
                Review from Beginning
              </Link>
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Lessons List */}
      <div>
        <h2 className="font-cyber text-xl text-primary mb-4">LESSONS</h2>
        <div className="space-y-3">
          {moduleLessons.map((lesson, index) => (
            <Card
              key={lesson.id}
              className={cn(
                "bg-card/50 border-border/50 transition-all duration-200",
                "hover:border-primary/50",
                status === "locked" && "opacity-50"
              )}
            >
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  <div className={cn(
                    "w-10 h-10 rounded-lg flex items-center justify-center font-cyber text-sm",
                    lesson.completed 
                      ? "bg-neon-green/20 text-neon-green" 
                      : "bg-muted text-muted-foreground"
                  )}>
                    {lesson.completed ? (
                      <CheckCircle2 className="h-5 w-5" />
                    ) : (
                      <span>{String(index + 1).padStart(2, '0')}</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className={cn(
                      "font-medium",
                      lesson.completed && "text-muted-foreground"
                    )}>
                      {lesson.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      <Clock className="h-3 w-3 inline mr-1" />
                      {lesson.estimatedMinutes} min
                    </p>
                  </div>
                  {status !== "locked" && (
                    <Button
                      asChild
                      variant={lesson.completed ? "ghost" : "default"}
                      size="sm"
                      className={cn(
                        lesson.completed 
                          ? "hover:bg-primary/10" 
                          : "neon-glow-cyan"
                      )}
                    >
                      <Link to={`/training/${module.id}/lesson/${lesson.id}`}>
                        {lesson.completed ? "Review" : "Start"}
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
