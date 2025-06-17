import apiClient from '@/lib/api';
import { Event, CreateEventForm, ApiResponse } from '@/types';

export const eventService = {
  // Get all events for the user
  async getEvents(): Promise<Event[]> {
    const response = await apiClient.get<ApiResponse<Event[]>>('/events/');
    return response.data.data;
  },

  // Get a specific event by ID
  async getEvent(id: string): Promise<Event> {
    const response = await apiClient.get<ApiResponse<Event>>(`/events/${id}/`);
    return response.data.data;
  },

  // Create a new event
  async createEvent(eventData: CreateEventForm): Promise<Event> {
    const response = await apiClient.post<ApiResponse<Event>>('/events/', eventData);
    return response.data.data;
  },

  // Update an event
  async updateEvent(id: string, eventData: Partial<CreateEventForm>): Promise<Event> {
    const response = await apiClient.put<ApiResponse<Event>>(`/events/${id}/`, eventData);
    return response.data.data;
  },

  // Delete an event
  async deleteEvent(id: string): Promise<void> {
    await apiClient.delete(`/events/${id}/`);
  },

  // Generate share link for event
  async generateShareLink(id: string): Promise<string> {
    const response = await apiClient.post<ApiResponse<{ shareLink: string }>>(`/events/${id}/share/`);
    return response.data.data.shareLink;
  },

  // Join event via share link
  async joinEvent(shareToken: string): Promise<Event> {
    const response = await apiClient.post<ApiResponse<Event>>(`/events/join/${shareToken}/`);
    return response.data.data;
  },
};
