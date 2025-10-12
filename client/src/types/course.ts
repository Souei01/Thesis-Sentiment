export interface Course {
  id: string;
  code: string;
  name: string;
  description?: string;
  instructor?: string;
  semester: string;
  hasSubmittedFeedback: boolean;
  modules?: {
    completed: number;
    total: number;
  };
  tasks?: number;
  projects?: number;
  progress?: number;
  startDate?: string;
  tag?: 'Student' | 'Recommended' | 'Popular';
  color?: 'pink' | 'blue' | 'yellow' | 'green';
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
