// QuestionCard Component - Interactive card displaying question information and actions
// This component renders individual questions with role-based actions and status indicators

// Import React for component creation
import React from 'react';
// Import Feather icons for action buttons and visual indicators
import { FiThumbsUp, FiStar, FiMessageSquare, FiMoreVertical, FiUser, FiClock } from 'react-icons/fi';
// Import TypeScript types for type safety
import { Question, UserRole } from '@/types';
// Import date formatting utility
import { format } from 'date-fns';

/**
 * Interface defining the props that QuestionCard component expects
 * Provides clear documentation of all possible interactions and callbacks
 */
interface QuestionCardProps {
  question: Question;                    // Question data to display
  userRole: UserRole;                    // Current user's role for permission checks
  onUpvote?: () => void;                 // Callback for upvoting the question
  onStar?: () => void;                   // Callback for starring/unstarring (moderators only)
  onStage?: () => void;                  // Callback for staging/unstaging (moderators only)
  onAnswer?: () => void;                 // Callback for marking as answered (moderators only)
  onEdit?: () => void;                   // Callback for editing question (owners only)
  onDelete?: () => void;                 // Callback for deleting question (owners only)
  showActions?: boolean;                 // Whether to show action buttons (default: true)
}

/**
 * QuestionCard Component
 * 
 * A comprehensive card component for displaying questions with interactive features.
 * Features:
 * - Author information with optional anonymity
 * - Question text with tag support
 * - Status indicators (answered, starred, staged)
 * - Role-based action buttons
 * - Upvoting functionality with visual feedback
 * - Presenter notes (visible to moderators only)
 * - AI summary integration
 * - Similar question grouping
 * 
 * @param props - QuestionCardProps containing question data and callbacks
 * @returns JSX element representing a question card
 */
export default function QuestionCard({
  question,
  userRole,
  onUpvote,
  onStar,
  onStage,
  onAnswer,
  onEdit,
  onDelete,
  showActions = true
}: QuestionCardProps) {
  // Determine if current user can moderate (star, stage, mark as answered)
  const canModerate = userRole === 'moderator' || userRole === 'presenter';
  
  // Determine if current user owns this question (for edit/delete permissions)
  // Note: This would typically compare question.author.id with current user ID
  // Currently hardcoded to false as user comparison logic is not implemented
  const isOwner = false;

  return (
    <div className={`card hover:shadow-lg transition-shadow duration-200 ${
      // Special styling for staged questions - blue border and background
      question.isStaged ? 'ring-2 ring-blue-500 bg-blue-50' : ''
    }`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          
          {/* Question Header - Author, timestamp, and status badges */}
          <div className="flex items-center gap-2 mb-3">
            {/* Author Information */}
            <div className="flex items-center gap-2">
              <FiUser className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">
                {/* Show "Anonymous" if question is anonymous, otherwise show author name */}
                {question.isAnonymous ? 'Anonymous' : question.author.name}
              </span>
            </div>
            
            {/* Timestamp */}
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <FiClock className="w-3 h-3" />
              <span>{format(question.createdAt, 'MMM dd, HH:mm')}</span>
            </div>
            
            {/* Status Badges */}
            <div className="flex gap-1">
              {/* Answered Badge - Green background when question has been answered */}
              {question.isAnswered && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                  Answered
                </span>
              )}
              
              {/* Starred Badge - Yellow background for important questions */}
              {question.isStarred && (
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
                  ⭐ Starred
                </span>
              )}
              
              {/* Staged Badge - Blue background for questions currently being presented */}
              {question.isStaged && (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                  🎭 On Stage
                </span>
              )}
            </div>
          </div>

          {/* Question Text - Main content of the question */}
          <p className="text-gray-900 mb-3">{question.text}</p>

          {/* Tags - Categorization and filtering aids */}
          {question.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {question.tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* Presenter Notes - Only visible to moderators and presenters */}
          {/* These are private notes to help with question preparation */}
          {canModerate && question.presenterNotes && (
            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-medium text-yellow-800">Presenter Notes:</span>
              </div>
              <p className="text-sm text-yellow-700">{question.presenterNotes}</p>
            </div>
          )}

          {/* AI Summary - Machine-generated summary or analysis */}
          {/* Helps presenters quickly understand complex questions */}
          {question.aiSummary && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-medium text-blue-800">AI Summary:</span>
              </div>
              <p className="text-sm text-blue-700">{question.aiSummary}</p>
            </div>
          )}
        </div>

        {/* Action Buttons Section */}
        {showActions && (
          <div className="flex items-center gap-2 ml-4">
            
            {/* Upvote Button - Available to all users except question owners */}
            <button
              onClick={onUpvote}
              className={`flex items-center gap-1 px-2 py-1 rounded-lg transition-colors ${
                // Different styling based on whether user has already upvoted
                question.hasUserUpvoted
                  ? 'bg-blue-100 text-blue-700'    // Active state - user has upvoted
                  : 'hover:bg-gray-100 text-gray-600'  // Default state - can upvote
              }`}
              disabled={isOwner}  // Prevent users from upvoting their own questions
              title={isOwner ? "Can't upvote your own question" : "Upvote this question"}
            >
              <FiThumbsUp className="w-4 h-4" />
              <span className="text-sm font-medium">{question.upvotes}</span>
            </button>

            {/* Moderator and Presenter Actions */}
            {/* These actions are only available to users with moderation privileges */}
            {canModerate && (
              <>
                {/* Star/Unstar Button - Mark questions as important */}
                <button
                  onClick={onStar}
                  className={`p-2 rounded-lg transition-colors ${
                    question.isStarred
                      ? 'bg-yellow-100 text-yellow-700'    // Active - question is starred
                      : 'hover:bg-gray-100 text-gray-600'  // Inactive - can star
                  }`}
                  title={question.isStarred ? "Remove star" : "Star question"}
                >
                  <FiStar className="w-4 h-4" />
                </button>

                {/* Stage/Unstage Button - Control which question is currently being presented */}
                <button
                  onClick={onStage}
                  className={`p-2 rounded-lg transition-colors ${
                    question.isStaged
                      ? 'bg-blue-100 text-blue-700'        // Active - question is on stage
                      : 'hover:bg-gray-100 text-gray-600'  // Inactive - can stage
                  }`}
                  title={question.isStaged ? "Remove from stage" : "Put on stage"}
                >
                  🎭
                </button>

                {/* Answer/Unanswer Button - Mark questions as answered */}
                <button
                  onClick={onAnswer}
                  className={`p-2 rounded-lg transition-colors ${
                    question.isAnswered
                      ? 'bg-green-100 text-green-700'      // Active - question is answered
                      : 'hover:bg-gray-100 text-gray-600'  // Inactive - can mark as answered
                  }`}
                  title={question.isAnswered ? "Mark as unanswered" : "Mark as answered"}
                >
                  ✓
                </button>
              </>
            )}

            {/* Owner Actions - Edit and delete options for question owners */}
            {/* Only shown to question owners and only for unanswered questions */}
            {isOwner && !question.isAnswered && (
              <div className="relative">
                <button
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600"
                  title="More options"
                >
                  <FiMoreVertical className="w-4 h-4" />
                </button>
                {/* Note: Dropdown menu would be implemented here for edit/delete options */}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Grouped Questions Section */}
      {/* Shows when this question has been grouped with similar questions */}
      {question.groupedQuestions && question.groupedQuestions.length > 0 && (
        <div className="mt-4 border-t pt-4">
          <button className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900">
            <span>+</span>
            <span>{question.groupedQuestions.length} similar questions</span>
          </button>
        </div>
      )}
    </div>
  );
}
