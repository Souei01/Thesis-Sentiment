'use client';

import { Fragment } from 'react';
import { Flame, Smile, Frown, Meh, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmotionHeatmapProps {
  emotionByField?: {
    [fieldName: string]: {
      joy: number;
      satisfaction: number;
      acceptance: number;
      boredom: number;
      disappointment: number;
    };
  };
  totalEmotions: number;
}

const emotions = ['joy', 'satisfaction', 'acceptance', 'boredom', 'disappointment'] as const;

const emotionMeta: { [key: string]: { color: string; bg: string; icon: any } } = {
  joy: { color: '#10b981', bg: 'bg-emerald-50', icon: Smile },
  satisfaction: { color: '#3b82f6', bg: 'bg-blue-50', icon: Smile },
  acceptance: { color: '#8b5cf6', bg: 'bg-violet-50', icon: Meh },
  boredom: { color: '#f59e0b', bg: 'bg-amber-50', icon: Clock },
  disappointment: { color: '#ef4444', bg: 'bg-red-50', icon: Frown },
};

export default function EmotionHeatmap({ emotionByField, totalEmotions }: EmotionHeatmapProps) {
  if (!emotionByField) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="p-12 text-center">
          <div className="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mx-auto mb-4">
            <Flame className="h-7 w-7 text-gray-300" />
          </div>
          <p className="text-gray-500 font-medium">No emotion data available</p>
          <p className="text-sm text-gray-400 mt-1">Heatmap data will appear after feedback is analyzed.</p>
        </div>
      </div>
    );
  }

  const fields = Object.keys(emotionByField);
  
  const maxValue = Math.max(
    ...fields.flatMap(field => 
      emotions.map(emotion => emotionByField[field][emotion] || 0)
    ),
    1
  );

  const getHeatColor = (value: number) => {
    if (value === 0) return 'rgba(243, 244, 246, 0.5)';
    const intensity = value / maxValue;
    return `rgba(142, 27, 27, ${Math.max(intensity * 0.85, 0.08)})`;
  };

  const getTextColor = (value: number) => {
    if (value === 0) return '#d1d5db';
    const intensity = value / maxValue;
    return intensity > 0.35 ? '#ffffff' : '#374151';
  };

  const getSubTextColor = (value: number) => {
    if (value === 0) return '#e5e7eb';
    const intensity = value / maxValue;
    return intensity > 0.35 ? 'rgba(255,255,255,0.7)' : '#9ca3af';
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
      <div className="px-6 py-5 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-orange-50 to-red-50">
            <Flame className="h-5 w-5 text-[#8E1B1B]" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-900">Emotion Heatmap</h3>
            <p className="text-xs text-gray-400 mt-0.5">Intensity of emotions across feedback sections</p>
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="overflow-x-auto -mx-2 px-2">
          <div className="inline-block min-w-full">
            {/* Table */}
            <div
              className="grid gap-[3px] rounded-xl overflow-hidden bg-gray-100/50"
              style={{ gridTemplateColumns: `minmax(180px, 200px) repeat(${emotions.length}, minmax(90px, 1fr))` }}
            >
              {/* Header Row */}
              <div className="p-3 bg-white text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-end">
                Field / Emotion
              </div>
              {emotions.map((emotion) => {
                const meta = emotionMeta[emotion];
                const Icon = meta.icon;
                return (
                  <div
                    key={emotion}
                    className="p-3 bg-white flex flex-col items-center justify-end gap-1.5"
                  >
                    <div className={cn("p-1.5 rounded-lg", meta.bg)}>
                      <Icon className="h-3.5 w-3.5" style={{ color: meta.color }} />
                    </div>
                    <span className="text-[11px] font-semibold capitalize" style={{ color: meta.color }}>
                      {emotion}
                    </span>
                  </div>
                );
              })}

              {/* Data Rows */}
              {fields.map((field) => (
                <Fragment key={field}>
                  <div className="p-3.5 bg-white font-medium text-sm text-gray-700 flex items-center">
                    {field}
                  </div>
                  {emotions.map((emotion) => {
                    const value = emotionByField[field][emotion] || 0;
                    const percentage = totalEmotions > 0 ? ((value / totalEmotions) * 100).toFixed(1) : '0';
                    
                    return (
                      <div
                        key={`${field}-${emotion}`}
                        className="relative group cursor-default transition-transform duration-150 hover:scale-[1.04] hover:z-10"
                      >
                        <div
                          className="p-3 h-full flex flex-col items-center justify-center rounded-sm"
                          style={{
                            backgroundColor: getHeatColor(value),
                          }}
                        >
                          <span
                            className="text-xl font-bold tabular-nums leading-none"
                            style={{ color: getTextColor(value) }}
                          >
                            {value}
                          </span>
                          <span
                            className="text-[10px] mt-1 tabular-nums"
                            style={{ color: getSubTextColor(value) }}
                          >
                            {percentage}%
                          </span>
                        </div>

                        {/* Modern Tooltip */}
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none z-20">
                          <div className="bg-gray-900/95 backdrop-blur-sm text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap shadow-xl">
                            <span className="font-semibold">{field}</span>
                            <br />
                            <span className="capitalize">{emotion}</span>: {value} ({percentage}%)
                          </div>
                          <div className="w-2 h-2 bg-gray-900/95 rotate-45 mx-auto -mt-1" />
                        </div>
                      </div>
                    );
                  })}
                </Fragment>
              ))}
            </div>

            {/* Legend */}
            <div className="mt-6 flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <span className="text-xs font-medium text-gray-400">Intensity</span>
                <div className="flex items-center gap-0.5">
                  {[0, 0.15, 0.3, 0.5, 0.7, 0.85].map((intensity, i) => (
                    <div
                      key={i}
                      className="w-8 h-5 first:rounded-l-md last:rounded-r-md"
                      style={{
                        backgroundColor: intensity === 0
                          ? 'rgba(243, 244, 246, 0.5)'
                          : `rgba(142, 27, 27, ${intensity})`,
                      }}
                    />
                  ))}
                </div>
                <div className="flex gap-4 text-[10px] text-gray-400">
                  <span>Low</span>
                  <span>High</span>
                </div>
              </div>
              <p className="text-[11px] text-gray-400">
                Cell color intensity represents relative frequency of each emotion
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
