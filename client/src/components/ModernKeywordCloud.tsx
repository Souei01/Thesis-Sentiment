'use client';

import { useMemo, useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import axiosInstance from '@/lib/axios';

interface KeywordCloudProps {
  comments: any[];
}

export default function ModernKeywordCloud({ comments }: KeywordCloudProps) {
  const [positiveWords, setPositiveWords] = useState<Set<string>>(new Set());
  const [negativeWords, setNegativeWords] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  // Load sentiment words from backend
  useEffect(() => {
    const loadSentimentWords = async () => {
      try {
        const response = await axiosInstance.get('/feedback/sentiment-words/');
        const positive = new Set(response.data.positive || []);
        const negative = new Set(response.data.negative || []);
        
        console.log('Loaded sentiment words:', {
          positiveCount: positive.size,
          negativeCount: negative.size,
          hasBest: positive.has('best')
        });
        
        setPositiveWords(positive);
        setNegativeWords(negative);
      } catch (error) {
        console.error('Error loading sentiment words:', error);
        // Fallback to basic word lists if API fails
        setPositiveWords(new Set([
          'excellent', 'great', 'good', 'best', 'better', 'amazing', 'wonderful', 'fantastic',
          'helpful', 'clear', 'engaging', 'knowledgeable', 'patient', 'passionate', 'approachable',
        ]));
        setNegativeWords(new Set([
          'difficult', 'hard', 'poor', 'bad', 'worst', 'confusing', 'unclear', 'boring',
          'slow', 'fast', 'rushed', 'limited', 'lack', 'insufficient', 'inadequate',
        ]));
      } finally {
        setLoading(false);
      }
    };
    
    loadSentimentWords();
  }, []);

  // Process comments to extract words and their frequencies
  const keywords = useMemo(() => {
    if (loading) return [];
    
    try {
      if (!comments || !Array.isArray(comments) || comments.length === 0) {
        return [];
      }

      const allText = comments
        .map((feedback) => {
          if (!feedback) return '';
          const texts = [];
          if (feedback.suggested_changes) texts.push(feedback.suggested_changes);
          if (feedback.best_teaching_aspect) texts.push(feedback.best_teaching_aspect);
          if (feedback.least_teaching_aspect) texts.push(feedback.least_teaching_aspect);
          if (feedback.further_comments) texts.push(feedback.further_comments);
          return texts.join(' ');
        })
        .join(' ')
        .toLowerCase();

      if (!allText || allText.trim().length === 0) {
        return [];
      }

      const stopWords = new Set([
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'it', 'its',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'some', 'such', 'no', 'nor',
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
        'about', 'also', 'any', 'because', 'even', 'however', 'if', 'into',
        'like', 'made', 'make', 'much', 'over', 'through', 'up', 'using', 'want',
      ]);

      const wordFrequency: Record<string, number> = {};
      const wordMatches = allText.match(/\b[a-z]+\b/g) || [];

      wordMatches.forEach((word) => {
        if (word && word.length > 3 && !stopWords.has(word)) {
          wordFrequency[word] = (wordFrequency[word] || 0) + 1;
        }
      });

      const wordArray = Object.entries(wordFrequency)
        .map(([text, count]) => {
          let sentiment: 'positive' | 'negative' | 'neutral' = 'neutral';
          if (positiveWords.has(text)) {
            sentiment = 'positive';
          } else if (negativeWords.has(text)) {
            sentiment = 'negative';
          }
          return { text, count, sentiment };
        })
        .sort((a, b) => b.count - a.count)
        .slice(0, 30);
      
      return wordArray;
    } catch (error) {
      console.error('Error processing keywords:', error);
      return [];
    }
  }, [comments, positiveWords, negativeWords, loading]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[300px] text-gray-500">
        <div className="text-center">
          <p className="text-lg font-medium mb-2">Loading sentiment dictionary...</p>
        </div>
      </div>
    );
  }

  if (!keywords || keywords.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-gray-500">
        <div className="text-center">
          <p className="text-lg font-medium mb-2">No keywords to display</p>
          <p className="text-sm">Student comments are too short or contain only common words</p>
        </div>
      </div>
    );
  }

  const maxCount = Math.max(...keywords.map(k => k.count));

  const getSentimentColor = (sentiment: string) => {
    if (sentiment === 'positive') return '#10b981'; // green-500
    if (sentiment === 'negative') return '#ef4444'; // red-500
    return '#6b7280'; // gray-500 for neutral
  };

  const getFontSize = (count: number) => {
    const ratio = count / maxCount;
    // Font size range from 14px to 56px based on frequency
    return 14 + (ratio * 42);
  };

  const getFontWeight = (count: number) => {
    const ratio = count / maxCount;
    if (ratio > 0.7) return 700; // bold
    if (ratio > 0.4) return 600; // semibold
    return 500; // medium
  };

  const getSentimentIcon = (sentiment: string) => {
    if (sentiment === 'positive') return <TrendingUp className="h-3 w-3" />;
    if (sentiment === 'negative') return <TrendingDown className="h-3 w-3" />;
    return <Minus className="h-3 w-3" />;
  };

  // Group by sentiment for organized display
  const groupedKeywords = {
    positive: keywords.filter(k => k.sentiment === 'positive'),
    negative: keywords.filter(k => k.sentiment === 'negative'),
    neutral: keywords.filter(k => k.sentiment === 'neutral'),
  };

  return (
    <div className="space-y-6">
      {/* Word Cloud Style Display */}
      <div className="flex flex-wrap items-center justify-center gap-3 p-6 bg-gradient-to-br from-gray-50 to-white rounded-lg min-h-[300px] max-h-[400px] overflow-auto">
        {keywords.map((keyword, index) => (
          <span
            key={`${keyword.text}-${index}`}
            className="inline-block px-2 py-1 hover:opacity-70 transition-all duration-200 cursor-default"
            style={{
              fontSize: `${getFontSize(keyword.count)}px`,
              color: getSentimentColor(keyword.sentiment),
              fontWeight: getFontWeight(keyword.count),
            }}
            title={`"${keyword.text}" appears ${keyword.count} time${keyword.count > 1 ? 's' : ''} (${keyword.sentiment})`}
          >
            {keyword.text}
          </span>
        ))}
      </div>

      {/* Grouped by Sentiment */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Positive Keywords */}
        {groupedKeywords.positive.length > 0 && (
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="text-sm font-semibold text-green-800 mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Positive ({groupedKeywords.positive.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {groupedKeywords.positive.map((keyword, index) => (
                <Badge
                  key={`pos-${keyword.text}-${index}`}
                  className="bg-white text-green-700 border-green-300 hover:bg-green-100"
                  variant="outline"
                >
                  {keyword.text} ({keyword.count})
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Neutral Keywords */}
        {groupedKeywords.neutral.length > 0 && (
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="text-sm font-semibold text-blue-800 mb-3 flex items-center gap-2">
              <Minus className="h-4 w-4" />
              Neutral ({groupedKeywords.neutral.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {groupedKeywords.neutral.map((keyword, index) => (
                <Badge
                  key={`neu-${keyword.text}-${index}`}
                  className="bg-white text-blue-700 border-blue-300 hover:bg-blue-100"
                  variant="outline"
                >
                  {keyword.text} ({keyword.count})
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Negative Keywords */}
        {groupedKeywords.negative.length > 0 && (
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <h4 className="text-sm font-semibold text-red-800 mb-3 flex items-center gap-2">
              <TrendingDown className="h-4 w-4" />
              Negative ({groupedKeywords.negative.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {groupedKeywords.negative.map((keyword, index) => (
                <Badge
                  key={`neg-${keyword.text}-${index}`}
                  className="bg-white text-red-700 border-red-300 hover:bg-red-100"
                  variant="outline"
                >
                  {keyword.text} ({keyword.count})
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
