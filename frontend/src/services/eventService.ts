// Event Service - API service layer for event management operations
// This service handles all event-related API calls including CRUD operations and sharing

// Import the configured API client for making HTTP requests
import apiClient from '@/lib/api';
// Import TypeScript types for type safety
import { Event, CreateEventForm, ApiResponse } from '@/types';

/**
 * Event Service Object
 * 
 * Provides methods for all event management operations including:
 * - Retrieving events (all events and individual events)
 * - Creating new AMA events
 * - Updating existing events
 * - Deleting events
 * - Generating and using share links
 * - Event participation management
 * 
 * All methods return promises and handle API communication with proper error handling.
 */
export const eventService = {
  
  /**
   * Get All Events
   * 
   * Retrieves all events that the current user has access to.
   * This includes events they created, moderate, or participate in.
   * 
   * @returns Promise resolving to array of Event objects
   * @throws Error if API request fails or user is not authenticated
   */
  async getEvents(): Promise<Event[]> {
    // Request all events from the server
    // Authentication token is automatically included by the API client
    const response = await apiClient.get<ApiResponse<Event[]>>('/events/');
    return response.data.data;
  },

  /**
   * Get Specific Event
   * 
   * Retrieves detailed information for a specific event by its ID.
   * Includes all event data, questions, participants, and metadata.
   * 
   * @param id - Unique identifier of the event to retrieve
   * @returns Promise resolving to Event object
   * @throws Error if event doesn't exist or user doesn't have access
   */
  async getEvent(id: string): Promise<Event> {
    // Request specific event data from the server
    const response = await apiClient.get<ApiResponse<Event>>(`/events/${id}/`);
    return response.data.data;
  },

  /**
   * Create New Event
   * 
   * Creates a new AMA event with the provided configuration.
   * Only moderators and presenters can create events.
   * 
   * @param eventData - Event creation form data including name, dates, and settings
   * @returns Promise resolving to the created Event object
   * @throws Error if user lacks permissions or data validation fails
   */
  async createEvent(eventData: CreateEventForm): Promise<Event> {
    // Send event creation request to the server
    const response = await apiClient.post<ApiResponse<Event>>('/events/', eventData);
    return response.data.data;
  },

  /**
   * Update Existing Event
   * 
   * Updates an existing event with new information.
   * Only moderators and event creators can update events.
   * 
   * @param id - Unique identifier of the event to update
   * @param eventData - Partial event data containing fields to update
   * @returns Promise resolving to the updated Event object
   * @throws Error if event doesn't exist or user lacks permissions
   */
  async updateEvent(id: string, eventData: Partial<CreateEventForm>): Promise<Event> {
    // Send update request with partial data to the server
    const response = await apiClient.put<ApiResponse<Event>>(`/events/${id}/`, eventData);
    return response.data.data;
  },

  /**
   * Delete Event
   * 
   * Permanently deletes an event and all associated data.
   * Only moderators and event creators can delete events.
   * This action cannot be undone.
   * 
   * @param id - Unique identifier of the event to delete
   * @returns Promise that resolves when deletion is complete
   * @throws Error if event doesn't exist or user lacks permissions
   */
  async deleteEvent(id: string): Promise<void> {
    // Send delete request to the server
    await apiClient.delete(`/events/${id}/`);
  },

  /**
   * Generate Share Link
   * 
   * Creates a unique share link that allows users to join the event.
   * The link contains a secure token that grants access to the event.
   * Only moderators and presenters can generate share links.
   * 
   * @param id - Unique identifier of the event to generate a link for
   * @returns Promise resolving to the share link URL
   * @throws Error if event doesn't exist or user lacks permissions
   */
  async generateShareLink(id: string): Promise<string> {
    // Request share link generation from the server
    const response = await apiClient.post<ApiResponse<{ shareLink: string }>>(`/events/${id}/share/`);
    return response.data.data.shareLink;
  },

  /**
   * Join Event via Share Link
   * 
   * Allows a user to join an event using a share token from a share link.
   * This adds the user to the event's participant list and grants access.
   * 
   * @param shareToken - Unique token extracted from the share link
   * @returns Promise resolving to the Event object the user joined
   * @throws Error if token is invalid, expired, or event is closed
   */
  async joinEvent(shareToken: string): Promise<Event> {
    // Send join request with the share token
    const response = await apiClient.post<ApiResponse<Event>>(`/events/join/${shareToken}/`);
    return response.data.data;
  },
};
