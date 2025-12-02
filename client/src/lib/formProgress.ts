/**
 * Utility functions for managing feedback form progress in localStorage
 */

const FORM_PROGRESS_PREFIX = 'feedback_progress_';

export interface FormProgressData {
  currentStep: number;
  totalSteps: number;
  formData: Record<string, any>;
  lastUpdated: string;
}

/**
 * Save form progress for a specific course
 */
export function saveFormProgress(courseId: string, progressData: FormProgressData): void {
  try {
    const key = `${FORM_PROGRESS_PREFIX}${courseId}`;
    localStorage.setItem(key, JSON.stringify(progressData));
    
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent('feedbackUpdated', { detail: { courseId } }));
  } catch (error) {
    console.error('Error saving form progress:', error);
  }
}

/**
 * Get form progress for a specific course
 */
export function getFormProgress(courseId: string): FormProgressData | null {
  try {
    const key = `${FORM_PROGRESS_PREFIX}${courseId}`;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Error getting form progress:', error);
    return null;
  }
}

/**
 * Calculate progress percentage for a specific course based on answered questions
 */
export function getFormProgressForCourse(courseId: string): number {
  const progress = getFormProgress(courseId);
  
  if (!progress || !progress.formData) {
    return 0;
  }

  // Count total questions and answered questions
  let totalQuestions = 0;
  let answeredQuestions = 0;

  const formData = progress.formData;
  
  // Helper function to check if a value is answered
  const isAnswered = (value: any): boolean => {
    if (typeof value === 'number') {
      return value > 0; // Rating must be > 0
    }
    if (typeof value === 'boolean') {
      return true; // Boolean values are always answered (true/false)
    }
    if (value === null) {
      return false; // Null means not answered
    }
    if (typeof value === 'string') {
      return value.trim().length > 0; // String must not be empty
    }
    return false;
  };

  // Iterate through all sections of the form
  Object.keys(formData).forEach(sectionKey => {
    const section = formData[sectionKey as keyof typeof formData];
    
    // Skip non-object values
    if (typeof section !== 'object' || section === null) {
      return;
    }

    // Count questions in this section
    Object.values(section).forEach(value => {
      totalQuestions++;
      if (isAnswered(value)) {
        answeredQuestions++;
      }
    });
  });

  // Calculate percentage
  if (totalQuestions === 0) {
    return 0;
  }

  const percentage = Math.round((answeredQuestions / totalQuestions) * 100);
  return Math.min(percentage, 100);
}

/**
 * Clear form progress for a specific course
 */
export function clearFormProgress(courseId: string): void {
  try {
    const key = `${FORM_PROGRESS_PREFIX}${courseId}`;
    localStorage.removeItem(key);
    
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent('feedbackUpdated', { detail: { courseId } }));
  } catch (error) {
    console.error('Error clearing form progress:', error);
  }
}

/**
 * Get all courses with saved progress
 */
export function getAllCoursesWithProgress(): string[] {
  try {
    const courseIds: string[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(FORM_PROGRESS_PREFIX)) {
        const courseId = key.replace(FORM_PROGRESS_PREFIX, '');
        courseIds.push(courseId);
      }
    }
    
    return courseIds;
  } catch (error) {
    console.error('Error getting courses with progress:', error);
    return [];
  }
}

/**
 * Clear all form progress (useful for logout or reset)
 */
export function clearAllFormProgress(): void {
  try {
    const keys: string[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(FORM_PROGRESS_PREFIX)) {
        keys.push(key);
      }
    }
    
    keys.forEach(key => localStorage.removeItem(key));
    
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent('feedbackUpdated', { detail: { cleared: true } }));
  } catch (error) {
    console.error('Error clearing all form progress:', error);
  }
}
