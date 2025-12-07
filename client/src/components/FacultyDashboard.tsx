'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import axiosInstance from '@/lib/axios';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar,
} from 'recharts';

interface FeedbackAnalytics {
  total_feedback: number;
  average_rating: number;
  commitment: {
    sensitivity: number;
    integration: number;
    availability: number;
    punctuality: number;
    record_keeping: number;
  };
  knowledge: {
    mastery: number;
    state_of_art: number;
    practical_integration: number;
    relevance: number;
    current_trends: number;
  };
  independent_learning: {
    teaching_strategies: number;
    student_esteem: number;
    student_autonomy: number;
    independent_thinking: number;
    beyond_required: number;
  };
  management: {
    student_contribution: number;
    facilitator_role: number;
    discussion_encouragement: number;
    instructional_methods: number;
    instructional_materials: number;
  };
  feedback_assessment: {
    clear_communication: number;
    timely_feedback: number;
    improvement_feedback: number;
  };
  overall: {
    overall_rating: number;
    hours_per_week: number;
  };
  student_evaluation: {
    constructive_contribution: number;
    achieving_outcomes: number;
  };
  course_info: {
    syllabus_explained: number;
    delivered_as_outlined: number;
    grading_criteria_explained: number;
    exams_related: number;
    assignments_related: number;
    lms_resources_useful: number;
    worthwhile_class: number;
    would_recommend: number;
  };
  text_feedback: Array<{
    id: number;
    student_name: string;
    course_name: string;
    suggested_changes: string;
    best_teaching_aspect: string;
    least_teaching_aspect: string;
    further_comments: string;
    sentiment_score: number;
  }>;
}

interface Instructor {
  id: number;
  first_name: string;
  last_name: string;
}

interface Course {
  id: number;
  code: string;
  name: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function FacultyDashboard({ userRole }: { userRole: string }) {
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [semester, setSemester] = useState<string>('');
  const [academicYear, setAcademicYear] = useState<string>('');
  const [instructorId, setInstructorId] = useState<string>('');
  const [courseId, setCourseId] = useState<string>('');
  const [instructors, setInstructors] = useState<Instructor[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);

  // Fetch instructors if admin and courses
  useEffect(() => {
    if (userRole === 'admin') {
      fetchInstructors();
    }
    fetchCourses();
  }, [userRole, instructorId]);

  const fetchInstructors = async () => {
    try {
      const response = await axiosInstance.get('/auth/users/?role=faculty');
      setInstructors(response.data.data || response.data);
    } catch (error) {
      console.error('Error fetching instructors:', error);
    }
  };

  const fetchCourses = async () => {
    try {
      const params = new URLSearchParams();
      if (instructorId && instructorId !== 'all') params.append('instructor_id', instructorId);
      
      const response = await axiosInstance.get(`/feedback/courses/?${params.toString()}`);
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
      setCourses([]);
    }
  };

  // Fetch analytics data
  useEffect(() => {
    fetchAnalytics();
  }, [semester, academicYear, instructorId, courseId]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (semester && semester !== 'all') params.append('semester', semester);
      if (academicYear && academicYear !== 'all') params.append('academic_year', academicYear);
      if (instructorId && instructorId !== 'all') params.append('instructor_id', instructorId);
      if (courseId && courseId !== 'all') params.append('course_id', courseId);

      console.log('Fetching analytics with URL:', `/feedback/analytics/?${params.toString()}`);
      const response = await axiosInstance.get(`/feedback/analytics/?${params.toString()}`);
      console.log('Analytics response:', response.data);
      setAnalytics(response.data);
    } catch (error: any) {
      console.error('Error fetching analytics:', error);
      console.error('Error response:', error.response);
      console.error('Error message:', error.message);
      setError(error.response?.data?.error || error.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
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
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
          <p className="font-semibold">Error loading analytics</p>
          <p className="text-sm">{error}</p>
          <button
            onClick={fetchAnalytics}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">No feedback data available</div>
      </div>
    );
  }

  // Prepare data for charts
  const commitmentData = [
    { name: 'Sensitivity to Concerns', value: analytics.commitment.sensitivity || 0 },
    { name: 'Course Integration', value: analytics.commitment.integration || 0 },
    { name: 'Availability', value: analytics.commitment.availability || 0 },
    { name: 'Punctuality', value: analytics.commitment.punctuality || 0 },
    { name: 'Record Keeping', value: analytics.commitment.record_keeping || 0 },
  ];

  const knowledgeData = [
    { name: 'Subject Mastery', value: analytics.knowledge.mastery || 0 },
    { name: 'State-of-the-Art', value: analytics.knowledge.state_of_art || 0 },
    { name: 'Practical Integration', value: analytics.knowledge.practical_integration || 0 },
    { name: 'Relevance', value: analytics.knowledge.relevance || 0 },
    { name: 'Current Trends', value: analytics.knowledge.current_trends || 0 },
  ];

  const independentLearningData = [
    { name: 'Teaching Strategies', value: analytics.independent_learning.teaching_strategies || 0 },
    { name: 'Student Esteem', value: analytics.independent_learning.student_esteem || 0 },
    { name: 'Student Autonomy', value: analytics.independent_learning.student_autonomy || 0 },
    { name: 'Independent Thinking', value: analytics.independent_learning.independent_thinking || 0 },
    { name: 'Beyond Required', value: analytics.independent_learning.beyond_required || 0 },
  ];

  const managementData = [
    { name: 'Student Contribution', value: analytics.management.student_contribution || 0 },
    { name: 'Facilitator Role', value: analytics.management.facilitator_role || 0 },
    { name: 'Discussion Encouragement', value: analytics.management.discussion_encouragement || 0 },
    { name: 'Instructional Methods', value: analytics.management.instructional_methods || 0 },
    { name: 'Instructional Materials', value: analytics.management.instructional_materials || 0 },
  ];

  const feedbackAssessmentData = [
    { name: 'Clear Communication', value: analytics.feedback_assessment.clear_communication || 0 },
    { name: 'Timely Feedback', value: analytics.feedback_assessment.timely_feedback || 0 },
    { name: 'Improvement Feedback', value: analytics.feedback_assessment.improvement_feedback || 0 },
  ];

  const studentEvaluationData = [
    { name: 'Constructive Contribution', value: analytics.student_evaluation.constructive_contribution || 0 },
    { name: 'Achieving Outcomes', value: analytics.student_evaluation.achieving_outcomes || 0 },
  ];

  const courseInfoData = [
    { name: 'Syllabus Explained', value: analytics.course_info.syllabus_explained || 0, color: '#0088FE' },
    { name: 'Delivered as Outlined', value: analytics.course_info.delivered_as_outlined || 0, color: '#00C49F' },
    { name: 'Grading Criteria Explained', value: analytics.course_info.grading_criteria_explained || 0, color: '#FFBB28' },
    { name: 'Exams Related', value: analytics.course_info.exams_related || 0, color: '#FF8042' },
    { name: 'Assignments Related', value: analytics.course_info.assignments_related || 0, color: '#8884D8' },
    { name: 'LMS Resources Useful', value: analytics.course_info.lms_resources_useful || 0, color: '#82ca9d' },
    { name: 'Worthwhile Class', value: analytics.course_info.worthwhile_class || 0, color: '#ffc658' },
    { name: 'Would Recommend', value: analytics.course_info.would_recommend || 0, color: '#ff7c7c' },
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Feedback Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            {analytics.total_feedback} total feedback responses
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Filter feedback data by semester, academic year, and instructor</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Semester Filter */}
            <div className="space-y-2">
              <Label htmlFor="semester">Semester</Label>
              <Select value={semester} onValueChange={setSemester}>
                <SelectTrigger id="semester">
                  <SelectValue placeholder="All Semesters" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Semesters</SelectItem>
                  <SelectItem value="1st">1st Semester</SelectItem>
                  <SelectItem value="2nd">2nd Semester</SelectItem>
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
                  <SelectItem value="2024-2025">2024-2025</SelectItem>
                  <SelectItem value="2023-2024">2023-2024</SelectItem>
                  <SelectItem value="2022-2023">2022-2023</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Instructor Filter (Admin only) */}
            {userRole === 'admin' && (
              <div className="space-y-2">
                <Label htmlFor="instructor">Instructor</Label>
                <Select value={instructorId} onValueChange={setInstructorId}>
                  <SelectTrigger id="instructor">
                    <SelectValue placeholder="All Instructors" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Instructors</SelectItem>
                    {instructors.map((instructor) => (
                      <SelectItem key={instructor.id} value={instructor.id.toString()}>
                        {instructor.first_name} {instructor.last_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Course Filter */}
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
          </div>
        </CardContent>
      </Card>

      {/* Overall Rating */}
      <Card>
        <CardHeader>
          <CardTitle>Overall Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-5xl font-bold text-primary">
                {analytics.average_rating?.toFixed(2) || 'N/A'}
              </div>
              <div className="text-sm text-muted-foreground mt-2">Average Rating (out of 5)</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-bold text-primary">
                {analytics.overall.overall_rating?.toFixed(2) || 'N/A'}
              </div>
              <div className="text-sm text-muted-foreground mt-2">Overall Course Rating</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-bold text-primary">
                {analytics.overall.hours_per_week?.toFixed(1) || 'N/A'}
              </div>
              <div className="text-sm text-muted-foreground mt-2">Avg Hours per Week</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Part 1: Commitment */}
      <Card>
        <CardHeader>
          <CardTitle>Part 1: Commitment to Teaching and Learning</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={commitmentData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 5]} />
              <YAxis dataKey="name" type="category" width={180} />
              <Tooltip />
              <Bar dataKey="value" fill="#0088FE" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Part 2: Knowledge of the Subject */}
      <Card>
        <CardHeader>
          <CardTitle>Part 2: Knowledge of the Subject</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={knowledgeData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 5]} />
              <YAxis dataKey="name" type="category" width={180} />
              <Tooltip />
              <Bar dataKey="value" fill="#00C49F" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Part 3: Independent Learning */}
      <Card>
        <CardHeader>
          <CardTitle>Part 3: Promoting Independent Learning</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={independentLearningData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 5]} />
              <YAxis dataKey="name" type="category" width={180} />
              <Tooltip />
              <Bar dataKey="value" fill="#FFBB28" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Part 4: Management of Learning */}
      <Card>
        <CardHeader>
          <CardTitle>Part 4: Management of Learning</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={managementData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 5]} />
              <YAxis dataKey="name" type="category" width={180} />
              <Tooltip />
              <Bar dataKey="value" fill="#FF8042" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Part 5: Feedback and Assessment */}
      <Card>
        <CardHeader>
          <CardTitle>Part 5: Feedback and Assessment</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={feedbackAssessmentData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 5]} />
              <YAxis dataKey="name" type="category" width={180} />
              <Tooltip />
              <Bar dataKey="value" fill="#8884D8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Part 8: Student Self-Evaluation */}
      <Card>
        <CardHeader>
          <CardTitle>Part 8: Student Self-Evaluation</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={studentEvaluationData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 5]} />
              <YAxis dataKey="name" type="category" width={200} />
              <Tooltip />
              <Bar dataKey="value" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Part 6: Course Information (Yes/No Questions) */}
      <Card>
        <CardHeader>
          <CardTitle>Part 6 & 7: Course Information (% of Students Who Agreed)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={courseInfoData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={120} />
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

      {/* Text Feedback */}
      <Card>
        <CardHeader>
          <CardTitle>Part 9: Student Comments (Recent Feedback)</CardTitle>
          <CardDescription>Showing up to 50 most recent comments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analytics.text_feedback.length === 0 ? (
              <p className="text-muted-foreground">No text feedback available</p>
            ) : (
              analytics.text_feedback.map((feedback) => (
                <div key={feedback.id} className="border rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="font-semibold">{feedback.student_name}</div>
                    <div className="text-sm text-muted-foreground">{feedback.course_name}</div>
                  </div>
                  
                  {feedback.suggested_changes && (
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Suggested Changes:</div>
                      <div className="text-sm">{feedback.suggested_changes}</div>
                    </div>
                  )}
                  
                  {feedback.best_teaching_aspect && (
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Best Teaching Aspect:</div>
                      <div className="text-sm">{feedback.best_teaching_aspect}</div>
                    </div>
                  )}
                  
                  {feedback.least_teaching_aspect && (
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Least Teaching Aspect:</div>
                      <div className="text-sm">{feedback.least_teaching_aspect}</div>
                    </div>
                  )}
                  
                  {feedback.further_comments && (
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Further Comments:</div>
                      <div className="text-sm">{feedback.further_comments}</div>
                    </div>
                  )}
                  
                  {feedback.sentiment_score !== null && (
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-muted-foreground">Sentiment:</span>
                      <span
                        className={`font-medium ${
                          feedback.sentiment_score > 0
                            ? 'text-green-600'
                            : feedback.sentiment_score < 0
                            ? 'text-red-600'
                            : 'text-gray-600'
                        }`}
                      >
                        {feedback.sentiment_score > 0
                          ? 'Positive'
                          : feedback.sentiment_score < 0
                          ? 'Negative'
                          : 'Neutral'}{' '}
                        ({feedback.sentiment_score.toFixed(2)})
                      </span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
