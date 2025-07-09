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

export default function JoinLinkPage({ params }: JoinLinkPageProps) {
  const { shareLink } = params;
  const { isAuthenticated, user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [event, setEvent] = useState<Event | null>(null);
  const [joining, setJoining] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      // Redirect to login with return URL
      router.push(`/login?returnUrl=${encodeURIComponent(`/join/${shareLink}`)}`);
      return;
    }

    // Try to join the event
    joinEvent();
  }, [isAuthenticated, shareLink]);

  const joinEvent = async () => {
    try {
      setLoading(true);
      setJoining(true);
      
      const response = await apiClient.post(`/events/join/${shareLink}/`);
      
      if (response.data.success) {
        setEvent(response.data.data);
        // Redirect to event page after successful join
        setTimeout(() => {
          router.push(`/events/${response.data.data.id}`);
        }, 2000);
      } else {
        setError(response.data.message || 'Failed to join event');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to join event');
    } finally {
      setLoading(false);
      setJoining(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Processing your invitation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-500 text-6xl mb-4">❌</div>
          <h2 className="text-xl font-semibold text-red-600 mb-2">Unable to Join Event</h2>
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

  if (event) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-green-500 text-6xl mb-4">✅</div>
          <h2 className="text-xl font-semibold text-green-600 mb-2">Successfully Joined!</h2>
          <p className="text-gray-600 mb-4">
            You have successfully joined <strong>{event.name}</strong>
          </p>
          <p className="text-sm text-gray-500 mb-4">
            Redirecting you to the event page...
          </p>
          <button
            onClick={() => router.push(`/events/${event.id}`)}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
          >
            Go to Event
          </button>
        </div>
      </div>
    );
  }

  return null;
}
