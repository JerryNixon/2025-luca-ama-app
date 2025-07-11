# Event Share Link System Documentation

## Overview

The Event Share Link system allows event creators to generate secure, shareable links that enable both new users and existing users to easily join AMA events. The system seamlessly integrates with the existing authentication and event access flow.

## Features

### Backend Features

1. **Automatic Share Link Generation**
   - Share links are automatically generated when events are created
   - Uses cryptographically secure random strings (32 characters)
   - Links are stored in the `share_link` field of the Event model

2. **Smart Join Endpoint** (`/api/join/{share_link}/`)
   - **GET**: Returns event information for the join page
   - **POST**: Handles user authentication and event joining
   - Supports both new user registration and existing user login
   - Automatically adds users to the event as participants

3. **Event Validation**
   - Validates that events are active (not expired)
   - Checks for valid share links
   - Proper error handling for invalid/expired links

4. **User Flow Support**
   - **Authenticated users**: Automatically adds them to the event
   - **New users**: Registration + automatic event joining
   - **Existing users**: Login + automatic event joining

### Frontend Features

1. **Enhanced Event Creation**
   - Displays share link immediately after event creation
   - Copy-to-clipboard functionality with toast notifications
   - No auto-redirect to allow users to copy the share link

2. **Share Button in Event Details**
   - Copy share link button in event header
   - Toast notifications for successful copy operations
   - Only visible to event creators and moderators

3. **Smart Join Page** (`/join/[shareLink]`)
   - Displays event information
   - Dynamic login/registration form
   - Detects user authentication status
   - Seamless redirect to event after successful join

4. **Toast Notification System**
   - Success, error, warning, and info notifications
   - Auto-dismissing with configurable duration
   - Integrated throughout the application

## API Endpoints

### Join Event via Share Link
```
GET/POST /api/join/{share_link}/
```

**GET Response:**
```json
{
  "success": true,
  "data": {
    "event": {
      "id": "event-uuid",
      "name": "Event Name",
      "created_by": "Creator Name"
    },
    "share_link": "share-link-string"
  }
}
```

**POST Request (Registration):**
```json
{
  "action": "register",
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}
```

**POST Request (Login):**
```json
{
  "action": "login",
  "email": "user@example.com",
  "password": "password123"
}
```

**POST Response:**
```json
{
  "success": true,
  "data": {
    "user": { /* User object */ },
    "token": "jwt-token",
    "refresh": "refresh-token",
    "event": { /* Event object */ }
  },
  "message": "Successfully joined Event Name",
  "redirect_url": "/events/event-uuid"
}
```

## Error Handling

### Backend Errors
- **404**: Invalid or non-existent share link
- **410**: Event is no longer active (expired)
- **400**: Missing required fields or invalid action
- **401**: Invalid login credentials

### Frontend Error Handling
- Invalid share links redirect to 404 page
- Authentication errors display user-friendly messages
- Copy failures show fallback instructions
- Network errors are handled gracefully

## Security Considerations

1. **Secure Link Generation**
   - Uses `secrets.token_urlsafe()` for cryptographically secure randomness
   - 32-character links provide sufficient entropy against brute force

2. **Event Access Control**
   - Share links only grant participant-level access
   - Event creators maintain full control over their events
   - Links can be regenerated if compromised

3. **Authentication Integration**
   - Follows existing authentication patterns
   - JWT tokens are properly generated and validated
   - User sessions are managed consistently

## Usage Examples

### Creating an Event with Share Link
1. User creates an event through `/events/create`
2. System automatically generates a share link
3. Share link is displayed with copy functionality
4. User can share the link with participants

### Joining via Share Link (New User)
1. User clicks share link: `https://app.com/join/abc123...`
2. System displays event info and registration form
3. User fills out registration details
4. System creates account, logs in user, and adds to event
5. User is redirected to event page

### Joining via Share Link (Existing User)
1. User clicks share link
2. System detects user needs to log in
3. User enters login credentials
4. System authenticates user and adds to event
5. User is redirected to event page

## File Structure

### Backend Files
- `backend/api/models.py` - Event model with share link methods
- `backend/api/views.py` - Join endpoint implementation
- `backend/api/serializers.py` - Event serializer with share_url
- `backend/api/urls.py` - URL routing for join endpoint

### Frontend Files
- `frontend/src/app/join/[shareLink]/page.tsx` - Join page component
- `frontend/src/app/events/create/page.tsx` - Enhanced event creation
- `frontend/src/app/events/[id]/page.tsx` - Share button in event details
- `frontend/src/components/ui/Toast.tsx` - Toast notification system
- `frontend/src/app/layout.tsx` - ToastProvider integration
- `frontend/src/types/index.ts` - Event type with share_url

## Testing

### Manual Testing Scenarios
1. **Event Creation**: Verify share link generation and display
2. **Share Link Copy**: Test copy functionality and toast notifications
3. **New User Join**: Test complete registration and event joining flow
4. **Existing User Join**: Test login and event joining flow
5. **Invalid Links**: Test error handling for bad/expired links
6. **Permissions**: Verify share button visibility and access control

### Edge Cases Covered
- Expired events
- Invalid share links
- Duplicate email registration attempts
- Network failures during join process
- Already joined users clicking share links
- Copy functionality in different browsers

## Future Enhancements

1. **Link Expiration**: Add configurable expiration dates for share links
2. **Usage Analytics**: Track link usage and join metrics
3. **Custom Links**: Allow custom share link slugs
4. **QR Codes**: Generate QR codes for share links
5. **Bulk Invites**: Send share links via email to multiple users
6. **Link Management**: Regenerate or disable share links
