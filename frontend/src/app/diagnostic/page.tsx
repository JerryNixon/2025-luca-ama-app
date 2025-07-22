'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://eysipjwmfgtvmjqgfojn.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV5c2lwandtZmd0dm1qcWdmb2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcwNDc3NzQsImV4cCI6MjA1MjYyMzc3NH0.1r8vNJIlEG5dTTJGf_LCuA_vQOJILnK8ZM5HryUMUGM';

export default function DiagnosticPage() {
  const [logs, setLogs] = useState<string[]>([]);
  const [connectionStatus, setConnectionStatus] = useState('Testing...');

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev.slice(0, 19)]);
  };

  useEffect(() => {
    const runDiagnostics = async () => {
      const supabase = createClient(supabaseUrl, supabaseAnonKey);
      
      addLog('🔧 Starting Supabase diagnostics...');
      
      // Test 1: Basic connection
      try {
        addLog('📡 Testing basic Supabase connection...');
        const { data, error } = await supabase
          .from('api_question')
          .select('count')
          .limit(1);
        
        if (error) {
          addLog(`❌ Connection test failed: ${error.message}`);
          setConnectionStatus('Connection Failed');
          return;
        } else {
          addLog('✅ Basic connection successful!');
        }
      } catch (err: any) {
        addLog(`❌ Connection error: ${err.message}`);
        setConnectionStatus('Connection Error');
        return;
      }

      // Test 2: Data fetch
      try {
        addLog('📊 Testing data fetch...');
        const { data, error } = await supabase
          .from('api_question')
          .select('id, text, created_at')
          .limit(5);
        
        if (error) {
          addLog(`❌ Data fetch failed: ${error.message}`);
        } else {
          addLog(`✅ Fetched ${data?.length || 0} questions`);
          if (data && data.length > 0) {
            addLog(`📝 Latest question: "${data[0].text?.substring(0, 50)}..."`);
          }
        }
      } catch (err: any) {
        addLog(`❌ Data fetch error: ${err.message}`);
      }

      // Test 3: Real-time subscription
      try {
        addLog('🔔 Testing real-time subscription...');
        
        const channel = supabase
          .channel('diagnostic-test')
          .on(
            'postgres_changes',
            {
              event: '*',
              schema: 'public',
              table: 'api_question',
            },
            (payload) => {
              addLog(`🎉 Real-time update received: ${payload.eventType}`);
              console.log('Real-time payload:', payload);
            }
          )
          .subscribe((status) => {
            addLog(`📡 Subscription status: ${status}`);
            if (status === 'SUBSCRIBED') {
              setConnectionStatus('✅ WebSocket Connected!');
              addLog('🚀 Real-time subscriptions are working!');
            } else if (status === 'CHANNEL_ERROR') {
              setConnectionStatus('❌ WebSocket Failed');
              addLog('❌ Real-time subscription failed');
            }
          });

        // Cleanup function
        return () => {
          addLog('🔌 Cleaning up subscription...');
          supabase.removeChannel(channel);
        };
        
      } catch (err: any) {
        addLog(`❌ Subscription setup error: ${err.message}`);
        setConnectionStatus('Subscription Error');
      }
    };

    const cleanup = runDiagnostics();
    return () => {
      cleanup.then(cleanupFn => cleanupFn?.());
    };
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        🔍 Supabase Connection Diagnostics
      </h1>
      
      <div className={`border rounded-lg p-4 mb-6 ${
        connectionStatus.includes('Connected') 
          ? 'bg-green-50 border-green-200' 
          : connectionStatus.includes('Failed') || connectionStatus.includes('Error')
          ? 'bg-red-50 border-red-200' 
          : 'bg-blue-50 border-blue-200'
      }`}>
        <h2 className="text-lg font-medium mb-2">Connection Status</h2>
        <p className="text-lg">{connectionStatus}</p>
      </div>

      <div className="bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-sm">
        <h3 className="text-white text-base font-bold mb-4">🖥️ Console Log</h3>
        <div className="space-y-1 max-h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <div className="text-gray-500">Starting diagnostics...</div>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="whitespace-pre-wrap">
                {log}
              </div>
            ))
          )}
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-lg font-medium text-blue-900 mb-2">🧪 Next Steps</h3>
        <div className="text-blue-700 text-sm">
          <p className="mb-2">1. If WebSocket connected: Run test_realtime.py script</p>
          <p className="mb-2">2. Watch this page for real-time updates</p>
          <p className="mb-2">3. Check browser console (F12) for detailed logs</p>
          <p>4. If failed: Check RLS policies and network settings</p>
        </div>
      </div>
    </div>
  );
}
