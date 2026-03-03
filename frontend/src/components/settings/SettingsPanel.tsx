import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import UserProfileSettings from "@/components/settings/UserProfileSettings";
import NotificationSettings from "@/components/settings/NotificationSettings";
import KeyboardShortcuts from "@/components/settings/KeyboardShortcuts";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { User, Bell, Keyboard } from "lucide-react";

interface SettingsPanelProps {
  onClose: () => void;
}

export default function SettingsPanel({ onClose }: SettingsPanelProps) {
  return (
    <Sheet open onOpenChange={(open) => !open && onClose()}>
      <SheetContent side="right" className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Settings</SheetTitle>
        </SheetHeader>
        <Tabs defaultValue="profile" className="mt-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="profile" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="shortcuts" className="flex items-center gap-2">
              <Keyboard className="h-4 w-4" />
              Shortcuts
            </TabsTrigger>
          </TabsList>
          <TabsContent value="profile" className="mt-4">
            <UserProfileSettings />
          </TabsContent>
          <TabsContent value="notifications" className="mt-4">
            <NotificationSettings />
          </TabsContent>
          <TabsContent value="shortcuts" className="mt-4">
            <KeyboardShortcuts />
          </TabsContent>
        </Tabs>
      </SheetContent>
    </Sheet>
  );
}
