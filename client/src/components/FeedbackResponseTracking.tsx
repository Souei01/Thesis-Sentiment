'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import axiosInstance from '@/lib/axios';
import { Users, CheckCircle, XCircle, TrendingUp, Clock } from 'lucide-react';

interface ResponseStats {
  total_students: number;
  total_responses: number;
  response_rate: number;
  respondents: Array<{
    id: number;
    name: string;
    email: string;
    student_id: string;
    submitted_at: string;
    course: string;
    section: string;
  }>;
  non_respondents: Array<{
    id: number;
    name: string;
    email: string;
    student_id: string;
    course: string;
    section: string;
  }>;
  submissions_over_time: Array<{
    date: string;
    count: number;
  }>;
}

interface Instructor {
  id: number;
  first_name: string;
  last_name: string;
  display_name: string;
}

interface Course {
  id: number;
  code: string;
  name: string;
}

export default function FeedbackResponseTracking({ userRole }: { userRole: string }) {
  const [stats, setStats] = useState<ResponseStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [semester, setSemester] = useState<string>('1st');
  const [academicYear, setAcademicYear] = useState<string>('2024-2025');
  const [instructorId, setInstructorId] = useState<string>('');
  const [courseId, setCourseId] = useState<string>('');
  const [department, setDepartment] = useState<string>('');
  const [instructors, setInstructors] = useState<Instructor[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [activeTab, setActiveTab] = useState<'respondents' | 'non-respondents'>('respondents');

  useEffect(() => {
    if (userRole === 'admin') {
      fetchInstructors();
    }
  }, [userRole, department]);

  useEffect(() => {
    fetchCourses();
  }, [instructorId, department]);

  useEffect(() => {
    fetchResponseStats();
  }, [semester, academicYear, instructorId, courseId, department]);

  const fetchInstructors = async () => {
    try {
      const params = new URLSearchParams({ role: 'faculty' });
      if (department && department !== 'all') params.append('department', department);
      
      const response = await axiosInstance.get(`/auth/users/?${params.toString()}`);
      setInstructors(response.data.data || response.data);
    } catch (error) {
      console.error('Error fetching instructors:', error);
    }
  };

  const fetchCourses = async () => {
    try {
      const params = new URLSearchParams();
      if (instructorId && instructorId !== 'all') params.append('instructor_id', instructorId);
      if (department && department !== 'all') params.append('department', department);
      
      const response = await axiosInstance.get(`/feedback/courses/?${params.toString()}`);
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
      setCourses([]);
    }
  };

  const fetchResponseStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (semester && semester !== 'all') params.append('semester', semester);
      if (academicYear && academicYear !== 'all') params.append('academic_year', academicYear);
      if (instructorId && instructorId !== 'all') params.append('instructor_id', instructorId);
      if (courseId && courseId !== 'all') params.append('course_id', courseId);
      if (department && department !== 'all') params.append('department', department);

      const response = await axiosInstance.get(`/feedback/response-stats/?${params.toString()}`);
      setStats(response.data);
    } catch (error: any) {
      console.error('Error fetching response stats:', error);
      setError(error.response?.data?.error || error.message || 'Failed to load response statistics');
    } finally {
      setLoading(false);
    }
  };

  const handleDepartmentChange = (value: string) => {
    setDepartment(value);
    setInstructorId('');
    setCourseId('');
  };

  const handleInstructorChange = (value: string) => {
    setInstructorId(value);
    setCourseId('');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading response statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
          <p className="font-semibold">Error loading statistics</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">No data available</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Feedback Response Tracking</h1>
          <p className="text-gray-500">Monitor student feedback submission rates</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {userRole === 'admin' && (
              <div>
                <Label>Department</Label>
                <Select value={department} onValueChange={handleDepartmentChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Departments" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Departments</SelectItem>
                    <SelectItem value="CS">Computer Science</SelectItem>
                    <SelectItem value="IT">Information Technology</SelectItem>
                    <SelectItem value="ACT">Associate in Computer Technology</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            {userRole === 'admin' && (
              <div>
                <Label>Instructor</Label>
                <Select value={instructorId} onValueChange={handleInstructorChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Instructors" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Instructors</SelectItem>
                    {instructors.map((instructor) => (
                      <SelectItem key={instructor.id} value={instructor.id.toString()}>
                        {instructor.display_name || `${instructor.first_name} ${instructor.last_name}`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div>
              <Label>Course</Label>
              <Select value={courseId} onValueChange={setCourseId}>
                <SelectTrigger>
                  <SelectValue placeholder="All Courses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Courses</SelectItem>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id.toString()}>
                      {course.code} - {course.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Semester</Label>
              <Select value={semester} onValueChange={setSemester}>
                <SelectTrigger>
                  <SelectValue placeholder="Select semester" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Semesters</SelectItem>
                  <SelectItem value="1st">1st Semester</SelectItem>
                  <SelectItem value="2nd">2nd Semester</SelectItem>
                  <SelectItem value="Summer">Summer</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Academic Year</Label>
              <Select value={academicYear} onValueChange={setAcademicYear}>
                <SelectTrigger>
                  <SelectValue placeholder="Select year" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Years</SelectItem>
                  <SelectItem value="2024-2025">2024-2025</SelectItem>
                  <SelectItem value="2023-2024">2023-2024</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Total Students</CardTitle>
            <Users className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.total_students}</p>
            <p className="text-xs text-gray-500 mt-1">Students invited</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Responses</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">{stats.total_responses}</p>
            <p className="text-xs text-gray-500 mt-1">Feedback submitted</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Response Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-600">{stats.response_rate.toFixed(1)}%</p>
            <p className="text-xs text-gray-500 mt-1">Completion percentage</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Pending</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-red-600">{stats.non_respondents.length}</p>
            <p className="text-xs text-gray-500 mt-1">Not yet submitted</p>
          </CardContent>
        </Card>
      </div>

      {/* Submissions Over Time */}
      {stats.submissions_over_time.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Submissions Over Time</CardTitle>
            <CardDescription>Daily submission count</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {stats.submissions_over_time.map((day, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span className="text-sm">{new Date(day.date).toLocaleDateString()}</span>
                  </div>
                  <span className="font-semibold">{day.count} submissions</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs for Respondents and Non-Respondents */}
      <Card>
        <CardHeader>
          <div className="flex gap-4 border-b">
            <button
              className={`pb-2 px-4 font-medium ${
                activeTab === 'respondents'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab('respondents')}
            >
              Respondents ({stats.respondents.length})
            </button>
            <button
              className={`pb-2 px-4 font-medium ${
                activeTab === 'non-respondents'
                  ? 'text-red-600 border-b-2 border-red-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab('non-respondents')}
            >
              Non-Respondents ({stats.non_respondents.length})
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Student ID</th>
                  <th className="text-left py-3 px-4">Name</th>
                  <th className="text-left py-3 px-4">Email</th>
                  <th className="text-left py-3 px-4">Course</th>
                  <th className="text-left py-3 px-4">Section</th>
                  {activeTab === 'respondents' && <th className="text-left py-3 px-4">Submitted At</th>}
                </tr>
              </thead>
              <tbody>
                {activeTab === 'respondents' ? (
                  stats.respondents.length > 0 ? (
                    stats.respondents.map((student) => (
                      <tr key={student.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">{student.student_id}</td>
                        <td className="py-3 px-4">{student.name}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">{student.email}</td>
                        <td className="py-3 px-4">{student.course}</td>
                        <td className="py-3 px-4">{student.section}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {new Date(student.submitted_at).toLocaleString()}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-500">
                        No responses yet
                      </td>
                    </tr>
                  )
                ) : (
                  stats.non_respondents.length > 0 ? (
                    stats.non_respondents.map((student) => (
                      <tr key={student.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">{student.student_id}</td>
                        <td className="py-3 px-4">{student.name}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">{student.email}</td>
                        <td className="py-3 px-4">{student.course}</td>
                        <td className="py-3 px-4">{student.section}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-gray-500">
                        All students have responded!
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
