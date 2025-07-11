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
  
  // New fields for Microsoft Entra ID and admin system
  microsoft_id?: string;         // Optional: Microsoft Entra ID identifier
  is_admin?: boolean;            // Whether this user is a system admin
  can_create_events?: boolean;   // Whether this user can create events
  is_system_admin?: boolean;     // Whether this user is a system admin
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
  share_link?: string;           // Optional: shareable link code for others to join
  share_url?: string;            // Optional: full shareable URL for others to join
  invite_link?: string;          // Optional: invite link for private events
  is_active: boolean;            // Whether the event is currently active
  is_public?: boolean;           // Whether the event is public or private
  created_at: Date;              // When this event was created
  updated_at: Date;              // When this event was last modified
  question_count?: number;       // Number of questions for this event
  
  // New permission fields for role-based access
  user_role_in_event: 'admin' | 'creator' | 'moderator' | 'participant' | 'no_access';
  can_user_moderate: boolean;
  can_user_access: boolean;
  is_created_by_user: boolean;
  user_permissions: {
    can_view: boolean;
    can_ask_questions: boolean;
    can_vote: boolean;
    can_moderate: boolean;
    can_edit_event: boolean;
    can_delete_event: boolean;
    can_add_moderators: boolean;
    view_type: 'no_access' | 'user' | 'moderator';
  };
}

// ==============================================================================
// QUESTION TYPES - The heart of the AMA system
// ==============================================================================

// Question interface - represents a question asked during an AMA
export interface Question {
  id: string;                      // Unique identifier for the question
  event: string;                   // Which event this question belongs to
  text: string;                    // The actual question content
  author: User;                    // Who asked this question
  is_anonymous: boolean;           // Whether the author chose to be anonymous
  upvotes: number;                 // How many people upvoted this question
  has_user_upvoted: boolean;       // Whether the current user has upvoted this
  is_answered: boolean;            // Whether this question has been answered
  is_starred: boolean;             // Whether moderators marked this as important
  is_staged: boolean;              // Whether this is currently being discussed
  presenter_notes?: string;        // Optional: notes for moderators/presenters only
  ai_summary?: string;             // Optional: AI-generated summary of the question
  parent_question?: string;        // Optional: if this is grouped under another question
  grouped_questions?: Question[];  // Optional: similar questions grouped under this one
  tags: string[];                  // Keywords/categories for this question
  created_at: string | Date;       // When this question was asked
  updated_at: string | Date;       // When this question was last modified
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
  open_date?: string;            // Optional: when questions can start (ISO string)
  close_date?: string;           // Optional: when event ends (ISO string)
}

export interface CreateQuestionForm {
  text: string;
  is_anonymous: boolean;
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
  microsoftLogin: (code: string) => Promise<void>;
  getMicrosoftOAuthUrl: () => Promise<string>;
  checkUserExists: (email: string) => Promise<boolean>;
  isLoading: boolean;
  isAuthenticated: boolean;
}
