'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../../../contexts/AuthContext';
import { useRouter, useParams } from 'next/navigation';
import { Event, Question, CreateQuestionForm } from '../../../../types';
import { FiArrowUp, FiSend, FiUser, FiEyeOff } from 'react-icons/fi';
import QuestionCard from '../../../../components/questions/QuestionCard';
import { eventService } from '../../../../services/eventService';
import { questionService } from '../../../../services/questionService';

/**
 * User Event View Page Component
 * 
 * This page provides a user-focused interface for participating in AMA events.
 * Unlike the moderator view, this shows:
 * - Simplified question list (no moderation tools)
 * - Question submission form with anonymous option
 * - Basic filtering (All/Answered tabs only)
 * - Vote functionality
 * 
 * Features:
 * - Combined question list and submission form on one page
 * - Anonymous posting option
 * - Real-time voting
 * - Clean, user-friendly interface
 * - Responsive design matching app theme
 */

// Question filter types for user view (simplified)
type UserQuestionFilter = 'all' | 'answered';

// Interface for question with user-specific data
interface UserQuestion extends Question {
  hasVoted?: boolean;
}

export default function UserEventViewPage() {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const params = useParams();
  const eventId = params.id as string;

  // Component state
  const [event, setEvent] = useState<Event | null>(null);
  const [questions, setQuestions] = useState<UserQuestion[]>([]);
  const [filteredQuestions, setFilteredQuestions] = useState<UserQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<UserQuestionFilter>('all');

  // Question submission form state
  const [questionText, setQuestionText] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Form validation
  const [showError, setShowError] = useState(false);

  /**
   * Load event data and questions for user view
   */
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Load event data regardless of role - let the backend handle permissions
    loadEventData();
  }, [eventId, isAuthenticated, router]);

  /**
   * Filter questions based on active tab
   */
  useEffect(() => {
    filterQuestions();
  }, [questions, activeFilter]);

  /**
   * Load event and question data (user view)
   */
  const loadEventData = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('Loading event data for eventId:', eventId);
      
      // Load event data from API
      const eventData = await eventService.getEvent(eventId);
      console.log('Event data loaded:', eventData);
      
      // Load questions for this event
      const questionsData = await questionService.getQuestions(eventId);
      console.log('Questions data loaded:', questionsData);
      
      // Convert questions to UserQuestion format with hasVoted info
      const userQuestions: UserQuestion[] = questionsData.map(q => ({
        ...q,
        hasVoted: q.has_user_upvoted || false
      }));

      setEvent(eventData);
      setQuestions(userQuestions);
    } catch (err) {
      console.error('Event loading error:', err);
      // More specific error messages
      if (err instanceof Error) {
        setError(`Failed to load event: ${err.message}`);
      } else {
        setError('Failed to load event data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Filter questions for user view
   */
  const filterQuestions = () => {
    let filtered = [...questions];

    // Apply tab filter
    switch (activeFilter) {
      case 'answered':
        filtered = filtered.filter(q => q.is_answered);
        break;
      case 'all':
      default:
        // Show all questions for users
        break;
    }

    // Sort by upvotes (descending) then by creation date (newest first)
    filtered.sort((a, b) => {
      if (b.upvotes !== a.upvotes) {
        return b.upvotes - a.upvotes;
      }
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });

    setFilteredQuestions(filtered);
  };

  /**
   * Handle question voting
   */
  const handleVote = async (questionId: string) => {
    try {
      // Call API to upvote/remove upvote
      await questionService.upvoteQuestion(questionId);
      
      // Update local state
      setQuestions(prev => prev.map(q => {
        if (q.id === questionId) {
          const hasVoted = q.has_user_upvoted;
          return {
            ...q,
            upvotes: hasVoted ? q.upvotes - 1 : q.upvotes + 1,
            has_user_upvoted: !hasVoted,
            hasVoted: !hasVoted
          };
        }
        return q;
      }));
    } catch (err) {
      console.error('Error voting on question:', err);
      // You could show a toast notification here
    }
  };

  /**
   * Handle question submission
   */
  const handleSubmitQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!questionText.trim()) {
      setShowError(true);
      return;
    }

    try {
      setSubmitting(true);
      setShowError(false);

      // Create question data
      const questionData: CreateQuestionForm = {
        text: questionText.trim(),
        is_anonymous: isAnonymous,
        tags: []
      };

      // Submit question via API
      const newQuestion = await questionService.createQuestion(eventId, questionData);
      
      // Convert to UserQuestion format and add to list
      const userQuestion: UserQuestion = {
        ...newQuestion,
        hasVoted: false
      };

      // Add to questions list
      setQuestions(prev => [userQuestion, ...prev]);

      // Reset form
      setQuestionText('');
      setIsAnonymous(false);
      setSubmitSuccess(true);

      // Hide success message after 3 seconds
      setTimeout(() => setSubmitSuccess(false), 3000);

    } catch (err) {
      setError('Failed to submit question. Please try again.');
      console.error('Question submission error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Error Loading Event</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500 mb-4">Event ID: {eventId}</p>
          <button
            onClick={() => router.push('/events')}
            className="btn-primary mr-4"
          >
            Back to Events
          </button>
          <button
            onClick={() => loadEventData()}
            className="bg-gray-600 hover:bg-gray-700 text-white font-medium px-6 py-2 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Event Not Found</h1>
          <p className="text-gray-600 mb-4">The event you're looking for doesn't exist.</p>
          <p className="text-sm text-gray-500 mb-4">Event ID: {eventId}</p>
          <button
            onClick={() => router.push('/events')}
            className="btn-primary"
          >
            Back to Events
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar - Consistent with other pages */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Luca AMA App</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">Welcome, {user?.name}</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                {user?.role}
              </span>
              <button
                onClick={() => router.push('/events')}
                className="text-gray-600 hover:text-gray-900 text-sm"
              >
                ← Back to Events
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Page Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">{event.name}</h1>
            <p className="text-gray-600 mt-2">
              Ask questions and vote on what matters most to you
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Question Submission Form */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Add A Question</h2>
          
          {submitSuccess && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <p className="text-green-800">Your question has been submitted successfully!</p>
            </div>
          )}

          <form onSubmit={handleSubmitQuestion} className="space-y-4">
            {/* Question Text Area */}
            <div>
              <textarea
                value={questionText}
                onChange={(e) => setQuestionText(e.target.value)}
                placeholder="How is project Galactica advancing? Do we have any updates on funding and timelines?"
                className={`w-full px-4 py-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  showError && !questionText.trim() 
                    ? 'border-red-300 bg-red-50' 
                    : 'border-gray-300'
                }`}
                rows={4}
                disabled={submitting}
              />
              {showError && !questionText.trim() && (
                <p className="text-red-600 text-sm mt-1">Please enter a question</p>
              )}
            </div>

            {/* Anonymous Toggle and Submit */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {/* Anonymous Toggle */}
                <label className="flex items-center space-x-2 cursor-pointer">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={isAnonymous}
                      onChange={(e) => setIsAnonymous(e.target.checked)}
                      className="sr-only"
                      disabled={submitting}
                    />
                    <div className={`w-6 h-6 border-2 rounded flex items-center justify-center transition-colors ${
                      isAnonymous 
                        ? 'bg-primary-600 border-primary-600' 
                        : 'border-gray-300 bg-white'
                    }`}>
                      {isAnonymous && (
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                  </div>
                  <span className="text-gray-700 font-medium">Anonymous</span>
                </label>

                {isAnonymous && (
                  <div className="flex items-center text-gray-500 text-sm">
                    <FiEyeOff className="w-4 h-4 mr-1" />
                    <span>Your name will be hidden</span>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={submitting}
                className="bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium px-6 py-2 rounded-lg transition-colors flex items-center space-x-2"
              >
                {submitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Posting...</span>
                  </>
                ) : (
                  <>
                    <FiSend className="w-4 h-4" />
                    <span>Post</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Tab Navigation - Simplified for users */}
        <div className="bg-white rounded-lg shadow-sm border mb-6">
          <div className="flex border-b">
            {[
              { key: 'all', label: 'All Questions', count: questions.length },
              { key: 'answered', label: 'Answered', count: questions.filter(q => q.is_answered).length }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveFilter(tab.key as UserQuestionFilter)}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeFilter === tab.key
                    ? 'text-primary-600 border-b-2 border-primary-500 bg-primary-50'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
                <span className="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2 rounded-full text-xs">
                  {tab.count}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Questions List */}
        <div className="space-y-4">
          {filteredQuestions.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow-sm border">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">❓</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No questions yet</h3>
              <p className="text-gray-600">
                {activeFilter === 'all' 
                  ? 'Be the first to ask a question!'
                  : 'No questions have been answered yet.'
                }
              </p>
            </div>          ) : (
            filteredQuestions.map((question) => (
              <QuestionCard
                key={question.id}
                question={question}
                userRole="user"
                onUpvote={() => handleVote(question.id)}
                showActions={true}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
