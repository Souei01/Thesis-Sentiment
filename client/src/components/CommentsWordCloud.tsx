'use client';

import { useMemo } from 'react';

interface WordCloudProps {
  comments: any[];
}

export default function CommentsWordCloud({ comments }: WordCloudProps) {
  // Define sentiment word lists
  const positiveWords = new Set([
    'excellent', 'great', 'good', 'best', 'better', 'amazing', 'wonderful', 'fantastic',
    'helpful', 'clear', 'engaging', 'knowledgeable', 'patient', 'passionate', 'approachable',
    'effective', 'appreciate', 'enjoyed', 'love', 'valuable', 'useful', 'relevant',
    'interactive', 'interesting', 'motivating', 'enthusiastic', 'inspiring', 'supportive',
    'organized', 'thorough', 'comprehensive', 'well', 'understanding', 'positive',
    'improvement', 'success', 'quality', 'strength', 'benefits', 'recommend', 'insightful',
  ]);

  const negativeWords = new Set([
    'difficult', 'hard', 'poor', 'bad', 'worst', 'confusing', 'unclear', 'boring',
    'slow', 'fast', 'rushed', 'limited', 'lack', 'insufficient', 'inadequate',
    'problems', 'issues', 'concerns', 'disappointing', 'frustrating', 'stress',
    'difficult', 'challenging', 'struggle', 'weak', 'needs', 'should', 'must',
    'without', 'never', 'rarely', 'sometimes', 'less', 'missing', 'absent',
  ]);

  // Process comments to extract words and their frequencies
  const words = useMemo(() => {
    try {
      // Check if comments is valid
      if (!comments || !Array.isArray(comments) || comments.length === 0) {
        return [];
      }

      // Combine all text from comments
      const allText = comments
        .map((feedback) => {
          if (!feedback) return '';
          const texts = [];
          if (feedback.suggested_changes && typeof feedback.suggested_changes === 'string') {
            texts.push(feedback.suggested_changes);
          }
          if (feedback.best_teaching_aspect && typeof feedback.best_teaching_aspect === 'string') {
            texts.push(feedback.best_teaching_aspect);
          }
          if (feedback.least_teaching_aspect && typeof feedback.least_teaching_aspect === 'string') {
            texts.push(feedback.least_teaching_aspect);
          }
          if (feedback.further_comments && typeof feedback.further_comments === 'string') {
            texts.push(feedback.further_comments);
          }
          return texts.join(' ');
        })
        .join(' ')
        .toLowerCase();

      // If no text, return empty array
      if (!allText || allText.trim().length === 0) {
        return [];
      }

      // Common stop words to filter out
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
        'none', 'would',
      ]);

      // Extract words and count frequencies
      const wordFrequency: Record<string, number> = {};
      const wordMatches = allText.match(/\b[a-z]+\b/g) || [];

      wordMatches.forEach((word) => {
        if (word && word.length > 3 && !stopWords.has(word)) {
          wordFrequency[word] = (wordFrequency[word] || 0) + 1;
        }
      });

      // Convert to word cloud format and sort by frequency
      const wordArray = Object.entries(wordFrequency)
        .map(([text, value]) => {
          // Determine sentiment
          let sentiment: 'positive' | 'negative' | 'neutral' = 'neutral';
          if (positiveWords.has(text)) {
            sentiment = 'positive';
          } else if (negativeWords.has(text)) {
            sentiment = 'negative';
          }
          return { text, value, sentiment };
        })
        .sort((a, b) => b.value - a.value)
        .slice(0, 50); // Top 50 words
      
      return wordArray;
    } catch (error) {
      console.error('Error processing comments for word cloud:', error);
      return [];
    }
  }, [comments, positiveWords, negativeWords]);

  // Early return if no words
  if (!words || words.length === 0) {
    return (
      <div className="flex items-center justify-center h-[400px] text-gray-500">
        <div className="text-center">
          <p className="text-lg font-medium mb-2">No meaningful words to display</p>
          <p className="text-sm">Student comments are too short or contain only common words</p>
        </div>
      </div>
    );
  }

  // Calculate font sizes based on frequency
  const maxFreq = Math.max(...words.map(w => w.value));
  const minFreq = Math.min(...words.map(w => w.value));
  
  const getFontSize = (value: number) => {
    const ratio = (value - minFreq) / (maxFreq - minFreq || 1);
    return 14 + ratio * 46; // Range from 14px to 60px
  };

  const getColor = (word: { text: string; value: number; sentiment: string }) => {
    // Color based on sentiment first, then intensity by frequency
    const maxFreq = Math.max(...words.map(w => w.value));
    const intensity = word.value / maxFreq;
    
    if (word.sentiment === 'positive') {
      // Green shades for positive words
      if (intensity > 0.7) return '#16a34a'; // dark green
      if (intensity > 0.4) return '#22c55e'; // medium green
      return '#4ade80'; // light green
    } else if (word.sentiment === 'negative') {
      // Red shades for negative words
      if (intensity > 0.7) return '#dc2626'; // dark red
      if (intensity > 0.4) return '#ef4444'; // medium red
      return '#f87171'; // light red
    } else {
      // Gray/blue shades for neutral words
      if (intensity > 0.7) return '#1e40af'; // dark blue
      if (intensity > 0.4) return '#3b82f6'; // medium blue
      return '#6b7280'; // gray
    }
  };

  return (
    <div className="w-full h-[500px] overflow-auto">
      <div className="flex flex-wrap items-center justify-center gap-4 p-8">
        {words.map((word, index) => (
          <span
            key={`${word.text}-${index}`}
            className="inline-block px-2 py-1 hover:opacity-70 transition-opacity cursor-default"
            style={{
              fontSize: `${getFontSize(word.value)}px`,
              color: getColor(word),
              fontWeight: word.value > maxFreq * 0.5 ? 'bold' : 'normal',
            }}
            title={`"${word.text}" appears ${word.value} time${word.value > 1 ? 's' : ''}`}
          >
            {word.text}
          </span>
        ))}
      </div>
    </div>
  );
}
