'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Flame } from 'lucide-react';

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

const emotionColors: { [key: string]: { low: string; medium: string; high: string; veryHigh: string } } = {
  joy: { low: '#dcfce7', medium: '#86efac', high: '#22c55e', veryHigh: '#15803d' },
  satisfaction: { low: '#dbeafe', medium: '#93c5fd', high: '#3b82f6', veryHigh: '#1e40af' },
  acceptance: { low: '#ede9fe', medium: '#c4b5fd', high: '#8b5cf6', veryHigh: '#6d28d9' },
  boredom: { low: '#fef3c7', medium: '#fcd34d', high: '#f59e0b', veryHigh: '#d97706' },
  disappointment: { low: '#fee2e2', medium: '#fca5a5', high: '#ef4444', veryHigh: '#dc2626' },
};

export default function EmotionHeatmap({ emotionByField, totalEmotions }: EmotionHeatmapProps) {
  if (!emotionByField) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-gray-500">
          No emotion data available for heatmap
        </CardContent>
      </Card>
    );
  }

  const fields = Object.keys(emotionByField);
  
  // Calculate max value across all cells for normalization
  const maxValue = Math.max(
    ...fields.flatMap(field => 
      emotions.map(emotion => emotionByField[field][emotion] || 0)
    ),
    1 // Ensure at least 1 to avoid division by zero
  );

  const getHeatColor = (emotion: string, value: number) => {
    if (value === 0) return '#f3f4f6'; // gray-100 for zero
    
    const intensity = value / maxValue;
    // Use maroon color (#8E1B1B) with varying opacity for intensity
    const alpha = intensity;
    return `rgba(142, 27, 27, ${alpha})`;
  };

  const getTextColor = (emotion: string, value: number) => {
    if (value === 0) return '#9ca3af'; // gray-400
    const intensity = value / maxValue;
    return intensity > 0.4 ? '#ffffff' : '#1f2937'; // white for dark bg, dark for light bg
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Flame className="h-5 w-5 text-[#8E1B1B]" />
          Emotion Heatmap
        </CardTitle>
        <CardDescription>
          Intensity of emotions across different feedback sections
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
            <div className="grid gap-1" style={{ gridTemplateColumns: `200px repeat(${emotions.length}, minmax(100px, 1fr))` }}>
              {/* Header Row */}
              <div className="p-3 font-semibold text-sm text-gray-700 bg-gray-50 rounded-tl-lg"></div>
              {emotions.map((emotion) => (
                <div
                  key={emotion}
                  className="p-3 text-center font-semibold text-sm capitalize bg-gray-50"
                  style={{ 
                    color: emotionColors[emotion].veryHigh,
                  }}
                >
                  {emotion}
                </div>
              ))}

              {/* Data Rows */}
              {fields.map((field, fieldIndex) => (
                <>
                  <div
                    key={`label-${field}`}
                    className={`p-3 font-medium text-sm text-gray-700 bg-gray-50 ${
                      fieldIndex === fields.length - 1 ? 'rounded-bl-lg' : ''
                    }`}
                  >
                    {field}
                  </div>
                  {emotions.map((emotion, emotionIndex) => {
                    const value = emotionByField[field][emotion] || 0;
                    const percentage = totalEmotions > 0 ? ((value / totalEmotions) * 100).toFixed(1) : '0';
                    
                    return (
                      <div
                        key={`${field}-${emotion}`}
                        className={`p-3 text-center transition-all hover:scale-105 hover:shadow-lg cursor-default relative group ${
                          fieldIndex === fields.length - 1 && emotionIndex === emotions.length - 1 ? 'rounded-br-lg' : ''
                        }`}
                        style={{
                          backgroundColor: getHeatColor(emotion, value),
                          color: getTextColor(emotion, value),
                        }}
                      >
                        <div className="font-bold text-lg">{value}</div>
                        <div className="text-xs opacity-75">{percentage}%</div>
                        
                        {/* Tooltip */}
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                          {field}: {value} {emotion} responses
                          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                            <div className="border-4 border-transparent border-t-gray-900"></div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </>
              ))}
            </div>

            {/* Legend */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Intensity Scale</h4>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <span>Low</span>
                <div className="flex gap-1">
                  {[0.2, 0.4, 0.6, 0.8, 1.0].map((intensity, i) => (
                    <div
                      key={i}
                      className="w-12 h-6 rounded"
                      style={{
                        backgroundColor: intensity < 0.3 
                          ? '#f3f4f6' 
                          : `rgba(142, 27, 27, ${intensity})`,
                      }}
                    ></div>
                  ))}
                </div>
                <span>High</span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Cell intensity represents the relative frequency of each emotion within the feedback section
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
