'use client';

import { useState } from 'react';
import { Check } from 'lucide-react';
import { Course } from '@/types/course';
import { MultistepFeedbackForm } from '@/components/FeedbackForm/MultistepFeedbackForm';
import { FeedbackFormData } from '@/types/feedback';

interface FeedbackDialogProps {
  course: Course | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (courseId: string, feedback: FeedbackFormData) => void;
}

export default function FeedbackDialog({
  course,
  open,
  onOpenChange,
  onSubmit,
}: FeedbackDialogProps) {
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSubmit = (data: FeedbackFormData) => {
    if (course) {
      onSubmit(course.id, data);
      setShowSuccess(true);
      
      // Show success message then close
      setTimeout(() => {
        setShowSuccess(false);
        onOpenChange(false);
      }, 2000);
    }
  };

  if (!course) return null;

  if (!open) return null;

  if (showSuccess) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-12 max-w-md">
          <div className="flex flex-col items-center justify-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <Check className="w-10 h-10 text-green-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Feedback Submitted!
            </h3>
            <p className="text-gray-600 text-center">
              Thank you for your cooperation.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <MultistepFeedbackForm
      courseId={course.id}
      courseName={course.name}
      courseCode={course.code}
      instructor={course.instructor}
      onSubmit={handleSubmit}
      onClose={() => onOpenChange(false)}
    />
  );
}
