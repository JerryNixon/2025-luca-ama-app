# Project Structure

This Django + Next.js AMA application has been organized into a clean, logical structure:

## Root Directory
- `README.md` - Main project documentation
- `LICENSE` - MIT license
- `.gitignore` - Git ignore patterns
- `.vscode/` - VS Code workspace settings

## Core Application
- `backend/` - Django backend application (clean structure)
  - `ama_backend/` - Django project settings
  - `api/` - Main Django app
  - `management/` - Django management scripts and utilities
  - `config/` - Configuration files
  - Core Django files (`manage.py`, `requirements.txt`, etc.)
- `frontend/` - Next.js frontend application

## Organization Structure
- `tests/` - All testing files organized by category
  - `tests/api/` - API testing scripts
  - `tests/auth/` - Authentication and authorization tests
  - `tests/database/` - Database connectivity and performance tests
  - `tests/frontend/` - Frontend integration tests
  - `tests/performance/` - Performance benchmarking scripts
  - `tests/results/` - Test output and result files
- `scripts/` - Startup scripts and automation tools
- `tools/` - Development utilities and debugging tools
  - `tools/debug/` - Debugging utilities and troubleshooting scripts
- `docs/` - Complete project documentation
  - `docs/project/` - Development progress notes and status updates

## Key Files
- `tests/performance/` contains the latency benchmarking scripts comparing Docker SQL Server vs Microsoft Fabric
- `backend/management/` contains all Django management scripts and user administration utilities
- `scripts/` contains PowerShell startup scripts for easy development
- `tools/` contains development utilities including database switching and HTML test generators
- `docs/` contains formal project documentation, API specs, and development guides
- `docs/project/` contains development progress notes and completion status updates

This structure makes it easy to find relevant files and maintain the codebase while keeping the root directory clean and professional.

## Cleanup Summary
- ✅ Eliminated duplicate `/tests/` directories (consolidated into root `/tests/`)
- ✅ Removed duplicate debug files (consolidated into `/tools/debug/`)
- ✅ Cleaned up backend directory - moved misplaced test/performance files
- ✅ Organized Django management scripts in `backend/management/`
- ✅ Consolidated duplicate management directories - removed empty root `/management/`
- ✅ Moved development utilities to appropriate locations (`tools/`)
- ✅ Fixed file path references after moves to maintain functionality
- ✅ Moved all files to their proper logical locations
- ✅ No more file duplications or inconsistent organization
- ✅ Preserved Django app structure and dependencies
- ✅ Clean, professional structure with single-purpose directories
