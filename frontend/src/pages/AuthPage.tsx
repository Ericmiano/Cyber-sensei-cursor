import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Shield, Zap, Mail, Lock, User, Eye, EyeOff, Loader2, ArrowRight } from "lucide-react";
import { TwoFactorVerify } from "@/components/auth/TwoFactorVerify";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "@/hooks/use-toast";
import { MagneticButton } from "@/components/effects/MagneticButton";

export default function AuthPage() {
  const navigate = useNavigate();
  const { login, signup, isAuthenticated } = useAuth();
  
  const [activeTab, setActiveTab] = useState<"login" | "signup">("login");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [show2FA, setShow2FA] = useState(false);
  const [tempToken, setTempToken] = useState("");
  
  // Form states
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Redirect if already authenticated
  if (isAuthenticated) {
    navigate("/");
    return null;
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast({ title: "Error", description: "Please fill in all fields", variant: "destructive" });
      return;
    }
    
    setIsLoading(true);
    const result = await login(email, password);
    setIsLoading(false);
    
    if (result.success) {
      toast({ title: "Welcome back!", description: "You've successfully logged in." });
      navigate("/");
    } else if (result.requires2FA && result.tempToken) {
      // 2FA required
      setTempToken(result.tempToken);
      setShow2FA(true);
    } else {
      toast({ title: "Login failed", description: result.error, variant: "destructive" });
    }
  };

  const handle2FASuccess = async (accessToken: string, refreshToken: string) => {
    // Store tokens and update auth state
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    toast({ title: "Welcome back!", description: "You've successfully logged in." });
    navigate("/");
    window.location.reload(); // Reload to update auth context
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || !name) {
      toast({ title: "Error", description: "Please fill in all fields", variant: "destructive" });
      return;
    }
    
    if (password !== confirmPassword) {
      toast({ title: "Error", description: "Passwords do not match", variant: "destructive" });
      return;
    }
    
    setIsLoading(true);
    const result = await signup(email, password, name);
    setIsLoading(false);
    
    if (result.success) {
      toast({ title: "Account created!", description: "Welcome to Cyber Sensei." });
      navigate("/");
    } else {
      toast({ title: "Signup failed", description: result.error, variant: "destructive" });
    }
  };

  // Show 2FA verification if needed
  if (show2FA) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-background cyber-grid">
        <div className="absolute inset-0 gradient-cyber opacity-30" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-3xl" />
        <div className="relative w-full max-w-md animate-slide-up">
          <TwoFactorVerify
            tempToken={tempToken}
            onSuccess={handle2FASuccess}
            onCancel={() => setShow2FA(false)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-background cyber-grid">
      {/* Background effects */}
      <div className="absolute inset-0 gradient-cyber opacity-30" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-3xl" />
      
      <div className="relative w-full max-w-md animate-slide-up">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <div className="relative animate-float">
            <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full scale-150" />
            <img src="/logo.png" alt="Cyber Sensei" className="relative h-20 w-20 object-contain animate-pulse-glow" />
          </div>
        </div>

        <Card className="bg-card/80 backdrop-blur-xl border-border/50 neon-border overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-neon-cyan via-neon-purple to-neon-magenta animate-border-flow" />
          
          <CardHeader className="text-center pb-4">
            <CardTitle className="font-cyber text-3xl">
              <span className="text-primary neon-text-cyan">CYBER</span>
              <span className="text-secondary neon-text-magenta ml-2">SENSEI</span>
            </CardTitle>
            <CardDescription>
              Your AI-powered cybersecurity training platform
            </CardDescription>
          </CardHeader>

          <CardContent>
            <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "login" | "signup")}>
              <TabsList className="grid w-full grid-cols-2 mb-6 bg-muted/50">
                <TabsTrigger value="login" className="data-[state=active]:neon-glow-cyan font-medium">
                  Login
                </TabsTrigger>
                <TabsTrigger value="signup" className="data-[state=active]:neon-glow-cyan font-medium">
                  Sign Up
                </TabsTrigger>
              </TabsList>

              <TabsContent value="login" className="space-y-4">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email">Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="login-email"
                        type="email"
                        placeholder="warrior@cyber.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="pl-10 bg-muted/50 border-border/50 focus:border-primary"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="login-password">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="login-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="pl-10 pr-10 bg-muted/50 border-border/50 focus:border-primary"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <MagneticButton
                    type="submit"
                    className="w-full neon-glow-cyan font-cyber"
                    disabled={isLoading}
                    strength={0.15}
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        Access System
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </>
                    )}
                  </MagneticButton>
                </form>
              </TabsContent>

              <TabsContent value="signup" className="space-y-4">
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="signup-name">Display Name</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="signup-name"
                        type="text"
                        placeholder="Cyber Warrior"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="pl-10 bg-muted/50 border-border/50 focus:border-primary"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signup-email">Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="signup-email"
                        type="email"
                        placeholder="warrior@cyber.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="pl-10 bg-muted/50 border-border/50 focus:border-primary"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signup-password">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="signup-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="pl-10 pr-10 bg-muted/50 border-border/50 focus:border-primary"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signup-confirm">Confirm Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="signup-confirm"
                        type={showPassword ? "text" : "password"}
                        placeholder="••••••••"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="pl-10 bg-muted/50 border-border/50 focus:border-primary"
                      />
                    </div>
                  </div>

                  <MagneticButton
                    type="submit"
                    className="w-full neon-glow-cyan font-cyber"
                    disabled={isLoading}
                    strength={0.15}
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        Create Account
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </>
                    )}
                  </MagneticButton>
                </form>
              </TabsContent>
            </Tabs>

            {/* Demo account hint */}
            <div className="mt-6 p-4 rounded-lg bg-muted/30 border border-dashed border-border/50 text-center">
              <p className="text-sm text-muted-foreground">
                <span className="text-primary font-medium">Frontend Demo:</span> Create an account or login with any credentials you've created.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Skip auth option */}
        <div className="mt-4 text-center">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="text-muted-foreground hover:text-primary"
          >
            Continue as Guest
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
}
