import { useState } from "react";
import { Shield, Copy, Check, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";
import { apiClient } from "@/lib/apiClient";

interface TwoFactorSetupProps {
  onComplete: () => void;
  onCancel: () => void;
}

export function TwoFactorSetup({ onComplete, onCancel }: TwoFactorSetupProps) {
  const [step, setStep] = useState<"setup" | "verify">("setup");
  const [qrCode, setQrCode] = useState<string>("");
  const [secret, setSecret] = useState<string>("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSetup = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.post("/2fa/setup");
      setQrCode(response.data.qr_code);
      setSecret(response.data.secret);
      setBackupCodes(response.data.backup_codes);
      setStep("verify");
      toast({ title: "2FA Setup", description: "Scan the QR code with your authenticator app" });
    } catch (error: any) {
      toast({ 
        title: "Setup Failed", 
        description: error.response?.data?.detail || "Failed to setup 2FA",
        variant: "destructive" 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      toast({ title: "Invalid Code", description: "Please enter a 6-digit code", variant: "destructive" });
      return;
    }

    setIsLoading(true);
    try {
      await apiClient.post("/2fa/enable", { token: verificationCode });
      toast({ title: "2FA Enabled", description: "Two-factor authentication is now active" });
      onComplete();
    } catch (error: any) {
      toast({ 
        title: "Verification Failed", 
        description: error.response?.data?.detail || "Invalid verification code",
        variant: "destructive" 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copySecret = () => {
    navigator.clipboard.writeText(secret);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    toast({ title: "Copied", description: "Secret key copied to clipboard" });
  };

  const downloadBackupCodes = () => {
    const content = `Cyber Sensei - 2FA Backup Codes\n\n${backupCodes.join("\n")}\n\nKeep these codes safe!`;
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "cyber-sensei-backup-codes.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  if (step === "setup") {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Enable Two-Factor Authentication
          </CardTitle>
          <CardDescription>
            Add an extra layer of security to your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Two-factor authentication (2FA) adds an additional layer of security by requiring a code from your phone in addition to your password.
          </p>
          <div className="flex gap-2">
            <Button onClick={handleSetup} disabled={isLoading} className="flex-1">
              {isLoading ? "Setting up..." : "Start Setup"}
            </Button>
            <Button onClick={onCancel} variant="outline">
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Scan QR Code</CardTitle>
        <CardDescription>
          Use your authenticator app to scan this code
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {qrCode && (
          <div className="flex justify-center p-4 bg-white rounded-lg">
            <img src={qrCode} alt="2FA QR Code" className="w-48 h-48" />
          </div>
        )}

        <div className="space-y-2">
          <Label>Or enter this key manually:</Label>
          <div className="flex gap-2">
            <Input value={secret} readOnly className="font-mono text-sm" />
            <Button onClick={copySecret} variant="outline" size="icon">
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <Label>Backup Codes</Label>
          <div className="p-3 bg-muted rounded-lg space-y-1">
            {backupCodes.slice(0, 3).map((code, i) => (
              <div key={i} className="font-mono text-xs">{code}</div>
            ))}
            <div className="text-xs text-muted-foreground">+ {backupCodes.length - 3} more codes</div>
          </div>
          <Button onClick={downloadBackupCodes} variant="outline" size="sm" className="w-full">
            <Download className="h-4 w-4 mr-2" />
            Download All Backup Codes
          </Button>
        </div>

        <div className="space-y-2">
          <Label htmlFor="verification-code">Enter Verification Code</Label>
          <Input
            id="verification-code"
            placeholder="000000"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            maxLength={6}
            className="text-center text-2xl tracking-widest font-mono"
          />
        </div>

        <div className="flex gap-2">
          <Button onClick={handleVerify} disabled={isLoading || verificationCode.length !== 6} className="flex-1">
            {isLoading ? "Verifying..." : "Verify & Enable"}
          </Button>
          <Button onClick={onCancel} variant="outline">
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
