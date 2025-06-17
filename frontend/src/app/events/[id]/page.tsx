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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{event.name}</h1>
              <p className="text-gray-600 mt-2">
                Manage questions and moderate the AMA session • {filteredQuestions.length} questions
              </p>
            </div>
            {canModerate && (
              <button
                onClick={() => setShowModeratorsOnly(!showModeratorsOnly)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  showModeratorsOnly
                    ? 'bg-primary-600 text-white'
                    : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {showModeratorsOnly ? 'Show All Questions' : 'Moderator View Only'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Tab Navigation - Clean Microsoft style */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { key: 'all', label: 'All Questions', count: questions.length },
              { key: 'answered', label: 'Answered', count: questions.filter(q => q.isAnswered).length },
              { key: 'starred', label: 'Starred', count: questions.filter(q => q.isStarred).length },
              { key: 'stage', label: 'On Stage', count: questions.filter(q => q.isOnStage).length }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveFilter(tab.key as QuestionFilter)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeFilter === tab.key
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
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
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions Bar */}
        {canModerate && (
          <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
              <div className="flex items-center space-x-3">
                <div className="text-sm text-gray-600">
                  Selected questions will be affected by these actions
                </div>
                <button className="btn-secondary text-sm">
                  Bulk Star
                </button>
                <button className="btn-secondary text-sm">
                  Bulk Stage
                </button>
                <button className="btn-primary text-sm">
                  Mark Answered
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Questions List */}
        <div className="space-y-4">
          {filteredQuestions.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow-sm border">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">❓</span>
              </div>
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
              <div key={question.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
                {/* Question Header - On Stage indicator */}
                {question.isOnStage && (
                  <div className="bg-primary-50 border-b px-6 py-3">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
                      <span className="text-sm font-medium text-primary-700">Currently on stage</span>
                    </div>
                  </div>
                )}

                {/* Question Content */}
                <div className="p-6">
                  <div className="flex space-x-4">
                    {/* Vote Section */}
                    <div className="flex flex-col items-center">
                      <button
                        onClick={() => handleVote(question.id)}
                        className="flex flex-col items-center p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors group"
                      >
                        <FiArrowUp className="w-5 h-5 text-gray-600 group-hover:text-primary-600" />
                        <span className="font-semibold text-lg text-gray-900">{question.upvotes}</span>
                        <span className="text-xs text-gray-500">votes</span>
                      </button>
                    </div>

                    {/* Question Content */}
                    <div className="flex-1">
                      {/* Question Text */}
                      <div className="mb-4">
                        <p className="text-gray-900 text-base leading-relaxed">{question.text}</p>
                        <div className="flex items-center mt-2 text-sm text-gray-500">
                          <span>by {question.isAnonymous ? 'Anonymous' : question.author.name}</span>
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

                      {/* Moderator Note */}
                      {question.moderatorNote && canModerate && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                          <div className="flex items-start">
                            <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                              <span className="text-blue-600 text-xs">📝</span>
                            </div>
                            <div>
                              <h4 className="font-medium text-blue-900 mb-1">Moderator Note</h4>
                              <p className="text-blue-800 text-sm">{question.moderatorNote}</p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Related Questions */}
                      {question.relatedQuestions && question.relatedQuestions.length > 0 && (
                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
                          <div className="flex items-start">
                            <button className="w-6 h-6 bg-white border border-amber-300 rounded flex items-center justify-center mr-3 mt-0.5 hover:bg-amber-50">
                              <FiPlus className="w-3 h-3 text-amber-600" />
                            </button>
                            <div className="flex-1">
                              <h4 className="font-medium text-amber-900 mb-2">Related Questions</h4>
                              <div className="space-y-1">
                                {question.relatedQuestions.map((relatedQ, index) => (
                                  <p key={index} className="text-amber-800 text-sm">
                                    {index + 1}. {relatedQ}
                                  </p>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Answer Display */}
                      {question.isAnswered && question.answer && (
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                          <div className="flex items-start">
                            <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                              <FiCheck className="w-3 h-3 text-green-600" />
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium text-green-900 mb-1">Answer</h4>
                              <p className="text-green-800 text-sm mb-2">{question.answer}</p>
                              {question.answeredBy && question.answeredAt && (
                                <p className="text-xs text-green-600">
                                  Answered by {question.answeredBy} on {question.answeredAt.toLocaleDateString()}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    {canModerate && (
                      <div className="flex flex-col space-y-2">
                        <button
                          onClick={() => handleStar(question.id)}
                          className={`p-2 rounded-lg transition-colors tooltip ${
                            question.isStarred
                              ? 'bg-yellow-100 text-yellow-600 border border-yellow-200'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-200'
                          }`}
                          title={question.isStarred ? 'Remove from starred' : 'Add to starred'}
                        >
                          <FiStar className={`w-4 h-4 ${question.isStarred ? 'fill-current' : ''}`} />
                        </button>
                        
                        <button
                          onClick={() => handleStage(question.id)}
                          className={`p-2 rounded-lg transition-colors ${
                            question.isOnStage
                              ? 'bg-primary-100 text-primary-600 border border-primary-200'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-200'
                          }`}
                          title={question.isOnStage ? 'Remove from stage' : 'Put on stage'}
                        >
                          <FiEye className="w-4 h-4" />
                        </button>
                        
                        <button
                          onClick={() => handleAnswer(question.id)}
                          className={`p-2 rounded-lg transition-colors ${
                            question.isAnswered
                              ? 'bg-green-100 text-green-600 border border-green-200'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-200'
                          }`}
                          title={question.isAnswered ? 'Mark as unanswered' : 'Mark as answered'}
                        >
                          <FiCheck className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}
