# Frontend - Luca AMA App

A modern Next.js React application for the AMA (Ask Me Anything) system.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

## 🔑 Demo Login
- **Email**: `demo@microsoft.com`
- **Password**: `demo123`

## 📁 Project Structure

```
src/
├── app/                    # Next.js 13+ App Router
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Home page
│   ├── login/
│   │   └── page.tsx       # Authentication page
│   └── events/
│       └── page.tsx       # Events listing page
├── components/            # Reusable UI components
│   ├── events/
│   │   └── EventCard.tsx  # Event display component
│   └── questions/
│       └── QuestionCard.tsx # Question display with actions
├── contexts/
│   └── AuthContext.tsx    # Authentication state management
├── services/              # API service layer (ready for backend)
│   ├── authService.ts     # Authentication API calls
│   ├── eventService.ts    # Event management API calls
│   └── questionService.ts # Question management API calls
├── types/
│   └── index.ts           # TypeScript interfaces
├── lib/
│   ├── api.ts             # Axios configuration
│   └── demoData.ts        # Demo data for development
└── styles/
    └── globals.css        # Tailwind CSS setup
```

## 🎨 Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS for responsive design
- **State**: React Context API for authentication
- **HTTP**: Axios for API communication
- **Icons**: React Icons (Feather icons)
- **Date**: date-fns for date formatting

## 🔧 Development Commands

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run start      # Start production server
npm run lint       # Run ESLint
```

## 👥 User Roles & Features

### 🔧 Moderator
- Create and manage events
- Question curation and moderation
- Generate share links
- Add presenter notes
- Star and stage questions

### 🎤 Presenter
- View and manage questions
- Mark questions as answered
- Add presenter notes
- Stage questions for discussion

### 👤 User
- Join events via shared links
- Submit questions (with anonymous option)
- Upvote questions
- View live discussions

## 🔄 Demo Data vs Real API

The application can switch between demo data and real API:

```typescript
// In AuthContext.tsx and events page
const USE_DEMO_DATA = true; // Change to false for real API
```

When `USE_DEMO_DATA = false`, the app will make real API calls to the Django backend.

## 📋 Component Overview

### EventCard
- Displays event information
- Shows user role and permissions
- Handles click navigation

### QuestionCard
- Shows question details and metadata
- Role-based action buttons
- Upvoting, starring, staging functionality
- Presenter notes (moderator/presenter only)

### AuthContext
- Manages user authentication state
- Handles login/logout
- Provides user role information

## 🛠️ Backend Integration Ready

The frontend is structured for seamless Django backend integration:

### API Service Layer
All API calls are abstracted through services:
- `authService.ts` - Authentication endpoints
- `eventService.ts` - Event CRUD operations
- `questionService.ts` - Question management

### TypeScript Interfaces
Comprehensive types matching expected API responses:
- User, Event, Question interfaces
- API response wrappers
- Form data types

### Configuration
- `next.config.js` includes API proxy to `localhost:8000`
- Axios client with authentication headers
- Error handling and loading states

## 🔗 Navigation Structure

```
/ (Home)
├── /login (Authentication)
├── /events (Event listing)
│   ├── /events/create (Create new event)
│   └── /events/[id] (Event details - to be implemented)
└── /profile (User profile - to be implemented)
```

## 🎯 Next Steps

1. **Backend Integration**: Switch `USE_DEMO_DATA = false`
2. **Event Details Page**: Implement individual event view
3. **Question Management**: Add create/edit question forms
4. **Real-time Updates**: WebSocket integration
5. **Advanced Filtering**: Implement search and filter UI

## 📱 Responsive Design

The application is fully responsive with:
- Mobile-first design approach
- Responsive grid layouts
- Touch-friendly buttons
- Optimized for tablets and phones

## 🔍 Development Notes

- All components use TypeScript for type safety
- Tailwind CSS classes are used consistently
- Error boundaries and loading states are implemented
- Role-based rendering prevents unauthorized access
- Demo data simulates realistic backend responses
