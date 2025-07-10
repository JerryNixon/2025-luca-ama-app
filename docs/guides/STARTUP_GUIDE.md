# AMA Application - Quick Start Guide

## ✅ **Fixed Issues**

### 1. **Backend Startup Issues**
- **Problem**: Virtual environment path was incorrect, causing activation to fail
- **Solution**: Updated `start-backend.ps1` to check multiple possible venv locations
- **Status**: ✅ Fixed

### 2. **Django Migration Error**
- **Problem**: `0004_fix_user_manager` migration had invalid import causing `BadMigrationError`
- **Solution**: Fixed migration file to use string reference instead of direct import
- **Status**: ✅ Fixed

### 3. **Database Authentication**
- **Problem**: Manual password prompts when connecting to Fabric SQL
- **Solution**: Configured `ActiveDirectoryDefault` authentication in Django settings
- **Status**: ✅ Fixed

### 4. **CORS Configuration**
- **Problem**: Frontend couldn't communicate with backend due to CORS restrictions
- **Solution**: Properly configured CORS origins for localhost:3000 and 127.0.0.1:3000
- **Status**: ✅ Fixed

## 🚀 **How to Start the Application**

### Method 1: Using PowerShell Scripts (Recommended)
```powershell
# Start backend (from project root)
.\start-backend.ps1

# Start frontend (from project root) 
.\start-frontend.ps1
```

### Method 2: Using VS Code Tasks
1. Open Command Palette (Ctrl+Shift+P)
2. Run "Tasks: Run Task"
3. Select "Start Django Backend"
4. Select "Start Next.js Frontend"

### Method 3: Manual Start
```powershell
# Backend
cd backend
python manage.py migrate
python manage.py runserver 127.0.0.1:8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 🔗 **Application URLs**

- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000/api/
- **Django Admin**: http://127.0.0.1:8000/admin/

## 🧪 **Testing the Setup**

Run the status check script to verify everything is working:

```powershell
python check_status.py
```

This will test:
- Backend API connectivity
- Frontend accessibility
- Database connection
- CORS configuration

## 🔧 **Configuration Summary**

### Backend Configuration
- **Database**: Microsoft Fabric SQL with ActiveDirectoryDefault authentication
- **API Framework**: Django REST Framework with JWT authentication
- **CORS**: Configured for localhost:3000 and 127.0.0.1:3000
- **Authentication**: Simple JWT with 24-hour access tokens

### Frontend Configuration
- **Framework**: Next.js 14 with TypeScript
- **API Client**: Axios with automatic token management
- **Authentication**: JWT tokens stored in cookies
- **Demo Data**: Disabled (USE_DEMO_DATA = false)

## 📁 **Key Files Modified**

1. **start-backend.ps1** - Fixed virtual environment path detection
2. **backend/api/migrations/0004_fix_user_manager.py** - Fixed migration import
3. **backend/ama_backend/settings.py** - Database and CORS configuration
4. **frontend/src/lib/api.ts** - API client configuration
5. **frontend/src/contexts/AuthContext.tsx** - Real API integration
6. **.vscode/tasks.json** - Added frontend task

## 🎯 **Test Users**

The following test users are available for testing:

| Username | Password | Role |
|----------|----------|------|
| moderator | test123 | Moderator |
| user | test123 | Regular User |
| presenter | test123 | Presenter |

## 📊 **Current Status**

- ✅ Backend connects to Fabric SQL without manual password prompts
- ✅ Django ORM migrations work correctly
- ✅ REST API endpoints are accessible
- ✅ Frontend connects to backend API
- ✅ CORS configuration allows frontend-backend communication
- ✅ JWT authentication is configured
- ✅ Both servers can be started with simple scripts

## 🔄 **What's Next**

1. **Test the full user flow**:
   - Login with test users
   - Create events
   - Submit questions
   - Vote on questions

2. **Verify data persistence**:
   - Check that all actions are saved to Fabric SQL
   - Test event sharing links
   - Verify question management

3. **Production hardening**:
   - Add input validation
   - Implement rate limiting
   - Add proper error handling
   - Security headers

## 🆘 **Troubleshooting**

### Backend Won't Start
- Check if port 8000 is available
- Verify Python and Django are installed
- Check database connectivity

### Frontend Won't Start
- Check if port 3000 is available
- Run `npm install` in frontend directory
- Verify Node.js is installed

### Database Issues
- Ensure you're connected to the Microsoft network
- Check Azure AD authentication
- Verify database credentials in .env file

### CORS Errors
- Ensure backend is running on 127.0.0.1:8000
- Check that frontend is on localhost:3000
- Verify CORS settings in Django settings

## 📞 **Support**

If you encounter any issues:

1. Run `python check_status.py` to diagnose the problem
2. Check the terminal output for error messages
3. Verify all services are running on the correct ports
4. Ensure database connectivity is working
