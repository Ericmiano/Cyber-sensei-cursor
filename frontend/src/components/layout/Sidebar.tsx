import { Shield, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SidebarProps {
  onOpenSettings: () => void;
}

export default function Sidebar({ onOpenSettings }: SidebarProps) {
  return (
    <aside className="hidden lg:flex flex-col w-64 border-r border-border/50 bg-card/30">
      <div className="p-4 border-b border-border/30 flex items-center gap-2">
        <Shield className="h-8 w-8 text-primary" />
        <span className="font-semibold text-lg">
          <span className="text-primary">Cyber</span>
          <span className="text-secondary"> Sensei</span>
        </span>
      </div>
      <div className="flex-1 p-4">
        <p className="text-sm text-muted-foreground">
          AI-powered cybersecurity assistant
        </p>
      </div>
      <div className="p-4 border-t border-border/30">
        <Button
          variant="ghost"
          className="w-full justify-start"
          onClick={onOpenSettings}
        >
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>
      </div>
    </aside>
  );
}
