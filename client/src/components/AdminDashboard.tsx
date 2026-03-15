'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from '@/components/ui/chart';
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
  BarChart3,
  Brain,
  Layers,
  LayoutDashboard,
  RefreshCw,
  ChevronRight,
  Sparkles,
  GraduationCap,
  ArrowUpRight,
  Heart,
  BookOpen,
  Target,
  Gauge,
  PieChart as PieChartIcon,
  FileCheck,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Spinner } from '@/components/ui/spinner';
import axiosInstance from '@/lib/axios';
import CommentsWordCloud from '@/components/CommentsWordCloud';
import ModernKeywordCloud from '@/components/ModernKeywordCloud';
import EmotionRadarChart from '@/components/EmotionRadarChart';
import EmotionHeatmap from '@/components/EmotionHeatmap';
import TopicModelingDashboard from '@/components/TopicModelingDashboard';
import RevisionAnalysis from '@/components/RevisionAnalysis';

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

interface AdminDashboardProps {
  userRole?: string;
  user?: {
    id: number;
    email: string;
    department?: string;
    role: string;
  } | null;
}

export default function AdminDashboard({ userRole = 'admin', user }: AdminDashboardProps) {
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSemester, setSelectedSemester] = useState('all');
  const [academicYear, setAcademicYear] = useState('all');
  
  // Determine if user is department head and their department
  const isDepartmentHead = user?.email?.includes('.head@wmsu.edu.ph');
  // Extract department from email (e.g., cs.head@wmsu.edu.ph -> CS)
  const emailDepartment = isDepartmentHead && user?.email ? user.email.split('.')[0].toUpperCase() : null;
  const userDepartment = emailDepartment || user?.department;
  
  // IT head can filter IT and ACT, CS head can only see CS
  const isITHead = isDepartmentHead && userDepartment === 'IT';
  const isCSHead = isDepartmentHead && userDepartment === 'CS';
  
  console.log('User:', user);
  console.log('Is Department Head:', isDepartmentHead);
  console.log('Email Department:', emailDepartment);
  console.log('User Department:', userDepartment);
  console.log('Is IT Head:', isITHead);
  console.log('Is CS Head:', isCSHead);
  console.log('User Role:', userRole);
  
  // CS head always locked to CS department, IT head defaults to 'all' (which means IT+ACT for them)
  const [selectedDepartment, setSelectedDepartment] = useState(
    isCSHead ? 'CS' : (isITHead ? 'all' : (isDepartmentHead && userDepartment ? userDepartment : 'all'))
  );
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

  // Set department to CS when CS head user is loaded
  useEffect(() => {
    if (isCSHead && selectedDepartment !== 'CS') {
      setSelectedDepartment('CS');
    }
  }, [isCSHead]);

  // Fetch instructors when department changes
  useEffect(() => {
    if (userRole === 'admin' || isDepartmentHead) {
      fetchInstructors();
    }
  }, [userRole, selectedDepartment, isDepartmentHead, isITHead, isCSHead]);

  // Fetch available years once
  useEffect(() => {
    if (userRole === 'admin') {
      fetchAvailableYears();
    }
  }, [userRole]);

  // Fetch courses when department or instructor changes
  useEffect(() => {
    if (userRole === 'admin' || isDepartmentHead) {
      fetchCourses();
    }
  }, [selectedDepartment, instructorId, isITHead, isCSHead, userRole, isDepartmentHead]);

  // Fetch courses for faculty users (filtered by their instructor_id)
  useEffect(() => {
    if (userRole === 'faculty' && user?.id) {
      fetchFacultyCourses();
    }
  }, [userRole, user?.id]);

  const fetchInstructors = async () => {
    try {
      console.log('🔍 Fetching instructors START');
      console.log('  - isITHead:', isITHead);
      console.log('  - isCSHead:', isCSHead);
      console.log('  - isDepartmentHead:', isDepartmentHead);
      console.log('  - selectedDepartment:', selectedDepartment);
      console.log('  - userRole:', userRole);
      
      const params = new URLSearchParams({ role: 'faculty' });
      
      // Filter by department based on user role
      if (isCSHead) {
        // CS head can only see CS instructors
        console.log('  - Mode: CS Head');
        params.append('department', 'CS');
      } else if (isITHead) {
        // IT head can see IT or ACT instructors based on selected department
        console.log('  - Mode: IT Head');
        if (selectedDepartment && selectedDepartment !== 'all') {
          console.log('  - Filtering by specific dept:', selectedDepartment);
          params.append('department', selectedDepartment);
        } else {
          // If "all" selected for IT head, don't send department param
          // Backend will automatically filter IT+ACT based on user's subrole
          console.log('  - Fetching IT+ACT instructors (via backend subrole)');
        }
      } else if (selectedDepartment && selectedDepartment !== 'all') {
        // Admin can filter by any department
        console.log('  - Mode: Admin with dept filter');
        params.append('department', selectedDepartment);
      } else {
        console.log('  - Mode: Admin without filter');
      }
      
      console.log('📡 API call URL:', `/auth/users/?${params.toString()}`);
      const response = await axiosInstance.get(`/auth/users/?${params.toString()}`);
      console.log('✅ Full response:', response.data);
      console.log('✅ Instructors array:', response.data.data || response.data);
      console.log('✅ Instructors count:', (response.data.data || response.data)?.length || 0);
      
      const instructorsList = response.data.data || response.data;
      setInstructors(Array.isArray(instructorsList) ? instructorsList : []);
    } catch (error) {
      console.error('❌ Error fetching instructors:', error);
      setInstructors([]);
    }
  };

  const fetchCourses = async () => {
    try {
      console.log('📚 Fetching courses START');
      console.log('  - isITHead:', isITHead);
      console.log('  - isCSHead:', isCSHead);
      console.log('  - selectedDepartment:', selectedDepartment);
      console.log('  - instructorId:', instructorId);
      
      const params = new URLSearchParams();
      
      // Filter by department based on user role
      if (isCSHead) {
        // CS head can only see CS courses
        console.log('  - Mode: CS Head');
        params.append('department', 'CS');
      } else if (isITHead) {
        // IT head can see IT or ACT courses based on selected department
        console.log('  - Mode: IT Head');
        if (selectedDepartment && selectedDepartment !== 'all') {
          console.log('  - Filtering by specific dept:', selectedDepartment);
          params.append('department', selectedDepartment);
        } else {
          // If "all" selected for IT head, don't send department param
          // Backend will automatically filter IT+ACT based on user's subrole
          console.log('  - Fetching IT+ACT courses (via backend subrole)');
        }
      } else if (selectedDepartment && selectedDepartment !== 'all') {
        // Admin can filter by any department
        console.log('  - Mode: Admin with dept filter');
        params.append('department', selectedDepartment);
      } else {
        console.log('  - Mode: Admin without filter');
      }
      
      if (instructorId && instructorId !== 'all') {
        console.log('  - Filtering by instructor:', instructorId);
        params.append('instructor_id', instructorId);
      }
      
      console.log('📡 Courses API URL:', `/feedback/courses/?${params.toString()}`);
      const response = await axiosInstance.get(`/feedback/courses/?${params.toString()}`);
      console.log('✅ Full courses response:', response.data);
      console.log('✅ Courses array:', response.data.courses);
      console.log('✅ Courses count:', response.data.courses?.length || 0);
      
      setCourses(Array.isArray(response.data.courses) ? response.data.courses : []);
    } catch (error) {
      console.error('❌ Error fetching courses:', error);
      setCourses([]);
    }
  };

  const fetchFacultyCourses = async () => {
    try {
      console.log('📚 Fetching faculty courses START');
      console.log('  - Faculty user ID:', user?.id);
      
      // Don't send instructor_id parameter - let the backend automatically filter by authenticated user
      const params = new URLSearchParams();
      
      console.log('📡 Faculty Courses API URL:', `/feedback/courses/?${params.toString()}`);
      const response = await axiosInstance.get(`/feedback/courses/?${params.toString()}`);
      console.log('✅ Faculty courses response:', response.data);
      console.log('✅ Faculty courses count:', response.data.courses?.length || 0);
      
      setCourses(Array.isArray(response.data.courses) ? response.data.courses : []);
    } catch (error) {
      console.error('❌ Error fetching faculty courses:', error);
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
    // Use isRefreshing if we already have data, otherwise use loading for initial load
    if (analytics) {
      setIsRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);
    try {
      const params = new URLSearchParams();
      if (selectedSemester && selectedSemester !== 'all') params.append('semester', selectedSemester);
      if (academicYear && academicYear !== 'all') params.append('academic_year', academicYear);
      
      // For faculty, automatically use their own instructor_id
      if (userRole === 'faculty' && user?.id) {
        params.append('instructor_id', user.id.toString());
      } else if (instructorId && instructorId !== 'all') {
        params.append('instructor_id', instructorId);
      }
      
      if (selectedDepartment && selectedDepartment !== 'all') params.append('department', selectedDepartment);
      if (courseId && courseId !== 'all') params.append('course_id', courseId);

      const response = await axiosInstance.get(`/feedback/analytics/?${params.toString()}`);
      console.log('Analytics Response - Semester:', selectedSemester);
      console.log('Text Feedback Count:', response.data.text_feedback?.length);
      console.log('Sample Feedback:', response.data.text_feedback?.slice(0, 2));
      setAnalytics(response.data);
    } catch (error: any) {
      console.error('Error fetching analytics:', error);
      setError(error.response?.data?.error || error.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const fetchEmotionAnalytics = async () => {
    setEmotionLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedSemester && selectedSemester !== 'all') params.append('semester', selectedSemester);
      if (academicYear && academicYear !== 'all') params.append('academic_year', academicYear);
      
      // For faculty, automatically use their own instructor_id
      if (userRole === 'faculty' && user?.id) {
        params.append('instructor_id', user.id.toString());
      } else if (instructorId && instructorId !== 'all') {
        params.append('instructor_id', instructorId);
      }
      
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
      const params = new URLSearchParams();
      if (selectedSemester && selectedSemester !== 'all') params.append('semester', selectedSemester);
      if (academicYear && academicYear !== 'all') params.append('academic_year', academicYear);
      
      // For faculty, automatically use their own instructor_id
      if (userRole === 'faculty' && user?.id) {
        params.append('instructor_id', user.id.toString());
      } else if (instructorId && instructorId !== 'all') {
        params.append('instructor_id', instructorId);
      }
      
      if (selectedDepartment && selectedDepartment !== 'all') params.append('department', selectedDepartment);
      if (courseId && courseId !== 'all') params.append('course_id', courseId);

      const response = await axiosInstance.get(`/topics/?${params.toString()}`);
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
      
      // For faculty, automatically use their own instructor_id
      if (userRole === 'faculty' && user?.id) {
        params.append('instructor_id', user.id.toString());
      } else if (instructorId && instructorId !== 'all') {
        params.append('instructor_id', instructorId);
      }
      
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
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      // Try to read error message from blob if present
      if (error.response?.data instanceof Blob) {
        const text = await error.response.data.text();
        console.error('Error blob content:', text);
        try {
          const errorData = JSON.parse(text);
          alert(`Cannot export report:\n\n${errorData.error || text}`);
        } catch {
          alert(`Cannot export report:\n\n${text}`);
        }
      } else {
        const errorMsg = error.response?.data?.error || error.message || 'Unknown error';
        alert(`Cannot export report:\n\n${errorMsg}`);
      }
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
      <div className="flex flex-col items-center justify-center min-h-screen gap-6 bg-gradient-to-br from-gray-50 via-white to-gray-100">
        <div className="relative">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#8E1B1B] to-rose-600 flex items-center justify-center shadow-lg shadow-red-200/50">
            <Spinner size="lg" className="text-white" />
          </div>
        </div>
        <div className="text-center">
          <p className="text-lg font-semibold text-gray-800">Loading Dashboard</p>
          <p className="text-sm text-gray-500 mt-1">Preparing your analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center p-6">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-2xl shadow-lg border border-red-100 overflow-hidden">
            <div className="h-1.5 bg-gradient-to-r from-red-500 to-rose-500" />
            <div className="p-8 text-center">
              <div className="w-14 h-14 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-4">
                <Frown className="h-7 w-7 text-red-500" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Analytics</h3>
              <p className="text-sm text-gray-500 mb-6">{error}</p>
              <Button
                onClick={fetchAnalytics}
                className="bg-gradient-to-r from-[#8E1B1B] to-rose-600 hover:from-[#7A1717] hover:to-rose-700 text-white rounded-xl px-6 shadow-md shadow-red-200/50"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center p-6">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-2xl shadow-lg border overflow-hidden">
            <div className="h-1.5 bg-gradient-to-r from-blue-500 to-indigo-500" />
            <div className="p-8 text-center">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-7 w-7 text-blue-500" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Feedback Data Yet</h3>
              <p className="text-sm text-gray-500 mb-6">
                Adjust your filters or wait for students to submit feedback.
              </p>
              <Button
                onClick={fetchAnalytics}
                className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white rounded-xl px-6 shadow-md shadow-blue-200/50"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
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

  const learningData = [
    { name: 'Teaching Strategies', value: analytics.independent_learning?.teaching_strategies || 0 },
    { name: 'Student Esteem', value: analytics.independent_learning?.student_esteem || 0 },
    { name: 'Student Autonomy', value: analytics.independent_learning?.student_autonomy || 0 },
    { name: 'Independent Thinking', value: analytics.independent_learning?.independent_thinking || 0 },
    { name: 'Beyond Required', value: analytics.independent_learning?.beyond_required || 0 },
  ];

  const assessmentData = [
    { name: 'Clear Communication', value: analytics.feedback_assessment?.clear_communication || 0 },
    { name: 'Timely Feedback', value: analytics.feedback_assessment?.timely_feedback || 0 },
    { name: 'Improvement Feedback', value: analytics.feedback_assessment?.improvement_feedback || 0 },
  ];

  const experienceData = [
    { name: 'Worthwhile Class', value: analytics.course_info?.worthwhile_class || 0, color: '#22c55e' },
    { name: 'Would Recommend', value: analytics.course_info?.would_recommend || 0, color: '#3b82f6' },
  ];

  const allRatingsData = [
    { subject: 'Commitment', value: (commitmentData.reduce((a, b) => a + b.value, 0) / commitmentData.length) || 0 },
    { subject: 'Knowledge', value: (knowledgeData.reduce((a, b) => a + b.value, 0) / knowledgeData.length) || 0 },
    { subject: 'Learning', value: (learningData.reduce((a, b) => a + b.value, 0) / learningData.length) || 0 },
    { subject: 'Management', value: (managementData.reduce((a, b) => a + b.value, 0) / managementData.length) || 0 },
    { subject: 'Assessment', value: (assessmentData.reduce((a, b) => a + b.value, 0) / assessmentData.length) || 0 },
  ];

  // Calculate sentiment data (no useMemo to avoid dependency loops)
  const getSentimentData = () => {
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
  };

  const sentimentData = getSentimentData();

  const sentimentDistributionData = [
    { name: 'Positive', value: sentimentData.positive, color: '#22c55e' },
    { name: 'Neutral', value: sentimentData.neutral, color: '#eab308' },
    { name: 'Negative', value: sentimentData.negative, color: '#ef4444' },
  ];

  // Tab configuration
  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'emotions', label: 'Emotions', icon: Heart },
    { id: 'topics', label: 'Topics', icon: Layers },
    { id: 'quality', label: 'Quality Review', icon: FileCheck },
  ];

  // Active filter count for badge
  const activeFilterCount = [
    selectedSemester !== 'all',
    academicYear !== 'all',
    selectedDepartment !== 'all',
    instructorId !== 'all',
    courseId !== 'all',
  ].filter(Boolean).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-gray-100/80">
      {/* Smooth loading bar */}
      {isRefreshing && (
        <div className="fixed top-0 left-0 right-0 z-[100] h-1 bg-gray-200/50 overflow-hidden">
          <div className="h-full w-1/3 bg-gradient-to-r from-[#8E1B1B] via-rose-500 to-[#8E1B1B] rounded-full animate-pulse" 
               style={{ animation: 'slideRight 1.5s ease-in-out infinite' }} />
        </div>
      )}

      {/* Hero Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-[#8E1B1B] via-[#A52222] to-[#7A1515]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white/10 via-transparent to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
        
        <div className="relative max-w-[1400px] mx-auto px-4 sm:px-6 py-6 sm:py-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex w-12 h-12 rounded-2xl bg-white/15 backdrop-blur-sm items-center justify-center border border-white/20">
                <GraduationCap className="h-6 w-6 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                    {userRole === 'faculty' ? 'Faculty Dashboard' : 'Admin Dashboard'}
                  </h1>
                  {isRefreshing && (
                    <Badge variant="secondary" className="bg-white/20 text-white border-white/30 text-xs animate-pulse">
                      Updating...
                    </Badge>
                  )}
                </div>
                <p className="text-white/60 text-sm mt-0.5">
                  Sentiment analysis & feedback insights
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <Button 
                size="sm"
                variant="ghost"
                className="text-white/80 hover:text-white hover:bg-white/10 rounded-xl"
                onClick={fetchAnalytics}
                disabled={isRefreshing}
              >
                <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
              </Button>
              <Button 
                size="sm" 
                className="gap-2 bg-white/15 hover:bg-white/25 text-white border border-white/20 backdrop-blur-sm rounded-xl shadow-lg shadow-black/10 transition-all w-full sm:w-auto"
                onClick={handleExportReport}
                disabled={exporting || isRefreshing || !analytics || analytics.total_feedback === 0 || analytics.total_feedback < 10}
                title={analytics && analytics.total_feedback < 10 ? `Need at least 10 feedback entries (currently ${analytics.total_feedback})` : ''}
              >
                <FileDown className="h-4 w-4" />
                {exporting ? 'Exporting...' : 'Export PDF'}
              </Button>
            </div>
          </div>
          {analytics && analytics.total_feedback > 0 && analytics.total_feedback < 10 && (
            <p className="text-amber-200/80 text-xs mt-2 flex items-center gap-1">
              <Sparkles className="h-3 w-3" /> Need 10+ feedback entries to generate reports
            </p>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 -mt-4 relative z-10">
        
        {/* Tab Navigation - Modern pill style */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200/60 p-1.5 inline-flex gap-1 overflow-x-auto w-full sm:w-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 whitespace-nowrap",
                    activeTab === tab.id
                      ? "bg-gradient-to-r from-[#8E1B1B] to-[#A52222] text-white shadow-md shadow-red-900/20"
                      : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                  )}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {activeFilterCount > 0 && (
            <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200 rounded-full">
              <Filter className="h-3 w-3 mr-1" />
              {activeFilterCount} filter{activeFilterCount > 1 ? 's' : ''} active
            </Badge>
          )}
        </div>

        {/* Filters Panel */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 shadow-sm mb-6 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-gray-100">
                <Filter className="h-4 w-4 text-gray-500" />
              </div>
              <span className="text-sm font-semibold text-gray-700">Filters</span>
            </div>
            {activeFilterCount > 0 && (
              <button 
                className="text-xs text-[#8E1B1B] hover:text-[#6B1414] font-medium transition-colors"
                onClick={() => {
                  setSelectedSemester('all');
                  setAcademicYear('all');
                  if (!isCSHead) setSelectedDepartment(isITHead ? 'all' : 'all');
                  setInstructorId('all');
                  setCourseId('all');
                }}
              >
                Reset all
              </button>
            )}
          </div>
          <div className="p-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Semester Filter */}
              <div className="space-y-1.5">
                <Label htmlFor="semester" className="text-xs font-medium text-gray-500 uppercase tracking-wider">Semester</Label>
                <Select value={selectedSemester} onValueChange={setSelectedSemester}>
                  <SelectTrigger id="semester" className="rounded-xl border-gray-200 focus:ring-[#8E1B1B]/20 focus:border-[#8E1B1B]/40 text-sm h-10">
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
              <div className="space-y-1.5">
                <Label htmlFor="academicYear" className="text-xs font-medium text-gray-500 uppercase tracking-wider">Academic Year</Label>
                <Select value={academicYear} onValueChange={setAcademicYear}>
                  <SelectTrigger id="academicYear" className="rounded-xl border-gray-200 focus:ring-[#8E1B1B]/20 focus:border-[#8E1B1B]/40 text-sm h-10">
                    <SelectValue placeholder="All Years" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Years</SelectItem>
                    {availableYears.map((year) => (
                      <SelectItem key={year} value={year}>{year}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Department Filter */}
              {(userRole === 'admin' || isITHead || isCSHead) && (
                <div className="space-y-1.5">
                  <Label htmlFor="department" className="text-xs font-medium text-gray-500 uppercase tracking-wider">Department</Label>
                  <Select value={selectedDepartment} onValueChange={handleDepartmentChange} disabled={isCSHead}>
                    <SelectTrigger id="department" className="rounded-xl border-gray-200 focus:ring-[#8E1B1B]/20 focus:border-[#8E1B1B]/40 text-sm h-10">
                      <SelectValue className="text-sm">
                        {isCSHead ? 'Computer Science' : selectedDepartment === 'all' ? (isITHead ? 'IT & ACT (All)' : 'All Departments') : selectedDepartment === 'CS' ? 'Computer Science' : selectedDepartment === 'IT' ? 'Information Technology' : 'Associate in Computer Technology'}
                      </SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      {isCSHead && <SelectItem value="CS">Computer Science</SelectItem>}
                      {userRole === 'admin' && !isITHead && !isCSHead && <SelectItem value="all">All Departments</SelectItem>}
                      {userRole === 'admin' && !isITHead && !isCSHead && <SelectItem value="CS">Computer Science</SelectItem>}
                      {isITHead && <SelectItem value="all">IT & ACT (All)</SelectItem>}
                      {(userRole === 'admin' || isITHead) && <SelectItem value="IT">Information Technology</SelectItem>}
                      {(userRole === 'admin' || isITHead) && <SelectItem value="ACT">Associate in Computer Technology</SelectItem>}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* Instructor Filter */}
              {(userRole === 'admin' || isITHead || isCSHead) && (
                <>
                  <div className="space-y-1.5">
                    <Label htmlFor="instructor" className="text-xs font-medium text-gray-500 uppercase tracking-wider">{isCSHead ? 'Instructor (CS)' : 'Instructor'}</Label>
                    <Select value={instructorId} onValueChange={handleInstructorChange} disabled={selectedDepartment === 'all'}>
                      <SelectTrigger id="instructor" className="rounded-xl border-gray-200 focus:ring-[#8E1B1B]/20 focus:border-[#8E1B1B]/40 text-sm h-10">
                        <SelectValue placeholder={selectedDepartment === 'all' ? 'Select department first' : 'All Instructors'} />
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
                  
                  <div className="space-y-1.5">
                    <Label htmlFor="course" className="text-xs font-medium text-gray-500 uppercase tracking-wider">{isCSHead ? 'Course (CS)' : 'Course/Subject'}</Label>
                    <Select value={courseId} onValueChange={setCourseId} disabled={instructorId === 'all'}>
                      <SelectTrigger id="course" className="rounded-xl border-gray-200 focus:ring-[#8E1B1B]/20 focus:border-[#8E1B1B]/40 text-sm h-10">
                        <SelectValue placeholder={instructorId === 'all' ? 'Select instructor first' : 'All Courses'} />
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

              {/* Faculty Course Filter */}
              {userRole === 'faculty' && (
                <div className="space-y-1.5">
                  <Label htmlFor="facultyCourse" className="text-xs font-medium text-gray-500 uppercase tracking-wider">Your Courses</Label>
                  <Select value={courseId} onValueChange={setCourseId}>
                    <SelectTrigger id="facultyCourse" className="rounded-xl border-gray-200 focus:ring-[#8E1B1B]/20 focus:border-[#8E1B1B]/40 text-sm h-10">
                      <SelectValue placeholder="All Courses" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Your Courses</SelectItem>
                      {courses.map((course) => (
                        <SelectItem key={course.id} value={course.id.toString()}>
                          {course.code} - {course.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ============ OVERVIEW TAB ============ */}
        {activeTab === 'overview' && (
          <>
            {/* No Data Banner */}
            {analytics.total_feedback === 0 && (
              <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200/60 rounded-2xl p-5 mb-6 flex items-start gap-3">
                <div className="p-2 rounded-xl bg-amber-100 shrink-0">
                  <Sparkles className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <p className="font-semibold text-amber-900 text-sm">No Feedback Data Found</p>
                  <p className="text-xs text-amber-700/70 mt-1">Adjust your filters or wait for students to submit feedback.</p>
                </div>
              </div>
            )}

            {/* Stats Cards - Modern glass design */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {/* Total Feedback */}
              <div className="group relative bg-white rounded-2xl border border-gray-200/60 shadow-sm hover:shadow-lg hover:shadow-gray-200/50 transition-all duration-300 overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#8E1B1B] to-rose-500" />
                <div className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2.5 rounded-xl bg-rose-50 group-hover:bg-rose-100 transition-colors">
                      <Activity className="h-5 w-5 text-[#8E1B1B]" />
                    </div>
                    <ArrowUpRight className="h-4 w-4 text-gray-300 group-hover:text-[#8E1B1B] transition-colors" />
                  </div>
                  <p className="text-sm text-gray-500 font-medium">Total Feedback</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1 tracking-tight">{analytics.total_feedback}</p>
                  <p className="text-xs text-gray-400 mt-2">Responses collected</p>
                </div>
              </div>

              {/* Average Rating */}
              <div className="group relative bg-white rounded-2xl border border-gray-200/60 shadow-sm hover:shadow-lg hover:shadow-gray-200/50 transition-all duration-300 overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-400 to-yellow-500" />
                <div className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2.5 rounded-xl bg-amber-50 group-hover:bg-amber-100 transition-colors">
                      <Star className="h-5 w-5 text-amber-500" />
                    </div>
                    <span className="text-xs font-medium text-gray-400">/ 5.0</span>
                  </div>
                  <p className="text-sm text-gray-500 font-medium">Average Rating</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1 tracking-tight">{analytics.average_rating?.toFixed(2) || 'N/A'}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {[1,2,3,4,5].map(i => (
                      <Star key={i} className={cn("h-3 w-3", i <= Math.round(analytics.average_rating || 0) ? "text-amber-400 fill-amber-400" : "text-gray-200")} />
                    ))}
                  </div>
                </div>
              </div>

              {/* Positive Sentiment */}
              <div className="group relative bg-white rounded-2xl border border-gray-200/60 shadow-sm hover:shadow-lg hover:shadow-gray-200/50 transition-all duration-300 overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-400 to-green-500" />
                <div className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2.5 rounded-xl bg-emerald-50 group-hover:bg-emerald-100 transition-colors">
                      <SmilePlus className="h-5 w-5 text-emerald-600" />
                    </div>
                    {analytics.text_feedback && analytics.text_feedback.length > 0 && (
                      <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 text-xs rounded-full">
                        {((sentimentData.positive / analytics.text_feedback.length) * 100).toFixed(0)}%
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 font-medium">Positive Sentiment</p>
                  <p className="text-3xl font-bold text-emerald-600 mt-1 tracking-tight">+{sentimentData.positive}</p>
                  <p className="text-xs text-gray-400 mt-2">
                    {analytics.text_feedback && analytics.text_feedback.length > 0 
                      ? `of ${analytics.text_feedback.length} responses`
                      : 'No responses yet'}
                  </p>
                </div>
              </div>

              {/* Hours/Week */}
              <div className="group relative bg-white rounded-2xl border border-gray-200/60 shadow-sm hover:shadow-lg hover:shadow-gray-200/50 transition-all duration-300 overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-400 to-indigo-500" />
                <div className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2.5 rounded-xl bg-blue-50 group-hover:bg-blue-100 transition-colors">
                      <Clock className="h-5 w-5 text-blue-600" />
                    </div>
                    <span className="text-xs font-medium text-gray-400">hrs/wk</span>
                  </div>
                  <p className="text-sm text-gray-500 font-medium">Avg Study Hours</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1 tracking-tight">{analytics.overall?.hours_per_week?.toFixed(1) || 'N/A'}</p>
                  <p className="text-xs text-gray-400 mt-2">Outside class time</p>
                </div>
              </div>
            </div>

            {/* Charts - Modern Bento Grid */}
            <div className="grid grid-cols-1 md:grid-cols-6 gap-5 mb-6">
              {/* Commitment - 2 columns */}
              <div className="md:col-span-2 bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-rose-50">
                      <Heart className="h-3.5 w-3.5 text-[#8E1B1B]" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-800">Commitment to Teaching</h3>
                  </div>
                </div>
                <div className="p-4">
                  <ChartContainer config={{ value: { label: "Rating", color: "#8E1B1B" } }} className="h-[250px] w-full">
                    <BarChart data={commitmentData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis type="number" domain={[0, 5]} tick={{ fontSize: 11 }} />
                      <YAxis dataKey="name" type="category" width={90} tick={{ fontSize: 11, fill: '#64748b' }} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="var(--color-value)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ChartContainer>
                </div>
              </div>

              {/* Knowledge - 2 columns */}
              <div className="md:col-span-2 bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-blue-50">
                      <BookOpen className="h-3.5 w-3.5 text-blue-600" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-800">Knowledge of Subject</h3>
                  </div>
                </div>
                <div className="p-4">
                  <ChartContainer config={{ value: { label: "Rating", color: "#3b82f6" } }} className="h-[250px] w-full">
                    <BarChart data={knowledgeData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis type="number" domain={[0, 5]} tick={{ fontSize: 11 }} />
                      <YAxis dataKey="name" type="category" width={90} tick={{ fontSize: 11, fill: '#64748b' }} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="var(--color-value)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ChartContainer>
                </div>
              </div>

              {/* Sentiment Distribution - 2 columns */}
              <div className="md:col-span-2 bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-purple-50">
                      <PieChartIcon className="h-3.5 w-3.5 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-gray-800">Sentiment Distribution</h3>
                      <p className="text-[10px] text-gray-400 mt-0.5">Joy + Satisfaction | Acceptance | Boredom + Disappointment</p>
                    </div>
                  </div>
                </div>
                <div className="p-4">
                  <ChartContainer
                    config={{
                      positive: { label: "Positive", color: "#10b981" },
                      neutral: { label: "Neutral", color: "#f59e0b" },
                      negative: { label: "Negative", color: "#ef4444" },
                    }}
                    className="h-[250px] w-full"
                  >
                    <PieChart>
                      <Pie data={sentimentDistributionData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={4} dataKey="value" strokeWidth={2} stroke="#fff">
                        {sentimentDistributionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <ChartLegend content={<ChartLegendContent />} />
                    </PieChart>
                  </ChartContainer>
                </div>
              </div>
            </div>

            {/* Second Row */}
            <div className="grid grid-cols-1 md:grid-cols-6 gap-5 mb-6">
              {/* Management - 2 columns */}
              <div className="md:col-span-2 bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-amber-50">
                      <Target className="h-3.5 w-3.5 text-amber-600" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-800">Management of Learning</h3>
                  </div>
                </div>
                <div className="p-4">
                  <ChartContainer config={{ value: { label: "Rating", color: "#f59e0b" } }} className="h-[280px] w-full">
                    <BarChart data={managementData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="name" angle={-20} textAnchor="end" height={70} tick={{ fontSize: 11, fill: '#64748b' }} />
                      <YAxis domain={[0, 5]} tick={{ fontSize: 11 }} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="var(--color-value)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ChartContainer>
                </div>
              </div>

              {/* Teaching & Learning - 2 columns */}
              <div className="md:col-span-2 bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-emerald-50">
                      <Sparkles className="h-3.5 w-3.5 text-emerald-600" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-800">Teaching & Learning Strategies</h3>
                  </div>
                </div>
                <div className="p-4">
                  <ChartContainer config={{ value: { label: "Rating", color: "#10b981" } }} className="h-[280px] w-full">
                    <BarChart data={learningData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="name" angle={-20} textAnchor="end" height={70} tick={{ fontSize: 10, fill: '#64748b' }} />
                      <YAxis domain={[0, 5]} tick={{ fontSize: 11 }} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="var(--color-value)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ChartContainer>
                </div>
              </div>

              {/* Feedback & Assessment - 2 columns */}
              <div className="md:col-span-2 bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-violet-50">
                      <MessageSquare className="h-3.5 w-3.5 text-violet-600" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-800">Feedback & Assessment</h3>
                  </div>
                </div>
                <div className="p-4">
                  <ChartContainer config={{ value: { label: "Rating", color: "#8b5cf6" } }} className="h-[280px] w-full">
                    <BarChart data={assessmentData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis type="number" domain={[0, 5]} tick={{ fontSize: 11 }} />
                      <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 10, fill: '#64748b' }} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="var(--color-value)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ChartContainer>
                </div>
              </div>
            </div>

            {/* Third Row - Radar and Experience */}
            <div className="grid grid-cols-1 md:grid-cols-6 gap-5 mb-6">
              {/* Overall Performance Radar - 3 columns */}
              <div className="md:col-span-3 bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-rose-50">
                      <Gauge className="h-3.5 w-3.5 text-[#8E1B1B]" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-800">Overall Performance Radar</h3>
                  </div>
                </div>
                <div className="p-4">
                  <ChartContainer config={{ value: { label: "Rating", color: "#8E1B1B" } }} className="h-[300px] w-full">
                    <RadarChart data={allRatingsData}>
                      <PolarGrid stroke="#e2e8f0" />
                      <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: '#64748b' }} />
                      <PolarRadiusAxis angle={90} domain={[0, 5]} tick={{ fontSize: 10 }} />
                      <Radar name="Rating" dataKey="value" stroke="var(--color-value)" fill="var(--color-value)" fillOpacity={0.25} strokeWidth={2} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                    </RadarChart>
                  </ChartContainer>
                </div>
              </div>

              {/* Overall Experience - 3 columns */}
              <div className="md:col-span-3 bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded-lg bg-emerald-50">
                        <TrendingUp className="h-3.5 w-3.5 text-emerald-600" />
                      </div>
                      <h3 className="text-sm font-semibold text-gray-800">Overall Experience</h3>
                    </div>
                    <span className="text-[10px] text-gray-400">% students agreeing</span>
                  </div>
                </div>
                <div className="p-4">
                  <ChartContainer config={{ value: { label: "Percentage", color: "#10b981" } }} className="h-[300px] w-full">
                    <BarChart data={experienceData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
                      <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11, fill: '#64748b' }} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                        {experienceData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ChartContainer>
                </div>
              </div>
            </div>

            {/* Fourth Row - Course Info */}
            <div className="mb-8">
              <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-indigo-50">
                      <BookOpen className="h-3.5 w-3.5 text-indigo-600" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-800">Course Information Agreement</h3>
                    <span className="text-[10px] text-gray-400 ml-auto">% of students</span>
                  </div>
                </div>
                <div className="p-4">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={courseInfoData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="name" angle={-15} textAnchor="end" height={80} tick={{ fontSize: 11, fill: '#64748b' }} />
                      <YAxis domain={[0, 100]} label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft', style: { fontSize: 11, fill: '#94a3b8' } }} tick={{ fontSize: 11 }} />
                      <Tooltip formatter={(value) => `${Number(value).toFixed(1)}%`} contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)' }} />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {courseInfoData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </>
        )}

        {/* ============ ANALYTICS TAB ============ */}
        {activeTab === 'analytics' && (
          <>
            {analytics.text_feedback && analytics.text_feedback.length > 0 ? (
              <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded-lg bg-indigo-50">
                        <MessageSquare className="h-3.5 w-3.5 text-indigo-600" />
                      </div>
                      <h3 className="text-sm font-semibold text-gray-800">Keyword Analysis</h3>
                    </div>
                    <Badge variant="outline" className="bg-gray-50 text-gray-600 border-gray-200 rounded-full text-xs">
                      {analytics.text_feedback.length} comments
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-400 mt-2 ml-8">
                    Most frequently mentioned words from student feedback, grouped by sentiment
                  </p>
                </div>
                <div className="p-5">
                  <ModernKeywordCloud comments={analytics.text_feedback} />
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
                <div className="p-12 text-center">
                  <div className="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mx-auto mb-4">
                    <MessageSquare className="h-7 w-7 text-gray-300" />
                  </div>
                  <p className="text-gray-500 font-medium">No text feedback available</p>
                  <p className="text-sm text-gray-400 mt-1">Students haven't submitted written feedback yet.</p>
                </div>
              </div>
            )}
          </>
        )}

        {/* ============ EMOTIONS TAB ============ */}
        {activeTab === 'emotions' && (
          <div className="space-y-6">
            {emotionLoading ? (
              <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm p-16">
                <div className="flex flex-col items-center justify-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-pink-50 flex items-center justify-center">
                    <Spinner size="lg" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-gray-700">Loading Emotions</p>
                    <p className="text-xs text-gray-400 mt-1">Analyzing sentiment data...</p>
                  </div>
                </div>
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
              <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
                <div className="p-12 text-center">
                  <div className="w-14 h-14 rounded-2xl bg-pink-50 flex items-center justify-center mx-auto mb-4">
                    <Heart className="h-7 w-7 text-pink-300" />
                  </div>
                  <p className="text-gray-500 font-medium">No Emotion Data Available</p>
                  <p className="text-sm text-gray-400 mt-1">Students need to submit feedback first.</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ============ TOPICS TAB ============ */}
        {activeTab === 'topics' && (
          <div>
            {topicLoading ? (
              <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm p-16">
                <div className="flex flex-col items-center justify-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center">
                    <Spinner size="lg" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-gray-700">Loading Topics</p>
                    <p className="text-xs text-gray-400 mt-1">Running topic modeling analysis...</p>
                  </div>
                </div>
              </div>
            ) : topicData ? (
              <TopicModelingDashboard
                topics={topicData.topics}
                topicDistribution={topicData.topic_distribution}
                totalTopics={topicData.total_topics}
                topicInsights={topicData.topic_insights}
              />
            ) : (
              <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
                <div className="p-12 text-center">
                  <div className="w-14 h-14 rounded-2xl bg-indigo-50 flex items-center justify-center mx-auto mb-4">
                    <Layers className="h-7 w-7 text-indigo-300" />
                  </div>
                  <p className="text-gray-500 font-medium">No Topic Data Available</p>
                  <p className="text-sm text-gray-400 mt-1">Run topic modeling analysis to see results here.</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ============ QUALITY REVIEW TAB ============ */}
        {activeTab === 'quality' && (
          <RevisionAnalysis
            filters={{
              semester: selectedSemester,
              academic_year: academicYear,
              instructor_id: instructorId,
              course_id: courseId,
              department: selectedDepartment,
            }}
          />
        )}

        {/* Bottom spacing */}
        <div className="h-8" />
      </div>
    </div>
  );
}
