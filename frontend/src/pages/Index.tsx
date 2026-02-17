import { Shield, Zap, MessageSquare, BookOpen, BarChart3, ArrowRight, PlayCircle, TrendingUp, Sparkles, LogIn } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { useUserProgress } from "@/contexts/UserProgressContext";
import { useAuth } from "@/contexts/AuthContext";
import GlitchText from "@/components/effects/GlitchText";
import WordReveal from "@/components/effects/WordReveal";
import InteractiveCard from "@/components/effects/InteractiveCard";

const ALL_LESSONS = [
  { moduleId: "1", lessonId: "1-1", title: "Introduction to Cybersecurity" },
  { moduleId: "1", lessonId: "1-2", title: "The CIA Triad" },
  { moduleId: "1", lessonId: "1-3", title: "Types of Cyber Threats" },
  { moduleId: "1", lessonId: "1-4", title: "Authentication & Access Control" },
  { moduleId: "2", lessonId: "2-1", title: "Network Fundamentals" },
  { moduleId: "2", lessonId: "2-2", title: "Firewalls & Packet Filtering" },
  { moduleId: "4", lessonId: "4-1", title: "Introduction to Ethical Hacking" },
  { moduleId: "4", lessonId: "4-2", title: "Vulnerability Scanning" },
];

const MODULE_NAMES: Record<string, string> = {
  "1": "Cybersecurity Fundamentals",
  "2": "Network Security",
  "3": "Cryptography Essentials",
  "4": "Ethical Hacking",
  "5": "Secure Coding Practices",
  "6": "Incident Response",
  "7": "Cloud Security",
};

const features = [
  {
    icon: MessageSquare,
    title: "AI Chat Interface",
    description: "Interact with your cybersecurity sensei for personalized guidance and answers.",
    link: "/chat",
  },
  {
    icon: BookOpen,
    title: "Training Modules",
    description: "Master cybersecurity concepts through interactive courses and challenges.",
    link: "/training",
  },
  {
    icon: BarChart3,
    title: "Progress Analytics",
    description: "Track your learning journey with detailed insights and statistics.",
    link: "/analytics",
  },
];

const Index = () => {
  const { progress } = useUserProgress();
  const { isAuthenticated } = useAuth();
  
  const getNextLesson = () => {
    const completedIds = new Set(
      progress.lessonsCompleted.filter(l => l.completed).map(l => l.lessonId)
    );
    const nextLesson = ALL_LESSONS.find(lesson => !completedIds.has(lesson.lessonId));
    if (nextLesson) {
      return {
        moduleId: nextLesson.moduleId,
        moduleName: MODULE_NAMES[nextLesson.moduleId] || "Training Module",
        lessonId: nextLesson.lessonId,
        lessonTitle: nextLesson.title,
      };
    }
    return { moduleId: "1", moduleName: "Cybersecurity Fundamentals", lessonId: "1-1", lessonTitle: "Introduction to Cybersecurity" };
  };

  const nextLesson = getNextLesson();
  const completedLessons = progress.lessonsCompleted.filter(l => l.completed).length;
  const totalLessons = ALL_LESSONS.length;

  return (
    <div className="min-h-full">
      {/* HUD Elements */}
      <div className="fixed top-20 left-72 hud-text z-10 hidden lg:block" aria-hidden="true">
        SYS.STATUS: ONLINE{"\n"}
        SEC.LEVEL: MAX{"\n"}
        USER: DETECTED
      </div>
      <div className="fixed bottom-20 right-8 hud-text z-10 hidden lg:block text-right" aria-hidden="true">
        V.2.0.45{"\n"}
        CYBER-SENSEI CORE
      </div>

      {/* Hero Section */}
      <section className="relative py-16 sm:py-24 px-4 sm:px-6 overflow-hidden">
        {/* Aurora background */}
        <div className="absolute inset-0 gradient-cyber opacity-60" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] sm:w-[700px] h-[500px] sm:h-[700px] rounded-full" 
          style={{ background: 'radial-gradient(circle, hsl(var(--amber) / 0.1) 0%, transparent 70%)', filter: 'blur(80px)' }} />
        
        {/* Corner brackets */}
        <div className="absolute top-8 left-8 w-24 h-24 border-t-2 border-l-2 border-primary/30 rounded-tl-3xl hidden lg:block" />
        <div className="absolute bottom-8 right-8 w-24 h-24 border-b-2 border-r-2 border-primary/30 rounded-br-3xl hidden lg:block" />

        <div className="relative max-w-4xl mx-auto text-center">
          {/* Logo with amber glow */}
          <div className="flex justify-center mb-8 sm:mb-10">
            <div className="relative animate-float">
              <div className="absolute inset-0 bg-primary/25 blur-3xl rounded-full scale-150" />
              <Shield className="relative h-16 w-16 sm:h-24 sm:w-24 text-primary animate-pulse-glow" />
              <Zap className="absolute -bottom-1 sm:-bottom-2 -right-1 sm:-right-2 h-7 w-7 sm:h-10 sm:w-10 text-secondary animate-neon-flicker" />
            </div>
          </div>

          {/* Title with glitch decryption effect */}
          <h1 className="font-cyber text-4xl sm:text-6xl md:text-8xl font-bold mb-3 sm:mb-4 tracking-wider">
            <GlitchText 
              text="CYBER" 
              className="text-primary neon-text-cyan"
              intensity={0.5}
            />
            <GlitchText 
              text=" SENSEI" 
              className="text-secondary neon-text-magenta ml-2 sm:ml-4"
              intensity={0.5}
            />
          </h1>
          
          {/* Word-by-word reveal description */}
          <p className="text-base sm:text-xl md:text-2xl text-muted-foreground mb-8 sm:mb-10 max-w-2xl mx-auto px-2 font-mono">
            <WordReveal 
              text="Your AI-powered cybersecurity mentor. Learn, train, and master the art of digital defense."
              baseDelay={1.2}
              stagger={0.04}
            />
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center px-4">
            {!isAuthenticated ? (
              <Button
                asChild
                size="lg"
                className={cn(
                  "font-cyber text-base sm:text-lg px-6 sm:px-8 py-5 sm:py-6 font-bold tracking-wider",
                  "bg-primary hover:bg-primary/90 text-primary-foreground",
                  "neon-glow-cyan transition-all duration-300",
                  "hover:scale-105"
                )}
              >
                <Link to="/auth">
                  <LogIn className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
                  INITIALIZE SYSTEM //
                </Link>
              </Button>
            ) : (
              <Button
                asChild
                size="lg"
                className={cn(
                  "font-cyber text-base sm:text-lg px-6 sm:px-8 py-5 sm:py-6 font-bold tracking-wider",
                  "bg-primary hover:bg-primary/90 text-primary-foreground",
                  "neon-glow-cyan transition-all duration-300",
                  "hover:scale-105"
                )}
              >
                <Link to="/chat">
                  <MessageSquare className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
                  START TRAINING //
                </Link>
              </Button>
            )}
            <Button
              asChild
              variant="outline"
              size="lg"
              className={cn(
                "font-cyber text-base sm:text-lg px-6 sm:px-8 py-5 sm:py-6 font-bold tracking-wider",
                "border-secondary/50 hover:border-secondary",
                "hover:bg-secondary/10 hover:text-secondary",
                "transition-all duration-300"
              )}
            >
              <Link to="/training">
                <BookOpen className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
                BROWSE MODULES_
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Continue Learning */}
      {completedLessons > 0 && (
        <section className="py-8 px-6">
          <div className="max-w-4xl mx-auto">
            <InteractiveCard className="rounded-2xl">
              <Card className="bg-card/50 border-primary/30 neon-border overflow-hidden">
                <div className="h-1 animate-border-flow" />
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-xl bg-primary/20 flex items-center justify-center animate-glow-pulse corner-brackets">
                        <PlayCircle className="h-7 w-7 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1 font-mono uppercase tracking-wider">Continue where you left off</p>
                        <h3 className="font-cyber text-lg text-primary font-bold">{nextLesson.moduleName}</h3>
                        <p className="text-sm text-muted-foreground font-mono">{nextLesson.lessonTitle}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Progress value={(completedLessons / totalLessons) * 100} className="w-32 h-2" />
                          <span className="text-xs text-muted-foreground font-mono">{completedLessons}/{totalLessons}</span>
                        </div>
                      </div>
                    </div>
                    <Button asChild className="neon-glow-cyan font-cyber font-bold tracking-wider">
                      <Link to={`/training/${nextLesson.moduleId}/lesson/${nextLesson.lessonId}`}>
                        <PlayCircle className="h-4 w-4 mr-2" />
                        CONTINUE
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </InteractiveCard>
          </div>
        </section>
      )}

      {/* Quick Stats */}
      {progress.xp > 0 && (
        <section className="py-4 px-6">
          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: "TOTAL XP", value: progress.xp.toLocaleString(), icon: Zap },
                { label: "STREAK", value: `${progress.currentStreak}d`, icon: TrendingUp },
                { label: "LEVEL", value: progress.level.toString(), icon: Sparkles },
              ].map((stat, index) => (
                <InteractiveCard key={stat.label} className="rounded-xl" enableTilt enableBrackets={false}>
                  <Card
                    className="bg-card/30 border-border/30 p-4 text-center animate-slide-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <stat.icon className="h-5 w-5 text-primary mx-auto mb-2" />
                    <div className="font-cyber text-xl text-primary font-bold neon-text-cyan">{stat.value}</div>
                    <div className="text-[10px] text-muted-foreground font-mono tracking-widest">{stat.label}</div>
                  </Card>
                </InteractiveCard>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Features Section */}
      <section className="py-12 sm:py-16 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8 sm:mb-12 relative">
            <h2 className="font-cyber text-2xl sm:text-3xl font-bold tracking-wider">
              <span className="text-primary">SYSTEM</span>
              <span className="text-muted-foreground ml-2">CAPABILITIES</span>
            </h2>
            {/* Animated sweep bar */}
            <div className="h-1 max-w-xs mx-auto mt-3 overflow-hidden rounded-full">
              <div className="h-full animate-shimmer" style={{ background: 'linear-gradient(90deg, transparent, hsl(var(--amber) / 0.3), transparent)', backgroundSize: '200% 100%' }} />
            </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
            {features.map((feature, index) => (
              <InteractiveCard
                key={feature.title}
                className="rounded-2xl animate-slide-up"
                enableTilt
                enableMagnetic
                enableGlow
                enableBrackets
              >
                <Card
                  className={cn(
                    "overflow-hidden h-full",
                    "bg-card/50 backdrop-blur-sm",
                    "border-border/50 hover:border-primary/50",
                    "transition-all duration-300"
                  )}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  
                  <CardHeader className="p-4 sm:p-6">
                    <div className={cn(
                      "w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center mb-3 sm:mb-4",
                      "bg-primary/10 group-hover:bg-primary/20",
                      "transition-colors duration-300"
                    )}>
                      <feature.icon className="h-5 w-5 sm:h-6 sm:w-6 text-primary group-hover:scale-110 transition-transform animate-breathe" />
                    </div>
                    <CardTitle className="font-cyber text-lg sm:text-xl group-hover:text-primary transition-colors font-bold tracking-wider">
                      {feature.title}
                    </CardTitle>
                    <CardDescription className="text-sm text-muted-foreground font-mono">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="p-4 sm:p-6 pt-0">
                    <Link
                      to={feature.link}
                      className={cn(
                        "inline-flex items-center text-sm font-bold font-cyber tracking-wider",
                        "text-primary hover:text-primary/80",
                        "group/link transition-colors"
                      )}
                    >
                      EXPLORE
                      <ArrowRight className="ml-1 h-4 w-4 group-hover/link:translate-x-1 transition-transform" />
                    </Link>
                  </CardContent>
                </Card>
              </InteractiveCard>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 sm:py-16 px-4 sm:px-6 border-t border-border/30">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 text-center">
            {[
              { value: "50+", label: "Training Modules" },
              { value: "1000+", label: "Questions" },
              { value: "24/7", label: "AI Assistance" },
              { value: "∞", label: "Learning Paths" },
            ].map((stat, index) => (
              <div
                key={stat.label}
                className="animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="font-cyber text-2xl sm:text-3xl md:text-4xl font-bold text-primary neon-text-cyan mb-1 sm:mb-2">
                  {stat.value}
                </div>
                <div className="text-[10px] sm:text-sm text-muted-foreground uppercase tracking-widest font-mono">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
