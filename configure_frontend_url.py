#!/usr/bin/env python3
"""
Frontend URL Configuration Script
Easily update the frontend URL for share link generation
"""

import os
import sys

def update_frontend_url(port):
    """Update the FRONTEND_URL in the .env file"""
    env_file = 'backend/.env'
    frontend_url = f'http://localhost:{port}'
    
    if not os.path.exists(env_file):
        print(f"❌ Error: {env_file} not found!")
        return False
    
    # Read the current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update the FRONTEND_URL line
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('FRONTEND_URL='):
            lines[i] = f'FRONTEND_URL={frontend_url}\n'
            updated = True
            break
    
    # If FRONTEND_URL doesn't exist, add it
    if not updated:
        lines.append(f'\n# Frontend URL Configuration\nFRONTEND_URL={frontend_url}\n')
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Updated FRONTEND_URL to: {frontend_url}")
    print(f"📝 File updated: {env_file}")
    print(f"🔄 Please restart the backend server to apply changes:")
    print(f"   cd backend && python manage.py runserver")
    
    return True

def main():
    print("🔗 Frontend URL Configuration Tool")
    print("=" * 40)
    
    if len(sys.argv) != 2:
        print("Usage: python configure_frontend_url.py <port>")
        print("")
        print("Examples:")
        print("  python configure_frontend_url.py 3000")
        print("  python configure_frontend_url.py 3001") 
        print("  python configure_frontend_url.py 3002")
        return
    
    try:
        port = int(sys.argv[1])
        if port < 1000 or port > 9999:
            print("❌ Error: Port must be between 1000 and 9999")
            return
        
        update_frontend_url(port)
        
    except ValueError:
        print("❌ Error: Port must be a number")

if __name__ == "__main__":
    main()
