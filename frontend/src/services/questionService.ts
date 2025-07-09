// Question Service - API service layer for question management operations
// This service handles all question-related API calls including CRUD operations, voting, and moderation

// Import the configured API client for making HTTP requests
import apiClient from '@/lib/api';
// Import TypeScript types for type safety
import { Question, CreateQuestionForm, QuestionFilters, ApiResponse, PaginatedResponse } from '@/types';

/**
 * Question Service Object
 * 
 * Provides methods for all question management operations including:
 * - Retrieving questions with filtering and sorting
 * - Creating, updating, and deleting questions
 * - Voting functionality (upvotes)
 * - Moderation features (starring, staging, marking as answered)
 * - Presenter notes management
 * - AI-powered question analysis
 * 
 * All methods return promises and handle API communication with proper error handling.
 */
export const questionService = {
  
  /**
   * Get Questions for Event
   * 
   * Retrieves all questions for a specific event with optional filtering and sorting.
   * Supports various filters to help moderators and participants find relevant questions.
   * 
   * @param eventId - Unique identifier of the event
   * @param filters - Optional filtering and sorting criteria
   * @returns Promise resolving to array of Question objects
   * @throws Error if event doesn't exist or user doesn't have access
   */
  async getQuestions(eventId: string, filters?: QuestionFilters): Promise<Question[]> {
    // Build query parameters from filter options
    const params = new URLSearchParams();
    
    // Add keyword search filter if provided
    if (filters?.keyword) params.append('keyword', filters.keyword);
    
    // Add author filter if provided
    if (filters?.author) params.append('author', filters.author);
    
    // Add answered status filter if specified
    if (filters?.isAnswered !== undefined) params.append('answered', String(filters.isAnswered));
    
    // Add starred status filter if specified
    if (filters?.isStarred !== undefined) params.append('starred', String(filters.isStarred));
    
    // Add sorting criteria if provided
    if (filters?.sortBy) params.append('sort_by', filters.sortBy);
    if (filters?.sortOrder) params.append('sort_order', filters.sortOrder);

    // Make request with constructed query parameters
    const response = await apiClient.get<Question[]>(
      `/events/${eventId}/questions/?${params.toString()}`
    );
    
    // DRF returns data directly, not wrapped
    return response.data;
  },

  /**
   * Get Specific Question
   * 
   * Retrieves detailed information for a specific question by its ID.
   * Includes all question data, metadata, votes, and moderation status.
   * 
   * @param questionId - Unique identifier of the question
   * @returns Promise resolving to Question object
   * @throws Error if question doesn't exist or user doesn't have access
   */
  async getQuestion(questionId: string): Promise<Question> {
    const response = await apiClient.get<Question>(`/questions/${questionId}/`);
    return response.data;
  },

  /**
   * Create New Question
   * 
   * Creates a new question for a specific event.
   * All authenticated users can create questions in active events.
   * 
   * @param eventId - Unique identifier of the event to add question to
   * @param questionData - Question creation form data including text and settings
   * @returns Promise resolving to the created Question object
   * @throws Error if event is closed or user lacks permissions
   */
  async createQuestion(eventId: string, questionData: CreateQuestionForm): Promise<Question> {
    const response = await apiClient.post<Question>(
      `/events/${eventId}/questions/`,
      questionData
    );
    return response.data;
  },

  /**
   * Update Existing Question
   * 
   * Updates an existing question with new information.
   * Only question authors can update their own questions before they're answered.
   * 
   * @param questionId - Unique identifier of the question to update
   * @param questionData - Partial question data containing fields to update
   * @returns Promise resolving to the updated Question object
   * @throws Error if question doesn't exist or user lacks permissions
   */
  async updateQuestion(questionId: string, questionData: Partial<Question>): Promise<Question> {
    const response = await apiClient.patch<Question>(`/questions/${questionId}/`, questionData);
    return response.data;
  },

  /**
   * Delete Question
   * 
   * Permanently deletes a question and all associated data.
   * Only question authors and moderators can delete questions.
   * This action cannot be undone.
   * 
   * @param questionId - Unique identifier of the question to delete
   * @returns Promise that resolves when deletion is complete
   * @throws Error if question doesn't exist or user lacks permissions
   */
  async deleteQuestion(questionId: string): Promise<void> {
    await apiClient.delete(`/questions/${questionId}/`);
  },

  /**
   * Upvote Question
   * 
   * Adds an upvote to a question to show support or interest.
   * Users cannot upvote their own questions and can only upvote once per question.
   * 
   * @param questionId - Unique identifier of the question to upvote
   * @returns Promise resolving to the updated Question object with new vote count
   * @throws Error if user already upvoted or question doesn't exist
   */
  async upvoteQuestion(questionId: string): Promise<Question> {
    const response = await apiClient.post<Question>(`/questions/${questionId}/upvote/`);
    return response.data;
  },

  /**
   * Remove Upvote
   * 
   * Removes a user's upvote from a question.
   * Only users who have previously upvoted can remove their vote.
   * 
   * @param questionId - Unique identifier of the question to remove upvote from
   * @returns Promise resolving to the updated Question object with new vote count
   * @throws Error if user hasn't upvoted or question doesn't exist
   */
  async removeUpvote(questionId: string): Promise<Question> {
    const response = await apiClient.delete<Question>(`/questions/${questionId}/upvote/`);
    return response.data;
  },

  /**
   * Mark Question as Answered
   * 
   * Updates the answered status of a question.
   * Only moderators and presenters can mark questions as answered/unanswered.
   * 
   * @param questionId - Unique identifier of the question
   * @param isAnswered - Whether the question should be marked as answered
   * @returns Promise resolving to the updated Question object
   * @throws Error if user lacks moderation permissions
   */
  async markAsAnswered(questionId: string, isAnswered: boolean): Promise<Question> {
    const response = await apiClient.patch<Question>(`/questions/${questionId}/`, {
      isAnswered
    });
    return response.data;
  },

  /**
   * Toggle Star Status
   * 
   * Stars or unstars a question to mark it as important or noteworthy.
   * Only moderators and presenters can star questions.
   * Starred questions are typically prioritized for answering.
   * 
   * @param questionId - Unique identifier of the question
   * @param isStarred - Whether the question should be starred
   * @returns Promise resolving to the updated Question object
   * @throws Error if user lacks moderation permissions
   */
  async toggleStar(questionId: string, isStarred: boolean): Promise<Question> {
    const response = await apiClient.patch<Question>(`/questions/${questionId}/`, {
      isStarred
    });
    return response.data;
  },

  /**
   * Toggle Stage Status
   * 
   * Stages or unstages a question for presentation.
   * Only one question can be staged at a time - it represents the current topic.
   * Only moderators and presenters can stage questions.
   * 
   * @param questionId - Unique identifier of the question
   * @param isStaged - Whether the question should be staged
   * @returns Promise resolving to the updated Question object
   * @throws Error if user lacks moderation permissions or another question is staged
   */
  async toggleStage(questionId: string, isStaged: boolean): Promise<Question> {
    const response = await apiClient.patch<ApiResponse<Question>>(`/questions/${questionId}/`, {
      isStaged
    });
    return response.data.data;
  },

  /**
   * Add Presenter Notes
   * 
   * Adds private notes to a question for presenter reference.
   * These notes are only visible to moderators and presenters.
   * Helps with question preparation and context.
   * 
   * @param questionId - Unique identifier of the question
   * @param notes - Private notes text for the presenter
   * @returns Promise resolving to the updated Question object
   * @throws Error if user lacks moderation permissions
   */
  async addPresenterNotes(questionId: string, notes: string): Promise<Question> {
    const response = await apiClient.patch<ApiResponse<Question>>(`/questions/${questionId}/`, {
      presenterNotes: notes
    });
    return response.data.data;
  },

  /**
   * Get AI Summary
   * 
   * Requests an AI-generated summary or analysis of a question.
   * Helps presenters quickly understand complex questions or identify themes.
   * Only available to moderators and presenters.
   * 
   * @param questionId - Unique identifier of the question to analyze
   * @returns Promise resolving to the AI-generated summary text
   * @throws Error if AI service is unavailable or user lacks permissions
   */
  async getAISummary(questionId: string): Promise<string> {
    const response = await apiClient.post<ApiResponse<{ summary: string }>>(`/questions/${questionId}/ai-summary/`);
    return response.data.data.summary;
  },
};
