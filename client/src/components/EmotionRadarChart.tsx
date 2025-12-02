'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { Smile, Frown, Meh, Clock, TrendingDown } from 'lucide-react';

interface EmotionData {
  emotion: string;
  count: number;
  percentage: number;
  fullMark: number;
}

interface EmotionRadarChartProps {
  emotionDistribution: {
    joy: number;
    satisfaction: number;
    acceptance: number;
    boredom: number;
    disappointment: number;
  };
  totalEmotions: number;
  emotionByField?: {
    [fieldName: string]: {
      joy: number;
      satisfaction: number;
      acceptance: number;
      boredom: number;
      disappointment: number;
    };
  };
}

const emotionIcons: { [key: string]: any } = {
  joy: Smile,
  satisfaction: Smile,
  acceptance: Meh,
  boredom: Clock,
  disappointment: Frown,
};

const emotionColors: { [key: string]: string } = {
  joy: '#10b981',
  satisfaction: '#3b82f6',
  acceptance: '#8b5cf6',
  boredom: '#f59e0b',
  disappointment: '#ef4444',
};

export default function EmotionRadarChart({ emotionDistribution, totalEmotions, emotionByField }: EmotionRadarChartProps) {
  // Prepare data for radar chart
  const radarData: EmotionData[] = Object.entries(emotionDistribution).map(([emotion, count]) => ({
    emotion: emotion.charAt(0).toUpperCase() + emotion.slice(1),
    count,
    percentage: totalEmotions > 0 ? (count / totalEmotions) * 100 : 0,
    fullMark: 100,
  }));

  // Prepare data for emotion cards
  const sortedEmotions = Object.entries(emotionDistribution)
    .sort(([, a], [, b]) => b - a)
    .map(([emotion, count]) => ({
      emotion,
      count,
      percentage: totalEmotions > 0 ? ((count / totalEmotions) * 100).toFixed(1) : '0',
    }));

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Smile className="h-5 w-5 text-[#8E1B1B]" />
            Emotion Distribution
          </CardTitle>
          <CardDescription>
            Analysis of {totalEmotions} emotional responses from feedback
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Radar Chart */}
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis
                    dataKey="emotion"
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 100]}
                    tick={{ fill: '#9ca3af', fontSize: 10 }}
                  />
                  <Radar
                    name="Percentage"
                    dataKey="percentage"
                    stroke="#8E1B1B"
                    fill="#8E1B1B"
                    fillOpacity={0.6}
                  />
                  <Tooltip
                    content={({ payload }) => {
                      if (payload && payload.length > 0) {
                        const data = payload[0].payload as EmotionData;
                        return (
                          <div className="bg-white p-3 rounded-lg shadow-lg border">
                            <p className="font-semibold text-sm">{data.emotion}</p>
                            <p className="text-sm text-gray-600">
                              {data.count} responses ({data.percentage.toFixed(1)}%)
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Emotion Breakdown */}
            <div className="space-y-3">
              <h3 className="font-semibold text-sm text-gray-700 mb-4">Emotion Breakdown</h3>
              {sortedEmotions.map(({ emotion, count, percentage }) => {
                const Icon = emotionIcons[emotion];
                const color = emotionColors[emotion];
                return (
                  <div key={emotion} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div
                        className="p-2 rounded-full"
                        style={{ backgroundColor: `${color}20` }}
                      >
                        <Icon className="h-5 w-5" style={{ color }} />
                      </div>
                      <div>
                        <p className="font-medium text-sm capitalize">{emotion}</p>
                        <p className="text-xs text-gray-500">{count} responses</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg" style={{ color }}>
                        {percentage}%
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Emotion by Field */}
      {emotionByField && (
        <Card>
          <CardHeader>
            <CardTitle>Emotion Distribution by Feedback Field</CardTitle>
            <CardDescription>
              See which emotions appear in different feedback sections
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {Object.entries(emotionByField).map(([fieldName, emotions]) => {
                const totalFieldEmotions = Object.values(emotions).reduce((sum, count) => sum + count, 0);
                return (
                  <div key={fieldName} className="border rounded-lg p-4">
                    <h4 className="font-semibold text-sm mb-3 text-gray-700">{fieldName}</h4>
                    <div className="space-y-2">
                      {Object.entries(emotions)
                        .sort(([, a], [, b]) => b - a)
                        .filter(([, count]) => count > 0)
                        .map(([emotion, count]) => {
                          const Icon = emotionIcons[emotion];
                          const color = emotionColors[emotion];
                          const percentage = totalFieldEmotions > 0 ? ((count / totalFieldEmotions) * 100).toFixed(1) : '0';
                          return (
                            <div key={emotion} className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Icon className="h-4 w-4" style={{ color }} />
                                <span className="text-sm capitalize text-gray-600">{emotion}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <div className="w-32 bg-gray-200 rounded-full h-2">
                                  <div
                                    className="h-2 rounded-full"
                                    style={{ 
                                      backgroundColor: color, 
                                      width: `${percentage}%` 
                                    }}
                                  />
                                </div>
                                <span className="text-sm font-semibold w-12 text-right" style={{ color }}>
                                  {count} ({percentage}%)
                                </span>
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

      {/* Legacy emotion cards section - only show if emotionByField not provided */}
      {!emotionByField && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Emotion Distribution by Feedback Field</CardTitle>
            <CardDescription className="text-xs">
              See which emotions appear in different feedback sections
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(emotionDistribution).map(([emotion, count]) => {
                const Icon = emotionIcons[emotion];
                const color = emotionColors[emotion];
                return (
                  <div key={emotion} className="text-center p-4 border rounded-lg">
                    <div className="flex justify-center mb-2">
                      <div
                        className="p-3 rounded-full"
                        style={{ backgroundColor: `${color}20` }}
                      >
                        <Icon className="h-6 w-6" style={{ color }} />
                      </div>
                    </div>
                    <p className="font-semibold text-sm capitalize">{emotion}</p>
                    <p className="text-2xl font-bold mt-1" style={{ color }}>
                      {count}
                    </p>
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
