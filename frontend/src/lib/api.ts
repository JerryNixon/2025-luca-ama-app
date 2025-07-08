// API Client Configuration - Centralized HTTP client with authentication and error handling
// This module configures Axios for all API communication with automatic token management

// Import Axios HTTP client library
import axios from 'axios';
// Import cookie utility for retrieving authentication tokens
import Cookies from 'js-cookie';

/**
 * API Client Instance
 * 
 * Pre-configured Axios instance with:
 * - Base URL pointing to the backend API
 * - Request timeout configuration
 * - Default headers for JSON communication
 * - Automatic authentication token injection
 * - Centralized error handling and redirects
 */
const apiClient = axios.create({
  // Base URL for all API requests - points to Django backend
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api',
  
  // Request timeout in milliseconds - increased for database operations
  timeout: 15000,
  
  // Default headers sent with every request
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Enable credentials for authentication
  withCredentials: false,  // Using Authorization header instead
});

/**
 * Request Interceptor
 * 
 * Automatically adds authentication tokens to outgoing requests.
 * This interceptor runs before every request is sent to the server.
 * Retrieves the JWT token from cookies and adds it to the Authorization header.
 */
apiClient.interceptors.request.use(
  (config) => {    // Retrieve authentication token from secure cookie storage
    const token = Cookies.get('access_token');
    
    // Add Authorization header with Bearer token if available
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Return modified config to continue with the request
    return config;
  },
  (error) => {
    // Handle any errors that occur during request setup
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * 
 * Handles common response scenarios and errors globally.
 * This interceptor runs after every response is received from the server.
 * Provides centralized error handling, especially for authentication failures.
 */
apiClient.interceptors.response.use(
  (response) => {
    // For successful responses, just return the response unchanged
    return response;
  },
  (error) => {
    // Handle HTTP 401 Unauthorized responses
    if (error.response?.status === 401) {
      // Token is invalid or expired - redirect to login page
      // Check if we're in a browser environment (not during SSR)
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    // Re-throw the error so calling code can handle specific errors
    return Promise.reject(error);
  }
);

// Export the configured API client for use throughout the application
export default apiClient;
