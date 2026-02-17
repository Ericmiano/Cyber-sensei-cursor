import { motion } from "framer-motion";

interface WordRevealProps {
  text: string;
  className?: string;
  baseDelay?: number;
  stagger?: number;
}

export default function WordReveal({ text, className = "", baseDelay = 0.5, stagger = 0.05 }: WordRevealProps) {
  const words = text.split(" ");

  return (
    <span className={className}>
      {words.map((word, index) => (
        <motion.span
          key={index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: baseDelay + index * stagger, duration: 0.3 }}
          className="inline-block mr-[0.25em]"
        >
          {word}
        </motion.span>
      ))}
    </span>
  );
}
