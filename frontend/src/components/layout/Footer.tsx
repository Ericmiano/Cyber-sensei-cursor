import { Shield, Zap } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-border/30 bg-card/30 backdrop-blur-sm mt-auto relative z-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            <Zap className="h-3 w-3 text-secondary -ml-1.5" />
            <span className="font-cyber text-sm text-primary font-bold tracking-wider">CYBER SENSEI</span>
          </div>

          {/* Electric line */}
          <div className="hidden sm:block flex-1 mx-8">
            <div className="electric-line" />
          </div>

          {/* Info */}
          <div className="flex items-center gap-4 text-xs text-muted-foreground font-mono">
            <span>AI-POWERED CYBERSECURITY TRAINING</span>
            <span className="hidden sm:inline">•</span>
            <span className="hidden sm:inline animate-electric-pulse text-primary/60">
              SYS.ONLINE
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
