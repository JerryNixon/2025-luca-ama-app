// Supabase Client Configuration
// This connects our frontend directly to Supabase database for testing REST API

import { createClient } from '@supabase/supabase-js';

// Use environment variables for secure configuration
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Database table names (matching our Django models)
export const TABLES = {
  QUESTIONS: 'questions', // Direct Supabase table name
  EVENTS: 'events', 
  USERS: 'users'
} as const;

// Type definition matching your Django Question model structure
export interface Question {
  id?: string
  text: string
  author_id?: string | null
  event_id?: string | null
  is_anonymous?: boolean
  upvotes?: number
  is_answered?: boolean
  is_starred?: boolean
  is_staged?: boolean
  presenter_notes?: string | null
  ai_summary?: string | null
  parent_question_id?: string | null
  tags?: string
  created_at?: string
  updated_at?: string
}

// Test data factory for creating new questions
export const createTestQuestion = (text: string): Omit<Question, 'id' | 'created_at' | 'updated_at'> => ({
  text,
  author_id: null, // Will use anonymous for testing
  event_id: null,  // Will use null for testing
  is_anonymous: true,
  upvotes: 0,
  is_answered: false,
  is_starred: false,
  is_staged: false,
  presenter_notes: '',
  ai_summary: '',
  parent_question_id: null,
  tags: '[]'
});

export default supabase;
