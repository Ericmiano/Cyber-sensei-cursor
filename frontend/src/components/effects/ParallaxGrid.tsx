/**
 * Parallax Grid Background Component
 */
import { useEffect, useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

export const ParallaxGrid = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll();
  
  const y1 = useTransform(scrollYProgress, [0, 1], [0, -100]);
  const y2 = useTransform(scrollYProgress, [0, 1], [0, -200]);
  const y3 = useTransform(scrollYProgress, [0, 1], [0, -300]);

  return (
    <div ref={containerRef} className="fixed inset-0 pointer-events-none overflow-hidden">
      {/* Grid Layer 1 - Slowest */}
      <motion.div
        style={{ y: y1 }}
        className="absolute inset-0 opacity-10"
      >
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(to right, rgba(251, 191, 36, 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(251, 191, 36, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '100px 100px',
        }} />
      </motion.div>

      {/* Grid Layer 2 - Medium */}
      <motion.div
        style={{ y: y2 }}
        className="absolute inset-0 opacity-5"
      >
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(to right, rgba(251, 191, 36, 0.15) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(251, 191, 36, 0.15) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }} />
      </motion.div>

      {/* Grid Layer 3 - Fastest */}
      <motion.div
        style={{ y: y3 }}
        className="absolute inset-0 opacity-3"
      >
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(to right, rgba(251, 191, 36, 0.2) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(251, 191, 36, 0.2) 1px, transparent 1px)
          `,
          backgroundSize: '25px 25px',
        }} />
      </motion.div>

      {/* Radial gradient overlay */}
      <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-black/50" />
    </div>
  );
};
