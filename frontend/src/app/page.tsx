'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

/**
 * Root Page Component - Handles initial routing
 * 
 * This component ensures that unauthenticated users are immediately
 * redirected to the login page when accessing the root URL.
 * Authenticated users are redirected to the events page.
 */
export default function RootPage() {
  const router = useRouter();
  useEffect(() => {
    // Check for authentication token
    const demoToken = typeof window !== 'undefined' ? localStorage.getItem('demo_token') : null;
    
    if (demoToken) {
      // User is authenticated, redirect to dashboard page (Welcome to Luca AMA)
      console.log('User authenticated, redirecting to dashboard...');
      router.replace('/dashboard');
    } else {
      // User is not authenticated, redirect to login
      console.log('User not authenticated, redirecting to login...');
      router.replace('/login');
    }
  }, [router]);

  // Show minimal loading while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Redirecting...</p>
      </div>
    </div>
  );
}
