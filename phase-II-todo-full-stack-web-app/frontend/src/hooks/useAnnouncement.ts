/**
 * useAnnouncement Hook
 *
 * Hook for announcing messages to screen readers
 * Manages announcement queue and timing
 */

'use client';

import { useCallback, useRef } from 'react';
import { announceToScreenReader, AriaLive } from '@/utils/accessibility';

export function useAnnouncement() {
  const queueRef = useRef<Array<{ message: string; politeness: AriaLive }>>([]);
  const isAnnouncingRef = useRef(false);

  const processQueue = useCallback(() => {
    if (isAnnouncingRef.current || queueRef.current.length === 0) {
      return;
    }

    isAnnouncingRef.current = true;
    const { message, politeness } = queueRef.current.shift()!;

    announceToScreenReader(message, politeness);

    // Wait before processing next announcement
    setTimeout(() => {
      isAnnouncingRef.current = false;
      processQueue();
    }, 1000);
  }, []);

  const announce = useCallback(
    (message: string, politeness: AriaLive = 'polite') => {
      queueRef.current.push({ message, politeness });
      processQueue();
    },
    [processQueue]
  );

  return { announce };
}
