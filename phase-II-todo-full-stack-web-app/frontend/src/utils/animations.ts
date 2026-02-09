/**
 * Animation Utilities
 *
 * Centralized animation timing and easing functions
 * Follows UX animation design system specifications
 */

/**
 * Animation Timing Standards
 * Based on UX specifications for consistent animation feel
 */
export const ANIMATION_TIMING = {
  // Quick interactions (100-200ms)
  quick: {
    duration: 150,
    css: '150ms',
  },
  // Moderate transitions (200-400ms)
  moderate: {
    duration: 300,
    css: '300ms',
  },
  // Extended animations (400-600ms)
  extended: {
    duration: 500,
    css: '500ms',
  },
  // Delayed feedback (600-1000ms)
  delayed: {
    duration: 800,
    css: '800ms',
  },
} as const;

/**
 * Easing Functions
 * Standard easing curves for different animation types
 */
export const EASING = {
  // Standard ease for most transitions
  standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
  // Accelerate for exit animations
  accelerate: 'cubic-bezier(0.4, 0, 1, 1)',
  // Decelerate for entrance animations
  decelerate: 'cubic-bezier(0, 0, 0.2, 1)',
  // Sharp for quick interactions
  sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
  // Bounce for playful interactions
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  // Smooth for elegant transitions
  smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
} as const;

/**
 * Animation Classes
 * Tailwind-compatible animation class names
 */
export const ANIMATION_CLASSES = {
  fadeIn: 'animate-fade-in',
  fadeOut: 'animate-fade-out',
  slideIn: 'animate-slide-in',
  slideOut: 'animate-slide-out',
  scaleIn: 'animate-scale-in',
  scaleOut: 'animate-scale-out',
  bounceSubtle: 'animate-bounce-subtle',
  pulseSubtle: 'animate-pulse-subtle',
} as const;

/**
 * Get animation delay for staggered animations
 * @param index - Item index in list
 * @param baseDelay - Base delay in milliseconds (default: 50ms)
 * @returns CSS delay string
 */
export function getStaggerDelay(index: number, baseDelay: number = 50): string {
  return `${index * baseDelay}ms`;
}

/**
 * Get animation duration based on distance
 * Longer distances = longer animations for natural feel
 * @param distance - Distance in pixels
 * @returns Duration in milliseconds
 */
export function getDistanceBasedDuration(distance: number): number {
  const minDuration = ANIMATION_TIMING.quick.duration;
  const maxDuration = ANIMATION_TIMING.extended.duration;
  const scaleFactor = 0.5; // Adjust sensitivity

  const duration = minDuration + (distance * scaleFactor);
  return Math.min(Math.max(duration, minDuration), maxDuration);
}

/**
 * Check if animations should be reduced
 * Respects user's prefers-reduced-motion setting
 * @returns boolean indicating if motion should be reduced
 */
export function shouldReduceMotion(): boolean {
  if (typeof window === 'undefined') return false;

  const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  return mediaQuery.matches;
}

/**
 * Get animation config with reduced motion support
 * @param normalConfig - Normal animation configuration
 * @param reducedConfig - Reduced motion configuration (optional)
 * @returns Appropriate configuration based on user preference
 */
export function getAnimationConfig<T>(
  normalConfig: T,
  reducedConfig?: Partial<T>
): T {
  if (shouldReduceMotion() && reducedConfig) {
    return { ...normalConfig, ...reducedConfig };
  }
  return normalConfig;
}

/**
 * Spring Animation Presets
 * For use with animation libraries like Framer Motion
 */
export const SPRING_PRESETS = {
  // Gentle spring for subtle movements
  gentle: {
    type: 'spring',
    stiffness: 120,
    damping: 14,
  },
  // Bouncy spring for playful interactions
  bouncy: {
    type: 'spring',
    stiffness: 300,
    damping: 10,
  },
  // Stiff spring for quick, responsive feel
  stiff: {
    type: 'spring',
    stiffness: 400,
    damping: 30,
  },
  // Slow spring for dramatic effect
  slow: {
    type: 'spring',
    stiffness: 80,
    damping: 20,
  },
} as const;

/**
 * Transition Presets
 * For use with CSS transitions or animation libraries
 */
export const TRANSITION_PRESETS = {
  // Default transition for most elements
  default: {
    duration: ANIMATION_TIMING.moderate.duration / 1000,
    ease: EASING.standard,
  },
  // Fast transition for immediate feedback
  fast: {
    duration: ANIMATION_TIMING.quick.duration / 1000,
    ease: EASING.sharp,
  },
  // Slow transition for emphasis
  slow: {
    duration: ANIMATION_TIMING.extended.duration / 1000,
    ease: EASING.smooth,
  },
  // Bounce transition for playful feel
  bounce: {
    duration: ANIMATION_TIMING.moderate.duration / 1000,
    ease: EASING.bounce,
  },
} as const;
