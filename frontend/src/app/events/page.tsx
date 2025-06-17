'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Event } from '@/types';
import { eventService } from '@/services/eventService';
import { demoService } from '@/lib/demoData';
import EventCard from '@/components/events/EventCard';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Toggle this to use demo data or real API
const USE_DEMO_DATA = true;

export default function EventsPage() {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchEvents = async () => {
      try {
        let eventsData: Event[];
        if (USE_DEMO_DATA) {
          eventsData = await demoService.getEvents();
        } else {
          eventsData = await eventService.getEvents();
        }
        setEvents(eventsData);
      } catch (err) {
        setError('Failed to load events');
        console.error('Failed to fetch events:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [isAuthenticated, router]);

  const handleEventClick = (eventId: string) => {
    router.push(`/events/${eventId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-2">Error</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  const canCreateEvents = user?.role === 'moderator' || user?.role === 'presenter';

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-semibold text-gray-900">
                Luca AMA App
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">Welcome, {user?.name}</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">AMA Events</h1>
            {canCreateEvents && (
              <Link
                href="/events/create"
                className="btn-primary"
              >
                Create New Event
              </Link>
            )}
          </div>

          {events.length === 0 ? (
            <div className="text-center py-12">
              <h3 className="text-lg font-medium text-gray-900 mb-2">No events found</h3>
              <p className="text-gray-600 mb-4">
                {canCreateEvents 
                  ? "Get started by creating your first AMA event." 
                  : "No events are currently available. Check back later."}
              </p>
              {canCreateEvents && (
                <Link href="/events/create" className="btn-primary">
                  Create Your First Event
                </Link>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {events.map((event) => (
                <EventCard
                  key={event.id}
                  event={event}
                  onClick={() => handleEventClick(event.id)}
                  userRole={user?.role || 'user'}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
