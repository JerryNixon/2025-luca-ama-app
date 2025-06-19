# Similar Questions Toggle Feature - Implementation Complete

## Overview

The "expand similar questions" toggle functionality has been successfully implemented in the user question list view. Users can now expand and collapse similar questions by clicking the + and - buttons.

## Features Implemented

### 1. **SimilarQuestionsSection Component**
- **Location**: `frontend/src/components/questions/QuestionCard.tsx`
- **Functionality**:
  - ✅ Toggle button with + (expand) and - (collapse) icons
  - ✅ Smooth expand/collapse animation
  - ✅ Shows count of similar questions
  - ✅ Displays similar questions in a compact format
  - ✅ Vote functionality for similar questions
  - ✅ Author information (with anonymity support)
  - ✅ Status indicators (answered, starred)
  - ✅ Tags display for similar questions

### 2. **User Interface Features**
- **Expand Button**: Shows `+ 3 similar questions` when collapsed
- **Collapse Button**: Shows `- 3 similar questions` when expanded  
- **Animation**: Smooth rotation transition for the +/- icon
- **Layout**: Similar questions indented with visual hierarchy
- **Voting**: Users can vote on similar questions without leaving the main view

### 3. **Mock Data Integration**
- **Location**: `frontend/src/app/events/[id]/user/page.tsx`
- **Sample Data**: Added realistic similar questions to demonstrate functionality
- **Question 1**: "Developer feedback on Fabric" with 3 grouped similar questions:
  - Tools for Fabric integration
  - API rate limits handling
  - Community resources and forums
- **Question 3**: "Data governance and compliance" with 2 grouped similar questions:
  - GDPR compliance features
  - Data lineage and audit trails

### 4. **Component Integration**
- **QuestionCard Component**: Updated to use the new SimilarQuestionsSection
- **User Event View**: Now uses QuestionCard component instead of custom rendering
- **Props Integration**: Proper handling of vote callbacks and user roles

## Technical Implementation

### State Management
```typescript
const [isExpanded, setIsExpanded] = useState(false);
```

### Toggle Functionality
```typescript
<button 
  onClick={() => setIsExpanded(!isExpanded)}
  className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
>
  <span className={`transition-transform duration-200 ${isExpanded ? 'rotate-45' : ''}`}>
    {isExpanded ? '−' : '+'}
  </span>
  <span>{question.groupedQuestions.length} similar question{question.groupedQuestions.length > 1 ? 's' : ''}</span>
</button>
```

### Conditional Rendering
```typescript
{isExpanded && (
  <div className="mt-3 space-y-3 pl-4 border-l-2 border-gray-100">
    {/* Similar questions content */}
  </div>
)}
```

## User Experience

### Visual Design
- **Hierarchy**: Similar questions indented with left border
- **Compact Layout**: Smaller vote buttons and text for similar questions
- **Color Coding**: Subtle background for similar questions (gray-50)
- **Status Indicators**: Green badges for answered questions
- **Animation**: Smooth 200ms transition for expand/collapse

### Interaction Flow
1. **User sees main question** with "📍 3 similar questions" link
2. **Click +** → Similar questions expand with smooth animation
3. **Browse similar questions** → Can vote and see details  
4. **Click -** → Similar questions collapse back to single line

### Responsive Behavior
- Works on all screen sizes
- Touch-friendly buttons for mobile
- Proper spacing and typography scaling

## Data Structure

### Question Type Extension
```typescript
interface Question {
  // ... existing fields
  groupedQuestions?: Question[]; // Array of similar questions
}
```

### Similar Question Properties
- All standard question properties (text, author, votes, etc.)
- Status indicators (answered, starred, staged)
- Tags for categorization
- Anonymous author support

## Testing Instructions

### How to Test the Feature

1. **Start the application**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Navigate to user view**:
   - Login as a user (email: `demo@microsoft.com`, password: `demo123`)
   - Go to any event
   - You'll be automatically redirected to the user view

3. **Test similar questions**:
   - Look for questions with "+ X similar questions" text
   - Click the + button to expand
   - Click the - button to collapse
   - Try voting on similar questions
   - Verify animations and styling

### Expected Questions with Similar Questions
- **Question 1**: "Developer feedback on Fabric" (3 similar questions)
- **Question 3**: "Data governance and compliance" (2 similar questions)

## Future Enhancements

### Potential Improvements
- **AI-Powered Grouping**: Automatically detect similar questions using AI
- **Drag and Drop**: Allow moderators to manually group questions
- **Search in Similar**: Search functionality within similar questions
- **Bulk Actions**: Operations on all similar questions at once
- **Advanced Filtering**: Filter similar questions by status or tags

### Performance Optimizations
- **Lazy Loading**: Load similar questions only when expanded
- **Virtual Scrolling**: For large numbers of similar questions
- **Caching**: Cache similar question data

## Code Files Modified

### Core Implementation
- ✅ `frontend/src/components/questions/QuestionCard.tsx` - Added SimilarQuestionsSection component
- ✅ `frontend/src/app/events/[id]/user/page.tsx` - Updated to use QuestionCard component and added mock data

### Supporting Files
- ✅ `frontend/src/types/index.ts` - Already had groupedQuestions field
- ✅ `docs/SIMILAR_QUESTIONS_FEATURE.md` - This documentation file

## Status: ✅ COMPLETE

The similar questions toggle functionality is fully implemented and ready for testing. Users can now:
- ✅ **See similar questions count** in a compact format
- ✅ **Expand similar questions** by clicking the + button
- ✅ **Collapse similar questions** by clicking the - button  
- ✅ **Vote on similar questions** without leaving the main view
- ✅ **View all question details** including author, tags, and status

The feature integrates seamlessly with the existing question card design and maintains consistency with the overall application UI/UX.
