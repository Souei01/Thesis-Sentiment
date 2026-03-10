'use client';

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
} from 'recharts';
import { BookOpen, Hash, TrendingUp, Lightbulb, AlertCircle, CheckCircle, Clock, Users, MessageSquare, Presentation, Book, Clipboard, Folder, Info, Sparkles, ArrowUpRight } from 'lucide-react';
import { cn } from '@/lib/utils';

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
  '#8E1B1B', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#ec4899',
];

const GRADIENT_PAIRS = [
  ['#8E1B1B', '#C62828'],
  ['#3b82f6', '#6366f1'],
  ['#10b981', '#059669'],
  ['#f59e0b', '#d97706'],
  ['#8b5cf6', '#7c3aed'],
  ['#ef4444', '#dc2626'],
  ['#06b6d4', '#0891b2'],
  ['#ec4899', '#db2777'],
];

export default function TopicModelingDashboard({ topics, topicDistribution, totalTopics, topicInsights }: TopicModelingProps) {
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

  const priorityConfig = {
    high: { bg: 'bg-red-50', border: 'border-red-200/60', text: 'text-red-700', icon: 'text-red-500', badge: 'bg-red-100 text-red-700', PriorityIcon: AlertCircle },
    medium: { bg: 'bg-amber-50', border: 'border-amber-200/60', text: 'text-amber-700', icon: 'text-amber-500', badge: 'bg-amber-100 text-amber-700', PriorityIcon: Clock },
    low: { bg: 'bg-emerald-50', border: 'border-emerald-200/60', text: 'text-emerald-700', icon: 'text-emerald-500', badge: 'bg-emerald-100 text-emerald-700', PriorityIcon: CheckCircle },
  };

  const distributionData = Object.entries(topicDistribution).map(([topic, count]) => ({
    topic: topic.replace('Topic ', 'T'),
    count,
    fullName: topic,
  }));

  const pieData = Object.entries(topicDistribution).map(([topic, count]) => ({
    name: topic,
    value: count,
  }));

  const totalFeedback = Object.values(topicDistribution).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'Total Topics', value: totalTopics, icon: Hash, color: '#8E1B1B', gradient: 'from-[#8E1B1B] to-rose-500', bg: 'bg-rose-50' },
          { label: 'Feedback Analyzed', value: totalFeedback, icon: BookOpen, color: '#3b82f6', gradient: 'from-blue-500 to-indigo-500', bg: 'bg-blue-50' },
          { label: 'Avg. per Topic', value: totalTopics > 0 ? Math.round(totalFeedback / totalTopics) : 0, icon: TrendingUp, color: '#10b981', gradient: 'from-emerald-500 to-green-500', bg: 'bg-emerald-50' },
        ].map(({ label, value, icon: Icon, color, gradient, bg }) => (
          <div key={label} className="group relative bg-white rounded-2xl border border-gray-200/60 shadow-sm hover:shadow-lg hover:shadow-gray-200/50 transition-all duration-300 overflow-hidden">
            <div className={cn("absolute top-0 left-0 w-full h-1 bg-gradient-to-r", gradient)} />
            <div className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className={cn("p-2.5 rounded-xl", bg)}>
                  <Icon className="h-5 w-5" style={{ color }} />
                </div>
                <ArrowUpRight className="h-4 w-4 text-gray-300 group-hover:text-gray-500 transition-colors" />
              </div>
              <p className="text-sm text-gray-500 font-medium">{label}</p>
              <p className="text-3xl font-bold mt-1 tracking-tight" style={{ color }}>{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
          <div className="px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-rose-50">
                <Hash className="h-3.5 w-3.5 text-[#8E1B1B]" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-800">Topic Distribution</h3>
                <p className="text-[11px] text-gray-400 mt-0.5">Feedback items per topic</p>
              </div>
            </div>
          </div>
          <div className="p-5">
            <div className="h-[340px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distributionData} barCategoryGap="20%">
                  <defs>
                    {distributionData.map((_, index) => (
                      <linearGradient key={`barGrad-${index}`} id={`barGrad-${index}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={GRADIENT_PAIRS[index % GRADIENT_PAIRS.length][0]} stopOpacity={1} />
                        <stop offset="100%" stopColor={GRADIENT_PAIRS[index % GRADIENT_PAIRS.length][1]} stopOpacity={0.7} />
                      </linearGradient>
                    ))}
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="topic" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: '#e2e8f0' }} tickLine={false} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(0,0,0,0.03)', radius: 8 }}
                    content={({ payload }) => {
                      if (payload && payload.length > 0) {
                        const data = payload[0].payload;
                        const pct = totalFeedback > 0 ? ((data.count / totalFeedback) * 100).toFixed(1) : '0';
                        return (
                          <div className="bg-white/95 backdrop-blur-sm p-3.5 rounded-xl shadow-xl border border-gray-100 min-w-[150px]">
                            <p className="font-semibold text-sm text-gray-900">{data.fullName}</p>
                            <div className="mt-1.5 space-y-0.5">
                              <p className="text-xs text-gray-500">{data.count} feedback items</p>
                              <p className="text-xs font-medium text-[#8E1B1B]">{pct}% of total</p>
                            </div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                    {distributionData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={`url(#barGrad-${index})`} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Pie Chart */}
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
          <div className="px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-indigo-50">
                <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-800">Topic Proportions</h3>
                <p className="text-[11px] text-gray-400 mt-0.5">Percentage distribution</p>
              </div>
            </div>
          </div>
          <div className="p-5">
            <div className="h-[340px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <defs>
                    {pieData.map((_, index) => (
                      <linearGradient key={`pieGrad-${index}`} id={`pieGrad-${index}`} x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stopColor={GRADIENT_PAIRS[index % GRADIENT_PAIRS.length][0]} />
                        <stop offset="100%" stopColor={GRADIENT_PAIRS[index % GRADIENT_PAIRS.length][1]} />
                      </linearGradient>
                    ))}
                  </defs>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={3}
                    dataKey="value"
                    strokeWidth={2}
                    stroke="#fff"
                    label={({ name, percent, cx, cy, midAngle, outerRadius: or }) => {
                      const RADIAN = Math.PI / 180;
                      const radius = (or || 100) + 25;
                      const x = (cx || 0) + radius * Math.cos(-midAngle * RADIAN);
                      const y = (cy || 0) + radius * Math.sin(-midAngle * RADIAN);
                      return (
                        <text x={x} y={y} fill="#64748b" fontSize={11} fontWeight={600} textAnchor={x > (cx || 0) ? 'start' : 'end'} dominantBaseline="central">
                          {name.replace('Topic ', 'T')}: {(percent * 100).toFixed(0)}%
                        </text>
                      );
                    }}
                  >
                    {pieData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={`url(#pieGrad-${index})`} />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ payload }) => {
                      if (payload && payload.length > 0) {
                        const data = payload[0];
                        const percentage = ((data.value as number) / totalFeedback * 100).toFixed(1);
                        return (
                          <div className="bg-white/95 backdrop-blur-sm p-3.5 rounded-xl shadow-xl border border-gray-100 min-w-[140px]">
                            <p className="font-semibold text-sm text-gray-900">{data.name}</p>
                            <p className="text-xs text-gray-500 mt-1">
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
          </div>
        </div>
      </div>

      {/* Topic Keywords */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-violet-50">
              <BookOpen className="h-3.5 w-3.5 text-violet-600" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-800">Topic Keywords</h3>
              <p className="text-[11px] text-gray-400 mt-0.5">Key terms identified for each topic theme</p>
            </div>
          </div>
        </div>
        <div className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {topics
              .filter((topic) => (topicDistribution[topic.topic] || 0) > 0)
              .map((topic, index) => {
                const count = topicDistribution[topic.topic] || 0;
                const percentage = totalFeedback > 0 ? ((count / totalFeedback) * 100).toFixed(1) : '0';
                const color = COLORS[index % COLORS.length];

                return (
                  <div
                    key={topic.topic}
                    className="group p-5 rounded-xl border border-gray-100 hover:border-gray-200 hover:shadow-md transition-all duration-200 relative overflow-hidden"
                  >
                    {/* Accent border left */}
                    <div className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl" style={{ backgroundColor: color }} />
                    
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-sm" style={{ color }}>
                        {topic.topic}
                      </h3>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-[10px] rounded-full border-gray-200 text-gray-500">
                          {count} items
                        </Badge>
                        <span className="text-xs font-bold tabular-nums" style={{ color }}>{percentage}%</span>
                      </div>
                    </div>

                    {/* Progress bar */}
                    <div className="h-1 w-full bg-gray-100 rounded-full overflow-hidden mb-3">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${percentage}%`, backgroundColor: color }}
                      />
                    </div>

                    <div className="flex flex-wrap gap-1.5">
                      {topic.keywords.slice(0, 8).map((keyword, kidx) => (
                        <span
                          key={kidx}
                          className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium transition-colors"
                          style={{
                            backgroundColor: `${color}10`,
                            color: color,
                          }}
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      </div>

      {/* Course Improvement Insights */}
      {topicInsights && topicInsights.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-amber-50">
                <Lightbulb className="h-3.5 w-3.5 text-amber-600" />
              </div>
              <h3 className="text-sm font-semibold text-gray-800">Course Improvement Insights</h3>
            </div>
          </div>
          <div className="p-5 space-y-6">
            {topicInsights.map((topicInsight, tidx) => {
              const topicColor = COLORS[tidx % COLORS.length];
              const hasInsights = topicInsight.insights && topicInsight.insights.length > 0;
              if (!hasInsights) return null;

              return (
                <div key={topicInsight.topic} className="space-y-3">
                  <div className="flex items-center gap-2 pb-2">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: topicColor }} />
                    <h4 className="text-sm font-semibold" style={{ color: topicColor }}>
                      {topicInsight.topic}
                    </h4>
                  </div>
                  <div className="grid grid-cols-1 gap-3">
                    {topicInsight.insights.map((insight, iidx) => {
                      const Icon = iconMap[insight.icon] || Info;
                      const config = priorityConfig[insight.priority];

                      return (
                        <div
                          key={iidx}
                          className={cn(
                            "p-4 rounded-xl border-l-[3px] transition-all hover:shadow-sm",
                            config.bg,
                            config.border
                          )}
                        >
                          <div className="flex items-start gap-3">
                            <div className="p-2 rounded-lg bg-white shadow-sm shrink-0">
                              <Icon className={cn("h-4 w-4", config.icon)} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1.5">
                                <h5 className={cn("font-semibold text-sm", config.text)}>
                                  {insight.category}
                                </h5>
                                <span className={cn("inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase", config.badge)}>
                                  <config.PriorityIcon className="h-2.5 w-2.5" />
                                  {insight.priority}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 leading-relaxed">
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
        </div>
      )}
    </div>
  );
}
