import { useState, useEffect } from "react";
import { Shield, Key, Bell, User, Palette } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/hooks/use-toast";
import { TwoFactorSetup } from "@/components/auth/TwoFactorSetup";
import { apiClient } from "@/lib/apiClient";
import { useAuth } from "@/contexts/AuthContext";

export default function SettingsPage() {
  const { user } = useAuth();
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [showTwoFactorSetup, setShowTwoFactorSetup] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadTwoFactorStatus();
  }, []);

  const loadTwoFactorStatus = async () => {
    try {
      const response = await apiClient.get("/2fa/status");
      setTwoFactorEnabled(response.data.is_enabled);
    } catch (error) {
      console.error("Failed to load 2FA status:", error);
    }
  };

  const handleDisable2FA = async () => {
    const code = prompt("Enter your 2FA code to disable:");
    if (!code) return;

    setIsLoading(true);
    try {
      await apiClient.post("/2fa/disable", { token: code });
      setTwoFactorEnabled(false);
      toast({ title: "2FA Disabled", description: "Two-factor authentication has been disabled" });
    } catch (error: any) {
      toast({ 
        title: "Failed to Disable", 
        description: error.response?.data?.detail || "Invalid code",
        variant: "destructive" 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container max-w-4xl py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-cyber mb-2">
          <span className="text-primary neon-text-cyan">SETTINGS</span>
        </h1>
        <p className="text-muted-foreground">Manage your account settings and preferences</p>
      </div>

      {/* Security Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Security
          </CardTitle>
          <CardDescription>Manage your account security settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Two-Factor Authentication</Label>
              <p className="text-sm text-muted-foreground">
                Add an extra layer of security to your account
              </p>
            </div>
            <div className="flex items-center gap-2">
              {twoFactorEnabled ? (
                <>
                  <span className="text-sm text-green-500">Enabled</span>
                  <Button 
                    onClick={handleDisable2FA} 
                    variant="outline" 
                    size="sm"
                    disabled={isLoading}
                  >
                    Disable
                  </Button>
                </>
              ) : (
                <Button 
                  onClick={() => setShowTwoFactorSetup(true)} 
                  size="sm"
                >
                  Enable
                </Button>
              )}
            </div>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Password</Label>
              <p className="text-sm text-muted-foreground">
                Change your password regularly for better security
              </p>
            </div>
            <Button variant="outline" size="sm">
              <Key className="h-4 w-4 mr-2" />
              Change Password
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Profile Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5 text-primary" />
            Profile
          </CardTitle>
          <CardDescription>Manage your profile information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Email</Label>
            <p className="text-sm text-muted-foreground">{user?.email || "Not logged in"}</p>
          </div>
          <div className="space-y-2">
            <Label>Username</Label>
            <p className="text-sm text-muted-foreground">{user?.username || "Not set"}</p>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-primary" />
            Notifications
          </CardTitle>
          <CardDescription>Configure your notification preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="email-notifications">Email Notifications</Label>
            <Switch id="email-notifications" />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="achievement-notifications">Achievement Alerts</Label>
            <Switch id="achievement-notifications" defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="progress-notifications">Progress Updates</Label>
            <Switch id="progress-notifications" defaultChecked />
          </div>
        </CardContent>
      </Card>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5 text-primary" />
            Appearance
          </CardTitle>
          <CardDescription>Customize the look and feel</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="dark-mode">Dark Mode</Label>
            <Switch id="dark-mode" defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="animations">Animations</Label>
            <Switch id="animations" defaultChecked />
          </div>
        </CardContent>
      </Card>

      {/* 2FA Setup Modal */}
      {showTwoFactorSetup && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <TwoFactorSetup
            onComplete={() => {
              setShowTwoFactorSetup(false);
              setTwoFactorEnabled(true);
            }}
            onCancel={() => setShowTwoFactorSetup(false)}
          />
        </div>
      )}
    </div>
  );
}
