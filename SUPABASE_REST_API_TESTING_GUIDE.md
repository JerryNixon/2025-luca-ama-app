# 🧪 Supabase REST API Testing Guide

This guide provides a comprehensive testing setup for comparing Supabase's auto-generated REST API with your existing Django + Fabric SQL backend.

## 📁 Project Structure

```
frontend/src/
├── app/
│   └── supabase-test/              # ← NEW: Isolated testing page
│       ├── page.tsx                # Main test page
│       └── components/
│           └── SupabaseTest.tsx    # Test component
├── lib/
│   └── supabase.ts                 # ← UPDATED: Supabase client config
├── services/
│   ├── supabaseApiTester.ts        # ← NEW: Advanced Supabase operations
│   └── backendComparison.ts        # ← NEW: Django vs Supabase comparison
└── .env.local                      # ← NEW: Environment variables
```

## 🚀 Quick Start

### 1. Navigate to Test Page
Open your browser and go to:
```
http://localhost:3000/supabase-test
```

### 2. Run Basic Tests
- **Auto-fetch**: Page automatically loads all questions from Supabase
- **Manual test**: Enter a test question and click "Run Tests"
- **Check console**: Open browser DevTools for detailed logging

### 3. Verify Results
- **UI Results**: View formatted results on the page
- **Console Logs**: Detailed API responses and timing data
- **Supabase Dashboard**: Check if data appears in your Supabase project
- **Performance**: Compare timing with your Django backend

## 🎯 What This Tests

### Core Operations
- ✅ **Fetch All Questions**: `GET` from Supabase REST API
- ✅ **Insert Question**: `POST` to create new questions
- ✅ **Performance Measurement**: Precise timing in milliseconds
- ✅ **Error Handling**: Catches and displays API errors

### Advanced Features (via Services)
- 🔍 **Advanced Querying**: Filters, sorting, pagination
- 📊 **Bulk Operations**: Insert multiple questions at once
- 🔄 **Real-time Subscriptions**: WebSocket-based live updates
- ⚡ **Performance Benchmarking**: Comprehensive speed tests
- 🆚 **Backend Comparison**: Django vs Supabase side-by-side

## 🛡️ Isolation Strategy

This testing setup is **completely isolated** from your Django backend:

1. **Separate Client**: Uses `@supabase/supabase-js` directly
2. **No Django Dependencies**: No models, serializers, or views involved
3. **Direct REST API**: Communicates with Supabase's auto-generated endpoints
4. **Separate Environment**: Uses `.env.local` for configuration
5. **No Database Conflicts**: Tests Supabase tables independently

## 🔧 Configuration Details

### Environment Variables (`.env.local`)
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### Supabase Client (`lib/supabase.ts`)
- Configured with environment variables
- Type definitions matching your Django models
- Reusable across components

### Table Configuration
Currently configured for `questions` table with these fields:
- `id`, `text`, `author_id`, `event_id`
- `is_anonymous`, `upvotes`, `is_answered`, `is_starred`, `is_staged`
- `presenter_notes`, `ai_summary`, `parent_question_id`, `tags`
- `created_at`, `updated_at`

## 📊 Performance Testing

### Basic Performance Metrics
The test page automatically measures:
- **Fetch Latency**: Time to retrieve all questions
- **Insert Latency**: Time to create new questions
- **Success Rate**: Percentage of successful operations

### Advanced Benchmarking
Use the `BackendComparison` service to:
```typescript
import BackendComparison from '../services/backendComparison';

const comparison = new BackendComparison('http://localhost:8000');
const results = await comparison.runComparison();
console.log('Performance Results:', results);
```

## 🔍 Debugging & Verification

### Browser Console Logs
The tests produce detailed console output:
```
🔍 Testing: Fetch all questions from Supabase...
✅ Fetch success: 15 questions found
⏱️ Fetch timing: 234.50 ms
```

### Supabase Dashboard
1. Go to your Supabase project dashboard
2. Navigate to Table Editor
3. Check the `questions` table for new entries
4. Verify data structure matches expectations

### Network Tab
Open DevTools → Network tab to see:
- REST API endpoints being called
- Request/response payloads
- HTTP status codes
- Response times

## 🔄 Real-time Testing

To test WebSocket subscriptions:
```typescript
import { SupabaseApiTester } from '../services/supabaseApiTester';

// Set up real-time listener
const subscription = SupabaseApiTester.subscribeToQuestions((payload) => {
  console.log('Real-time update:', payload);
});

// Don't forget to unsubscribe
subscription.unsubscribe();
```

## 🧹 Cleanup & Maintenance

### Remove Test Data
```typescript
import { SupabaseTestUtils } from '../services/supabaseApiTester';

// Remove test questions containing specific text
await SupabaseTestUtils.cleanupTestData('test');
```

### Reset Environment
If you need to switch back to Django:
1. Comment out Supabase client code
2. Restore Django API calls
3. Update environment variables

## 🆚 Backend Integration (Optional)

To integrate this into your Django backend for comparison:

### 1. Create Django View
```python
# backend/api/views.py
from django.http import JsonResponse
from .models import Question

def supabase_comparison_view(request):
    # Your existing Django logic
    questions = Question.objects.all()
    
    # Compare with Supabase
    # (Add comparison logic here)
    
    return JsonResponse({
        'django_count': questions.count(),
        'supabase_sync_status': 'pending'  # Your comparison results
    })
```

### 2. Add URL Pattern
```python
# backend/api/urls.py
urlpatterns = [
    path('supabase-comparison/', views.supabase_comparison_view),
    # ... existing patterns
]
```

### 3. Frontend Integration
```typescript
// Call your Django comparison endpoint
const response = await axios.get('/api/supabase-comparison/');
console.log('Django comparison:', response.data);
```

## 📈 Next Steps

After running these tests, you can:

1. **Analyze Performance**: Compare response times with your Django backend
2. **Test Scalability**: Use bulk operations to test with larger datasets  
3. **Evaluate Features**: Try real-time subscriptions, advanced querying
4. **Migration Planning**: Use results to plan potential migration strategy
5. **Hybrid Approach**: Consider using both backends for different use cases

## ⚠️ Important Notes

- **Anon Key Safety**: The anon key is safe for frontend use (RLS-protected)
- **Service Role Key**: Never use service role key in frontend code
- **CORS Configuration**: Ensure Supabase allows your domain
- **RLS Policies**: May need to configure Row Level Security for full functionality
- **Data Consistency**: Test data may differ between Django and Supabase

## 🎯 Success Criteria

Your test setup is working correctly if you can:
- ✅ See questions fetched from Supabase in the UI
- ✅ Successfully insert new questions
- ✅ View detailed console logs with timing data
- ✅ See new data in Supabase dashboard
- ✅ Compare performance with Django backend
- ✅ Handle errors gracefully

## 🆘 Troubleshooting

### Common Issues:

**Environment Variables Not Loading**
- Restart Next.js dev server after creating `.env.local`
- Ensure variable names start with `NEXT_PUBLIC_`

**CORS Errors**
- Check Supabase dashboard → Settings → API → CORS origins
- Add your frontend URL (e.g., `http://localhost:3000`)

**Database Connection Errors**
- Verify Supabase credentials in `.env.local`
- Check if `questions` table exists in Supabase
- Ensure RLS policies allow anonymous access (for testing)

**TypeScript Errors**
- Run `npm run build` to check for type issues
- Ensure all imports are correct

---

Happy testing! 🚀 This setup gives you a comprehensive way to evaluate Supabase's REST API capabilities against your existing Django backend.
