import * as React from "react";
import * as SliderPrimitive from "@radix-ui/react-slider";
import { cn } from "@/lib/utils";

interface AnimatedSliderProps
  extends React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root> {
  showValue?: boolean;
  lowLabel?: string;
  highLabel?: string;
  icon?: React.ReactNode;
  valueFormatter?: (value: number) => string;
  glowColor?: "cyan" | "magenta" | "purple" | "green" | "orange";
}

const glowColors = {
  cyan: "bg-neon-cyan shadow-[0_0_10px_hsl(var(--neon-cyan)/0.5)]",
  magenta: "bg-neon-magenta shadow-[0_0_10px_hsl(var(--neon-magenta)/0.5)]",
  purple: "bg-neon-purple shadow-[0_0_10px_hsl(var(--neon-purple)/0.5)]",
  green: "bg-neon-green shadow-[0_0_10px_hsl(var(--neon-green)/0.5)]",
  orange: "bg-neon-orange shadow-[0_0_10px_hsl(var(--neon-orange)/0.5)]",
};

const AnimatedSlider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  AnimatedSliderProps
>(({ 
  className, 
  showValue = true,
  lowLabel,
  highLabel,
  icon,
  valueFormatter,
  glowColor = "cyan",
  value,
  ...props 
}, ref) => {
  const currentValue = value?.[0] ?? 0;
  const displayValue = valueFormatter ? valueFormatter(currentValue) : currentValue;

  return (
    <div className="space-y-3">
      <SliderPrimitive.Root
        ref={ref}
        className={cn(
          "relative flex w-full touch-none select-none items-center group",
          className
        )}
        value={value}
        {...props}
      >
        <SliderPrimitive.Track className="relative h-3 w-full grow overflow-hidden rounded-full bg-muted/50 border border-border/50">
          <SliderPrimitive.Range 
            className={cn(
              "absolute h-full transition-all duration-200",
              "bg-gradient-to-r from-primary/80 to-primary",
              glowColors[glowColor]
            )} 
          />
          {/* Tick marks */}
          <div className="absolute inset-0 flex items-center justify-between px-1 pointer-events-none">
            {[0, 25, 50, 75, 100].map((tick) => (
              <div 
                key={tick}
                className={cn(
                  "w-0.5 h-2 rounded-full transition-colors",
                  currentValue >= tick ? "bg-primary-foreground/30" : "bg-muted-foreground/20"
                )}
              />
            ))}
          </div>
        </SliderPrimitive.Track>
        <SliderPrimitive.Thumb 
          className={cn(
            "block h-6 w-6 rounded-full border-2 border-primary bg-background",
            "ring-offset-background transition-all duration-200",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            "disabled:pointer-events-none disabled:opacity-50",
            "hover:scale-110 hover:border-primary",
            "group-hover:shadow-[0_0_15px_hsl(var(--primary)/0.5)]",
            "cursor-grab active:cursor-grabbing active:scale-95"
          )}
        >
          {/* Inner glow */}
          <div className={cn(
            "absolute inset-1 rounded-full",
            glowColors[glowColor],
            "opacity-60"
          )} />
        </SliderPrimitive.Thumb>
      </SliderPrimitive.Root>

      {/* Labels */}
      {(lowLabel || highLabel) && (
        <div className="flex justify-between items-center">
          <span className={cn(
            "text-xs transition-colors",
            currentValue < 33 ? "text-primary font-medium" : "text-muted-foreground"
          )}>
            {lowLabel}
          </span>
          {showValue && (
            <span className={cn(
              "text-sm font-medium px-3 py-1 rounded-full",
              "bg-primary/10 text-primary border border-primary/20"
            )}>
              {displayValue}
            </span>
          )}
          <span className={cn(
            "text-xs transition-colors",
            currentValue > 66 ? "text-primary font-medium" : "text-muted-foreground"
          )}>
            {highLabel}
          </span>
        </div>
      )}
    </div>
  );
});

AnimatedSlider.displayName = "AnimatedSlider";

export { AnimatedSlider };
