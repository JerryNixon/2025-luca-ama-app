#!/usr/bin/env python3
"""
Debug Frontend Authentication State
This script creates a debug component to help identify authentication issues
"""

debug_component = '''
'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useEffect, useState } from 'react';

export default function DebugAuth() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [cookieToken, setCookieToken] = useState<string | null>(null);
  const [localStorageToken, setLocalStorageToken] = useState<string | null>(null);

  useEffect(() => {
    // Check for tokens in browser storage
    const checkTokens = () => {
      // Check cookies
      const cookies = document.cookie.split(';').reduce((acc, cookie) => {
        const [key, value] = cookie.trim().split('=');
        acc[key] = value;
        return acc;
      }, {} as Record<string, string>);
      
      setCookieToken(cookies['access_token'] || null);
      
      // Check localStorage
      const localToken = localStorage.getItem('demo_token');
      setLocalStorageToken(localToken);
    };

    checkTokens();
    
    // Check tokens periodically
    const interval = setInterval(checkTokens, 1000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return <div>Loading authentication state...</div>;
  }

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      right: 0, 
      background: '#f0f0f0', 
      padding: '10px', 
      border: '1px solid #ccc',
      zIndex: 9999,
      maxWidth: '300px',
      fontSize: '12px'
    }}>
      <h3>🔍 Auth Debug</h3>
      <p><strong>Is Authenticated:</strong> {isAuthenticated ? '✅ Yes' : '❌ No'}</p>
      <p><strong>Is Loading:</strong> {isLoading ? '⏳ Yes' : '✅ No'}</p>
      <p><strong>User:</strong> {user ? user.name : 'None'}</p>
      <p><strong>Email:</strong> {user ? user.email : 'None'}</p>
      <p><strong>Can Create Events:</strong> {user?.can_create_events ? '✅ Yes' : '❌ No'}</p>
      <p><strong>Cookie Token:</strong> {cookieToken ? `${cookieToken.substring(0, 20)}...` : 'None'}</p>
      <p><strong>LocalStorage Token:</strong> {localStorageToken ? `${localStorageToken.substring(0, 20)}...` : 'None'}</p>
      <p><strong>Current Path:</strong> {typeof window !== 'undefined' ? window.location.pathname : 'Unknown'}</p>
    </div>
  );
}
'''

with open('c:/Users/t-lucahadife/Documents/luca-ama-app/frontend/src/components/DebugAuth.tsx', 'w', encoding='utf-8') as f:
    f.write(debug_component)

print("Created DebugAuth.tsx component")
print("Add this to your layout or events page to debug authentication state")
