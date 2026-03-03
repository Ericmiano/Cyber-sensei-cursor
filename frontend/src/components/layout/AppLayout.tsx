import { ReactNode } from "react";
import { cn } from "@/lib/utils";
import TutorialOverlay from "@/components/tutorial/TutorialOverlay";
import TutorialTrigger from "@/components/tutorial/TutorialTrigger";
import Hyperspeed from "@/components/effects/Hyperspeed";
import CursorEffects from "@/components/effects/CursorEffects";
import ScanlineOverlay from "@/components/effects/ScanlineOverlay";
import AppDock from "@/components/navigation/AppDock";

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col w-full bg-background relative overflow-hidden">
      {/* Background Effects Layer - Fixed, lowest z-index */}
      <Hyperspeed 
        colors={{
          roadColor: 0x080808,
          islandColor: 0x0a0a0a,
          background: 0x000000,
          leftCars: [0xff102a, 0xeb383e, 0xff102a],
          rightCars: [0xffb700, 0xcc5500, 0xff8800],
          sticks: 0xffb700
        }}
      />
      <CursorEffects />
      <ScanlineOverlay />
      
      {/* Content Layer - Higher z-index */}
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Header – styled like macOS menu bar */}
        <header className="h-12 flex items-center px-4 border-b border-border/20 bg-background/50 backdrop-blur-lg sticky top-0 z-40">
          {/* macOS window control dots */}
          <div className="flex items-center space-x-2">
            <span className="h-3 w-3 rounded-full bg-red-500"></span>
            <span className="h-3 w-3 rounded-full bg-yellow-500"></span>
            <span className="h-3 w-3 rounded-full bg-green-500"></span>
          </div>

          {/* title centered on larger screens */}
          <div className="flex-1 flex justify-center items-center pointer-events-none">
            <span className="font-cyber text-base sm:text-lg">
              <span className="text-primary neon-text-cyan">CYBER</span>
              <span className="text-secondary neon-text-magenta ml-1">SENSEI</span>
            </span>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            <kbd className="hidden sm:inline-flex items-center gap-1 text-[10px] font-mono px-2 py-1 rounded bg-muted border border-border text-muted-foreground cursor-pointer hover:border-primary/30 transition-colors"
              onClick={() => window.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true }))}>
              ⌘K
            </kbd>
            <TutorialTrigger />
          </div>
        </header>
        
        {/* Main Content */}
        <main className="flex-1 overflow-auto pb-24 relative">
          <div className={cn("animate-fade-in", "min-h-full")}>
            {children}
          </div>
        </main>
      </div>
      
      {/* Dock Navigation - Highest z-index */}
      <AppDock />
      
      <TutorialOverlay />
    </div>
  );
}
