# Single Question Staging Implementation

## Overview
Implemented single-question staging functionality for the moderator/presenter view in the Luca AMA App. Only one question can be on stage at any given time.

## Implementation Details

### Feature Requirements
- ✅ Only one question can be staged at a time
- ✅ When staging a new question, automatically unstage the currently staged question
- ✅ Staging button toggles correctly (stage/unstage)
- ✅ Stage tab shows only the currently staged question

### Technical Implementation

#### Updated `handleStage` Function
```typescript
/**
 * Handle staging question (moderator/presenter only)
 * Only one question can be staged at a time
 */
const handleStage = (questionId: string) => {
  if (!canModerate) return;
  
  setQuestions(prev => prev.map(q => {
    if (q.id === questionId) {
      // Toggle the clicked question's stage status
      return { ...q, isOnStage: !q.isOnStage };
    } else {
      // If we're staging a new question, unstage all others
      // If we're unstaging the current question, leave others as they are
      const clickedQuestion = prev.find(question => question.id === questionId);
      if (clickedQuestion && !clickedQuestion.isOnStage) {
        // We're staging a new question, so unstage this one
        return { ...q, isOnStage: false };
      }
      // We're unstaging, so leave this question's status unchanged
      return q;
    }
  }));
};
```

### Logic Flow

#### When Staging a New Question:
1. User clicks "Put on Stage" button for Question A
2. System checks if Question A is currently staged (`!clickedQuestion.isOnStage`)
3. If not staged, Question A gets staged (`isOnStage: true`)
4. All other questions get unstaged (`isOnStage: false`)
5. Stage tab now shows only Question A

#### When Unstaging Current Question:
1. User clicks "Remove from Stage" button for currently staged Question A
2. Question A gets unstaged (`isOnStage: false`)
3. All other questions remain unchanged
4. Stage tab becomes empty

#### Visual Feedback:
- **Stage Button**: Shows "eye" icon, changes color when question is staged
- **Stage Tab**: Displays count of staged questions (0 or 1)
- **Question Header**: Shows "Currently on stage" indicator for staged question

### User Experience

#### For Moderators and Presenters:
1. **Staging**: Click the eye icon (👁) to put a question on stage
2. **Automatic Unstaging**: Previous staged question automatically gets removed
3. **Unstaging**: Click the eye icon again to remove from stage
4. **Stage View**: Switch to "On Stage" tab to see only the current staged question

#### Visual Indicators:
- **Staged Question**: Blue background header with "Currently on stage" text
- **Stage Button**: Blue background when question is staged, gray when not
- **Stage Tab Badge**: Shows "0" or "1" to indicate staged question count

### Benefits

1. **Clear Focus**: Only one question is highlighted at a time
2. **No Confusion**: Automatic unstaging prevents multiple staged questions
3. **Better Workflow**: Moderators can easily manage what's currently being discussed
4. **Visual Clarity**: Clear indicators show which question is active

### Files Modified

- `frontend/src/app/events/[id]/page.tsx` - Updated `handleStage` function

### Testing Scenarios

#### Test Case 1: Stage New Question
1. Start with Question 1 staged
2. Click stage button on Question 2
3. Expected: Question 1 unstaged, Question 2 staged

#### Test Case 2: Unstage Current Question
1. Start with Question 1 staged
2. Click stage button on Question 1
3. Expected: Question 1 unstaged, no questions staged

#### Test Case 3: Stage Tab Filtering
1. Stage Question 2
2. Switch to "On Stage" tab
3. Expected: Only Question 2 visible in list

#### Test Case 4: Multiple Stage Attempts
1. Stage Question 1
2. Stage Question 2
3. Stage Question 3
4. Expected: Only Question 3 is staged at the end

### Future Enhancements

1. **Confirmation Dialog**: Add confirmation when switching staged questions
2. **Animation**: Smooth transitions when questions move in/out of stage
3. **Stage History**: Track which questions were previously staged
4. **Auto-Stage**: Automatically stage highest-voted unanswered questions
5. **Stage Timer**: Add time tracking for how long questions stay staged

## Conclusion

The single-question staging feature provides a clean, intuitive way for moderators and presenters to manage which question is currently being discussed. The automatic unstaging ensures there's never confusion about which question is active, improving the overall AMA experience.
