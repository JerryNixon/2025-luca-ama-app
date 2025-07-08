// Authentication Context - Centralized user authentication and state management
// This context provides authentication functionality throughout the entire application

// Mark as client component for browser-specific functionality (localStorage, cookies)
'use client';

// Import React hooks and utilities for context creation
import React, { createContext, useContext, useEffect, useState } from 'react';
// Import TypeScript types for type safety
import { User, AuthContextType, LoginForm } from '@/types';
// Import authentication services
import { authService } from '@/services/authService';
import { demoService } from '@/lib/demoData';
// Import cookie handling library for secure token storage
import Cookies from 'js-cookie';

// Create the authentication context with undefined default value
// This forces proper error handling when context is used outside of provider
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Development toggle for switching between demo data and real API
// Set to false to use real backend authentication with Fabric database
const USE_DEMO_DATA = false;

/**
 * AuthProvider Component
 * 
 * Provides authentication context to all child components.
 * Features:
 * - User state management (login/logout)
 * - Persistent authentication via tokens
 * - Loading states during authentication operations
 * - Automatic token validation and refresh
 * - Demo mode for development and testing
 * 
 * @param children - React components that need access to authentication
 * @returns JSX provider component wrapping children with auth context
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  // Authentication state management
  const [user, setUser] = useState<User | null>(null);        // Current authenticated user
  const [isLoading, setIsLoading] = useState(true);           // Loading state for async operations

  // Computed property - user is authenticated if user object exists
  const isAuthenticated = !!user;

  // Effect hook to initialize authentication on app startup
  // Checks for existing tokens and validates user session
  useEffect(() => {
    /**
     * Initialize authentication state
     * Checks for existing authentication tokens and validates user session
     */    const initializeAuth = async () => {
      if (USE_DEMO_DATA) {
        // Demo mode - check localStorage for demo token
        const token = localStorage.getItem('demo_token');
        if (token) {
          // Get demo user data if token exists and is valid
          const demoUser = demoService.getCurrentUser();
          if (demoUser) {
            setUser(demoUser);
          } else {
            // Token exists but is invalid, clean up
            localStorage.removeItem('demo_token');
          }
        }
      } else {
        // Production mode - check secure HTTP-only cookie for token
        const token = Cookies.get('access_token');
        if (token) {
          try {
            // Validate token and get current user from API
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
          } catch (error) {
            console.error('Failed to get current user:', error);
            // Token might be invalid or expired, clean up
            await authService.logout();
          }
        }
      }
      // Set loading to false regardless of success or failure
      setIsLoading(false);
    };

    // Execute initialization
    initializeAuth();
  }, []); // Empty dependency array - only run on component mount

  /**
   * Login function
   * Authenticates user with provided credentials and updates application state
   * 
   * @param credentials - User login credentials (email and password)
   * @throws Error if authentication fails
   */
  const login = async (credentials: LoginForm) => {
    setIsLoading(true);
    try {
      if (USE_DEMO_DATA) {
        // Demo authentication - validate against hardcoded credentials
        const { user: loggedInUser, token } = await demoService.login(credentials.email, credentials.password);
        // Store demo token in localStorage (not secure, for demo only)
        localStorage.setItem('demo_token', token);
        setUser(loggedInUser);
      } else {
        // Production authentication - authenticate with backend API
        console.log('Attempting login with:', credentials.email);
        const { user: loggedInUser } = await authService.login(credentials);
        console.log('Login successful, user:', loggedInUser);
        // Real authentication sets HTTP-only cookie automatically
        setUser(loggedInUser);
      }
    } catch (error) {
      console.error('Login failed:', error);
      // Re-throw error so components can handle login failures
      throw error;
    } finally {
      // Always set loading to false, even if login fails
      setIsLoading(false);
    }
  };

  /**
   * Logout function
   * Clears user session and removes authentication tokens
   */  const logout = async () => {
    setIsLoading(true);
    try {
      if (USE_DEMO_DATA) {
        // Demo logout - use demoService to clear token
        await demoService.logout();
      } else {
        // Production logout - call API to invalidate token
        await authService.logout();
      }
      // Clear user state
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Microsoft OAuth login function
   * Authenticates user with Microsoft OAuth and updates application state
   * 
   * @param code - OAuth authorization code from Microsoft
   * @throws Error if OAuth authentication fails
   */
  const microsoftLogin = async (code: string) => {
    setIsLoading(true);
    try {
      console.log('Attempting Microsoft OAuth login with code:', code);
      const { user: loggedInUser } = await authService.microsoftLogin(code);
      console.log('Microsoft OAuth login successful, user:', loggedInUser);
      setUser(loggedInUser);
    } catch (error) {
      console.error('Microsoft OAuth login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Get Microsoft OAuth URL
   * Returns the URL for Microsoft OAuth authorization
   */
  const getMicrosoftOAuthUrl = async () => {
    try {
      return await authService.getMicrosoftOAuthUrl();
    } catch (error) {
      console.error('Failed to get Microsoft OAuth URL:', error);
      throw error;
    }
  };

  /**
   * Check if user exists in database
   * Checks if a user exists without requiring authentication
   */
  const checkUserExists = async (email: string) => {
    try {
      return await authService.checkUserExists(email);
    } catch (error) {
      console.error('Failed to check user existence:', error);
      return false;
    }
  };

  // Create context value object with all authentication functionality
  const value: AuthContextType = {
    user,              // Current user object or null
    login,             // Login function
    logout,            // Logout function
    microsoftLogin,    // Microsoft OAuth login function
    getMicrosoftOAuthUrl, // Get Microsoft OAuth URL function
    checkUserExists,   // Check user existence function
    isLoading,         // Loading state for UI feedback
    isAuthenticated,   // Boolean indicating if user is logged in
  };

  // Provide context value to all child components
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * useAuth Hook
 * 
 * Custom hook for accessing authentication context in components.
 * Provides error handling to ensure hook is used within AuthProvider.
 * 
 * @returns AuthContextType containing user state and authentication methods
 * @throws Error if used outside of AuthProvider
 */
export function useAuth() {
  const context = useContext(AuthContext);
  
  // Ensure hook is used within provider - prevents runtime errors
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}
