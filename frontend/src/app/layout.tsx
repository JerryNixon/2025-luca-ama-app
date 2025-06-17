// Root layout component for the Luca AMA App
// This is the top-level layout that wraps all pages in the Next.js 13+ app directory structure

// Import global CSS styles that apply to the entire application
import './globals.css'
// Import Next.js metadata type for proper TypeScript typing
import type { Metadata } from 'next'
// Import Google Fonts Inter for consistent typography throughout the app
import { Inter } from 'next/font/google'
// Import the authentication context provider to manage user state globally
import { AuthProvider } from '@/contexts/AuthContext'

// Configure the Inter font with Latin character subset for optimal loading
// This ensures the font is preloaded and optimized for better performance
const inter = Inter({ subsets: ['latin'] })

// Define metadata for the application that appears in browser tabs and search results
// This is used by Next.js for SEO optimization and social media sharing
export const metadata: Metadata = {
  title: 'Luca AMA App',
  description: 'Ask Me Anything application for Microsoft events',
}

/**
 * RootLayout Component
 * 
 * This is the root layout component that wraps all pages in the application.
 * It provides:
 * - Global HTML structure (html and body tags)
 * - Font configuration using Google Fonts
 * - Authentication context for the entire app
 * - Global CSS styling
 * 
 * @param children - React components that will be rendered inside this layout
 * @returns JSX element representing the root HTML structure
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    // Set the document language to English for accessibility and SEO
    <html lang="en">
      <body className={inter.className}>
        {/* 
          Wrap the entire application with AuthProvider to:
          - Provide authentication state to all components
          - Handle login/logout functionality globally
          - Manage user session persistence
        */}
        <AuthProvider>
          {/* 
            children represents all the page content that will be rendered
            This could be the home page, events page, login page, etc.
          */}
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
