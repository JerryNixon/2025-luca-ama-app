'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'next/navigation';

/**
 * Profile Page Component
 * 
 * This page allows users to:
 * 1. View their current profile information (name, email, role, join date)
 * 2. Edit their profile details (name and email)
 * 3. View their activity statistics (events created, questions asked, etc.)
 * 4. Manage their account settings
 * 
 * Features:
 * - Protected route (requires authentication)
 * - Form validation for profile updates
 * - Role-based content display
 * - Activity summary based on user's role
 * - Responsive design with Tailwind CSS
 */

// Interface for user profile data
interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: 'user' | 'presenter' | 'moderator';
  joinDate: string;
  bio?: string;
  department?: string;
}

// Interface for user activity statistics
interface UserActivity {
  eventsCreated: number;
  questionsAsked: number;
  questionsAnswered: number;
  eventsAttended: number;
}

export default function ProfilePage() {
  // Get authentication context and router for navigation
  const { user, logout } = useAuth();
  const router = useRouter();

  // State for profile editing
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [editForm, setEditForm] = useState({
    name: '',
    email: '',
    bio: '',
    department: ''
  });

  // State for user activity statistics
  const [activity, setActivity] = useState<UserActivity>({
    eventsCreated: 0,
    questionsAsked: 0,
    questionsAnswered: 0,
    eventsAttended: 0
  });

  // Loading and error states
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Effect to check authentication and load profile data
   * Redirects to login if user is not authenticated
   */
  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    // Load user profile data
    loadProfileData();
  }, [user, router]);

  /**
   * Simulates loading profile data from an API
   * In a real app, this would fetch from your backend
   */
  const loadProfileData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));      // Mock profile data based on current user
      const mockProfile: UserProfile = {
        id: user?.id || '1',
        name: user?.name || 'John Doe',
        email: user?.email || 'john@university.edu',
        role: user?.role || 'user',
        joinDate: '2023-09-01',
        bio: `Hello! I'm a ${user?.role} at the university.`,
        department: user?.role === 'presenter' ? 'Computer Science' : 'Information Technology'
      };

      // Mock activity data based on user role
      const mockActivity: UserActivity = {
        eventsCreated: user?.role === 'presenter' ? 8 : user?.role === 'moderator' ? 15 : 0,
        questionsAsked: user?.role === 'user' ? 24 : 5,
        questionsAnswered: user?.role === 'presenter' ? 156 : user?.role === 'moderator' ? 89 : 12,
        eventsAttended: user?.role === 'user' ? 12 : 8
      };

      setProfile(mockProfile);
      setActivity(mockActivity);
      
      // Initialize edit form with current data
      setEditForm({
        name: mockProfile.name,
        email: mockProfile.email,
        bio: mockProfile.bio || '',
        department: mockProfile.department || ''
      });

    } catch (err) {
      setError('Failed to load profile data. Please try again.');
      console.error('Profile loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handles form input changes for profile editing
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEditForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * Saves profile changes
   * In a real app, this would send data to your backend API
   */
  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      setError(null);

      // Basic validation
      if (!editForm.name.trim() || !editForm.email.trim()) {
        setError('Name and email are required.');
        return;
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(editForm.email)) {
        setError('Please enter a valid email address.');
        return;
      }

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Update profile state
      if (profile) {
        setProfile({
          ...profile,
          name: editForm.name,
          email: editForm.email,
          bio: editForm.bio,
          department: editForm.department
        });
      }

      setIsEditing(false);
      
      // Show success message (in real app, you might use a toast notification)
      alert('Profile updated successfully!');

    } catch (err) {
      setError('Failed to save profile changes. Please try again.');
      console.error('Profile save error:', err);
    } finally {
      setSaving(false);
    }
  };

  /**
   * Cancels profile editing and resets form
   */
  const handleCancelEdit = () => {
    if (profile) {
      setEditForm({
        name: profile.name,
        email: profile.email,
        bio: profile.bio || '',
        department: profile.department || ''
      });
    }
    setIsEditing(false);
    setError(null);
  };

  /**
   * Handles user logout
   */
  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Show loading spinner
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // Show error if profile couldn't be loaded
  if (!profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Error Loading Profile</h1>
          <p className="text-gray-600 mb-4">{error || 'Something went wrong.'}</p>
          <button
            onClick={loadProfileData}
            className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
              <p className="text-gray-600 mt-1">Manage your account settings and information</p>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Information Card */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Personal Information</h2>
                {!isEditing && (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 transition-colors"
                  >
                    Edit Profile
                  </button>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <p className="text-red-700">{error}</p>
                </div>
              )}

              {isEditing ? (
                /* Edit Mode */
                <div className="space-y-4">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                      Full Name
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={editForm.name}
                      onChange={handleInputChange}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={editForm.email}
                      onChange={handleInputChange}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">
                      Department
                    </label>
                    <input
                      type="text"
                      id="department"
                      name="department"
                      value={editForm.department}
                      onChange={handleInputChange}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div>
                    <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-1">
                      Bio
                    </label>
                    <textarea
                      id="bio"
                      name="bio"
                      value={editForm.bio}
                      onChange={handleInputChange}
                      rows={4}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Tell us about yourself..."
                    />
                  </div>

                  <div className="flex space-x-3 pt-4">
                    <button
                      onClick={handleSaveProfile}
                      disabled={saving}
                      className="bg-primary-500 text-white px-6 py-2 rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      disabled={saving}
                      className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                /* View Mode */
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Full Name</label>
                    <p className="text-gray-900 text-lg">{profile.name}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Email Address</label>
                    <p className="text-gray-900">{profile.email}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Role</label>                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium capitalize ${
                      profile.role === 'moderator' ? 'bg-red-100 text-red-800' :
                      profile.role === 'presenter' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {profile.role}
                    </span>
                  </div>

                  {profile.department && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Department</label>
                      <p className="text-gray-900">{profile.department}</p>
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Member Since</label>
                    <p className="text-gray-900">{new Date(profile.joinDate).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}</p>
                  </div>

                  {profile.bio && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Bio</label>
                      <p className="text-gray-900">{profile.bio}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Activity Statistics Card */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Summary</h3>              <div className="space-y-4">
                {profile.role === 'presenter' || profile.role === 'moderator' ? (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Events Created</span>
                    <span className="font-semibold text-primary-600">{activity.eventsCreated}</span>
                  </div>
                ) : null}

                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Questions Asked</span>
                  <span className="font-semibold text-secondary-600">{activity.questionsAsked}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Questions Answered</span>
                  <span className="font-semibold text-green-600">{activity.questionsAnswered}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Events Attended</span>
                  <span className="font-semibold text-blue-600">{activity.eventsAttended}</span>
                </div>
              </div>
            </div>

            {/* Quick Actions Card */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => router.push('/events')}
                  className="w-full bg-primary-50 text-primary-700 px-4 py-2 rounded-lg hover:bg-primary-100 transition-colors text-left"
                >
                  View All Events
                </button>                
                {(profile.role === 'presenter' || profile.role === 'moderator') && (
                  <button
                    onClick={() => router.push('/events/create')}
                    className="w-full bg-secondary-50 text-secondary-700 px-4 py-2 rounded-lg hover:bg-secondary-100 transition-colors text-left"
                  >
                    Create New Event
                  </button>
                )}
                
                <button
                  onClick={() => router.push('/')}
                  className="w-full bg-gray-50 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors text-left"
                >
                  Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
