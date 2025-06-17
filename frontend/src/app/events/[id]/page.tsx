'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { useRouter, useParams } from 'next/navigation';
import { Event, Question } from '../../../types';
import { FiStar, FiArrowUp, FiCheck, FiEye, FiTrash2, FiPlus, FiFilter } from 'react-icons/fi';

/**
 * Event Details Page Component
 * 
 * This page displays an individual AMA event with its questions and provides
 * comprehensive question management features for moderators and presenters.
 * 
 * Features:
 * - Real-time question display with filtering and sorting
 * - Tab-based navigation (ALL, ANSWERED, STARRED, STAGE)
 * - Question voting, starring, staging, and answering
 * - Moderator-only notes and controls
 * - Semantically related question suggestions
 * - Responsive design with role-based permissions
 * 
 * Based on the Microsoft AMA interface design patterns
 */

// Question filter types for tab navigation
type QuestionFilter = 'all' | 'answered' | 'starred' | 'stage';

// Interface for question with additional metadata
interface ExtendedQuestion extends Question {
  isOnStage?: boolean;
  moderatorNote?: string;
  relatedQuestions?: string[];
  answer?: string;
  answeredBy?: string;
  answeredAt?: Date;
}

export default function EventDetailsPage() {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const params = useParams();
  const eventId = params.id as string;

  // Component state
  const [event, setEvent] = useState<Event | null>(null);
  const [questions, setQuestions] = useState<ExtendedQuestion[]>([]);
  const [filteredQuestions, setFilteredQuestions] = useState<ExtendedQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<QuestionFilter>('all');
  const [showModeratorsOnly, setShowModeratorsOnly] = useState(false);

  // Role-based permissions
  const isModerator = user?.role === 'moderator';
  const isPresenter = user?.role === 'presenter';
  const canModerate = isModerator || isPresenter;
  /**
   * Load event data and questions
   */
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Only moderators and presenters can access the question management interface
    if (!canModerate) {
      router.push('/events');
      return;
    }

    loadEventData();
  }, [eventId, isAuthenticated, canModerate, router]);

  /**
   * Filter questions based on active tab
   */
  useEffect(() => {
    filterQuestions();
  }, [questions, activeFilter, showModeratorsOnly]);

  /**
   * Simulates loading event and question data
   */
  const loadEventData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));

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
      };      // Mock questions data with rich metadata
      const mockQuestions: ExtendedQuestion[] = [
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
          isStarred: true,
          isStaged: false,
          isOnStage: true,
          presenterNotes: 'talk about how we are running a pilot test with one of our interns to see how it feels to use fabric to develope an end-to-end application',
          tags: ['fabric', 'development', 'integration'],
          createdAt: new Date('2024-01-15T10:15:00'),
          updatedAt: new Date('2024-01-15T10:30:00'),
          moderatorNote: 'talk about how we are running a pilot test with one of our interns to see how it feels to use fabric to develope an end-to-end application',
          relatedQuestions: [
            'What kind of feedback have developers shared about their experience with Fabric so far?',
            'How are development teams currently integrating Fabric into their workflows or tech stacks?',
            'What opportunities exist for expanding our presence in the Fabric ecosystem or market?'
          ]
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
          isOnStage: false,
          tags: ['fabric', 'performance', 'data-processing'],
          answer: 'Fabric provides significant performance improvements through its unified compute engine and optimized data lake architecture.',
          answeredBy: 'presenter@microsoft.com',
          answeredAt: new Date('2024-01-15T10:45:00'),
          createdAt: new Date('2024-01-15T10:20:00'),
          updatedAt: new Date('2024-01-15T10:45:00')
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
          isStarred: true,
          isStaged: false,
          isOnStage: false,
          tags: ['fabric', 'governance', 'compliance'],
          createdAt: new Date('2024-01-15T10:25:00'),
          updatedAt: new Date('2024-01-15T10:25:00'),
          moderatorNote: 'Important compliance question - prepare detailed response'
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
          isOnStage: false,
          tags: ['fabric', 'migration', 'cost'],
          createdAt: new Date('2024-01-15T10:30:00'),
          updatedAt: new Date('2024-01-15T10:30:00')
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
   * Filter questions based on active tab and moderator filter
   */
  const filterQuestions = () => {
    let filtered = [...questions];

    // Apply tab filter
    switch (activeFilter) {
      case 'answered':
        filtered = filtered.filter(q => q.isAnswered);
        break;
      case 'starred':
        filtered = filtered.filter(q => q.isStarred);
        break;
      case 'stage':
        filtered = filtered.filter(q => q.isOnStage);
        break;
      case 'all':
      default:
        // No additional filtering for 'all'
        break;
    }

    // Apply moderator-only filter
    if (showModeratorsOnly && canModerate) {
      filtered = filtered.filter(q => q.moderatorNote);
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
    setQuestions(prev => prev.map(q => 
      q.id === questionId 
        ? { ...q, upvotes: q.upvotes + 1 }
        : q
    ));
  };

  /**
   * Handle question starring (moderator/presenter only)
   */
  const handleStar = (questionId: string) => {
    if (!canModerate) return;
    
    setQuestions(prev => prev.map(q => 
      q.id === questionId 
        ? { ...q, isStarred: !q.isStarred }
        : q
    ));
  };

  /**
   * Handle staging question (moderator/presenter only)
   */
  const handleStage = (questionId: string) => {
    if (!canModerate) return;
    
    setQuestions(prev => prev.map(q => 
      q.id === questionId 
        ? { ...q, isOnStage: !q.isOnStage }
        : q
    ));
  };

  /**
   * Handle marking question as answered (moderator/presenter only)
   */
  const handleAnswer = (questionId: string) => {
    if (!canModerate) return;
    
    setQuestions(prev => prev.map(q => 
      q.id === questionId 
        ? { 
            ...q, 
            isAnswered: !q.isAnswered,
            answeredBy: q.isAnswered ? undefined : user?.email,
            answeredAt: q.isAnswered ? undefined : new Date()
          }
        : q
    ));
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
  if (error || !event) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Event Not Found</h1>
          <p className="text-gray-600 mb-4">{error || 'The event you\'re looking for doesn\'t exist.'}</p>
          <button
            onClick={() => router.push('/events')}
            className="bg-primary-500 text-white px-6 py-2 rounded-lg hover:bg-primary-600"
          >
            Back to Events
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{event.name}</h1>
              <p className="text-gray-600 mt-1">{filteredQuestions.length} questions</p>
            </div>
            <div className="flex items-center space-x-4">
              {canModerate && (
                <button
                  onClick={() => setShowModeratorsOnly(!showModeratorsOnly)}
                  className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                    showModeratorsOnly
                      ? 'bg-primary-50 border-primary-200 text-primary-700'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Hide All
                </button>
              )}
              <button
                onClick={() => router.push('/events')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back to Events
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-0">
            {[
              { key: 'all', label: 'TAB: ALL', color: 'bg-blue-600' },
              { key: 'answered', label: 'TAB: ANSWERED', color: 'bg-blue-600' },
              { key: 'starred', label: 'TAB: STARRED', color: 'bg-green-600' },
              { key: 'stage', label: 'TAB: STAGE', color: 'bg-green-600' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveFilter(tab.key as QuestionFilter)}
                className={`px-6 py-3 text-sm font-medium text-white transition-colors ${
                  activeFilter === tab.key ? tab.color : 'bg-gray-500 hover:bg-gray-600'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filter Bar */}
        <div className="flex items-center justify-between mb-6">
          <button className="bg-orange-500 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2">
            <FiFilter className="w-4 h-4" />
            FILTER
          </button>
          
          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center bg-yellow-100 text-yellow-800 px-3 py-2 rounded-lg">
              <FiArrowUp className="w-4 h-4 mr-1" />
              <span className="font-semibold">10</span>
              <span className="ml-1 text-sm">Vote</span>
            </div>
            <button className="flex items-center bg-yellow-100 text-yellow-800 px-3 py-2 rounded-lg">
              <FiStar className="w-4 h-4 mr-1" />
              <span className="text-sm">Star</span>
            </button>
            <button className="flex items-center bg-blue-100 text-blue-800 px-3 py-2 rounded-lg">
              <FiArrowUp className="w-4 h-4 mr-1" />
              <span className="text-sm">Stage</span>
            </button>
            <button className="flex items-center bg-green-100 text-green-800 px-3 py-2 rounded-lg">
              <FiCheck className="w-4 h-4 mr-1" />
              <span className="text-sm">Answered</span>
            </button>
            <button className="flex items-center bg-gray-100 text-gray-800 px-3 py-2 rounded-lg">
              <FiTrash2 className="w-4 h-4 mr-1" />
            </button>
          </div>
        </div>

        {/* Questions List */}
        <div className="space-y-4">
          {filteredQuestions.length === 0 ? (
            <div className="text-center py-12">
              <h3 className="text-lg font-medium text-gray-900 mb-2">No questions found</h3>
              <p className="text-gray-600">
                {activeFilter === 'all' 
                  ? 'No questions have been submitted yet.'
                  : `No questions match the ${activeFilter} filter.`
                }
              </p>
            </div>
          ) : (
            filteredQuestions.map((question) => (
              <div key={question.id} className="bg-white border rounded-lg">
                {/* Question Header - Stage indicator */}
                {question.isOnStage && (
                  <div className="flex items-center bg-green-50 px-4 py-2 border-b">
                    <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center mr-2">
                      <FiEye className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="text-sm text-green-700 font-medium">On Stage</span>
                  </div>
                )}

                {/* Question Content */}
                <div className="p-4">
                  <div className="flex items-start space-x-4">
                    {/* Vote Button */}
                    <button
                      onClick={() => handleVote(question.id)}
                      className="flex flex-col items-center bg-yellow-100 text-yellow-800 px-3 py-2 rounded-lg hover:bg-yellow-200 transition-colors"
                    >
                      <FiArrowUp className="w-4 h-4" />
                      <span className="font-semibold text-lg">{question.upvotes}</span>
                      <span className="text-xs">Vote</span>
                    </button>

                    {/* Question Text */}
                    <div className="flex-1">
                      <div className="mb-2">
                        <span className="font-semibold text-gray-900">QUESTION TEXT </span>
                        <span className="text-gray-700">{question.text}</span>
                      </div>

                      {/* Moderator Note */}
                      {question.moderatorNote && canModerate && (
                        <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
                          <span className="font-semibold text-gray-900">MODERATOR-ONLY NOTE </span>
                          <span className="text-gray-700">{question.moderatorNote}</span>
                        </div>
                      )}

                      {/* Related Questions */}
                      {question.relatedQuestions && question.relatedQuestions.length > 0 && (
                        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                          <div className="flex items-start space-x-2">
                            <button className="bg-white border border-gray-300 rounded p-1 mt-1">
                              <FiPlus className="w-4 h-4" />
                            </button>
                            <div className="flex-1">
                              <div className="mb-2">
                                <span className="text-sm text-gray-600">Expands similar questions</span>
                              </div>
                              <div className="space-y-1">
                                <div className="font-semibold text-gray-900">SEMANTICALLY RELATED QUESTION</div>
                                {question.relatedQuestions.map((relatedQ, index) => (
                                  <div key={index} className="text-gray-700 text-sm">
                                    {index + 1}-{relatedQ}
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col space-y-2">
                      {canModerate && (
                        <>
                          <button
                            onClick={() => handleStar(question.id)}
                            className={`p-2 rounded-lg transition-colors ${
                              question.isStarred
                                ? 'bg-yellow-100 text-yellow-600'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                            title={question.isStarred ? 'UnStar' : 'Star'}
                          >
                            <FiStar className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleStage(question.id)}
                            className={`p-2 rounded-lg transition-colors ${
                              question.isOnStage
                                ? 'bg-blue-100 text-blue-600'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                            title="Stage"
                          >
                            <FiArrowUp className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleAnswer(question.id)}
                            className={`p-2 rounded-lg transition-colors ${
                              question.isAnswered
                                ? 'bg-green-100 text-green-600'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                            title={question.isAnswered ? 'Mark as Unanswered' : 'Mark as Answered'}
                          >
                            <FiCheck className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Answer Display */}
                  {question.isAnswered && question.answer && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="bg-green-50 rounded-lg p-3">
                        <div className="font-semibold text-green-800 mb-1">Answer:</div>
                        <div className="text-green-700">{question.answer}</div>
                        {question.answeredBy && question.answeredAt && (
                          <div className="text-xs text-green-600 mt-2">
                            Answered by {question.answeredBy} on {question.answeredAt.toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
