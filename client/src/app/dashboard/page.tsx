'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/DashboardLayout';
import AdminDashboard from '@/components/AdminDashboard';
import StudentDashboard from '@/components/StudentDashboard';
import { useAuth } from '@/contexts/AuthContext';
import { Course } from '@/types/course';
import { FeedbackFormData } from '@/types/feedback';

// Sample course data - replace with API calls
const sampleCourses: Course[] = [
  {
    id: '1',
    code: 'CS 101',
    name: 'UI/UX designer',
    description: 'Master the principles of user interface and user experience design.',
    semester: '1st Semester',
    hasSubmittedFeedback: false,
    tasks: 350,
    projects: 3,
    progress: 72,
    tag: 'Student',
    color: 'pink',
    avatar: '👩🏾‍🎨',
    modules: { completed: 12, total: 16 },
  },
  {
    id: '2',
    code: 'CS 102',
    name: 'QA engineer',
    description: 'Learn the fundamentals of quality assurance and software testing.',
    semester: '1st Semester',
    hasSubmittedFeedback: false,
    tasks: 622,
    projects: 4,
    progress: 0,
    tag: 'Recommended',
    color: 'blue',
    avatar: '👨🏾‍💼',
    startDate: '20 July',
  },
  {
    id: '3',
    code: 'CC 101',
    name: 'Recruiter',
    description: 'Understand the hiring process, talent acquisition strategies.',
    semester: '1st Semester',
    hasSubmittedFeedback: false,
    tasks: 350,
    projects: 622,
    progress: 0,
    tag: 'Popular',
    color: 'yellow',
    avatar: '👨🏿‍💼',
    startDate: '20 July',
  },
  {
    id: '4',
    code: 'CC 103',
    name: 'Front-end developer',
    description: 'Build stunning and responsive websites using modern front-end technologies.',
    semester: '1st Semester',
    hasSubmittedFeedback: false,
    tasks: 350,
    projects: 3,
    progress: 0,
    tag: 'Student',
    color: 'green',
    avatar: '👩🏻‍💻',
    startDate: '20 July',
  },
  {
    id: '5',
    code: 'CS 201',
    name: 'Software Engineering 1',
    description: 'Introduction to software development lifecycle and methodologies.',
    semester: '2nd Semester',
    hasSubmittedFeedback: false,
    tasks: 450,
    projects: 5,
    progress: 45,
    color: 'pink',
    avatar: '💻',
  },
  {
    id: '6',
    code: 'CS 202',
    name: 'Software Engineering 1',
    description: 'Advanced concepts in software architecture and design patterns.',
    semester: '2nd Semester',
    hasSubmittedFeedback: false,
    tasks: 380,
    projects: 4,
    progress: 0,
    color: 'blue',
    avatar: '🏗️',
    startDate: '15 August',
  },
  {
    id: '7',
    code: 'CS 203',
    name: 'Software Engineering 1',
    description: 'Database design and management systems.',
    semester: '2nd Semester',
    hasSubmittedFeedback: false,
    tasks: 420,
    projects: 3,
    progress: 0,
    color: 'yellow',
    avatar: '🗄️',
    startDate: '15 August',
  },
  {
    id: '8',
    code: 'CS 204',
    name: 'Software Engineering 1',
    description: 'Web application development with modern frameworks.',
    semester: '2nd Semester',
    hasSubmittedFeedback: false,
    tasks: 500,
    projects: 6,
    progress: 0,
    color: 'green',
    avatar: '🌐',
    startDate: '15 August',
  },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>(sampleCourses);

  const handleSubmitFeedback = async (courseId: string, feedback: FeedbackFormData) => {
    // TODO: Send feedback to API
    console.log('Submitting feedback for course:', courseId, feedback);
    
    // Update local state to mark as submitted
    setCourses(courses.map(course => 
      course.id === courseId 
        ? { ...course, hasSubmittedFeedback: true }
        : course
    ));
    
    // TODO: Make API call
    // await axios.post('/api/feedback', { courseId, ...feedback });
  };

  // Show admin dashboard for admin and faculty
  if (user?.role === 'admin' || user?.role === 'faculty') {
    return (
      <ProtectedRoute allowedRoles={['admin', 'faculty']}>
        <DashboardLayout>
          <AdminDashboard />
        </DashboardLayout>
      </ProtectedRoute>
    );
  }

  // Show student dashboard for students
  return (
    <ProtectedRoute allowedRoles={['student']}>
      <DashboardLayout>
        <div className="max-w-[1400px] mx-auto px-6 py-8">
          <StudentDashboard
            courses={courses}
            onSubmitFeedback={handleSubmitFeedback}
          />
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
