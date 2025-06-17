# Development Guide - Luca AMA App

Complete guide for developing and extending the AMA application.

## 🚀 Getting Started

### Prerequisites
- **Node.js 18+** for frontend development
- **Python 3.9+** for backend development  
- **Git** for version control
- **VS Code** (recommended) with extensions:
  - TypeScript and JavaScript Language Features
  - Tailwind CSS IntelliSense
  - Python extension
  - Django extension

### Project Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd luca-ama-app
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

3. **Backend Setup** (when ready)
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

## 📁 Project Organization

```
luca-ama-app/
├── frontend/              # Next.js React application
│   ├── src/              # All source code
│   ├── package.json      # Dependencies and scripts
│   └── README.md         # Frontend documentation
├── backend/              # Django REST API
│   ├── apps/             # Django applications
│   ├── requirements.txt  # Python dependencies
│   └── README.md         # Backend documentation
├── docs/                 # Project documentation
│   ├── API_SPEC.md       # API documentation
│   ├── USER_STORIES.md   # Requirements and personas
│   └── DEVELOPMENT.md    # This file
├── .git/                 # Git repository
├── .gitignore           # Git ignore rules
├── README.md            # Main project README
└── LICENSE              # Project license
```

## 🎯 Development Workflow

### Week-by-Week Plan

#### Weeks 3-5: Frontend Development ✅
- [x] Project setup and structure
- [x] User authentication system
- [x] Event management UI
- [x] Question display and interaction
- [x] Role-based permissions
- [x] Demo data integration

#### Weeks 6-7: Backend Development 🚧
- [ ] Django project setup
- [ ] Database models and migrations
- [ ] Authentication endpoints
- [ ] Event CRUD operations
- [ ] Question management APIs
- [ ] Real-time WebSocket integration

#### Week 8: Advanced Features
- [ ] Azure OpenAI integration
- [ ] Question similarity detection
- [ ] Power BI analytics setup
- [ ] Performance optimization

#### Week 9: Integration & Polish
- [ ] Frontend-backend integration testing
- [ ] UI/UX improvements
- [ ] Error handling and validation
- [ ] Documentation updates

#### Week 10: Deployment & Presentation
- [ ] Azure deployment
- [ ] Performance testing
- [ ] Final presentation prep
- [ ] Demo environment setup

## 🛠️ Development Standards

### Frontend Standards

#### File Organization
```
src/
├── app/                  # Next.js pages
├── components/           # Reusable components
│   ├── ui/              # Generic UI components
│   ├── events/          # Event-specific components
│   └── questions/       # Question-specific components
├── contexts/            # React contexts
├── services/            # API service layer
├── types/               # TypeScript definitions
├── lib/                 # Utilities and configurations
└── styles/              # Global styles
```

#### Naming Conventions
- **Components**: PascalCase (`EventCard.tsx`)
- **Files/Folders**: camelCase (`authService.ts`)
- **CSS Classes**: kebab-case (`btn-primary`)
- **Constants**: UPPER_SNAKE_CASE (`USE_DEMO_DATA`)

#### TypeScript Guidelines
- Always use TypeScript for new files
- Define interfaces for all data structures
- Use strict type checking
- Export types from `types/index.ts`

#### Component Guidelines
```typescript
// Good component structure
interface ComponentProps {
  prop1: string;
  prop2?: number;
  onAction: () => void;
}

export default function Component({ prop1, prop2, onAction }: ComponentProps) {
  // Component logic
  return <div>Component JSX</div>;
}
```

### Backend Standards

#### Django App Organization
```
backend/
├── apps/
│   ├── authentication/   # User management
│   ├── events/          # Event models and views
│   ├── questions/       # Question and vote models
│   └── analytics/       # Reporting and analytics
```

#### API Response Format
```python
# Consistent API response format
{
    "success": True,
    "data": {...},
    "message": "Optional message"
}

# Error response format
{
    "success": False,
    "error": "Error message",
    "details": {...}
}
```

#### Model Guidelines
- Use UUIDs for primary keys
- Include created_at/updated_at timestamps
- Add proper string representations
- Use model managers for complex queries

## 🔧 Development Tools

### VS Code Configuration

Create `.vscode/settings.json`:
```json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.defaultInterpreterPath": "./backend/venv/bin/python"
}
```

### Git Workflow

1. **Feature Branches**
```bash
git checkout -b feature/event-creation
# Make changes
git add .
git commit -m "Add event creation form"
git push origin feature/event-creation
```

2. **Commit Messages**
- Use present tense: "Add feature" not "Added feature"
- Be descriptive but concise
- Reference issues: "Fix login bug (#123)"

### Testing Strategy

#### Frontend Testing
```bash
# Component testing with Jest
npm test

# E2E testing with Playwright (planned)
npm run test:e2e
```

#### Backend Testing
```bash
# Unit tests
python manage.py test

# API testing
pytest tests/
```

## 🔄 Switching Between Demo and Real Data

The frontend is designed to easily switch between demo data and real API:

**In `AuthContext.tsx` and event pages:**
```typescript
// Change this flag to switch data sources
const USE_DEMO_DATA = true; // false for real API
```

**Demo Data Benefits:**
- Immediate development and testing
- No backend dependency
- Realistic data structure
- Easy to modify for different scenarios

**Real API Benefits:**
- Actual backend integration
- Real-time updates
- Production-ready flow
- Database persistence

## 🧪 Testing Scenarios

### User Role Testing
1. **Moderator Flow**
   - Create event
   - Generate share link  
   - Manage questions
   - Star and stage questions

2. **Presenter Flow**
   - Join event
   - View questions with notes
   - Mark as answered
   - Stage questions

3. **User Flow**
   - Join via share link
   - Submit questions
   - Upvote questions
   - View answers

### Error Scenarios
- Invalid login credentials
- Network connectivity issues
- Permission denied actions
- Form validation errors

## 📊 Performance Considerations

### Frontend Optimization
- Lazy loading for large component trees
- Memoization for expensive calculations
- Optimized re-renders with React.memo
- Code splitting for route-based chunks

### Backend Optimization
- Database query optimization
- Caching for frequently accessed data
- Pagination for large datasets
- Background tasks for heavy operations

## 🔒 Security Guidelines

### Frontend Security
- Never store sensitive data in localStorage
- Validate all user inputs
- Use HTTPS in production
- Implement proper error boundaries

### Backend Security
- JWT token expiration
- Rate limiting on API endpoints
- SQL injection prevention
- CORS configuration
- Input validation and sanitization

## 📚 Resources & References

### Frontend Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [React Best Practices](https://react.dev)

### Backend Resources
- [Django Documentation](https://docs.djangoproject.com)
- [Django REST Framework](https://www.django-rest-framework.org)
- [Microsoft Fabric](https://docs.microsoft.com/fabric)
- [Azure OpenAI](https://docs.microsoft.com/azure/openai)

### Development Tools
- [VS Code Extensions](https://code.visualstudio.com)
- [Postman for API Testing](https://postman.com)
- [Git Best Practices](https://git-scm.com/docs)

## 🆘 Troubleshooting

### Common Frontend Issues
1. **TypeScript errors**: Check type definitions
2. **Import errors**: Verify file paths and exports
3. **CSS not applying**: Check Tailwind configuration
4. **API errors**: Verify backend connectivity

### Common Backend Issues
1. **Database connection**: Check connection strings
2. **Migration errors**: Reset and rerun migrations
3. **Import errors**: Check Python path and virtual environment
4. **Authentication issues**: Verify JWT configuration

### Getting Help
1. Check this documentation first
2. Search existing GitHub issues
3. Review API specification
4. Ask team members for guidance
5. Create detailed issue reports with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Error messages and logs
