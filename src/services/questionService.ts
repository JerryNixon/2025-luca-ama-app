import apiClient from '@/lib/api';
import { Question, CreateQuestionForm, QuestionFilters, ApiResponse, PaginatedResponse } from '@/types';

export const questionService = {
  // Get questions for an event
  async getQuestions(eventId: string, filters?: QuestionFilters): Promise<Question[]> {
    const params = new URLSearchParams();
    if (filters?.keyword) params.append('keyword', filters.keyword);
    if (filters?.author) params.append('author', filters.author);
    if (filters?.isAnswered !== undefined) params.append('answered', String(filters.isAnswered));
    if (filters?.isStarred !== undefined) params.append('starred', String(filters.isStarred));
    if (filters?.sortBy) params.append('sort_by', filters.sortBy);
    if (filters?.sortOrder) params.append('sort_order', filters.sortOrder);

    const response = await apiClient.get<ApiResponse<Question[]>>(
      `/events/${eventId}/questions/?${params.toString()}`
    );
    return response.data.data;
  },

  // Get a specific question
  async getQuestion(questionId: string): Promise<Question> {
    const response = await apiClient.get<ApiResponse<Question>>(`/questions/${questionId}/`);
    return response.data.data;
  },

  // Create a new question
  async createQuestion(eventId: string, questionData: CreateQuestionForm): Promise<Question> {
    const response = await apiClient.post<ApiResponse<Question>>(
      `/events/${eventId}/questions/`,
      questionData
    );
    return response.data.data;
  },

  // Update a question
  async updateQuestion(questionId: string, questionData: Partial<CreateQuestionForm>): Promise<Question> {
    const response = await apiClient.put<ApiResponse<Question>>(`/questions/${questionId}/`, questionData);
    return response.data.data;
  },

  // Delete a question
  async deleteQuestion(questionId: string): Promise<void> {
    await apiClient.delete(`/questions/${questionId}/`);
  },

  // Upvote a question
  async upvoteQuestion(questionId: string): Promise<Question> {
    const response = await apiClient.post<ApiResponse<Question>>(`/questions/${questionId}/upvote/`);
    return response.data.data;
  },

  // Remove upvote from a question
  async removeUpvote(questionId: string): Promise<Question> {
    const response = await apiClient.delete<ApiResponse<Question>>(`/questions/${questionId}/upvote/`);
    return response.data.data;
  },

  // Mark question as answered
  async markAsAnswered(questionId: string, isAnswered: boolean): Promise<Question> {
    const response = await apiClient.patch<ApiResponse<Question>>(`/questions/${questionId}/`, {
      isAnswered
    });
    return response.data.data;
  },

  // Star/unstar a question
  async toggleStar(questionId: string, isStarred: boolean): Promise<Question> {
    const response = await apiClient.patch<ApiResponse<Question>>(`/questions/${questionId}/`, {
      isStarred
    });
    return response.data.data;
  },

  // Stage/unstage a question
  async toggleStage(questionId: string, isStaged: boolean): Promise<Question> {
    const response = await apiClient.patch<ApiResponse<Question>>(`/questions/${questionId}/`, {
      isStaged
    });
    return response.data.data;
  },

  // Add presenter notes
  async addPresenterNotes(questionId: string, notes: string): Promise<Question> {
    const response = await apiClient.patch<ApiResponse<Question>>(`/questions/${questionId}/`, {
      presenterNotes: notes
    });
    return response.data.data;
  },

  // Get AI summary for question
  async getAISummary(questionId: string): Promise<string> {
    const response = await apiClient.post<ApiResponse<{ summary: string }>>(`/questions/${questionId}/ai-summary/`);
    return response.data.data.summary;
  },
};
