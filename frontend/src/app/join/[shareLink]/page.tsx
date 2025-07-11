'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Event } from '@/types';
import apiClient from '@/lib/api';

interface JoinLinkPageProps {
  params: {
    shareLink: string;
  };
}

interface EventInfo {
  id: string;
  name: string;
  created_by: string;
}

export default function JoinLinkPage({ params }: JoinLinkPageProps) {
  const { shareLink } = params;
  const { isAuthenticated, user, login } = useAuth();
  const router = useRouter();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [eventInfo, setEventInfo] = useState<EventInfo | null>(null);
  const [processing, setProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Form state
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [userExists, setUserExists] = useState<boolean | null>(null);

  useEffect(() => {
    fetchEventInfo();
  }, [shareLink]);

  useEffect(() => {
    if (isAuthenticated && eventInfo) {
      // User is already authenticated, try to join event
      handleAuthenticatedJoin();
    }
  }, [isAuthenticated, eventInfo]);

  const fetchEventInfo = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/events/join/${shareLink}/`);
      
      if (response.data.success) {
        setEventInfo(response.data.data.event);
      } else {
        setError('Invalid or expired share link');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid or expired share link');
    } finally {
      setLoading(false);
    }
  };

  const handleAuthenticatedJoin = async () => {
    try {
      setProcessing(true);
      const response = await apiClient.post(`/events/join/${shareLink}/`);
      
      if (response.data.success) {
        setSuccess(true);
        setSuccessMessage(response.data.message);
        
        // Redirect after success
        setTimeout(() => {
          router.push(response.data.redirect_url || `/events/${response.data.data.event?.id || eventInfo?.id}`);
        }, 2000);
      } else {
        setError(response.data.message || 'Failed to join event');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to join event');
    } finally {
      setProcessing(false);
    }
  };

  const checkUserExists = async (email: string) => {
    try {
      const response = await apiClient.post('/auth/check-user/', { email });
      const exists = response.data.data?.exists || false;
      setUserExists(exists);
      setIsLoginMode(exists);
      return exists;
    } catch (err) {
      console.error('Error checking user:', err);
      return false;
    }
  };

  const handleEmailChange = async (email: string) => {
    setFormData({ ...formData, email });
    
    if (email.includes('@')) {
      await checkUserExists(email);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setProcessing(true);

    try {
      const action = isLoginMode ? 'login' : 'register';
      const response = await apiClient.post(`/events/join/${shareLink}/`, {
        action,
        email: formData.email,
        password: formData.password,
        name: formData.name
      });

      if (response.data.success) {
        // Store auth data
        await login(response.data.data.user, response.data.data.token, response.data.data.refresh);
        
        setSuccess(true);
        setSuccessMessage(response.data.message);
        
        // Redirect after success
        setTimeout(() => {
          router.push(response.data.redirect_url || `/events/${response.data.data.event?.id}`);
        }, 2000);
      } else {
        setError(response.data.message || 'Authentication failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Authentication failed');
    } finally {
      setProcessing(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading event information...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !eventInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-500 text-6xl mb-4">❌</div>
          <h2 className="text-xl font-semibold text-red-600 mb-2">Invalid Share Link</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/events')}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
          >
            Go to Events
          </button>
        </div>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-green-500 text-6xl mb-4">✅</div>
          <h2 className="text-xl font-semibold text-green-600 mb-2">Success!</h2>
          <p className="text-gray-600 mb-4">{successMessage}</p>
          <p className="text-sm text-gray-500 mb-4">Redirecting you to the event...</p>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  // Processing authenticated user join
  if (isAuthenticated && processing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Adding you to the event...</p>
        </div>
      </div>
    );
  }

  // Main form for non-authenticated users
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Join AMA Event
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            You've been invited to join <strong>{eventInfo?.name}</strong>
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Created by {eventInfo?.created_by}
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={formData.email}
                onChange={(e) => handleEmailChange(e.target.value)}
              />
            </div>

            {!isLoginMode && (
              <div>
                <label htmlFor="name" className="sr-only">Full name</label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                  placeholder="Full name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
            )}

            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete={isLoginMode ? "current-password" : "new-password"}
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>
          </div>

          {userExists !== null && (
            <div className="text-center">
              <p className="text-sm text-gray-600">
                {userExists ? (
                  <>
                    Welcome back! Please <strong>log in</strong> to join this event.
                  </>
                ) : (
                  <>
                    New user? <strong>Create an account</strong> to join this event.
                  </>
                )}
              </p>
              {userExists && !isLoginMode && (
                <button
                  type="button"
                  onClick={() => setIsLoginMode(true)}
                  className="text-primary-600 hover:text-primary-500 text-sm font-medium"
                >
                  Switch to login
                </button>
              )}
              {!userExists && isLoginMode && (
                <button
                  type="button"
                  onClick={() => setIsLoginMode(false)}
                  className="text-primary-600 hover:text-primary-500 text-sm font-medium"
                >
                  Switch to register
                </button>
              )}
            </div>
          )}

          {error && (
            <div className="text-center">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={processing}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {processing ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </div>
              ) : (
                <>
                  {isLoginMode ? 'Log in' : 'Create account'} and join event
                </>
              )}
            </button>
          </div>

          <div className="text-center">
            <p className="text-xs text-gray-500">
              By joining, you'll become a participant in this AMA event
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
