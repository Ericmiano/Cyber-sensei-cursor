import { useState } from "react";
import { Shield, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";
import { apiClient } from "@/lib/apiClient";

interface TwoFactorVerifyProps {
  tempToken: string;
  onSuccess: (accessToken: string, refreshToken: string) => void;
  onCancel: () => void;
}

export function TwoFactorVerify({ tempToken, onSuccess, onCancel }: TwoFactorVerifyProps) {
  const [code, setCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [useBackupCode, setUseBackupCode] = useState(false);

  const handleVerify = async () => {
    if (!code || (useBackupCode ? code.length < 8 : code.length !== 6)) {
      toast({ 
        title: "Invalid Code", 
        description: useBackupCode ? "Please enter a valid backup code" : "Please enter a 6-digit code",
        variant: "destructive" 
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiClient.post("/auth/login/2fa", {
        temp_token: tempToken,
        token: code
      });
      
      toast({ title: "Success", description: "Login successful!" });
      onSuccess(response.data.access_token, response.data.refresh_token);
    } catch (error: any) {
      toast({ 
        title: "Verification Failed", 
        description: error.response?.data?.detail || "Invalid code",
        variant: "destructive" 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-primary" />
          Two-Factor Authentication
        </CardTitle>
        <CardDescription>
          Enter the code from your authenticator app
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="2fa-code">
            {useBackupCode ? "Backup Code" : "Authentication Code"}
          </Label>
          <Input
            id="2fa-code"
            placeholder={useBackupCode ? "XXXX-XXXX" : "000000"}
            value={code}
            onChange={(e) => {
              const value = useBackupCode 
                ? e.target.value.toUpperCase()
                : e.target.value.replace(/\D/g, "").slice(0, 6);
              setCode(value);
            }}
            maxLength={useBackupCode ? 9 : 6}
            className="text-center text-2xl tracking-widest font-mono"
            autoFocus
          />
        </div>

        <Button 
          onClick={handleVerify} 
          disabled={isLoading || !code} 
          className="w-full"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Verifying...
            </>
          ) : (
            "Verify"
          )}
        </Button>

        <div className="text-center space-y-2">
          <Button
            variant="link"
            onClick={() => {
              setUseBackupCode(!useBackupCode);
              setCode("");
            }}
            className="text-sm text-muted-foreground"
          >
            {useBackupCode ? "Use authenticator code" : "Use backup code"}
          </Button>
          <Button
            variant="link"
            onClick={onCancel}
            className="text-sm text-muted-foreground block w-full"
          >
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
