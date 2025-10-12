export interface Course {
  id: string;
  code: string;
  name: string;
  description?: string;
  instructor?: string;
  instructorId?: string;
  section?: string;
  semester: string;
  hasSubmittedFeedback: boolean;
  progress?: number;
  dueDate?: string;
  tag?: 'Student' | 'Recommended' | 'Popular';
  color?: 'pink' | 'blue' | 'yellow' | 'green';
  // Deprecated fields - kept for backward compatibility
  modules?: {
    completed: number;
    total: number;
  };
  tasks?: number;
  projects?: number;
  startDate?: string;
  avatar?: string;
}

export interface FeedbackQuestion {
  id: string;
  question: string;
  type: 'text' | 'rating' | 'multiple-choice';
  required: boolean;
  options?: string[];
}

export interface FeedbackSubmission {
  courseId: string;
  answers: Record<string, string | number>;
  submittedAt: string;
}
