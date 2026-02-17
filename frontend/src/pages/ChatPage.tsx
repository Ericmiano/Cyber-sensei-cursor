import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Sparkles, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useTheme } from "@/contexts/ThemeContext";
import { useChatHistory } from "@/contexts/ChatHistoryContext";
import { useUserProgress } from "@/contexts/UserProgressContext";
import XPBar from "@/components/gamification/XPBar";
import StreakDisplay from "@/components/gamification/StreakDisplay";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const generateAIResponse = (userMessage: string, personality: ReturnType<typeof useTheme>['personality']): string => {
  const responses = [
    `Excellent question about "${userMessage.slice(0, 30)}..."! In cybersecurity, understanding the fundamentals is crucial. Let me break this down for you.`,
    `That's a great topic to explore! When it comes to ${userMessage.includes('security') ? 'security' : 'this subject'}, there are several key concepts to understand.`,
    `Ah, I see you're interested in this area! This is fundamental to building a strong security mindset. Here's what you need to know...`,
    `Great inquiry! This touches on core cybersecurity principles. Let me explain with some practical examples...`,
  ];
  
  const baseResponse = responses[Math.floor(Math.random() * responses.length)];
  
  // Modify response based on personality
  let modifier = "";
  if (personality.humorLevel > 70) {
    modifier = " 😄 Don't worry, I'll make this fun!";
  }
  if (personality.technicalDepth > 70) {
    modifier += " Let's dive into the technical details...";
  }
  if (personality.formality < 30) {
    return baseResponse.replace("Excellent question", "Nice one").replace("Great inquiry", "Cool question") + modifier;
  }
  
  return baseResponse + modifier;
};

export default function ChatPage() {
  const { personality } = useTheme();
  const { messages: savedMessages, addMessage, clearHistory } = useChatHistory();
  const { incrementChatMessages, updateStreak } = useUserProgress();
  
  const [messages, setMessages] = useState<Message[]>(() => {
    if (savedMessages.length > 0) {
      return savedMessages.map(m => ({
        ...m,
        timestamp: new Date(m.timestamp),
      }));
    }
    return [{
      id: "welcome",
      role: "assistant" as const,
      content: "Greetings, cyber warrior! I am your Cyber Sensei, here to guide you through the digital realm. What would you like to learn about cybersecurity today?",
      timestamp: new Date(),
    }];
  });
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    updateStreak();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    addMessage({ role: "user", content: userMessage.content });
    incrementChatMessages();
    setInput("");
    setIsTyping(true);

    // Simulate AI response delay
    setTimeout(() => {
      const aiContent = generateAIResponse(userMessage.content, personality);
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: aiContent,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
      addMessage({ role: "assistant", content: aiContent });
      setIsTyping(false);
    }, 1000 + Math.random() * 1500);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleClearChat = () => {
    clearHistory();
    setMessages([
      {
        id: "welcome-new",
        role: "assistant",
        content: "Chat cleared! Ready for a fresh start. What would you like to explore?",
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-3 sm:px-6 py-3 sm:py-4 border-b border-border/30 bg-card/30 backdrop-blur-sm gap-2">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          <div className="relative flex-shrink-0">
            <Bot className="h-6 w-6 sm:h-8 sm:w-8 text-primary" />
            <div className="absolute -bottom-0.5 -right-0.5 w-2 h-2 sm:w-3 sm:h-3 bg-neon-green rounded-full animate-pulse" />
          </div>
          <div className="min-w-0">
            <h1 className="font-cyber text-sm sm:text-lg font-bold text-primary truncate">CYBER SENSEI</h1>
            <p className="text-[10px] sm:text-xs text-muted-foreground hidden xs:block">AI Mentor • Online</p>
          </div>
        </div>
        <div className="flex items-center gap-1 sm:gap-4 flex-shrink-0">
          <div className="hidden sm:block">
            <StreakDisplay variant="compact" />
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearChat}
            className="text-muted-foreground hover:text-primary h-8 px-2 sm:px-3"
          >
            <RefreshCw className="h-4 w-4 sm:mr-2" />
            <span className="hidden sm:inline">Clear Chat</span>
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 p-3 sm:p-6" ref={scrollRef}>
        <div className="max-w-3xl mx-auto space-y-4 sm:space-y-6">
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={cn(
                "flex gap-4 animate-slide-up",
                message.role === "user" ? "flex-row-reverse" : "flex-row"
              )}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Avatar */}
              <div
                className={cn(
                  "flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center",
                  message.role === "assistant"
                    ? "bg-primary/20 neon-glow-cyan"
                    : "bg-secondary/20 neon-glow-magenta"
                )}
              >
                {message.role === "assistant" ? (
                  <Bot className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                ) : (
                  <User className="h-4 w-4 sm:h-5 sm:w-5 text-secondary" />
                )}
              </div>

              {/* Message Bubble */}
              <Card
                className={cn(
                  "max-w-[85%] sm:max-w-[80%] p-3 sm:p-4",
                  "bg-card/50 backdrop-blur-sm",
                  message.role === "assistant"
                    ? "border-primary/20"
                    : "border-secondary/20"
                )}
              >
                <p className="text-sm sm:text-base text-foreground whitespace-pre-wrap">{message.content}</p>
                <span className="text-[10px] sm:text-xs text-muted-foreground mt-1.5 sm:mt-2 block">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </Card>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex gap-4 animate-fade-in">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-primary/20 neon-glow-cyan">
                <Bot className="h-5 w-5 text-primary" />
              </div>
              <Card className="p-4 bg-card/50 border-primary/20">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary animate-pulse" />
                  <span className="text-muted-foreground">Cyber Sensei is thinking...</span>
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t border-border/30 p-3 sm:p-4 bg-card/30 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="relative flex items-end gap-2">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask your Cyber Sensei anything..."
              className={cn(
                "min-h-[50px] sm:min-h-[60px] max-h-[150px] sm:max-h-[200px] resize-none pr-12 text-sm sm:text-base",
                "bg-background/50 border-border/50",
                "focus:border-primary focus:ring-primary/20",
                "placeholder:text-muted-foreground/50"
              )}
              rows={1}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!input.trim() || isTyping}
              className={cn(
                "absolute right-2 bottom-2 h-8 w-8 sm:h-10 sm:w-10",
                "bg-primary hover:bg-primary/90",
                "disabled:opacity-50",
                "neon-glow-cyan transition-all"
              )}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-[10px] sm:text-xs text-muted-foreground mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </form>
      </div>
    </div>
  );
}
