/**
 * Real-time synchronization hook for AMA events
 * 
 * This hook provides real-time updates for questions and event data
 * Used by both moderator and user views to stay synchronized
 */

import { useEffect, useRef, useCallback } from 'react';
import { questionService } from '../services/questionService';
import { eventService } from '../services/eventService';

interface UseRealTimeSyncOptions {
  eventId: string;
  enabled: boolean;
  onQuestionsUpdate: (questions: any[]) => void;
  onEventUpdate?: (event: any) => void;
  pollInterval?: number; // in milliseconds, default 30000 (30 seconds)
  onError?: (error: Error) => void;
}

export function useRealTimeSync({
  eventId,
  enabled,
  onQuestionsUpdate,
  onEventUpdate,
  pollInterval = 30000,
  onError
}: UseRealTimeSyncOptions) {
  const questionsIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const eventIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastUpdateTimeRef = useRef<Date | null>(null);

  /**
   * Refresh questions data
   */
  const refreshQuestions = useCallback(async () => {
    try {
      console.log(`[RealTimeSync] Refreshing questions for event ${eventId}`);
      const questionsData = await questionService.getQuestions(eventId);
      onQuestionsUpdate(questionsData);
      lastUpdateTimeRef.current = new Date();
      console.log(`[RealTimeSync] Questions refreshed: ${questionsData.length} questions`);
    } catch (error) {
      console.error('[RealTimeSync] Failed to refresh questions:', error);
      if (onError) {
        onError(error as Error);
      }
      // Don't propagate errors to avoid disrupting the UI
    }
  }, [eventId, onQuestionsUpdate, onError]);

  /**
   * Refresh event data (if callback provided)
   */
  const refreshEvent = useCallback(async () => {
    if (!onEventUpdate) return;
    
    try {
      console.log(`[RealTimeSync] Refreshing event data for ${eventId}`);
      const eventData = await eventService.getEvent(eventId);
      onEventUpdate(eventData);
      lastUpdateTimeRef.current = new Date();
      console.log('[RealTimeSync] Event data refreshed');
    } catch (error) {
      console.error('[RealTimeSync] Failed to refresh event:', error);
      if (onError) {
        onError(error as Error);
      }
      // Don't propagate errors to avoid disrupting the UI
    }
  }, [eventId, onEventUpdate, onError]);

  /**
   * Manual refresh function that can be called by components
   */
  const manualRefresh = useCallback(async () => {
    console.log(`[RealTimeSync] Manual refresh triggered for event ${eventId}`);
    await Promise.all([
      refreshQuestions(),
      refreshEvent()
    ]);
  }, [refreshQuestions, refreshEvent, eventId]);

  /**
   * Set up polling when enabled
   */
  useEffect(() => {
    if (!enabled || !eventId) {
      console.log(`[RealTimeSync] Sync disabled for event ${eventId}`);
      return;
    }

    console.log(`[RealTimeSync] Starting polling for event ${eventId} (interval: ${pollInterval}ms)`);

    // Initial load
    manualRefresh();

    // Set up questions polling
    questionsIntervalRef.current = setInterval(refreshQuestions, pollInterval);

    // Set up event polling if callback provided
    if (onEventUpdate) {
      eventIntervalRef.current = setInterval(refreshEvent, pollInterval);
    }

    // Cleanup on unmount or when disabled
    return () => {
      console.log(`[RealTimeSync] Stopping polling for event ${eventId}`);
      
      if (questionsIntervalRef.current) {
        clearInterval(questionsIntervalRef.current);
        questionsIntervalRef.current = null;
      }
      
      if (eventIntervalRef.current) {
        clearInterval(eventIntervalRef.current);
        eventIntervalRef.current = null;
      }
    };
  }, [enabled, eventId, pollInterval, refreshQuestions, refreshEvent, onEventUpdate, manualRefresh]);

  return {
    manualRefresh,
    refreshQuestions,
    refreshEvent,
    lastUpdateTime: lastUpdateTimeRef.current
  };
}
