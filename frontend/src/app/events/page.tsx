// Events Page Component - Display all available AMA events
// This page shows a grid of event cards and handles event navigation

// Mark as client component for React hooks and interactivity
'use client';

// Import React hooks for state management and side effects
import { useEffect } from 'react';
// Import authentication context to check user permissions
import { useAuth } from '@/contexts/AuthContext';
// Import events context to manage events state
import { useEvents } from '@/contexts/EventsContext';
// Import TypeScript types for type safety
import { Event } from '@/types';
// Import reusable components
import EventCard from '@/components/events/EventCard';
// Import Next.js components for navigation
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';

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
 * - Global state management for events
 * 
 * @returns JSX element representing the events listing page
 */
export default function EventsPage() {
  // Get authentication state and user information
  const { user, isAuthenticated } = useAuth();
  // Get events state and functions from context
  const { events, loading, error, refetchEvents } = useEvents();
  // Router for programmatic navigation
  const router = useRouter();
  // Current pathname for route change detection
  const pathname = usePathname();

  // Debug logging
  console.log('Events page render - events:', events);
  console.log('Events page render - loading:', loading);
  console.log('Events page render - error:', error);

  // Effect hook to redirect unauthenticated users
  useEffect(() => {
    // Redirect unauthenticated users to login page
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
  }, [isAuthenticated, router]);

  // Effect hook to refetch events when page comes back into focus (debounced)
  useEffect(() => {
    let focusTimeout: NodeJS.Timeout;
    
    const handleFocus = () => {
      if (isAuthenticated) {
        // Clear any existing timeout
        clearTimeout(focusTimeout);
        // Debounce the refetch call
        focusTimeout = setTimeout(() => {
          console.log('Page focused, refetching events...');
          refetchEvents();
        }, 500); // 500ms debounce
      }
    };

    // Add focus event listener
    window.addEventListener('focus', handleFocus);
    
    // Cleanup event listener on unmount
    return () => {
      window.removeEventListener('focus', handleFocus);
      clearTimeout(focusTimeout);
    };
  }, [isAuthenticated, refetchEvents]);

  /**
   * Handle manual refresh of events list
   * Allows users to refresh the events list manually
   */
  const handleRefresh = () => {
    console.log('Manual refresh triggered');
    refetchEvents();
  };

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
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading events...</p>
          <p className="text-xs text-gray-500 mt-2">This may take a moment while connecting to the database</p>
        </div>
      </div>
    );
  }

  // Error state UI - shows error message if data fetching fails
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-red-600 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
          >
            Try Again
          </button>
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
          {/* Page Header with conditional Create button and Refresh button */}
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center space-x-4">
              <h1 className="text-3xl font-bold text-gray-900">AMA Events</h1>
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Refresh events list"
              >
                {loading ? '🔄' : '↻'} Refresh
              </button>
            </div>
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
          {!events || events.length === 0 ? (
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
