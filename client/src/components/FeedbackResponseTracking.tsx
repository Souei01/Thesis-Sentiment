'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import axiosInstance from '@/lib/axios';
import { Users, CheckCircle, XCircle, TrendingUp, Clock, Search, ChevronLeft, ChevronRight } from 'lucide-react';

interface ResponseStats {
  total_students: number;
  total_enrollments: number;
  total_completed: number;
  response_rate: number;
  respondents: Array<{
    id: number;
    name: string;
    email: string;
    student_id: string;
    completed: number;
    total: number;
    progress: string;
    completion_rate: number;
    status: string;
    feedbacks: Array<{
      course: string;
      section: string;
      submitted: boolean;
      submitted_at: string | null;
    }>;
  }>;
  non_respondents: Array<{
    id: number;
    name: string;
    email: string;
    student_id: string;
    completed: number;
    total: number;
    progress: string;
    completion_rate: number;
    status: string;
    feedbacks: Array<{
      course: string;
      section: string;
      submitted: boolean;
      submitted_at: string | null;
    }>;
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
  
  // Pagination and search states
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage, setItemsPerPage] = useState<number>(10);
  const [yearFilter, setYearFilter] = useState<string>('all');
  const [sectionFilter, setSectionFilter] = useState<string>('all');

  useEffect(() => {
    if (userRole === 'admin') {
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
      fetchInstructors();
    }
  }, [userRole, department]);

  useEffect(() => {
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
    fetchCourses();
  }, [instructorId, department]);

  useEffect(() => {
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
        
        // Ensure arrays exist even if empty
        const data = response.data;
        setStats({
          total_students: data.total_students || 0,
          total_responses: data.total_responses || 0,
          response_rate: data.response_rate || 0,
          respondents: data.respondents || [],
          non_respondents: data.non_respondents || [],
          submissions_over_time: data.submissions_over_time || []
        });
      } catch (error: any) {
        console.error('Error fetching response stats:', error);
        setError(error.response?.data?.error || error.message || 'Failed to load response statistics');
        // Set empty stats on error
        setStats({
          total_students: 0,
          total_responses: 0,
          response_rate: 0,
          respondents: [],
          non_respondents: [],
          submissions_over_time: []
        });
      } finally {
        setLoading(false);
      }
    };
    fetchResponseStats();
  }, [semester, academicYear, instructorId, courseId, department]);

  // Reset to page 1 when search or tab changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, activeTab]);

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

  // Filter and paginate data
  // Filter by search query
  if (!stats) return null;
  
  const currentData = activeTab === 'respondents' ? (stats.respondents || []) : (stats.non_respondents || []);
  
  // Filter data with validation
  const filteredData = currentData.filter(student => {
    // Search query filter with validation
    if (searchQuery && searchQuery.trim().length > 0) {
      const query = searchQuery.toLowerCase().trim();
      
      // Validate search query - only allow alphanumeric, spaces, @, ., -
      if (!/^[a-zA-Z0-9\s@.\-]+$/.test(query)) {
        return false;
      }
      
      const matchesSearch = 
        student.name?.toLowerCase().includes(query) ||
        student.email?.toLowerCase().includes(query) ||
        student.student_id?.toLowerCase().includes(query) ||
        student.feedbacks?.some(f => 
          f.course?.toLowerCase().includes(query) ||
          f.section?.toLowerCase().includes(query)
        );
      
      if (!matchesSearch) return false;
    }
    
    // Year level filter
    if (yearFilter && yearFilter !== 'all') {
      const hasMatchingYear = student.feedbacks?.some(f => {
        // Extract year from course code (e.g., "CS301" -> 3rd year)
        const match = f.course?.match(/[A-Z]+(\d)/);
        if (match) {
          const yearLevel = match[1];
          return yearLevel === yearFilter;
        }
        return false;
      });
      if (!hasMatchingYear) return false;
    }
    
    // Section filter
    if (sectionFilter && sectionFilter !== 'all') {
      const hasMatchingSection = student.feedbacks?.some(f => 
        f.section === sectionFilter
      );
      if (!hasMatchingSection) return false;
    }
    
    return true;
  });
  
  // Pagination calculations
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedData = filteredData.slice(startIndex, endIndex);
  
  const currentDataLength = currentData.length;

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
          {/* Search Bar, Filters, and Items Per Page */}
          <div className="flex items-center justify-between mb-4 gap-4 flex-wrap">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search by name, email, or student ID..."
                value={searchQuery}
                onChange={(e) => {
                  const value = e.target.value;
                  // Only allow alphanumeric, spaces, @, ., -
                  if (value === '' || /^[a-zA-Z0-9\s@.\-]*$/.test(value)) {
                    setSearchQuery(value);
                  }
                }}
                className="pl-10"
                maxLength={50}
              />
            </div>
            
            {/* Year Filter */}
            <div className="flex items-center gap-2">
              <Label className="text-sm text-gray-600">Year:</Label>
              <Select value={yearFilter} onValueChange={setYearFilter}>
                <SelectTrigger className="w-24">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="1">1st</SelectItem>
                  <SelectItem value="2">2nd</SelectItem>
                  <SelectItem value="3">3rd</SelectItem>
                  <SelectItem value="4">4th</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Section Filter */}
            <div className="flex items-center gap-2">
              <Label className="text-sm text-gray-600">Section:</Label>
              <Select value={sectionFilter} onValueChange={setSectionFilter}>
                <SelectTrigger className="w-24">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="A">A</SelectItem>
                  <SelectItem value="B">B</SelectItem>
                  <SelectItem value="C">C</SelectItem>
                  <SelectItem value="D">D</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center gap-2">
              <Label className="text-sm text-gray-600">Show:</Label>
              <Select value={itemsPerPage.toString()} onValueChange={(val) => setItemsPerPage(Number(val))}>
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="25">25</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Results Info */}
          <div className="text-sm text-gray-600 mb-2">
            Showing {startIndex + 1} to {Math.min(endIndex, filteredData.length)} of {filteredData.length} 
            {searchQuery && ` (filtered from ${currentDataLength} total)`}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Student ID</th>
                  <th className="text-left py-3 px-4">Name</th>
                  <th className="text-left py-3 px-4">Email</th>
                  <th className="text-left py-3 px-4">Progress</th>
                  <th className="text-left py-3 px-4">Completion</th>
                  <th className="text-left py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody>
                {paginatedData.length > 0 ? (
                  paginatedData.map((student) => (
                    <tr key={student.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">{student.student_id}</td>
                      <td className="py-3 px-4">{student.name}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{student.email}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{(student as any).progress}</span>
                          <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-green-500 transition-all"
                              style={{ width: `${(student as any).completion_rate}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm font-medium">{(student as any).completion_rate.toFixed(1)}%</span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          (student as any).status === 'Complete' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {(student as any).status}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-gray-500">
                      {searchQuery ? 'No results found for your search' : activeTab === 'respondents' ? 'No responses yet' : 'All students have responded!'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-600">
                Page {currentPage} of {totalPages}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
                
                {/* Page Numbers */}
                <div className="flex gap-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    
                    return (
                      <Button
                        key={pageNum}
                        variant={currentPage === pageNum ? "default" : "outline"}
                        size="sm"
                        onClick={() => setCurrentPage(pageNum)}
                        className="w-10"
                      >
                        {pageNum}
                      </Button>
                    );
                  })}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
