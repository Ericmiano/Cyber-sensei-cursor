import { useEffect, useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { useTutorial } from "@/contexts/TutorialContext";
import { useSwipeGesture } from "@/hooks/use-swipe-gesture";
import TutorialCard from "./TutorialCard";

export default function TutorialOverlay() {
  const {
    isActive,
    currentStep,
    steps,
    currentStepData,
    nextStep,
    prevStep,
    skipTutorial,
    endTutorial,
  } = useTutorial();

  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  // Swipe gesture support for mobile
  const { bind } = useSwipeGesture({
    onSwipeLeft: nextStep,
    onSwipeRight: prevStep,
    enabled: isActive,
    threshold: 50,
  });

  // Attach swipe gestures
  useEffect(() => {
    if (overlayRef.current && isActive) {
      return bind(overlayRef.current);
    }
  }, [bind, isActive]);

  // Find and highlight target element
  useEffect(() => {
    if (!isActive || !currentStepData?.targetSelector) {
      setTargetRect(null);
      return;
    }

    const findTarget = () => {
      const target = document.querySelector(currentStepData.targetSelector!);
      if (target) {
        setTargetRect(target.getBoundingClientRect());
      } else {
        setTargetRect(null);
      }
    };

    findTarget();
    window.addEventListener("resize", findTarget);
    window.addEventListener("scroll", findTarget);

    return () => {
      window.removeEventListener("resize", findTarget);
      window.removeEventListener("scroll", findTarget);
    };
  }, [isActive, currentStepData]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isActive) return;
      if (e.key === "Escape") skipTutorial();
      if (e.key === "ArrowRight" || e.key === "Enter") nextStep();
      if (e.key === "ArrowLeft") prevStep();
    },
    [isActive, nextStep, prevStep, skipTutorial]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  if (!isActive || !currentStepData) return null;

  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;
  // Force center if card would overflow viewport (e.g. sidebar is too tall)
  const wouldOverflow = targetRect && (targetRect.bottom + 300 > window.innerHeight);
  const isCentered = currentStepData.placement === "center" || !targetRect || wouldOverflow;

  return (
    <AnimatePresence>
      <div 
        ref={overlayRef}
        className="fixed inset-0 z-[100] pointer-events-none touch-pan-y"
      >
        {/* Backdrop overlay */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-background/80 backdrop-blur-sm pointer-events-auto"
          onClick={skipTutorial}
        />

        {/* Highlight cutout for target element */}
        {targetRect && currentStepData.highlight && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute pointer-events-none"
            style={{
              top: targetRect.top - 6,
              left: targetRect.left - 6,
              width: targetRect.width + 12,
              height: targetRect.height + 12,
              boxShadow: "0 0 0 9999px rgba(0, 0, 0, 0.75)",
              borderRadius: "8px",
              border: "2px solid hsl(var(--primary))",
            }}
          >
            <div className="absolute inset-0 rounded-lg animate-pulse-glow" />
          </motion.div>
        )}

        {/* Tutorial tooltip card - centered container */}
        {isCentered ? (
          <div className="absolute inset-0 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="pointer-events-auto w-full max-w-sm"
            >
              <TutorialCard
                step={currentStepData}
                currentStep={currentStep}
                totalSteps={steps.length}
                onNext={nextStep}
                onPrev={prevStep}
                onSkip={skipTutorial}
                onEnd={endTutorial}
                isFirstStep={isFirstStep}
                isLastStep={isLastStep}
              />
            </motion.div>
          </div>
        ) : (
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="pointer-events-auto fixed p-4"
            style={{
              top: targetRect ? targetRect.bottom + 12 : "50%",
              left: window.innerWidth < 640 ? "50%" : (targetRect?.left ?? 0),
              transform: window.innerWidth < 640 ? "translateX(-50%)" : undefined,
              maxWidth: "calc(100vw - 2rem)",
            }}
          >
            <TutorialCard
              step={currentStepData}
              currentStep={currentStep}
              totalSteps={steps.length}
              onNext={nextStep}
              onPrev={prevStep}
              onSkip={skipTutorial}
              onEnd={endTutorial}
              isFirstStep={isFirstStep}
              isLastStep={isLastStep}
            />
          </motion.div>
        )}
      </div>
    </AnimatePresence>
  );
}
