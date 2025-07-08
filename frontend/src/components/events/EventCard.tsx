// EventCard Component - Reusable card component for displaying event information
// This component renders individual event cards in a grid layout with interactive features

// Import React for component creation
import React from 'react';
// Import Feather icons for UI elements and visual indicators
import { FiStar, FiMessageSquare, FiUsers, FiClock, FiChevronRight } from 'react-icons/fi';
// Import TypeScript types for type safety
import { Event } from '@/types';
// Import date formatting utility for consistent date display
import { format } from 'date-fns';

/**
 * Interface defining the props that EventCard component expects
 * This ensures type safety and provides clear documentation of required data
 */
interface EventCardProps {
  event: Event;                                           // Event data to display
  onClick: () => void;                                    // Function to call when card is clicked
}

/**
 * EventCard Component
 * 
 * A reusable card component that displays event information in a visually appealing format.
 * Features:
 * - Event status indicators (active/inactive)
 * - Role-based information display using new permission system
 * - Date formatting and validation
 * - Hover effects and click handling
 * - Responsive design with consistent styling
 * 
 * @param event - Event object containing all event data
 * @param onClick - Callback function executed when the card is clicked
 * @returns JSX element representing an event card
 */
export default function EventCard({ event, onClick }: EventCardProps) {
  // Determine if the event is currently active
  // An event is active if:
  // 1. The is_active flag is true, AND
  // 2. Either there's no close date OR the close date hasn't passed yet
  const isActive = event.is_active && (!event.close_date || new Date() < new Date(event.close_date));
  
  // Use the new permission system from the backend
  const userRole = event.user_role_in_event || 'no_access';
  const canModerate = event.can_user_moderate || false;
  const canAccess = event.can_user_access || false;
  const isCreator = event.is_created_by_user || false;

  return (
    <div
      className="card hover:shadow-lg transition-shadow duration-200 cursor-pointer"
      onClick={onClick}
    >
      {/* Card Header - Event name and status badges */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Event Title and Status Badges */}
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{event.name}</h3>
            
            {/* Active Status Badge - Only shown for currently active events */}
            {isActive && (
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                Active
              </span>
            )}
            
            {/* User Role Badge - Shows user's role in this event */}
            {userRole !== 'no_access' && userRole !== 'visitor' && (
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                isCreator ? 'bg-purple-100 text-purple-800' :
                canModerate ? 'bg-blue-100 text-blue-800' :
                userRole === 'participant' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {isCreator ? 'Creator' : 
                 canModerate ? 'Moderator' : 
                 userRole === 'participant' ? 'Participant' : 
                 'Visitor'}
              </span>
            )}
            
            {/* Event Privacy Badge - Shows if event is public or private */}
            {event.is_public !== undefined && (
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                event.is_public ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
              }`}>
                {event.is_public ? 'Public' : 'Private'}
              </span>
            )}
          </div>

          {/* Event Details Section */}
          <div className="space-y-2 text-sm text-gray-600">
            
            {/* Event Open Date - When the event starts accepting questions */}
            {event.open_date && (
              <div className="flex items-center gap-2">
                <FiClock className="w-4 h-4" />
                <span>Opens: {format(new Date(event.open_date), 'MMM dd, yyyy HH:mm')}</span>
              </div>
            )}
            
            {/* Event Close Date - When the event stops accepting questions */}
            {event.close_date && (
              <div className="flex items-center gap-2">
                <FiClock className="w-4 h-4" />
                <span>Closes: {format(new Date(event.close_date), 'MMM dd, yyyy HH:mm')}</span>
              </div>
            )}

            {/* Participant and Moderator Statistics */}
            <div className="flex items-center gap-4">
              {/* Participant Count - Always visible to show event popularity */}
              <div className="flex items-center gap-1">
                <FiUsers className="w-4 h-4" />
                <span>{event.participants.length} participants</span>
              </div>
              
              {/* Moderator Count - Only visible to users who can moderate or are participants */}
              {(canModerate || userRole === 'participant') && (
                <div className="flex items-center gap-1">
                  <FiStar className="w-4 h-4" />
                  <span>{event.moderators.length} moderators</span>
                </div>
              )}
              
              {/* Question Count - Show if available */}
              {event.question_count !== undefined && (
                <div className="flex items-center gap-1">
                  <FiMessageSquare className="w-4 h-4" />
                  <span>{event.question_count} questions</span>
                </div>
              )}
            </div>

            {/* Event Creation Date - Provides context about when the event was set up */}
            <div className="text-xs text-gray-500">
              Created {format(new Date(event.created_at), 'MMM dd, yyyy')}
            </div>
          </div>
        </div>

        {/* Right Arrow Indicator - Visual cue that the card is clickable */}
        <div className="flex items-center gap-2">
          <FiChevronRight className="w-5 h-5 text-gray-400" />
        </div>
      </div>
    </div>
  );
}
