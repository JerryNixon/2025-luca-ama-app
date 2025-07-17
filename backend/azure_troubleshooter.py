#!/usr/bin/env python3
"""
Azure SQL Connection Troubleshooter
Tests different connection methods to diagnose the issue
"""

def test_basic_connectivity():
    """Test if we can reach Azure SQL server at all"""
    import socket
    
    print("🔍 Testing basic network connectivity...")
    
    host = "luca-azure-ama.database.windows.net"
    port = 1433
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Network connectivity OK: Can reach {host}:{port}")
            return True
        else:
            print(f"❌ Network connectivity FAILED: Cannot reach {host}:{port}")
            print(f"💡 This confirms firewall is blocking the connection")
            return False
            
    except Exception as e:
        print(f"❌ Network test error: {e}")
        return False

def test_odbc_drivers():
    """List available ODBC drivers"""
    print("\n🔍 Checking ODBC drivers...")
    
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        print("📋 Available ODBC drivers:")
        for driver in drivers:
            print(f"  - {driver}")
        
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        print(f"\n🎯 SQL Server drivers: {len(sql_drivers)} found")
        return sql_drivers
        
    except ImportError:
        print("❌ pyodbc not installed")
        return []

def get_public_ip():
    """Get your current public IP address"""
    print("\n🔍 Getting your public IP address...")
    
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=10)
        ip = response.text.strip()
        print(f"🌐 Your public IP: {ip}")
        print(f"💡 This is the IP you need to add to Azure SQL firewall")
        return ip
    except Exception as e:
        print(f"❌ Could not get public IP: {e}")
        
        # Alternative method
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                print(f"🏠 Your local IP: {local_ip}")
                print("💡 Note: You need your PUBLIC IP for Azure firewall")
                return local_ip
        except Exception as e2:
            print(f"❌ Could not determine IP: {e2}")
            return None

if __name__ == "__main__":
    print("🔧 Azure SQL Connection Troubleshooter")
    print("=" * 50)
    
    # Test 1: Basic network connectivity
    can_connect = test_basic_connectivity()
    
    # Test 2: ODBC drivers
    sql_drivers = test_odbc_drivers()
    
    # Test 3: Get public IP
    public_ip = get_public_ip()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    
    if not can_connect:
        print("❌ FIREWALL ISSUE: Cannot reach Azure SQL server")
        print("🔧 SOLUTION: Add your IP to Azure SQL firewall rules")
        if public_ip:
            print(f"   IP to add: {public_ip}")
    else:
        print("✅ Network connectivity OK")
    
    if sql_drivers:
        print("✅ SQL Server ODBC drivers available")
    else:
        print("❌ No SQL Server ODBC drivers found")
    
    print("\n🎯 Next steps:")
    if not can_connect:
        print("1. Find Azure SQL firewall settings")
        print("2. Add your client IP address")
        print("3. Test connection again")
    else:
        print("1. Check Django database configuration")
        print("2. Test with different ODBC driver")
