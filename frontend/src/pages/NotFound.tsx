import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Shield, Zap, ArrowLeft, Terminal, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 gradient-cyber opacity-40" />
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-destructive/5 rounded-full blur-3xl" />

      <div className="relative text-center max-w-lg mx-auto animate-slide-up">
        {/* Glitch 404 */}
        <div className="relative mb-6">
          <div className="flex items-center justify-center gap-2 mb-4">
            <AlertTriangle className="h-8 w-8 text-destructive animate-pulse-glow" />
          </div>
          <h1 className="font-cyber text-8xl sm:text-9xl font-bold text-primary neon-text-cyan tracking-widest">
            404
          </h1>
          <div className="electric-line w-3/4 mx-auto my-4" />
        </div>

        {/* Terminal-style error */}
        <div className="bg-card/80 border border-border/50 rounded-xl p-5 mb-8 text-left font-mono text-sm neon-border">
          <div className="flex items-center gap-2 mb-3 text-muted-foreground">
            <Terminal className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">System Log</span>
          </div>
          <p className="text-destructive mb-1">
            <span className="text-muted-foreground">$ </span>
            access --route "{location.pathname}"
          </p>
          <p className="text-muted-foreground">
            ERROR: Route not found in system registry.
          </p>
          <p className="text-muted-foreground">
            STATUS: <span className="text-neon-orange">UNAUTHORIZED_PATH</span>
          </p>
          <p className="text-primary mt-2 animate-electric-pulse">
            Redirecting to secure zone...
          </p>
        </div>

        {/* Description */}
        <p className="text-muted-foreground mb-6">
          The path you're looking for doesn't exist in the Cyber Sensei network.
        </p>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button asChild className="neon-glow-cyan font-cyber">
            <Link to="/">
              <Shield className="h-4 w-4 mr-2" />
              Return to Base
            </Link>
          </Button>
          <Button asChild variant="outline" className="hover:neon-border">
            <Link to="/chat">
              <Zap className="h-4 w-4 mr-2" />
              Ask Sensei
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
