// QuestionCard Component - Interactive card displaying question information and actions
// This component renders individual questions with role-based actions and status indicators

// Import React for component creation
import React, { useState } from 'react';
// Import Feather icons for action buttons and visual indicators
import { FiStar, FiMessageSquare, FiMoreVertical, FiUser, FiClock, FiArrowUp, FiEyeOff } from 'react-icons/fi';
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
  isVoting?: boolean;                    // Whether vote action is in progress
  isStarring?: boolean;                  // Whether star action is in progress
  isStaging?: boolean;                   // Whether stage action is in progress
  isAnswering?: boolean;                 // Whether answer action is in progress
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
  showActions = true,
  isVoting = false,
  isStarring = false,
  isStaging = false,
  isAnswering = false
}: QuestionCardProps) {
  // Determine if current user can moderate (star, stage, mark as answered)
  const canModerate = userRole === 'moderator' || userRole === 'presenter';
  
  // Determine if current user owns this question (for edit/delete permissions)
  // Note: This would typically compare question.author.id with current user ID
  // Currently hardcoded to false as user comparison logic is not implemented
  const isOwner = false;
  return (
    <div className={`card fade-in hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 ${
      // Special styling for staged questions - blue border and background with glow effect
      question.is_staged ? 'ring-2 ring-blue-500 bg-blue-50 shadow-blue-500/20 shadow-lg' : ''
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
                {question.is_anonymous ? 'Anonymous' : question.author.name}
              </span>
            </div>
            
            {/* Timestamp */}
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <FiClock className="w-3 h-3" />
              <span>
                {(() => {
                  try {
                    return format(new Date(question.created_at), 'MMM dd, HH:mm');
                  } catch (error) {
                    return 'Invalid date';
                  }
                })()}
              </span>
            </div>
            
            {/* Status Badges */}
            <div className="flex gap-1">
              {/* Answered Badge - Green background when question has been answered */}
              {question.is_answered && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                  Answered
                </span>
              )}
              
              {/* Starred Badge - Yellow background for important questions */}
              {question.is_starred && (
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
                  ⭐ Starred
                </span>
              )}
              
              {/* Staged Badge - Blue background for questions currently being presented */}
              {question.is_staged && (
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
          {canModerate && question.presenter_notes && (
            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-medium text-yellow-800">Presenter Notes:</span>
              </div>
              <p className="text-sm text-yellow-700">{question.presenter_notes}</p>
            </div>
          )}

          {/* AI Summary - Machine-generated summary or analysis */}
          {/* Helps presenters quickly understand complex questions */}
          {question.ai_summary && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-medium text-blue-800">AI Summary:</span>
              </div>
              <p className="text-sm text-blue-700">{question.ai_summary}</p>
            </div>
          )}
        </div>

        {/* Action Buttons Section */}
        {showActions && (
          <div className="flex items-center gap-2 ml-4">              {/* Upvote Button - Available to all users except question owners */}
            <button
              onClick={onUpvote}
              className={`flex flex-col items-center p-3 rounded-lg transition-all duration-200 transform hover:scale-105 active:scale-95 ${
                // Different styling based on whether user has already upvoted
                question.has_user_upvoted
                  ? 'bg-primary-100 text-primary-600 shadow-md pulse-on-hover'    // Active state - user has upvoted
                  : 'bg-gray-50 hover:bg-gray-100 text-gray-600 hover:shadow-md'  // Default state - can upvote
              } ${isVoting ? 'opacity-50 cursor-not-allowed' : ''}`}
              disabled={isOwner || isVoting}  // Prevent users from upvoting their own questions or while loading
              title={isVoting ? "Processing vote..." : (isOwner ? "Can't upvote your own question" : (question.has_user_upvoted ? "Remove your vote" : "Vote for this question"))}
            >
              {isVoting ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              ) : (
                <FiArrowUp className={`w-5 h-5 transition-transform duration-200 ${question.has_user_upvoted ? 'text-primary-600' : ''}`} />
              )}
              <span className={`font-semibold text-lg transition-colors duration-200 ${question.has_user_upvoted ? 'text-primary-600' : ''}`}>{question.upvotes}</span>
              <span className={`text-xs transition-colors duration-200 ${question.has_user_upvoted ? 'text-primary-500' : ''}`}>votes</span>
            </button>

            {/* Moderator and Presenter Actions */}
            {/* These actions are only available to users with moderation privileges */}
            {canModerate && (
              <>
                {/* Star/Unstar Button - Mark questions as important */}
                <button
                  onClick={onStar}
                  disabled={isStarring}
                  className={`p-2 rounded-lg transition-colors ${
                    question.is_starred
                      ? 'bg-yellow-100 text-yellow-700'    // Active - question is starred
                      : 'hover:bg-gray-100 text-gray-600'  // Inactive - can star
                  } ${isStarring ? 'opacity-50 cursor-not-allowed' : ''}`}
                  title={isStarring ? "Processing..." : (question.is_starred ? "Remove star" : "Star question")}
                >
                  {isStarring ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600"></div>
                  ) : (
                    <FiStar className={`w-4 h-4 ${question.is_starred ? 'fill-current' : ''}`} />
                  )}
                </button>

                {/* Stage/Unstage Button - Control which question is currently being presented */}
                <button
                  onClick={onStage}
                  disabled={isStaging}
                  className={`p-2 rounded-lg transition-colors ${
                    question.is_staged
                      ? 'bg-blue-100 text-blue-700'        // Active - question is on stage
                      : 'hover:bg-gray-100 text-gray-600'  // Inactive - can stage
                  } ${isStaging ? 'opacity-50 cursor-not-allowed' : ''}`}
                  title={isStaging ? "Processing..." : (question.is_staged ? "Remove from stage" : "Put on stage")}
                >
                  {isStaging ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  ) : (
                    '🎭'
                  )}
                </button>

                {/* Answer/Unanswer Button - Mark questions as answered */}
                <button
                  onClick={onAnswer}
                  disabled={isAnswering}
                  className={`p-2 rounded-lg transition-colors ${
                    question.is_answered
                      ? 'bg-green-100 text-green-700'      // Active - question is answered
                      : 'hover:bg-gray-100 text-gray-600'  // Inactive - can mark as answered
                  } ${isAnswering ? 'opacity-50 cursor-not-allowed' : ''}`}
                  title={isAnswering ? "Processing..." : (question.is_answered ? "Mark as unanswered" : "Mark as answered")}
                >
                  {isAnswering ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600"></div>
                  ) : (
                    '✓'
                  )}
                </button>
              </>
            )}

            {/* Owner Actions - Edit and delete options for question owners */}
            {/* Only shown to question owners and only for unanswered questions */}
            {isOwner && !question.is_answered && (
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
        )}      </div>      {/* Grouped Questions Section */}
      {/* Shows when this question has been grouped with similar questions */}
      <SimilarQuestionsSection 
        question={question}
        isModeratorView={userRole === 'moderator' || userRole === 'presenter'}
        onUpvote={onUpvote || (() => {})}
      />
    </div>
  );
}

/**
 * Similar Questions Section Component
 * 
 * Displays a collapsible section for similar/grouped questions.
 * Features:
 * - Toggle expand/collapse functionality
 * - Shows grouped questions count
 * - Displays similar questions in a compact format
 * - Supports voting on similar questions
 */
interface SimilarQuestionsSectionProps {
  question: Question;
  isModeratorView: boolean;
  onUpvote: (questionId: string) => void;
}

function SimilarQuestionsSection({ question, isModeratorView, onUpvote }: SimilarQuestionsSectionProps) {
  // State to track if similar questions are expanded
  const [isExpanded, setIsExpanded] = useState(false);

  // Don't render if no grouped questions
  if (!question.grouped_questions || question.grouped_questions.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border-t pt-4">
      {/* Toggle Button */}
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
      >
        <span className={`transition-transform duration-200 ${isExpanded ? 'rotate-45' : ''}`}>
          {isExpanded ? '−' : '+'}
        </span>
        <span>{question.grouped_questions.length} similar question{question.grouped_questions.length > 1 ? 's' : ''}</span>
      </button>

      {/* Expanded Similar Questions */}
      {isExpanded && (
        <div className="mt-3 space-y-3 pl-4 border-l-2 border-gray-100">
          {question.grouped_questions.map((similarQuestion) => (
            <div key={similarQuestion.id} className="bg-gray-50 rounded-lg p-4">
              <div className="flex space-x-3">                {/* Vote Button for Similar Questions */}
                <div className="flex flex-col items-center">
                  <button
                    onClick={() => onUpvote(similarQuestion.id)}
                    className={`flex flex-col items-center p-2 rounded-lg transition-colors ${
                      similarQuestion.has_user_upvoted
                        ? 'bg-primary-100 text-primary-600'
                        : 'bg-white hover:bg-gray-100 text-gray-600'
                    }`}
                    title={similarQuestion.has_user_upvoted ? "Remove your vote" : "Vote for this question"}
                  >
                    <FiArrowUp className="w-4 h-4" />
                    <span className="font-medium text-sm">{similarQuestion.upvotes}</span>
                    <span className="text-xs">votes</span>
                  </button>
                </div>

                {/* Similar Question Content */}
                <div className="flex-1">
                  <p className="text-gray-900 text-sm leading-relaxed mb-2">
                    {similarQuestion.text}
                  </p>
                  
                  <div className="flex items-center text-xs text-gray-500 space-x-2">
                    <div className="flex items-center">
                      {similarQuestion.is_anonymous ? (
                        <>
                          <FiEyeOff className="w-3 h-3 mr-1" />
                          <span>Anonymous</span>
                        </>
                      ) : (
                        <>
                          <FiUser className="w-3 h-3 mr-1" />
                          <span>{similarQuestion.author.name}</span>
                        </>
                      )}
                    </div>
                    <span>•</span>
                    <span>{new Date(similarQuestion.created_at).toLocaleDateString()}</span>
                    
                    {/* Status Badge for Similar Questions */}
                    {similarQuestion.is_answered && (
                      <>
                        <span>•</span>
                        <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">
                          Answered
                        </span>
                      </>
                    )}
                    
                    {isModeratorView && similarQuestion.is_starred && (
                      <>
                        <span>•</span>
                        <span className="text-yellow-600" title="Starred">⭐</span>
                      </>
                    )}
                  </div>

                  {/* Tags for Similar Questions */}
                  {similarQuestion.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {similarQuestion.tags.map((tag, index) => (
                        <span key={index} className="bg-gray-200 text-gray-700 px-2 py-0.5 rounded text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
