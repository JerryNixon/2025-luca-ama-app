// User roles
export type UserRole = 'moderator' | 'presenter' | 'user';

// User interface
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  isAnonymous?: boolean;
}

// Event interface
export interface Event {
  id: string;
  name: string;
  openDate?: Date;
  closeDate?: Date;
  createdBy: string;
  moderators: string[];
  participants: string[];
  shareLink?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Question interface
export interface Question {
  id: string;
  eventId: string;
  text: string;
  author: User;
  isAnonymous: boolean;
  upvotes: number;
  hasUserUpvoted: boolean;
  isAnswered: boolean;
  isStarred: boolean;
  isStaged: boolean;
  presenterNotes?: string;
  aiSummary?: string;
  parentQuestionId?: string;
  groupedQuestions?: Question[];
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

// Vote interface
export interface Vote {
  id: string;
  questionId: string;
  userId: string;
  createdAt: Date;
}

// API Response interfaces
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  totalCount: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Filter and sort options
export interface QuestionFilters {
  keyword?: string;
  author?: string;
  isAnswered?: boolean;
  isStarred?: boolean;
  sortBy?: 'votes' | 'date' | 'author';
  sortOrder?: 'asc' | 'desc';
}

// Form interfaces
export interface CreateEventForm {
  name: string;
  openDate?: Date;
  closeDate?: Date;
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
