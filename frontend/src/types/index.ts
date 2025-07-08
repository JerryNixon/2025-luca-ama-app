// ==============================================================================
// TYPE DEFINITIONS - The foundation of our TypeScript application
// ==============================================================================
// This file defines all the data structures used throughout the application.
// TypeScript interfaces ensure type safety and better code documentation.

// ==============================================================================
// USER TYPES - Defining the three personas in our AMA system
// ==============================================================================

// User roles enum - defines the three types of users in our system
// - 'user': Regular participants who ask questions and vote
// - 'presenter': People answering questions during AMA sessions  
// - 'moderator': Admins who manage events and moderate content
export type UserRole = 'moderator' | 'presenter' | 'user';

// User interface - represents a person using the AMA system
export interface User {
  id: string;                    // Unique identifier for the user
  email: string;                 // User's email address (for login)
  name: string;                  // Display name shown in the UI
  role: UserRole;                // Their permission level (moderator/presenter/user)
  isAnonymous?: boolean;         // Optional: if this user chose to be anonymous
}

// ==============================================================================
// EVENT TYPES - AMA sessions/meetings structure
// ==============================================================================

// Event interface - represents an AMA session or meeting
export interface Event {
  id: string;                    // Unique identifier for the event
  name: string;                  // Event title (e.g., "Town Hall Q&A")
  open_date?: Date;              // Optional: when questions can start being submitted
  close_date?: Date;             // Optional: when the event ends
  created_by: any;               // User object who created this event
  moderators: any[];             // Array of user objects who can moderate this event
  participants: any[];           // Array of user objects who have joined this event
  share_link?: string;           // Optional: shareable link for others to join
  is_active: boolean;            // Whether the event is currently active
  created_at: Date;              // When this event was created
  updated_at: Date;              // When this event was last modified
  question_count?: number;       // Number of questions for this event
}

// ==============================================================================
// QUESTION TYPES - The heart of the AMA system
// ==============================================================================

// Question interface - represents a question asked during an AMA
export interface Question {
  id: string;                    // Unique identifier for the question
  eventId: string;               // Which event this question belongs to
  text: string;                  // The actual question content
  author: User;                  // Who asked this question
  isAnonymous: boolean;          // Whether the author chose to be anonymous
  upvotes: number;               // How many people upvoted this question
  hasUserUpvoted: boolean;       // Whether the current user has upvoted this
  isAnswered: boolean;           // Whether this question has been answered
  isStarred: boolean;            // Whether moderators marked this as important
  isStaged: boolean;             // Whether this is currently being discussed
  presenterNotes?: string;       // Optional: notes for moderators/presenters only
  aiSummary?: string;            // Optional: AI-generated summary of the question
  parentQuestionId?: string;     // Optional: if this is grouped under another question
  groupedQuestions?: Question[]; // Optional: similar questions grouped under this one
  tags: string[];                // Keywords/categories for this question
  createdAt: Date;               // When this question was asked
  updatedAt: Date;               // When this question was last modified
}

// ==============================================================================
// VOTING SYSTEM TYPES - Tracking who voted on what
// ==============================================================================

// Vote interface - represents when a user upvotes a question
export interface Vote {
  id: string;                    // Unique identifier for this vote
  questionId: string;            // Which question was voted on
  userId: string;                // Who cast this vote
  createdAt: Date;               // When the vote was cast
}

// ==============================================================================
// API COMMUNICATION TYPES - How frontend talks to backend
// ==============================================================================

// Generic API response wrapper - consistent format for all API responses
export interface ApiResponse<T> {
  data: T;                       // The actual data being returned
  message?: string;              // Optional success/info message
  success: boolean;              // Whether the request was successful
}

// Paginated response - for handling large lists of data
export interface PaginatedResponse<T> {
  data: T[];                     // Array of items for current page
  totalCount: number;            // Total number of items across all pages
  page: number;                  // Current page number (1-based)
  pageSize: number;              // Number of items per page
  totalPages: number;            // Total number of pages available
}

// ==============================================================================
// FILTERING AND SEARCH TYPES - How users find specific content
// ==============================================================================

// Question filters - options for searching and filtering questions
export interface QuestionFilters {
  keyword?: string;              // Search within question text
  author?: string;               // Filter by who asked the question
  isAnswered?: boolean;          // Show only answered/unanswered questions
  isStarred?: boolean;           // Show only starred questions
  sortBy?: 'votes' | 'date' | 'author';  // How to sort the results
  sortOrder?: 'asc' | 'desc';    // Ascending or descending order
}

// ==============================================================================
// FORM TYPES - Data structures for user input forms
// ==============================================================================

// Event creation form - data needed to create a new AMA event
export interface CreateEventForm {
  name: string;                  // Event name (required)
  openDate?: Date;               // Optional: when questions can start
  closeDate?: Date;              // Optional: when event ends
}

export interface CreateQuestionForm {
  text: string;
  isAnonymous: boolean;
  tags?: string[];
}

export interface LoginForm {
  email: string;
  password: string;
}

// Auth context interface
export interface AuthContextType {
  user: User | null;
  login: (credentials: LoginForm) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}
