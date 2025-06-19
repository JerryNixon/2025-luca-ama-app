# Backend - Luca AMA App

Django REST Framework API for the AMA (Ask Me Anything) system.

## (Coming Soon)

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

# API will be available at http://localhost:8000
```

## 📁 Planned Structure

```
backend/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── luca_ama/             # Main Django project
│   ├── __init__.py
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── apps/                 # Django applications
│   ├── authentication/   # User auth and roles
│   ├── events/           # Event management
│   ├── questions/        # Question and voting system
│   └── analytics/        # Power BI integration
└── tests/                # Test files
```

## 🛠️ Technology Stack

- **Framework**: Django + Django REST Framework
- **Database**: Microsoft Fabric SQL Database
- **Authentication**: JWT + Microsoft OAuth
- **AI**: Azure OpenAI Service
- **Analytics**: Power BI integration
- **Testing**: Django TestCase + pytest

## 📋 API Endpoints (Planned)

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/me/` - Current user info
- `POST /api/auth/microsoft/` - Microsoft OAuth

### Events
- `GET /api/events/` - List events
- `POST /api/events/` - Create event
- `GET /api/events/{id}/` - Event details
- `PUT /api/events/{id}/` - Update event
- `DELETE /api/events/{id}/` - Delete event
- `POST /api/events/{id}/share/` - Generate share link

### Questions
- `GET /api/events/{id}/questions/` - List questions
- `POST /api/events/{id}/questions/` - Create question
- `PUT /api/questions/{id}/` - Update question
- `DELETE /api/questions/{id}/` - Delete question
- `POST /api/questions/{id}/upvote/` - Upvote question
- `DELETE /api/questions/{id}/upvote/` - Remove upvote

## 🔗 Frontend Integration

The backend API is designed to match the frontend service interfaces:

```typescript
// Frontend service calls will map directly to Django endpoints
eventService.getEvents() → GET /api/events/
questionService.upvoteQuestion(id) → POST /api/questions/{id}/upvote/
```

## 🗄️ Database Schema

### User Model
- Microsoft tenant integration
- Role-based permissions (user, presenter, moderator)

### Event Model
- Event metadata and scheduling
- Share link generation
- Participant tracking

### Question Model
- Question content and metadata
- Anonymous option support
- Presenter notes field

### Vote Model
- User-question voting relationships
- Upvote tracking and validation

## 🔮 AI Integration (Optional)

- **Question Similarity**: Detect duplicate questions
- **Content Moderation**: Flag inappropriate content
- **Summarization**: Generate question themes
- **Analytics**: Participation insights

## 📊 Analytics Integration

- Power BI dashboard connectivity
- Participation metrics
- Question theme analysis
- Event success tracking

## 🧪 Development Phases

### Phase 1: Core API (Week 6)
- User authentication
- Basic CRUD operations
- Database setup

### Phase 2: Advanced Features (Week 7)
- Real-time updates
- Question management
- Share link functionality

### Phase 3: AI & Analytics (Week 8)
- Azure OpenAI integration
- Power BI connectivity
- Advanced analytics

## 🔒 Security Features

- JWT token authentication
- Microsoft tenant validation
- Role-based access control
- CORS configuration for frontend
- Rate limiting and throttling

## 📝 Development Notes

This backend structure is designed to:
- Match the frontend TypeScript interfaces
- Support all user stories and workflows
- Scale for enterprise usage
- Integrate with Microsoft ecosystem
- Provide real-time capabilities
