'use client';

import { useState } from 'react';
import { Course } from '@/types/course';
import { FeedbackFormData } from '@/types/feedback';
import CourseCard from '@/components/CourseCard';
import FeedbackDialog from '@/components/FeedbackDialog';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface StudentDashboardProps {
  courses: Course[];
  onSubmitFeedback?: (courseId: string, feedback: FeedbackFormData) => void;
  onRateCourse?: (courseId: string) => void;
}

export default function StudentDashboard({ courses, onSubmitFeedback, onRateCourse }: StudentDashboardProps) {
  const [selectedSemester, setSelectedSemester] = useState('all');
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);

  const handleRateCourse = (courseId: string) => {
    if (onRateCourse) {
      onRateCourse(courseId);
    } else {
      const course = courses.find((c) => c.id === courseId);
      if (course) {
        setSelectedCourse(course);
        setFeedbackDialogOpen(true);
      }
    }
  };

  const handleSubmitFeedback = (courseId: string, feedback: FeedbackFormData) => {
    if (onSubmitFeedback) {
      onSubmitFeedback(courseId, feedback);
    }
    setFeedbackDialogOpen(false);
  };

  const filteredCourses = selectedSemester === 'all'
    ? courses
    : courses.filter((course) => {
        // Debug: Log semester values
        console.log(`Course: ${course.name}, Semester: "${course.semester}", Selected: "${selectedSemester}", Match: ${course.semester === selectedSemester}`);
        return course.semester === selectedSemester;
      });

  // Group courses by semester when showing all
  const groupedCourses = selectedSemester === 'all' 
    ? courses.reduce((acc, course) => {
        const sem = course.semester || 'Unknown';
        if (!acc[sem]) acc[sem] = [];
        acc[sem].push(course);
        return acc;
      }, {} as Record<string, Course[]>)
    : null;

  // Log total courses and filtered count
  console.log(`Total courses: ${courses.length}, Filtered: ${filteredCourses.length}, Selected semester: "${selectedSemester}"`);

  return (
    <>
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Courses Enrolled</h1>
        <Select value={selectedSemester} onValueChange={setSelectedSemester}>
          <SelectTrigger className="w-[200px] bg-[#8E1B1B] text-white border-[#8E1B1B] hover:bg-[#6B1414]">
            <SelectValue placeholder="Filter: Semester" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Semesters</SelectItem>
            <SelectItem value="1st Semester">1st Semester</SelectItem>
            <SelectItem value="2nd Semester">2nd Semester</SelectItem>
            <SelectItem value="Summer">Summer</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Show grouped by semester when "all" is selected */}
      {selectedSemester === 'all' && groupedCourses ? (
        <div className="space-y-8">
          {Object.entries(groupedCourses).map(([semester, semesterCourses]) => (
            <div key={semester} className="space-y-4">
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-bold text-gray-800">{semester}</h2>
                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium border border-purple-200">
                  {semesterCourses.length} {semesterCourses.length === 1 ? 'course' : 'courses'}
                </span>
              </div>
              <div className="h-1 bg-gradient-to-r from-purple-500 to-transparent rounded-full" />
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {semesterCourses.map((course) => (
                  <CourseCard
                    key={course.id}
                    course={course}
                    onRateCourse={handleRateCourse}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Show filtered courses when specific semester is selected */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {filteredCourses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              onRateCourse={handleRateCourse}
            />
          ))}
        </div>
      )}

      {filteredCourses.length === 0 && selectedSemester !== 'all' && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No courses found for the selected semester.</p>
        </div>
      )}

      <FeedbackDialog
        course={selectedCourse}
        open={feedbackDialogOpen}
        onOpenChange={setFeedbackDialogOpen}
        onSubmit={handleSubmitFeedback}
      />
    </>
  );
}
