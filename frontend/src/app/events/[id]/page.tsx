'use client';

import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { useRouter, useParams } from 'next/navigation';
import { Event, Question } from '../../../types';
import { eventService } from '../../../services/eventService';
import { questionService } from '../../../services/questionService';
import { FiStar, FiArrowUp, FiCheck, FiEye, FiTrash2, FiPlus, FiMinus, FiFilter } from 'react-icons/fi';
import { EventHeaderSkeleton, QuestionCardSkeleton } from '../../../components/ui/LoadingSkeleton';
import { useRealTimeSync } from '../../../hooks/useRealTimeSync';
import { useOptimisticUpdates } from '../../../hooks/useOptimisticUpdates';


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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<QuestionFilter>('all');
  const [showModeratorsOnly, setShowModeratorsOnly] = useState(false);
    // Track which questions have their related questions expanded
  const [expandedRelatedQuestions, setExpandedRelatedQuestions] = useState<Set<string>>(new Set());  // Track which moderator notes are being edited
  const [editingModeratorNotes, setEditingModeratorNotes] = useState<Set<string>>(new Set());
  const [moderatorNoteTexts, setModeratorNoteTexts] = useState<Record<string, string>>({});
    // Track processing state to prevent duplicate calls
  const [processingActions, setProcessingActions] = useState<Set<string>>(new Set());
  const lastActionRef = useRef<{ action: string; timestamp: number } | null>(null);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Helper function to check if an action is currently processing
  const isProcessing = useCallback((actionKey: string) => {
    return processingActions.has(actionKey);
  }, [processingActions]);

  // Helper function to set processing state
  const setProcessing = useCallback((actionKey: string, processing: boolean) => {
    setProcessingActions(prev => {
      const newSet = new Set(prev);
      if (processing) {
        newSet.add(actionKey);
      } else {
        newSet.delete(actionKey);
      }
      return newSet;
    });
  }, []);

  // Initialize moderator note texts when questions load
  useEffect(() => {
    const noteTexts: Record<string, string> = {};
    questions.forEach(question => {
      if (question.moderatorNote) {
        noteTexts[question.id] = question.moderatorNote;
      }
    });
    setModeratorNoteTexts(noteTexts);
  }, [questions]);

  // Role-based permissions using new dynamic system
  const userRole = event?.user_role_in_event || 'no_access';
  const canModerate = event?.can_user_moderate || false;
  const canAccess = event?.can_user_access || false;
  const isCreator = event?.is_created_by_user || false;

  // Track ongoing stage operations to prevent polling interference
  const [stagingInProgress, setStagingInProgress] = useState<Set<string>>(new Set());

  /**
   * Manual refresh function for questions
   */
  const refreshQuestions = useCallback(async () => {
    try {
      console.log('Refreshing questions...');
      const questionsData = await questionService.getQuestions(eventId);
      
      // Convert to ExtendedQuestion format
      const extendedQuestions: ExtendedQuestion[] = questionsData.map(q => ({
        ...q,
        isOnStage: q.is_staged,
        moderatorNote: q.presenter_notes || '',
        relatedQuestions: [],
        answer: '',
        answeredBy: '',
        answeredAt: undefined
      }));
      
      // Only update questions if no staging operations are in progress
      // This prevents polling from overwriting optimistic updates
      if (stagingInProgress.size === 0) {
        setQuestions(extendedQuestions);
        console.log('Questions refreshed successfully:', extendedQuestions.length);
      } else {
        console.log('Skipping refresh - staging operation in progress');
      }
    } catch (err: any) {
      console.error('Questions refresh error:', err);
      // Don't show error UI for refresh failures, just log them
    }
  }, [eventId, stagingInProgress]);

  // Real-time sync setup
  const handleQuestionsUpdate = useCallback((questionsData: Question[]) => {
    // Convert to ExtendedQuestion format
    const extendedQuestions: ExtendedQuestion[] = questionsData.map(q => ({
      ...q,
      isOnStage: q.is_staged,
      moderatorNote: q.presenter_notes || '',
      relatedQuestions: [],
      answer: '',
      answeredBy: '',
      answeredAt: undefined
    }));
    
    // Only update if no staging operations are in progress
    if (stagingInProgress.size === 0) {
      setQuestions(extendedQuestions);
    }
  }, [stagingInProgress]);

  /**
   * Load event data and questions
   */
  useEffect(() => {
    // Check authentication status but don't redirect immediately
    // Let the AuthContext handle authentication state properly
    if (isAuthenticated === false) {
      console.log('User not authenticated, redirecting to login');
      router.push('/login');
      return;
    }

    // Only proceed if user is authenticated
    if (isAuthenticated && eventId) {
      loadEventData();
    }
  }, [eventId, isAuthenticated, router]);
  
  // Permission-based routing effect
  useEffect(() => {
    if (!event || loading) return;
    
    console.log('Event loaded, checking permissions:', {
      event: event.name,
      userRole,
      canModerate,
      canAccess,
      user_role_in_event: event.user_role_in_event,
      can_user_moderate: event.can_user_moderate,
      user_permissions: event.user_permissions
    });
    
    // Check if user can access this event
    if (!canAccess) {
      console.log('User cannot access event, redirecting to events list');
      router.push('/events');
      return;
    }
    
    // Route users to the user-specific view if they can't moderate
    if (!canModerate && userRole === 'participant') {
      console.log('User is participant without moderation rights, redirecting to user view');
      router.push(`/events/${eventId}/user`);
      return;
    }
    
    console.log('User has moderation rights or is not a participant, staying on main event page');
  }, [event, loading, canAccess, canModerate, userRole, eventId, router]);

  // Set up polling for real-time updates in moderator view
  useEffect(() => {
    if (!event || !canModerate) return;
    
    // Set up polling every 10 seconds for better performance
    // Still responsive but reduces server load
    refreshIntervalRef.current = setInterval(() => {
      refreshQuestions();
    }, 10000);
    
    // Cleanup interval on unmount
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [event, canModerate, refreshQuestions]);

  /**
   * Load event and question data from API
   */
  const loadEventData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch event data from the API
      const eventData = await eventService.getEvent(eventId);
      setEvent(eventData);

      // Load questions for this event
      await loadQuestions();
    } catch (err: any) {
      setError(err.message || 'Failed to load event data. Please try again.');
      console.error('Event loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load questions separately for refresh capability
   */
  const loadQuestions = async () => {
    try {
      const questionsData = await questionService.getQuestions(eventId);
      
      // Convert to ExtendedQuestion format
      const extendedQuestions: ExtendedQuestion[] = questionsData.map(q => ({
        ...q,
        isOnStage: q.is_staged,
        moderatorNote: q.presenter_notes || '',
        relatedQuestions: [],
        answer: '',
        answeredBy: '',
        answeredAt: undefined
      }));
      
      setQuestions(extendedQuestions);
    } catch (err: any) {
      console.error('Questions loading error:', err);
    }
  };
  /**
   * Memoized filtered questions for better performance
   * Only recalculates when questions, activeFilter, or showModeratorsOnly changes
   */
  const filteredQuestions = useMemo(() => {
    let filtered = [...questions];

    // Apply tab filter
    switch (activeFilter) {
      case 'answered':
        filtered = filtered.filter(q => q.is_answered);
        break;
      case 'starred':
        filtered = filtered.filter(q => q.is_starred);
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
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });

    return filtered;
  }, [questions, activeFilter, showModeratorsOnly, canModerate]);  /**
   * Handle question voting with optimistic updates for immediate feedback
   */
  const handleVote = useCallback(async (questionId: string) => {
    const actionKey = `vote-${questionId}`;
    
    // Prevent multiple simultaneous calls
    if (isProcessing(actionKey)) {
      console.log('Vote action already in progress');
      return;
    }
    
    setProcessing(actionKey, true);
    
    // Find the question to update
    const currentQuestion = questions.find(q => q.id === questionId);
    if (!currentQuestion) return;
    
    const hasVoted = currentQuestion.has_user_upvoted;
    const newVoteCount = hasVoted ? currentQuestion.upvotes - 1 : currentQuestion.upvotes + 1;
    
    // Apply optimistic update immediately
    setQuestions(prev => prev.map(q => {
      if (q.id === questionId) {
        return {
          ...q,
          upvotes: newVoteCount,
          has_user_upvoted: !hasVoted
        };
      }
      return q;
    }));
    
    try {
      // Call API to toggle vote (this will take 2+ seconds with Fabric SQL)
      await questionService.upvoteQuestion(questionId);
      
      // Optimistic update already applied, so we're done
      console.log('✅ Vote confirmed by server');
      
    } catch (error) {
      console.error('Failed to vote on question:', error);
      
      // Revert optimistic update on error
      setQuestions(prev => prev.map(q => {
        if (q.id === questionId) {
          return {
            ...q,
            upvotes: currentQuestion.upvotes,
            has_user_upvoted: currentQuestion.has_user_upvoted
          };
        }
        return q;
      }));
      
      // Show error feedback
      alert('Failed to update vote. Please try again.');
    } finally {
      setProcessing(actionKey, false);
    }
  }, [isProcessing, setProcessing]);  /**
   * Handle question starring with optimistic updates (moderator/presenter only)
   */
  const handleStar = useCallback(async (questionId: string) => {
    if (!canModerate) return;
    
    const actionKey = `star-${questionId}`;
    
    // Prevent multiple simultaneous calls
    if (isProcessing(actionKey)) {
      console.log('Star action already in progress');
      return;
    }
    
    setProcessing(actionKey, true);
    
    // Get current state to determine new starred status
    const currentQuestion = questions.find(q => q.id === questionId);
    if (!currentQuestion) return;
    
    const newStarred = !currentQuestion.is_starred;
    
    // Apply optimistic update immediately
    setQuestions(prev => prev.map(q => {
      if (q.id === questionId) {
        return { ...q, is_starred: newStarred };
      }
      return q;
    }));
    
    try {
      // Call API to update starred status (slow with Fabric SQL)
      await questionService.updateQuestion(questionId, {
        is_starred: newStarred
      });
      
      console.log('✅ Star status confirmed by server');
      
    } catch (error) {
      console.error('Failed to star/unstar question:', error);
      
      // Revert optimistic update on error
      setQuestions(prev => prev.map(q => {
        if (q.id === questionId) {
          return { ...q, is_starred: currentQuestion.is_starred };
        }
        return q;
      }));
      
      alert('Failed to update star status. Please try again.');
    } finally {
      setProcessing(actionKey, false);
    }
  }, [canModerate, questions, isProcessing, setProcessing]);  /**
   * Handle staging question with optimistic updates (moderator/presenter only)
   * Only one question can be staged at a time
   */
  const handleStage = useCallback(async (questionId: string) => {
    if (!canModerate) return;
    
    const actionKey = `stage-${questionId}`;
    
    // Prevent multiple simultaneous calls
    if (isProcessing(actionKey)) {
      console.log('Stage action already in progress');
      return;
    }
    
    setProcessing(actionKey, true);
    
    // Track this staging operation to prevent polling interference
    setStagingInProgress(prev => new Set(prev).add(questionId));
    
    // Get current question state
    const currentQuestion = questions.find(q => q.id === questionId);
    if (!currentQuestion) {
      setStagingInProgress(prev => {
        const newSet = new Set(prev);
        newSet.delete(questionId);
        return newSet;
      });
      setProcessing(actionKey, false);
      return;
    }
    
    const willBeStaged = !currentQuestion.is_staged;
    
    // Apply optimistic update immediately
    setQuestions(prev => prev.map(q => {
      if (q.id === questionId) {
        // Update the clicked question
        return { ...q, is_staged: willBeStaged, isOnStage: willBeStaged };
      } else if (willBeStaged) {
        // If staging this question, unstage all others
        return { ...q, is_staged: false, isOnStage: false };
      }
      // If unstaging, leave other questions unchanged
      return q;
    }));
    
    try {
      // Use the dedicated staging endpoint (slow with Fabric SQL)
      const updatedQuestion = await questionService.toggleStage(questionId);
      
      console.log('✅ Stage status confirmed by server');
      
      // Final update with server response
      setQuestions(prev => prev.map(q => {
        if (q.id === questionId) {
          return { ...q, is_staged: updatedQuestion.is_staged, isOnStage: updatedQuestion.is_staged };
        } else if (updatedQuestion.is_staged) {
          // Backend unstaged others, sync UI
          return { ...q, is_staged: false, isOnStage: false };
        }
        return q;
      }));
      
    } catch (error) {
      console.error('Failed to stage/unstage question:', error);
      
      // Revert optimistic update on error
      setQuestions(prev => prev.map(q => {
        if (q.id === questionId) {
          return { ...q, is_staged: currentQuestion.is_staged, isOnStage: currentQuestion.is_staged };
        }
        return q;
      }));
      
      alert('Failed to update stage status. Please try again.');
    } finally {
      // Remove from staging tracking and processing
      setStagingInProgress(prev => {
        const newSet = new Set(prev);
        newSet.delete(questionId);
        return newSet;
      });
      setProcessing(actionKey, false);
    }
  }, [canModerate, questions, isProcessing, setProcessing]);  /**
   * Handle marking question as answered (moderator/presenter only)
   */
  const handleAnswer = useCallback(async (questionId: string) => {
    if (!canModerate) return;
    
    const actionKey = `answer-${questionId}`;
    
    // Prevent multiple simultaneous calls
    if (isProcessing(actionKey)) {
      console.log('Answer action already in progress');
      return;
    }
    
    setProcessing(actionKey, true);
    
    try {
      // Get current state to determine new answered status
      const currentQuestion = questions.find(q => q.id === questionId);
      if (!currentQuestion) return;
      
      const newAnswered = !currentQuestion.is_answered;
      
      // Call API to update answered status
      await questionService.updateQuestion(questionId, {
        is_answered: newAnswered
      });
      
      // Update local state after successful API call
      setQuestions(prev => prev.map(q => {
        if (q.id === questionId) {
          return { 
            ...q, 
            is_answered: newAnswered,
            answeredBy: newAnswered ? user?.email : undefined,
            answeredAt: newAnswered ? new Date() : undefined
          };
        }
        return q;
      }));
    } catch (error) {
      console.error('Failed to mark question as answered/unanswered:', error);
    } finally {
      setProcessing(actionKey, false);
    }
  }, [canModerate, user?.email, questions, isProcessing, setProcessing]);

  /**
   * Toggle the expanded state of related questions for a specific question
   */
  const toggleRelatedQuestions = (questionId: string) => {
    setExpandedRelatedQuestions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });
  };  /**
   * Start editing a moderator note
   */
  const startEditingNote = (questionId: string) => {
    if (!canModerate) return;
    
    setEditingModeratorNotes(prev => new Set(prev).add(questionId));
    
    // Initialize the text area with existing note or empty string
    const question = questions.find(q => q.id === questionId);
    setModeratorNoteTexts(prev => ({
      ...prev,
      [questionId]: question?.moderatorNote || ''
    }));
  };

  /**
   * Cancel editing a moderator note
   */
  const cancelEditingNote = (questionId: string) => {
    setEditingModeratorNotes(prev => {
      const newSet = new Set(prev);
      newSet.delete(questionId);
      return newSet;
    });
    
    // Reset text to original value
    const question = questions.find(q => q.id === questionId);
    setModeratorNoteTexts(prev => ({
      ...prev,
      [questionId]: question?.moderatorNote || ''
    }));
  };  /**
   * Save a moderator note
   */
  const saveModeratorNote = async (questionId: string) => {
    if (!canModerate) return;
    
    const noteText = moderatorNoteTexts[questionId]?.trim() || '';
    
    try {
      // Call API to save the note to the backend
      await questionService.updateQuestion(questionId, {
        presenter_notes: noteText || undefined
      });
      
      // Update local state only after successful API call
      setQuestions(prev => prev.map(q => 
        q.id === questionId 
          ? { ...q, moderatorNote: noteText || undefined }
          : q
      ));
      
      console.log('Moderator note saved successfully');
    } catch (error) {
      console.error('Failed to save moderator note:', error);
      alert('Failed to save note. Please try again.');
      return; // Don't update UI state if save failed
    }
    
    // Stop editing
    setEditingModeratorNotes(prev => {
      const newSet = new Set(prev);
      newSet.delete(questionId);
      return newSet;
    });
    
    // Keep the text in state for persistence
    if (!noteText) {
      setModeratorNoteTexts(prev => {
        const newTexts = { ...prev };
        delete newTexts[questionId];
        return newTexts;
      });
    }
  };
  /**
   * Update moderator note text as user types
   */
  const updateModeratorNoteText = (questionId: string, text: string) => {
    setModeratorNoteTexts(prev => ({
      ...prev,
      [questionId]: text
    }));
  };
  // Loading state with enhanced skeleton
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Navigation skeleton */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="h-6 w-32 bg-gray-200 rounded animate-pulse"></div>
              <div className="flex items-center space-x-4">
                <div className="h-4 w-24 bg-gray-200 rounded animate-pulse"></div>
                <div className="h-6 w-16 bg-gray-200 rounded-full animate-pulse"></div>
                <div className="h-4 w-20 bg-gray-200 rounded animate-pulse"></div>
              </div>
            </div>
          </div>
        </nav>
        
        {/* Header skeleton */}
        <EventHeaderSkeleton />
        
        {/* Content skeleton */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <QuestionCardSkeleton count={5} />
        </main>
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
              <div className="flex items-center space-x-3">
                {/* Share Link Button */}
                <button
                  onClick={() => {
                    if (event.share_url) {
                      navigator.clipboard.writeText(event.share_url);
                      // You could add a toast notification here
                      alert('Share link copied to clipboard!');
                    }
                  }}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  title="Copy share link"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                  </svg>
                  Share Link
                </button>
                <button
                  onClick={refreshQuestions}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  title="Refresh questions"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh
                </button>
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
              </div>
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
              { key: 'answered', label: 'Answered', count: questions.filter(q => q.is_answered).length },
              { key: 'starred', label: 'Starred', count: questions.filter(q => q.is_starred).length },
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
                  <div className="flex space-x-4">                    {/* Vote Section */}
                    <div className="flex flex-col items-center">                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleVote(question.id);
                        }}
                        className={`flex flex-col items-center p-3 rounded-lg transition-colors group ${
                          question.has_user_upvoted
                            ? 'bg-primary-100 text-primary-600'
                            : 'bg-gray-50 hover:bg-gray-100 text-gray-600'
                        }`}
                        title={question.has_user_upvoted ? "Remove your vote" : "Vote for this question"}
                      >
                        <FiArrowUp className="w-5 h-5" />
                        <span className="font-semibold text-lg">{question.upvotes}</span>
                        <span className="text-xs">votes</span>
                      </button>
                    </div>

                    {/* Question Content */}
                    <div className="flex-1">
                      {/* Question Text */}
                      <div className="mb-4">
                        <p className="text-gray-900 text-base leading-relaxed">{question.text}</p>
                        <div className="flex items-center mt-2 text-sm text-gray-500">
                          <span>by {question.is_anonymous ? 'Anonymous' : question.author.name}</span>
                          <span className="mx-2">•</span>
                          <span>{new Date(question.created_at).toLocaleDateString()}</span>
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
                      </div>                      {/* Moderator Note - Editable */}
                      {canModerate && (question.moderatorNote || editingModeratorNotes.has(question.id)) && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                          <div className="flex items-start">
                            <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                              <span className="text-blue-600 text-xs">📝</span>
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium text-blue-900">Moderator Note</h4>                                {!editingModeratorNotes.has(question.id) && canModerate && (
                                  <button
                                    onClick={() => startEditingNote(question.id)}
                                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                  >
                                    Edit
                                  </button>
                                )}
                              </div>
                              
                              {editingModeratorNotes.has(question.id) ? (
                                <div className="space-y-3">
                                  <textarea
                                    value={moderatorNoteTexts[question.id] || ''}
                                    onChange={(e) => updateModeratorNoteText(question.id, e.target.value)}
                                    placeholder="Add a note for this question..."
                                    className="w-full px-3 py-2 border border-blue-200 rounded-md text-sm text-blue-900 bg-white placeholder-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                                    rows={3}
                                  />
                                  <div className="flex items-center space-x-2">
                                    <button
                                      onClick={() => saveModeratorNote(question.id)}
                                      className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                                    >
                                      Save
                                    </button>
                                    <button
                                      onClick={() => cancelEditingNote(question.id)}
                                      className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
                                    >
                                      Cancel
                                    </button>
                                  </div>
                                </div>
                              ) : (
                                <p className="text-blue-800 text-sm">{question.moderatorNote}</p>
                              )}
                            </div>
                          </div>
                        </div>
                      )}                      {/* Add Note Button - Show when no note exists and not editing */}
                      {canModerate && !question.moderatorNote && !editingModeratorNotes.has(question.id) && (<div className="mb-4">
                          <button
                            onClick={() => startEditingNote(question.id)}
                            className="flex items-center space-x-2 px-3 py-2 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors border border-blue-200 hover:border-blue-300"
                          >
                            <span className="text-blue-600">📝</span>
                            <span>Add Note</span>
                          </button>
                        </div>
                      )}

                      {/* Related Questions - Now functional with expand/collapse */}
                      {question.relatedQuestions && question.relatedQuestions.length > 0 && (
                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">                          <div className="flex items-start">
                            <button 
                              onClick={() => toggleRelatedQuestions(question.id)}
                              className="w-6 h-6 bg-white border border-amber-300 rounded flex items-center justify-center mr-3 mt-0.5 hover:bg-amber-50 transition-colors"
                              title={expandedRelatedQuestions.has(question.id) ? "Collapse related questions" : "Expand related questions"}
                            >
                              {expandedRelatedQuestions.has(question.id) ? (
                                <FiMinus className="w-3 h-3 text-amber-600" />
                              ) : (
                                <FiPlus className="w-3 h-3 text-amber-600" />
                              )}
                            </button>
                            <div className="flex-1">
                              <button 
                                onClick={() => toggleRelatedQuestions(question.id)}
                                className="text-left hover:text-amber-800 transition-colors"
                              >
                                <h4 className="font-medium text-amber-900">
                                  {question.relatedQuestions.length} Related Question{question.relatedQuestions.length > 1 ? 's' : ''}
                                </h4>
                              </button>
                              
                              {/* Collapsible Related Questions List */}
                              {expandedRelatedQuestions.has(question.id) && (
                                <div className="mt-2 space-y-1">
                                  {question.relatedQuestions.map((relatedQ, index) => (
                                    <p key={index} className="text-amber-800 text-sm">
                                      {index + 1}. {relatedQ}
                                    </p>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )}                      {/* Answer Display */}
                      {question.is_answered && question.answer && (
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
                      <div className="flex flex-col space-y-2">                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            handleStar(question.id);
                          }}
                          className={`p-2 rounded-lg transition-colors tooltip ${
                            question.is_starred
                              ? 'bg-yellow-100 text-yellow-600 border border-yellow-200'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-200'
                          }`}
                          title={question.is_starred ? 'Remove from starred' : 'Add to starred'}
                        >
                          <FiStar className={`w-4 h-4 ${question.is_starred ? 'fill-current' : ''}`} />
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
                            question.is_answered
                              ? 'bg-green-100 text-green-600 border border-green-200'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-200'
                          }`}
                          title={question.is_answered ? 'Mark as unanswered' : 'Mark as answered'}
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
