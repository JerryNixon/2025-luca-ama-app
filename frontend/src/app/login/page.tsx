// Login Page Component - Simplified dual authentication interface
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const { login, microsoftLogin, getMicrosoftOAuthUrl, checkUserExists, isLoading } = useAuth();
  const router = useRouter();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [userExists, setUserExists] = useState<boolean | null>(null);
  const [checkingUser, setCheckingUser] = useState(false);

  // Clear tokens on page load
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('demo_token');
    }
  }, []);

  // Check if user exists when email is entered
  const handleEmailChange = async (newEmail: string) => {
    setEmail(newEmail);
    setError('');
    
    if (newEmail.includes('@') && newEmail.includes('.')) {
      setCheckingUser(true);
      try {
        const exists = await checkUserExists(newEmail);
        setUserExists(exists);
      } catch (error) {
        console.error('Error checking user existence:', error);
        setUserExists(null);
      } finally {
        setCheckingUser(false);
      }
    } else {
      setUserExists(null);
    }
  };

  // Handle Microsoft OAuth login
  const handleMicrosoftLogin = async () => {
    setError('');
    try {
      const oauthUrl = await getMicrosoftOAuthUrl();
      window.location.href = oauthUrl;
    } catch (err) {
      setError('Failed to initiate Microsoft login. Please try again.');
      console.error('Microsoft OAuth failed:', err);
    }
  };

  // Handle database login
  const handleDatabaseLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    console.log('Attempting database login for:', email);
    console.log('Password provided:', password ? 'Yes' : 'No');

    try {
      console.log('Calling login function...');
      await login({ email, password });
      console.log('Login successful, redirecting to dashboard');
      router.push('/dashboard');
    } catch (err: any) {
      console.error('Database login failed:', err);
      console.error('Error details:', err.response?.data);
      setError(`Invalid credentials. Please try again. (${err.message})`);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        
        {/* Header */}
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Sign in to Luca AMA
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Access your AMA events and participate in discussions
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Database Login Form */}
        <form className="space-y-6" onSubmit={handleDatabaseLogin}>
          <div className="text-center">
            <h3 className="text-lg font-medium text-gray-900">Database Login</h3>
            <p className="mt-2 text-sm text-gray-600">
              Sign in with your email and password.
            </p>
          </div>
          
          <div className="space-y-4">
            {/* Email Input */}
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
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={email}
                onChange={(e) => handleEmailChange(e.target.value)}
                placeholder="Enter your email address"
              />
              
              {/* User Status */}
              {checkingUser && (
                <p className="mt-2 text-sm text-gray-600">
                  🔍 Checking if you have an account...
                </p>
              )}
              
              {userExists === true && (
                <p className="mt-2 text-sm text-green-600">
                  ✅ Account found! You can log in with your password below.
                </p>
              )}
              
              {userExists === false && (
                <p className="mt-2 text-sm text-blue-600">
                  ℹ️ Account not found in database. You can use Microsoft login or try password login.
                </p>
              )}
            </div>
            
            {/* Password Input */}
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
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </div>
        </form>

        {/* Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-gray-50 text-gray-500">Or</span>
          </div>
        </div>

        {/* Microsoft Login */}
        <div className="space-y-4">
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
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-600">
          <p>
            <Link href="/" className="text-blue-600 hover:text-blue-500">
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
