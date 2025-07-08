// Authentication Service - API service layer for user authentication operations
// This service handles all authentication-related API calls and token management

// Import the configured API client for making HTTP requests
import apiClient from '@/lib/api';
// Import TypeScript types for type safety and clear interfaces
import { User, LoginForm, ApiResponse } from '@/types';
// Import cookie utilities for secure token storage
import Cookies from 'js-cookie';

/**
 * Authentication Service Object
 * 
 * Provides methods for all authentication operations including:
 * - User login with email/password
 * - User logout and session cleanup
 * - Current user information retrieval
 * - Token refresh functionality
 * - Microsoft OAuth integration for tenant validation
 * 
 * All methods return promises and handle API communication with proper error handling.
 */
export const authService = {
  
  /**
   * Login User
   * 
   * Authenticates a user with email and password credentials.
   * On successful login, stores the authentication token in a secure cookie.
   * 
   * @param credentials - User login credentials containing email and password
   * @returns Promise resolving to user object and authentication token
   * @throws Error if authentication fails (invalid credentials, network issues, etc.)
   */
  async login(credentials: LoginForm): Promise<{ user: User; token: string }> {
    console.log('AuthService: Attempting login for', credentials.email);
    // Make POST request to login endpoint with user credentials
    const response = await apiClient.post<ApiResponse<{ user: User; token: string }>>('/auth/login/', credentials);
    
    console.log('AuthService: Login response status', response.status);
    console.log('AuthService: Login response data', response.data);
    
    // Extract user and token from API response
    const { user, token } = response.data.data;
    console.log('AuthService: Setting cookie with token');
    // Store authentication token in secure HTTP-only cookie
    // Cookie expires in 7 days and is automatically sent with future requests
    Cookies.set('access_token', token, { expires: 7 });
    
    console.log('AuthService: Cookie set, returning user and token');
    return { user, token };
  },

  /**
   * Logout User
   * 
   * Logs out the current user by invalidating their session on the server
   * and removing the authentication token from client storage.
   * Always cleans up local token, even if server request fails.
   * 
   * @returns Promise that resolves when logout is complete
   */
  async logout(): Promise<void> {
    try {
      // Notify server to invalidate the user's session
      // This ensures the token can't be used elsewhere
      await apiClient.post('/auth/logout/');
    } catch (error) {
      // Log error but don't prevent local cleanup
      // User should still be logged out locally even if server is unreachable
      console.error('Logout error:', error);
    } finally {      // Always remove token from client, regardless of server response
      // This ensures user appears logged out in the UI
      Cookies.remove('access_token');
    }
  },

  /**
   * Get Current User
   * 
   * Retrieves the current user's information from the server.
   * Uses the authentication token stored in cookies for authorization.
   * 
   * @returns Promise resolving to current user object
   * @throws Error if token is invalid or user doesn't exist
   */
  async getCurrentUser(): Promise<User> {
    // Request current user data from server
    // API client automatically includes authentication token from cookies
    const response = await apiClient.get<ApiResponse<User>>('/auth/me/');
    return response.data.data;
  },

  /**
   * Refresh Authentication Token
   * 
   * Exchanges the current token for a new one to extend the user's session.
   * This is typically called automatically when the current token is near expiration.
   * 
   * @returns Promise resolving to new authentication token
   * @throws Error if current token is invalid or expired
   */
  async refreshToken(): Promise<string> {
    // Request new token from server using current token
    const response = await apiClient.post<ApiResponse<{ token: string }>>('/auth/refresh/');
    const { token } = response.data.data;
      // Update stored token with new value and reset expiration
    Cookies.set('access_token', token, { expires: 7 });
    
    return token;
  },

  /**
   * Microsoft OAuth Login
   * 
   * Completes the OAuth flow with Microsoft for tenant validation.
   * This method is called after the user has been redirected back from Microsoft
   * with an authorization code.
   * 
   * @param code - Authorization code received from Microsoft OAuth redirect
   * @returns Promise resolving to user object and authentication token
   * @throws Error if OAuth code is invalid or Microsoft authentication fails
   */
  async microsoftLogin(code: string): Promise<{ user: User; token: string }> {
    // Exchange OAuth code for user information and authentication token
    const response = await apiClient.post<ApiResponse<{ user: User; token: string }>>('/auth/microsoft/', { code });
    const { user, token } = response.data.data;
    // Store authentication token for authenticated sessions
    Cookies.set('access_token', token, { expires: 7 });
    
    return { user, token };
  },

  /**
   * Get Microsoft OAuth URL
   * 
   * Retrieves the Microsoft OAuth authorization URL for redirecting users
   * to Microsoft's login page.
   * 
   * @returns Promise resolving to OAuth authorization URL
   */
  async getMicrosoftOAuthUrl(): Promise<string> {
    const response = await apiClient.get<ApiResponse<{ auth_url: string }>>('/auth/microsoft/url/');
    return response.data.data.auth_url;
  },

  /**
   * Check if user exists in database
   * 
   * Checks if a user with the given email exists in the database
   * without requiring authentication.
   * 
   * @param email - User's email address
   * @returns Promise resolving to boolean indicating if user exists
   */
  async checkUserExists(email: string): Promise<boolean> {
    try {
      const response = await apiClient.post<ApiResponse<{ exists: boolean }>>('/auth/check-user/', { email });
      return response.data.data.exists;
    } catch (error) {
      console.error('Error checking user existence:', error);
      return false;
    }
  },
};
