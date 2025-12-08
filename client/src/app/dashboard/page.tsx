'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/DashboardLayout';
import AdminDashboard from '@/components/AdminDashboard';
import StudentDashboard from '@/components/StudentDashboard';
import FacultyDashboard from '@/components/FacultyDashboard';
import { useAuth } from '@/contexts/AuthContext';
import { Course } from '@/types/course';
import { FeedbackFormData } from '@/types/feedback';
import axiosInstance from '@/lib/axios';
import Cookies from 'js-cookie';

export default function DashboardPage() {
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch enrolled courses for students
  useEffect(() => {
    if (user?.role === 'student') {
      fetchEnrolledCourses();
    }
  }, [user]);

  const fetchEnrolledCourses = async () => {
    try {
      setLoading(true);
      const token = Cookies.get('access_token');
      console.log('Fetching courses with token:', token ? 'Token exists' : 'No token');
      console.log('Making request to: /enrollments/');
      
      const response = await axiosInstance.get('/enrollments/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      console.log('Courses response:', response.data);
      setCourses(response.data.courses);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching courses:', err);
      console.error('Error response:', err.response);
      setError(err.response?.data?.error || err.message || 'Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async (courseId: string, feedback: FeedbackFormData) => {
    try {
      // Optimistic update - immediately mark as submitted in UI
      setCourses(prevCourses => 
        prevCourses.map(course => 
          course.id === courseId 
            ? { ...course, hasSubmittedFeedback: true }
            : course
        )
      );

      const token = Cookies.get('access_token');
      await axiosInstance.post(
        '/feedback/',
        {
          courseId: parseInt(courseId),
          feedback,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      
      // Success - optimistic update was correct, no need to refetch
    } catch (err: any) {
      console.error('Error submitting feedback:', err);
      // Revert optimistic update on error
      setCourses(prevCourses => 
        prevCourses.map(course => 
          course.id === courseId 
            ? { ...course, hasSubmittedFeedback: false }
            : course
        )
      );
      throw err;
    }
  };

  // Show admin dashboard for admin and faculty
  if (user?.role === 'admin' || user?.role === 'faculty') {
    return (
      <ProtectedRoute allowedRoles={['admin', 'faculty']}>
        <DashboardLayout>
          <AdminDashboard userRole={user?.role || 'faculty'} />
        </DashboardLayout>
      </ProtectedRoute>
    );
  }

  // Show student dashboard for students
  return (
    <ProtectedRoute allowedRoles={['student']}>
      <DashboardLayout>
        <div className="max-w-[1400px] mx-auto px-6 py-8">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-lg text-gray-600">Loading your courses...</div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
              <p className="font-semibold">Error loading courses</p>
              <p className="text-sm">{error}</p>
            </div>
          ) : (
            <StudentDashboard
              courses={courses}
              onSubmitFeedback={handleSubmitFeedback}
            />
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
