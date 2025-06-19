'use client';

// LoadingSkeleton Component - Provides skeleton loading placeholders
// Creates visually appealing loading states while content is fetching

import React from 'react';

/**
 * Props for the LoadingSkeleton component
 */
interface LoadingSkeletonProps {
  variant?: 'card' | 'list' | 'text' | 'avatar' | 'button';
  count?: number;
  height?: string;
  width?: string;
  className?: string;
}

/**
 * LoadingSkeleton Component
 * 
 * Provides animated skeleton placeholders for different content types.
 * Improves perceived performance by showing content structure while loading.
 * 
 * @param variant - Type of skeleton to render
 * @param count - Number of skeletons to render
 * @param height - Custom height override
 * @param width - Custom width override
 * @param className - Additional CSS classes
 */
export default function LoadingSkeleton({
  variant = 'text',
  count = 1,
  height,
  width,
  className = ''
}: LoadingSkeletonProps) {
  
  const baseClasses = 'animate-pulse bg-gray-200 rounded';
  
  const variants = {
    card: `${baseClasses} h-48 w-full`,
    list: `${baseClasses} h-16 w-full`,
    text: `${baseClasses} h-4 w-3/4`,
    avatar: `${baseClasses} h-10 w-10 rounded-full`,
    button: `${baseClasses} h-10 w-24`
  };
  
  const skeletonClass = variants[variant];
  const customStyle = {
    ...(height && { height }),
    ...(width && { width })
  };

  return (
    <div className={className}>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={`${skeletonClass} ${index < count - 1 ? 'mb-3' : ''}`}
          style={customStyle}
        />
      ))}
    </div>
  );
}

/**
 * QuestionCardSkeleton - Specific skeleton for question cards
 */
export function QuestionCardSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="card fade-in">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {/* Header skeleton */}
              <div className="flex items-center gap-2 mb-3">
                <LoadingSkeleton variant="avatar" width="16px" height="16px" />
                <LoadingSkeleton variant="text" width="120px" height="14px" />
                <LoadingSkeleton variant="text" width="80px" height="12px" />
              </div>
              
              {/* Question text skeleton */}
              <div className="space-y-2 mb-3">
                <LoadingSkeleton variant="text" width="100%" height="16px" />
                <LoadingSkeleton variant="text" width="85%" height="16px" />
                <LoadingSkeleton variant="text" width="60%" height="16px" />
              </div>
              
              {/* Tags skeleton */}
              <div className="flex gap-2">
                <LoadingSkeleton width="60px" height="20px" className="rounded-full" />
                <LoadingSkeleton width="80px" height="20px" className="rounded-full" />
                <LoadingSkeleton width="70px" height="20px" className="rounded-full" />
              </div>
            </div>
            
            {/* Action buttons skeleton */}
            <div className="flex items-center gap-2 ml-4">
              <LoadingSkeleton variant="button" width="60px" height="80px" />
              <LoadingSkeleton variant="button" width="40px" height="40px" />
              <LoadingSkeleton variant="button" width="40px" height="40px" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * EventHeaderSkeleton - Skeleton for event header
 */
export function EventHeaderSkeleton() {
  return (
    <div className="bg-white border-b border-gray-200 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Event title */}
        <LoadingSkeleton width="400px" height="32px" className="mb-4" />
        
        {/* Event details */}
        <div className="flex items-center gap-4 mb-4">
          <LoadingSkeleton width="150px" height="16px" />
          <LoadingSkeleton width="120px" height="16px" />
          <LoadingSkeleton width="100px" height="16px" />
        </div>
        
        {/* Tab navigation */}
        <div className="flex space-x-1">
          {Array.from({ length: 4 }).map((_, index) => (
            <LoadingSkeleton
              key={index}
              width="80px"
              height="36px"
              className="rounded-lg"
            />
          ))}
        </div>
      </div>
    </div>
  );
}
