import axiosInstance from '@/lib/axios';

// Build query string from filters
const buildQueryString = (filters: any) => {
  const params = new URLSearchParams();
  if (filters.semester && filters.semester !== 'all') params.append('semester', filters.semester);
  if (filters.academic_year && filters.academic_year !== 'all') params.append('academic_year', filters.academic_year);
  if (filters.instructor_id && filters.instructor_id !== 'all') params.append('instructor_id', filters.instructor_id);
  if (filters.course_id && filters.course_id !== 'all') params.append('course_id', filters.course_id);
  if (filters.department && filters.department !== 'all') params.append('department', filters.department);
  return params.toString();
};

export const revisionService = {
  /**
   * REVISION #1: Alignment Analysis
   * Compare Likert scores with text sentiment
   */
  async getAlignmentAnalysis(filters: any = {}) {
    const queryString = buildQueryString(filters);
    const url = `/revision/alignment-analysis/${queryString ? '?' + queryString : ''}`;
    const response = await axiosInstance.get(url);
    return response.data;
  },

  /**
   * REVISION #2: Thematic Analysis
   * Analyze negative feedback patterns
   */
  async getThematicAnalysis(filters: any = {}) {
    const queryString = buildQueryString(filters);
    const url = `/revision/thematic-analysis/${queryString ? '?' + queryString : ''}`;
    const response = await axiosInstance.get(url);
    return response.data;
  },

  /**
   * REVISION #3: Encoding Consistency
   * Inter-rater reliability and bias control
   */
  async getEncodingConsistency(filters: any = {}) {
    const queryString = buildQueryString(filters);
    const url = `/revision/encoding-consistency/${queryString ? '?' + queryString : ''}`;
    const response = await axiosInstance.get(url);
    return response.data;
  },

  /**
   * REVISION #4: Negative Course Summary
   * Star-based summary for low-rated courses
   */
  async getNegativeSummary(filters: any = {}) {
    const queryString = buildQueryString(filters);
    const url = `/revision/negative-summary/${queryString ? '?' + queryString : ''}`;
    const response = await axiosInstance.get(url);
    return response.data;
  },

  async getVisualizationSummary(filters: any = {}) {
    const queryString = buildQueryString(filters);
    const url = `/revision/visualization-summary/${queryString ? '?' + queryString : ''}`;
    const response = await axiosInstance.get(url);
    return response.data;
  },

  /**
   * REVISION #5: AI vs Expert Comparison
   * Compare ML predictions with human expert labels
   */
  async getAIExpertComparison(filters: any = {}) {
    const queryString = buildQueryString(filters);
    const url = `/revision/ai-expert-comparison/${queryString ? '?' + queryString : ''}`;
    const response = await axiosInstance.get(url);
    return response.data;
  },
};
