// Next.js Configuration - Settings for the Next.js application
// This file configures routing, API proxying, and environment variables

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Environment variables available to the application
  env: {
    CUSTOM_KEY: 'my-value',    // Example custom environment variable
  },
  
  /**
   * URL Rewrites Configuration
   * 
   * Proxies API requests to the Django backend during development.
   * This allows the frontend to make requests to /api/* which get
   * automatically forwarded to the Django server on localhost:8000.
   * 
   * Benefits:
   * - Avoids CORS issues during development
   * - Provides clean API URLs for the frontend
   * - Makes it easy to switch between dev and production backends
   */
  async rewrites() {
    return [
      {
        source: '/api/:path*',                                // Frontend API path pattern
        destination: 'http://localhost:8000/api/:path*',     // Django backend URL
      },
    ]
  },
}

// Export configuration for Next.js to use
module.exports = nextConfig
