'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { useRouter, useParams } from 'next/navigation';
import { Event, Question, SimilarQuestionsResponse } from '../../../types';
import { FiArrowUp, FiSend, FiUser, FiEyeOff } from 'react-icons/fi';
import { questionService } from '../../../services/questionService';
import SimilarQuestionsPanel from '../../../components/questions/SimilarQuestionsPanel';
import SimpleTest from '../../../components/test/SimpleTest';
import AISimilarityDetector from '../../../components/ai/AISimilarityDetector';

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
  console.log('🔥🔥🔥 UserEventViewPage component is EXECUTING! 🔥🔥🔥');
  
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const params = useParams();
  const eventId = params.id as string;

  // Debug logging
  console.log('🎯 UserEventViewPage initialized with eventId:', eventId);
  console.log('🎯 Params:', params);
  console.log('🎯 User:', user);
  console.log('🎯 IsAuthenticated:', isAuthenticated);
  console.log('🚀 AI Similarity Detection Feature LOADED - Version 2.0');

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

  // AI Similarity Detection state
  const [similarQuestionsData, setSimilarQuestionsData] = useState<SimilarQuestionsResponse | null>(null);
  const [similarityLoading, setSimilarityLoading] = useState(false);
  const [showSimilarPanel, setShowSimilarPanel] = useState(false);
  const [upvotingQuestions, setUpvotingQuestions] = useState<Set<string>>(new Set());

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

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 600));

      // Mock event data
      const mockEvent: Event = {
        id: eventId,
        name: 'Microsoft Fabric Developer Q&A Session',
        openDate: new Date('2024-01-15T10:00:00'),
        closeDate: new Date('2024-01-15T12:00:00'),
        createdBy: 'presenter@microsoft.com',
        moderators: ['moderator@microsoft.com'],
        participants: ['demo@microsoft.com', 'presenter@microsoft.com'],
        shareLink: `https://ama.microsoft.com/events/${eventId}`,
        isActive: true,
        createdAt: new Date('2024-01-10T09:00:00'),
        updatedAt: new Date('2024-01-15T10:30:00')
      };

      // Mock questions data for user view (simplified)
      const mockQuestions: UserQuestion[] = [
        {
          id: '1',
          eventId: eventId,
          text: 'Hi, I was wondering if developers had any feedback about using fabric, and how they were integrating it? I think it is a market we should try to aggressively expand in.',
          author: {
            id: '1',
            email: 'demo@microsoft.com',
            name: 'Anonymous User',
            role: 'user'
          },
          isAnonymous: true,
          upvotes: 10,
          hasUserUpvoted: false,
          isAnswered: false,
          isStarred: false,
          isStaged: false,
          tags: ['fabric', 'development', 'integration'],
          createdAt: new Date('2024-01-15T10:15:00'),
          updatedAt: new Date('2024-01-15T10:30:00'),
          hasVoted: false
        },
        {
          id: '2',
          eventId: eventId,
          text: 'What are the main performance benefits when using Fabric for large-scale data processing?',
          author: {
            id: '2',
            email: 'user2@microsoft.com',
            name: 'Sarah Chen',
            role: 'user'
          },
          isAnonymous: false,
          upvotes: 8,
          hasUserUpvoted: true,
          isAnswered: true,
          isStarred: false,
          isStaged: false,
          tags: ['fabric', 'performance', 'data-processing'],
          createdAt: new Date('2024-01-15T10:20:00'),
          updatedAt: new Date('2024-01-15T10:45:00'),
          hasVoted: true
        },
        {
          id: '3',
          eventId: eventId,
          text: 'Can you explain how Fabric handles data governance and compliance requirements?',
          author: {
            id: '3',
            email: 'user3@microsoft.com',
            name: 'Mike Rodriguez',
            role: 'user'
          },
          isAnonymous: false,
          upvotes: 6,
          hasUserUpvoted: false,
          isAnswered: false,
          isStarred: false,
          isStaged: false,
          tags: ['fabric', 'governance', 'compliance'],
          createdAt: new Date('2024-01-15T10:25:00'),
          updatedAt: new Date('2024-01-15T10:25:00'),
          hasVoted: false
        },
        {
          id: '4',
          eventId: eventId,
          text: 'What are the cost implications of migrating from Azure Synapse to Fabric?',
          author: {
            id: '4',
            email: 'user4@microsoft.com',
            name: 'Lisa Park',
            role: 'user'
          },
          isAnonymous: false,
          upvotes: 12,
          hasUserUpvoted: false,
          isAnswered: false,
          isStarred: false,
          isStaged: false,
          tags: ['fabric', 'migration', 'cost'],
          createdAt: new Date('2024-01-15T10:30:00'),
          updatedAt: new Date('2024-01-15T10:30:00'),
          hasVoted: false
        }
      ];

      setEvent(mockEvent);
      setQuestions(mockQuestions);
    } catch (err) {
      setError('Failed to load event data. Please try again.');
      console.error('Event loading error:', err);
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
        filtered = filtered.filter(q => q.isAnswered);
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
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });

    setFilteredQuestions(filtered);
  };

  /**
   * Handle question voting
   */
  const handleVote = (questionId: string) => {
    setQuestions(prev => prev.map(q => {
      if (q.id === questionId) {
        const hasVoted = q.hasUserUpvoted;
        return {
          ...q,
          upvotes: hasVoted ? q.upvotes - 1 : q.upvotes + 1,
          hasUserUpvoted: !hasVoted
        };
      }
      return q;
    }));
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

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Create new question
      const newQuestion: UserQuestion = {
        id: Date.now().toString(),
        eventId: eventId,
        text: questionText.trim(),
        author: {
          id: user?.id || 'current-user',
          email: user?.email || 'current@user.com',
          name: isAnonymous ? 'Anonymous' : (user?.name || 'Current User'),
          role: user?.role || 'user'
        },
        isAnonymous: isAnonymous,
        upvotes: 0,
        hasUserUpvoted: false,
        isAnswered: false,
        isStarred: false,
        isStaged: false,
        tags: [],
        createdAt: new Date(),
        updatedAt: new Date(),
        hasVoted: false
      };

      // Add to questions list
      setQuestions(prev => [newQuestion, ...prev]);

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

  /**
   * Debounced similarity detection for real-time AI analysis
   * Triggers when user types in the question textarea
   */
  const debouncedSimilarityCheck = useCallback(
    async (text: string) => {
      console.log('🔍 Similarity check triggered for text:', text);
      
      // Don't check if text is too short
      if (!text.trim() || text.trim().length < 10) {
        console.log('❌ Text too short, hiding panel');
        setShowSimilarPanel(false);
        setSimilarQuestionsData(null);
        return;
      }

      try {
        console.log('🤖 Starting AI analysis...');
        setSimilarityLoading(true);
        setShowSimilarPanel(true);

        // Call the AI similarity detection API
        console.log('📡 Calling API with eventId:', eventId, 'text:', text.trim());
        const response = await questionService.findSimilarQuestions(eventId, text.trim());
        console.log('✅ AI response received:', response);
        setSimilarQuestionsData(response);

        // Only show panel if we have similar questions
        const shouldShow = response.similar_questions.length > 0;
        console.log('📊 Similar questions found:', response.similar_questions.length, 'Show panel:', shouldShow);
        setShowSimilarPanel(shouldShow);
      } catch (error) {
        console.error('❌ Similarity detection failed:', error);
        // On error, hide the panel gracefully
        setShowSimilarPanel(false);
        setSimilarQuestionsData(null);
      } finally {
        setSimilarityLoading(false);
        console.log('🏁 Similarity check complete');
      }
    },
    []
  );

  /**
   * Handle upvoting a similar question from the panel
   */
  const handleUpvoteSimilar = async (questionId: string): Promise<void> => {
    setUpvotingQuestions(prev => new Set(prev).add(questionId));
    
    try {
      // Mock upvote API call - replace with actual API
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Update the local questions state if the question exists
      setQuestions(prev => prev.map(q => 
        q.id === questionId ? { ...q, upvotes: q.upvotes + 1, hasVoted: true } : q
      ));

      // Optionally close the panel and clear the form on successful upvote
      setShowSimilarPanel(false);
      setQuestionText('');
      setSimilarQuestionsData(null);
      
    } catch (error) {
      console.error('Failed to upvote similar question:', error);
      throw error; // Re-throw to let the component handle the error
    } finally {
      setUpvotingQuestions(prev => {
        const newSet = new Set(prev);
        newSet.delete(questionId);
        return newSet;
      });
    }
  };

  /**
   * Handle user decision to continue with posting new question
   */
  const handleContinueWithNew = () => {
    setShowSimilarPanel(false);
    setSimilarQuestionsData(null);
    // Focus back to textarea for user to continue
    const textarea = document.querySelector('textarea');
    textarea?.focus();
  };

  /**
   * Debounced effect for similarity detection
   */
  useEffect(() => {
    console.log('⏱️ useEffect triggered, questionText:', questionText);
    const timeoutId = setTimeout(() => {
      if (questionText.trim()) {
        console.log('🚀 Triggering similarity check after 1 second delay');
        debouncedSimilarityCheck(questionText);
      } else {
        console.log('⭕ No text to analyze');
      }
    }, 1000); // 1 second debounce

    return () => {
      console.log('🧹 Cleaning up timeout');
      clearTimeout(timeoutId);
    };
  }, [questionText, debouncedSimilarityCheck]);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // Error state
  if (error || !event) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Event Not Found</h1>
          <p className="text-gray-600 mb-4">{error || 'The event you\'re looking for doesn\'t exist.'}</p>
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
          <div style={{backgroundColor: 'red', color: 'white', padding: '20px', fontSize: '20px', fontWeight: 'bold'}}>
            ⚠️ EMERGENCY TEST - If you see this, React is working
          </div>
          <SimpleTest />
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
                onChange={(e) => {
                  console.log('📝 Textarea onChange triggered:', e.target.value);
                  setQuestionText(e.target.value);
                }}
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

            {/* Simple AI Similarity Detection Test */}
            <AISimilarityDetector 
              eventId={eventId}
              questionText={questionText}
              onSimilarFound={(data) => {
                console.log('🎯 Similar questions found:', data);
                setSimilarQuestionsData(data);
                setShowSimilarPanel(data.similar_questions.length > 0);
              }}
            />

            {/* AI-Powered Similar Questions Panel */}
            <div style={{backgroundColor: 'yellow', padding: '10px', margin: '10px'}}>
              🧪 DEBUG: SimilarQuestionsPanel Container - Loading: {similarityLoading.toString()}, Visible: {showSimilarPanel.toString()}
            </div>
            <SimilarQuestionsPanel
              similarData={similarQuestionsData}
              isLoading={similarityLoading}
              isVisible={showSimilarPanel}
              onUpvoteSimilar={handleUpvoteSimilar}
              onContinueWithNew={handleContinueWithNew}
              upvotingQuestions={upvotingQuestions}
            />

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
              { key: 'answered', label: 'Answered', count: questions.filter(q => q.isAnswered).length }
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
            </div>
          ) : (
            filteredQuestions.map((question) => (
              <div key={question.id} className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex space-x-4">
                  {/* Vote Section */}
                  <div className="flex flex-col items-center">
                    <button
                      onClick={() => handleVote(question.id)}
                      className={`flex flex-col items-center p-3 rounded-lg transition-colors ${
                        question.hasUserUpvoted
                          ? 'bg-primary-100 text-primary-600'
                          : 'bg-gray-50 hover:bg-gray-100 text-gray-600'
                      }`}
                    >
                      <FiArrowUp className="w-5 h-5 mb-1" />
                      <span className="font-semibold text-lg">{question.upvotes}</span>
                      <span className="text-xs">votes</span>
                    </button>
                  </div>

                  {/* Question Content */}
                  <div className="flex-1">
                    {/* Question Text */}
                    <div className="mb-4">
                      <p className="text-gray-900 text-base leading-relaxed mb-2">{question.text}</p>
                      <div className="flex items-center text-sm text-gray-500">
                        <div className="flex items-center">
                          {question.isAnonymous ? (
                            <>
                              <FiEyeOff className="w-4 h-4 mr-1" />
                              <span>Anonymous</span>
                            </>
                          ) : (
                            <>
                              <FiUser className="w-4 h-4 mr-1" />
                              <span>{question.author.name}</span>
                            </>
                          )}
                        </div>
                        <span className="mx-2">•</span>
                        <span>{question.createdAt.toLocaleDateString()}</span>
                        {question.tags.length > 0 && (
                          <>
                            <span className="mx-2">•</span>
                            <div className="flex space-x-1">
                              {question.tags.map((tag, index) => (
                                <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Answer Display */}
                    {question.isAnswered && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <div className="flex items-start">
                          <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                            <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                          <div className="flex-1">
                            <h4 className="font-medium text-green-900 mb-1">Answered</h4>
                            <p className="text-green-800 text-sm">This question has been addressed by the presenter.</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
