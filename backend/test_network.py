"""
Script to test network connectivity to Fabric SQL Database.
Run this after connecting to Microsoft internal network.
"""

import subprocess
import sys

def test_network_connectivity():
    print("🔍 Testing network connectivity to Fabric SQL Database...")
    
    # Test hostname resolution
    hostname = "inlizh03ifejobtqt6dm75du-54fd7oykv2ebdzecamxep3ygi.msit-datawarehouse.database.windows.net"
    port = 1433
    
    try:
        # Test with PowerShell Test-NetConnection
        result = subprocess.run([
            "powershell.exe", 
            f"Test-NetConnection -ComputerName '{hostname}' -Port {port} -InformationLevel Quiet"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "True" in result.stdout:
            print("✅ Network connectivity successful!")
            print(f"✅ Can reach {hostname}:{port}")
            return True
        else:
            print("❌ Network connectivity failed")
            print(f"❌ Cannot reach {hostname}:{port}")
            print("📋 Troubleshooting steps:")
            print("   1. Connect to Microsoft VPN or corporate network")
            print("   2. Verify VPN connection is active")
            print("   3. Contact IT support if still unable to connect")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Connection test timed out")
        print("📋 This usually means you're not on Microsoft internal network")
        return False
    except Exception as e:
        print(f"❌ Error testing connectivity: {e}")
        return False

if __name__ == "__main__":
    test_network_connectivity()
