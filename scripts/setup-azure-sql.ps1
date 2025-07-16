# Azure SQL Database Setup Script
# Automates the complete setup process for Azure SQL Database (Serverless) testing

param(
    [string]$Password = "",
    [string]$ServerName = "luca-ama-serverless-srv",
    [string]$DatabaseName = "luca-ama-serverless-db"
)

Write-Host "🔵 Azure SQL Database (Serverless) Setup" -ForegroundColor Blue
Write-Host "=" * 50

# Check if password is provided
if (-not $Password) {
    Write-Host "❌ Password is required!" -ForegroundColor Red
    Write-Host "Usage: .\setup-azure-sql.ps1 -Password 'YourStrongPassword123!'" -ForegroundColor Yellow
    exit 1
}

# Validate password strength
if ($Password.Length -lt 8) {
    Write-Host "❌ Password must be at least 8 characters long!" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Setting up Azure SQL Database configuration..." -ForegroundColor Green

# Step 1: Update environment file
Write-Host "📝 Updating environment configuration..."
$envContent = @"
# Azure SQL Database (Serverless) Environment Configuration
# Branch: azure-sql-serverless-test
# Purpose: Performance testing against Microsoft Fabric SQL

# Django Settings
DJANGO_SETTINGS_MODULE=azure_sql_settings

# Azure SQL Database (Serverless) Connection
AZURE_SQL_SERVER=$ServerName.database.windows.net
AZURE_SQL_DATABASE=$DatabaseName
AZURE_SQL_USERNAME=lucaadmin
AZURE_SQL_PASSWORD=$Password

# Performance Testing
DATABASE_TYPE=azure_sql_serverless
TEST_ENVIRONMENT=azure_sql_comparison

# Debugging
DEBUG=True
SQL_DEBUG=True
"@

$envContent | Out-File -FilePath "backend\.env.azure_sql" -Encoding UTF8
Write-Host "✅ Environment file updated: backend\.env.azure_sql"

# Step 2: Switch to Azure SQL configuration
Write-Host "🔄 Switching to Azure SQL database configuration..."
try {
    python tools\switch_database.py azure_sql
    Write-Host "✅ Database configuration switched to Azure SQL"
} catch {
    Write-Host "❌ Failed to switch database configuration: $_" -ForegroundColor Red
    Write-Host "💡 Try running manually: python tools\switch_database.py azure_sql" -ForegroundColor Yellow
}

# Step 3: Test connection
Write-Host "🔍 Testing Azure SQL Database connection..."
try {
    python tests\database\test_azure_sql_connection.py
    Write-Host "✅ Connection test completed"
} catch {
    Write-Host "⚠️  Connection test failed or not yet configured" -ForegroundColor Yellow
    Write-Host "💡 This is expected if Azure SQL Database is not yet created" -ForegroundColor Cyan
}

# Display next steps
Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "=" * 30

Write-Host "1️⃣  Create Azure SQL Database (if not done):" -ForegroundColor White
Write-Host "   • Go to portal.azure.com" -ForegroundColor Gray
Write-Host "   • Create SQL Database with these settings:" -ForegroundColor Gray
Write-Host "     - Server: $ServerName" -ForegroundColor Gray
Write-Host "     - Database: $DatabaseName" -ForegroundColor Gray
Write-Host "     - Username: lucaadmin" -ForegroundColor Gray
Write-Host "     - Service Tier: General Purpose (Serverless)" -ForegroundColor Gray

Write-Host "`n2️⃣  Configure Firewall:" -ForegroundColor White
Write-Host "   • Add your IP address to firewall rules" -ForegroundColor Gray
Write-Host "   • Allow Azure services to access server" -ForegroundColor Gray

Write-Host "`n3️⃣  Run Database Migrations:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python manage.py migrate" -ForegroundColor Gray

Write-Host "`n4️⃣  Create Test Data:" -ForegroundColor White
Write-Host "   python management\create_quick_users.py" -ForegroundColor Gray
Write-Host "   python management\create_sample_data.py" -ForegroundColor Gray

Write-Host "`n5️⃣  Run Performance Tests:" -ForegroundColor White
Write-Host "   python tests\performance\azure_sql_performance_test.py" -ForegroundColor Gray

Write-Host "`n6️⃣  Compare Results:" -ForegroundColor White
Write-Host "   • Compare with Docker SQL results" -ForegroundColor Gray
Write-Host "   • Compare with Fabric SQL results" -ForegroundColor Gray
Write-Host "   • Analyze performance differences" -ForegroundColor Gray

Write-Host "`n📊 Configuration Summary:" -ForegroundColor Green
Write-Host "   Server: $ServerName.database.windows.net" -ForegroundColor White
Write-Host "   Database: $DatabaseName" -ForegroundColor White
Write-Host "   Username: lucaadmin" -ForegroundColor White
Write-Host "   Service Tier: Serverless" -ForegroundColor White
Write-Host "   Branch: azure-sql-serverless-test" -ForegroundColor White

Write-Host "`n🔐 Security Notes:" -ForegroundColor Yellow
Write-Host "   • Password is stored in .env.azure_sql (keep secure)" -ForegroundColor Gray
Write-Host "   • Use strong passwords for production" -ForegroundColor Gray
Write-Host "   • Limit firewall rules to necessary IPs only" -ForegroundColor Gray
Write-Host "   • Consider Azure AD authentication for production" -ForegroundColor Gray

Write-Host "`n✅ Setup script completed!" -ForegroundColor Green
Write-Host "📖 See docs\AZURE_SQL_SERVERLESS_SETUP.md for detailed instructions" -ForegroundColor Cyan
