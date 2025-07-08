// Create Event Page Component - Form for creating new AMA events
// This page allows moderators and presenters to create new AMA sessions

// Mark as client component since we're using React hooks and form handling
'use client';

// Import authentication hook to check user permissions
import { useAuth } from '@/contexts/AuthContext';
// Import events context to manage events state
import { useEvents } from '@/contexts/EventsContext';
// Import Next.js router for navigation after successful creation
import { useRouter } from 'next/navigation';
// Import React hooks for form state management and side effects
import { useState, useEffect } from 'react';
// Import Next.js Link component for navigation
import Link from 'next/link';
// Import event service for API calls
import { eventService } from '@/services/eventService';

/**
 * CreateEventPage Component
 * 
 * This page provides a form interface for creating new AMA events.
 * Features:
 * - Role-based access control (only moderators and presenters can access)
 * - Form validation and error handling
 * - Date/time selection for event scheduling
 * - Loading states during form submission
 * - Success feedback and navigation
 * 
 * @returns JSX element representing the create event page
 */
export default function CreateEventPage() {
  // Get authentication state and user information
  const { user, isLoading, isAuthenticated } = useAuth();
  // Get events functions from context
  const { addEvent, refetchEvents } = useEvents();
  // Get router instance for navigation
  const router = useRouter();
  
  // Form state management
  const [formData, setFormData] = useState({
    name: '',                 // Changed from 'title' to match backend
    description: '',
    presenter: '',
    scheduledDate: '',
    scheduledTime: '',
    duration: '60',          // Default duration in minutes
    maxQuestions: '50'       // Default max questions
  });
  
  // UI state management
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Effect to handle authentication and authorization
  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }
    
    // Check if user has permission to create events
    if (!isLoading && isAuthenticated && user) {
      if (user.role !== 'moderator' && user.role !== 'presenter') {
        // Redirect unauthorized users to home page
        router.push('/');
        return;
      }
      
      // Auto-fill presenter field if user is a presenter
      if (user.role === 'presenter') {
        setFormData(prev => ({
          ...prev,
          presenter: user.name || ''
        }));
      }
    }
  }, [isLoading, isAuthenticated, user, router]);

  /**
   * Handle form input changes
   * Updates the form state when user types in input fields
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * Handle form submission
   * Validates form data and simulates event creation
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      // Basic form validation
      if (!formData.name.trim()) {
        throw new Error('Event name is required');
      }
      if (!formData.description.trim()) {
        throw new Error('Event description is required');
      }
      if (!formData.presenter.trim()) {
        throw new Error('Presenter name is required');
      }
      if (!formData.scheduledDate) {
        throw new Error('Event date is required');
      }
      if (!formData.scheduledTime) {
        throw new Error('Event time is required');
      }

      // Combine date and time for open_date if provided
      let open_date = null;
      if (formData.scheduledDate && formData.scheduledTime) {
        open_date = new Date(`${formData.scheduledDate}T${formData.scheduledTime}`).toISOString();
      }

      // Prepare event data for API
      const eventData = {
        name: formData.name.trim(),
        open_date: open_date,
        close_date: null, // Can be extended later
      };

      console.log('Creating event with data:', eventData);
      
      // Call the actual API to create the event
      const createdEvent = await eventService.createEvent(eventData);
      console.log('Event created successfully:', createdEvent);
      
      // Add the event to the global state immediately
      addEvent(createdEvent);
      
      // Also trigger a refetch to ensure consistency
      refetchEvents();
      
      // Show success message
      setSuccess(true);
      
      // Redirect to events page after short delay
      setTimeout(() => {
        router.push('/events');
      }, 1500);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create event');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Don't render anything if not authenticated (will redirect)
  if (!isAuthenticated || !user) {
    return null;
  }

  // Don't render if user doesn't have permission (will redirect)
  if (user.role !== 'moderator' && user.role !== 'presenter') {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-semibold text-gray-900 hover:text-primary-600">
                Luca AMA App
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">Welcome, {user?.name}</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                {user?.role}
              </span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Page Header */}
          <div className="mb-8">
            <Link 
              href="/" 
              className="text-primary-600 hover:text-primary-800 text-sm font-medium mb-4 inline-block"
            >
              ← Back to Dashboard
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Create New AMA Event</h1>
            <p className="mt-2 text-gray-600">
              Set up a new Ask Me Anything session for participants to join and ask questions.
            </p>
          </div>

          {/* Success Message */}
          {success && (
            <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-green-400">✅</span>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">
                    Event Created Successfully!
                  </h3>
                  <p className="mt-1 text-sm text-green-700">
                    Your AMA event has been created. Redirecting to events page...
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-red-400">❌</span>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    Error Creating Event
                  </h3>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Create Event Form */}
          <div className="bg-white shadow rounded-lg">
            <form onSubmit={handleSubmit} className="space-y-6 p-6">
              
              {/* Event Title */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Event Name *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., AMA with Tech Lead - Career Advice"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  disabled={isSubmitting}
                />
              </div>

              {/* Event Description */}
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Describe what this AMA session will cover, topics that will be discussed, and any special instructions for participants..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  disabled={isSubmitting}
                />
              </div>

              {/* Presenter Name */}
              <div>
                <label htmlFor="presenter" className="block text-sm font-medium text-gray-700 mb-2">
                  Presenter *
                </label>
                <input
                  type="text"
                  id="presenter"
                  name="presenter"
                  value={formData.presenter}
                  onChange={handleInputChange}
                  placeholder="Name of the person presenting"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  disabled={isSubmitting}
                />
              </div>

              {/* Date and Time Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Scheduled Date */}
                <div>
                  <label htmlFor="scheduledDate" className="block text-sm font-medium text-gray-700 mb-2">
                    Date *
                  </label>
                  <input
                    type="date"
                    id="scheduledDate"
                    name="scheduledDate"
                    value={formData.scheduledDate}
                    onChange={handleInputChange}
                    min={new Date().toISOString().split('T')[0]} // Can't select past dates
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    disabled={isSubmitting}
                  />
                </div>

                {/* Scheduled Time */}
                <div>
                  <label htmlFor="scheduledTime" className="block text-sm font-medium text-gray-700 mb-2">
                    Time *
                  </label>
                  <input
                    type="time"
                    id="scheduledTime"
                    name="scheduledTime"
                    value={formData.scheduledTime}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    disabled={isSubmitting}
                  />
                </div>
              </div>

              {/* Duration and Max Questions Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Duration */}
                <div>
                  <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-2">
                    Duration (minutes)
                  </label>
                  <select
                    id="duration"
                    name="duration"
                    value={formData.duration}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    disabled={isSubmitting}
                  >
                    <option value="30">30 minutes</option>
                    <option value="45">45 minutes</option>
                    <option value="60">60 minutes</option>
                    <option value="90">90 minutes</option>
                    <option value="120">2 hours</option>
                  </select>
                </div>

                {/* Max Questions */}
                <div>
                  <label htmlFor="maxQuestions" className="block text-sm font-medium text-gray-700 mb-2">
                    Max Questions
                  </label>
                  <select
                    id="maxQuestions"
                    name="maxQuestions"
                    value={formData.maxQuestions}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    disabled={isSubmitting}
                  >
                    <option value="25">25 questions</option>
                    <option value="50">50 questions</option>
                    <option value="100">100 questions</option>
                    <option value="unlimited">Unlimited</option>
                  </select>
                </div>
              </div>

              {/* Form Actions */}
              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
                <Link
                  href="/"
                  className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Cancel
                </Link>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <span className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                      Creating Event...
                    </>
                  ) : (
                    'Create Event'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
