/**
 * Optimistic Updates Hook
 * Provides immediate UI feedback while Fabric SQL requests are processing
 */

import { useState, useCallback, useRef } from 'react';

interface OptimisticState<T> {
  data: T;
  isOptimistic: boolean;
  originalData?: T;
}

export function useOptimisticUpdates<T>(initialData: T) {
  const [state, setState] = useState<OptimisticState<T>>({
    data: initialData,
    isOptimistic: false
  });
  
  const pendingUpdate = useRef<Promise<any> | null>(null);

  /**
   * Apply optimistic update immediately, then perform real update
   */
  const applyOptimisticUpdate = useCallback(async <R>(
    optimisticData: T,
    actualUpdateFn: () => Promise<R>,
    onSuccess?: (result: R, wasOptimistic: boolean) => T,
    onError?: (error: any, originalData: T) => T
  ): Promise<R | null> => {
    
    // Store original data and apply optimistic update immediately
    const originalData = state.data;
    setState({
      data: optimisticData,
      isOptimistic: true,
      originalData
    });

    try {
      // Wait for any pending update to complete first
      if (pendingUpdate.current) {
        await pendingUpdate.current;
      }

      // Perform the actual update
      const updatePromise = actualUpdateFn();
      pendingUpdate.current = updatePromise;
      
      const result = await updatePromise;
      
      // Update with real data
      const finalData = onSuccess ? onSuccess(result, true) : optimisticData;
      setState({
        data: finalData,
        isOptimistic: false,
        originalData: undefined
      });

      pendingUpdate.current = null;
      return result;

    } catch (error) {
      console.error('Optimistic update failed:', error);
      
      // Revert to original data on error
      const revertedData = onError ? onError(error, originalData) : originalData;
      setState({
        data: revertedData,
        isOptimistic: false,
        originalData: undefined
      });

      pendingUpdate.current = null;
      return null;
    }
  }, [state.data]);

  /**
   * Reset to non-optimistic state with new data
   */
  const resetWithData = useCallback((newData: T) => {
    setState({
      data: newData,
      isOptimistic: false,
      originalData: undefined
    });
  }, []);

  return {
    data: state.data,
    isOptimistic: state.isOptimistic,
    originalData: state.originalData,
    applyOptimisticUpdate,
    resetWithData
  };
}
