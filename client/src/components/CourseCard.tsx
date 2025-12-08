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
      "overflow-hidden transition-all hover:shadow-md flex flex-col h-full border",
      course.color === 'pink' && "bg-white border-gray-200",
      course.color === 'blue' && "bg-white border-gray-200",
      course.color === 'yellow' && "bg-white border-gray-200",
      course.color === 'green' && "bg-white border-gray-200"
    )}>
      <CardHeader className="pb-3">
        {/* Tag and Semester Badge with fixed height to maintain alignment */}
        <div className="h-6 mb-2 flex items-center gap-2">
          {course.tag && (
            <span className={cn("text-xs font-medium px-2 py-1 rounded", tagColors[course.tag])}>
              {course.tag}
            </span>
          )}
          {course.semester && (
            <span className="text-xs font-medium px-2 py-1 rounded bg-gray-100 text-gray-700 border border-gray-200">
              {course.semester}
            </span>
          )}
        </div>
        
        <div className="flex items-start gap-4">
          <div className={cn("w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0 bg-gray-100 border border-gray-200")}>
            {course.avatar ? (
              <div className="text-3xl">{course.avatar}</div>
            ) : (
              <BookOpen className="w-8 h-8 text-gray-500" />
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-base text-gray-900 line-clamp-1">{course.code}</h3>
            <p className="text-sm text-gray-600 mt-0.5 line-clamp-2">
              {course.name}
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pb-3 flex-grow">
        {/* Description with fixed height and ellipsis */}
        <div className="mb-3">
          <p 
            className="text-xs text-gray-500 line-clamp-3 h-[3.6rem] overflow-hidden text-ellipsis" 
            title={course.description || 'No description available'}
            style={{ 
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}
          >
            {course.description || 'No description available'}
          </p>
        </div>

        {/* Due date prominently displayed with colored background */}
        {course.dueDate && (
          <div className="mb-3 p-2 bg-gray-50 border border-gray-200 rounded-lg">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-600" />
              <div className="flex-1">
                <p className="text-xs font-medium text-gray-600">Due Date</p>
                <p className="text-sm font-semibold text-gray-900">{course.dueDate}</p>
              </div>
            </div>
          </div>
        )}

        {/* Progress section with fixed height */}
        <div className="h-16 flex flex-col justify-center">
          {/* Always show feedback progress bar if feedback not submitted */}
          {!course.hasSubmittedFeedback && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Feedback Progress</span>
                <span className="font-medium text-gray-900">{feedbackProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gray-900 h-2 rounded-full transition-all"
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
                <span className="font-medium text-gray-900">Completed</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gray-900 h-2 rounded-full transition-all"
                  style={{ width: '100%' }}
                />
              </div>
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
