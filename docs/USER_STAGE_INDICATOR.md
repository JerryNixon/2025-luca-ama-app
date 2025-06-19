# User Stage Indicator Implementation

## Overview
Implemented a visual indicator for users to see which question is currently being staged/discussed in the AMA session. Users can now easily identify which question the moderator/presenter is currently addressing.

## Implementation Details

### Feature Requirements
- ✅ Visual indicator shows which question is currently on stage
- ✅ Hard-coded for now (ready for backend integration)
- ✅ Clear, intuitive design that doesn't interfere with user experience
- ✅ Consistent with existing app styling

### Visual Indicators

#### 1. Stage Badge
- **Icon**: 🎭 (theater masks emoji)
- **Text**: "On Stage"
- **Styling**: Blue background (`bg-blue-100`) with blue text (`text-blue-800`)
- **Position**: Appears in the status badges area of each question card

#### 2. Enhanced Card Styling
- **Border**: Blue ring border (`ring-2 ring-blue-500`) around the entire question card
- **Background**: Light blue background (`bg-blue-50`) for the staged question
- **Effect**: Makes the staged question stand out prominently from others

### Technical Implementation

#### Mock Data Setup
```typescript
// Question 1 is set as currently staged
{
  id: '1',
  text: 'Hi, I was wondering if developers had any feedback about using fabric...',
  // ... other properties
  isStaged: true, // This question is currently being discussed
  // ... other properties
}

// All other questions are not staged
{
  id: '2',
  // ... other properties
  isStaged: false, // Not currently on stage
  // ... other properties
}
```

#### QuestionCard Component Integration
The existing `QuestionCard` component already handles stage indicators through:

1. **Conditional Badge Rendering**:
```tsx
{question.isStaged && (
  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
    🎭 On Stage
  </span>
)}
```

2. **Conditional Card Styling**:
```tsx
<div className={`card hover:shadow-lg transition-shadow duration-200 ${
  question.isStaged ? 'ring-2 ring-blue-500 bg-blue-50' : ''
}`}>
```

### User Experience

#### For Regular Users:
1. **Easy Identification**: Staged questions are immediately visible with blue styling and stage badge
2. **Context Awareness**: Users know exactly which question is being addressed
3. **Non-intrusive**: The indicator enhances rather than distracts from the experience
4. **Consistent Design**: Follows the same design patterns as other status indicators

#### Visual Hierarchy:
1. **Primary**: Blue border and background make staged question prominent
2. **Secondary**: Theater mask emoji provides intuitive visual cue
3. **Tertiary**: "On Stage" text label provides clear context

### Files Modified

#### Updated Files:
- `frontend/src/app/events/[id]/user/page.tsx` - Added `isStaged: true` to first question in mock data

#### Existing Components Used:
- `frontend/src/components/questions/QuestionCard.tsx` - Already had staging indicator functionality

### Backend Integration Preparation

#### Current State (Hard-coded):
- Question 1 is always marked as staged (`isStaged: true`)
- All other questions are not staged (`isStaged: false`)

#### Future Backend Integration:
```typescript
// The QuestionCard component is already prepared for dynamic data
// When backend is implemented, simply update the API response:

interface Question {
  // ... existing properties
  isStaged: boolean; // Will be populated from backend stage status
  // ... other properties
}

// API endpoint could be:
// GET /api/events/{eventId}/questions - returns questions with current stage status
// PUT /api/questions/{questionId}/stage - moderator action to stage/unstage questions
```

### Testing Scenarios

#### Visual Testing:
1. **Staged Question Display**: Question 1 shows blue border, blue background, and "🎭 On Stage" badge
2. **Non-staged Questions**: Questions 2-4 show normal styling without stage indicators
3. **Responsive Design**: Stage indicators work properly on mobile and desktop
4. **Tab Navigation**: Stage indicators persist across "All Questions" and "Answered" tabs

#### User Flow Testing:
1. User opens event page → sees Question 1 prominently highlighted as staged
2. User scrolls through questions → easily identifies which one is being discussed
3. User submits new question → new question appears without stage indicator

### Design Considerations

#### Color Scheme:
- **Blue Theme**: Consistent with app's primary color scheme
- **Contrast**: Sufficient contrast for accessibility
- **Hierarchy**: Blue indicates active/important status (consistent with other UI elements)

#### Icon Choice:
- **Theater Masks (🎭)**: Universally understood symbol for "on stage" or "performance"
- **Appropriate Size**: Large enough to be visible, small enough to not dominate
- **Platform Support**: Emoji renders consistently across devices

#### Layout Impact:
- **Non-disruptive**: Stage indicators don't affect question card layout
- **Scannable**: Users can quickly scan to find staged question
- **Scalable**: Design works with varying question text lengths

### Future Enhancements

#### Potential Improvements:
1. **Animation**: Subtle pulse or glow effect for staged questions
2. **Auto-scroll**: Automatically scroll to staged question when page loads
3. **Stage Transitions**: Smooth animations when stage status changes
4. **Multiple Stages**: Support for multiple presenters with different stage indicators
5. **Stage History**: Show recently staged questions with different styling

#### Real-time Updates:
When backend is implemented:
1. **WebSocket Integration**: Real-time updates when moderators change staged questions
2. **Polling Fallback**: Regular API calls to sync stage status
3. **Optimistic Updates**: Immediate UI feedback for stage changes

## Conclusion

The user stage indicator provides clear, intuitive feedback about which question is currently being discussed. The implementation leverages existing components and styling patterns, ensuring consistency with the overall app design. The feature is ready for backend integration with minimal changes required to the frontend code.

Users can now easily follow along with AMA sessions by knowing exactly which question is being addressed, improving engagement and comprehension of the discussion flow.
