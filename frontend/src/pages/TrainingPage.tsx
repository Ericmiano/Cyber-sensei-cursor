import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  BookOpen, 
  Shield, 
  Lock, 
  Network, 
  Bug, 
  Code, 
  Server, 
  AlertTriangle,
  CheckCircle2,
  Clock,
  Star,
  ChevronRight,
  Sparkles,
  TrendingUp,
  Zap
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import { useUserProgress } from "@/contexts/UserProgressContext";
import { useBackendTraining } from "@/hooks/useBackendTraining";
import InteractiveCard from "@/components/effects/InteractiveCard";
import { MagneticButton } from "@/components/effects/MagneticButton";

const iconMap: Record<string, typeof Shield> = {
  Shield,
  Network,
  Lock,
  Bug,
  Code,
  AlertTriangle,
  Server,
};

const categories = [
  { id: "all", label: "All Modules" },
  { id: "fundamentals", label: "Fundamentals" },
  { id: "networking", label: "Networking" },
  { id: "offensive", label: "Offensive Security" },
  { id: "development", label: "Development" },
  { id: "operations", label: "Operations" },
  { id: "infrastructure", label: "Infrastructure" },
];

const difficultyColors = {
  beginner: "bg-neon-green/20 text-neon-green border-neon-green/30",
  intermediate: "bg-neon-orange/20 text-neon-orange border-neon-orange/30",
  advanced: "bg-neon-magenta/20 text-neon-magenta border-neon-magenta/30",
};

export default function TrainingPage() {
  const [activeCategory, setActiveCategory] = useState("all");
  const { progress } = useUserProgress();
  const { modules, loading } = useBackendTraining();

  const filteredModules = modules.filter(
    (module) => activeCategory === "all" || module.category === activeCategory
  );

  const totalProgress = modules.length > 0 
    ? Math.round(
        (modules.reduce((acc, m) => acc + (m.completedLessons || 0), 0) /
          modules.reduce((acc, m) => acc + (m.totalLessons || 0), 0)) *
          100
      )
    : 0;

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-muted rounded w-64" />
          <div className="h-32 bg-muted rounded" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="h-64 bg-muted rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6 sm:mb-8 animate-slide-up">
        <h1 className="font-cyber text-2xl sm:text-3xl font-bold mb-2 flex flex-wrap items-center gap-2 sm:gap-3">
          <span className="text-primary animate-text-glow">TRAINING</span>
          <span className="text-muted-foreground">MODULES</span>
          <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 text-secondary animate-pulse-glow" />
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground">
          Master cybersecurity through structured learning paths and hands-on challenges.
        </p>
      </div>

      {/* Progress Overview */}
      <Card className="mb-6 sm:mb-8 bg-card/50 border-border/50 neon-border interactive-card overflow-hidden">
        <div className="h-1 bg-gradient-to-r from-neon-cyan via-neon-purple to-neon-magenta animate-border-flow" />
        <CardContent className="p-4 sm:p-6">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3 sm:gap-4">
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-primary/20 flex items-center justify-center animate-float flex-shrink-0">
                <TrendingUp className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-cyber text-base sm:text-lg text-primary truncate">OVERALL PROGRESS</h3>
                <p className="text-xs sm:text-sm text-muted-foreground">
                  {modules.filter((m) => m.status === "completed").length} of {modules.length} modules completed
                </p>
              </div>
              <span className="font-cyber text-xl sm:text-2xl text-primary neon-text-cyan animate-glow-pulse flex-shrink-0">
                {totalProgress}%
              </span>
            </div>
            <Progress value={totalProgress} className="h-2 sm:h-3 bg-muted" />
          </div>
          
          {/* Quick stats */}
          <div className="grid grid-cols-3 gap-2 sm:gap-4 mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-border/30">
            {[
              { label: "Lessons", value: progress.lessonsCompleted.filter(l => l.completed).length, icon: BookOpen },
              { label: "XP", value: progress.xp, icon: Zap },
              { label: "Streak", value: `${progress.currentStreak}d`, icon: Star },
            ].map((stat, i) => (
              <div key={stat.label} className="text-center animate-slide-up" style={{ animationDelay: `${i * 100}ms` }}>
                <div className="flex justify-center mb-1 sm:mb-2">
                  <stat.icon className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                </div>
                <div className="font-cyber text-lg sm:text-xl text-primary">{stat.value}</div>
                <div className="text-[10px] sm:text-xs text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Category Tabs */}
      <Tabs value={activeCategory} onValueChange={setActiveCategory} className="mb-4 sm:mb-6">
        <TabsList className="bg-muted/50 flex flex-wrap h-auto gap-1 p-1 w-full justify-start overflow-x-auto">
          {categories.map((category) => (
            <TabsTrigger
              key={category.id}
              value={category.id}
              className={cn(
                "data-[state=active]:bg-primary data-[state=active]:text-primary-foreground",
                "transition-all duration-200 text-xs sm:text-sm whitespace-nowrap"
              )}
            >
              {category.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Modules Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {filteredModules.map((module, index) => {
          const Icon = iconMap[module.icon] || Shield;
          const completedLessons = module.completedLessons || 0;
          const totalLessons = module.totalLessons || 1;
          const status = completedLessons === 0 ? "locked" : completedLessons === totalLessons ? "completed" : "in-progress";
          
          return (
            <InteractiveCard
              key={module.id}
              className={cn(
                "animate-slide-up"
              )}
              style={{ animationDelay: `${index * 100}ms` } as any}
              enableTilt={true}
              enableMagnetic={true}
              enableGlow={true}
              enableBrackets={true}
            >
              <Card
                className={cn(
                  "group relative overflow-hidden transition-all duration-300 h-full",
                  "bg-card/50 border-border/50",
                  status === "locked" && "opacity-60 grayscale"
                )}
              >
              {status === "completed" && (
                <div className="absolute top-4 right-4 z-10">
                  <CheckCircle2 className="h-6 w-6 text-neon-green" />
                </div>
              )}

              <CardHeader className="pb-4">
                <div className="flex items-start gap-4">
                  <div
                    className={cn(
                      "w-12 h-12 rounded-lg flex items-center justify-center",
                      "bg-primary/10 group-hover:bg-primary/20",
                      "transition-colors duration-300"
                    )}
                  >
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="font-cyber text-lg group-hover:text-primary transition-colors">
                      {module.title}
                    </CardTitle>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge
                        variant="outline"
                        className={cn("text-xs", difficultyColors[module.difficulty as keyof typeof difficultyColors])}
                      >
                        {module.difficulty}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        <Clock className="h-3 w-3 mr-1" />
                        {module.estimatedHours}h
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <CardDescription className="mb-4">{module.description}</CardDescription>

                {/* Progress */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="text-primary font-medium">
                      {completedLessons}/{totalLessons} lessons
                    </span>
                  </div>
                  <Progress
                    value={(completedLessons / totalLessons) * 100}
                    className="h-2 bg-muted"
                  />
                </div>

                {/* Action Button */}
                {status === "locked" ? (
                  <Button
                    className="w-full bg-muted text-muted-foreground cursor-not-allowed"
                    disabled
                  >
                    <Lock className="h-4 w-4 mr-2" />
                    Locked
                  </Button>
                ) : (
                  <Link to={`/training/${module.id}`} className="block">
                    <MagneticButton
                      className={cn(
                        "w-full font-medium",
                        status === "completed"
                          ? "bg-neon-green/20 text-neon-green hover:bg-neon-green/30"
                          : "neon-glow-cyan"
                      )}
                      strength={0.2}
                    >
                      {status === "completed" ? (
                        <>
                          <Star className="h-4 w-4 mr-2" />
                          Review Module
                        </>
                      ) : (
                        <>
                          Continue Learning
                          <ChevronRight className="h-4 w-4 ml-2" />
                        </>
                      )}
                    </MagneticButton>
                  </Link>
                )}
              </CardContent>
            </Card>
          </InteractiveCard>
          );
        })}
      </div>
    </div>
  );
}
