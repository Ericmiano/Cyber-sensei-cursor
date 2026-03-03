import { Menu, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="h-14 flex items-center px-4 border-b border-border/50 bg-background/80 backdrop-blur shrink-0">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden mr-2"
        onClick={onMenuClick}
      >
        <Menu className="h-5 w-5" />
      </Button>
      <div className="flex items-center gap-2">
        <Shield className="h-6 w-6 text-primary" />
        <span className="font-semibold text-lg">
          <span className="text-primary">Cyber</span>
          <span className="text-secondary"> Sensei</span>
        </span>
      </div>
    </header>
  );
}
