# API Specification - Luca AMA App

RESTful API documentation for the AMA system backend.

## 🔗 Base URL
- **Development**: `http://localhost:8000/api`
- **Production**: `https://your-domain.com/api`

## 🔐 Authentication

### JWT Token Authentication
All API requests (except login) require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Login Flow
1. POST credentials to `/auth/login/`
2. Receive JWT token in response
3. Include token in subsequent requests
4. Token expires after 24 hours (configurable)

## 📋 API Endpoints

### Authentication Endpoints

#### POST /auth/login/
Login with email and password.

**Request:**
```json
{
  "email": "user@microsoft.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@microsoft.com", 
      "name": "John Doe",
      "role": "user"
    },
    "token": "jwt-token-string"
  }
}
```

#### POST /auth/logout/
Logout current user.

#### GET /auth/me/
Get current user information.

#### POST /auth/microsoft/
Microsoft OAuth login.

### Event Endpoints

#### GET /events/
List all events for the current user.

**Query Parameters:**
- `status`: Filter by status (active, closed, upcoming)
- `role`: Filter by user role in event

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Town Hall Q&A",
      "openDate": "2025-06-20T10:00:00Z",
      "closeDate": "2025-06-20T11:00:00Z",
      "createdBy": "uuid",
      "moderators": ["uuid1", "uuid2"],
      "participants": ["uuid3", "uuid4"],
      "shareLink": "https://ama.app/join/abc123",
      "isActive": true,
      "createdAt": "2025-06-17T09:00:00Z",
      "updatedAt": "2025-06-17T09:00:00Z"
    }
  ]
}
```

#### POST /events/
Create a new event.

**Request:**
```json
{
  "name": "New AMA Session",
  "openDate": "2025-06-25T14:00:00Z",
  "closeDate": "2025-06-25T15:00:00Z"
}
```

#### GET /events/{id}/
Get event details.

#### PUT /events/{id}/
Update event (moderator/presenter only).

#### DELETE /events/{id}/
Delete event (moderator only).

#### POST /events/{id}/share/
Generate or refresh share link.

#### POST /events/join/{token}/
Join event via share token.

### Question Endpoints

#### GET /events/{eventId}/questions/
List questions for an event.

**Query Parameters:**
- `keyword`: Search in question text
- `author`: Filter by author
- `answered`: Filter by answered status (true/false)
- `starred`: Filter by starred status (true/false)  
- `sort_by`: Sort by (votes, date, author)
- `sort_order`: Sort order (asc, desc)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "eventId": "uuid",
      "text": "What's the roadmap for next quarter?",
      "author": {
        "id": "uuid",
        "name": "Jane Smith",
        "email": "jane@microsoft.com",
        "role": "user"
      },
      "isAnonymous": false,
      "upvotes": 15,
      "hasUserUpvoted": false,
      "isAnswered": false,
      "isStarred": true,
      "isStaged": false,
      "presenterNotes": "Good strategic question",
      "aiSummary": "Question about future planning",
      "parentQuestionId": null,
      "groupedQuestions": [],
      "tags": ["strategy", "planning"],
      "createdAt": "2025-06-17T10:30:00Z",
      "updatedAt": "2025-06-17T10:30:00Z"
    }
  ]
}
```

#### POST /events/{eventId}/questions/
Create a new question.

**Request:**
```json
{
  "text": "How will AI impact our development process?",
  "isAnonymous": false,
  "tags": ["ai", "development"]
}
```

#### GET /questions/{id}/
Get question details.

#### PUT /questions/{id}/
Update question (owner only, unless moderator/presenter).

#### DELETE /questions/{id}/
Delete question (owner only, unless moderator).

#### POST /questions/{id}/upvote/
Upvote a question.

#### DELETE /questions/{id}/upvote/
Remove upvote from question.

#### POST /questions/{id}/ai-summary/
Generate AI summary for question (moderator/presenter only).

### Bulk Operations

#### PATCH /questions/bulk/
Bulk update questions (moderator/presenter only).

**Request:**
```json
{
  "questions": [
    {
      "id": "uuid1",
      "isAnswered": true
    },
    {
      "id": "uuid2", 
      "isStarred": true
    }
  ]
}
```

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Optional success message"
}
```

### Error Response  
```json
{
  "success": false,
  "error": "Error message",
  "details": {...}
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "totalCount": 150,
    "page": 1,
    "pageSize": 20,
    "totalPages": 8
  }
}
```

## 🔒 Permissions

### Role-Based Access Control

#### User
- Can view events they're invited to
- Can create/edit/delete own questions
- Can upvote questions (not own)
- Can join events via share link

#### Presenter  
- All User permissions
- Can view/edit presenter notes
- Can mark questions as answered
- Can star/unstar questions
- Can stage/unstage questions

#### Moderator
- All Presenter permissions
- Can create/edit/delete events
- Can manage event participants
- Can moderate any question
- Can generate share links

## 🚨 Rate Limiting

- **Authentication**: 5 requests per minute
- **General API**: 100 requests per minute
- **Question Creation**: 10 requests per minute
- **Upvoting**: 30 requests per minute

## 📈 Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized  
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

## 🔄 Real-time Updates

WebSocket connections available at:
- `ws://localhost:8000/ws/events/{eventId}/`

Events pushed:
- New questions
- Question updates (votes, answers, staging)
- User joins/leaves
