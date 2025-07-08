// Microsoft OAuth Callback Handler
// This page handles the callback from Microsoft OAuth and completes the authentication

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function MicrosoftCallbackPage() {
  const { microsoftLogin } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [error, setError] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the authorization code from URL parameters
        const code = searchParams.get('code');
        const error = searchParams.get('error');
        
        if (error) {
          setError(`Microsoft OAuth error: ${error}`);
          setStatus('error');
          return;
        }
        
        if (!code) {
          setError('No authorization code received from Microsoft');
          setStatus('error');
          return;
        }

        // Complete the Microsoft OAuth login
        await microsoftLogin(code);
        setStatus('success');
        
        // Redirect to dashboard after successful login
        setTimeout(() => {
          router.push('/dashboard');
        }, 2000);
        
      } catch (err) {
        console.error('Microsoft OAuth callback error:', err);
        setError('Failed to complete Microsoft authentication');
        setStatus('error');
      }
    };

    handleCallback();
  }, [searchParams, microsoftLogin, router]);

  // Render based on current status
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full text-center space-y-6">
        
        {status === 'processing' && (
          <>
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
            <h2 className="text-2xl font-bold text-gray-900">Processing Microsoft Login</h2>
            <p className="text-gray-600">
              Please wait while we complete your authentication...
            </p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="text-green-500 text-6xl">✅</div>
            <h2 className="text-2xl font-bold text-gray-900">Login Successful!</h2>
            <p className="text-gray-600">
              You have been successfully authenticated with Microsoft.
            </p>
            <p className="text-sm text-gray-500">
              Redirecting to dashboard...
            </p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="text-red-500 text-6xl">❌</div>
            <h2 className="text-2xl font-bold text-gray-900">Authentication Failed</h2>
            <p className="text-gray-600 mb-4">
              {error}
            </p>
            <button
              onClick={() => router.push('/login')}
              className="btn-primary"
            >
              Back to Login
            </button>
          </>
        )}
        
      </div>
    </div>
  );
}
