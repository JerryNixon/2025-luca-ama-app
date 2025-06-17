// Events Page Component - Display all available AMA events
// This page shows a grid of event cards and handles event navigation

// Mark as client component for React hooks and interactivity
'use client';

// Import React hooks for state management and side effects
import { useState, useEffect } from 'react';
// Import authentication context to check user permissions
import { useAuth } from '@/contexts/AuthContext';
// Import TypeScript types for type safety
import { Event } from '@/types';
// Import services for data fetching
import { eventService } from '@/services/eventService';
import { demoService } from '@/lib/demoData';
// Import reusable components
import EventCard from '@/components/events/EventCard';
// Import Next.js components for navigation
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Development toggle - switch between demo data and real API
// Set to false when backend API is ready for production
const USE_DEMO_DATA = true;

/**
 * EventsPage Component
 * 
 * This page displays all available AMA events in a responsive grid layout.
 * Features:
 * - Authentication check and redirect
 * - Loading states and error handling
 * - Role-based permissions for event creation
 * - Event filtering and navigation
 * - Empty state handling
 * 
 * @returns JSX element representing the events listing page
 */
export default function EventsPage() {
  // Get authentication state and user information
  const { user, isAuthenticated } = useAuth();
  // Router for programmatic navigation
  const router = useRouter();
  
  // Component state management
  const [events, setEvents] = useState<Event[]>([]);         // Array of events to display
  const [loading, setLoading] = useState(true);             // Loading state for UI feedback
  const [error, setError] = useState<string | null>(null);  // Error state for error handling

  // Effect hook to fetch events when component mounts or authentication changes
  useEffect(() => {
    // Redirect unauthenticated users to login page
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    /**
     * Async function to fetch events from either demo service or real API
     * Handles both success and error cases with appropriate state updates
     */
    const fetchEvents = async () => {
      try {
        let eventsData: Event[];
        
        // Choose data source based on development flag
        if (USE_DEMO_DATA) {
          // Use demo data for development/testing
          eventsData = await demoService.getEvents();
        } else {
          // Use real API service for production
          eventsData = await eventService.getEvents();
        }
        
        // Update state with fetched events
        setEvents(eventsData);
      } catch (err) {
        // Handle any errors during data fetching
        setError('Failed to load events');
        console.error('Failed to fetch events:', err);
      } finally {
        // Always set loading to false, regardless of success or failure
        setLoading(false);
      }
    };

    // Execute the fetch function
    fetchEvents();
  }, [isAuthenticated, router]); // Re-run effect when these dependencies change

  /**
   * Handle clicking on an event card
   * Navigates to the detailed event page
   * 
   * @param eventId - Unique identifier of the clicked event
   */
  const handleEventClick = (eventId: string) => {
    router.push(`/events/${eventId}`);
  };

  // Loading state UI - shows spinner while fetching data
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        {/* Tailwind CSS animated spinner */}
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Error state UI - shows error message if data fetching fails
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-2">Error</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  // Check if current user has permission to create events
  // Only moderators and presenters can create events
  const canCreateEvents = user?.role === 'moderator' || user?.role === 'presenter';

  // Main page content - events grid with navigation
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Left side - App name with link to home */}
            <div className="flex items-center">
              <Link href="/" className="text-xl font-semibold text-gray-900">
                Luca AMA App
              </Link>
            </div>
            {/* Right side - User greeting */}
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">Welcome, {user?.name}</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Page Header with conditional Create button */}
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">AMA Events</h1>
            {/* Only show Create button to authorized users */}
            {canCreateEvents && (
              <Link
                href="/events/create"
                className="btn-primary"
              >
                Create New Event
              </Link>
            )}
          </div>

          {/* Conditional rendering based on events availability */}
          {events.length === 0 ? (
            // Empty State - No events available
            <div className="text-center py-12">
              <h3 className="text-lg font-medium text-gray-900 mb-2">No events found</h3>
              <p className="text-gray-600 mb-4">
                {/* Different message based on user permissions */}
                {canCreateEvents 
                  ? "Get started by creating your first AMA event." 
                  : "No events are currently available. Check back later."}
              </p>
              {/* Show create button only to authorized users in empty state */}
              {canCreateEvents && (
                <Link href="/events/create" className="btn-primary">
                  Create Your First Event
                </Link>
              )}
            </div>
          ) : (
            // Events Grid - Display all events in responsive grid
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {events.map((event) => (
                <EventCard
                  key={event.id}                                    // Unique key for React rendering
                  event={event}                                     // Event data to display
                  onClick={() => handleEventClick(event.id)}       // Click handler for navigation
                  userRole={user?.role || 'user'}                  // User role for permission-based features
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
