import { useTheme } from "@/contexts/ThemeContext";

export default function ScanlineOverlay() {
  // ThemeContext stores preferences; older code expected a `theme` object.
  // Safely read whether animations are enabled and map to a modest opacity.
  const { preferences } = useTheme();
  const animationsEnabled = preferences?.animations_enabled ?? true;
  const opacity = animationsEnabled ? 0.12 : 0;

  if (!animationsEnabled || opacity <= 0) return null;

  return (
    <div
      className="fixed inset-0 pointer-events-none z-[10]"
      aria-hidden="true"
      style={{
        opacity,
        background: `
          linear-gradient(rgba(18,16,16,0) 50%, rgba(0,0,0,0.25) 50%),
          linear-gradient(90deg, rgba(255,183,0,0.03), rgba(204,85,0,0.01), rgba(138,28,28,0.03))
        `,
        backgroundSize: '100% 2px, 3px 100%',
        mixBlendMode: 'overlay',
      }}
    />
  );
}
