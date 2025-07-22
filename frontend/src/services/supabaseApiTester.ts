// Advanced Supabase REST API service functions
// These functions provide more sophisticated testing capabilities

import { supabase, Question, TABLES } from '../lib/supabase';

export interface SupabaseApiResult<T = any> {
  data: T | null;
  error: string | null;
  timing: number;
  metadata?: {
    count?: number;
    statusCode?: number;
  };
}

export class SupabaseApiTester {
  
  // 1. Fetch with advanced filtering and pagination
  static async fetchQuestionsAdvanced(options: {
    limit?: number;
    offset?: number;
    orderBy?: 'created_at' | 'upvotes';
    ascending?: boolean;
    filters?: {
      is_answered?: boolean;
      is_starred?: boolean;
      min_upvotes?: number;
    };
  } = {}): Promise<SupabaseApiResult<Question[]>> {
    
    const startTime = performance.now();
    console.log('🔍 Advanced fetch with options:', options);

    try {
      let query = supabase
        .from(TABLES.QUESTIONS)
        .select('*', { count: 'exact' });

      // Apply filters
      if (options.filters) {
        if (options.filters.is_answered !== undefined) {
          query = query.eq('is_answered', options.filters.is_answered);
        }
        if (options.filters.is_starred !== undefined) {
          query = query.eq('is_starred', options.filters.is_starred);
        }
        if (options.filters.min_upvotes !== undefined) {
          query = query.gte('upvotes', options.filters.min_upvotes);
        }
      }

      // Apply ordering
      const orderBy = options.orderBy || 'created_at';
      const ascending = options.ascending ?? false;
      query = query.order(orderBy, { ascending });

      // Apply pagination
      if (options.limit) {
        query = query.limit(options.limit);
      }
      if (options.offset) {
        query = query.range(options.offset, options.offset + (options.limit || 10) - 1);
      }

      const { data, error, count } = await query;
      const timing = performance.now() - startTime;

      if (error) {
        console.error('❌ Advanced fetch error:', error);
        return { data: null, error: error.message, timing };
      }

      console.log(`✅ Advanced fetch: ${data?.length}/${count} questions in ${timing.toFixed(2)}ms`);
      return { 
        data: data || [], 
        error: null, 
        timing,
        metadata: { count: count || 0 }
      };

    } catch (err) {
      const timing = performance.now() - startTime;
      console.error('❌ Advanced fetch exception:', err);
      return { data: null, error: String(err), timing };
    }
  }

  // 2. Bulk insert multiple questions
  static async bulkInsertQuestions(questions: Omit<Question, 'id' | 'created_at' | 'updated_at'>[]): Promise<SupabaseApiResult<Question[]>> {
    const startTime = performance.now();
    console.log(`➕ Bulk inserting ${questions.length} questions...`);

    try {
      const { data, error } = await supabase
        .from(TABLES.QUESTIONS)
        .insert(questions)
        .select();

      const timing = performance.now() - startTime;

      if (error) {
        console.error('❌ Bulk insert error:', error);
        return { data: null, error: error.message, timing };
      }

      console.log(`✅ Bulk insert: ${data?.length} questions in ${timing.toFixed(2)}ms`);
      return { data: data || [], error: null, timing };

    } catch (err) {
      const timing = performance.now() - startTime;
      console.error('❌ Bulk insert exception:', err);
      return { data: null, error: String(err), timing };
    }
  }

  // 3. Update question (for testing PATCH operations)
  static async updateQuestion(id: string, updates: Partial<Question>): Promise<SupabaseApiResult<Question>> {
    const startTime = performance.now();
    console.log('📝 Updating question:', id, updates);

    try {
      const { data, error } = await supabase
        .from(TABLES.QUESTIONS)
        .update(updates)
        .eq('id', id)
        .select()
        .single();

      const timing = performance.now() - startTime;

      if (error) {
        console.error('❌ Update error:', error);
        return { data: null, error: error.message, timing };
      }

      console.log(`✅ Updated question in ${timing.toFixed(2)}ms`);
      return { data, error: null, timing };

    } catch (err) {
      const timing = performance.now() - startTime;
      console.error('❌ Update exception:', err);
      return { data: null, error: String(err), timing };
    }
  }

  // 4. Delete question (for cleanup)
  static async deleteQuestion(id: string): Promise<SupabaseApiResult<void>> {
    const startTime = performance.now();
    console.log('🗑️ Deleting question:', id);

    try {
      const { error } = await supabase
        .from(TABLES.QUESTIONS)
        .delete()
        .eq('id', id);

      const timing = performance.now() - startTime;

      if (error) {
        console.error('❌ Delete error:', error);
        return { data: null, error: error.message, timing };
      }

      console.log(`✅ Deleted question in ${timing.toFixed(2)}ms`);
      return { data: null, error: null, timing };

    } catch (err) {
      const timing = performance.now() - startTime;
      console.error('❌ Delete exception:', err);
      return { data: null, error: String(err), timing };
    }
  }

  // 5. Performance benchmark (compare multiple operations)
  static async runPerformanceBenchmark(): Promise<{
    results: {
      operation: string;
      timing: number;
      success: boolean;
    }[];
    totalTime: number;
  }> {
    const overallStart = performance.now();
    console.log('🏃‍♂️ Starting performance benchmark...');
    
    const results = [];
    
    // Test 1: Simple fetch
    const fetch1 = await this.fetchQuestionsAdvanced({ limit: 10 });
    results.push({
      operation: 'Fetch 10 questions',
      timing: fetch1.timing,
      success: !fetch1.error
    });

    // Test 2: Complex fetch with filters
    const fetch2 = await this.fetchQuestionsAdvanced({ 
      limit: 20, 
      orderBy: 'upvotes', 
      filters: { min_upvotes: 0 } 
    });
    results.push({
      operation: 'Fetch with filters & sorting',
      timing: fetch2.timing,
      success: !fetch2.error
    });

    // Test 3: Insert
    const insert = await supabase
      .from(TABLES.QUESTIONS)
      .insert([{
        text: `Benchmark test question ${Date.now()}`,
        is_anonymous: true,
        upvotes: 0,
        is_answered: false,
        is_starred: false,
        is_staged: false,
        tags: '[]'
      }])
      .select();
    
    results.push({
      operation: 'Insert question',
      timing: 0, // We'll measure this separately if needed
      success: !insert.error
    });

    const totalTime = performance.now() - overallStart;
    console.log(`🏁 Benchmark completed in ${totalTime.toFixed(2)}ms`);
    
    return { results, totalTime };
  }

  // 6. Test real-time subscriptions (for WebSocket testing)
  static subscribeToQuestions(callback: (payload: any) => void) {
    console.log('🔄 Setting up real-time subscription...');
    
    const subscription = supabase
      .channel('questions_changes')
      .on(
        'postgres_changes',
        {
          event: '*', // Listen to all changes
          schema: 'public',
          table: TABLES.QUESTIONS
        },
        callback
      )
      .subscribe();

    console.log('✅ Real-time subscription active');
    
    return {
      unsubscribe: () => {
        console.log('🛑 Unsubscribing from real-time updates');
        supabase.removeChannel(subscription);
      }
    };
  }
}

// Utility functions for testing
export const SupabaseTestUtils = {
  // Generate realistic test data
  generateTestQuestions: (count: number): Omit<Question, 'id' | 'created_at' | 'updated_at'>[] => {
    const templates = [
      "How does {topic} affect {outcome}?",
      "What are the best practices for {topic}?",
      "Can you explain {topic} in simple terms?",
      "What's the difference between {topic1} and {topic2}?",
      "How do you implement {topic} in a production environment?"
    ];

    const topics = ['React', 'Supabase', 'Performance', 'Security', 'Scalability', 'Testing'];
    
    return Array.from({ length: count }, (_, i) => {
      const template = templates[i % templates.length];
      const topic = topics[i % topics.length];
      const text = template
        .replace('{topic}', topic)
        .replace('{topic1}', topic)
        .replace('{topic2}', topics[(i + 1) % topics.length])
        .replace('{outcome}', 'user experience');

      return {
        text,
        is_anonymous: Math.random() > 0.5,
        upvotes: Math.floor(Math.random() * 10),
        is_answered: Math.random() > 0.7,
        is_starred: Math.random() > 0.8,
        is_staged: Math.random() > 0.9,
        presenter_notes: '',
        ai_summary: '',
        tags: JSON.stringify([topic.toLowerCase()])
      };
    });
  },

  // Clean up test data
  cleanupTestData: async (textPattern: string): Promise<number> => {
    console.log('🧹 Cleaning up test data containing:', textPattern);
    
    const { data, error } = await supabase
      .from(TABLES.QUESTIONS)
      .delete()
      .like('text', `%${textPattern}%`)
      .select();

    if (error) {
      console.error('❌ Cleanup error:', error);
      return 0;
    }

    const deletedCount = data?.length || 0;
    console.log(`✅ Cleaned up ${deletedCount} test questions`);
    return deletedCount;
  }
};

export default SupabaseApiTester;
