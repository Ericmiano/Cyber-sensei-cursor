import { useRef, useCallback, useEffect, useState } from "react";

interface SwipeConfig {
  threshold?: number;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  enabled?: boolean;
}

interface SwipeState {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  swiping: boolean;
}

export function useSwipeGesture({
  threshold = 50,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  enabled = true,
}: SwipeConfig) {
  const [swipeDirection, setSwipeDirection] = useState<string | null>(null);
  const stateRef = useRef<SwipeState>({
    startX: 0,
    startY: 0,
    endX: 0,
    endY: 0,
    swiping: false,
  });

  const handleTouchStart = useCallback(
    (e: TouchEvent) => {
      if (!enabled) return;
      const touch = e.touches[0];
      stateRef.current = {
        ...stateRef.current,
        startX: touch.clientX,
        startY: touch.clientY,
        swiping: true,
      };
    },
    [enabled]
  );

  const handleTouchMove = useCallback(
    (e: TouchEvent) => {
      if (!enabled || !stateRef.current.swiping) return;
      const touch = e.touches[0];
      stateRef.current.endX = touch.clientX;
      stateRef.current.endY = touch.clientY;
    },
    [enabled]
  );

  const handleTouchEnd = useCallback(() => {
    if (!enabled || !stateRef.current.swiping) return;

    const { startX, startY, endX, endY } = stateRef.current;
    const deltaX = endX - startX;
    const deltaY = endY - startY;
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);

    stateRef.current.swiping = false;

    // Determine if it's a horizontal or vertical swipe
    if (absDeltaX > absDeltaY && absDeltaX > threshold) {
      if (deltaX > 0) {
        setSwipeDirection("right");
        onSwipeRight?.();
      } else {
        setSwipeDirection("left");
        onSwipeLeft?.();
      }
    } else if (absDeltaY > absDeltaX && absDeltaY > threshold) {
      if (deltaY > 0) {
        setSwipeDirection("down");
        onSwipeDown?.();
      } else {
        setSwipeDirection("up");
        onSwipeUp?.();
      }
    }

    // Reset direction after a short delay
    setTimeout(() => setSwipeDirection(null), 300);
  }, [enabled, threshold, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown]);

  const bind = useCallback(
    (element: HTMLElement | null) => {
      if (!element) return;

      element.addEventListener("touchstart", handleTouchStart, { passive: true });
      element.addEventListener("touchmove", handleTouchMove, { passive: true });
      element.addEventListener("touchend", handleTouchEnd);

      return () => {
        element.removeEventListener("touchstart", handleTouchStart);
        element.removeEventListener("touchmove", handleTouchMove);
        element.removeEventListener("touchend", handleTouchEnd);
      };
    },
    [handleTouchStart, handleTouchMove, handleTouchEnd]
  );

  return { bind, swipeDirection };
}

// Hook version that attaches to window for global swipe detection
export function useGlobalSwipeGesture(config: SwipeConfig) {
  const { bind } = useSwipeGesture(config);

  useEffect(() => {
    const cleanup = bind(document.body);
    return cleanup;
  }, [bind]);
}
