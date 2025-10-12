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
    code: 'CC100',
    name: 'Introduction to Computing',
    description: 'An overview of computing fundamentals, including computer hardware, software, and basic concepts in IT and computer science.',
    semester: 'First Semester',
    hasSubmittedFeedback: false,
    progress: 0,
    color: 'pink',
    dueDate: '15 December 2024',
  },
  {
    id: '2',
    code: 'CC101',
    name: 'Computer Programming 1',
    description: 'Introduces the basics of programming using structured approaches, focusing on problem-solving and logic development.',
    semester: 'First Semester',
    hasSubmittedFeedback: false,
    progress: 0,
    color: 'blue',
    dueDate: '15 December 2024',
  },
  {
    id: '3',
    code: 'ACT115',
    name: 'Platform Technologies',
    description: 'Covers foundational knowledge of operating systems, hardware platforms, and virtualization technologies.',
    semester: 'First Semester',
    hasSubmittedFeedback: false,
    progress: 0,
    color: 'yellow',
    dueDate: '15 December 2024',
  },
  {
    id: '4',
    code: 'ACT116',
    name: 'Human Computer Interactions',
    description: 'Explores the design and evaluation of user interfaces with an emphasis on usability and user-centered design.',
    semester: 'First Semester',
    hasSubmittedFeedback: false,
    progress: 0,
    color: 'green',
    dueDate: '15 December 2024',
  },
  {
    id: '5',
    code: 'CC102',
    name: 'Computer Programming 2',
    description: 'Builds on Programming 1 by introducing advanced programming concepts such as functions, arrays, and file handling.',
    semester: 'Second Semester',
    hasSubmittedFeedback: false,
    progress: 0,
    color: 'pink',
    dueDate: '15 May 2025',
  },
  {
    id: '6',
    code: 'ACT112',
    name: 'Data Communications and Networking 1',
    description: 'Covers the basics of computer networks, data transmission, network models, and protocols.',
    semester: 'Second Semester',
    hasSubmittedFeedback: false,
    progress: 0,
    color: 'blue',
    dueDate: '15 May 2025',
  },
  {
    id: '7',
    code: 'ACT123',
    name: 'Systems Administration',
    description: 'Focuses on managing and maintaining computer systems, including user accounts, backups, and security policies.',
    semester: 'Second Semester',
    hasSubmittedFeedback: false,
    progress: 0,
    color: 'yellow',
    dueDate: '15 May 2025',
  },
  {
    id: '8',
    code: 'ACT124',
    name: 'Object Oriented Programming',
    description: 'Teaches programming using the object-oriented paradigm, including classes, objects, inheritance, and polymorphism.',
    semester: 'Second Semester',
    hasSubmittedFeedback: false,
    progress: 0,
    color: 'green',
    dueDate: '15 May 2025',
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
