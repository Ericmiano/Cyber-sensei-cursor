import { useEffect, useState, useRef } from "react";

interface GlitchTextProps {
  text: string;
  className?: string;
  intensity?: number;
  speed?: number;
}

const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?";

export default function GlitchText({ text, className = "", intensity = 0.5, speed = 30 }: GlitchTextProps) {
  const [displayedText, setDisplayedText] = useState(text);
  const iterationRef = useRef(0);

  useEffect(() => {
    iterationRef.current = 0;
    
    const interval = setInterval(() => {
      setDisplayedText(
        text
          .split("")
          .map((letter, index) => {
            if (letter === " ") return " ";
            if (index < iterationRef.current) return text[index];
            if (Math.random() > intensity) return text[index];
            return CHARS[Math.floor(Math.random() * CHARS.length)];
          })
          .join("")
      );
      iterationRef.current += 1 / 3;

      if (iterationRef.current >= text.length) {
        clearInterval(interval);
        setDisplayedText(text);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, intensity, speed]);

  return <span className={className}>{displayedText}</span>;
}
