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
  const [activeTab, setActiveTab] = useState<'alignment' | 'thematic' | 'negative'>('alignment');
  const [loading, setLoading] = useState(true);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>({});
  const [ratingExtremes, setRatingExtremes] = useState<any>(null);

  const tabs = [
    { id: 'alignment', label: 'Alignment Analysis', icon: Target, desc: 'Likert vs Sentiment' },
    { id: 'thematic', label: 'Thematic Patterns', icon: Lightbulb, desc: 'Comment Themes' },
    { id: 'negative', label: 'Negative Summary', icon: Star, desc: 'Low-Rating Severity' },
  ];

  useEffect(() => {
    loadData();
  }, [activeTab, JSON.stringify(filters)]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      let result;
      switch (activeTab) {
        case 'alignment':
          result = await revisionService.getAlignmentAnalysis(filters);
          break;
        case 'thematic':
          result = await revisionService.getThematicAnalysis(filters);
          break;

        case 'negative':
          result = await revisionService.getNegativeSummary(filters);
          break;
      }
      const [tabData, extremesData] = await Promise.all([
        Promise.resolve(result),
        revisionService.getCourseRatingExtremes(filters),
      ]);
      setData(tabData);
      setRatingExtremes(extremesData);
    } catch (error: any) {
      console.error('Error loading revision data:', error);
      if (!error?.response) {
        setError('Cannot connect to the backend API. Start the Django server at http://127.0.0.1:8000 and try again.');
      } else {
        setError(error?.response?.data?.error || 'Failed to load revision data.');
      }
    } finally {
      setLoading(false);
    }
  };

  const exportPdfReport = async () => {
    setExportingPdf(true);
    try {
      const [{ default: jsPDF }, autoTableModule] = await Promise.all([
        import('jspdf'),
        import('jspdf-autotable'),
      ]);

      const autoTable = autoTableModule.default;
      const doc = new jsPDF({ orientation: 'landscape', unit: 'pt', format: 'a4' });

      const tabLabel = tabs.find((tab) => tab.id === activeTab)?.label || 'Analysis';
      const generatedAt = new Date().toLocaleString();

      doc.setFontSize(16);
      doc.text('Feedback Analysis Report', 40, 36);
      doc.setFontSize(11);
      doc.text(`Section: ${tabLabel}`, 40, 56);
      doc.text(`Generated: ${generatedAt}`, 40, 72);

      const highest = ratingExtremes?.highest_rated_course;
      const lowest = ratingExtremes?.lowest_rated_course;
      const summaryRows = [
        ['Courses Analyzed', String(ratingExtremes?.courses_analyzed ?? 0)],
        [
          'Highest Rated Course',
          highest
            ? `${highest.course_code} (${highest.avg_rating}/5, ${highest.response_count} responses)`
            : 'N/A',
        ],
        [
          'Lowest Rated Course',
          lowest
            ? `${lowest.course_code} (${lowest.avg_rating}/5, ${lowest.response_count} responses)`
            : 'N/A',
        ],
      ];

      autoTable(doc, {
        startY: 88,
        head: [['Metric', 'Value']],
        body: summaryRows,
        theme: 'grid',
        styles: { fontSize: 9 },
        headStyles: { fillColor: [142, 27, 27] },
        columnStyles: { 0: { cellWidth: 180 }, 1: { cellWidth: 520 } },
      });

      let detailRows: string[][] = [];
      let detailHead = [['Field', 'Value 1', 'Value 2', 'Value 3']];

      if (activeTab === 'alignment') {
        const ratings: Array<[string, any]> = Object.entries(data?.alignment_by_rating || {});
        detailHead = [['Rating Bucket', 'Responses', 'Aligned', 'Alignment %']];
        detailRows = ratings.map(([bucket, value]: [string, any]) => {
          const alignedPct = value?.count ? ((value.aligned / value.count) * 100).toFixed(1) : '0.0';
          return [bucket.replace('_', ' '), String(value?.count ?? 0), String(value?.aligned ?? 0), `${alignedPct}%`];
        });
      } else if (activeTab === 'thematic') {
        detailHead = [['Course', 'Comments', 'Dominant Theme', 'Theme Coverage %']];
        detailRows = (data?.course_breakdown || []).slice(0, 12).map((course: any) => [
          String(course.course_code || ''),
          String(course.count || 0),
          String(course.dominant_theme || 'n/a').replace('_', ' '),
          `${course.theme_coverage_pct ?? 0}%`,
        ]);
      } else {
        detailHead = [['Course', 'Avg Rating', 'Negative Count', 'Dominant Emotion']];
        detailRows = (data?.course_details || []).slice(0, 12).map((course: any) => [
          String(course.course_code || ''),
          String(course.avg_rating ?? 0),
          String(course.total_negative ?? 0),
          String(course.dominant_emotion || 'n/a'),
        ]);
      }

      autoTable(doc, {
        startY: 200,
        head: detailHead,
        body: detailRows.length ? detailRows : [['No data available for current filters', '', '', '']],
        theme: 'striped',
        styles: { fontSize: 9 },
        headStyles: { fillColor: [30, 64, 175] },
      });

      const filename = `feedback-analysis-${activeTab}-report.pdf`;
      doc.save(filename);
    } catch (err) {
      console.error('Failed to export PDF report:', err);
      setError('Failed to export PDF report. Please try again.');
    } finally {
      setExportingPdf(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-5 bg-gradient-to-r from-[#8E1B1B] to-rose-700">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Feedback Analysis</h1>
              <p className="text-rose-100 text-sm mt-1">Course feedback patterns, sentiment alignment, and low-rating risk signals</p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                onClick={exportPdfReport}
                variant="outline"
                size="sm"
                disabled={loading || exportingPdf}
                className="bg-white/10 border-white/20 text-white hover:bg-white/20 disabled:opacity-60"
              >
                <Download className="h-4 w-4 mr-2" />
                {exportingPdf ? 'Exporting...' : 'Export PDF'}
              </Button>
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
      ) : error ? (
        <div className="bg-white rounded-2xl border border-red-200/70 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-red-100 bg-red-50/70">
            <h3 className="font-semibold text-red-800">Analysis Data Unavailable</h3>
            <p className="text-xs text-red-600 mt-1">Connection or API issue detected.</p>
          </div>
          <div className="p-5">
            <p className="text-sm text-gray-700">{error}</p>
            <p className="text-xs text-gray-500 mt-3">If this is local development, ensure both frontend and backend servers are running.</p>
          </div>
        </div>
      ) : (
        <>
          {ratingExtremes && (ratingExtremes.highest_rated_course || ratingExtremes.lowest_rated_course) && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white rounded-xl border border-emerald-200/70 p-5">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-emerald-50">
                      <TrendingUp className="h-5 w-5 text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Highest Rated Course</p>
                      <p className="text-lg font-bold text-emerald-700">
                        {ratingExtremes.highest_rated_course
                          ? `${ratingExtremes.highest_rated_course.course_code} (${ratingExtremes.highest_rated_course.avg_rating}/5)`
                          : 'N/A'}
                      </p>
                      {ratingExtremes.highest_rated_course && (
                        <p className="text-xs text-gray-500">
                          {ratingExtremes.highest_rated_course.course_name} • {ratingExtremes.highest_rated_course.response_count} responses
                        </p>
                      )}
                    </div>
                  </div>
                  {ratingExtremes.highest_rated_course?.reason && (
                    <p className="text-xs text-emerald-700 mt-3">Reason: {ratingExtremes.highest_rated_course.reason}</p>
                  )}
                  {ratingExtremes.highest_rated_course?.sample_feedback && (
                    <p className="text-xs text-gray-600 mt-1 italic">"{ratingExtremes.highest_rated_course.sample_feedback}"</p>
                  )}
                </div>

                <div className="bg-white rounded-xl border border-red-200/70 p-5">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-red-50">
                      <TrendingDown className="h-5 w-5 text-red-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Lowest Rated Course</p>
                      <p className="text-lg font-bold text-red-700">
                        {ratingExtremes.lowest_rated_course
                          ? `${ratingExtremes.lowest_rated_course.course_code} (${ratingExtremes.lowest_rated_course.avg_rating}/5)`
                          : 'N/A'}
                      </p>
                      {ratingExtremes.lowest_rated_course && (
                        <p className="text-xs text-gray-500">
                          {ratingExtremes.lowest_rated_course.course_name} • {ratingExtremes.lowest_rated_course.response_count} responses
                        </p>
                      )}
                    </div>
                  </div>
                  {ratingExtremes.lowest_rated_course?.reason && (
                    <p className="text-xs text-red-700 mt-3">Reason: {ratingExtremes.lowest_rated_course.reason}</p>
                  )}
                  {ratingExtremes.lowest_rated_course?.sample_feedback && (
                    <p className="text-xs text-gray-600 mt-1 italic">"{ratingExtremes.lowest_rated_course.sample_feedback}"</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                <TopCoursesTable
                  title="Top 10 Highest Rated Courses"
                  titleClassName="text-emerald-700"
                  rows={ratingExtremes.top_10_highest_courses || []}
                  accentClassName="bg-emerald-50 border-emerald-100"
                />
                <TopCoursesTable
                  title="Top 10 Lowest Rated Courses"
                  titleClassName="text-red-700"
                  rows={ratingExtremes.top_10_lowest_courses || []}
                  accentClassName="bg-red-50 border-red-100"
                />
              </div>
            </div>
          )}

          {activeTab === 'alignment' && <AlignmentAnalysisView data={data} />}
          {activeTab === 'thematic' && <ThematicAnalysisView data={data} />}
          {activeTab === 'negative' && <NegativeSummaryView data={data} />}
        </>
      )}
    </div>
  );
}

function TopCoursesTable({
  title,
  titleClassName,
  rows,
  accentClassName,
}: {
  title: string;
  titleClassName: string;
  rows: any[];
  accentClassName: string;
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200/70 overflow-hidden">
      <div className={cn('px-4 py-3 border-b', accentClassName)}>
        <h3 className={cn('text-sm font-semibold', titleClassName)}>{title}</h3>
      </div>
      <div className="p-4 space-y-3 max-h-[440px] overflow-auto">
        {rows.length === 0 ? (
          <p className="text-sm text-gray-500">No course data available.</p>
        ) : (
          rows.map((course: any, idx: number) => (
            <div key={`${course.course_code}-${idx}`} className="rounded-lg border border-gray-100 p-3 bg-gray-50/60">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs text-gray-500">#{idx + 1}</p>
                  <p className="text-sm font-semibold text-gray-900">{course.course_code}</p>
                  <p className="text-xs text-gray-600">{course.course_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-gray-900">{course.avg_rating}/5</p>
                  <p className="text-xs text-gray-500">{course.response_count} responses</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
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

  const activeThemeCount = data.active_theme_count ?? Object.values(data.overall_themes || {}).filter((count: any) => count > 0).length;

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
            <div className="p-2 rounded-lg bg-amber-50">
              <FileText className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Comment Records Analyzed</p>
              <p className="text-2xl font-bold text-gray-900">{data.total_feedback_analyzed}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200/60 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-50">
              <BarChart3 className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Themed Comments</p>
              <p className="text-2xl font-bold text-gray-900">{data.themed_feedback_count}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200/60 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-violet-50">
              <Lightbulb className="h-5 w-5 text-violet-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Active Themes</p>
              <p className="text-2xl font-bold text-gray-900">
                {activeThemeCount}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-amber-50 to-white rounded-2xl border border-amber-100 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-white shadow-sm">
            <Lightbulb className="h-6 w-6 text-amber-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-2">What This Tab Shows</h3>
            <p className="text-sm text-gray-600">
              This view scans comment text for recurring issue themes across all submitted feedback. It is separate from the Negative Summary tab, which only reports low-rating volume and severity.
            </p>
          </div>
        </div>
      </div>

      {/* Overall Themes */}
      <div className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900">Overall Theme Distribution</h3>
          <p className="text-xs text-gray-500 mt-1">Counts of comment records that matched each theme keyword set.</p>
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
          <p className="text-xs text-gray-500 mt-1">Theme signals by course across submitted comment text</p>
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
                  <Badge variant="outline" className="mb-1">{course.count} comment records</Badge>
                  <div className="flex items-center gap-1">
                    <Lightbulb className="h-3 w-3 text-amber-500" />
                    <span className="text-sm font-bold text-gray-900">{course.theme_coverage_pct}% coverage</span>
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
                <p className="text-xs text-gray-500">{course.theme_match_count} of {course.count} comment records matched at least one theme.</p>
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

