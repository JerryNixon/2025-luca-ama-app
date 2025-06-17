// Login Page Component - User authentication interface
// This page handles user login with email and password authentication

// Mark as client component for form handling and state management
'use client';

// Import React hooks for state management
import { useState } from 'react';
// Import authentication context for login functionality
import { useAuth } from '@/contexts/AuthContext';
// Import Next.js router for navigation after successful login
import { useRouter } from 'next/navigation';
// Import Next.js Link component for internal navigation
import Link from 'next/link';

/**
 * LoginPage Component
 * 
 * This component provides a user authentication interface with:
 * - Email and password form inputs
 * - Form validation and error handling
 * - Loading states during authentication
 * - Demo credentials for testing
 * - Navigation after successful login
 * 
 * @returns JSX element representing the login page
 */
export default function LoginPage() {
  // Get login function and loading state from authentication context
  const { login, isLoading } = useAuth();
  // Router instance for programmatic navigation after login
  const router = useRouter();
  
  // Form state management
  const [email, setEmail] = useState('');           // User's email input
  const [password, setPassword] = useState('');     // User's password input
  const [error, setError] = useState('');           // Error message for failed login attempts

  /**
   * Handle form submission for user login
   * Prevents default form behavior, validates inputs, and attempts authentication
   * 
   * @param e - React form event object
   */
  const handleSubmit = async (e: React.FormEvent) => {
    // Prevent default form submission behavior (page reload)
    e.preventDefault();
    // Clear any previous error messages
    setError('');

    try {
      // Attempt to authenticate user with provided credentials
      await login({ email, password });
      // If login successful, redirect to home page
      router.push('/');
    } catch (err) {
      // If login fails, show user-friendly error message
      setError('Invalid credentials. Please try again.');
      // Log detailed error information for debugging
      console.error('Login failed:', err);
    }
  };

  // Render login page with centered form layout
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      {/* Main login form container with responsive width */}
      <div className="max-w-md w-full space-y-8">
        
        {/* Page Header Section */}
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Sign in to Luca AMA
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Access your AMA events and participate in discussions
          </p>
        </div>
        
        {/* Login Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          
          {/* Error Message Display */}
          {/* Only show error message when there's an error to display */}
          {error && (
            <div className="bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          
          {/* Form Input Fields */}
          <div className="space-y-4">
            
            {/* Email Input Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"                                      // Unique ID for accessibility
                name="email"                                    // Form field name
                type="email"                                    // HTML5 email validation
                autoComplete="email"                            // Browser autocomplete hint
                required                                        // HTML5 required validation
                className="input-field mt-1"                   // Custom CSS class for styling
                value={email}                                   // Controlled input value
                onChange={(e) => setEmail(e.target.value)}      // Update state on change
                placeholder="Enter your email"
              />
            </div>
            
            {/* Password Input Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"                                   // Unique ID for accessibility
                name="password"                                 // Form field name
                type="password"                                 // Hide password input
                autoComplete="current-password"                 // Browser autocomplete hint
                required                                        // HTML5 required validation
                className="input-field mt-1"                   // Custom CSS class for styling
                value={password}                                // Controlled input value
                onChange={(e) => setPassword(e.target.value)}   // Update state on change
                placeholder="Enter your password"
              />
            </div>
          </div>

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              disabled={isLoading}                              // Disable during authentication
              className={`w-full btn-primary ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {/* Dynamic button text based on loading state */}
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>

          {/* Demo Credentials and Navigation */}
          <div className="text-center text-sm text-gray-600">
            {/* Demo credentials for testing purposes */}
            <p>Demo Login:</p>
            <p>Email: demo@microsoft.com | Password: demo123</p>
            {/* Link back to home page */}
            <p className="mt-2">
              <Link href="/" className="text-primary-600 hover:text-primary-500">
                Back to Home
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
