export default function AuroraBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden" aria-hidden="true">
      {/* Amber orb */}
      <div
        className="absolute w-[500px] h-[500px] rounded-full animate-aurora"
        style={{
          top: '20%',
          left: '60%',
          background: 'radial-gradient(circle, hsl(var(--amber) / 0.15) 0%, transparent 70%)',
          filter: 'blur(100px)',
        }}
      />
      {/* Rust orb */}
      <div
        className="absolute w-[400px] h-[400px] rounded-full animate-aurora"
        style={{
          top: '60%',
          left: '20%',
          background: 'radial-gradient(circle, hsl(var(--rust) / 0.08) 0%, transparent 70%)',
          filter: 'blur(120px)',
          animationDelay: '-5s',
        }}
      />
      {/* Deep rust accent */}
      <div
        className="absolute w-[350px] h-[350px] rounded-full animate-breathe"
        style={{
          top: '10%',
          left: '10%',
          background: 'radial-gradient(circle, hsl(var(--deep-rust) / 0.06) 0%, transparent 70%)',
          filter: 'blur(80px)',
          animationDelay: '-2s',
        }}
      />
    </div>
  );
}
