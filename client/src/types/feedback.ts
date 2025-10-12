export interface FeedbackFormData {
  // A. Commitment (1-5 rating)
  commitment: {
    sensitivity: number;
    integration: number;
    availability: number;
    punctuality: number;
    recordKeeping: number;
  };
  
  // B. Knowledge of Subject (1-5 rating)
  knowledgeOfSubject: {
    mastery: number;
    stateOfArt: number;
    practicalIntegration: number;
    relevance: number;
    currentTrends: number;
  };
  
  // C. Teaching for Independent Learning (1-5 rating)
  independentLearning: {
    teachingStrategies: number;
    studentEsteem: number;
    studentAutonomy: number;
    independentThinking: number;
    beyondRequired: number;
  };
  
  // D. Management of Learning (1-5 rating)
  managementOfLearning: {
    studentContribution: number;
    facilitatorRole: number;
    discussionEncouragement: number;
    instructionalMethods: number;
    instructionalMaterials: number;
  };
  
  // E. Feedback and Assessment (1-5 rating)
  feedbackAssessment: {
    clearCommunication: number;
    timelyFeedback: number;
    improvementFeedback: number;
  };
  
  // F. Other Questions (yes/no)
  otherQuestions: {
    syllabusExplained: boolean | null;
    deliveredAsOutlined: boolean | null;
    gradingCriteriaExplained: boolean | null;
    examsRelated: boolean | null;
    assignmentsRelated: boolean | null;
    lmsResourcesUseful: boolean | null;
  };
  
  // G. Overall Experience
  overallExperience: {
    worthwhileClass: boolean | null;
    wouldRecommend: boolean | null;
    hoursPerWeek: number;
    overallRating: number;
  };
  
  // H. Student Evaluation (1-5 rating)
  studentEvaluation: {
    constructiveContribution: number;
    achievingOutcomes: number;
  };
  
  // I. Comments
  comments: {
    recommendedChanges: string;
    likeBest: string;
    likeLeast: string;
    additionalComments: string;
  };
  
  // Metadata
  courseId: string;
  currentStep: number;
  completedAt?: Date;
}

export const RATING_LABELS = {
  1: 'Poor',
  2: 'Fair',
  3: 'Satisfactory',
  4: 'Very Satisfactory',
  5: 'Outstanding'
};

export const FORM_STEPS = [
  { id: 1, title: 'Commitment', key: 'commitment' },
  { id: 2, title: 'Knowledge', key: 'knowledgeOfSubject' },
  { id: 3, title: 'Teaching', key: 'independentLearning' },
  { id: 4, title: 'Management', key: 'managementOfLearning' },
  { id: 5, title: 'Assessment', key: 'feedbackAssessment' },
  { id: 6, title: 'Course Info', key: 'otherQuestions' },
  { id: 7, title: 'Experience', key: 'overallExperience' },
  { id: 8, title: 'Self-Eval', key: 'studentEvaluation' },
  { id: 9, title: 'Comments', key: 'comments' }
];
