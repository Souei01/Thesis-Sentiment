/**
 * Sanitize text input to prevent XSS attacks
 * This is a client-side validation layer. Server-side validation is the primary defense.
 */

/**
 * Sanitize text input by removing potentially dangerous characters
 * @param text - Input text to sanitize
 * @param maxLength - Maximum allowed length
 * @returns Sanitized text
 */
export function sanitizeTextInput(text: string, maxLength: number = 2000): string {
  if (!text) return '';
  
  // Convert to string and trim
  let sanitized = String(text).trim();
  
  // Enforce maximum length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }
  
  // Remove null bytes
  sanitized = sanitized.replace(/\0/g, '');
  
  // Remove script tags and event handlers (basic filter)
  // The server will do more comprehensive escaping
  sanitized = sanitized.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  sanitized = sanitized.replace(/on\w+\s*=\s*["'][^"']*["']/gi, '');
  
  return sanitized;
}

/**
 * Validate that text is not just placeholder content
 * @param text - Text to validate
 * @returns true if text is meaningful
 */
export function isMeaningfulText(text: string): boolean {
  if (!text) return false;
  
  const trimmed = text.trim().toLowerCase();
  
  // Check for common placeholder responses
  const placeholders = ['n/a', 'na', 'none', 'nothing', '.', '-', 'no comment', 'no comments'];
  
  return trimmed.length > 2 && !placeholders.includes(trimmed);
}

/**
 * Validate feedback form comments
 * @param comments - Comments object from form
 * @returns Object with validation result and message
 */
export function validateFeedbackComments(comments: {
  recommendedChanges: string;
  likeBest: string;
  likeLeast: string;
  additionalComments: string;
}): { valid: boolean; message?: string } {
  const meaningfulComments = [
    comments.recommendedChanges,
    comments.likeBest,
    comments.likeLeast,
    comments.additionalComments
  ].filter(isMeaningfulText);
  
  if (meaningfulComments.length === 0) {
    return {
      valid: false,
      message: 'Please provide at least one meaningful comment. Avoid responses like "N/A", "none", or "."'
    };
  }
  
  return { valid: true };
}
