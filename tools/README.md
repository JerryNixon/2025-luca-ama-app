# Tools Directory

This directory contains development, testing, and debugging tools for the Luca AMA application.

## Structure

### `/tests/`
Contains all test scripts for validating application functionality:
- API testing scripts (`test_api_*.py`)
- Database connectivity tests (`test_database_*.py`) 
- Frontend/backend integration tests (`test_frontend_*.py`)
- Authentication tests (`test_login_*.py`, `test_jerry_*.py`)
- Performance tests (`test_backend_speed.py`, `test_button_performance.py`)
- Quick validation scripts (`quick_*.py`, `simple_*.py`)

### `/debug/`
Contains debugging utilities for troubleshooting:
- Authentication debugging (`debug_*_auth.py`)
- State inspection tools (`debug_current_state.py`)
- Event workflow debugging (`debug_events_workflow.py`)
- Login flow debugging (`debug_login.py`)

### `/utils/`
Contains utility scripts for maintenance and checks:
- Status checking (`status_check.py`, `check_*.py`)
- Access control analysis (`ACCESS_CONTROL_SUMMARY.py`)
- Component creation tools (`create_*.py`)
- Performance optimization tools (`fix_button_lag.py`)

## Usage

All scripts in this directory should be run from the project root directory:

```bash
# Example: Run API tests
python tools/tests/test_api_endpoints.py

# Example: Check application status  
python tools/utils/status_check.py

# Example: Debug authentication issues
python tools/debug/debug_frontend_auth.py
```

## Note on Path Setup

Scripts in subdirectories (`tests/`, `debug/`, `utils/`) automatically adjust their Python path to locate the backend Django modules. No manual path configuration is needed.
