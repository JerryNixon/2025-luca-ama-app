// 🧪 COMPLETE Supabase REST API Examples
// This shows all the different ways to call Supabase's auto-generated REST API

import { supabase } from '../lib/supabase';

// ==========================================
// METHOD 1: Using @supabase/supabase-js Client (EASIEST)
// ==========================================

export const exampleSupabaseClient = {
  // Fetch all questions
  async fetchQuestions() {
    const { data, error } = await supabase
      .from('questions')  // ← Table name here
      .select('*');       // ← What columns to get
    
    return { data, error };
  },

  // Insert a new question
  async insertQuestion(questionText: string) {
    const { data, error } = await supabase
      .from('questions')
      .insert([
        {
          text: questionText,
          upvotes: 0,
          is_answered: false
        }
      ])
      .select(); // Return the inserted data

    return { data, error };
  },

  // Update a question
  async updateQuestion(id: string, updates: any) {
    const { data, error } = await supabase
      .from('questions')
      .update(updates)
      .eq('id', id)       // ← WHERE condition
      .select();

    return { data, error };
  },

  // Delete a question
  async deleteQuestion(id: string) {
    const { error } = await supabase
      .from('questions')
      .delete()
      .eq('id', id);

    return { error };
  },

  // Advanced querying with filters
  async getFilteredQuestions() {
    const { data, error } = await supabase
      .from('questions')
      .select('*')
      .eq('is_answered', false)    // WHERE is_answered = false
      .gte('upvotes', 5)           // AND upvotes >= 5
      .order('upvotes', { ascending: false })  // ORDER BY upvotes DESC
      .limit(10);                  // LIMIT 10

    return { data, error };
  }
};

// ==========================================
// METHOD 2: Direct HTTP Calls with fetch() (MANUAL)
// ==========================================

export const exampleDirectHttp = {
  baseUrl: 'https://zcbgzcoqrxkzkzfugoqk.supabase.co/rest/v1',
  apiKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjYmd6Y29xcnhremt6ZnVnb3FrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4NjA0NDUsImV4cCI6MjA2ODQzNjQ0NX0.Jk1EOZLtOX1G53JcbpxV2t4m9nUqlc75FGWtqQ93zwc',

  // GET - Fetch all questions
  async fetchQuestionsHttp() {
    const response = await fetch(`${this.baseUrl}/questions`, {
      method: 'GET',
      headers: {
        'apikey': this.apiKey,
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  },

  // POST - Create new question
  async insertQuestionHttp(questionData: any) {
    const response = await fetch(`${this.baseUrl}/questions`, {
      method: 'POST',
      headers: {
        'apikey': this.apiKey,
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'  // ← Return inserted data
      },
      body: JSON.stringify(questionData)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  },

  // PATCH - Update question
  async updateQuestionHttp(id: string, updates: any) {
    const response = await fetch(`${this.baseUrl}/questions?id=eq.${id}`, {
      method: 'PATCH',
      headers: {
        'apikey': this.apiKey,
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
      },
      body: JSON.stringify(updates)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  },

  // DELETE - Remove question
  async deleteQuestionHttp(id: string) {
    const response = await fetch(`${this.baseUrl}/questions?id=eq.${id}`, {
      method: 'DELETE',
      headers: {
        'apikey': this.apiKey,
        'Authorization': `Bearer ${this.apiKey}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return { success: true };
  }
};

// ==========================================
// METHOD 3: Using Axios (ALTERNATIVE)
// ==========================================

export const exampleAxios = {
  baseUrl: 'https://zcbgzcoqrxkzkzfugoqk.supabase.co/rest/v1',
  
  // Create axios instance with default headers
  client: (() => {
    const axios = require('axios');
    return axios.create({
      baseURL: 'https://zcbgzcoqrxkzkzfugoqk.supabase.co/rest/v1',
      headers: {
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjYmd6Y29xcnhremt6ZnVnb3FrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4NjA0NDUsImV4cCI6MjA2ODQzNjQ0NX0.Jk1EOZLtOX1G53JcbpxV2t4m9nUqlc75FGWtqQ93zwc',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjYmd6Y29xcnhremt6ZnVnb3FrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4NjA0NDUsImV4cCI6MjA2ODQzNjQ0NX0.Jk1EOZLtOX1G53JcbpxV2t4m9nUqlc75FGWtqQ93zwc',
        'Content-Type': 'application/json'
      }
    });
  })(),

  async fetchQuestionsAxios() {
    const response = await this.client.get('/questions');
    return response.data;
  },

  async insertQuestionAxios(questionData: any) {
    const response = await this.client.post('/questions', questionData, {
      headers: { 'Prefer': 'return=representation' }
    });
    return response.data;
  }
};

// ==========================================
// QUERY EXAMPLES - Advanced Filtering
// ==========================================

export const queryExamples = {
  // Filter examples (using PostgREST syntax)
  examples: {
    // Simple filters
    'Equal': '?column=eq.value',
    'Not equal': '?column=neq.value', 
    'Greater than': '?column=gt.5',
    'Greater or equal': '?column=gte.5',
    'Less than': '?column=lt.10',
    'Less or equal': '?column=lte.10',
    'Like pattern': '?column=like.*pattern*',
    'In list': '?column=in.(value1,value2,value3)',
    
    // Multiple filters (AND)
    'Multiple AND': '?is_answered=eq.false&upvotes=gte.5',
    
    // Sorting
    'Order by': '?order=upvotes.desc,created_at.asc',
    
    // Pagination
    'Limit': '?limit=10',
    'Range': '?offset=20&limit=10',
    
    // Select specific columns
    'Select columns': '?select=id,text,upvotes',
    
    // Count
    'Count only': '?select=count()',
  },

  // Real examples for questions table
  async getRealExamples() {
    const { data: unanswered } = await supabase
      .from('questions')
      .select('*')
      .eq('is_answered', false);

    const { data: popular } = await supabase
      .from('questions') 
      .select('*')
      .gte('upvotes', 10)
      .order('upvotes', { ascending: false })
      .limit(5);

    const { data: recent } = await supabase
      .from('questions')
      .select('id, text, created_at')
      .order('created_at', { ascending: false })
      .limit(10);

    return { unanswered, popular, recent };
  }
};

// ==========================================
// ERROR HANDLING EXAMPLES
// ==========================================

export const errorHandlingExamples = {
  async safeApiCall() {
    try {
      const { data, error } = await supabase
        .from('questions')
        .select('*');

      // Supabase-specific error handling
      if (error) {
        console.error('Supabase error:', error.message);
        console.error('Error details:', error.details);
        console.error('Error hint:', error.hint);
        return { success: false, error: error.message };
      }

      return { success: true, data };

    } catch (exception) {
      // Network or other errors
      console.error('Network/JS error:', exception);
      return { success: false, error: 'Connection failed' };
    }
  },

  // Common error types you'll see:
  errorTypes: {
    '404': 'Table does not exist or is not accessible',
    '401': 'Authentication failed - check API key', 
    '403': 'Permission denied - check RLS policies',
    '400': 'Bad request - check your query syntax',
    '500': 'Server error - check Supabase status'
  }
};

export default {
  supabaseClient: exampleSupabaseClient,
  directHttp: exampleDirectHttp,
  axios: exampleAxios,
  queries: queryExamples,
  errors: errorHandlingExamples
};
