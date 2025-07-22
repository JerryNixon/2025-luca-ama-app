// Real-time Questions Hook
// This hook automatically updates when questions change in the database

import { useState, useEffect } from 'react';
import { supabase, TABLES } from '@/lib/supabase';
import type { Question } from '@/types';

export function useRealTimeQuestions(eventId: string) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Initial fetch of questions
    fetchQuestions();

    // Set up real-time subscription
    const subscription = supabase
      .channel('questions-channel')
      .on(
        'postgres_changes',
        {
          event: '*', // Listen to all changes (INSERT, UPDATE, DELETE)
          schema: 'public',
          table: TABLES.QUESTIONS,
          filter: `event_id=eq.${eventId}` // Only questions for this event
        },
        (payload) => {
          console.log('🔄 Real-time update received:', payload);
          handleRealTimeChange(payload);
        }
      )
      .subscribe();

    // Cleanup subscription on unmount
    return () => {
      console.log('🔌 Unsubscribing from real-time updates');
      supabase.removeChannel(subscription);
    };
  }, [eventId]);

  // Fetch initial questions from database
  const fetchQuestions = async () => {
    try {
      setLoading(true);
      
      // Query questions for this event with user information
      const { data, error } = await supabase
        .from(TABLES.QUESTIONS)
        .select(`
          *,
          author:author_id(id, name, email, role)
        `)
        .eq('event_id', eventId)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('❌ Error fetching questions:', error);
        setError(error.message);
        return;
      }

      console.log(`✅ Loaded ${data?.length || 0} questions for event ${eventId}`);
      
      // Transform data to match our frontend types
      const transformedQuestions = data?.map(transformQuestion) || [];
      setQuestions(transformedQuestions);
      
    } catch (err) {
      console.error('❌ Unexpected error:', err);
      setError('Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  // Handle real-time database changes
  const handleRealTimeChange = (payload: any) => {
    const { eventType, new: newRecord, old: oldRecord } = payload;

    switch (eventType) {
      case 'INSERT':
        console.log('➕ New question added:', newRecord);
        // Add new question to the list
        setQuestions(prev => [transformQuestion(newRecord), ...prev]);
        break;

      case 'UPDATE':
        console.log('✏️ Question updated:', newRecord);
        // Update existing question
        setQuestions(prev => 
          prev.map(q => q.id === newRecord.id ? transformQuestion(newRecord) : q)
        );
        break;

      case 'DELETE':
        console.log('🗑️ Question deleted:', oldRecord);
        // Remove question from list
        setQuestions(prev => prev.filter(q => q.id !== oldRecord.id));
        break;
    }
  };

  // Transform database record to frontend Question type
  const transformQuestion = (dbQuestion: any): Question => {
    return {
      id: dbQuestion.id,
      event: dbQuestion.event_id,
      text: dbQuestion.text,
      author: dbQuestion.author ? {
        id: dbQuestion.author.id,
        name: dbQuestion.author.name,
        email: dbQuestion.author.email,
        role: dbQuestion.author.role
      } : {
        id: dbQuestion.author_id,
        name: 'Unknown User',
        email: '',
        role: 'user'
      },
      is_anonymous: dbQuestion.is_anonymous || false,
      upvotes: dbQuestion.upvotes || 0,
      has_user_upvoted: false, // TODO: Implement user-specific upvote checking
      is_answered: dbQuestion.is_answered || false,
      is_starred: dbQuestion.is_starred || false,
      is_staged: dbQuestion.is_staged || false,
      presenter_notes: dbQuestion.presenter_notes || '',
      tags: [], // TODO: Implement tags system
      created_at: dbQuestion.created_at,
      updated_at: dbQuestion.updated_at || dbQuestion.created_at
    };
  };

  return {
    questions,
    loading,
    error,
    refetch: fetchQuestions
  };
}
