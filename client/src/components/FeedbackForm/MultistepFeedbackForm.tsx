'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertDialog } from '@/components/ui/alert-dialog-custom';
import { ChevronLeft, ChevronRight, Save, Send } from 'lucide-react';
import { ProgressBar } from './ProgressBar';
import { RatingInput } from './RatingInput';
import { YesNoInput } from './YesNoInput';
import { FeedbackFormData, FORM_STEPS } from '@/types/feedback';
import { saveFormProgress, getFormProgress, clearFormProgress } from '@/lib/formProgress';
import { sanitizeTextInput, validateFeedbackComments } from '@/lib/sanitize';

interface MultistepFeedbackFormProps {
  courseId: string;
  courseName: string;
  courseCode: string;
  instructor?: string;
  onSubmit: (data: FeedbackFormData) => void;
  onClose: () => void;
  serverError?: string | null;
}

const getInitialFormData = (courseId: string): FeedbackFormData => ({
  courseId,
  currentStep: 1,
  commitment: { 
    sensitivity: 0, 
    integration: 0, 
    availability: 0, 
    punctuality: 0, 
    recordKeeping: 0 
  },
  knowledgeOfSubject: { 
    mastery: 0, 
    stateOfArt: 0, 
    practicalIntegration: 0, 
    relevance: 0, 
    currentTrends: 0 
  },
  independentLearning: { 
    teachingStrategies: 0, 
    studentEsteem: 0, 
    studentAutonomy: 0, 
    independentThinking: 0, 
    beyondRequired: 0 
  },
  managementOfLearning: { 
    studentContribution: 0, 
    facilitatorRole: 0, 
    discussionEncouragement: 0, 
    instructionalMethods: 0, 
    instructionalMaterials: 0 
  },
  feedbackAssessment: { 
    clearCommunication: 0, 
    timelyFeedback: 0, 
    improvementFeedback: 0 
  },
  otherQuestions: { 
    syllabusExplained: null, 
    deliveredAsOutlined: null, 
    gradingCriteriaExplained: null, 
    examsRelated: null, 
    assignmentsRelated: null, 
    lmsResourcesUseful: null 
  },
  overallExperience: { 
    worthwhileClass: null, 
    wouldRecommend: null, 
    hoursPerWeek: 0, 
    overallRating: 0 
  },
  studentEvaluation: { 
    constructiveContribution: 0, 
    achievingOutcomes: 0 
  },
  comments: { 
    recommendedChanges: '', 
    likeBest: '', 
    likeLeast: '', 
    additionalComments: '' 
  }
});

export const MultistepFeedbackForm: React.FC<MultistepFeedbackFormProps> = ({
  courseId,
  courseName,
  courseCode,
  instructor,
  onSubmit,
  onClose,
  serverError
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [alertDialog, setAlertDialog] = useState<{ open: boolean; title: string; description: string; type: 'error' | 'warning' | 'info' }>({ 
    open: false, 
    title: '', 
    description: '', 
    type: 'warning' 
  });
  const [formData, setFormData] = useState<FeedbackFormData>(() => {
    // Load saved progress from formProgress utility
    const saved = getFormProgress(courseId);
    if (saved && saved.formData) {
      try {
        setCurrentStep(saved.currentStep || 1);
        return saved.formData as FeedbackFormData;
      } catch (e) {
        console.error('Error loading saved form data:', e);
      }
    }
    return getInitialFormData(courseId);
  });

  // Save progress using formProgress utility whenever form data changes
  useEffect(() => {
    saveFormProgress(courseId, {
      currentStep,
      totalSteps: FORM_STEPS.length,
      formData,
      lastUpdated: new Date().toISOString()
    });
  }, [formData, currentStep, courseId]);

  const updateFormData = (section: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...(prev[section as keyof FeedbackFormData] as object),
        [field]: value
      }
    }));
  };

  // Helper function to check if a comment is meaningful
  const isValidComment = (text: string): boolean => {
    if (!text || text.trim() === '') {
      return false;
    }

    const trimmed = text.trim().toLowerCase();
    
    // List of invalid responses
    const invalidResponses = [
      'n/a', 'na', 'none', 'nothing', 'no', 'nope', 'nah',
      'idk', "i don't know", 'dunno', 'not sure',
      '.', '..', '...', '-', '--', '---', '_', '__', '___',
      'no comment', 'no comments', 'no feedback',
      'pass', 'skip', 'skipped',
      'wala', 'wla', 'walang', 'walang sagot'
    ];

    // Check if response is in invalid list
    if (invalidResponses.includes(trimmed)) {
      return false;
    }

    // Check if response is only punctuation or special characters
    if (/^[^a-zA-Z0-9]+$/.test(trimmed)) {
      return false;
    }

    // Require at least 3 characters of actual content
    const alphanumericContent = trimmed.replace(/[^a-zA-Z0-9]/g, '');
    if (alphanumericContent.length < 3) {
      return false;
    }

    return true;
  };

  const validateCurrentStep = (): boolean => {
    const step = FORM_STEPS[currentStep - 1];
    const sectionData = formData[step.key as keyof FeedbackFormData];

    // Comments section (step 9) - validate meaningful responses
    if (currentStep === 9) {
      const comments = formData.comments;
      const hasAtLeastOneComment = 
        isValidComment(comments.recommendedChanges) ||
        isValidComment(comments.likeBest) ||
        isValidComment(comments.likeLeast) ||
        isValidComment(comments.additionalComments);

      if (!hasAtLeastOneComment) {
        setAlertDialog({
          open: true,
          title: 'Comment Required',
          description: 'Please provide at least one meaningful comment. Avoid responses like "N/A", "none", or "." - we value your constructive feedback.',
          type: 'warning'
        });
        return false;
      }

      // Validate each non-empty comment
      const commentFields = [
        { value: comments.recommendedChanges, label: 'recommended changes' },
        { value: comments.likeBest, label: 'what you liked best' },
        { value: comments.likeLeast, label: 'what you liked least' },
        { value: comments.additionalComments, label: 'additional comments' }
      ];

      for (const field of commentFields) {
        // If there's text, it must be valid
        if (field.value && field.value.trim() !== '' && !isValidComment(field.value)) {
          setAlertDialog({
            open: true,
            title: 'Invalid Comment',
            description: `Please provide a meaningful response for "${field.label}". Avoid responses like "N/A", "none", or just punctuation marks.`,
            type: 'warning'
          });
          return false;
        }
      }

      return true;
    }

    if (typeof sectionData === 'object' && sectionData !== null) {
      // Check all fields in the section
      const allFieldsValid = Object.values(sectionData).every(value => {
        if (typeof value === 'number') {
          return value > 0; // Rating must be selected (1-5)
        }
        if (typeof value === 'boolean' || value === null) {
          return value !== null; // Yes/No must be answered
        }
        // Strings are not required (only in comments section)
        return true;
      });

      if (!allFieldsValid) {
        return false;
      }
    }
    
    return true;
  };

  const handleNext = () => {
    if (validateCurrentStep()) {
      setCurrentStep(prev => Math.min(prev + 1, FORM_STEPS.length));
    } else {
      setAlertDialog({
        open: true,
        title: 'Incomplete Form',
        description: 'Please answer all required questions before proceeding.',
        type: 'warning'
      });
    }
  };

  const handleBack = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = () => {
    if (validateCurrentStep()) {
      // Validate and sanitize comments
      const commentsValidation = validateFeedbackComments(formData.comments);
      if (!commentsValidation.valid) {
        setAlertDialog({
          open: true,
          title: 'Invalid Comments',
          description: commentsValidation.message || 'Please provide meaningful feedback.',
          type: 'warning'
        });
        return;
      }
      
      // Sanitize text inputs before submission
      const sanitizedData = {
        ...formData,
        comments: {
          recommendedChanges: sanitizeTextInput(formData.comments.recommendedChanges, 1000),
          likeBest: sanitizeTextInput(formData.comments.likeBest, 1000),
          likeLeast: sanitizeTextInput(formData.comments.likeLeast, 1000),
          additionalComments: sanitizeTextInput(formData.comments.additionalComments, 2000)
        },
        completedAt: new Date()
      };
      
      onSubmit(sanitizedData);
      // Clear form progress from storage
      clearFormProgress(courseId);
    } else {
      setAlertDialog({
        open: true,
        title: 'Incomplete Form',
        description: 'Please answer all required questions before submitting.',
        type: 'warning'
      });
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1: // Commitment
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="mb-4 sm:mb-6">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800">A. Commitment</h3>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Please rate your instructor's commitment using the scale: 1-Poor, 2-Fair, 3-Satisfactory, 4-Very Satisfactory, 5-Outstanding
              </p>
              <p className="text-xs text-red-600 mt-1">* All questions are required</p>
            </div>
            <RatingInput
              label="1. Demonstrates sensitivity to students' ability to attend and absorb content information."
              value={formData.commitment.sensitivity}
              onChange={(v) => updateFormData('commitment', 'sensitivity', v)}
              required
            />
            <RatingInput
              label="2. Integrates sensitively his/her learning objectives with those of the students in a collaborative process."
              value={formData.commitment.integration}
              onChange={(v) => updateFormData('commitment', 'integration', v)}
              required
            />
            <RatingInput
              label="3. Makes self available to students after class session."
              value={formData.commitment.availability}
              onChange={(v) => updateFormData('commitment', 'availability', v)}
              required
            />
            <RatingInput
              label="4. Regularly comes to class on time, well-groomed and well-prepared to complete assigned responsibilities."
              value={formData.commitment.punctuality}
              onChange={(v) => updateFormData('commitment', 'punctuality', v)}
              required
            />
            <RatingInput
              label="5. Keeps accurate records of students' performance and prompt submission of the same."
              value={formData.commitment.recordKeeping}
              onChange={(v) => updateFormData('commitment', 'recordKeeping', v)}
              required
            />
          </div>
        );

      case 2: // Knowledge of Subject
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="mb-4 sm:mb-6">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800">B. Knowledge of Subject</h3>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Please rate your instructor's knowledge and expertise
              </p>
              <p className="text-xs text-red-600 mt-1">* All questions are required</p>
            </div>
            <RatingInput
              label="1. Demonstrates mastery of the subject matter (explains the subject matter without relying solely on the prescribed textbook)."
              value={formData.knowledgeOfSubject.mastery}
              onChange={(v) => updateFormData('knowledgeOfSubject', 'mastery', v)}
              required
            />
            <RatingInput
              label="2. Draws and shares information on the state of the art of theory and practice in his/her discipline."
              value={formData.knowledgeOfSubject.stateOfArt}
              onChange={(v) => updateFormData('knowledgeOfSubject', 'stateOfArt', v)}
              required
            />
            <RatingInput
              label="3. Integrates subject to practical circumstances and learning intents/purposes of students."
              value={formData.knowledgeOfSubject.practicalIntegration}
              onChange={(v) => updateFormData('knowledgeOfSubject', 'practicalIntegration', v)}
              required
            />
            <RatingInput
              label="4. Explains the relevance of present topics to the previous lessons, and relates the subject matter to relevant current issues and/or daily life activities."
              value={formData.knowledgeOfSubject.relevance}
              onChange={(v) => updateFormData('knowledgeOfSubject', 'relevance', v)}
              required
            />
            <RatingInput
              label="5. Demonstrates up-to-date knowledge and/or awareness on current trends and issues of the subject."
              value={formData.knowledgeOfSubject.currentTrends}
              onChange={(v) => updateFormData('knowledgeOfSubject', 'currentTrends', v)}
              required
            />
          </div>
        );

      case 3: // Independent Learning
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="mb-4 sm:mb-6">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800">C. Teaching for Independent Learning</h3>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Please rate how well your instructor promotes independent learning
              </p>
              <p className="text-xs text-red-600 mt-1">* All questions are required</p>
            </div>
            <RatingInput
              label="1. Creates teaching strategies that allow students to practice using concepts they need to understand (interactive discussion)."
              value={formData.independentLearning.teachingStrategies}
              onChange={(v) => updateFormData('independentLearning', 'teachingStrategies', v)}
              required
            />
            <RatingInput
              label="2. Enhances student self-esteem and/or gives due recognition to students' performance/potentials."
              value={formData.independentLearning.studentEsteem}
              onChange={(v) => updateFormData('independentLearning', 'studentEsteem', v)}
              required
            />
            <RatingInput
              label="3. Allows students to create their own course with objectives and realistically defined student-professor rules and make them accountable for their performance."
              value={formData.independentLearning.studentAutonomy}
              onChange={(v) => updateFormData('independentLearning', 'studentAutonomy', v)}
              required
            />
            <RatingInput
              label="4. Allows students to think independently and make their own decisions and holding them accountable for their performance based largely on their success in executing decisions."
              value={formData.independentLearning.independentThinking}
              onChange={(v) => updateFormData('independentLearning', 'independentThinking', v)}
              required
            />
            <RatingInput
              label="5. Encourages students to learn beyond what is required and help/guide the students how to apply the concepts learned."
              value={formData.independentLearning.beyondRequired}
              onChange={(v) => updateFormData('independentLearning', 'beyondRequired', v)}
              required
            />
          </div>
        );

      case 4: // Management of Learning
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="mb-4 sm:mb-6">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800">D. Management of Learning</h3>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Please rate your instructor's classroom management and teaching methods
              </p>
              <p className="text-xs text-red-600 mt-1">* All questions are required</p>
            </div>
            <RatingInput
              label="1. Creates opportunities for intensive and/or extensive contribution of students in the class activities (e.g. breaks class into dyads, triads or buzz/task groups)."
              value={formData.managementOfLearning.studentContribution}
              onChange={(v) => updateFormData('managementOfLearning', 'studentContribution', v)}
              required
            />
            <RatingInput
              label="2. Assumes roles as facilitator, resource person, coach, inquisitor, integrator, referee in drawing students to contribute to knowledge and understanding of the concepts at hand."
              value={formData.managementOfLearning.facilitatorRole}
              onChange={(v) => updateFormData('managementOfLearning', 'facilitatorRole', v)}
              required
            />
            <RatingInput
              label="3. The instructor encouraged discussions and responded to questions."
              value={formData.managementOfLearning.discussionEncouragement}
              onChange={(v) => updateFormData('managementOfLearning', 'discussionEncouragement', v)}
              required
            />
            <RatingInput
              label="4. The instructor used a variety of instructional methods to reach the course objectives (e.g. group discussions, student presentations, etc.)."
              value={formData.managementOfLearning.instructionalMethods}
              onChange={(v) => updateFormData('managementOfLearning', 'instructionalMethods', v)}
              required
            />
            <RatingInput
              label="5. Use of Instructional Materials (audio/video materials: field trips, film showing, computer aided instruction, etc.) to reinforce learning processes."
              value={formData.managementOfLearning.instructionalMaterials}
              onChange={(v) => updateFormData('managementOfLearning', 'instructionalMaterials', v)}
              required
            />
          </div>
        );

      case 5: // Feedback and Assessment
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="mb-4 sm:mb-6">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800">E. Feedback and Assessment</h3>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Please rate the quality of feedback and assessment in this course
              </p>
              <p className="text-xs text-red-600 mt-1">* All questions are required</p>
            </div>
            <RatingInput
              label="1. Information about the assessment was communicated clearly."
              value={formData.feedbackAssessment.clearCommunication}
              onChange={(v) => updateFormData('feedbackAssessment', 'clearCommunication', v)}
              required
            />
            <RatingInput
              label="2. Feedback was provided within the stated timeframe (returning of assessment result)."
              value={formData.feedbackAssessment.timelyFeedback}
              onChange={(v) => updateFormData('feedbackAssessment', 'timelyFeedback', v)}
              required
            />
            <RatingInput
              label="3. Feedback showed how to improve my work (e.g. corrections including comments)."
              value={formData.feedbackAssessment.improvementFeedback}
              onChange={(v) => updateFormData('feedbackAssessment', 'improvementFeedback', v)}
              required
            />
          </div>
        );

      case 6: // Other Questions
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="mb-4 sm:mb-6">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800">F. Course Information</h3>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Please answer the following questions about the course
              </p>
              <p className="text-xs text-red-600 mt-1">* All questions are required</p>
            </div>
            <YesNoInput
              label="1. The syllabus was explained at the beginning of the course."
              value={formData.otherQuestions.syllabusExplained}
              onChange={(v) => updateFormData('otherQuestions', 'syllabusExplained', v)}
              required
            />
            <YesNoInput
              label="2. The course was delivered as outlined in the syllabus."
              value={formData.otherQuestions.deliveredAsOutlined}
              onChange={(v) => updateFormData('otherQuestions', 'deliveredAsOutlined', v)}
              required
            />
            <YesNoInput
              label="3. Instructor explained the grading criteria of the course."
              value={formData.otherQuestions.gradingCriteriaExplained}
              onChange={(v) => updateFormData('otherQuestions', 'gradingCriteriaExplained', v)}
              required
            />
            <YesNoInput
              label="4. Exams related to the course learning outcomes."
              value={formData.otherQuestions.examsRelated}
              onChange={(v) => updateFormData('otherQuestions', 'examsRelated', v)}
              required
            />
            <YesNoInput
              label="5. Projects/assignments related to the course learning outcomes."
              value={formData.otherQuestions.assignmentsRelated}
              onChange={(v) => updateFormData('otherQuestions', 'assignmentsRelated', v)}
              required
            />
            <YesNoInput
              label="6. Learning Management resources for the course were useful."
              value={formData.otherQuestions.lmsResourcesUseful}
              onChange={(v) => updateFormData('otherQuestions', 'lmsResourcesUseful', v)}
              required
            />
          </div>
        );

      case 7: // Overall Experience
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="mb-4 sm:mb-6">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800">G. Overall Experience</h3>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Please share your overall experience in this course
              </p>
              <p className="text-xs text-red-600 mt-1">* All questions are required</p>
            </div>
            <YesNoInput
              label="1. This was a worthwhile class."
              value={formData.overallExperience.worthwhileClass}
              onChange={(v) => updateFormData('overallExperience', 'worthwhileClass', v)}
              required
            />
            <YesNoInput
              label="2. Would you recommend this course to a fellow student?"
              value={formData.overallExperience.wouldRecommend}
              onChange={(v) => updateFormData('overallExperience', 'wouldRecommend', v)}
              required
            />
            <div className="space-y-2 sm:space-y-3">
              <Label className="text-xs sm:text-sm font-medium text-gray-700 block">
                3. How many hours did you spend per week on preparation/homework for this course? <span className="text-red-500">*</span>
              </Label>
              <Input
                type="number"
                min="0"
                max="168"
                step="0.5"
                value={formData.overallExperience.hoursPerWeek || ''}
                onChange={(e) => {
                  const val = parseFloat(e.target.value) || 0;
                  if (val <= 168) {
                    updateFormData('overallExperience', 'hoursPerWeek', val);
                  }
                }}
                className="max-w-xs"
                placeholder="Enter hours (e.g., 4.5)"
              />
              <p className="text-xs text-gray-500 mt-1">Maximum: 168 hours per week (decimal values allowed)</p>
            </div>
            <RatingInput
              label="4. Overall, how do you rate your experience in this course?"
              value={formData.overallExperience.overallRating}
              onChange={(v) => updateFormData('overallExperience', 'overallRating', v)}
              required
            />
          </div>
        );

      case 8: // Student Evaluation
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="mb-4 sm:mb-6">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800">H. Student Self-Evaluation</h3>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Please evaluate your own performance in this course
              </p>
              <p className="text-xs text-red-600 mt-1">* All questions are required</p>
            </div>
            <RatingInput
              label="1. I contributed constructively during in-class activities."
              value={formData.studentEvaluation.constructiveContribution}
              onChange={(v) => updateFormData('studentEvaluation', 'constructiveContribution', v)}
              required
            />
            <RatingInput
              label="2. I feel I am achieving the learning outcomes."
              value={formData.studentEvaluation.achievingOutcomes}
              onChange={(v) => updateFormData('studentEvaluation', 'achievingOutcomes', v)}
              required
            />
          </div>
        );

      case 9: // Comments
        return (
          <div className="space-y-4 sm:space-y-6">
            <div className="mb-4 sm:mb-6">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800">I. Comments on Strengths and Ways of Improvement</h3>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Please provide meaningful, constructive feedback in at least one field
              </p>
              <p className="text-xs text-red-600 mt-1">
                * At least one meaningful comment is required (avoid responses like "N/A", "none", or ".")
              </p>
            </div>
            <div className="space-y-2 sm:space-y-3">
              <Label className="text-xs sm:text-sm font-medium text-gray-700">
                1. What changes would you recommend to improve this course?
              </Label>
              <Textarea
                value={formData.comments.recommendedChanges}
                onChange={(e) => updateFormData('comments', 'recommendedChanges', e.target.value)}
                placeholder="Share your suggestions for improvement..."
                rows={4}
                maxLength={1000}
                className="text-sm"
              />
              <p className="text-xs text-gray-500">{formData.comments.recommendedChanges.length}/1000 characters</p>
            </div>
            <div className="space-y-2 sm:space-y-3">
              <Label className="text-xs sm:text-sm font-medium text-gray-700">
                2. What did you like best about your instructor&apos;s teaching?
              </Label>
              <Textarea
                value={formData.comments.likeBest}
                onChange={(e) => updateFormData('comments', 'likeBest', e.target.value)}
                placeholder="What you appreciated most..."
                rows={4}
                maxLength={1000}
                className="text-sm"
              />
              <p className="text-xs text-gray-500">{formData.comments.likeBest.length}/1000 characters</p>
            </div>
            <div className="space-y-2 sm:space-y-3">
              <Label className="text-xs sm:text-sm font-medium text-gray-700">
                3. What did you like least about your instructor&apos;s teaching?
              </Label>
              <Textarea
                value={formData.comments.likeLeast}
                onChange={(e) => updateFormData('comments', 'likeLeast', e.target.value)}
                placeholder="Areas that could be improved..."
                rows={4}
                maxLength={1000}
                className="text-sm"
              />
              <p className="text-xs text-gray-500">{formData.comments.likeLeast.length}/1000 characters</p>
            </div>
            <div className="space-y-2 sm:space-y-3">
              <Label className="text-xs sm:text-sm font-medium text-gray-700">
                4. Any further, constructive comments:
              </Label>
              <Textarea
                value={formData.comments.additionalComments}
                onChange={(e) => updateFormData('comments', 'additionalComments', e.target.value)}
                placeholder="Additional feedback..."
                rows={4}
                maxLength={2000}
                className="text-sm"
              />
              <p className="text-xs text-gray-500">{formData.comments.additionalComments.length}/2000 characters</p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-2 sm:p-4 overflow-y-auto">
      <Card className="w-full max-w-4xl bg-white p-4 sm:p-6 md:p-8 my-4 sm:my-8 max-h-[95vh] overflow-y-auto">
        {/* Header */}
        <div className="mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-800 mb-2">Faculty Evaluation Form</h2>
          <p className="text-sm sm:text-base text-gray-600">{courseCode} - {courseName}</p>
          {instructor && (
            <p className="text-sm sm:text-base text-gray-700 font-medium mt-1">
              Instructor: {instructor}
            </p>
          )}
          <p className="text-xs sm:text-sm text-gray-500 mt-2 flex items-center gap-2">
            <Save className="w-3 h-3 sm:w-4 sm:h-4" />
            Your progress is automatically saved. You can return to complete this form later.
          </p>
        </div>

        {/* Progress Bar */}
        <ProgressBar currentStep={currentStep} />

        {/* Server Error Display */}
        {serverError && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800 font-medium">⚠️ Submission Failed</p>
            <p className="text-sm text-red-700 mt-1">{serverError}</p>
          </div>
        )}

        {/* Form Content */}
        <div className="min-h-[300px] sm:min-h-[500px] mb-6 sm:mb-8">
          {renderStepContent()}
        </div>

        {/* Navigation Buttons */}
        <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3 pt-4 sm:pt-6 border-t">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStep === 1}
            className="flex items-center justify-center gap-2 w-full sm:w-auto order-2 sm:order-1"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </Button>

          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto order-1 sm:order-2">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex items-center justify-center gap-2 w-full sm:w-auto"
            >
              <Save className="w-4 h-4" />
              Save & Exit
            </Button>

            {currentStep < FORM_STEPS.length ? (
              <Button
                onClick={handleNext}
                className="bg-[#8E1B1B] hover:bg-[#7A1717] flex items-center justify-center gap-2 w-full sm:w-auto"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                className="bg-green-600 hover:bg-green-700 flex items-center justify-center gap-2 w-full sm:w-auto"
              >
                <Send className="w-4 h-4" />
                Submit Feedback
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Alert Dialog for validations */}
      <AlertDialog
        open={alertDialog.open}
        onClose={() => setAlertDialog({ ...alertDialog, open: false })}
        title={alertDialog.title}
        description={alertDialog.description}
        type={alertDialog.type}
      />
    </div>
  );
};
