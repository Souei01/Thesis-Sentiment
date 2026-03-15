'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Spinner } from '@/components/ui/spinner';
import { Button } from '@/components/ui/button';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  BarChart3,
  FileText,
  Shield,
  Star,
  Brain,
  Users,
  Target,
  Lightbulb,
  Info,
  ThumbsUp,
  ThumbsDown,
  ArrowRight,
  Download,
  RefreshCw
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { revisionService } from '@/services/revisionService';

interface RevisionAnalysisProps {
  filters?: {
    semester?: string;
    academic_year?: string;
    instructor_id?: string;
    course_id?: string;
    department?: string;
  };
}

export default function RevisionAnalysis({ filters = {} }: RevisionAnalysisProps) {
  const [activeTab, setActiveTab] = useState<'alignment' | 'thematic' | 'consistency' | 'negative' | 'comparison'>('alignment');
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>({});

  const tabs = [
    { id: 'alignment', label: 'Alignment Analysis', icon: Target, desc: 'Likert vs Sentiment' },
    { id: 'thematic', label: 'Thematic Analysis', icon: Lightbulb, desc: 'Negative Themes' },
    { id: 'consistency', label: 'Data Encoding', icon: Shield, desc: 'Reliability' },
    { id: 'negative', label: 'Negative Summary', icon: Star, desc: 'Low Ratings' },
    { id: 'comparison', label: 'AI vs Expert', icon: Brain, desc: 'Model Validation' },
  ];

  useEffect(() => {
    loadData();
  }, [activeTab, JSON.stringify(filters)]);

  const loadData = async () => {
    setLoading(true);
    try {
      let result;
      switch (activeTab) {
        case 'alignment':
          result = await revisionService.getAlignmentAnalysis(filters);
          break;
        case 'thematic':
          result = await revisionService.getThematicAnalysis(filters);
          break;
        case 'consistency':
          result = await revisionService.getEncodingConsistency(filters);
          break;
        case 'negative':
          result = await revisionService.getNegativeSummary(filters);
          break;
        case 'comparison':
          result = await revisionService.getAIExpertComparison(filters);
          break;
      }
      setData(result);
    } catch (error) {
      console.error('Error loading revision data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-5 bg-gradient-to-r from-[#8E1B1B] to-rose-700">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Thesis Revision Analysis</h1>
              <p className="text-rose-100 text-sm mt-1">Comprehensive analysis for research validation and improvement</p>
            </div>
            <Button
              onClick={loadData}
              variant="outline"
              size="sm"
              className="bg-white/10 border-white/20 text-white hover:bg-white/20"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="px-6 border-b border-gray-100 overflow-x-auto">
          <div className="flex gap-1 -mb-px min-w-max">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={cn(
                    "px-4 py-3 text-sm font-medium transition-all relative group",
                    isActive
                      ? "text-[#8E1B1B]"
                      : "text-gray-500 hover:text-gray-700"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <Icon className={cn("h-4 w-4", isActive && "text-[#8E1B1B]")} />
                    <div className="text-left">
                      <div>{tab.label}</div>
                      <div className="text-[10px] text-gray-400 font-normal">{tab.desc}</div>
                    </div>
                  </div>
                  {isActive && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8E1B1B]" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Spinner className="h-8 w-8 text-[#8E1B1B]" />
        </div>
      ) : (
        <>
          {activeTab === 'alignment' && <AlignmentAnalysisView data={data} />}
          {activeTab === 'thematic' && <ThematicAnalysisView data={data} />}
          {activeTab === 'consistency' && <EncodingConsistencyView data={data} />}
          {activeTab === 'negative' && <NegativeSummaryView data={data} />}
          {activeTab === 'comparison' && <AIExpertComparisonView data={data} />}
        </>
      )}
    </div>
  );
}

// ============================================================================
// REVISION #1: Alignment Analysis
// ============================================================================
function AlignmentAnalysisView({ data }: { data: any }) {
  if (!data || !data.alignment_by_rating) {
    return <div className="text-center py-10 text-gray-500">No alignment data available</div>;
  }

  const ratings = ['5_star', '4_star', '3_star', '2_star', '1_star'];
  const ratingLabels = {
    '5_star': '5 Stars - Excellent',
    '4_star': '4 Stars - Very Good',
    '3_star': '3 Stars - Good',
    '2_star': '2 Stars - Poor',
    '1_star': '1 Star - Very Poor',
  };

  const ratingColors = {
    '5_star': { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', bar: '#10b981' },
    '4_star': { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', bar: '#3b82f6' },
    '3_star': { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', bar: '#f59e0b' },
    '2_star': { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', bar: '#fb923c' },
    '1_star': { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', bar: '#ef4444' },
  };

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-white shadow-sm">
            <Target className="h-6 w-6 text-indigo-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-2">Alignment Analysis Summary</h3>
            <p className="text-sm text-gray-600 mb-4">{data.summary}</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500">Overall Alignment</p>
                <p className="text-2xl font-bold text-indigo-600">{data.overall_alignment_percentage}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Total Feedback</p>
                <p className="text-2xl font-bold text-gray-900">{data.total_feedback}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Rating Breakdown */}
      <div className="grid grid-cols-1 gap-4">
        {ratings.map((rating) => {
          const ratingData = data.alignment_by_rating[rating];
          if (!ratingData || ratingData.count === 0) return null;

          const alignmentPct = ratingData.count > 0 ? ((ratingData.aligned / ratingData.count) * 100).toFixed(1) : 0;
          const colors = ratingColors[rating as keyof typeof ratingColors];

          return (
            <div
              key={rating}
              className={cn(
                "rounded-xl border p-5 transition-all hover:shadow-md",
                colors.bg,
                colors.border
              )}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Star className={cn("h-5 w-5", colors.text)} />
                  <h3 className={cn("font-semibold", colors.text)}>
                    {ratingLabels[rating as keyof typeof ratingLabels]}
                  </h3>
                </div>
                <Badge variant="outline" className="text-xs">
                  {ratingData.count} responses
                </Badge>
              </div>

              {/* Alignment Progress */}
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs text-gray-600">Alignment Rate</span>
                  <span className="text-sm font-bold" style={{ color: colors.bar }}>{alignmentPct}%</span>
                </div>
                <div className="h-2 bg-white/50 rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all duration-700"
                    style={{ width: `${alignmentPct}%`, backgroundColor: colors.bar }}
                  />
                </div>
              </div>

              {/* Emotion Distribution */}
              <div className="grid grid-cols-5 gap-2">
                {Object.entries(ratingData.emotions).map(([emotion, count]: [string, any]) => (
                  <div key={emotion} className="text-center">
                    <div className="text-lg font-bold text-gray-900">{count}</div>
                    <div className="text-[10px] text-gray-500 capitalize">{emotion}</div>
                  </div>
                ))}
              </div>

              {/* Aligned vs Misaligned */}
              <div className="mt-4 pt-4 border-t border-gray-200/50 flex gap-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span className="text-sm text-gray-600">
                    Aligned: <span className="font-semibold">{ratingData.aligned}</span>
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <XCircle className="h-4 w-4 text-red-600" />
                  <span className="text-sm text-gray-600">
                    Misaligned: <span className="font-semibold">{ratingData.misaligned}</span>
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Misaligned Cases */}
      {data.misaligned_cases && data.misaligned_cases.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <h3 className="font-semibold text-gray-900">Misaligned Cases (Sample)</h3>
            </div>
            <p className="text-xs text-gray-500 mt-1">Instances where Likert rating doesn't match emotional sentiment</p>
          </div>
          <div className="p-5 space-y-3">
            {data.misaligned_cases.map((caseItem: any, idx: number) => (
              <div key={idx} className="p-4 rounded-lg bg-amber-50/50 border border-amber-100">
                <div className="flex items-start gap-3">
                  <Badge variant="outline" className="text-xs">{caseItem.rating} ⭐</Badge>
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 mb-2">{caseItem.sample_text}</p>
                    <div className="flex flex-wrap gap-1">
                      {caseItem.emotions.map((emotion: string, eidx: number) => (
                        <span key={eidx} className="px-2 py-0.5 rounded-full bg-white text-xs capitalize">
                          {emotion}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">{caseItem.course}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// REVISION #2: Thematic Analysis
// ============================================================================
function ThematicAnalysisView({ data }: { data: any }) {
  if (!data || !data.course_breakdown) {
    return <div className="text-center py-10 text-gray-500">No thematic data available</div>;
  }

  const themeColors = {
    teaching_methods: { color: '#ef4444', bg: 'bg-red-50', icon: Users },
    course_materials: { color: '#f59e0b', bg: 'bg-amber-50', icon: FileText },
    assessment: { color: '#8b5cf6', bg: 'bg-violet-50', icon: BarChart3 },
    workload: { color: '#3b82f6', bg: 'bg-blue-50', icon: TrendingUp },
    communication: { color: '#10b981', bg: 'bg-emerald-50', icon: Info },
    engagement: { color: '#ec4899', bg: 'bg-pink-50', icon: Lightbulb },
    other: { color: '#64748b', bg: 'bg-gray-50', icon: AlertTriangle },
  };

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-200/60 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-50">
              <TrendingDown className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Negative Feedback</p>
              <p className="text-2xl font-bold text-gray-900">{data.total_negative_feedback}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200/60 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-50">
              <BarChart3 className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Courses Analyzed</p>
              <p className="text-2xl font-bold text-gray-900">{data.courses_analyzed}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200/60 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-violet-50">
              <Lightbulb className="h-5 w-5 text-violet-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Themes Identified</p>
              <p className="text-2xl font-bold text-gray-900">
                {Object.keys(data.overall_themes || {}).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Overall Themes */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Overall Theme Distribution</h3>
        </div>
        <div className="p-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(data.overall_themes || {}).map(([theme, count]: [string, any]) => {
              const themeConfig = themeColors[theme as keyof typeof themeColors];
              const Icon = themeConfig?.icon || AlertTriangle;
              return (
                <div
                  key={theme}
                  className={cn(
                    "p-4 rounded-xl border",
                    themeConfig?.bg || 'bg-gray-50',
                    "border-gray-200"
                  )}
                >
                  <Icon className="h-5 w-5 mb-2" style={{ color: themeConfig?.color }} />
                  <p className="text-xs text-gray-600 capitalize mb-1">{theme.replace('_', ' ')}</p>
                  <p className="text-2xl font-bold" style={{ color: themeConfig?.color }}>{count}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Course Breakdown */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Per-Course Analysis</h3>
          <p className="text-xs text-gray-500 mt-1">Negative feedback breakdown by course</p>
        </div>
        <div className="p-5 space-y-4">
          {data.course_breakdown.slice(0, 10).map((course: any, idx: number) => (
            <div
              key={idx}
              className="p-5 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="font-semibold text-gray-900">{course.course_code}</h4>
                  <p className="text-sm text-gray-600">{course.course_name}</p>
                  <p className="text-xs text-gray-500 mt-1">Instructor: {course.instructor}</p>
                </div>
                <div className="text-right">
                  <Badge variant="outline" className="mb-1">{course.count} feedback</Badge>
                  <div className="flex items-center gap-1">
                    <Star className="h-3 w-3 text-amber-500 fill-amber-500" />
                    <span className="text-sm font-bold text-gray-900">{course.avg_rating}</span>
                  </div>
                </div>
              </div>

              {/* Dominant Theme */}
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className="bg-gradient-to-r from-[#8E1B1B] to-rose-600 text-white">
                    Dominant Theme
                  </Badge>
                  <span className="text-sm font-medium capitalize">{course.dominant_theme.replace('_', ' ')}</span>
                  <span className="text-xs text-gray-500">({course.dominant_theme_count} mentions)</span>
                </div>
              </div>

              {/* Theme Breakdown */}
              <div className="grid grid-cols-3 md:grid-cols-7 gap-2 mb-4">
                {Object.entries(course.themes).map(([theme, count]: [string, any]) => (
                  <div key={theme} className="text-center">
                    <div className="text-sm font-bold text-gray-900">{count}</div>
                    <div className="text-[9px] text-gray-500 capitalize">{theme.replace('_', ' ')}</div>
                  </div>
                ))}
              </div>

              {/* Sample Comments */}
              {course.sample_comments && course.sample_comments.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-gray-700">Sample Comments:</p>
                  {course.sample_comments.map((comment: any, cidx: number) => (
                    <div key={cidx} className="p-3 bg-gray-50 rounded-lg text-sm text-gray-600 italic">
                      "{comment.text}"
                      <Badge variant="outline" className="ml-2 text-[10px]">{comment.emotion}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// REVISION #3: Encoding Consistency
// ============================================================================
function EncodingConsistencyView({ data }: { data: any }) {
  if (!data || !data.kappa_scores) {
    return <div className="text-center py-10 text-gray-500">No consistency data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border border-green-100 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-white shadow-sm">
            <Shield className="h-6 w-6 text-green-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-2">Inter-Rater Reliability Assessment</h3>
            <p className="text-sm text-gray-600 mb-4">{data.conclusion}</p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-500">Average Cohen's Kappa</p>
                <p className="text-2xl font-bold text-green-600">{data.average_kappa}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Total Annotations</p>
                <p className="text-2xl font-bold text-gray-900">{data.total_annotations}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Reliability</p>
                <p className="text-sm font-semibold text-green-600">{data.reliability_assessment}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Kappa Scores */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Cohen's Kappa Scores (Pairwise Agreement)</h3>
        </div>
        <div className="p-5 space-y-3">
          {data.kappa_scores.map((score: any, idx: number) => (
            <div key={idx} className="p-4 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100/50 border border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <Users className="h-5 w-5 text-gray-600" />
                  <span className="font-medium text-gray-900">{score.pair}</span>
                </div>
                <Badge
                  className={cn(
                    score.kappa >= 0.80 ? 'bg-green-100 text-green-700' :
                    score.kappa >= 0.60 ? 'bg-blue-100 text-blue-700' :
                    score.kappa >= 0.40 ? 'bg-amber-100 text-amber-700' :
                    'bg-red-100 text-red-700'
                  )}
                >
                  κ = {score.kappa}
                </Badge>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-500 text-xs">Interpretation</p>
                  <p className="font-medium text-gray-900">{score.interpretation}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs">Raw Agreement</p>
                  <p className="font-medium text-gray-900">{score.raw_agreement_pct}%</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs">Items</p>
                  <p className="font-medium text-gray-900">{score.raw_agreement}/{score.total_items}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bias Control Procedures */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Bias Control Procedures</h3>
          <p className="text-xs text-gray-500 mt-1">Methods implemented to ensure reliable and unbiased encoding</p>
        </div>
        <div className="p-5 space-y-4">
          {data.bias_control_procedures.map((procedure: any, idx: number) => (
            <div key={idx} className="p-5 rounded-xl bg-blue-50/50 border border-blue-100">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-white shadow-sm shrink-0">
                  <CheckCircle2 className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-1">{procedure.procedure}</h4>
                  <p className="text-sm text-gray-600 mb-2">{procedure.description}</p>
                  <div className="flex items-center gap-2">
                    <Info className="h-3 w-3 text-gray-400" />
                    <p className="text-xs text-gray-500">{procedure.evidence}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Emotion Distribution */}
      {data.emotion_distribution && (
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">Emotion Label Distribution</h3>
          </div>
          <div className="p-5">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {Object.entries(data.emotion_distribution).map(([emotion, count]: [string, any]) => (
                <div key={emotion} className="p-4 rounded-xl bg-gray-50 border border-gray-200 text-center">
                  <p className="text-xs text-gray-600 capitalize mb-1">{emotion}</p>
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// REVISION #4: Negative Course Summary
// ============================================================================
function NegativeSummaryView({ data }: { data: any }) {
  if (!data || !data.course_details) {
    return <div className="text-center py-10 text-gray-500">No negative course data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Star Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-200/60 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-50">
              <Star className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">1 Star Ratings</p>
              <p className="text-2xl font-bold text-red-600">{data.star_breakdown['1_star']}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200/60 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-orange-50">
              <Star className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">2 Star Ratings</p>
              <p className="text-2xl font-bold text-orange-600">{data.star_breakdown['2_star']}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200/60 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gray-50">
              <BarChart3 className="h-5 w-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Affected Courses</p>
              <p className="text-2xl font-bold text-gray-900">{data.courses_with_negative_ratings}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Key Trends */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Key Trends</h3>
        </div>
        <div className="p-5">
          <ul className="space-y-2">
            {data.key_trends.map((trend: string, idx: number) => (
              <li key={idx} className="flex items-start gap-3">
                <ArrowRight className="h-4 w-4 text-[#8E1B1B] mt-0.5 shrink-0" />
                <span className="text-sm text-gray-700">{trend}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Course Details */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Negatively Rated Courses</h3>
          <p className="text-xs text-gray-500 mt-1">Detailed breakdown of courses with 1-2 star ratings</p>
        </div>
        <div className="p-5 space-y-4">
          {data.course_details.map((course: any, idx: number) => (
            <div
              key={idx}
              className="p-5 rounded-xl border-l-4 bg-gradient-to-r from-red-50/50 to-transparent"
              style={{ borderLeftColor: course.avg_rating <= 1.5 ? '#ef4444' : '#fb923c' }}
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="font-semibold text-gray-900">{course.course_code}</h4>
                  <p className="text-sm text-gray-600">{course.course_name}</p>
                  <p className="text-xs text-gray-500 mt-1">Instructor: {course.instructor}</p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 mb-1">
                    <Star className="h-4 w-4 text-red-500 fill-red-500" />
                    <span className="text-lg font-bold text-red-600">{course.avg_rating}</span>
                  </div>
                  <Badge variant="outline" className="text-xs">{course.total_negative} negative</Badge>
                </div>
              </div>

              {/* Star Distribution */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="p-3 bg-white rounded-lg border border-red-100">
                  <div className="flex items-center gap-2">
                    <Star className="h-3 w-3 text-red-600 fill-red-600" />
                    <span className="text-xs text-gray-600">1 Star</span>
                  </div>
                  <p className="text-xl font-bold text-red-600 mt-1">{course.star_distribution['1']}</p>
                </div>
                <div className="p-3 bg-white rounded-lg border border-orange-100">
                  <div className="flex items-center gap-2">
                    <Star className="h-3 w-3 text-orange-600 fill-orange-600" />
                    <Star className="h-3 w-3 text-orange-600 fill-orange-600" />
                  </div>
                  <p className="text-xl font-bold text-orange-600 mt-1">{course.star_distribution['2']}</p>
                </div>
              </div>

              {/* Emotions */}
              <div className="mb-4">
                <p className="text-xs font-medium text-gray-700 mb-2">Emotional Profile</p>
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(course.emotion_counts).map(([emotion, count]: [string, any]) => {
                    if (count === 0) return null;
                    return (
                      <span key={emotion} className="px-2 py-1 rounded-full bg-gray-100 text-xs capitalize">
                        {emotion}: {count}
                      </span>
                    );
                  })}
                  <Badge className="bg-gradient-to-r from-red-500 to-orange-500 text-white">
                    Dominant: {course.dominant_emotion}
                  </Badge>
                </div>
              </div>

              {/* Key Concerns */}
              {course.key_concerns && course.key_concerns.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-700 mb-2">Key Concerns:</p>
                  <div className="space-y-2">
                    {course.key_concerns.map((concern: string, cidx: number) => (
                      <div key={cidx} className="p-3 bg-white rounded-lg text-sm text-gray-600 italic border border-gray-100">
                        "{concern}"
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// REVISION #5: AI vs Expert Comparison
// ============================================================================
function AIExpertComparisonView({ data }: { data: any }) {
  if (!data || !data.overall_accuracy) {
    return <div className="text-center py-10 text-gray-500">No comparison data available</div>;
  }

  const accuracyPct = (data.overall_accuracy * 100).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl border border-purple-100 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-white shadow-sm">
            <Brain className="h-6 w-6 text-purple-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-2">AI vs Human Expert Comparison</h3>
            <p className="text-sm text-gray-600 mb-4">{data.conclusion}</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500">Overall Agreement</p>
                <p className="text-3xl font-bold text-purple-600">{accuracyPct}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Total Comparisons</p>
                <p className="text-3xl font-bold text-gray-900">{data.total_comparisons}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Emotion Performance */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Per-Emotion Performance</h3>
          <p className="text-xs text-gray-500 mt-1">Precision, recall, and F1-score for each emotion category</p>
        </div>
        <div className="p-5 space-y-3">
          {data.emotion_performance?.map((perf: any, idx: number) => (
            <div key={idx} className="p-4 rounded-xl bg-gray-50 border border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-gray-900 capitalize">{perf.emotion}</h4>
                  <p className="text-xs text-gray-500">{perf.support} samples</p>
                </div>
                <Badge className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white">
                  F1: {perf.f1_score}
                </Badge>
              </div>
              <div className="grid grid-cols-3 gap-3 text-sm">
                <div>
                  <p className="text-gray-500 text-xs">Precision</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500" style={{ width: `${perf.precision * 100}%` }} />
                    </div>
                    <span className="font-medium text-gray-900">{perf.precision}</span>
                  </div>
                </div>
                <div>
                  <p className="text-gray-500 text-xs">Recall</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: `${perf.recall * 100}%` }} />
                    </div>
                    <span className="font-medium text-gray-900">{perf.recall}</span>
                  </div>
                </div>
                <div>
                  <p className="text-gray-500 text-xs">F1-Score</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-purple-500" style={{ width: `${perf.f1_score * 100}%` }} />
                    </div>
                    <span className="font-medium text-gray-900">{perf.f1_score}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Similarities and Differences */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Similarities */}
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <ThumbsUp className="h-4 w-4 text-green-600" />
              <h3 className="font-semibold text-gray-900">Similarities</h3>
            </div>
          </div>
          <div className="p-5">
            <ul className="space-y-2">
              {data.similarities?.map((sim: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                  <span className="text-sm text-gray-700">{sim}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Differences */}
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <ThumbsDown className="h-4 w-4 text-amber-600" />
              <h3 className="font-semibold text-gray-900">Differences</h3>
            </div>
          </div>
          <div className="p-5">
            <ul className="space-y-2">
              {data.differences?.map((diff: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2">
                  <Info className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
                  <span className="text-sm text-gray-700">{diff}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Divergence Reasons */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Reasons for Divergence</h3>
          <p className="text-xs text-gray-500 mt-1">Factors contributing to disagreement between AI and human experts</p>
        </div>
        <div className="p-5 space-y-4">
          {data.divergence_reasons?.map((reason: any, idx: number) => (
            <div key={idx} className="p-5 rounded-xl bg-amber-50/50 border border-amber-100">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-white shadow-sm shrink-0">
                  <AlertTriangle className="h-4 w-4 text-amber-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-1">{reason.reason}</h4>
                  <p className="text-sm text-gray-600 mb-2">{reason.description}</p>
                  <div className="flex items-start gap-2">
                    <Lightbulb className="h-3 w-3 text-gray-400 mt-0.5 shrink-0" />
                    <p className="text-xs text-gray-500 italic">{reason.example}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Agreement Examples */}
      {data.agreement_examples && data.agreement_examples.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <h3 className="font-semibold text-gray-900">Agreement Examples</h3>
            </div>
          </div>
          <div className="p-5 space-y-3">
            {data.agreement_examples.map((example: any, idx: number) => (
              <div key={idx} className="p-4 rounded-lg bg-green-50/50 border border-green-100">
                <p className="text-sm text-gray-700 mb-2">"{example.text}"</p>
                <Badge className="bg-green-100 text-green-700 capitalize">{example.label}</Badge>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Disagreement Examples */}
      {data.disagreement_examples && data.disagreement_examples.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-600" />
              <h3 className="font-semibold text-gray-900">Disagreement Examples</h3>
            </div>
          </div>
          <div className="p-5 space-y-3">
            {data.disagreement_examples.map((example: any, idx: number) => (
              <div key={idx} className="p-4 rounded-lg bg-red-50/50 border border-red-100">
                <p className="text-sm text-gray-700 mb-2">"{example.text}"</p>
                <div className="flex gap-2">
                  <Badge className="bg-blue-100 text-blue-700 capitalize">Expert: {example.expert_label}</Badge>
                  <Badge className="bg-purple-100 text-purple-700 capitalize">AI: {example.ai_label}</Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
