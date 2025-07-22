// 🏗️ COMPLETE APP BUILT WITH ONLY SUPABASE REST API
// No Django, No ORM, No Backend Code Required!

'use client';

import React, { useState, useEffect } from 'react';
import { supabase } from '../../lib/supabase';

interface Question {
  id: string;
  text: string;
  upvotes: number;
  is_answered: boolean;
  created_at: string;
  author_id?: string;
}

// This is a COMPLETE questions app using only Supabase REST API
export default function CompleteSupabaseApp() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [newQuestion, setNewQuestion] = useState('');
  const [loading, setLoading] = useState(false);

  // 1. FETCH DATA (replaces Django views.py)
  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    const { data, error } = await supabase
      .from('questions')
      .select(`
        id,
        text,
        upvotes,
        is_answered,
        created_at,
        author_id
      `)
      .order('upvotes', { ascending: false });

    if (error) {
      console.error('Error:', error);
    } else {
      setQuestions(data || []);
    }
  };

  // 2. CREATE DATA (replaces Django POST endpoint)
  const createQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQuestion.trim()) return;

    setLoading(true);
    
    const { data, error } = await supabase
      .from('questions')
      .insert([{
        text: newQuestion,
        upvotes: 0,
        is_answered: false,
        is_anonymous: true
      }])
      .select();

    if (error) {
      alert('Error creating question: ' + error.message);
    } else {
      setQuestions([...questions, ...(data as Question[])]);
      setNewQuestion('');
    }
    
    setLoading(false);
  };

  // 3. UPDATE DATA (replaces Django PATCH endpoint)
  const upvoteQuestion = async (id: string) => {
    const question = questions.find(q => q.id === id);
    if (!question) return;
    
    const { error } = await supabase
      .from('questions')
      .update({ upvotes: question.upvotes + 1 })
      .eq('id', id);

    if (error) {
      alert('Error upvoting: ' + error.message);
    } else {
      fetchQuestions(); // Refresh data
    }
  };

  // 4. DELETE DATA (replaces Django DELETE endpoint) 
  const deleteQuestion = async (id: string) => {
    if (!confirm('Delete this question?')) return;

    const { error } = await supabase
      .from('questions')
      .delete()
      .eq('id', id);

    if (error) {
      alert('Error deleting: ' + error.message);
    } else {
      setQuestions(questions.filter(q => q.id !== id));
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">
        🚀 Complete App - Supabase REST API Only!
      </h1>
      
      <div className="bg-blue-50 p-4 rounded-lg mb-6">
        <h2 className="font-semibold mb-2">No Django Backend Required!</h2>
        <p className="text-sm text-gray-700">
          This entire app uses only Supabase REST API calls. 
          No Django views, serializers, or URLs needed!
        </p>
      </div>

      {/* CREATE FORM */}
      <form onSubmit={createQuestion} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={newQuestion}
            onChange={(e) => setNewQuestion(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 px-4 py-2 border rounded-lg"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Adding...' : 'Add Question'}
          </button>
        </div>
      </form>

      {/* QUESTIONS LIST */}
      <div className="space-y-4">
        {questions.map((question) => (
          <div key={question.id} className="bg-white p-4 rounded-lg shadow border">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <p className="text-lg">{question.text}</p>
                <div className="text-sm text-gray-500 mt-2">
                  {question.upvotes} upvotes • 
                  {question.is_answered ? ' Answered' : ' Unanswered'} •
                  {new Date(question.created_at).toLocaleDateString()}
                </div>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={() => upvoteQuestion(question.id)}
                  className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
                >
                  👍 Upvote
                </button>
                <button
                  onClick={() => deleteQuestion(question.id)}
                  className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {questions.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No questions yet. Add one above!
        </div>
      )}
    </div>
  );
}

// 🎯 WHAT THIS REPLACES IN DJANGO:

/*
DJANGO FILES YOU DON'T NEED:
❌ views.py - API logic handled by Supabase
❌ serializers.py - Data validation handled by Supabase  
❌ urls.py - Endpoints auto-generated by Supabase
❌ models.py - Database schema managed in Supabase dashboard
❌ admin.py - Admin interface built into Supabase
❌ permissions.py - Row Level Security in Supabase
❌ Custom middleware - Built into Supabase
❌ Database migrations - Handled by Supabase

DJANGO ENDPOINTS THIS REPLACES:
✅ GET /api/questions/ → supabase.from('questions').select()
✅ POST /api/questions/ → supabase.from('questions').insert()  
✅ PATCH /api/questions/123/ → supabase.from('questions').update().eq('id', 123)
✅ DELETE /api/questions/123/ → supabase.from('questions').delete().eq('id', 123)
*/
