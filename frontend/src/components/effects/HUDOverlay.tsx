export default function HUDOverlay() {
  return (
    <div className="fixed inset-0 pointer-events-none z-10" aria-hidden="true">
      {/* Top-left HUD */}
      <div className="absolute top-3 left-3 hud-text leading-relaxed hidden sm:block">
        SYS.STATUS: ONLINE<br />
        ENCRYPTION: AES-256<br />
        UPLINK: SECURE
      </div>

      {/* Bottom-right HUD */}
      <div className="absolute bottom-3 right-3 hud-text text-right leading-relaxed hidden sm:block">
        ALGORITHM: ACTIVE<br />
        NODE: PRIMARY<br />
        SHIELD: ENGAGED
      </div>

      {/* Corner brackets top-left */}
      <div className="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 border-primary/20 rounded-tl-xl" />
      {/* Corner brackets top-right */}
      <div className="absolute top-0 right-0 w-16 h-16 border-t-2 border-r-2 border-primary/20 rounded-tr-xl" />
      {/* Corner brackets bottom-left */}
      <div className="absolute bottom-0 left-0 w-16 h-16 border-b-2 border-l-2 border-primary/20 rounded-bl-xl" />
      {/* Corner brackets bottom-right */}
      <div className="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 border-primary/20 rounded-br-xl" />
    </div>
  );
}
