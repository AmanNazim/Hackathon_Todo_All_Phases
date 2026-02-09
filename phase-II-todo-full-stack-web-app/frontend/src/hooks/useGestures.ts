/**
 * useGestures Hook
 *
 * React hook for handling touch gestures
 * Supports swipe, long press, and tap gestures
 */

'use client';

import { useRef, useEffect, RefObject } from 'react';
import { createGestureHandlers, GestureHandlers } from '@/utils/gestures';

export function useGestures(
  ref: RefObject<HTMLElement>,
  handlers: GestureHandlers,
  enabled: boolean = true
) {
  const gestureHandlersRef = useRef(createGestureHandlers(handlers));

  useEffect(() => {
    // Update handlers when they change
    gestureHandlersRef.current = createGestureHandlers(handlers);
  }, [handlers]);

  useEffect(() => {
    const element = ref.current;
    if (!element || !enabled) return;

    const gestureHandlers = gestureHandlersRef.current;

    // Add touch event listeners
    element.addEventListener('touchstart', gestureHandlers.onTouchStart as EventListener);
    element.addEventListener('touchmove', gestureHandlers.onTouchMove as EventListener);
    element.addEventListener('touchend', gestureHandlers.onTouchEnd as EventListener);
    element.addEventListener('touchcancel', gestureHandlers.onTouchCancel as EventListener);

    return () => {
      // Cleanup
      element.removeEventListener('touchstart', gestureHandlers.onTouchStart as EventListener);
      element.removeEventListener('touchmove', gestureHandlers.onTouchMove as EventListener);
      element.removeEventListener('touchend', gestureHandlers.onTouchEnd as EventListener);
      element.removeEventListener('touchcancel', gestureHandlers.onTouchCancel as EventListener);
    };
  }, [ref, enabled]);
}
