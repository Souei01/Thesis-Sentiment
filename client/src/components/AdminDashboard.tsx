'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  Upload,
  Filter,
  SmilePlus,
  Frown,
  Meh,
} from 'lucide-react';

// Sample data based on the image
const emotionFrequencyData = [
  { name: 'SATISFACTION', value: 2200 },
  { name: 'JOY', value: 2800 },
  { name: 'DISAPPOINTMENT', value: 800 },
  { name: 'BOREDOM', value: 1800 },
  { name: 'ACCEPTANCE', value: 3400 },
  { name: 'INDIFFERENCE', value: 1000 },
];

const courseEmotionData = [
  { course: 'CC 101', joy: 0.8, gratitude: 0.6, disappointment: 0.3, boredom: 0.2 },
  { course: 'CC 103', joy: 0.7, gratitude: 0.5, disappointment: 0.4, boredom: 0.3 },
  { course: 'CS 101', joy: 0.6, gratitude: 0.7, disappointment: 0.6, boredom: 0.5 },
  { course: 'CS 102', joy: 0.9, gratitude: 0.8, disappointment: 0.5, boredom: 0.6 },
];

const sentimentTrendData = [
  { month: 'Jan', value: 26.5 },
  { month: 'Feb', value: 27.2 },
  { month: 'Mar', value: 26.8 },
  { month: 'Apr', value: 27.0 },
  { month: 'May', value: 27.5 },
  { month: 'Jun', value: 27.0 },
];

const sentimentDistributionData = [
  { name: 'Positive', value: 1038, color: '#22c55e' },
  { name: 'Neutral', value: 150, color: '#eab308' },
  { name: 'Negative', value: 173, color: '#ef4444' },
];

const heatMapData = [
  { emotion: 'Satisfaction', intensity: 0.7, color: '#93c5fd' },
  { emotion: 'Joy', intensity: 0.5, color: '#fbbf24' },
  { emotion: 'Disappointment', intensity: 0.8, color: '#f87171' },
  { emotion: 'Boredom', intensity: 0.4, color: '#93c5fd' },
  { emotion: 'Acceptance', intensity: 0.6, color: '#fbbf24' },
];

const COLORS = ['#8b5cf6', '#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#6366f1'];

export default function AdminDashboard() {
  const [selectedSemester, setSelectedSemester] = useState('1st Semester');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-[1400px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm" className="gap-2">
                <Filter className="h-4 w-4" />
                Filter By: {selectedSemester}
              </Button>
              <Button size="sm" className="gap-2 bg-[#8E1B1B] hover:bg-[#6B1414]">
                <Upload className="h-4 w-4" />
                Upload CSV
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1400px] mx-auto px-6 py-6">
        {/* Overview Tabs */}
        <div className="flex gap-4 mb-6">
          <Button variant="default" className="bg-white text-gray-900 hover:bg-gray-100 border-b-2 border-[#8E1B1B]">
            Overview
          </Button>
          <Button variant="ghost" className="text-gray-500">Analytics</Button>
          <Button variant="ghost" className="text-gray-500">Reports</Button>
          <Button variant="ghost" className="text-gray-500">Notifications</Button>
        </div>

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
              <div className="text-3xl font-bold">2356</div>
              <p className="text-xs text-green-600 flex items-center gap-1 mt-1">
                <TrendingUp className="h-3 w-3" />
                +23% from last month semester
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Positive
              </CardTitle>
              <SmilePlus className="h-4 w-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">+1850</div>
              <p className="text-xs text-green-600 flex items-center gap-1 mt-1">
                <TrendingUp className="h-3 w-3" />
                +863% from last semester
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Neutral
              </CardTitle>
              <Meh className="h-4 w-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">+150</div>
              <p className="text-xs text-gray-600 flex items-center gap-1 mt-1">
                <Activity className="h-3 w-3" />
                +19% from last semester
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Negative
              </CardTitle>
              <Frown className="h-4 w-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">-173</div>
              <p className="text-xs text-red-600 flex items-center gap-1 mt-1">
                <TrendingDown className="h-3 w-3" />
                -2% from last semester
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Emotion Frequency */}
          <Card>
            <CardHeader>
              <CardTitle>Emotion Frequency</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={emotionFrequencyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8E1B1B" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Emotion Frequency by Course */}
          <Card>
            <CardHeader>
              <CardTitle>Emotion Frequency: Frequency of Emotions across Courses</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={courseEmotionData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 1]} />
                  <YAxis dataKey="course" type="category" />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="joy" fill="#fbbf24" stackId="a" />
                  <Bar dataKey="gratitude" fill="#fb923c" stackId="a" />
                  <Bar dataKey="disappointment" fill="#f87171" stackId="a" />
                  <Bar dataKey="boredom" fill="#dc2626" stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sentiment Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Sentiment Trend Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={sentimentTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis domain={[25, 29]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#8E1B1B" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Sentiment Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Sentiment Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={sentimentDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
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

          {/* Heat Map */}
          <Card>
            <CardHeader>
              <CardTitle>Heat Map</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {heatMapData.map((item, index) => (
                  <div key={index} className="relative">
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium">{item.emotion}</span>
                      <span className="text-sm text-gray-500">{Math.round(item.intensity * 100)}%</span>
                    </div>
                    <div className="w-full h-8 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${item.intensity * 100}%`,
                          backgroundColor: item.color,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
