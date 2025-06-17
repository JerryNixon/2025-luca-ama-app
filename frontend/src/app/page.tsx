// Home Page Component - Main landing page for authenticated users
// This is a client-side component that provides the main dashboard interface

// Mark as client component since we're using React hooks and browser APIs
'use client';

// Import authentication hook to manage user state and authentication status
import { useAuth } from '@/contexts/AuthContext';
// Import Next.js router for programmatic navigation
import { useRouter } from 'next/navigation';
// Import React hook for handling side effects (redirects, etc.)
import { useEffect } from 'react';
// Import Next.js optimized Link component for client-side routing
import Link from 'next/link';

/**
 * HomePage Component
 * 
 * This is the main dashboard page that users see after logging in.
 * Features:
 * - Authentication check and automatic redirect to login if not authenticated
 * - Welcome message with user information
 * - Navigation cards for different app features
 * - Role-based access control (moderators/presenters see additional options)
 * - Loading state management
 * 
 * @returns JSX element representing the home page dashboard
 */
export default function HomePage() {
  // Destructure authentication state and user information from context
  const { user, isLoading, isAuthenticated } = useAuth();
  // Get router instance for programmatic navigation
  const router = useRouter();

  // Effect hook to handle authentication redirects
  // Runs whenever loading state or authentication status changes
  useEffect(() => {
    // If we're done loading and user is not authenticated, redirect to login
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Show loading spinner while authentication state is being determined
  // This prevents flash of content before redirect
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        {/* Tailwind CSS animated spinner with primary color border */}
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Return null if not authenticated (user will be redirected)
  // This prevents any content from showing during the redirect process
  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  // Main dashboard content for authenticated users
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Left side - App branding */}
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Luca AMA App</h1>
            </div>
            {/* Right side - User information and role badge */}
            <div className="flex items-center space-x-4">
              {/* Personalized welcome message using optional chaining for safety */}
              <span className="text-sm text-gray-700">Welcome, {user?.name}</span>
              {/* Role badge with color coding - helps users understand their permissions */}
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                {user?.role}
              </span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center">
            {/* Hero Section - Main heading and description */}
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Welcome to AMA Events
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Manage your Ask Me Anything sessions, submit questions, and engage with participants.
            </p>
            
            {/* Feature Cards Grid - Responsive grid layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl mx-auto">
              
              {/* Browse Events Card - Available to all authenticated users */}
              <Link href="/events" className="card hover:shadow-lg transition-shadow">
                <div className="text-center">
                  {/* Icon container with emoji - could be replaced with proper icons */}
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    📅
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Browse Events</h3>
                  <p className="text-gray-600">View and join available AMA sessions</p>
                </div>
              </Link>

              {/* Create Event Card - Only shown to moderators and presenters */}
              {/* This demonstrates role-based UI rendering */}
              {(user?.role === 'moderator' || user?.role === 'presenter') && (
                <Link href="/events/create" className="card hover:shadow-lg transition-shadow">
                  <div className="text-center">
                    {/* Green color scheme for creation/positive actions */}
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                      ➕
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Create Event</h3>
                    <p className="text-gray-600">Start a new AMA session</p>
                  </div>
                </Link>
              )}

              {/* Profile Card - Available to all authenticated users */}
              <Link href="/profile" className="card hover:shadow-lg transition-shadow">
                <div className="text-center">
                  {/* Purple color scheme for profile/user-related actions */}
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    👤
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Profile</h3>
                  <p className="text-gray-600">Manage your account settings</p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
