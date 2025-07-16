# Azure SQL Database Serverless Setup Guide

## Overview
This guide walks through setting up Azure SQL Database (Serverless) to test database performance compared to Microsoft Fabric SQL. The goal is to determine if latency issues are from Fabric's abstraction layer or the underlying Azure SQL infrastructure.

## Branch: `azure-sql-serverless-test`

## Phase 1: Azure Portal Setup

### Step 1: Access Azure Portal
1. Go to [portal.azure.com](https://portal.azure.com)
2. Sign in with your Microsoft account
3. Ensure you have an active Azure subscription

### Step 2: Create Resource Group (if needed)
1. Navigate to **Resource Groups** in the Azure Portal
2. Click **+ Create**
3. Fill in details:
   - **Subscription**: Select your subscription
   - **Resource group name**: `luca-ama-test-rg` (or use existing)
   - **Region**: Choose same region as your application (e.g., East US)
4. Click **Review + Create** → **Create**

### Step 3: Create Azure SQL Database (Serverless)
1. Navigate to **SQL databases** in Azure Portal
2. Click **+ Create**
3. Configure **Basics** tab:
   - **Subscription**: Your subscription
   - **Resource group**: `luca-ama-test-rg`
   - **Database name**: `luca-ama-serverless-db`
   - **Server**: Click **Create new**

### Step 4: Create SQL Server
1. In the **Create SQL Database Server** dialog:
   - **Server name**: `luca-ama-serverless-srv` (must be globally unique)
   - **Location**: Same as resource group
   - **Authentication method**: Use SQL authentication
   - **Server admin login**: `lucaadmin`
   - **Password**: Create a strong password (save this!)
   - **Confirm password**: Re-enter password
2. Click **OK**

### Step 5: Configure Database Settings
1. Back in **Create SQL Database**:
   - **Want to use SQL elastic pool?**: No
   - **Compute + storage**: Click **Configure database**
2. In **Configure** dialog:
   - **Service tier**: General Purpose
   - **Compute tier**: Serverless
   - **Hardware configuration**: Gen5
   - **vCores**: 1 vCore (minimum)
   - **Memory**: 3 GB
   - **Min vCores**: 0.5
   - **Auto-pause delay**: 60 minutes
   - **Data max size**: 32 GB
3. Click **Apply**

### Step 6: Networking Configuration
1. Go to **Networking** tab:
   - **Connectivity method**: Public endpoint
   - **Allow Azure services**: Yes
   - **Add current client IP**: Yes
   - **Connection policy**: Default
2. Click **Next: Security**

### Step 7: Security Settings
1. **Security** tab:
   - **Enable Microsoft Defender for SQL**: Not now (to save costs)
   - **Ledger**: Leave unchecked
2. Click **Next: Additional settings**

### Step 8: Additional Settings
1. **Additional settings** tab:
   - **Use existing data**: None
   - **Database collation**: Default (SQL_Latin1_General_CP1_CI_AS)
   - **Enable advanced data security**: Not now
2. Click **Review + Create**

### Step 9: Review and Create
1. Review all settings
2. Click **Create**
3. Wait for deployment (usually 2-5 minutes)

## Phase 2: Database Configuration

### Step 10: Get Connection Details
1. Once deployed, go to the SQL database resource
2. Click **Connection strings** in the left menu
3. Copy the **ADO.NET** connection string
4. Note the format: `Server=tcp:[server].database.windows.net,1433;Initial Catalog=[database];Persist Security Info=False;User ID=[username];Password=[password];MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;`

### Step 11: Configure Firewall (if needed)
1. Go to the SQL server resource (not the database)
2. Click **Networking** in the left menu
3. Under **Firewall rules**, ensure your IP is listed
4. Add additional IPs if needed for your development environment

## Phase 3: Application Configuration

### Step 12: Update Django Settings
The connection string format for Azure SQL Database:
```
Server=tcp:luca-ama-serverless-srv.database.windows.net,1433;Database=luca-ama-serverless-db;User ID=lucaadmin;Password=[YOUR_PASSWORD];Encrypt=true;Connection Timeout=30;
```

### Step 13: Environment Variables
Create new environment variables for Azure SQL connection:
- `AZURE_SQL_SERVER`: luca-ama-serverless-srv.database.windows.net
- `AZURE_SQL_DATABASE`: luca-ama-serverless-db  
- `AZURE_SQL_USERNAME`: lucaadmin
- `AZURE_SQL_PASSWORD`: [your password]

## Next Steps
1. Update Django database configuration
2. Run migrations
3. Create test data
4. Run performance benchmarks
5. Compare results with Docker and Fabric

## Important Notes
- **Serverless Auto-Pause**: Database will pause after 60 minutes of inactivity
- **Cold Start**: First query after pause will have higher latency
- **Scaling**: vCores can scale from 0.5 to 1 automatically
- **Billing**: Pay per vCore-second used, not provisioned
- **Backup**: Automatic backups included (7-day retention)

## Cost Considerations
- Serverless billing is based on compute usage
- Storage is billed separately
- Expect minimal costs for development/testing
- Consider pausing when not in use

## Security Best Practices
- Use strong passwords
- Limit firewall rules to necessary IPs
- Consider Azure AD authentication for production
- Enable SSL/TLS encryption (default)
