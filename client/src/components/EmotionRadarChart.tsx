'use client';

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { Smile, Frown, Meh, Clock, TrendingDown, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

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

const emotionMeta: { [key: string]: { color: string; bg: string; label: string } } = {
  joy: { color: '#10b981', bg: 'bg-emerald-50', label: 'Joy' },
  satisfaction: { color: '#3b82f6', bg: 'bg-blue-50', label: 'Satisfaction' },
  acceptance: { color: '#8b5cf6', bg: 'bg-violet-50', label: 'Acceptance' },
  boredom: { color: '#f59e0b', bg: 'bg-amber-50', label: 'Boredom' },
  disappointment: { color: '#ef4444', bg: 'bg-red-50', label: 'Disappointment' },
};

export default function EmotionRadarChart({ emotionDistribution, totalEmotions, emotionByField }: EmotionRadarChartProps) {
  const radarData: EmotionData[] = Object.entries(emotionDistribution).map(([emotion, count]) => ({
    emotion: emotion.charAt(0).toUpperCase() + emotion.slice(1),
    count,
    percentage: totalEmotions > 0 ? (count / totalEmotions) * 100 : 0,
    fullMark: 100,
  }));

  const sortedEmotions = Object.entries(emotionDistribution)
    .sort(([, a], [, b]) => b - a)
    .map(([emotion, count]) => ({
      emotion,
      count,
      percentage: totalEmotions > 0 ? ((count / totalEmotions) * 100) : 0,
    }));

  const dominantEmotion = sortedEmotions[0];

  return (
    <div className="space-y-6">
      {/* Main Radar + Breakdown */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-gradient-to-br from-pink-50 to-rose-100">
                <Sparkles className="h-5 w-5 text-[#8E1B1B]" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-gray-900">Emotion Distribution</h3>
                <p className="text-xs text-gray-400 mt-0.5">
                  Analysis of {totalEmotions.toLocaleString()} emotional responses
                </p>
              </div>
            </div>
            {dominantEmotion && (
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-50 border border-gray-200/60">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: emotionMeta[dominantEmotion.emotion]?.color }} />
                <span className="text-xs font-medium text-gray-600">
                  Dominant: <span className="capitalize" style={{ color: emotionMeta[dominantEmotion.emotion]?.color }}>{dominantEmotion.emotion}</span>
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Radar Chart */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-gray-50/50 to-transparent rounded-2xl" />
              <div className="relative h-[380px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData} cx="50%" cy="50%">
                    <PolarGrid stroke="#e2e8f0" strokeWidth={0.5} />
                    <PolarAngleAxis
                      dataKey="emotion"
                      tick={{ fill: '#64748b', fontSize: 12, fontWeight: 500 }}
                    />
                    <PolarRadiusAxis
                      angle={90}
                      domain={[0, 100]}
                      tick={{ fill: '#94a3b8', fontSize: 9 }}
                      tickCount={5}
                    />
                    <defs>
                      <linearGradient id="radarGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#8E1B1B" stopOpacity={0.4} />
                        <stop offset="100%" stopColor="#8E1B1B" stopOpacity={0.05} />
                      </linearGradient>
                    </defs>
                    <Radar
                      name="Percentage"
                      dataKey="percentage"
                      stroke="#8E1B1B"
                      strokeWidth={2.5}
                      fill="url(#radarGradient)"
                      dot={{ r: 5, fill: '#8E1B1B', stroke: '#fff', strokeWidth: 2 }}
                    />
                    <Tooltip
                      content={({ payload }) => {
                        if (payload && payload.length > 0) {
                          const data = payload[0].payload as EmotionData;
                          const emotionKey = data.emotion.toLowerCase();
                          const meta = emotionMeta[emotionKey];
                          return (
                            <div className="bg-white/95 backdrop-blur-sm p-3.5 rounded-xl shadow-xl border border-gray-100 min-w-[160px]">
                              <div className="flex items-center gap-2 mb-2">
                                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: meta?.color || '#8E1B1B' }} />
                                <span className="font-semibold text-sm text-gray-900">{data.emotion}</span>
                              </div>
                              <div className="space-y-1">
                                <div className="flex justify-between text-xs">
                                  <span className="text-gray-500">Count</span>
                                  <span className="font-medium text-gray-800">{data.count}</span>
                                </div>
                                <div className="flex justify-between text-xs">
                                  <span className="text-gray-500">Percentage</span>
                                  <span className="font-bold" style={{ color: meta?.color || '#8E1B1B' }}>{data.percentage.toFixed(1)}%</span>
                                </div>
                              </div>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Emotion Breakdown Cards */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Breakdown</h4>
              {sortedEmotions.map(({ emotion, count, percentage }, index) => {
                const Icon = emotionIcons[emotion];
                const meta = emotionMeta[emotion];
                return (
                  <div
                    key={emotion}
                    className={cn(
                      "group relative flex items-center gap-4 p-4 rounded-xl border transition-all duration-200",
                      index === 0
                        ? "bg-gradient-to-r from-white to-gray-50/50 border-gray-200 shadow-sm"
                        : "bg-white border-gray-100 hover:border-gray-200 hover:shadow-sm"
                    )}
                  >
                    <div className={cn("p-2.5 rounded-xl shrink-0", meta.bg)}>
                      <Icon className="h-5 w-5" style={{ color: meta.color }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-gray-800 capitalize">{emotion}</span>
                        <span className="text-lg font-bold tabular-nums" style={{ color: meta.color }}>
                          {percentage.toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-700 ease-out"
                          style={{
                            width: `${percentage}%`,
                            background: `linear-gradient(90deg, ${meta.color}cc, ${meta.color})`,
                          }}
                        />
                      </div>
                      <p className="text-[11px] text-gray-400 mt-1.5">{count.toLocaleString()} responses</p>
                    </div>
                    {index === 0 && (
                      <div className="absolute -top-2 -right-2 px-2 py-0.5 rounded-full text-[10px] font-bold text-white bg-gradient-to-r from-amber-400 to-orange-500 shadow-sm">
                        TOP
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Emotion by Field */}
      {emotionByField && (
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-indigo-50">
                <TrendingDown className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-gray-900">Emotion by Feedback Field</h3>
                <p className="text-xs text-gray-400 mt-0.5">How emotions vary across different feedback sections</p>
              </div>
            </div>
          </div>
          <div className="p-6 space-y-5">
            {Object.entries(emotionByField).map(([fieldName, emotions]) => {
              const totalFieldEmotions = Object.values(emotions).reduce((sum, count) => sum + count, 0);
              if (totalFieldEmotions === 0) return null;
              return (
                <div key={fieldName} className="rounded-xl border border-gray-100 overflow-hidden">
                  <div className="px-5 py-3 bg-gray-50/50 border-b border-gray-100">
                    <h4 className="text-sm font-semibold text-gray-700">{fieldName}</h4>
                  </div>
                  <div className="p-4 space-y-2.5">
                    {Object.entries(emotions)
                      .sort(([, a], [, b]) => b - a)
                      .filter(([, count]) => count > 0)
                      .map(([emotion, count]) => {
                        const Icon = emotionIcons[emotion];
                        const meta = emotionMeta[emotion];
                        const pct = totalFieldEmotions > 0 ? ((count / totalFieldEmotions) * 100) : 0;
                        return (
                          <div key={emotion} className="flex items-center gap-3">
                            <div className={cn("p-1.5 rounded-lg shrink-0", meta.bg)}>
                              <Icon className="h-3.5 w-3.5" style={{ color: meta.color }} />
                            </div>
                            <span className="text-sm text-gray-600 capitalize w-28 shrink-0">{emotion}</span>
                            <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full transition-all duration-500"
                                style={{
                                  backgroundColor: meta.color,
                                  width: `${pct}%`,
                                }}
                              />
                            </div>
                            <span className="text-xs font-semibold w-20 text-right tabular-nums" style={{ color: meta.color }}>
                              {count} ({pct.toFixed(1)}%)
                            </span>
                          </div>
                        );
                      })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Legacy fallback when no emotionByField */}
      {!emotionByField && (
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-100">
            <h3 className="text-base font-semibold text-gray-900">Emotion Summary</h3>
            <p className="text-xs text-gray-400 mt-0.5">Overview of emotion categories</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
              {Object.entries(emotionDistribution).map(([emotion, count]) => {
                const Icon = emotionIcons[emotion];
                const meta = emotionMeta[emotion];
                const pct = totalEmotions > 0 ? ((count / totalEmotions) * 100).toFixed(1) : '0';
                return (
                  <div key={emotion} className="text-center p-4 rounded-xl border border-gray-100 hover:border-gray-200 hover:shadow-sm transition-all">
                    <div className={cn("w-12 h-12 rounded-xl mx-auto flex items-center justify-center mb-3", meta.bg)}>
                      <Icon className="h-6 w-6" style={{ color: meta.color }} />
                    </div>
                    <p className="font-semibold text-sm capitalize text-gray-700">{emotion}</p>
                    <p className="text-2xl font-bold mt-1 tabular-nums" style={{ color: meta.color }}>{count}</p>
                    <p className="text-[11px] text-gray-400 mt-0.5">{pct}%</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
