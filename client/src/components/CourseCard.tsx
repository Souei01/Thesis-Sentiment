'use client';

import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar, BookOpen } from 'lucide-react';
import { Course } from '@/types/course';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';
import { getFormProgressForCourse } from '@/lib/formProgress';

interface CourseCardProps {
  course: Course;
  onRateCourse: (courseId: string) => void;
}

const avatarColors = {
  pink: 'bg-pink-200',
  blue: 'bg-blue-200',
  yellow: 'bg-yellow-200',
  green: 'bg-green-200',
};

const tagColors = {
  Student: 'bg-pink-100 text-pink-800',
  Recommended: 'bg-blue-100 text-blue-800',
  Popular: 'bg-yellow-100 text-yellow-800',
};

export default function CourseCard({ course, onRateCourse }: CourseCardProps) {
  const cardColor = course.color || 'pink';
  const bgColorClass = avatarColors[cardColor];
  
  // Get real-time feedback form progress
  const [feedbackProgress, setFeedbackProgress] = useState(0);

  useEffect(() => {
    // Update progress on mount and when localStorage changes
    const updateProgress = () => {
      const progress = getFormProgressForCourse(course.id);
      setFeedbackProgress(progress);
    };

    updateProgress();

    // Listen for storage events (when form is updated)
    window.addEventListener('storage', updateProgress);
    
    // Also listen for custom event when form is updated in same tab
    window.addEventListener('feedbackUpdated', updateProgress);

    return () => {
      window.removeEventListener('storage', updateProgress);
      window.removeEventListener('feedbackUpdated', updateProgress);
    };
  }, [course.id]);

  return (
    <Card className={cn(
      "overflow-hidden transition-all hover:shadow-lg flex flex-col h-full",
      course.color === 'pink' && "bg-pink-50 border-pink-200",
      course.color === 'blue' && "bg-blue-50 border-blue-200",
      course.color === 'yellow' && "bg-yellow-50 border-yellow-200",
      course.color === 'green' && "bg-green-50 border-green-200"
    )}>
      <CardHeader className="pb-3">
        {/* Tag with fixed height to maintain alignment */}
        <div className="h-6 mb-2">
          {course.tag && (
            <span className={cn("text-xs font-medium px-2 py-1 rounded", tagColors[course.tag])}>
              {course.tag}
            </span>
          )}
        </div>
        
        <div className="flex items-start gap-4">
          <div className={cn("w-16 h-16 rounded-2xl flex items-center justify-center flex-shrink-0", bgColorClass)}>
            {course.avatar ? (
              <div className="text-3xl">{course.avatar}</div>
            ) : (
              <BookOpen className="w-8 h-8 text-gray-600" />
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-base text-gray-900 line-clamp-1">{course.code}</h3>
            <p className="text-sm font-medium text-gray-700 mt-0.5 line-clamp-2">
              {course.name}
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pb-3 flex-grow">
        {/* Description with fixed height */}
        <div className="mb-3">
          <p className="text-xs text-gray-600 line-clamp-3 h-[3.6rem]">
            {course.description || 'No description available'}
          </p>
        </div>

        {/* Progress section with fixed height */}
        <div className="h-16 flex flex-col justify-center">
          {/* Always show feedback progress bar if feedback not submitted */}
          {!course.hasSubmittedFeedback && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Feedback Progress</span>
                <span className="font-semibold text-[#8E1B1B]">{feedbackProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-[#8E1B1B] h-2 rounded-full transition-all"
                  style={{ width: `${feedbackProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Show completion message if feedback submitted */}
          {course.hasSubmittedFeedback && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Status</span>
                <span className="font-semibold text-green-600">Completed</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all"
                  style={{ width: '100%' }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Due date with fixed height */}
        <div className="h-6 flex items-center mt-2">
          {course.dueDate && (
            <div className="flex items-center gap-2 text-xs text-gray-600">
              <Calendar className="w-3.5 h-3.5" />
              <span>Due: {course.dueDate}</span>
            </div>
          )}
        </div>
      </CardContent>

      <CardFooter className="pt-3">
        <Button
          onClick={() => onRateCourse(course.id)}
          className={cn(
            "w-full font-medium",
            course.hasSubmittedFeedback 
              ? "bg-gray-400 hover:bg-gray-500" 
              : "bg-[#8E1B1B] hover:bg-[#6B1414]"
          )}
          disabled={course.hasSubmittedFeedback}
        >
          {course.hasSubmittedFeedback 
            ? 'Feedback Submitted' 
            : feedbackProgress > 0 
              ? 'Continue Feedback' 
              : 'Start Feedback'}
        </Button>
      </CardFooter>
    </Card>
  );
}
