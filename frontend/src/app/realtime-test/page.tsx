// True WebSocket Real-time Test using Supabase JavaScript Client
// This uses Supabase's real-time subscriptions directly

'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import type { Question } from '@/types';

// Supabase configuration
const supabaseUrl = 'https://eysipjwmfgtvmjqgfojn.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV5c2lwandtZmd0dm1qcWdmb2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwNDc3NzQsImV4cCI6MjA1MjYyMzc3NH0.1r8vNJIlEG5dTTJGf_LCuA_vQOJILnK8ZM5HryUMUGM';

export default function RealTimeEventPage() {
  const [eventId] = useState('daf3690d-784e-49bb-8ec0-547cc4cc2d8b');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'error'>('connecting');

  useEffect(() => {
    const supabase = createClient(supabaseUrl, supabaseAnonKey);

    const setupRealTime = async () => {
      try {
        console.log('🔄 Setting up Supabase real-time connection...');
        
        // Initial data fetch
        console.log('📊 Fetching initial questions...');
        const { data: initialData, error: fetchError } = await supabase
          .from('api_question')
          .select(`
            *,
            author:author_id(id, name, email, role)
          `)
          .eq('event_id', eventId)
          .order('created_at', { ascending: false });

        if (fetchError) {
          console.error('❌ Initial fetch error:', fetchError);
          setError(`Failed to fetch questions: ${fetchError.message}`);
          setConnectionStatus('error');
          return;
        }

        console.log(`✅ Fetched ${initialData?.length || 0} initial questions`);
        
        // Transform data
        if (initialData) {
          const transformedQuestions = initialData.map(transformQuestion);
          setQuestions(transformedQuestions);
        }

        setConnectionStatus('connected');
        setError(null);

        // Set up real-time subscription
        console.log('🔔 Setting up real-time subscription...');
        const channel = supabase
          .channel('questions-realtime')
          .on(
            'postgres_changes',
            {
              event: '*',
              schema: 'public',
              table: 'api_question',
              filter: `event_id=eq.${eventId}`,
            },
            (payload) => {
              console.log('🔄 Real-time update received:', payload);
              handleRealTimeChange(payload);
            }
          )
          .subscribe((status) => {
            console.log('📡 Subscription status:', status);
            if (status === 'SUBSCRIBED') {
              console.log('✅ Real-time subscription active!');
            }
          });

        return () => {
          console.log('🔌 Cleaning up subscription...');
          supabase.removeChannel(channel);
        };

      } catch (err: any) {
        console.error('❌ Setup error:', err);
        setError(`Setup failed: ${err.message}`);
        setConnectionStatus('error');
      } finally {
        setLoading(false);
      }
    };

    const cleanup = setupRealTime();
    
    return () => {
      cleanup.then(cleanupFn => cleanupFn?.());
    };
  }, [eventId]);

  // Transform Supabase data to frontend format
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
      has_user_upvoted: false,
      is_answered: dbQuestion.is_answered || false,
      is_starred: dbQuestion.is_starred || false,
      is_staged: dbQuestion.is_staged || false,
      presenter_notes: dbQuestion.presenter_notes || '',
      tags: [],
      created_at: dbQuestion.created_at,
      updated_at: dbQuestion.updated_at || dbQuestion.created_at
    };
  };

  // Handle real-time changes
  const handleRealTimeChange = (payload: any) => {
    const { eventType, new: newRecord, old: oldRecord } = payload;

    switch (eventType) {
      case 'INSERT':
        console.log('➕ New question added:', newRecord);
        setQuestions(prev => [transformQuestion(newRecord), ...prev]);
        break;

      case 'UPDATE':
        console.log('✏️ Question updated:', newRecord);
        setQuestions(prev =>
          prev.map(q => q.id === newRecord.id ? transformQuestion(newRecord) : q)
        );
        break;

      case 'DELETE':
        console.log('🗑️ Question deleted:', oldRecord);
        setQuestions(prev => prev.filter(q => q.id !== oldRecord.id));
        break;
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-medium text-blue-900 mb-2">🔄 Connecting to Supabase...</h2>
          <p className="text-blue-700">Setting up WebSocket connection...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-lg font-medium text-red-900 mb-2">❌ Connection Error</h2>
          <p className="text-red-700">{error}</p>
          <p className="text-red-600 text-sm mt-2">
            Check browser console for detailed error messages
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          ⚡ True WebSocket Real-time Questions
        </h1>
        <div className={`border rounded-lg p-4 ${
          connectionStatus === 'connected' 
            ? 'bg-green-50 border-green-200' 
            : connectionStatus === 'error' 
            ? 'bg-red-50 border-red-200' 
            : 'bg-yellow-50 border-yellow-200'
        }`}>
          <h2 className={`text-lg font-medium mb-2 ${
            connectionStatus === 'connected' ? 'text-green-900' : 
            connectionStatus === 'error' ? 'text-red-900' : 'text-yellow-900'
          }`}>
            {connectionStatus === 'connected' && '✅ WebSocket Connected!'}
            {connectionStatus === 'error' && '❌ Connection Failed'}
            {connectionStatus === 'connecting' && '🔄 Connecting...'}
          </h2>
          <p className={connectionStatus === 'connected' ? 'text-green-700' : 
                        connectionStatus === 'error' ? 'text-red-700' : 'text-yellow-700'}>
            {connectionStatus === 'connected' && 'Questions will appear instantly when added to database!'}
            {connectionStatus === 'error' && 'Check RLS policies and network connection'}
            {connectionStatus === 'connecting' && 'Establishing real-time connection...'}
          </p>
        </div>
      </div>

      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">
          Questions ({questions.length})
        </h2>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 
            connectionStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
          }`}></div>
          <span className="text-sm text-gray-600">
            {connectionStatus === 'connected' && 'Live WebSocket'}
            {connectionStatus === 'error' && 'Disconnected'}
            {connectionStatus === 'connecting' && 'Connecting...'}
          </span>
        </div>
      </div>

      {questions.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">No questions found for this event.</p>
          <p className="text-gray-500 text-sm mt-2">
            Add questions via Django admin to see them appear instantly!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {questions.map((question) => (
            <div key={question.id} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    {question.author.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{question.author.name}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(question.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {question.is_starred && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      ⭐ Starred
                    </span>
                  )}
                  {question.is_staged && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      🎭 On Stage
                    </span>
                  )}
                  {question.is_answered && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✅ Answered
                    </span>
                  )}
                </div>
              </div>
              
              <p className="text-gray-800 text-base leading-relaxed mb-4">
                {question.text}
              </p>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <button className="flex items-center space-x-1 text-gray-600 hover:text-blue-600 transition-colors">
                    <span className="text-sm">👍</span>
                    <span className="text-sm font-medium">{question.upvotes}</span>
                  </button>
                </div>
                <div className="text-xs text-gray-400">
                  ID: {question.id.slice(0, 8)}...
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-lg font-medium text-blue-900 mb-2">🧪 Test Real-time Updates</h3>
        <p className="text-blue-700 text-sm">
          To see instant WebSocket updates:
          <br />
          1. Open this page in another browser window
          <br />
          2. Add a question via Django admin or run our test script
          <br />
          3. Watch it appear instantly in both windows!
          <br />
          <br />
          <strong>Check browser console (F12) for real-time connection logs</strong>
        </p>
      </div>
    </div>
  );
}
