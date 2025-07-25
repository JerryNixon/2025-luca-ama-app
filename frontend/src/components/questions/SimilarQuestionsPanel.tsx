// SimilarQuestionsPanel Component - AI-powered similar question detection
// Displays similar questions found by Microsoft Fabric AI to prevent duplicates

import React from 'react';
import { FiArrowUp, FiZap, FiLoader, FiAlertCircle, FiCheckCircle } from 'react-icons/fi';
import { SimilarQuestion, SimilarQuestionsResponse } from '@/types';

/**
 * Interface defining the props for SimilarQuestionsPanel component
 */
interface SimilarQuestionsPanelProps {
  /** The similar questions data from AI analysis */
  similarData: SimilarQuestionsResponse | null;
  /** Whether the AI analysis is currently loading (shows main spinner) */
  isLoading: boolean;
  /** Whether the AI is updating results in background (shows subtle indicator) */
  isBackgroundUpdating?: boolean;
  /** Whether to show the panel (for animation control) */
  isVisible: boolean;
  /** Callback when user chooses to upvote a similar question instead of posting new */
  onUpvoteSimilar: (questionId: string) => Promise<void>;
  /** Callback when user decides to post their question anyway */
  onContinueWithNew: () => void;
  /** Optional loading states for individual upvote actions */
  upvotingQuestions?: Set<string>;
}

/**
 * SimilarQuestionsPanel Component
 * 
 * A sleek, animated panel that appears below the question textarea when
 * Microsoft Fabric AI detects similar existing questions. Provides users
 * with the option to upvote existing questions instead of creating duplicates.
 * 
 * Features:
 * - Smooth slide-down animation
 * - AI similarity scores with visual indicators
 * - One-click upvoting of similar questions
 * - Clean, modern design matching app aesthetics
 * - Loading states and error handling
 * - Performance indicators from Fabric AI
 * 
 * @param props - SimilarQuestionsPanelProps containing data and callbacks
 * @returns JSX element representing the similar questions panel
 */
export default function SimilarQuestionsPanel({
  similarData,
  isLoading,
  isBackgroundUpdating = false,
  isVisible,
  onUpvoteSimilar,
  onContinueWithNew,
  upvotingQuestions = new Set()
}: SimilarQuestionsPanelProps) {
  
  // Don't render anything if not visible and not loading
  if (!isVisible && !isLoading) {
    return null;
  }

  /**
   * Get visual indicator for similarity score
   */
  const getSimilarityIndicator = (score: number) => {
    if (score >= 0.9) return { color: 'text-red-600', bg: 'bg-red-50', label: 'Very Similar', icon: '🔥' };
    if (score >= 0.8) return { color: 'text-orange-600', bg: 'bg-orange-50', label: 'Similar', icon: '⚡' };
    if (score >= 0.7) return { color: 'text-yellow-600', bg: 'bg-yellow-50', label: 'Somewhat Similar', icon: '💡' };
    return { color: 'text-blue-600', bg: 'bg-blue-50', label: 'Related', icon: '🔍' };
  };

  /**
   * Handle upvote click with loading state
   */
  const handleUpvote = async (questionId: string) => {
    try {
      await onUpvoteSimilar(questionId);
    } catch (error) {
      console.error('Failed to upvote similar question:', error);
      // Error handling could be enhanced with toast notifications
    }
  };

  return (
    <div className={`transition-all duration-300 ease-in-out overflow-hidden ${
      isVisible ? 'max-h-96 opacity-100 mt-4' : 'max-h-0 opacity-0 mt-0'
    }`}>
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 shadow-sm">
        
        {/* Panel Header */}
        <div className="px-6 py-4 border-b border-blue-200 bg-white bg-opacity-60 rounded-t-lg">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <FiZap className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold text-gray-900">
                {isLoading ? 'Finding Similar Questions...' : 'Similar Questions Found'}
              </h3>
              {/* Subtle background updating indicator */}
              {isBackgroundUpdating && !isLoading && (
                <div className="flex items-center space-x-1 text-blue-500">
                  <FiLoader className="w-3 h-3 animate-spin" />
                  <span className="text-xs font-medium">Updating...</span>
                </div>
              )}
            </div>
            
            {/* AI Method Indicator */}
            {similarData && (
              <div className="flex items-center space-x-2">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                  🤖 {similarData.method === 'fabric_ai' ? 'Fabric AI' : 'Fallback'}
                </span>
                {similarData.method === 'fabric_ai' && (
                  <span className="text-xs text-green-600 font-medium">
                    ✨ Enhanced Analysis
                  </span>
                )}
              </div>
            )}
          </div>
          
          {/* Subtitle */}
          <p className="text-sm text-gray-600 mt-1">
            {isLoading 
              ? 'Our AI is analyzing your question for similarities...'
              : 'Consider upvoting an existing question instead of posting a duplicate'
            }
          </p>
        </div>

        {/* Panel Content */}
        <div className="p-6">
          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center space-x-3">
                <FiLoader className="w-5 h-5 text-blue-600 animate-spin" />
                <span className="text-gray-600">Analyzing with Microsoft Fabric AI...</span>
              </div>
            </div>
          )}

          {/* Similar Questions List */}
          {!isLoading && similarData && similarData.similar_questions.length > 0 && (
            <div className="space-y-3">
              {similarData.similar_questions.map((question, index) => {
                const similarity = getSimilarityIndicator(question.similarity_score);
                const isUpvoting = upvotingQuestions.has(question.id);
                
                return (
                  <div 
                    key={question.id}
                    className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      {/* Question Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-2">
                          {/* Similarity Score Badge */}
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${similarity.bg} ${similarity.color}`}>
                            <span className="mr-1">{similarity.icon}</span>
                            {Math.round(question.similarity_score * 100)}% {similarity.label}
                          </span>
                          
                          {/* Vote Count */}
                          <span className="text-sm font-medium text-gray-700">
                            {question.upvote_count} votes
                          </span>
                          
                          {/* AI Metadata */}
                          {question.ai_sentiment && (
                            <span className="text-xs text-gray-500">
                              {question.ai_sentiment === 'positive' ? '😊' : 
                               question.ai_sentiment === 'negative' ? '😟' : '😐'} 
                              {question.ai_sentiment}
                            </span>
                          )}
                        </div>
                        
                        {/* Question Text */}
                        <p className="text-gray-900 text-sm leading-relaxed">
                          {question.text}
                        </p>
                        
                        {/* Question Metadata */}
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span>
                            {new Date(question.created_at).toLocaleDateString()}
                          </span>
                          {question.ai_category && (
                            <span className="px-2 py-0.5 bg-gray-100 rounded">
                              {question.ai_category}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Upvote Button */}
                      <div className="ml-4 flex-shrink-0">
                        <button
                          onClick={() => handleUpvote(question.id)}
                          disabled={isUpvoting}
                          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
                        >
                          {isUpvoting ? (
                            <>
                              <FiLoader className="w-4 h-4 animate-spin" />
                              <span>Upvoting...</span>
                            </>
                          ) : (
                            <>
                              <FiArrowUp className="w-4 h-4" />
                              <span>Upvote</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* No Similar Questions Found */}
          {!isLoading && similarData && similarData.similar_questions.length === 0 && (
            <div className="text-center py-6">
              <FiCheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <h4 className="text-sm font-medium text-gray-900 mb-1">No Similar Questions Found</h4>
              <p className="text-xs text-gray-600">Your question appears to be unique!</p>
            </div>
          )}

          {/* Error State - Show when method is fallback indicating AI failure */}
          {!isLoading && similarData && similarData.method === 'fallback' && (
            <div className="text-center py-6">
              <FiAlertCircle className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
              <h4 className="text-sm font-medium text-gray-900 mb-1">AI Analysis Unavailable</h4>
              <p className="text-xs text-gray-600">Similarity detection is temporarily offline</p>
            </div>
          )}

          {/* Action Buttons */}
          {!isLoading && similarData && similarData.similar_questions.length > 0 && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
              {/* AI Performance Info */}
              <div className="text-xs text-gray-500">
                <span>Powered by Microsoft Fabric AI</span>
                {similarData.performance_info && (
                  <span className="ml-2">
                    • {similarData.performance_info.vector_dimension}D vectors
                  </span>
                )}
              </div>
              
              {/* Continue Button */}
              <button
                onClick={onContinueWithNew}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                📝 Post New Question Anyway
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
