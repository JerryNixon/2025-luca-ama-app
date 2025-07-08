// Login Page Component - Dual authentication interface
// This page handles both Microsoft Entra ID OAuth and manual database login

// Mark as client component for form handling and state management
'use client';

// Import React hooks for state management
import { useState, useEffect } from 'react';
// Import authentication context for login functionality
import { useAuth } from '@/contexts/AuthContext';
// Import Next.js router for navigation after successful login
import { useRouter } from 'next/navigation';
// Import Next.js Link component for internal navigation
import Link from 'next/link';

/**
 * LoginPage Component
 * 
 * This component provides a dual authentication interface with:
 * - Microsoft Entra ID OAuth login (primary method)
 * - Manual database login (for admin-added users)
 * - Dynamic UI based on user type
 * - Form validation and error handling
 * - Loading states during authentication
 * 
 * @returns JSX element representing the login page
 */
export default function LoginPage() {
  // Get authentication functions from context
  const { login, microsoftLogin, getMicrosoftOAuthUrl, checkUserExists, isLoading } = useAuth();
  // Router instance for programmatic navigation after login
  const router = useRouter();
  
  // Form state management
  const [email, setEmail] = useState('');           // User's email input
  const [password, setPassword] = useState('');     // User's password input
  const [error, setError] = useState('');           // Error message for failed attempts
  const [authMethod, setAuthMethod] = useState<'choose' | 'microsoft' | 'manual'>('choose'); // Authentication method
  const [userExists, setUserExists] = useState<boolean | null>(null); // Whether user exists in database
  const [checkingUser, setCheckingUser] = useState(false); // Loading state for user check

  // Clear any existing authentication tokens when login page loads
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('demo_token');
      console.log('Cleared existing demo tokens');
    }
  }, []);

  /**
   * Check if user exists in database when email is entered
   */
  const handleEmailChange = async (newEmail: string) => {
    setEmail(newEmail);
    setError('');
    
    // Only check if it's a valid email format
    if (newEmail.includes('@') && newEmail.includes('.')) {
      setCheckingUser(true);
      try {
        const exists = await checkUserExists(newEmail);
        setUserExists(exists);
        
        // If user exists in database, default to manual login
        // If user doesn't exist, they should use Microsoft OAuth
        if (exists) {
          setAuthMethod('manual');
        } else {
          setAuthMethod('microsoft');
        }
      } catch (error) {
        console.error('Error checking user existence:', error);
        setUserExists(null);
      } finally {
        setCheckingUser(false);
      }
    } else {
      setUserExists(null);
      setAuthMethod('choose');
    }
  };

  /**
   * Handle Microsoft OAuth login
   */
  const handleMicrosoftLogin = async () => {
    setError('');
    try {
      const oauthUrl = await getMicrosoftOAuthUrl();
      // Redirect to Microsoft OAuth
      window.location.href = oauthUrl;
    } catch (err) {
      setError('Failed to initiate Microsoft login. Please try again.');
      console.error('Microsoft OAuth failed:', err);
    }
  };

  /**
   * Handle manual database login
   */
  const handleManualLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await login({ email, password });
      router.push('/dashboard');
    } catch (err) {
      setError('Invalid credentials. Please try again.');
      console.error('Manual login failed:', err);
    }
  };

  // Render login page with dual authentication options
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        
        {/* Page Header */}
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Sign in to Luca AMA
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Access your AMA events and participate in discussions
          </p>
        </div>

        {/* Error Message Display */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Authentication Method Selection */}
        {authMethod === 'choose' && (
          <div className="space-y-6">
            
            {/* Email Input for User Detection */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="input-field mt-1"
                value={email}
                onChange={(e) => handleEmailChange(e.target.value)}
                placeholder="Enter your email to get started"
              />
              
              {/* User Status Indicator */}
              {checkingUser && (
                <p className="mt-2 text-sm text-gray-600">
                  🔍 Checking if you have an account...
                </p>
              )}
              
              {userExists === true && (
                <p className="mt-2 text-sm text-green-600">
                  ✅ Account found! You can log in with your password.
                </p>
              )}
              
              {userExists === false && (
                <p className="mt-2 text-sm text-blue-600">
                  🔑 New user? Sign in with Microsoft Entra ID.
                </p>
              )}
            </div>

            {/* Authentication Options */}
            <div className="space-y-4">
              
              {/* Microsoft OAuth Login */}
              <button
                onClick={handleMicrosoftLogin}
                disabled={isLoading}
                className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path fill="#00BCF2" d="M0 0h11.377v11.372H0z"/>
                  <path fill="#0078D4" d="M12.623 0H24v11.372H12.623z"/>
                  <path fill="#00BCF2" d="M0 12.623h11.377V24H0z"/>
                  <path fill="#FFB900" d="M12.623 12.623H24V24H12.623z"/>
                </svg>
                {isLoading ? 'Redirecting...' : 'Sign in with Microsoft'}
              </button>
              
              {/* Manual Login Option */}
              <button
                onClick={() => setAuthMethod('manual')}
                disabled={isLoading}
                className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
              >
                🔑 Sign in with Password
              </button>
            </div>
          </div>
        )}

        {/* Microsoft OAuth Method */}
        {authMethod === 'microsoft' && (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">Microsoft Account Required</h3>
              <p className="mt-2 text-sm text-gray-600">
                Your email ({email}) is not in our database. Please sign in with your Microsoft account.
              </p>
            </div>
            
            <button
              onClick={handleMicrosoftLogin}
              disabled={isLoading}
              className="w-full flex justify-center items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path fill="currentColor" d="M0 0h11.377v11.372H0z"/>
                <path fill="currentColor" d="M12.623 0H24v11.372H12.623z"/>
                <path fill="currentColor" d="M0 12.623h11.377V24H0z"/>
                <path fill="currentColor" d="M12.623 12.623H24V24H12.623z"/>
              </svg>
              {isLoading ? 'Redirecting to Microsoft...' : 'Continue with Microsoft'}
            </button>
            
            <button
              onClick={() => setAuthMethod('choose')}
              className="w-full text-sm text-gray-600 hover:text-gray-500"
            >
              ← Back to login options
            </button>
          </div>
        )}

        {/* Manual Database Login */}
        {authMethod === 'manual' && (
          <form className="space-y-6" onSubmit={handleManualLogin}>
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">Database Login</h3>
              <p className="mt-2 text-sm text-gray-600">
                Your account ({email}) was found in our database. Please enter your password.
              </p>
            </div>
            
            <div className="space-y-4">
              {/* Email (read-only) */}
              <div>
                <label htmlFor="email-readonly" className="block text-sm font-medium text-gray-700">
                  Email address
                </label>
                <input
                  id="email-readonly"
                  type="email"
                  className="input-field mt-1 bg-gray-50"
                  value={email}
                  readOnly
                />
              </div>
              
              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className="input-field mt-1"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <div className="space-y-4">
              <button
                type="submit"
                disabled={isLoading}
                className={`w-full btn-primary ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </button>
              
              <button
                type="button"
                onClick={() => setAuthMethod('choose')}
                className="w-full text-sm text-gray-600 hover:text-gray-500"
              >
                ← Back to login options
              </button>
            </div>
          </form>
        )}

        {/* Footer */}
        <div className="text-center text-sm text-gray-600">
          <p>
            <Link href="/" className="text-primary-600 hover:text-primary-500">
              Back to Home
            </Link>
          </p>
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="font-medium">Two ways to sign in:</p>
            <p className="mt-1">🔑 <strong>Microsoft Entra ID:</strong> For all Microsoft employees</p>
            <p>🔐 <strong>Database Login:</strong> For manually added users</p>
          </div>
        </div>
      </div>
    </div>
  );
}
