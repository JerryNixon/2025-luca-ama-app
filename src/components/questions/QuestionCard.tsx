import React from 'react';
import { FiThumbsUp, FiStar, FiMessageSquare, FiMoreVertical, FiUser, FiClock } from 'react-icons/fi';
import { Question, UserRole } from '@/types';
import { format } from 'date-fns';

interface QuestionCardProps {
  question: Question;
  userRole: UserRole;
  onUpvote?: () => void;
  onStar?: () => void;
  onStage?: () => void;
  onAnswer?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  showActions?: boolean;
}

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
  const canModerate = userRole === 'moderator' || userRole === 'presenter';
  const isOwner = false; // This would be determined by comparing question.author.id with current user id

  return (
    <div className={`card hover:shadow-lg transition-shadow duration-200 ${
      question.isStaged ? 'ring-2 ring-blue-500 bg-blue-50' : ''
    }`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Question Header */}
          <div className="flex items-center gap-2 mb-3">
            <div className="flex items-center gap-2">
              <FiUser className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">
                {question.isAnonymous ? 'Anonymous' : question.author.name}
              </span>
            </div>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <FiClock className="w-3 h-3" />
              <span>{format(question.createdAt, 'MMM dd, HH:mm')}</span>
            </div>
            
            {/* Status badges */}
            <div className="flex gap-1">
              {question.isAnswered && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                  Answered
                </span>
              )}
              {question.isStarred && (
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
                  ⭐ Starred
                </span>
              )}
              {question.isStaged && (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                  🎭 On Stage
                </span>
              )}
            </div>
          </div>

          {/* Question Text */}
          <p className="text-gray-900 mb-3">{question.text}</p>

          {/* Tags */}
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

          {/* Presenter Notes (only visible to moderators/presenters) */}
          {canModerate && question.presenterNotes && (
            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-medium text-yellow-800">Presenter Notes:</span>
              </div>
              <p className="text-sm text-yellow-700">{question.presenterNotes}</p>
            </div>
          )}

          {/* AI Summary */}
          {question.aiSummary && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-medium text-blue-800">AI Summary:</span>
              </div>
              <p className="text-sm text-blue-700">{question.aiSummary}</p>
            </div>
          )}
        </div>

        {/* Actions */}
        {showActions && (
          <div className="flex items-center gap-2 ml-4">
            {/* Upvote */}
            <button
              onClick={onUpvote}
              className={`flex items-center gap-1 px-2 py-1 rounded-lg transition-colors ${
                question.hasUserUpvoted
                  ? 'bg-blue-100 text-blue-700'
                  : 'hover:bg-gray-100 text-gray-600'
              }`}
              disabled={isOwner}
              title={isOwner ? "Can't upvote your own question" : "Upvote this question"}
            >
              <FiThumbsUp className="w-4 h-4" />
              <span className="text-sm font-medium">{question.upvotes}</span>
            </button>

            {/* Moderator/Presenter Actions */}
            {canModerate && (
              <>
                <button
                  onClick={onStar}
                  className={`p-2 rounded-lg transition-colors ${
                    question.isStarred
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'hover:bg-gray-100 text-gray-600'
                  }`}
                  title={question.isStarred ? "Remove star" : "Star question"}
                >
                  <FiStar className="w-4 h-4" />
                </button>

                <button
                  onClick={onStage}
                  className={`p-2 rounded-lg transition-colors ${
                    question.isStaged
                      ? 'bg-blue-100 text-blue-700'
                      : 'hover:bg-gray-100 text-gray-600'
                  }`}
                  title={question.isStaged ? "Remove from stage" : "Put on stage"}
                >
                  🎭
                </button>

                <button
                  onClick={onAnswer}
                  className={`p-2 rounded-lg transition-colors ${
                    question.isAnswered
                      ? 'bg-green-100 text-green-700'
                      : 'hover:bg-gray-100 text-gray-600'
                  }`}
                  title={question.isAnswered ? "Mark as unanswered" : "Mark as answered"}
                >
                  ✓
                </button>
              </>
            )}

            {/* Owner Actions */}
            {isOwner && !question.isAnswered && (
              <div className="relative">
                <button
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600"
                  title="More options"
                >
                  <FiMoreVertical className="w-4 h-4" />
                </button>
                {/* Dropdown menu would go here */}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Grouped Questions */}
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
