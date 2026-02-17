import { useRef, useState, ReactNode } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";
import { cn } from "@/lib/utils";

interface InteractiveCardProps {
  children: ReactNode;
  className?: string;
  enableTilt?: boolean;
  enableMagnetic?: boolean;
  enableGlow?: boolean;
  enableBrackets?: boolean;
  pullStrength?: number;
}

export default function InteractiveCard({
  children,
  className = "",
  enableTilt = true,
  enableMagnetic = true,
  enableGlow = true,
  enableBrackets = true,
  pullStrength = 0.15,
}: InteractiveCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [tilt, setTilt] = useState({ rotateX: 0, rotateY: 0 });

  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, { damping: 20, stiffness: 200 });
  const springY = useSpring(y, { damping: 20, stiffness: 200 });

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    if (enableMagnetic) {
      x.set((e.clientX - centerX) * pullStrength);
      y.set((e.clientY - centerY) * pullStrength);
    }

    if (enableTilt) {
      const px = (e.clientX - rect.left) / rect.width;
      const py = (e.clientY - rect.top) / rect.height;
      setTilt({
        rotateY: (px - 0.5) * 20,
        rotateX: (0.5 - py) * 20,
      });
    }
  };

  const handlePointerLeave = () => {
    x.set(0);
    y.set(0);
    setTilt({ rotateX: 0, rotateY: 0 });
    setIsHovered(false);
  };

  return (
    <motion.div
      ref={cardRef}
      className={cn("relative group", className)}
      style={{
        x: springX,
        y: springY,
        rotateX: enableTilt ? tilt.rotateX : 0,
        rotateY: enableTilt ? tilt.rotateY : 0,
        transformStyle: "preserve-3d",
        perspective: 1000,
      }}
      onPointerMove={handlePointerMove}
      onPointerEnter={() => setIsHovered(true)}
      onPointerLeave={handlePointerLeave}
    >
      {children}

      {/* Proximity glow overlay */}
      {enableGlow && isHovered && (
        <div
          className="absolute inset-0 rounded-[inherit] pointer-events-none"
          style={{
            background: 'radial-gradient(circle at 50% 50%, hsl(var(--amber) / 0.08), transparent 70%)',
          }}
        />
      )}

      {/* Corner brackets */}
      {enableBrackets && isHovered && (
        <>
          <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-primary/50 rounded-tl-lg pointer-events-none transition-opacity duration-300" />
          <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-primary/50 rounded-tr-lg pointer-events-none transition-opacity duration-300" />
          <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-primary/50 rounded-bl-lg pointer-events-none transition-opacity duration-300" />
          <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-primary/50 rounded-br-lg pointer-events-none transition-opacity duration-300" />
        </>
      )}

      {/* Holographic shimmer on hover */}
      {isHovered && (
        <motion.div
          className="absolute inset-0 rounded-[inherit] pointer-events-none overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            className="absolute inset-0"
            style={{
              background: 'linear-gradient(90deg, transparent, hsl(var(--amber) / 0.08), transparent)',
            }}
            initial={{ x: '-100%' }}
            animate={{ x: '100%' }}
            transition={{ duration: 0.8, ease: 'easeInOut' }}
          />
        </motion.div>
      )}
    </motion.div>
  );
}
