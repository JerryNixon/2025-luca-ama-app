// Minimal AI Similarity Detection Integration
// This component can be dropped into any form to add AI similarity detection

import React, { useState, useEffect, useCallback } from 'react';
import { SimilarQuestionsResponse } from '../../types';
import { questionService } from '../../services/questionService';

interface AISimilarityDetectorProps {
  eventId: string;
  questionText: string;
  onSimilarFound: (data: SimilarQuestionsResponse) => void;
}

export default function AISimilarityDetector({ 
  eventId, 
  questionText, 
  onSimilarFound 
}: AISimilarityDetectorProps) {
  const [loading, setLoading] = useState(false);

  // Debounced similarity check
  useEffect(() => {
    console.log('🚀 AISimilarityDetector: questionText changed:', questionText);
    
    if (!questionText || questionText.trim().length < 10) {
      console.log('❌ Text too short, skipping AI analysis');
      return;
    }

    const timeoutId = setTimeout(async () => {
      console.log('🤖 Starting AI similarity analysis...');
      setLoading(true);
      
      try {
        console.log('📡 Calling API with eventId:', eventId);
        const response = await questionService.findSimilarQuestions(eventId, questionText.trim());
        console.log('✅ AI Response:', response);
        onSimilarFound(response);
      } catch (error) {
        console.error('❌ AI Analysis failed:', error);
      } finally {
        setLoading(false);
        console.log('🏁 AI Analysis complete');
      }
    }, 1000);

    return () => {
      console.log('🧹 Cleaning up AI analysis timeout');
      clearTimeout(timeoutId);
    };
  }, [eventId, questionText, onSimilarFound]);

  return (
    <div style={{
      backgroundColor: loading ? 'yellow' : 'lightblue',
      padding: '10px',
      margin: '5px 0',
      border: '2px solid blue',
      borderRadius: '5px'
    }}>
      🤖 AI Detector: {loading ? '🔄 Analyzing...' : '💤 Waiting'}
      <br />
      <small>Text length: {questionText?.length || 0}</small>
    </div>
  );
}
