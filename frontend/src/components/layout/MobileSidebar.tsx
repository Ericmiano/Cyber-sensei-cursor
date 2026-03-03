import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Shield, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";

interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenSettings: () => void;
}

export default function MobileSidebar({ isOpen, onClose, onOpenSettings }: MobileSidebarProps) {
  const handleSettings = () => {
    onOpenSettings();
    onClose();
  };

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent side="left" className="w-64">
        <div className="flex flex-col h-full">
          <div className="p-4 border-b border-border/30 flex items-center gap-2">
            <Shield className="h-8 w-8 text-primary" />
            <span className="font-semibold text-lg">Cyber Sensei</span>
          </div>
          <div className="flex-1 p-4" />
          <div className="p-4 border-t border-border/30">
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={handleSettings}
            >
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
