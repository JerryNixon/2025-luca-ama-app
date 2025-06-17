# Luca AMA App

A modern full-stack application for managing Ask Me Anything (AMA) sessions during Microsoft events.

## 📁 Project Structure

```
luca-ama-app/
├── frontend/              # Next.js React application
│   ├── src/              # Source code
│   ├── package.json      # Frontend dependencies
│   └── ...config files   # Next.js, TypeScript, Tailwind
├── backend/              # Django REST API (to be implemented)
│   ├── requirements.txt  # Python dependencies
│   ├── manage.py         # Django management
│   └── apps/             # Django applications
├── docs/                 # Project documentation
│   ├── FRONTEND_SUMMARY.md
│   ├── API_SPEC.md       # API documentation
│   └── USER_STORIES.md   # Persona requirements
├── .git/                 # Git repository
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── LICENSE              # Project license
```

## 🚀 Quick Start

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

This application streamlines Q&A workflows during Microsoft all-hands, town halls, or team-wide events. Users can post questions, upvote others, and see what's being addressed live. Admins can mark questions as answered and export them to reports.

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
- Azure deployment

## 👥 User Roles & Features

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

## 🔗 Key Links

- **Frontend**: http://localhost:3000 (when running)
- **Backend API**: http://localhost:8000 (when implemented)
- **Documentation**: [`docs/`](./docs/)
- **User Stories**: See project attachments and flowcharts

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

## 🤝 Contributing

This is a development project for Microsoft internship. Follow the established patterns for components, services, and types when adding new features.

Current focus: **Frontend complete ✅** → **Backend development next** 🚧