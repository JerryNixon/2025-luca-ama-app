'use client';

// Isolated Supabase REST API Test Component
// This component tests Supabase's auto-generated REST API without interfering with your Django backend

import { useState, useEffect } from 'react';
import { supabase, Question, createTestQuestion, TABLES } from '../../../lib/supabase';

interface TestResults {
  fetchAll: any[];
  insertResult: any;
  errors: string[];
  timings: {
    fetchAllMs: number;
    insertMs: number;
  };
}

export default function SupabaseTest() {
  const [testResults, setTestResults] = useState<TestResults>({
    fetchAll: [],
    insertResult: null,
    errors: [],
    timings: { fetchAllMs: 0, insertMs: 0 }
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [testQuestionText, setTestQuestionText] = useState('');

  // Function 1: Fetch all questions from Supabase REST API
  const testFetchAllQuestions = async () => {
    console.log('🔍 Testing: Fetch all questions from Supabase...');
    const startTime = performance.now();
    
    try {
      const { data, error } = await supabase
        .from(TABLES.QUESTIONS)
        .select('*')
        .order('created_at', { ascending: false });

      const endTime = performance.now();
      const duration = endTime - startTime;

      if (error) {
        console.error('❌ Fetch error:', error);
        return { data: [], error: error.message, timing: duration };
      }

      console.log('✅ Fetch success:', data?.length, 'questions found');
      console.log('⏱️ Fetch timing:', duration.toFixed(2), 'ms');
      return { data: data || [], error: null, timing: duration };
      
    } catch (err) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.error('❌ Fetch exception:', err);
      return { data: [], error: String(err), timing: duration };
    }
  };

  // Function 2: Insert a new question via Supabase REST API
  const testInsertQuestion = async (questionText: string) => {
    console.log('➕ Testing: Insert new question to Supabase...');
    const startTime = performance.now();
    
    try {
      const questionData = createTestQuestion(questionText);
      
      const { data, error } = await supabase
        .from(TABLES.QUESTIONS)
        .insert([questionData])
        .select(); // Return the inserted data

      const endTime = performance.now();
      const duration = endTime - startTime;

      if (error) {
        console.error('❌ Insert error:', error);
        return { data: null, error: error.message, timing: duration };
      }

      console.log('✅ Insert success:', data);
      console.log('⏱️ Insert timing:', duration.toFixed(2), 'ms');
      return { data: data?.[0] || null, error: null, timing: duration };
      
    } catch (err) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      console.error('❌ Insert exception:', err);
      return { data: null, error: String(err), timing: duration };
    }
  };

  // Run comprehensive test suite
  const runTestSuite = async () => {
    setIsLoading(true);
    const errors: string[] = [];
    
    console.log('🧪 Starting Supabase REST API Test Suite...');
    
    // Test 1: Fetch all questions
    const fetchResult = await testFetchAllQuestions();
    if (fetchResult.error) errors.push(`Fetch: ${fetchResult.error}`);
    
    // Test 2: Insert a new question (only if user provided text)
    let insertResult = null;
    let insertTiming = 0;
    
    if (testQuestionText.trim()) {
      const insertResponse = await testInsertQuestion(testQuestionText);
      insertResult = insertResponse.data;
      insertTiming = insertResponse.timing;
      if (insertResponse.error) errors.push(`Insert: ${insertResponse.error}`);
    }

    setTestResults({
      fetchAll: fetchResult.data,
      insertResult,
      errors,
      timings: {
        fetchAllMs: fetchResult.timing,
        insertMs: insertTiming
      }
    });
    
    setIsLoading(false);
    console.log('🏁 Test suite completed!');
  };

  // Auto-run fetch test on component mount
  useEffect(() => {
    testFetchAllQuestions().then(result => {
      setTestResults(prev => ({
        ...prev,
        fetchAll: result.data,
        errors: result.error ? [result.error] : [],
        timings: { ...prev.timings, fetchAllMs: result.timing }
      }));
    });
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🧪 Supabase REST API Test
        </h1>
        <p className="text-gray-600">
          Testing Supabase&apos;s auto-generated REST API independently from Django backend
        </p>
      </div>

      {/* Test Controls */}
      <div className="bg-blue-50 p-4 rounded-lg mb-6">
        <h2 className="text-lg font-semibold mb-4">Test Controls</h2>
        
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label htmlFor="question-text" className="block text-sm font-medium text-gray-700 mb-2">
              Test Question Text (optional)
            </label>
            <input
              id="question-text"
              type="text"
              value={testQuestionText}
              onChange={(e) => setTestQuestionText(e.target.value)}
              placeholder="Enter a test question to insert..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={runTestSuite}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Testing...' : 'Run Tests'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {testResults.errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg mb-6">
          <h3 className="text-lg font-semibold text-red-800 mb-2">❌ Errors</h3>
          {testResults.errors.map((error, index) => (
            <div key={index} className="text-red-700 mb-1">
              • {error}
            </div>
          ))}
        </div>
      )}

      {/* Performance Metrics */}
      <div className="bg-green-50 border border-green-200 p-4 rounded-lg mb-6">
        <h3 className="text-lg font-semibold text-green-800 mb-2">⏱️ Performance</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="font-medium">Fetch All:</span> {testResults.timings.fetchAllMs.toFixed(2)}ms
          </div>
          {testResults.timings.insertMs > 0 && (
            <div>
              <span className="font-medium">Insert:</span> {testResults.timings.insertMs.toFixed(2)}ms
            </div>
          )}
        </div>
      </div>

      {/* Results Display */}
      <div className="space-y-6">
        {/* Fetch Results */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">
            📋 Fetched Questions ({testResults.fetchAll.length})
          </h3>
          {testResults.fetchAll.length === 0 ? (
            <p className="text-gray-600 italic">No questions found in database</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {testResults.fetchAll.slice(0, 5).map((question: any, index) => (
                <div key={question.id || index} className="bg-white p-3 rounded border">
                  <p className="font-medium truncate">{question.text}</p>
                  <div className="text-sm text-gray-500 mt-1">
                    ID: {question.id} • Upvotes: {question.upvotes} • 
                    {question.created_at && ` Created: ${new Date(question.created_at).toLocaleString()}`}
                  </div>
                </div>
              ))}
              {testResults.fetchAll.length > 5 && (
                <p className="text-gray-500 text-sm">
                  ... and {testResults.fetchAll.length - 5} more questions
                </p>
              )}
            </div>
          )}
        </div>

        {/* Insert Result */}
        {testResults.insertResult && (
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800 mb-4">
              ✅ Successfully Inserted Question
            </h3>
            <div className="bg-white p-3 rounded border">
              <p className="font-medium">{testResults.insertResult.text}</p>
              <div className="text-sm text-gray-500 mt-1">
                ID: {testResults.insertResult.id} • 
                Created: {new Date(testResults.insertResult.created_at).toLocaleString()}
              </div>
            </div>
          </div>
        )}

        {/* Raw Data Debug */}
        <details className="bg-gray-100 p-4 rounded-lg">
          <summary className="cursor-pointer font-semibold text-gray-700">
            🔍 Raw API Response Data (Click to expand)
          </summary>
          <pre className="mt-4 text-sm bg-white p-3 rounded border overflow-auto max-h-64">
            {JSON.stringify({ 
              fetchedData: testResults.fetchAll, 
              insertedData: testResults.insertResult 
            }, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}
