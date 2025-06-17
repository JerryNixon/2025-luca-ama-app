import React from 'react';
import { FiStar, FiMessageSquare, FiUsers, FiClock, FiChevronRight } from 'react-icons/fi';
import { Event } from '@/types';
import { format } from 'date-fns';

interface EventCardProps {
  event: Event;
  onClick: () => void;
  userRole: 'moderator' | 'presenter' | 'user';
}

export default function EventCard({ event, onClick, userRole }: EventCardProps) {
  const isActive = event.isActive && (!event.closeDate || new Date() < event.closeDate);
  const canModerate = userRole === 'moderator' || userRole === 'presenter';

  return (
    <div
      className="card hover:shadow-lg transition-shadow duration-200 cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{event.name}</h3>
            {isActive && (
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                Active
              </span>
            )}
            {canModerate && (
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                {userRole}
              </span>
            )}
          </div>

          <div className="space-y-2 text-sm text-gray-600">
            {event.openDate && (
              <div className="flex items-center gap-2">
                <FiClock className="w-4 h-4" />
                <span>Opens: {format(event.openDate, 'MMM dd, yyyy HH:mm')}</span>
              </div>
            )}
            
            {event.closeDate && (
              <div className="flex items-center gap-2">
                <FiClock className="w-4 h-4" />
                <span>Closes: {format(event.closeDate, 'MMM dd, yyyy HH:mm')}</span>
              </div>
            )}

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <FiUsers className="w-4 h-4" />
                <span>{event.participants.length} participants</span>
              </div>
              
              {canModerate && (
                <div className="flex items-center gap-1">
                  <FiStar className="w-4 h-4" />
                  <span>{event.moderators.length} moderators</span>
                </div>
              )}
            </div>

            <div className="text-xs text-gray-500">
              Created {format(event.createdAt, 'MMM dd, yyyy')}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <FiChevronRight className="w-5 h-5 text-gray-400" />
        </div>
      </div>
    </div>
  );
}
