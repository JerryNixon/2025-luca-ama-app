/**
 * Real-time Event Sync Context
 * 
 * This context enables real-time synchronization between different views of the same event
 * (e.g., moderator view and user view) by providing a shared state management layer
 * and broadcast mechanism for event updates.
 */

'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { Question, Event } from '@/types';

interface EventSyncContextType {
  // Current event data
  currentEvent: Event | null;
  currentQuestions: Question[];
  
  // Update functions
  updateEvent: (event: Event) => void;
  updateQuestions: (questions: Question[]) => void;
  updateQuestion: (questionId: string, updates: Partial<Question>) => void;
  
  // Real-time sync control
  enableSync: (eventId: string) => void;
  disableSync: () => void;
  forceRefresh: () => void;
  
  // Status
  isSyncing: boolean;
  lastSyncTime: Date | null;
}

const EventSyncContext = createContext<EventSyncContextType | undefined>(undefined);

/**
 * Custom hook to use event sync context
 */
export function useEventSync() {
  const context = useContext(EventSyncContext);
  if (context === undefined) {
    throw new Error('useEventSync must be used within an EventSyncProvider');
  }
  return context;
}

/**
 * Event sync provider component
 */
export function EventSyncProvider({ children }: { children: React.ReactNode }) {
  const [currentEvent, setCurrentEvent] = useState<Event | null>(null);
  const [currentQuestions, setCurrentQuestions] = useState<Question[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  
  const syncIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const currentEventIdRef = useRef<string | null>(null);
  const listenersRef = useRef<Set<() => void>>(new Set());

  /**
   * Update event data and notify listeners
   */
  const updateEvent = useCallback((event: Event) => {
    setCurrentEvent(event);
    setLastSyncTime(new Date());
    
    // Notify all listeners about the update
    listenersRef.current.forEach(listener => {
      try {
        listener();
      } catch (error) {
        console.error('[EventSync] Listener error:', error);
      }
    });
  }, []);

  /**
   * Update questions data and notify listeners
   */
  const updateQuestions = useCallback((questions: Question[]) => {
    setCurrentQuestions(questions);
    setLastSyncTime(new Date());
    
    // Notify all listeners about the update
    listenersRef.current.forEach(listener => {
      try {
        listener();
      } catch (error) {
        console.error('[EventSync] Listener error:', error);
      }
    });
  }, []);

  /**
   * Update a specific question
   */
  const updateQuestion = useCallback((questionId: string, updates: Partial<Question>) => {
    setCurrentQuestions(prev => prev.map(q => 
      q.id === questionId ? { ...q, ...updates } : q
    ));
    setLastSyncTime(new Date());
    
    // Notify all listeners about the update
    listenersRef.current.forEach(listener => {
      try {
        listener();
      } catch (error) {
        console.error('[EventSync] Listener error:', error);
      }
    });
  }, []);

  /**
   * Enable real-time sync for an event
   */
  const enableSync = useCallback((eventId: string) => {
    console.log(`[EventSync] Enabling sync for event ${eventId}`);
    
    // Update current event ID
    currentEventIdRef.current = eventId;
    setIsSyncing(true);
    
    // Note: The actual polling is handled by individual components using useRealTimeSync
    // This context provides shared state management
  }, []);

  /**
   * Disable real-time sync
   */
  const disableSync = useCallback(() => {
    console.log('[EventSync] Disabling sync');
    
    currentEventIdRef.current = null;
    setIsSyncing(false);
    
    // Clear sync interval if it exists
    if (syncIntervalRef.current) {
      clearInterval(syncIntervalRef.current);
      syncIntervalRef.current = null;
    }
  }, []);

  /**
   * Force refresh from all connected views
   */
  const forceRefresh = useCallback(() => {
    console.log('[EventSync] Force refresh triggered');
    setLastSyncTime(new Date());
    
    // Notify all listeners to refresh
    listenersRef.current.forEach(listener => {
      try {
        listener();
      } catch (error) {
        console.error('[EventSync] Force refresh listener error:', error);
      }
    });
  }, []);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      disableSync();
    };
  }, [disableSync]);

  const value: EventSyncContextType = {
    currentEvent,
    currentQuestions,
    updateEvent,
    updateQuestions,
    updateQuestion,
    enableSync,
    disableSync,
    forceRefresh,
    isSyncing,
    lastSyncTime
  };

  return (
    <EventSyncContext.Provider value={value}>
      {children}
    </EventSyncContext.Provider>
  );
}
