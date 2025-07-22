// Backend Performance Comparison Service
// This helps compare your Django/Fabric SQL backend with Supabase REST API

import axios from 'axios';
import { SupabaseApiTester } from './supabaseApiTester';
import { supabase, Question, TABLES } from '../lib/supabase';

interface PerformanceResult {
  backend: string;
  operation: string;
  timing: number;
  success: boolean;
  dataCount: number;
  error?: string;
}

export class BackendComparison {
  private djangoBaseUrl: string;

  constructor(djangoBaseUrl = 'http://localhost:8000') {
    this.djangoBaseUrl = djangoBaseUrl;
  }

  // Test Django backend (your existing Fabric SQL setup)
  async testDjangoFetch(): Promise<PerformanceResult> {
    const startTime = performance.now();
    
    try {
      const response = await axios.get(`${this.djangoBaseUrl}/api/questions/`, {
        timeout: 10000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      const timing = performance.now() - startTime;
      
      return {
        backend: 'Django + Fabric SQL',
        operation: 'Fetch Questions',
        timing,
        success: true,
        dataCount: response.data?.length || response.data?.results?.length || 0
      };

    } catch (error: any) {
      const timing = performance.now() - startTime;
      
      return {
        backend: 'Django + Fabric SQL',
        operation: 'Fetch Questions',
        timing,
        success: false,
        dataCount: 0,
        error: error.message || 'Connection failed'
      };
    }
  }

  // Test Django insertion
  async testDjangoInsert(questionText: string): Promise<PerformanceResult> {
    const startTime = performance.now();
    
    try {
      const response = await axios.post(
        `${this.djangoBaseUrl}/api/questions/`,
        {
          text: questionText,
          is_anonymous: true,
          event: null // Adjust based on your API requirements
        },
        {
          timeout: 10000,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            // Add authentication headers if required
          }
        }
      );

      const timing = performance.now() - startTime;
      
      return {
        backend: 'Django + Fabric SQL',
        operation: 'Insert Question',
        timing,
        success: true,
        dataCount: 1
      };

    } catch (error: any) {
      const timing = performance.now() - startTime;
      
      return {
        backend: 'Django + Fabric SQL',
        operation: 'Insert Question',
        timing,
        success: false,
        dataCount: 0,
        error: error.message || 'Insert failed'
      };
    }
  }

  // Test Supabase fetch
  async testSupabaseFetch(): Promise<PerformanceResult> {
    const startTime = performance.now();
    
    try {
      const { data, error } = await supabase
        .from(TABLES.QUESTIONS)
        .select('*');

      const timing = performance.now() - startTime;
      
      if (error) {
        return {
          backend: 'Supabase REST API',
          operation: 'Fetch Questions',
          timing,
          success: false,
          dataCount: 0,
          error: error.message
        };
      }

      return {
        backend: 'Supabase REST API',
        operation: 'Fetch Questions',
        timing,
        success: true,
        dataCount: data?.length || 0
      };

    } catch (error: any) {
      const timing = performance.now() - startTime;
      
      return {
        backend: 'Supabase REST API',
        operation: 'Fetch Questions',
        timing,
        success: false,
        dataCount: 0,
        error: error.message
      };
    }
  }

  // Test Supabase insertion
  async testSupabaseInsert(questionText: string): Promise<PerformanceResult> {
    const startTime = performance.now();
    
    try {
      const { data, error } = await supabase
        .from(TABLES.QUESTIONS)
        .insert([{
          text: questionText,
          is_anonymous: true,
          upvotes: 0,
          is_answered: false,
          is_starred: false,
          is_staged: false,
          tags: '[]'
        }])
        .select();

      const timing = performance.now() - startTime;
      
      if (error) {
        return {
          backend: 'Supabase REST API',
          operation: 'Insert Question',
          timing,
          success: false,
          dataCount: 0,
          error: error.message
        };
      }

      return {
        backend: 'Supabase REST API',
        operation: 'Insert Question',
        timing,
        success: true,
        dataCount: data?.length || 1
      };

    } catch (error: any) {
      const timing = performance.now() - startTime;
      
      return {
        backend: 'Supabase REST API',
        operation: 'Insert Question',
        timing,
        success: false,
        dataCount: 0,
        error: error.message
      };
    }
  }

  // Run comprehensive comparison
  async runComparison(testQuestionText = 'Performance comparison test'): Promise<{
    results: PerformanceResult[];
    summary: {
      djangoFetchAvg: number;
      supabaseFetchAvg: number;
      djangoInsertAvg: number;
      supabaseInsertAvg: number;
      winner: {
        fetch: string;
        insert: string;
      };
    };
  }> {
    console.log('🏁 Starting Django vs Supabase performance comparison...');
    
    const results: PerformanceResult[] = [];
    
    // Run multiple tests for better averages
    const iterations = 3;
    
    for (let i = 0; i < iterations; i++) {
      console.log(`📊 Running test iteration ${i + 1}/${iterations}`);
      
      // Django tests
      const djangoFetch = await this.testDjangoFetch();
      const djangoInsert = await this.testDjangoInsert(`${testQuestionText} (Django test ${i + 1})`);
      
      // Supabase tests  
      const supabaseFetch = await this.testSupabaseFetch();
      const supabaseInsert = await this.testSupabaseInsert(`${testQuestionText} (Supabase test ${i + 1})`);
      
      results.push(djangoFetch, djangoInsert, supabaseFetch, supabaseInsert);
      
      // Small delay between iterations
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // Calculate averages
    const djangoFetchResults = results.filter(r => r.backend.includes('Django') && r.operation.includes('Fetch') && r.success);
    const supabaseFetchResults = results.filter(r => r.backend.includes('Supabase') && r.operation.includes('Fetch') && r.success);
    const djangoInsertResults = results.filter(r => r.backend.includes('Django') && r.operation.includes('Insert') && r.success);
    const supabaseInsertResults = results.filter(r => r.backend.includes('Supabase') && r.operation.includes('Insert') && r.success);

    const avgTiming = (results: PerformanceResult[]) => 
      results.length > 0 ? results.reduce((sum, r) => sum + r.timing, 0) / results.length : 0;

    const djangoFetchAvg = avgTiming(djangoFetchResults);
    const supabaseFetchAvg = avgTiming(supabaseFetchResults);
    const djangoInsertAvg = avgTiming(djangoInsertResults);
    const supabaseInsertAvg = avgTiming(supabaseInsertResults);

    const summary = {
      djangoFetchAvg,
      supabaseFetchAvg,
      djangoInsertAvg,
      supabaseInsertAvg,
      winner: {
        fetch: djangoFetchAvg === 0 ? 'Supabase' : 
               supabaseFetchAvg === 0 ? 'Django' :
               djangoFetchAvg < supabaseFetchAvg ? 'Django' : 'Supabase',
        insert: djangoInsertAvg === 0 ? 'Supabase' : 
                supabaseInsertAvg === 0 ? 'Django' :
                djangoInsertAvg < supabaseInsertAvg ? 'Django' : 'Supabase'
      }
    };

    console.log('✅ Performance comparison completed:', summary);
    
    return { results, summary };
  }

  // Quick connectivity test
  async testConnectivity(): Promise<{
    django: { connected: boolean; responseTime: number; error?: string };
    supabase: { connected: boolean; responseTime: number; error?: string };
  }> {
    console.log('🔗 Testing backend connectivity...');

    // Test Django
    const djangoStart = performance.now();
    let djangoResult;
    try {
      await axios.get(`${this.djangoBaseUrl}/api/health/`, { timeout: 5000 });
      djangoResult = {
        connected: true,
        responseTime: performance.now() - djangoStart
      };
    } catch (error: any) {
      djangoResult = {
        connected: false,
        responseTime: performance.now() - djangoStart,
        error: error.message
      };
    }

    // Test Supabase
    const supabaseStart = performance.now();
    let supabaseResult;
    try {
      const { error } = await supabase.from(TABLES.QUESTIONS).select('id').limit(1);
      supabaseResult = {
        connected: !error,
        responseTime: performance.now() - supabaseStart,
        error: error?.message
      };
    } catch (error: any) {
      supabaseResult = {
        connected: false,
        responseTime: performance.now() - supabaseStart,
        error: error.message
      };
    }

    return {
      django: djangoResult,
      supabase: supabaseResult
    };
  }
}

export default BackendComparison;
