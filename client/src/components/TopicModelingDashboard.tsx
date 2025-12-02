'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { BookOpen, Hash, TrendingUp, Lightbulb, AlertCircle, CheckCircle, Clock, Users, MessageSquare, Presentation, Book, Clipboard, Folder, Info } from 'lucide-react';

interface Topic {
  topic: string;
  keywords: string[];
}

interface Insight {
  category: string;
  priority: 'high' | 'medium' | 'low';
  suggestion: string;
  icon: string;
}

interface TopicInsight {
  topic: string;
  insights: Insight[];
}

interface TopicModelingProps {
  topics: Topic[];
  topicDistribution: { [key: string]: number };
  totalTopics: number;
  topicInsights?: TopicInsight[];
}

const COLORS = [
  '#8E1B1B', // Maroon
  '#3b82f6', // Blue
  '#10b981', // Green
  '#f59e0b', // Orange
  '#8b5cf6', // Purple
  '#ef4444', // Red
  '#06b6d4', // Cyan
  '#ec4899', // Pink
];

export default function TopicModelingDashboard({ topics, topicDistribution, totalTopics, topicInsights }: TopicModelingProps) {
  // Icon mapping
  const iconMap: { [key: string]: any } = {
    presentation: Presentation,
    book: Book,
    clipboard: Clipboard,
    clock: Clock,
    users: Users,
    message: MessageSquare,
    folder: Folder,
    info: Info,
  };

  // Priority styling
  const priorityStyles = {
    high: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: 'text-red-500' },
    medium: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700', icon: 'text-yellow-500' },
    low: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', icon: 'text-green-500' },
  };

  // Prepare data for bar chart
  const distributionData = Object.entries(topicDistribution).map(([topic, count]) => ({
    topic: topic.replace('Topic ', 'T'),
    count,
    fullName: topic,
  }));

  // Prepare data for pie chart
  const pieData = Object.entries(topicDistribution).map(([topic, count]) => ({
    name: topic,
    value: count,
  }));

  const totalFeedback = Object.values(topicDistribution).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">Total Topics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <p className="text-3xl font-bold text-[#8E1B1B]">{totalTopics}</p>
              <Hash className="h-8 w-8 text-[#8E1B1B] opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">Feedback Analyzed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <p className="text-3xl font-bold text-blue-600">{totalFeedback}</p>
              <BookOpen className="h-8 w-8 text-blue-600 opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">Avg. per Topic</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <p className="text-3xl font-bold text-green-600">
                {totalTopics > 0 ? Math.round(totalFeedback / totalTopics) : 0}
              </p>
              <TrendingUp className="h-8 w-8 text-green-600 opacity-50" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Topic Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Topic Distribution</CardTitle>
            <CardDescription className="text-xs">Number of feedback items per topic</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distributionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="topic"
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                  />
                  <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} />
                  <Tooltip
                    content={({ payload }) => {
                      if (payload && payload.length > 0) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white p-3 rounded-lg shadow-lg border">
                            <p className="font-semibold text-sm">{data.fullName}</p>
                            <p className="text-sm text-gray-600">{data.count} feedback items</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="count" fill="#8E1B1B" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Topic Proportions</CardTitle>
            <CardDescription className="text-xs">Percentage distribution of topics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name.replace('Topic ', 'T')}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ payload }) => {
                      if (payload && payload.length > 0) {
                        const data = payload[0];
                        const percentage = ((data.value as number) / totalFeedback * 100).toFixed(1);
                        return (
                          <div className="bg-white p-3 rounded-lg shadow-lg border">
                            <p className="font-semibold text-sm">{data.name}</p>
                            <p className="text-sm text-gray-600">
                              {data.value} items ({percentage}%)
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Topic Keywords Grid */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Topic Keywords</CardTitle>
          <CardDescription className="text-xs">
            Key terms identified for each topic theme
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {topics.map((topic, index) => {
              const count = topicDistribution[topic.topic] || 0;
              const percentage = totalFeedback > 0 ? ((count / totalFeedback) * 100).toFixed(1) : '0';
              
              return (
                <div
                  key={topic.topic}
                  className="p-4 border rounded-lg hover:shadow-md transition-shadow"
                  style={{ borderLeft: `4px solid ${COLORS[index % COLORS.length]}` }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-sm" style={{ color: COLORS[index % COLORS.length] }}>
                      {topic.topic}
                    </h3>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">{count} items</p>
                      <p className="text-xs font-semibold text-gray-700">{percentage}%</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {topic.keywords.slice(0, 8).map((keyword, kidx) => (
                      <Badge
                        key={kidx}
                        variant="secondary"
                        className="text-xs"
                        style={{
                          backgroundColor: `${COLORS[index % COLORS.length]}15`,
                          color: COLORS[index % COLORS.length],
                        }}
                      >
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Course Improvement Insights */}
      {topicInsights && topicInsights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-[#8E1B1B]" />
              Course Improvement Insights
            </CardTitle>
            <CardDescription>
              AI-generated recommendations based on topic analysis and student emotions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {topicInsights.map((topicInsight, tidx) => {
                const topicColor = COLORS[tidx % COLORS.length];
                const hasInsights = topicInsight.insights && topicInsight.insights.length > 0;
                
                if (!hasInsights) return null;

                return (
                  <div key={topicInsight.topic} className="space-y-3">
                    <h3 
                      className="font-semibold text-sm pb-2 border-b"
                      style={{ color: topicColor, borderColor: `${topicColor}30` }}
                    >
                      {topicInsight.topic}
                    </h3>
                    <div className="grid grid-cols-1 gap-3">
                      {topicInsight.insights.map((insight, iidx) => {
                        const Icon = iconMap[insight.icon] || Info;
                        const style = priorityStyles[insight.priority];
                        const PriorityIcon = insight.priority === 'high' ? AlertCircle : insight.priority === 'medium' ? Clock : CheckCircle;

                        return (
                          <div 
                            key={iidx}
                            className={`p-4 rounded-lg border-l-4 ${style.bg} ${style.border}`}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`p-2 rounded-lg bg-white`}>
                                <Icon className={`h-5 w-5 ${style.icon}`} />
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <h4 className={`font-semibold text-sm ${style.text}`}>
                                    {insight.category}
                                  </h4>
                                  <div className="flex items-center gap-1">
                                    <PriorityIcon className={`h-3 w-3 ${style.icon}`} />
                                    <span className={`text-xs font-medium uppercase ${style.text}`}>
                                      {insight.priority}
                                    </span>
                                  </div>
                                </div>
                                <p className="text-sm text-gray-700">
                                  {insight.suggestion}
                                </p>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
