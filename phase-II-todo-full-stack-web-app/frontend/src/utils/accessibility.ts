/**
 * Accessibility Utilities
 *
 * Helper functions for implementing WCAG 2.1 AA accessibility standards
 * Includes ARIA helpers, focus management, and screen reader utilities
 */

/**
 * ARIA Live Region Politeness Levels
 */
export type AriaLive = 'off' | 'polite' | 'assertive';

/**
 * ARIA Role Types
 */
export type AriaRole =
  | 'alert'
  | 'alertdialog'
  | 'button'
  | 'checkbox'
  | 'dialog'
  | 'gridcell'
  | 'link'
  | 'log'
  | 'marquee'
  | 'menuitem'
  | 'menuitemcheckbox'
  | 'menuitemradio'
  | 'option'
  | 'progressbar'
  | 'radio'
  | 'scrollbar'
  | 'searchbox'
  | 'slider'
  | 'spinbutton'
  | 'status'
  | 'switch'
  | 'tab'
  | 'tabpanel'
  | 'textbox'
  | 'timer'
  | 'tooltip'
  | 'treeitem';

/**
 * Generate unique ID for accessibility attributes
 * @param prefix - Prefix for the ID
 * @returns Unique ID string
 */
export function generateA11yId(prefix: string = 'a11y'): string {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Create ARIA label attributes
 * @param label - Label text
 * @param describedBy - Optional ID of describing element
 * @returns Object with ARIA attributes
 */
export function createAriaLabel(label: string, describedBy?: string) {
  return {
    'aria-label': label,
    ...(describedBy && { 'aria-describedby': describedBy }),
  };
}

/**
 * Create ARIA live region attributes
 * @param politeness - Politeness level
 * @param atomic - Whether to read entire region
 * @returns Object with ARIA attributes
 */
export function createAriaLiveRegion(
  politeness: AriaLive = 'polite',
  atomic: boolean = true
) {
  return {
    'aria-live': politeness,
    'aria-atomic': atomic,
  };
}

/**
 * Create ARIA expanded attributes for collapsible elements
 * @param isExpanded - Whether element is expanded
 * @param controls - ID of controlled element
 * @returns Object with ARIA attributes
 */
export function createAriaExpanded(isExpanded: boolean, controls?: string) {
  return {
    'aria-expanded': isExpanded,
    ...(controls && { 'aria-controls': controls }),
  };
}

/**
 * Create ARIA pressed attributes for toggle buttons
 * @param isPressed - Whether button is pressed
 * @returns Object with ARIA attributes
 */
export function createAriaPressed(isPressed: boolean) {
  return {
    'aria-pressed': isPressed,
  };
}

/**
 * Create ARIA checked attributes for checkboxes and radio buttons
 * @param isChecked - Whether element is checked
 * @returns Object with ARIA attributes
 */
export function createAriaChecked(isChecked: boolean) {
  return {
    'aria-checked': isChecked,
  };
}

/**
 * Create ARIA selected attributes for selectable items
 * @param isSelected - Whether element is selected
 * @returns Object with ARIA attributes
 */
export function createAriaSelected(isSelected: boolean) {
  return {
    'aria-selected': isSelected,
  };
}

/**
 * Create ARIA disabled attributes
 * @param isDisabled - Whether element is disabled
 * @returns Object with ARIA attributes
 */
export function createAriaDisabled(isDisabled: boolean) {
  return {
    'aria-disabled': isDisabled,
  };
}

/**
 * Create ARIA invalid attributes for form validation
 * @param isInvalid - Whether element has validation error
 * @param errorId - ID of error message element
 * @returns Object with ARIA attributes
 */
export function createAriaInvalid(isInvalid: boolean, errorId?: string) {
  return {
    'aria-invalid': isInvalid,
    ...(isInvalid && errorId && { 'aria-describedby': errorId }),
  };
}

/**
 * Create ARIA required attributes for form fields
 * @param isRequired - Whether field is required
 * @returns Object with ARIA attributes
 */
export function createAriaRequired(isRequired: boolean) {
  return {
    'aria-required': isRequired,
  };
}

/**
 * Announce message to screen readers
 * Creates a temporary live region to announce a message
 * @param message - Message to announce
 * @param politeness - Politeness level
 */
export function announceToScreenReader(
  message: string,
  politeness: AriaLive = 'polite'
) {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', politeness);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

/**
 * Focus Management Utilities
 */

/**
 * Get all focusable elements within a container
 * @param container - Container element
 * @returns Array of focusable elements
 */
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const selector =
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

  return Array.from(container.querySelectorAll<HTMLElement>(selector));
}

/**
 * Focus first focusable element in container
 * @param container - Container element
 * @returns boolean indicating if focus was successful
 */
export function focusFirstElement(container: HTMLElement): boolean {
  const focusable = getFocusableElements(container);
  if (focusable.length > 0) {
    focusable[0].focus();
    return true;
  }
  return false;
}

/**
 * Focus last focusable element in container
 * @param container - Container element
 * @returns boolean indicating if focus was successful
 */
export function focusLastElement(container: HTMLElement): boolean {
  const focusable = getFocusableElements(container);
  if (focusable.length > 0) {
    focusable[focusable.length - 1].focus();
    return true;
  }
  return false;
}

/**
 * Restore focus to previously focused element
 * @param previousElement - Element to restore focus to
 */
export function restoreFocus(previousElement: HTMLElement | null) {
  if (previousElement && document.body.contains(previousElement)) {
    previousElement.focus();
  }
}

/**
 * Screen Reader Only CSS Class
 * Visually hidden but accessible to screen readers
 */
export const SR_ONLY_CLASS = 'sr-only';

/**
 * Get screen reader only styles
 * @returns CSS-in-JS object for screen reader only content
 */
export function getSrOnlyStyles() {
  return {
    position: 'absolute' as const,
    width: '1px',
    height: '1px',
    padding: '0',
    margin: '-1px',
    overflow: 'hidden',
    clip: 'rect(0, 0, 0, 0)',
    whiteSpace: 'nowrap' as const,
    borderWidth: '0',
  };
}

/**
 * Color Contrast Utilities
 */

/**
 * Calculate relative luminance of a color
 * @param r - Red value (0-255)
 * @param g - Green value (0-255)
 * @param b - Blue value (0-255)
 * @returns Relative luminance (0-1)
 */
export function getRelativeLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const sRGB = c / 255;
    return sRGB <= 0.03928 ? sRGB / 12.92 : Math.pow((sRGB + 0.055) / 1.055, 2.4);
  });

  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

/**
 * Calculate contrast ratio between two colors
 * @param l1 - Luminance of first color
 * @param l2 - Luminance of second color
 * @returns Contrast ratio (1-21)
 */
export function getContrastRatio(l1: number, l2: number): number {
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Check if contrast ratio meets WCAG AA standards
 * @param ratio - Contrast ratio
 * @param isLargeText - Whether text is large (18pt+ or 14pt+ bold)
 * @returns boolean indicating if meets standards
 */
export function meetsWCAGAA(ratio: number, isLargeText: boolean = false): boolean {
  return isLargeText ? ratio >= 3 : ratio >= 4.5;
}

/**
 * Check if contrast ratio meets WCAG AAA standards
 * @param ratio - Contrast ratio
 * @param isLargeText - Whether text is large (18pt+ or 14pt+ bold)
 * @returns boolean indicating if meets standards
 */
export function meetsWCAGAAA(ratio: number, isLargeText: boolean = false): boolean {
  return isLargeText ? ratio >= 4.5 : ratio >= 7;
}
