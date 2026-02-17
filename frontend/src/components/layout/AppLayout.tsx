import { ReactNode } from "react";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import Footer from "./Footer";
import { cn } from "@/lib/utils";
import TutorialOverlay from "@/components/tutorial/TutorialOverlay";
import TutorialTrigger from "@/components/tutorial/TutorialTrigger";
import FloatingParticles from "@/components/effects/FloatingParticles";
import AuroraBackground from "@/components/effects/AuroraBackground";
import HUDOverlay from "@/components/effects/HUDOverlay";
import CursorEffects from "@/components/effects/CursorEffects";
import ScanlineOverlay from "@/components/effects/ScanlineOverlay";
import { ParallaxGrid } from "@/components/effects/ParallaxGrid";

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background cyber-grid relative">
        <AuroraBackground />
        <ParallaxGrid />
        <FloatingParticles count={25} />
        <HUDOverlay />
        <CursorEffects />
        <ScanlineOverlay />
        <AppSidebar />
        <div className="flex-1 flex flex-col min-h-screen min-w-0 relative z-20">
          <header className="h-14 flex items-center px-3 sm:px-4 border-b border-border/30 bg-background/50 backdrop-blur-md sticky top-0 z-40">
            <SidebarTrigger className="hover:bg-primary/10 hover:text-primary transition-colors" />
            <div className="flex items-center gap-2 ml-3">
              <img src="/logo.png" alt="Cyber Sensei" className="h-8 w-8 object-contain" />
              <span className="font-cyber text-lg hidden sm:inline">
                <span className="text-primary neon-text-cyan">CYBER</span>
                <span className="text-secondary neon-text-magenta ml-1">SENSEI</span>
              </span>
            </div>
            <div className="ml-auto flex items-center gap-2 sm:gap-4">
              <kbd className="hidden sm:inline-flex items-center gap-1 text-[10px] font-mono px-2 py-1 rounded bg-muted border border-border text-muted-foreground cursor-pointer hover:border-primary/30 transition-colors"
                onClick={() => window.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true }))}>
                ⌘K
              </kbd>
              <TutorialTrigger />
            </div>
          </header>
          <main className="flex-1 overflow-auto">
            <div className={cn("animate-fade-in", "min-h-full")}>
              {children}
            </div>
          </main>
          <Footer />
        </div>
        <TutorialOverlay />
      </div>
    </SidebarProvider>
  );
}
