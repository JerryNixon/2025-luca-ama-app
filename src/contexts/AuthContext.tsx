'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, AuthContextType, LoginForm } from '@/types';
import { authService } from '@/services/authService';
import { demoService } from '@/lib/demoData';
import Cookies from 'js-cookie';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Toggle this to use demo data or real API
const USE_DEMO_DATA = true;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  useEffect(() => {
    const initializeAuth = async () => {
      if (USE_DEMO_DATA) {
        // For demo, just set a default user
        const token = localStorage.getItem('demo_token');
        if (token) {
          const demoUser = demoService.getCurrentUser();
          setUser(demoUser);
        }
      } else {
        const token = Cookies.get('access_token');
        if (token) {
          try {
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
          } catch (error) {
            console.error('Failed to get current user:', error);
            // Token might be invalid, remove it
            await authService.logout();
          }
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginForm) => {
    setIsLoading(true);
    try {
      if (USE_DEMO_DATA) {
        const { user: loggedInUser, token } = await demoService.login(credentials.email, credentials.password);
        localStorage.setItem('demo_token', token);
        setUser(loggedInUser);
      } else {
        const { user: loggedInUser } = await authService.login(credentials);
        setUser(loggedInUser);
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      if (USE_DEMO_DATA) {
        localStorage.removeItem('demo_token');
      } else {
        await authService.logout();
      }
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    login,
    logout,
    isLoading,
    isAuthenticated,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
