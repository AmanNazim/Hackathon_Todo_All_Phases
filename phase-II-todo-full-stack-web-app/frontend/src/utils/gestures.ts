/**
 * Gesture Utilities
 *
 * Touch gesture detection and handling for mobile UX
 * Supports swipe, long press, and tap gestures
 */

export interface SwipeGesture {
  direction: 'left' | 'right' | 'up' | 'down';
  distance: number;
  velocity: number;
  duration: number;
}

export interface TouchPosition {
  x: number;
  y: number;
  timestamp: number;
}

/**
 * Swipe Detection Configuration
 */
export const SWIPE_CONFIG = {
  minDistance: 50, // Minimum distance in pixels to register as swipe
  maxDuration: 500, // Maximum duration in ms for swipe
  minVelocity: 0.3, // Minimum velocity (pixels/ms)
} as const;

/**
 * Long Press Configuration
 */
export const LONG_PRESS_CONFIG = {
  duration: 500, // Duration in ms to trigger long press
  movementThreshold: 10, // Max movement in pixels before canceling
} as const;

/**
 * Detect swipe gesture from touch events
 * @param startPos - Starting touch position
 * @param endPos - Ending touch position
 * @returns SwipeGesture object or null if not a valid swipe
 */
export function detectSwipe(
  startPos: TouchPosition,
  endPos: TouchPosition
): SwipeGesture | null {
  const deltaX = endPos.x - startPos.x;
  const deltaY = endPos.y - startPos.y;
  const duration = endPos.timestamp - startPos.timestamp;

  // Calculate distance and velocity
  const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
  const velocity = distance / duration;

  // Check if meets minimum requirements
  if (
    distance < SWIPE_CONFIG.minDistance ||
    duration > SWIPE_CONFIG.maxDuration ||
    velocity < SWIPE_CONFIG.minVelocity
  ) {
    return null;
  }

  // Determine direction (prioritize horizontal or vertical)
  const absX = Math.abs(deltaX);
  const absY = Math.abs(deltaY);

  let direction: SwipeGesture['direction'];
  if (absX > absY) {
    direction = deltaX > 0 ? 'right' : 'left';
  } else {
    direction = deltaY > 0 ? 'down' : 'up';
  }

  return {
    direction,
    distance,
    velocity,
    duration,
  };
}

/**
 * Create touch position from touch event
 * @param touch - Touch object from event
 * @returns TouchPosition object
 */
export function getTouchPosition(touch: Touch): TouchPosition {
  return {
    x: touch.clientX,
    y: touch.clientY,
    timestamp: Date.now(),
  };
}

/**
 * Calculate distance between two touch positions
 * @param pos1 - First position
 * @param pos2 - Second position
 * @returns Distance in pixels
 */
export function getTouchDistance(pos1: TouchPosition, pos2: TouchPosition): number {
  const deltaX = pos2.x - pos1.x;
  const deltaY = pos2.y - pos1.y;
  return Math.sqrt(deltaX * deltaX + deltaY * deltaY);
}

/**
 * Check if touch movement is within threshold
 * @param startPos - Starting position
 * @param currentPos - Current position
 * @param threshold - Maximum allowed movement
 * @returns boolean indicating if within threshold
 */
export function isWithinMovementThreshold(
  startPos: TouchPosition,
  currentPos: TouchPosition,
  threshold: number = LONG_PRESS_CONFIG.movementThreshold
): boolean {
  const distance = getTouchDistance(startPos, currentPos);
  return distance <= threshold;
}

/**
 * Gesture Event Handlers
 * Helper functions to attach gesture handlers to elements
 */

export interface GestureHandlers {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onLongPress?: () => void;
  onTap?: () => void;
}

/**
 * Create gesture event handlers for an element
 * @param handlers - Gesture callback functions
 * @returns Object with touch event handlers
 */
export function createGestureHandlers(handlers: GestureHandlers) {
  let startPos: TouchPosition | null = null;
  let longPressTimer: NodeJS.Timeout | null = null;

  const handleTouchStart = (event: TouchEvent) => {
    const touch = event.touches[0];
    startPos = getTouchPosition(touch);

    // Start long press timer
    if (handlers.onLongPress) {
      longPressTimer = setTimeout(() => {
        if (startPos && handlers.onLongPress) {
          handlers.onLongPress();
          startPos = null; // Prevent swipe after long press
        }
      }, LONG_PRESS_CONFIG.duration);
    }
  };

  const handleTouchMove = (event: TouchEvent) => {
    if (!startPos || !longPressTimer) return;

    const touch = event.touches[0];
    const currentPos = getTouchPosition(touch);

    // Cancel long press if moved too much
    if (!isWithinMovementThreshold(startPos, currentPos)) {
      clearTimeout(longPressTimer);
      longPressTimer = null;
    }
  };

  const handleTouchEnd = (event: TouchEvent) => {
    // Clear long press timer
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      longPressTimer = null;
    }

    if (!startPos) return;

    const touch = event.changedTouches[0];
    const endPos = getTouchPosition(touch);

    // Detect swipe
    const swipe = detectSwipe(startPos, endPos);
    if (swipe) {
      switch (swipe.direction) {
        case 'left':
          handlers.onSwipeLeft?.();
          break;
        case 'right':
          handlers.onSwipeRight?.();
          break;
        case 'up':
          handlers.onSwipeUp?.();
          break;
        case 'down':
          handlers.onSwipeDown?.();
          break;
      }
    } else {
      // If not a swipe, consider it a tap
      const distance = getTouchDistance(startPos, endPos);
      if (distance < LONG_PRESS_CONFIG.movementThreshold) {
        handlers.onTap?.();
      }
    }

    startPos = null;
  };

  const handleTouchCancel = () => {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      longPressTimer = null;
    }
    startPos = null;
  };

  return {
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd,
    onTouchCancel: handleTouchCancel,
  };
}
