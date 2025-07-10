# Luca AMA App

Ask Me Anything (AMA) sessions during Microsoft events.

## 📁 Project Structure

```
luca-ama-app/
├── frontend/              # Next.js React application
│   ├── src/              # Source code
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # Reusable UI components
│   │   ├── contexts/     # React contexts
│   │   ├── services/     # API service layer
│   │   ├── types/        # TypeScript definitions
│   │   ├── lib/          # Utilities and config
│   │   └── styles/       # Global styles
│   ├── package.json      # Frontend dependencies
│   ├── next.config.js    # Next.js configuration
│   ├── tailwind.config.js # Tailwind CSS config
│   ├── tsconfig.json     # TypeScript config
│   └── README.md         # Frontend documentation
├── backend/              # Django REST API
│   ├── ama_backend/      # Django project configuration
│   ├── api/              # Main application (models, views, URLs)
│   ├── scripts/          # Database utility scripts
│   ├── tests/            # Backend-specific tests
│   ├── management/       # Database management scripts
│   ├── config/           # Configuration files and certificates
│   ├── docs/             # Backend documentation
│   ├── manage.py         # Django management script
│   ├── requirements.txt  # Python dependencies
│   └── README.md         # Backend documentation
├── tools/                # Development and testing tools
│   ├── tests/            # Comprehensive test scripts
│   ├── debug/            # Debugging utilities
│   ├── utils/            # Utility scripts and status checks
│   ├── jerry_auth_test.html # Authentication test interface
│   ├── test_frontend_auth.html # Frontend auth test
│   └── README.md         # Tools documentation
├── scripts/              # PowerShell startup scripts
│   ├── start-app.ps1     # Start both frontend and backend
│   ├── start-app-fixed.ps1 # Fixed startup script
│   ├── start-backend.ps1 # Start backend only
│   └── start-frontend.ps1 # Start frontend only
├── docs/                 # Project documentation
│   ├── guides/           # Development and usage guides
│   ├── features/         # Feature documentation
│   ├── fixes/            # Bug fixes and solutions
│   ├── project/          # Project status and organization
│   ├── API_SPEC.md       # API documentation
│   ├── USER_STORIES.md   # Persona requirements
│   ├── FRONTEND_SUMMARY.md # Frontend architecture
│   └── README.md         # Documentation index
├── .vscode/              # VS Code workspace settings
├── .git/                 # Git repository
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── LICENSE              # Project license
```


### Frontend Development
```bash
cd frontend
npm install
npm run dev
# Opens http://localhost:3000
```

**Demo Login:**
- Email: `demo@microsoft.com`
- Password: `demo123`

### Backend Development (Coming Soon)
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
# Will serve http://localhost:8000
```

## 🎯 Project Overview

This application helps with Q&A workflows during Microsoft all-hands, town halls, or team-wide events. Users can post questions, upvote others, and see what's being addressed live. Admins can mark questions as answered and export them to reports.

### Technology Stack

**Frontend:**
- Next.js 14 with React 18 and TypeScript
- Tailwind CSS for styling
- React Context for state management
- Axios for API communication

**Backend (Planned):**
- Django REST Framework
- Microsoft Fabric SQL Database
- Azure OpenAI for AI features
- Power BI for analytics

**DevOps:**
- GitHub for version control
- VS Code Dev Containers
- Github action

## Personnas Roles & Features

### 🔧 Moderator
- Full event management (create, edit, delete)
- Question curation and organization
- Generate share links for events
- Presenter notes management

### 🎤 Presenter
- View and manage event questions
- Mark questions as answered
- Add presenter notes
- Stage questions for discussion

### 👤 User
- Join events via shared links
- Submit questions (anonymous option)
- Upvote interesting questions
- View live Q&A sessions

## 📋 Development Timeline

- **Weeks 1-2**: Project planning and setup ✅
- **Weeks 3-5**: Frontend development ✅
- **Weeks 6-7**: Backend & API layer 🚧
- **Week 8**: Analytics layer (Power BI integration)
- **Week 9**: Deployment & polish
- **Week 10**: Final Connect + Presentation

## 🛠️ Development Commands

```bash
# Frontend
cd frontend
npm run dev        # Development server
npm run build      # Production build
npm run lint       # Code linting

# Backend (when ready)
cd backend
python manage.py runserver    # Development server
python manage.py migrate      # Database migrations
python manage.py test         # Run tests
```

## 📚 Documentation

- [`docs/FRONTEND_SUMMARY.md`](./docs/FRONTEND_SUMMARY.md) - Complete frontend overview
- [`frontend/README.md`](./frontend/README.md) - Frontend-specific documentation
- User stories and flowcharts - See project attachments