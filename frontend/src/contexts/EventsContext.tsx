// Events Context - Global state management for events
// This provides a centralized way to manage events state across the application

'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Event } from '@/types';
import { eventService } from '@/services/eventService';
import { useAuth } from './AuthContext';

interface EventsContextType {
  events: Event[];
  loading: boolean;
  error: string | null;
  refetchEvents: () => Promise<void>;
  addEvent: (event: Event) => void;
  updateEvent: (eventId: string, updatedEvent: Event) => void;
  removeEvent: (eventId: string) => void;
}

const EventsContext = createContext<EventsContextType | undefined>(undefined);

export const useEvents = () => {
  const context = useContext(EventsContext);
  if (!context) {
    throw new Error('useEvents must be used within an EventsProvider');
  }
  return context;
};

interface EventsProviderProps {
  children: ReactNode;
}

export const EventsProvider: React.FC<EventsProviderProps> = ({ children }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefetching, setIsRefetching] = useState(false);
  const { isAuthenticated } = useAuth();

  const refetchEvents = async () => {
    if (!isAuthenticated || isRefetching) return;
    
    try {
      console.log('EventsContext: Fetching events...');
      setIsRefetching(true);
      setLoading(true);
      setError(null);
      const eventsData = await eventService.getEvents();
      setEvents(eventsData);
      console.log('EventsContext: Events updated:', eventsData);
    } catch (err) {
      console.error('EventsContext: Error fetching events:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch events');
    } finally {
      setLoading(false);
      // Add a small delay to prevent rapid successive calls
      setTimeout(() => setIsRefetching(false), 1000);
    }
  };

  const addEvent = (event: Event) => {
    console.log('EventsContext: Adding event:', event);
    setEvents(prev => [event, ...prev]);
  };

  const updateEvent = (eventId: string, updatedEvent: Event) => {
    console.log('EventsContext: Updating event:', eventId, updatedEvent);
    setEvents(prev => prev.map(event => 
      event.id === eventId ? updatedEvent : event
    ));
  };

  const removeEvent = (eventId: string) => {
    console.log('EventsContext: Removing event:', eventId);
    setEvents(prev => prev.filter(event => event.id !== eventId));
  };

  useEffect(() => {
    refetchEvents();
  }, [isAuthenticated]);

  const value: EventsContextType = {
    events,
    loading,
    error,
    refetchEvents,
    addEvent,
    updateEvent,
    removeEvent
  };

  return (
    <EventsContext.Provider value={value}>
      {children}
    </EventsContext.Provider>
  );
};
