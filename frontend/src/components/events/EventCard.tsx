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
  userRole: 'moderator' | 'presenter' | 'user';         // Current user's role for permission-based features
}

/**
 * EventCard Component
 * 
 * A reusable card component that displays event information in a visually appealing format.
 * Features:
 * - Event status indicators (active/inactive)
 * - Role-based information display
 * - Date formatting and validation
 * - Hover effects and click handling
 * - Responsive design with consistent styling
 * 
 * @param event - Event object containing all event data
 * @param onClick - Callback function executed when the card is clicked
 * @param userRole - Current user's role for determining what information to show
 * @returns JSX element representing an event card
 */
export default function EventCard({ event, onClick, userRole }: EventCardProps) {
  // Determine if the event is currently active
  // An event is active if:
  // 1. The is_active flag is true, AND
  // 2. Either there's no close date OR the close date hasn't passed yet
  const isActive = event.is_active && (!event.close_date || new Date() < new Date(event.close_date));
  
  // Check if current user has moderation privileges
  // Moderators and presenters see additional information and controls
  const canModerate = userRole === 'moderator' || userRole === 'presenter';

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
            
            {/* User Role Badge - Only shown to moderators and presenters */}
            {/* Helps users understand their permission level for this event */}
            {canModerate && (
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                {userRole}
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
              
              {/* Moderator Count - Only visible to users who can moderate */}
              {/* This helps moderators see how many people are managing the event */}
              {canModerate && (
                <div className="flex items-center gap-1">
                  <FiStar className="w-4 h-4" />
                  <span>{event.moderators.length} moderators</span>
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
