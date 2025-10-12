'use client';

import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileCheck, BookOpen, FolderKanban, Calendar } from 'lucide-react';
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
      "overflow-hidden transition-all hover:shadow-lg",
      course.color === 'pink' && "bg-pink-50 border-pink-200",
      course.color === 'blue' && "bg-blue-50 border-blue-200",
      course.color === 'yellow' && "bg-yellow-50 border-yellow-200",
      course.color === 'green' && "bg-green-50 border-green-200"
    )}>
      <CardHeader className="pb-3">
        {course.tag && (
          <div className="mb-2">
            <span className={cn("text-xs font-medium px-2 py-1 rounded", tagColors[course.tag])}>
              {course.tag}
            </span>
          </div>
        )}
        
        <div className="flex items-start gap-4">
          <div className={cn("w-20 h-20 rounded-2xl flex items-center justify-center", bgColorClass)}>
            {course.avatar ? (
              <div className="text-4xl">{course.avatar}</div>
            ) : (
              <BookOpen className="w-10 h-10 text-gray-600" />
            )}
          </div>
          
          <div className="flex-1">
            <h3 className="font-bold text-lg text-gray-900">{course.name}</h3>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {course.description || 'No description available'}
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pb-3">
        <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
          {course.tasks && (
            <div className="flex items-center gap-1">
              <FileCheck className="w-4 h-4" />
              <span>{course.tasks} tasks</span>
            </div>
          )}
          {course.projects !== undefined && (
            <div className="flex items-center gap-1">
              <FolderKanban className="w-4 h-4" />
              <span>{course.projects} projects</span>
            </div>
          )}
        </div>

        {/* Show feedback form progress if any progress has been made */}
        {feedbackProgress > 0 && !course.hasSubmittedFeedback && (
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

        {/* Show original course progress if available and no feedback in progress */}
        {course.progress !== undefined && feedbackProgress === 0 && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Progress</span>
              <span className="font-semibold">{course.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-gray-900 h-2 rounded-full transition-all"
                style={{ width: `${course.progress}%` }}
              />
            </div>
          </div>
        )}

        {course.modules && (
          <div className="flex justify-between text-sm mt-3">
            <span className="text-gray-600">Modules:</span>
            <span className="font-semibold">{course.modules.completed}/{course.modules.total}</span>
          </div>
        )}

        {course.startDate && !course.progress && feedbackProgress === 0 && (
          <div className="flex items-center gap-2 text-sm text-gray-600 mt-3">
            <Calendar className="w-4 h-4" />
            <span>Start date: {course.startDate}</span>
          </div>
        )}
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
              : 'Rate Course'}
        </Button>
      </CardFooter>
    </Card>
  );
}
