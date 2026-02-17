import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { 
  ArrowLeft, 
  ArrowRight, 
  CheckCircle2, 
  PlayCircle,
  BookOpen,
  MessageSquare,
  Lightbulb,
  Code,
  Terminal
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";
import { useUserProgress } from "@/contexts/UserProgressContext";
import CodeExercise from "@/components/exercises/CodeExercise";
import TerminalExercise from "@/components/exercises/TerminalExercise";
import XPBar from "@/components/gamification/XPBar";

// Lesson content data
const lessonContent: Record<string, {
  title: string;
  moduleId: string;
  moduleName: string;
  content: Array<{
    type: "text" | "code" | "tip" | "terminal";
    content: string;
  }>;
  quiz?: {
    question: string;
    options: string[];
    correctIndex: number;
  };
  exercise?: {
    type: "code" | "terminal";
    title: string;
    description: string;
    initialCode?: string;
    expectedOutput?: string;
    hints: string[];
    difficulty: "easy" | "medium" | "hard";
    // For code exercises
    validationKeywords?: string[];
    // For terminal exercises
    objectives?: string[];
    commands?: { command: string; output: string; isRequired?: boolean }[];
  };
  nextLessonId?: string;
  prevLessonId?: string;
}> = {
  "1-1": {
    title: "Introduction to Cybersecurity",
    moduleId: "1",
    moduleName: "Cybersecurity Fundamentals",
    content: [
      {
        type: "text",
        content: "Welcome to the world of cybersecurity! In this lesson, we'll explore what cybersecurity means, why it's important, and the fundamental concepts that form the foundation of digital security."
      },
      {
        type: "text",
        content: "**What is Cybersecurity?**\n\nCybersecurity is the practice of protecting systems, networks, programs, and data from digital attacks. These attacks are usually aimed at accessing, changing, or destroying sensitive information, extorting money from users, or interrupting normal business processes."
      },
      {
        type: "tip",
        content: "Cybersecurity is not just about technology—it also involves people and processes. The human element is often the weakest link in security."
      },
      {
        type: "text",
        content: "**Key Areas of Cybersecurity:**\n\n• **Network Security** - Protecting the network infrastructure\n• **Application Security** - Keeping software and devices free of threats\n• **Information Security** - Protecting data integrity and privacy\n• **Operational Security** - Handling and protecting data assets\n• **Disaster Recovery** - Responding to security incidents"
      },
      {
        type: "code",
        content: "# Example: Basic security check in Python\nimport hashlib\n\ndef verify_password(stored_hash, password):\n    \"\"\"Verify a password against a stored hash\"\"\"\n    password_hash = hashlib.sha256(password.encode()).hexdigest()\n    return password_hash == stored_hash"
      }
    ],
    quiz: {
      question: "What is the primary goal of cybersecurity?",
      options: [
        "To make computers faster",
        "To protect systems and data from digital attacks",
        "To create new software",
        "To design websites"
      ],
      correctIndex: 1
    },
    exercise: {
      type: "code",
      title: "Hash a Password",
      description: "Write a function that takes a password string and returns its SHA-256 hash. Use the hashlib library.",
      initialCode: "import hashlib\n\ndef hash_password(password):\n    # Your code here\n    pass",
      expectedOutput: "A 64-character hexadecimal hash string",
      hints: [
        "Use hashlib.sha256() to create a hash object",
        "Remember to encode the string to bytes using .encode()",
        "Use .hexdigest() to get the hash as a hex string"
      ],
      difficulty: "easy",
      validationKeywords: ["hashlib", "sha256", "encode", "hexdigest"]
    },
    nextLessonId: "1-2"
  },
  "1-2": {
    title: "The CIA Triad",
    moduleId: "1",
    moduleName: "Cybersecurity Fundamentals",
    content: [
      {
        type: "text",
        content: "The CIA Triad is a fundamental model in cybersecurity that guides information security policies. It stands for Confidentiality, Integrity, and Availability."
      },
      {
        type: "text",
        content: "**Confidentiality**\n\nEnsuring that information is accessible only to those authorized to have access. Methods include encryption, access controls, and authentication."
      },
      {
        type: "text",
        content: "**Integrity**\n\nMaintaining the accuracy and completeness of data. This means data cannot be modified in an unauthorized or undetected manner."
      },
      {
        type: "text",
        content: "**Availability**\n\nEnsuring that authorized users have access to information and resources when needed. This involves maintaining hardware, performing upgrades, and having disaster recovery plans."
      },
      {
        type: "tip",
        content: "When designing security controls, always consider how they affect all three aspects of the CIA triad. Strengthening one shouldn't weaken another."
      },
      {
        type: "terminal",
        content: "$ openssl enc -aes-256-cbc -salt -in secret.txt -out encrypted.txt\nenter aes-256-cbc encryption password:\nVerifying - enter aes-256-cbc encryption password:"
      }
    ],
    quiz: {
      question: "Which component of the CIA Triad ensures data cannot be modified without authorization?",
      options: [
        "Confidentiality",
        "Integrity",
        "Availability",
        "Authentication"
      ],
      correctIndex: 1
    },
    exercise: {
      type: "terminal",
      title: "File Encryption Lab",
      description: "Practice using OpenSSL commands to encrypt and verify files. Complete the objectives below.",
      objectives: [
        "Check the OpenSSL version",
        "List available encryption algorithms",
        "Encrypt a sample file"
      ],
      commands: [
        { command: "openssl version", output: "OpenSSL 3.0.2 15 Mar 2022 (Library: OpenSSL 3.0.2 15 Mar 2022)", isRequired: true },
        { command: "openssl list -cipher-algorithms", output: "AES-128-CBC\nAES-256-CBC\nAES-128-GCM\nAES-256-GCM\nDES-EDE3-CBC\n...", isRequired: true },
        { command: "openssl enc -aes-256-cbc -salt -in file.txt -out encrypted.txt", output: "File encrypted successfully.\nOutput: encrypted.txt", isRequired: true }
      ],
      hints: [
        "Use 'openssl version' to check the installed version",
        "List ciphers with 'openssl list -cipher-algorithms'",
        "Encrypt files with 'openssl enc -aes-256-cbc -salt -in [file] -out [output]'"
      ],
      difficulty: "medium"
    },
    prevLessonId: "1-1",
    nextLessonId: "1-3"
  },
  "1-3": {
    title: "Types of Cyber Threats",
    moduleId: "1",
    moduleName: "Cybersecurity Fundamentals",
    content: [
      {
        type: "text",
        content: "Understanding the different types of cyber threats is essential for building effective defenses. Let's explore the most common attack vectors."
      },
      {
        type: "text",
        content: "**Malware**\n\nMalicious software designed to damage, disrupt, or gain unauthorized access:\n• **Viruses** - Attach to legitimate programs\n• **Worms** - Self-replicate across networks\n• **Trojans** - Disguise as legitimate software\n• **Ransomware** - Encrypt files for ransom\n• **Spyware** - Secretly monitor user activity"
      },
      {
        type: "text",
        content: "**Social Engineering**\n\nManipulating people into divulging confidential information:\n• **Phishing** - Fraudulent emails/websites\n• **Spear Phishing** - Targeted phishing\n• **Pretexting** - Creating false scenarios\n• **Baiting** - Luring victims with promises"
      },
      {
        type: "tip",
        content: "Over 90% of successful cyber attacks start with phishing. Training users to recognize these attacks is critical!"
      },
      {
        type: "code",
        content: "# Example: Detecting suspicious URLs\nimport re\n\ndef is_suspicious_url(url):\n    suspicious_patterns = [\n        r'[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+',  # IP address\n        r'@',  # @ symbol in URL\n        r'(login|secure|account|update).*\\.php',  # Common phishing patterns\n    ]\n    return any(re.search(p, url.lower()) for p in suspicious_patterns)"
      }
    ],
    quiz: {
      question: "Which type of malware encrypts your files and demands payment?",
      options: [
        "Spyware",
        "Worm",
        "Ransomware",
        "Trojan"
      ],
      correctIndex: 2
    },
    exercise: {
      type: "code",
      title: "Phishing URL Detector",
      description: "Create a function that checks if a URL might be a phishing attempt by looking for suspicious patterns.",
      initialCode: "def detect_phishing(url):\n    # Check for these red flags:\n    # 1. IP address instead of domain\n    # 2. Misspelled popular domains\n    # 3. Suspicious keywords\n    pass",
      hints: [
        "Check if the URL contains an IP address pattern",
        "Look for common misspellings like 'paypa1' or 'g00gle'",
        "Check for suspicious keywords like 'login', 'verify', 'update'"
      ],
      difficulty: "medium",
      validationKeywords: ["if", "return", "in", "lower"]
    },
    prevLessonId: "1-2",
    nextLessonId: "1-4"
  },
  "1-4": {
    title: "Authentication & Access Control",
    moduleId: "1",
    moduleName: "Cybersecurity Fundamentals",
    content: [
      {
        type: "text",
        content: "Authentication verifies identity while authorization determines access levels. Together, they form the foundation of access control."
      },
      {
        type: "text",
        content: "**Authentication Factors:**\n\n• **Something you know** - Passwords, PINs\n• **Something you have** - Smart cards, tokens, phones\n• **Something you are** - Biometrics (fingerprint, face)\n• **Somewhere you are** - Location-based\n• **Something you do** - Behavioral patterns"
      },
      {
        type: "text",
        content: "**Multi-Factor Authentication (MFA)**\n\nCombining two or more factors significantly increases security. Even if one factor is compromised, the attacker still needs the others."
      },
      {
        type: "tip",
        content: "Use password managers to generate and store strong, unique passwords for each account. Never reuse passwords!"
      },
      {
        type: "code",
        content: "# Example: Password strength checker\nimport re\n\ndef check_password_strength(password):\n    score = 0\n    if len(password) >= 12: score += 2\n    elif len(password) >= 8: score += 1\n    if re.search(r'[A-Z]', password): score += 1\n    if re.search(r'[a-z]', password): score += 1\n    if re.search(r'[0-9]', password): score += 1\n    if re.search(r'[!@#$%^&*]', password): score += 2\n    return 'Strong' if score >= 6 else 'Medium' if score >= 4 else 'Weak'"
      }
    ],
    quiz: {
      question: "What does MFA stand for and why is it important?",
      options: [
        "Multiple File Access - allows accessing many files",
        "Multi-Factor Authentication - adds extra security layers",
        "Manual Firewall Adjustment - configures firewalls",
        "Master File Archive - stores backup files"
      ],
      correctIndex: 1
    },
    exercise: {
      type: "code",
      title: "Password Strength Validator",
      description: "Build a comprehensive password strength checker that evaluates multiple criteria.",
      initialCode: "def validate_password(password):\n    # Check:\n    # - Minimum 8 characters\n    # - Has uppercase and lowercase\n    # - Has numbers\n    # - Has special characters\n    # Return score 0-100\n    pass",
      hints: [
        "Use len() to check password length",
        "Use string methods like isupper(), islower(), isdigit()",
        "Check for special characters using a set or regex"
      ],
      difficulty: "easy",
      validationKeywords: ["len", "if", "return"]
    },
    prevLessonId: "1-3"
  },
  "2-1": {
    title: "Network Fundamentals",
    moduleId: "2",
    moduleName: "Network Security",
    content: [
      {
        type: "text",
        content: "Before diving into network security, let's understand how networks work. Networks connect devices to share resources and communicate."
      },
      {
        type: "text",
        content: "**The OSI Model**\n\n7. **Application** - End-user layer (HTTP, FTP)\n6. **Presentation** - Data formatting (SSL, encryption)\n5. **Session** - Connection management\n4. **Transport** - Reliable delivery (TCP, UDP)\n3. **Network** - Routing and addressing (IP)\n2. **Data Link** - Local delivery (MAC)\n1. **Physical** - Hardware connections"
      },
      {
        type: "tip",
        content: "Remember the OSI layers with: 'All People Seem To Need Data Processing' (top to bottom)"
      },
      {
        type: "terminal",
        content: "$ ifconfig\neth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n        inet 192.168.1.100  netmask 255.255.255.0  broadcast 192.168.1.255\n        inet6 fe80::1  prefixlen 64  scopeid 0x20<link>"
      }
    ],
    quiz: {
      question: "At which OSI layer does IP addressing occur?",
      options: [
        "Application Layer",
        "Transport Layer",
        "Network Layer",
        "Data Link Layer"
      ],
      correctIndex: 2
    },
    exercise: {
      type: "terminal",
      title: "Network Discovery",
      description: "Use network commands to explore your network configuration and discover active hosts.",
      objectives: [
        "View your IP configuration",
        "Test connectivity to a server",
        "Trace the route to a website"
      ],
      commands: [
        { command: "ifconfig", output: "eth0: inet 192.168.1.100  netmask 255.255.255.0\nlo: inet 127.0.0.1  netmask 255.0.0.0", isRequired: true },
        { command: "ping -c 4 8.8.8.8", output: "PING 8.8.8.8: 64 bytes from 8.8.8.8: icmp_seq=1 ttl=118 time=12.5 ms\n4 packets transmitted, 4 received, 0% packet loss", isRequired: true },
        { command: "traceroute google.com", output: "1  192.168.1.1 (gateway) 1.234 ms\n2  10.0.0.1 2.567 ms\n3  google.com (142.250.x.x) 15.789 ms", isRequired: true }
      ],
      hints: [
        "Use 'ifconfig' or 'ip addr' to view network interfaces",
        "Ping tests connectivity: 'ping -c 4 [address]'",
        "Traceroute shows the path: 'traceroute [domain]'"
      ],
      difficulty: "easy"
    },
    nextLessonId: "2-2"
  },
  "2-2": {
    title: "Firewalls & Packet Filtering",
    moduleId: "2",
    moduleName: "Network Security",
    content: [
      {
        type: "text",
        content: "Firewalls are network security devices that monitor and control incoming and outgoing network traffic based on predetermined security rules."
      },
      {
        type: "text",
        content: "**Types of Firewalls:**\n\n• **Packet Filtering** - Examines packets at network layer\n• **Stateful Inspection** - Tracks connection states\n• **Application Layer** - Deep packet inspection\n• **Next-Generation (NGFW)** - Combines multiple features"
      },
      {
        type: "code",
        content: "# Example: Simple iptables rules\n# Block all incoming traffic by default\n# iptables -P INPUT DROP\n\n# Allow established connections\n# iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT\n\n# Allow SSH on port 22\n# iptables -A INPUT -p tcp --dport 22 -j ACCEPT\n\n# Allow HTTP and HTTPS\n# iptables -A INPUT -p tcp --dport 80 -j ACCEPT\n# iptables -A INPUT -p tcp --dport 443 -j ACCEPT"
      },
      {
        type: "tip",
        content: "Follow the principle of least privilege: only allow traffic that is explicitly needed."
      }
    ],
    quiz: {
      question: "What does a stateful firewall track that a simple packet filter does not?",
      options: [
        "IP addresses",
        "Port numbers",
        "Connection states",
        "Packet sizes"
      ],
      correctIndex: 2
    },
    exercise: {
      type: "terminal",
      title: "Firewall Configuration",
      description: "Configure basic firewall rules using iptables commands.",
      objectives: [
        "View current firewall rules",
        "Allow SSH connections",
        "Block a specific IP address"
      ],
      commands: [
        { command: "iptables -L", output: "Chain INPUT (policy ACCEPT)\ntarget     prot opt source               destination\n\nChain FORWARD (policy ACCEPT)\nChain OUTPUT (policy ACCEPT)", isRequired: true },
        { command: "iptables -A INPUT -p tcp --dport 22 -j ACCEPT", output: "Rule added: Allow TCP port 22 (SSH)", isRequired: true },
        { command: "iptables -A INPUT -s 10.0.0.5 -j DROP", output: "Rule added: Block all traffic from 10.0.0.5", isRequired: true }
      ],
      hints: [
        "List rules with 'iptables -L'",
        "Add rules with 'iptables -A INPUT -p tcp --dport [port] -j ACCEPT'",
        "Block IPs with 'iptables -A INPUT -s [IP] -j DROP'"
      ],
      difficulty: "medium"
    },
    prevLessonId: "2-1",
    nextLessonId: "2-3"
  },
  "4-1": {
    title: "Introduction to Ethical Hacking",
    moduleId: "4",
    moduleName: "Ethical Hacking",
    content: [
      {
        type: "text",
        content: "Ethical hacking involves legally testing systems for vulnerabilities using the same techniques as malicious hackers—but with permission and for defensive purposes."
      },
      {
        type: "text",
        content: "**Types of Hackers:**\n\n• **White Hat** - Ethical hackers who help improve security\n• **Black Hat** - Malicious hackers who exploit systems\n• **Grey Hat** - Operate between legal and illegal\n• **Script Kiddies** - Use existing tools without understanding\n• **Hacktivists** - Hack for political/social causes"
      },
      {
        type: "text",
        content: "**Penetration Testing Phases:**\n\n1. **Reconnaissance** - Gathering information\n2. **Scanning** - Identifying vulnerabilities\n3. **Gaining Access** - Exploiting vulnerabilities\n4. **Maintaining Access** - Establishing persistence\n5. **Covering Tracks** - Removing evidence\n6. **Reporting** - Documenting findings"
      },
      {
        type: "tip",
        content: "Always get written authorization before testing any system. Unauthorized testing is illegal regardless of intent!"
      }
    ],
    quiz: {
      question: "What is the most important requirement before conducting a penetration test?",
      options: [
        "Having the latest hacking tools",
        "Written authorization from the system owner",
        "A fast internet connection",
        "Knowledge of all exploits"
      ],
      correctIndex: 1
    },
    exercise: {
      type: "terminal",
      title: "Reconnaissance Lab",
      description: "Practice passive reconnaissance techniques to gather information about a target.",
      objectives: [
        "Perform DNS lookup",
        "Find WHOIS information",
        "Scan for open ports"
      ],
      commands: [
        { command: "nslookup example.com", output: "Server:  8.8.8.8\nAddress:  8.8.8.8#53\n\nNon-authoritative answer:\nName:    example.com\nAddress: 93.184.216.34", isRequired: true },
        { command: "whois example.com", output: "Domain Name: EXAMPLE.COM\nRegistry Domain ID: 2336799_DOMAIN_COM-VRSN\nRegistrar: RESERVED-Internet Assigned Numbers Authority\nUpdated Date: 2023-08-14T07:01:38Z", isRequired: true },
        { command: "nmap -sV example.com", output: "Starting Nmap scan...\nPORT     STATE SERVICE\n80/tcp   open  http\n443/tcp  open  https\nNmap done: 1 IP address (1 host up)", isRequired: true }
      ],
      hints: [
        "Use 'nslookup' or 'dig' for DNS queries",
        "WHOIS provides domain registration info",
        "Nmap is the go-to tool for port scanning"
      ],
      difficulty: "medium"
    },
    nextLessonId: "4-2"
  },
  "4-2": {
    title: "Vulnerability Scanning",
    moduleId: "4",
    moduleName: "Ethical Hacking",
    content: [
      {
        type: "text",
        content: "Vulnerability scanning is the process of identifying security weaknesses in systems, networks, and applications."
      },
      {
        type: "text",
        content: "**Common Vulnerability Scanners:**\n\n• **Nessus** - Comprehensive vulnerability scanner\n• **OpenVAS** - Open-source alternative\n• **Nikto** - Web server scanner\n• **OWASP ZAP** - Web application security\n• **Burp Suite** - Web vulnerability scanner"
      },
      {
        type: "text",
        content: "**CVSS (Common Vulnerability Scoring System):**\n\n• **0.0** - None\n• **0.1-3.9** - Low\n• **4.0-6.9** - Medium\n• **7.0-8.9** - High\n• **9.0-10.0** - Critical"
      },
      {
        type: "code",
        content: "# Example: Simple vulnerability check\nVULNERABLE_VERSIONS = {\n    'apache': ['2.4.49', '2.4.50'],  # Path traversal\n    'log4j': ['2.0', '2.14.1'],       # Log4Shell\n    'openssl': ['3.0.0', '3.0.6'],    # Heartbleed-like\n}\n\ndef check_vulnerable(software, version):\n    if software in VULNERABLE_VERSIONS:\n        vuln_range = VULNERABLE_VERSIONS[software]\n        return vuln_range[0] <= version <= vuln_range[1]\n    return False"
      }
    ],
    quiz: {
      question: "What CVSS score range indicates a Critical vulnerability?",
      options: [
        "0.0 - 3.9",
        "4.0 - 6.9",
        "7.0 - 8.9",
        "9.0 - 10.0"
      ],
      correctIndex: 3
    },
    prevLessonId: "4-1",
    nextLessonId: "4-3"
  },
};

// Type for lesson content
interface LessonData {
  title: string;
  moduleId: string;
  moduleName: string;
  content: Array<{
    type: "text" | "code" | "tip" | "terminal";
    content: string;
  }>;
  quiz?: {
    question: string;
    options: string[];
    correctIndex: number;
  };
  exercise?: {
    type: "code" | "terminal";
    title: string;
    description: string;
    initialCode?: string;
    expectedOutput?: string;
    hints: string[];
    difficulty: "easy" | "medium" | "hard";
    validationKeywords?: string[];
    objectives?: string[];
    commands?: { command: string; output: string; isRequired?: boolean }[];
  };
  nextLessonId?: string;
  prevLessonId?: string;
}

// Generate default content for lessons that don't have specific content
const getDefaultLessonContent = (lessonId: string): LessonData => {
  const [moduleId, lessonNum] = lessonId.split("-");
  return {
    title: `Lesson ${lessonNum}`,
    moduleId,
    moduleName: "Training Module",
    content: [
      {
        type: "text" as const,
        content: "This lesson is currently under development. Check back soon for comprehensive cybersecurity training content!"
      },
      {
        type: "tip" as const,
        content: "In the meantime, try chatting with the AI Sensei to learn more about this topic."
      }
    ],
    quiz: {
      question: "What is the best way to continue learning?",
      options: [
        "Give up",
        "Practice consistently and ask questions",
        "Only read theory",
        "Skip the basics"
      ],
      correctIndex: 1
    }
  };
};

export default function LessonPage() {
  const { moduleId, lessonId } = useParams<{ moduleId: string; lessonId: string }>();
  const navigate = useNavigate();
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const { progress, completeLesson, passQuiz, updateStreak } = useUserProgress();

  const lesson = lessonId 
    ? (lessonContent[lessonId] || getDefaultLessonContent(lessonId))
    : null;

  const isLessonCompleted = lessonId 
    ? progress.lessonsCompleted.some(l => l.lessonId === lessonId && l.completed)
    : false;

  useEffect(() => {
    updateStreak();
  }, []);

  if (!lesson || !moduleId) {
    return (
      <div className="p-6 max-w-4xl mx-auto text-center">
        <h1 className="font-cyber text-3xl text-primary mb-4">LESSON NOT FOUND</h1>
        <p className="text-muted-foreground mb-6">The requested lesson does not exist.</p>
        <Button onClick={() => navigate("/training")} variant="outline">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Training
        </Button>
      </div>
    );
  }

  const handleAnswerSubmit = () => {
    if (selectedAnswer === null) return;
    setShowResult(true);
    
    if (lesson.quiz && selectedAnswer === lesson.quiz.correctIndex) {
      toast({
        title: "Correct! 🎉",
        description: "+100 XP earned!",
      });
      if (lessonId) {
        completeLesson(lessonId, moduleId);
        passQuiz(lessonId, 100);
      }
    } else {
      toast({
        title: "Not quite right",
        description: "Review the material and try again!",
        variant: "destructive",
      });
    }
  };

  const handleContinue = () => {
    if (lesson.nextLessonId) {
      navigate(`/training/${moduleId}/lesson/${lesson.nextLessonId}`);
      setSelectedAnswer(null);
      setShowResult(false);
    } else {
      navigate(`/training/${moduleId}`);
    }
  };

  // Validation function for code exercises
  const validateCode = (code: string): { success: boolean; message: string } => {
    const keywords = lesson.exercise?.validationKeywords || [];
    const hasAllKeywords = keywords.every(kw => code.toLowerCase().includes(kw.toLowerCase()));
    
    if (!hasAllKeywords) {
      return {
        success: false,
        message: `Your code is missing some required elements. Make sure to use: ${keywords.join(", ")}`
      };
    }
    
    if (code.includes("pass") && code.split("pass").length > 1) {
      return {
        success: false,
        message: "Replace the 'pass' statement with your implementation."
      };
    }
    
    return {
      success: true,
      message: "Great job! Your implementation looks correct. The function properly hashes the password using SHA-256."
    };
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate(`/training/${moduleId}`)}
          className="mb-4 hover:bg-primary/10"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to {lesson.moduleName}
        </Button>

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <BookOpen className="h-4 w-4" />
            <span>{lesson.moduleName}</span>
          </div>
          <XPBar showDetails={false} className="w-48" />
        </div>
        
        <h1 className="font-cyber text-3xl font-bold text-primary mb-4">
          {lesson.title}
        </h1>

        <Progress value={isLessonCompleted ? 100 : 50} className="h-2 bg-muted" />
        {isLessonCompleted && (
          <p className="text-xs text-neon-green mt-2 flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3" />
            Lesson Completed
          </p>
        )}
      </div>

      {/* Lesson Content */}
      <div className="space-y-6 mb-8">
        {lesson.content.map((block, index) => (
          <div key={index} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
            {block.type === "text" && (
              <Card className="bg-card/50 border-border/50">
                <CardContent className="p-6">
                  <div className="prose prose-invert max-w-none">
                    {block.content.split('\n').map((paragraph, i) => (
                      <p key={i} className="text-foreground mb-4 last:mb-0 whitespace-pre-wrap">
                        {paragraph.startsWith('**') ? (
                          <strong className="text-primary font-cyber">
                            {paragraph.replace(/\*\*/g, '')}
                          </strong>
                        ) : paragraph.startsWith('•') ? (
                          <span className="block ml-4">{paragraph}</span>
                        ) : (
                          paragraph
                        )}
                      </p>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {block.type === "tip" && (
              <Card className="bg-neon-orange/10 border-neon-orange/30">
                <CardContent className="p-6 flex gap-4">
                  <Lightbulb className="h-6 w-6 text-neon-orange flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-medium text-neon-orange mb-1">Pro Tip</h4>
                    <p className="text-foreground">{block.content}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {block.type === "code" && (
              <Card className="bg-muted/50 border-border/50 overflow-hidden">
                <CardHeader className="py-3 px-4 bg-muted/80 border-b border-border/30">
                  <div className="flex items-center gap-2">
                    <Code className="h-4 w-4 text-primary" />
                    <span className="text-sm font-mono text-muted-foreground">Code Example</span>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <pre className="p-4 overflow-x-auto">
                    <code className="text-sm font-mono text-neon-green">
                      {block.content}
                    </code>
                  </pre>
                </CardContent>
              </Card>
            )}

            {block.type === "terminal" && (
              <Card className="bg-black border-neon-green/30 overflow-hidden">
                <CardHeader className="py-3 px-4 bg-black border-b border-neon-green/20">
                  <div className="flex items-center gap-2">
                    <Terminal className="h-4 w-4 text-neon-green" />
                    <span className="text-sm font-mono text-neon-green/70">Terminal</span>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <pre className="p-4 overflow-x-auto">
                    <code className="text-sm font-mono text-neon-green">
                      {block.content}
                    </code>
                  </pre>
                </CardContent>
              </Card>
            )}
          </div>
        ))}
      </div>

      {/* Interactive Exercise */}
      {lesson.exercise && lessonId && (
        <div className="mb-8">
          {lesson.exercise.type === "code" && lesson.exercise.initialCode && (
            <CodeExercise
              lessonId={lessonId}
              title={lesson.exercise.title}
              description={lesson.exercise.description}
              initialCode={lesson.exercise.initialCode}
              expectedOutput={lesson.exercise.expectedOutput}
              validationFn={validateCode}
              hints={lesson.exercise.hints}
              difficulty={lesson.exercise.difficulty}
            />
          )}
          {lesson.exercise.type === "terminal" && lesson.exercise.objectives && lesson.exercise.commands && (
            <TerminalExercise
              lessonId={lessonId}
              title={lesson.exercise.title}
              description={lesson.exercise.description}
              objectives={lesson.exercise.objectives}
              commands={lesson.exercise.commands}
              hints={lesson.exercise.hints}
            />
          )}
        </div>
      )}

      {/* Quiz Section */}
      {lesson.quiz && (
        <Card className="bg-card/50 border-primary/30 neon-border mb-8">
          <CardHeader>
            <CardTitle className="font-cyber text-xl text-primary flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              KNOWLEDGE CHECK
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg mb-6">{lesson.quiz.question}</p>
            
            <div className="space-y-3 mb-6">
              {lesson.quiz.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => !showResult && setSelectedAnswer(index)}
                  disabled={showResult}
                  className={cn(
                    "w-full p-4 rounded-lg text-left transition-all duration-200",
                    "border",
                    selectedAnswer === index
                      ? showResult
                        ? index === lesson.quiz!.correctIndex
                          ? "border-neon-green bg-neon-green/20 text-neon-green"
                          : "border-destructive bg-destructive/20 text-destructive"
                        : "border-primary bg-primary/20"
                      : showResult && index === lesson.quiz!.correctIndex
                        ? "border-neon-green bg-neon-green/10"
                        : "border-border/50 hover:border-primary/50 bg-muted/30",
                    !showResult && "cursor-pointer"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
                      selectedAnswer === index
                        ? "bg-primary/30 text-primary"
                        : "bg-muted text-muted-foreground"
                    )}>
                      {String.fromCharCode(65 + index)}
                    </div>
                    <span>{option}</span>
                    {showResult && index === lesson.quiz!.correctIndex && (
                      <CheckCircle2 className="h-5 w-5 text-neon-green ml-auto" />
                    )}
                  </div>
                </button>
              ))}
            </div>

            {!showResult ? (
              <Button 
                onClick={handleAnswerSubmit}
                disabled={selectedAnswer === null}
                className="w-full neon-glow-cyan"
              >
                Submit Answer
              </Button>
            ) : (
              <Button 
                onClick={handleContinue}
                className="w-full neon-glow-cyan"
              >
                {lesson.nextLessonId ? (
                  <>
                    Continue to Next Lesson
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Complete Module
                  </>
                )}
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex justify-between">
        {lesson.prevLessonId ? (
          <Button
            variant="outline"
            onClick={() => {
              navigate(`/training/${moduleId}/lesson/${lesson.prevLessonId}`);
              setSelectedAnswer(null);
              setShowResult(false);
            }}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Previous Lesson
          </Button>
        ) : (
          <div />
        )}
        
        <Button asChild variant="ghost" className="hover:bg-primary/10">
          <Link to="/chat">
            <MessageSquare className="h-4 w-4 mr-2" />
            Ask AI Sensei
          </Link>
        </Button>
      </div>
    </div>
  );
}
