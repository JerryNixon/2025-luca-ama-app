// Tailwind CSS Configuration - Styling framework configuration
// This file defines the design system, color palette, and component scanning

/** @type {import('tailwindcss').Config} */
module.exports = {
  // Content paths where Tailwind should look for class names
  // This enables tree-shaking to only include used CSS classes
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',      // Next.js pages directory
    './src/components/**/*.{js,ts,jsx,tsx,mdx}', // React components
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',        // Next.js 13+ app directory
  ],
  
  // Theme configuration and customizations
  theme: {
    extend: {
      // Custom color palette for the AMA application
      colors: {        // Primary color scheme - blue tones for main actions and branding
        primary: {
          50: '#eff6ff',    // Very light blue for backgrounds
          100: '#dbeafe',   // Light blue for hover states
          200: '#bfdbfe',   // Slightly darker blue
          500: '#3b82f6',   // Standard blue for normal states
          600: '#2563eb',   // Darker blue for primary buttons
          700: '#1d4ed8',   // Darkest blue for hover states
        },// Secondary color scheme - gray tones for subtle elements
        secondary: {
          50: '#f8fafc',    // Very light gray for backgrounds
          100: '#f1f5f9',   // Light gray for secondary buttons
          200: '#e2e8f0',   // Slightly darker gray for hover states
          500: '#64748b',   // Medium gray for text
          600: '#475569',   // Darker gray for emphasis
          700: '#334155',   // Darkest gray for headings
        }
      },
    },
  },
  
  // Tailwind plugins for additional functionality
  plugins: [],
}
