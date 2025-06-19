// Demo Data Service - Mock data and services for development and testing
// This module provides realistic demo data and simulates API responses for frontend development

// Import TypeScript types for type safety
import { Event, Question, User } from '@/types';

/**
 * Demo Users Collection
 * 
 * Predefined user accounts representing different roles in the AMA system:
 * - User: Basic participant who can ask questions and vote
 * - Presenter: Can manage questions and moderate events
 * - Moderator: Full administrative control over events and questions
 */
export const demoUsers: User[] = [
  {
    id: '1',
    email: 'demo@microsoft.com',
    name: 'Demo User',
    role: 'user',                // Basic user role - can participate and ask questions
  },
  {
    id: '2',
    email: 'presenter@microsoft.com',
    name: 'Jane Presenter',
    role: 'presenter',           // Presenter role - can moderate questions during events
  },
  {
    id: '3',
    email: 'moderator@microsoft.com',
    name: 'John Moderator',
    role: 'moderator',           // Moderator role - full administrative control
  },
];

/**
 * Demo Events Collection
 * 
 * Sample AMA events with different states and configurations:
 * - Active and inactive events
 * - Different time ranges and participants
 * - Various moderator configurations
 */
export const demoEvents: Event[] = [
  {
    id: '1',
    name: 'Microsoft Q4 All-Hands',                    // Quarterly company-wide meeting
    openDate: new Date('2025-06-15T09:00:00'),        // When questions start being accepted
    closeDate: new Date('2025-06-20T17:00:00'),       // When question submission closes
    createdBy: '3',                                    // Created by John Moderator
    moderators: ['3'],                                 // Moderator IDs who can manage this event
    participants: ['1', '2', '3'],                    // All user IDs who have joined
    shareLink: 'https://ama.microsoft.com/join/q4-all-hands',  // Public join link
    isActive: true,                                    // Currently accepting questions
    createdAt: new Date('2025-06-10T10:00:00'),      // When event was created
    updatedAt: new Date('2025-06-15T10:00:00'),      // Last modification
  },
  {
    id: '2',
    name: 'Azure Team Sync',                          // Team-specific technical discussion
    openDate: new Date('2025-06-18T14:00:00'),
    closeDate: new Date('2025-06-18T16:00:00'),       // Short 2-hour window
    createdBy: '2',                                    // Created by Jane Presenter
    moderators: ['2', '3'],                           // Multiple moderators
    participants: ['1', '2', '3'],
    shareLink: 'https://ama.microsoft.com/join/azure-sync',
    isActive: true,
    createdAt: new Date('2025-06-12T14:00:00'),
    updatedAt: new Date('2025-06-16T14:00:00'),
  },
  {
    id: '3',
    name: 'Product Roadmap Discussion',               // Future planning session
    openDate: new Date('2025-06-25T10:00:00'),
    closeDate: new Date('2025-06-25T12:00:00'),
    createdBy: '3',
    moderators: ['3'],
    participants: ['1', '2', '3'],
    shareLink: 'https://ama.microsoft.com/join/product-roadmap',
    isActive: false,                                  // Not currently active
    createdAt: new Date('2025-06-14T10:00:00'),
    updatedAt: new Date('2025-06-14T10:00:00'),
  },
];

/**
 * Demo Questions Collection
 * 
 * Sample questions demonstrating various states and features:
 * - Answered and unanswered questions
 * - Starred and staged questions
 * - Questions with different vote counts
 * - Anonymous and named questions
 * - Questions with presenter notes and AI summaries
 */
export const demoQuestions: Question[] = [
  {
    id: '1',
    eventId: '1',                                     // Belongs to Microsoft Q4 All-Hands event
    text: 'What are the key priorities for Microsoft in 2025?',
    author: demoUsers[0],                             // Asked by Demo User
    isAnonymous: false,                               // Public authorship
    upvotes: 15,                                      // High engagement question
    hasUserUpvoted: false,                            // Current user hasn't upvoted
    isAnswered: false,                                // Still pending response
    isStarred: true,                                  // Marked as important by moderator
    isStaged: true,                                   // Currently being presented
    presenterNotes: 'Focus on AI integration and cloud services',  // Private moderator notes
    aiSummary: 'Question about Microsoft strategic priorities for the upcoming year',
    tags: ['strategy', 'priorities', '2025'],        // Categorization tags
    createdAt: new Date('2025-06-15T09:30:00'),
    updatedAt: new Date('2025-06-17T14:20:00'),      // Updated when starred/staged
  },
  {
    id: '2',
    eventId: '1',
    text: 'How will the new AI features impact our daily workflow?',
    author: demoUsers[1],                             // Asked by Jane Presenter
    isAnonymous: false,
    upvotes: 12,
    hasUserUpvoted: true,                             // Current user has upvoted this
    isAnswered: true,                                 // Already answered
    isStarred: false,
    isStaged: false,
    aiSummary: 'Question about AI impact on workplace productivity',
    tags: ['ai', 'workflow', 'productivity'],
    createdAt: new Date('2025-06-15T10:15:00'),
    updatedAt: new Date('2025-06-16T11:30:00'),
  },
  {
    id: '3',
    eventId: '1',
    text: 'Can we expect more remote work flexibility policies?',
    author: demoUsers[0],
    isAnonymous: true,                                // Anonymous question
    upvotes: 8,
    hasUserUpvoted: false,
    isAnswered: false,
    isStarred: false,
    isStaged: false,
    tags: ['remote-work', 'policy', 'flexibility'],
    createdAt: new Date('2025-06-15T11:00:00'),
    updatedAt: new Date('2025-06-15T11:00:00'),
  },
  {
    id: '4',
    eventId: '2',                                     // Belongs to Azure Team Sync event
    text: 'What are the latest updates on Azure security features?',
    author: demoUsers[2],                             // Asked by John Moderator
    isAnonymous: false,
    upvotes: 6,
    hasUserUpvoted: false,
    isAnswered: false,
    isStarred: true,                                  // Important technical question
    isStaged: false,
    presenterNotes: 'Cover Zero Trust architecture and new compliance features',
    tags: ['azure', 'security', 'compliance'],
    createdAt: new Date('2025-06-16T09:00:00'),
    updatedAt: new Date('2025-06-16T09:00:00'),
  },
  {
    id: '5',
    eventId: '1',
    text: 'How is Microsoft handling sustainability initiatives?',
    author: demoUsers[1],
    isAnonymous: false,
    upvotes: 10,
    hasUserUpvoted: false,
    isAnswered: false,
    isStarred: false,
    isStaged: false,
    tags: ['sustainability', 'environment', 'corporate-responsibility'],
    createdAt: new Date('2025-06-15T12:30:00'),
    updatedAt: new Date('2025-06-15T12:30:00'),
  },
];

/**
 * Demo Service Object
 * 
 * Simulates backend API functionality for development and testing.
 * Provides realistic delays and responses that match the real API interface.
 * All methods return promises to simulate asynchronous API calls.
 */
export const demoService = {  /**
   * Get Current User
   * 
   * Simulates retrieving the currently authenticated user.
   * In a real application, this would validate the JWT token.
   * Only returns a user if there's a valid demo token in localStorage.
   * 
   * @returns Currently authenticated user object or null if not authenticated
   */
  getCurrentUser: (): User | null => {
    // Check if there's a valid demo token
    const token = localStorage.getItem('demo_token');
    if (!token) {
      return null; // No token, user is not authenticated
    }
    
    // In a real app, we would validate the token here
    // For demo purposes, we just check if token exists
    return demoUsers[0]; // Return demo user if token exists
  },

  /**
   * User Authentication
   * 
   * Simulates login with email and password validation.
   * Includes realistic API delay and error handling.
   * 
   * @param email - User's email address
   * @param password - User's password (demo accepts 'demo123' for all users)
   * @returns Promise resolving to user object and authentication token
   * @throws Error if credentials are invalid
   */
  login: async (email: string, password: string): Promise<{ user: User; token: string }> => {
    // Simulate network delay for realistic UX testing
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Find user by email in demo database
    const user = demoUsers.find(u => u.email === email);
    if (!user || password !== 'demo123') {
      throw new Error('Invalid credentials');
    }    return {
      user,
      token: 'demo-jwt-token-' + user.id,    // Mock JWT token
    };
  },

  /**
   * User Logout
   * 
   * Simulates logout by clearing the demo token from localStorage.
   * 
   * @returns Promise resolving when logout is complete
   */
  logout: async (): Promise<void> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Clear the demo token
    localStorage.removeItem('demo_token');
  },

  /**
   * Get All Events
   * 
   * Simulates retrieving all events the current user has access to.
   * 
   * @returns Promise resolving to array of events
   */
  getEvents: async (): Promise<Event[]> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return demoEvents;
  },

  /**
   * Get Specific Event
   * 
   * Simulates retrieving a single event by ID.
   * 
   * @param id - Event ID to retrieve
   * @returns Promise resolving to event object
   * @throws Error if event doesn't exist
   */
  getEvent: async (id: string): Promise<Event> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const event = demoEvents.find(e => e.id === id);
    if (!event) throw new Error('Event not found');
    return event;
  },

  /**
   * Get Questions for Event
   * 
   * Simulates retrieving all questions for a specific event.
   * 
   * @param eventId - Event ID to get questions for
   * @returns Promise resolving to array of questions
   */
  getQuestions: async (eventId: string): Promise<Question[]> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return demoQuestions.filter(q => q.eventId === eventId);
  },

  /**
   * Create New Question
   * 
   * Simulates creating a new question for an event.
   * 
   * @param eventId - Event ID to add question to
   * @param text - Question text content
   * @param isAnonymous - Whether the question should be anonymous
   * @returns Promise resolving to created question object
   */
  createQuestion: async (eventId: string, text: string, isAnonymous: boolean): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Create new question object with default values
    const newQuestion: Question = {
      id: Date.now().toString(),              // Simple ID generation for demo
      eventId,
      text,
      author: demoUsers[0],                   // Default to current demo user
      isAnonymous,
      upvotes: 0,                             // Start with no votes
      hasUserUpvoted: false,                  // User hasn't voted on their own question
      isAnswered: false,                      // New questions are unanswered
      isStarred: false,                       // Not starred by default
      isStaged: false,                        // Not staged by default
      tags: [],                               // No tags initially
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    // Add to demo database
    demoQuestions.push(newQuestion);
    return newQuestion;
  },

  /**
   * Toggle Question Upvote
   * 
   * Simulates upvoting or removing upvote from a question.
   * Implements proper vote counting logic.
   * 
   * @param questionId - Question ID to toggle vote on
   * @returns Promise resolving to updated question object
   * @throws Error if question doesn't exist
   */
  toggleUpvote: async (questionId: string): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const question = demoQuestions.find(q => q.id === questionId);
    if (!question) throw new Error('Question not found');

    // Toggle upvote status and update count
    if (question.hasUserUpvoted) {
      question.upvotes--;
      question.hasUserUpvoted = false;
    } else {
      question.upvotes++;
      question.hasUserUpvoted = true;
    }

    question.updatedAt = new Date();
    return question;
  },

  /**
   * Toggle Question Star Status
   * 
   * Simulates starring or unstarring a question (moderator action).
   * 
   * @param questionId - Question ID to toggle star on
   * @returns Promise resolving to updated question object
   * @throws Error if question doesn't exist
   */
  toggleStar: async (questionId: string): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const question = demoQuestions.find(q => q.id === questionId);
    if (!question) throw new Error('Question not found');

    question.isStarred = !question.isStarred;
    question.updatedAt = new Date();
    return question;
  },

  /**
   * Toggle Question Stage Status
   * 
   * Simulates staging or unstaging a question for presentation.
   * Only one question can be staged at a time per event.
   * 
   * @param questionId - Question ID to toggle stage status
   * @returns Promise resolving to updated question object
   * @throws Error if question doesn't exist
   */
  toggleStage: async (questionId: string): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Find the question to stage/unstage
    const question = demoQuestions.find(q => q.id === questionId);
    if (!question) throw new Error('Question not found');    // Unstage any other questions in the same event (only one can be staged)
    const eventQuestions = demoQuestions.filter(q => q.eventId === question.eventId);
    eventQuestions.forEach(q => {
      if (q.id !== questionId) {
        q.isStaged = false;              // Unstage other questions
      }
    });

    // Toggle the target question's stage status
    question.isStaged = !question.isStaged;
    question.updatedAt = new Date();
    return question;
  },

  /**
   * Toggle Question Answered Status
   * 
   * Simulates marking a question as answered or unanswered (moderator action).
   * 
   * @param questionId - Question ID to toggle answered status
   * @returns Promise resolving to updated question object
   * @throws Error if question doesn't exist
   */
  toggleAnswer: async (questionId: string): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const question = demoQuestions.find(q => q.id === questionId);
    if (!question) throw new Error('Question not found');

    question.isAnswered = !question.isAnswered;
    question.updatedAt = new Date();
    return question;
  },
};
