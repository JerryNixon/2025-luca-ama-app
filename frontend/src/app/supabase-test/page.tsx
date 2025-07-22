// Main page for Supabase REST API testing
// This is completely isolated from your existing Django backend and Fabric SQL setup

import SupabaseTest from './components/SupabaseTest';

export default function SupabaseTestPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Navigation breadcrumb */}
        <div className="mb-6">
          <a href="/" className="text-blue-600 hover:text-blue-800">
            ← Back to Home
          </a>
        </div>

        {/* Page header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🧪 Supabase REST API Testing Lab
          </h1>
          <div className="prose text-gray-700 max-w-none">
            <p className="text-lg mb-4">
              This page tests <strong>Supabase&apos;s auto-generated REST API</strong> in complete isolation 
              from your Django backend and Fabric SQL database.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">🎯 What This Tests:</h3>
              <ul className="text-blue-700 space-y-1">
                <li>• <strong>Direct REST API calls</strong> to your Supabase <code>questions</code> table</li>
                <li>• <strong>Performance comparison</strong> with latency measurements</li>
                <li>• <strong>Data insertion & retrieval</strong> without Django ORM</li>
                <li>• <strong>Real-time capabilities</strong> (auto-refresh on changes)</li>
              </ul>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">🔒 Isolation Strategy:</h3>
              <ul className="text-yellow-700 space-y-1">
                <li>• Uses <code>@supabase/supabase-js</code> client directly</li>
                <li>• No Django models or serializers involved</li>
                <li>• Separate environment variables for Supabase</li>
                <li>• Results logged to browser console for debugging</li>
              </ul>
            </div>
          </div>
        </div>

        {/* The actual test component */}
        <SupabaseTest />

        {/* Instructions */}
        <div className="bg-white rounded-lg shadow-sm p-6 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">📋 How to Use This Test</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">🚀 Running Tests:</h3>
              <ol className="text-gray-700 space-y-2">
                <li>1. The page automatically fetches all questions on load</li>
                <li>2. Optionally enter test question text</li>
                <li>3. Click &quot;Run Tests&quot; to test insertion</li>
                <li>4. Check browser console for detailed logs</li>
              </ol>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">🔍 Verification Steps:</h3>
              <ol className="text-gray-700 space-y-2">
                <li>1. Compare performance with your Django backend</li>
                <li>2. Verify data appears in Supabase dashboard</li>
                <li>3. Check console logs for API response structure</li>
                <li>4. Test error handling with invalid data</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
