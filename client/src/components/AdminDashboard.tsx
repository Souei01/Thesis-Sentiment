'use client';

import { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  FileDown,
  Filter,
  SmilePlus,
  Frown,
  Meh,
  Star,
  Clock,
  MessageSquare,
} from 'lucide-react';
import axiosInstance from '@/lib/axios';
import CommentsWordCloud from '@/components/CommentsWordCloud';
import ModernKeywordCloud from '@/components/ModernKeywordCloud';
import EmotionRadarChart from '@/components/EmotionRadarChart';
import EmotionHeatmap from '@/components/EmotionHeatmap';
import TopicModelingDashboard from '@/components/TopicModelingDashboard';

interface FeedbackAnalytics {
  total_feedback: number;
  average_rating: number;
  message?: string;
  commitment: any;
  knowledge: any;
  independent_learning: any;
  management: any;
  feedback_assessment: any;
  overall: any;
  student_evaluation: any;
  course_info: any;
  text_feedback: any[];
}

interface Instructor {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  display_name?: string;
}

interface Course {
  id: number;
  code: string;
  name: string;
  department: string;
  year_level: number;
}

interface EmotionAnalytics {
  total_feedback: number;
  total_emotions_analyzed: number;
  emotion_distribution: {
    joy: number;
    satisfaction: number;
    acceptance: number;
    boredom: number;
    disappointment: number;
  };
  emotion_by_field: any;
  emotion_percentages: any;
}

interface TopicData {
  topics: Array<{ topic: string; keywords: string[] }>;
  topic_distribution: { [key: string]: number };
  total_topics: number;
  topic_insights?: Array<{
    topic: string;
    insights: Array<{
      category: string;
      priority: 'high' | 'medium' | 'low';
      suggestion: string;
      icon: string;
    }>;
  }>;
}

export default function AdminDashboard({ userRole = 'admin' }: { userRole?: string }) {
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSemester, setSelectedSemester] = useState('all');
  const [academicYear, setAcademicYear] = useState('all');
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [instructorId, setInstructorId] = useState('all');
  const [courseId, setCourseId] = useState('all');
  const [instructors, setInstructors] = useState<Instructor[]>([]);
  const [courses, setCourses] = useState<any[]>([]);
  const [availableYears, setAvailableYears] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [emotionData, setEmotionData] = useState<EmotionAnalytics | null>(null);
  const [topicData, setTopicData] = useState<TopicData | null>(null);
  const [emotionLoading, setEmotionLoading] = useState(false);
  const [topicLoading, setTopicLoading] = useState(false);
  const [exporting, setExporting] = useState(false);

  // Fetch instructors when department changes
  useEffect(() => {
    if (userRole === 'admin') {
      fetchInstructors();
    }
  }, [userRole, selectedDepartment]);

  // Fetch available years once
  useEffect(() => {
    if (userRole === 'admin') {
      fetchAvailableYears();
    }
  }, [userRole]);

  // Fetch courses when department or instructor changes
  useEffect(() => {
    fetchCourses();
  }, [selectedDepartment, instructorId]);

  const fetchInstructors = async () => {
    try {
      const params = new URLSearchParams({ role: 'faculty' });
      if (selectedDepartment && selectedDepartment !== 'all') {
        params.append('department', selectedDepartment);
      }
      
      const response = await axiosInstance.get(`/auth/users/?${params.toString()}`);
      setInstructors(response.data.data || response.data);
    } catch (error) {
      console.error('Error fetching instructors:', error);
    }
  };

  const fetchCourses = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedDepartment && selectedDepartment !== 'all') params.append('department', selectedDepartment);
      if (instructorId && instructorId !== 'all') params.append('instructor_id', instructorId);
      
      const response = await axiosInstance.get(`/feedback/courses/?${params.toString()}`);
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
      setCourses([]);
    }
  };

  const fetchAvailableYears = async () => {
    try {
      const response = await axiosInstance.get('/feedback/available-years/');
      setAvailableYears(response.data.years || []);
    } catch (error) {
      console.error('Error fetching available years:', error);
      // Fallback to current and next year
      const currentYear = new Date().getFullYear();
      const currentAcademicYear = `${currentYear}-${currentYear + 1}`;
      const nextAcademicYear = `${currentYear + 1}-${currentYear + 2}`;
      setAvailableYears([currentAcademicYear, nextAcademicYear]);
    }
  };

  // Fetch analytics data
  useEffect(() => {
    fetchAnalytics();
  }, [selectedSemester, academicYear, instructorId, selectedDepartment, courseId]);

  // Fetch emotion and topic data when switching tabs
  useEffect(() => {
    if (activeTab === 'emotions') {
      fetchEmotionAnalytics();
    } else if (activeTab === 'topics') {
      fetchTopicData();
    }
  }, [activeTab, selectedSemester, academicYear, instructorId, selectedDepartment, courseId]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (selectedSemester && selectedSemester !== 'all') params.append('semester', selectedSemester);
      if (academicYear && academicYear !== 'all') params.append('academic_year', academicYear);
      if (instructorId && instructorId !== 'all') params.append('instructor_id', instructorId);
      if (selectedDepartment && selectedDepartment !== 'all') params.append('department', selectedDepartment);
      if (courseId && courseId !== 'all') params.append('course_id', courseId);

      const response = await axiosInstance.get(`/feedback/analytics/?${params.toString()}`);
      setAnalytics(response.data);
    } catch (error: any) {
      console.error('Error fetching analytics:', error);
      setError(error.response?.data?.error || error.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const fetchEmotionAnalytics = async () => {
    setEmotionLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedSemester && selectedSemester !== 'all') params.append('semester', selectedSemester);
      if (academicYear && academicYear !== 'all') params.append('academic_year', academicYear);
      if (instructorId && instructorId !== 'all') params.append('instructor_id', instructorId);
      if (selectedDepartment && selectedDepartment !== 'all') params.append('department', selectedDepartment);
      if (courseId && courseId !== 'all') params.append('course_id', courseId);

      const response = await axiosInstance.get(`/emotions/analytics/?${params.toString()}`);
      setEmotionData(response.data);
    } catch (error: any) {
      console.error('Error fetching emotion analytics:', error);
    } finally {
      setEmotionLoading(false);
    }
  };

  const fetchTopicData = async () => {
    setTopicLoading(true);
    try {
      const response = await axiosInstance.get('/topics/');
      setTopicData(response.data);
    } catch (error: any) {
      console.error('Error fetching topic data:', error);
    } finally {
      setTopicLoading(false);
    }
  };

  const handleExportReport = async () => {
    setExporting(true);
    try {
      const params = new URLSearchParams();
      if (selectedSemester && selectedSemester !== 'all') params.append('semester', selectedSemester);
      if (academicYear && academicYear !== 'all') params.append('academic_year', academicYear);
      if (instructorId && instructorId !== 'all') params.append('instructor_id', instructorId);
      if (selectedDepartment && selectedDepartment !== 'all') params.append('department', selectedDepartment);
      if (courseId && courseId !== 'all') params.append('course_id', courseId);

      const response = await axiosInstance.get(`/feedback/export-pdf/?${params.toString()}`, {
        responseType: 'blob',
      });

      // Create download link
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename based on filters
      let filename = 'feedback-report';
      if (instructorId && instructorId !== 'all') {
        const instructor = instructors.find(i => i.id.toString() === instructorId);
        if (instructor) {
          filename += `-${instructor.first_name}-${instructor.last_name}`;
        }
      } else {
        filename += '-overall';
      }
      if (selectedSemester && selectedSemester !== 'all') filename += `-${selectedSemester}`;
      if (academicYear && academicYear !== 'all') filename += `-${academicYear}`;
      filename += '.pdf';
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Error exporting report:', error);
      alert('Failed to export report. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  // Cascading filter handlers
  const handleDepartmentChange = (value: string) => {
    setSelectedDepartment(value);
    // Reset dependent filters
    setInstructorId('all');
    setCourseId('all');
  };

  const handleInstructorChange = (value: string) => {
    setInstructorId(value);
    // Reset course filter
    setCourseId('all');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-[1400px] mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
            <p className="font-semibold">Error loading analytics</p>
            <p className="text-sm">{error}</p>
            <Button
              onClick={fetchAnalytics}
              className="mt-4 bg-red-600 hover:bg-red-700"
            >
              Retry
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-[1400px] mx-auto">
          <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-lg p-6 text-center">
            <p className="font-semibold text-lg mb-2">No Feedback Data Available</p>
            <p className="text-sm mb-4">
              No feedback data available for the selected filters. Try adjusting your filters or wait for students to submit feedback.
            </p>
            <Button
              onClick={fetchAnalytics}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Refresh
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Prepare chart data from analytics
  const commitmentData = [
    { name: 'Sensitivity', value: analytics.commitment?.sensitivity || 0 },
    { name: 'Integration', value: analytics.commitment?.integration || 0 },
    { name: 'Availability', value: analytics.commitment?.availability || 0 },
    { name: 'Punctuality', value: analytics.commitment?.punctuality || 0 },
    { name: 'Record Keeping', value: analytics.commitment?.record_keeping || 0 },
  ];

  const knowledgeData = [
    { name: 'Mastery', value: analytics.knowledge?.mastery || 0 },
    { name: 'State of Art', value: analytics.knowledge?.state_of_art || 0 },
    { name: 'Practical', value: analytics.knowledge?.practical_integration || 0 },
    { name: 'Relevance', value: analytics.knowledge?.relevance || 0 },
    { name: 'Trends', value: analytics.knowledge?.current_trends || 0 },
  ];

  const managementData = [
    { name: 'Contribution', value: analytics.management?.student_contribution || 0 },
    { name: 'Facilitator', value: analytics.management?.facilitator_role || 0 },
    { name: 'Discussion', value: analytics.management?.discussion_encouragement || 0 },
    { name: 'Methods', value: analytics.management?.instructional_methods || 0 },
    { name: 'Materials', value: analytics.management?.instructional_materials || 0 },
  ];

  const courseInfoData = [
    { name: 'Syllabus Explained', value: analytics.course_info?.syllabus_explained || 0, color: '#22c55e' },
    { name: 'Delivered as Outlined', value: analytics.course_info?.delivered_as_outlined || 0, color: '#3b82f6' },
    { name: 'Grading Explained', value: analytics.course_info?.grading_criteria_explained || 0, color: '#a855f7' },
    { name: 'Exams Related', value: analytics.course_info?.exams_related || 0, color: '#f59e0b' },
    { name: 'Assignments Related', value: analytics.course_info?.assignments_related || 0, color: '#ef4444' },
    { name: 'LMS Useful', value: analytics.course_info?.lms_resources_useful || 0, color: '#14b8a6' },
  ];

  const allRatingsData = [
    { subject: 'Commitment', value: (commitmentData.reduce((a, b) => a + b.value, 0) / commitmentData.length) || 0 },
    { subject: 'Knowledge', value: (knowledgeData.reduce((a, b) => a + b.value, 0) / knowledgeData.length) || 0 },
    { subject: 'Learning', value: analytics.independent_learning?.teaching_strategies || 0 },
    { subject: 'Management', value: (managementData.reduce((a, b) => a + b.value, 0) / managementData.length) || 0 },
    { subject: 'Feedback', value: analytics.feedback_assessment?.clear_communication || 0 },
  ];

  const sentimentData = useMemo(() => {
    if (!analytics) {
      return { positive: 0, neutral: 0, negative: 0 };
    }
    
    // Use emotion data if available, otherwise fallback to sentiment_score
    if (emotionData && emotionData.emotion_distribution) {
      const emotions = emotionData.emotion_distribution;
      return {
        positive: emotions.joy + emotions.satisfaction,
        neutral: emotions.acceptance,
        negative: emotions.boredom + emotions.disappointment,
      };
    }
    
    // Fallback to sentiment_score from text feedback
    if (!analytics.text_feedback || analytics.text_feedback.length === 0) {
      return { positive: 0, neutral: 0, negative: 0 };
    }
    
    return analytics.text_feedback.reduce((acc: any, fb: any) => {
      if (fb.sentiment_score > 0) acc.positive++;
      else if (fb.sentiment_score < 0) acc.negative++;
      else acc.neutral++;
      return acc;
    }, { positive: 0, neutral: 0, negative: 0 });
  }, [emotionData, analytics]);

  const sentimentDistributionData = useMemo(() => [
    { name: 'Positive', value: sentimentData.positive, color: '#22c55e' },
    { name: 'Neutral', value: sentimentData.neutral, color: '#eab308' },
    { name: 'Negative', value: sentimentData.negative, color: '#ef4444' },
  ], [sentimentData]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-[1400px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <div className="flex items-center gap-4">
              <Button 
                size="sm" 
                className="gap-2 bg-[#8E1B1B] hover:bg-[#6B1414]"
                onClick={handleExportReport}
                disabled={exporting || !analytics || analytics.total_feedback === 0}
              >
                <FileDown className="h-4 w-4" />
                {exporting ? 'Exporting...' : 'Export Report'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1400px] mx-auto px-6 py-6">
        {/* Overview Tabs */}
        <div className="flex gap-4 mb-6">
          <Button 
            variant={activeTab === 'overview' ? 'default' : 'ghost'}
            className={activeTab === 'overview' ? 'bg-white text-gray-900 hover:bg-gray-100 border-b-2 border-[#8E1B1B]' : 'text-gray-500'}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </Button>
          <Button 
            variant={activeTab === 'analytics' ? 'default' : 'ghost'}
            className={activeTab === 'analytics' ? 'bg-white text-gray-900 hover:bg-gray-100 border-b-2 border-[#8E1B1B]' : 'text-gray-500'}
            onClick={() => setActiveTab('analytics')}
          >
            Analytics
          </Button>
          <Button 
            variant={activeTab === 'emotions' ? 'default' : 'ghost'}
            className={activeTab === 'emotions' ? 'bg-white text-gray-900 hover:bg-gray-100 border-b-2 border-[#8E1B1B]' : 'text-gray-500'}
            onClick={() => setActiveTab('emotions')}
          >
            Emotions
          </Button>
          <Button 
            variant={activeTab === 'topics' ? 'default' : 'ghost'}
            className={activeTab === 'topics' ? 'bg-white text-gray-900 hover:bg-gray-100 border-b-2 border-[#8E1B1B]' : 'text-gray-500'}
            onClick={() => setActiveTab('topics')}
          >
            Topics
          </Button>
        </div>

        {/* Filters Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Filters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Semester Filter */}
              <div className="space-y-2">
                <Label htmlFor="semester">Semester</Label>
                <Select value={selectedSemester} onValueChange={setSelectedSemester}>
                  <SelectTrigger id="semester">
                    <SelectValue placeholder="All Semesters" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Semesters</SelectItem>
                    <SelectItem value="1st">1st Semester</SelectItem>
                    <SelectItem value="2nd">2nd Semester</SelectItem>
                    <SelectItem value="Summer">Summer</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Academic Year Filter */}
              <div className="space-y-2">
                <Label htmlFor="academicYear">Academic Year</Label>
                <Select value={academicYear} onValueChange={setAcademicYear}>
                  <SelectTrigger id="academicYear">
                    <SelectValue placeholder="All Years" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Years</SelectItem>
                    {availableYears.map((year) => (
                      <SelectItem key={year} value={year}>
                        {year}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Instructor Filter (Admin only) */}
              {userRole === 'admin' && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="department">Department</Label>
                    <Select value={selectedDepartment} onValueChange={handleDepartmentChange}>
                      <SelectTrigger id="department">
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
                  
                  <div className="space-y-2">
                    <Label htmlFor="instructor">Instructor</Label>
                    <Select value={instructorId} onValueChange={handleInstructorChange}>
                      <SelectTrigger id="instructor">
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
                  
                  <div className="space-y-2">
                    <Label htmlFor="course">Course/Subject</Label>
                    <Select value={courseId} onValueChange={setCourseId}>
                      <SelectTrigger id="course">
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
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Overview Tab Content */}
        {activeTab === 'overview' && (
          <>
            {/* No Data Banner */}
            {analytics.total_feedback === 0 && (
              <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg p-4 mb-6">
                <p className="font-semibold">No feedback data matches your current filters</p>
                <p className="text-sm mt-1">Try adjusting your filters above to see feedback data, or wait for students to submit feedback.</p>
              </div>
            )}

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Feedback
              </CardTitle>
              <Activity className="h-4 w-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{analytics.total_feedback}</div>
              <p className="text-xs text-gray-500 mt-1">
                Responses collected
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Average Rating
              </CardTitle>
              <Star className="h-4 w-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{analytics.average_rating?.toFixed(2) || 'N/A'}</div>
              <p className="text-xs text-gray-500 mt-1">
                Out of 5.0
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Positive Sentiment
              </CardTitle>
              <SmilePlus className="h-4 w-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">+{sentimentData.positive}</div>
              <p className="text-xs text-gray-500 mt-1">
                {analytics.text_feedback && analytics.text_feedback.length > 0 
                  ? `${((sentimentData.positive / analytics.text_feedback.length) * 100).toFixed(1)}% of responses`
                  : 'No responses yet'
                }
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Avg Hours/Week
              </CardTitle>
              <Clock className="h-4 w-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{analytics.overall?.hours_per_week?.toFixed(1) || 'N/A'}</div>
              <p className="text-xs text-gray-500 mt-1">
                Study time outside class
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Bento Grid Layout - Charts */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-6 mb-6">
          {/* Commitment - 2 columns */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Commitment to Teaching</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={commitmentData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 5]} />
                  <YAxis dataKey="name" type="category" width={90} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8E1B1B" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Knowledge - 2 columns */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Knowledge of Subject</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={knowledgeData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 5]} />
                  <YAxis dataKey="name" type="category" width={90} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Sentiment Distribution - 2 columns */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Sentiment Distribution</CardTitle>
              <CardDescription className="text-xs">
                Positive (Joy + Satisfaction), Neutral (Acceptance), Negative (Boredom + Disappointment)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={sentimentDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sentimentDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Second Row - Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-6 mb-6">
          {/* Management - 3 columns */}
          <Card className="md:col-span-3">
            <CardHeader>
              <CardTitle className="text-base">Management of Learning</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={managementData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-20} textAnchor="end" height={70} tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 5]} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* All Areas Radar - 3 columns */}
          <Card className="md:col-span-3">
            <CardHeader>
              <CardTitle className="text-base">Overall Performance Radar</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={allRatingsData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 5]} />
                  <Radar
                    name="Rating"
                    dataKey="value"
                    stroke="#8E1B1B"
                    fill="#8E1B1B"
                    fillOpacity={0.6}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Third Row - Course Info */}
        <div className="grid grid-cols-1 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle>Course Information Agreement (% of Students)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={courseInfoData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-15} textAnchor="end" height={80} />
                  <YAxis domain={[0, 100]} label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip formatter={(value) => `${Number(value).toFixed(1)}%`} />
                  <Bar dataKey="value">
                    {courseInfoData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
          </>
        )}

        {/* Analytics Tab Content */}
        {activeTab === 'analytics' && (
          <>
        {/* Modern Keyword Analysis */}
        {analytics.text_feedback && analytics.text_feedback.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Keyword Analysis ({analytics.text_feedback.length} comments)
              </CardTitle>
              <CardDescription>
                Most frequently mentioned words from student feedback, grouped by sentiment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ModernKeywordCloud comments={analytics.text_feedback} />
            </CardContent>
          </Card>
        )}
          </>
        )}

        {/* Emotions Tab */}
        {activeTab === 'emotions' && (
          <div className="space-y-6">
            {emotionLoading ? (
              <div className="flex items-center justify-center py-20">
                <div className="text-lg text-gray-600">Loading emotion analytics...</div>
              </div>
            ) : emotionData ? (
              <>
                <EmotionRadarChart
                  emotionDistribution={emotionData.emotion_distribution}
                  totalEmotions={emotionData.total_emotions_analyzed}
                  emotionByField={emotionData.emotion_by_field}
                />
                <EmotionHeatmap
                  emotionByField={emotionData.emotion_by_field}
                  totalEmotions={emotionData.total_emotions_analyzed}
                />
              </>
            ) : (
              <Card>
                <CardContent className="py-10 text-center text-gray-500">
                  No emotion data available. Students need to submit feedback first.
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Topics Tab */}
        {activeTab === 'topics' && (
          <div>
            {topicLoading ? (
              <div className="flex items-center justify-center py-20">
                <div className="text-lg text-gray-600">Loading topic modeling data...</div>
              </div>
            ) : topicData ? (
              <TopicModelingDashboard
                topics={topicData.topics}
                topicDistribution={topicData.topic_distribution}
                totalTopics={topicData.total_topics}
                topicInsights={topicData.topic_insights}
              />
            ) : (
              <Card>
                <CardContent className="py-10 text-center text-gray-500">
                  No topic modeling data available. Please run topic modeling analysis first.
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
