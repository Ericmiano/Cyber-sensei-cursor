import { useState, useEffect, useCallback, useRef } from "react";

interface TrailParticle {
  x: number;
  y: number;
  time: number;
  id: number;
}

interface Ripple {
  x: number;
  y: number;
  id: number;
}

export default function CursorEffects() {
  const [trail, setTrail] = useState<TrailParticle[]>([]);
  const [ripples, setRipples] = useState<Ripple[]>([]);
  const idRef = useRef(0);

  const handlePointerMove = useCallback((e: PointerEvent) => {
    const now = Date.now();
    setTrail(prev => [
      ...prev.filter(p => now - p.time < 500),
      { x: e.clientX, y: e.clientY, time: now, id: idRef.current++ }
    ].slice(-15));
  }, []);

  const handleClick = useCallback((e: MouseEvent) => {
    const ripple = { x: e.clientX, y: e.clientY, id: Date.now() };
    setRipples(prev => [...prev, ripple]);
    setTimeout(() => {
      setRipples(prev => prev.filter(r => r.id !== ripple.id));
    }, 1000);
  }, []);

  useEffect(() => {
    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("click", handleClick);
    
    const cleanup = setInterval(() => {
      setTrail(prev => prev.filter(p => Date.now() - p.time < 500));
    }, 50);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("click", handleClick);
      clearInterval(cleanup);
    };
  }, [handlePointerMove, handleClick]);

  return (
    <div className="fixed inset-0 pointer-events-none z-[90]" aria-hidden="true">
      {/* Cursor trail */}
      {trail.map(particle => {
        const age = Date.now() - particle.time;
        const opacity = 0.6 * (1 - age / 500);
        const scale = 1 - age / 1000;
        return (
          <div
            key={particle.id}
            className="absolute w-[3px] h-[3px] rounded-full"
            style={{
              left: particle.x,
              top: particle.y,
              opacity: Math.max(0, opacity),
              transform: `translate(-50%, -50%) scale(${Math.max(0.3, scale)})`,
              background: 'hsl(var(--amber))',
              boxShadow: '0 0 6px hsl(var(--amber) / 0.6)',
              mixBlendMode: 'screen',
            }}
          />
        );
      })}

      {/* Click ripples */}
      {ripples.map(ripple => (
        <div
          key={ripple.id}
          className="absolute rounded-full"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: 24,
            height: 24,
            border: '2px solid hsl(var(--amber) / 0.5)',
            transform: 'translate(-50%, -50%)',
            animation: 'ripple 1s ease-out forwards',
            filter: 'blur(1px)',
          }}
        />
      ))}
    </div>
  );
}
