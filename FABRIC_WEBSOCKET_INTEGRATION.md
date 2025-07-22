# 🔗 Integrating WebSockets with Microsoft Fabric: Complete Guide

## 🎯 **Overview: Why Integrate Fabric with WebSockets?**

Microsoft Fabric excels at **data processing and analytics**, while WebSockets provide **real-time user interaction**. Combining them gives you:

- **Real-time dashboards** powered by Fabric analytics
- **Live notifications** from Fabric data pipeline events
- **Interactive applications** that respond to Fabric insights
- **Event-driven architectures** that scale massively

## 🏗️ **Architecture Patterns**

### **Pattern 1: Event-Driven Real-time Updates**
```
Fabric Pipeline → Event Hub → Azure Function → SignalR → Web Clients
```
**Best For**: Real-time dashboard updates, live analytics notifications

### **Pattern 2: Data Change Notifications**
```
Fabric → SQL Database → Change Data Capture → SignalR → Clients
```
**Best For**: Real-time data synchronization, live reporting

### **Pattern 3: Streaming Analytics to WebSocket**
```
Fabric KQL Database → Event Stream → Azure Function → Web PubSub → Clients
```
**Best For**: IoT dashboards, real-time monitoring

### **Pattern 4: PowerBI + SignalR Integration**
```
Fabric → PowerBI Dataset → PowerBI Streaming → SignalR → Custom App
```
**Best For**: Enhanced PowerBI experiences with custom interactions

## 🛠️ **Implementation Guide**

### **Step 1: Set Up Azure SignalR Service**

```bash
# Create SignalR Service
az signalr create --name "fabric-websocket-hub" \
  --resource-group "fabric-rg" \
  --location "East US" \
  --service-mode "Default" \
  --unit-count 1
```

```javascript
// JavaScript Client Setup
import { HubConnectionBuilder } from '@microsoft/signalr';

const connection = new HubConnectionBuilder()
  .withUrl('https://fabric-websocket-hub.service.signalr.net/realtime')
  .withAutomaticReconnect()
  .build();

// Listen for Fabric data updates
connection.on('FabricDataUpdate', (data) => {
  console.log('New data from Fabric:', data);
  updateDashboard(data);
});

await connection.start();
```

### **Step 2: Create Azure Function Bridge**

```csharp
// Azure Function: Fabric Event Hub → SignalR
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.SignalR.Management;
using System.Text.Json;

[Function("FabricToSignalR")]
public static async Task Run(
    [EventHubTrigger("fabric-events", Connection = "EventHubConnection")] 
    EventData[] events,
    
    [SignalROutput(HubName = "fabricHub")] 
    IAsyncCollector<SignalRMessage> signalRMessages)
{
    foreach (var eventData in events)
    {
        var fabricData = JsonSerializer.Deserialize<FabricEventData>(
            eventData.EventBody.ToString());
        
        // Transform Fabric data for WebSocket clients
        var clientMessage = new
        {
            Type = "DataUpdate",
            TableName = fabricData.TableName,
            Data = fabricData.ProcessedResults,
            Timestamp = DateTime.UtcNow,
            EventType = fabricData.EventType
        };
        
        // Send to all connected WebSocket clients
        await signalRMessages.AddAsync(new SignalRMessage
        {
            Target = "FabricDataUpdate",
            Arguments = new[] { clientMessage }
        });
    }
}
```

### **Step 3: Fabric Data Pipeline Configuration**

```sql
-- KQL Query in Fabric that triggers events
.create-or-alter function FabricToEventHub() {
    // Your analytics query
    YourTable
    | where Timestamp > ago(1m)
    | summarize 
        TotalCount = count(),
        AvgValue = avg(Value),
        MaxValue = max(Value)
        by bin(Timestamp, 30s)
    | extend EventType = "MetricsUpdate"
}

-- Set up continuous export to Event Hub
.create-or-alter continuous-export FabricWebSocketExport
over (YourTable)
to table ExternalTable 
with (intervalBetweenRuns=30s)
<| FabricToEventHub()
```

### **Step 4: Real-time Dashboard Implementation**

```typescript
// React component for real-time Fabric dashboard
import React, { useState, useEffect } from 'react';
import { HubConnection, HubConnectionBuilder } from '@microsoft/signalr';

interface FabricMetrics {
  totalCount: number;
  avgValue: number;
  maxValue: number;
  timestamp: string;
  eventType: string;
}

export default function FabricRealTimeDashboard() {
  const [connection, setConnection] = useState<HubConnection | null>(null);
  const [metrics, setMetrics] = useState<FabricMetrics[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const newConnection = new HubConnectionBuilder()
      .withUrl('/api/signalr', {
        skipNegotiation: true,
        transport: HttpTransportType.WebSockets
      })
      .withAutomaticReconnect()
      .build();

    setConnection(newConnection);

    const startConnection = async () => {
      try {
        await newConnection.start();
        setIsConnected(true);
        console.log('Connected to Fabric WebSocket hub!');

        // Listen for Fabric data updates
        newConnection.on('FabricDataUpdate', (data: any) => {
          console.log('Received Fabric update:', data);
          
          if (data.EventType === 'MetricsUpdate') {
            setMetrics(prevMetrics => [
              data.Data,
              ...prevMetrics.slice(0, 49) // Keep last 50 updates
            ]);
          }
        });

      } catch (error) {
        console.error('SignalR Connection Error:', error);
        setIsConnected(false);
      }
    };

    startConnection();

    return () => {
      if (newConnection) {
        newConnection.stop();
      }
    };
  }, []);

  return (
    <div className="fabric-realtime-dashboard">
      <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
        {isConnected ? '🟢 Connected to Fabric' : '🔴 Disconnected'}
      </div>
      
      <div className="metrics-grid">
        {metrics.map((metric, index) => (
          <div key={index} className="metric-card">
            <h3>Real-time Metrics</h3>
            <div className="metric-values">
              <div>Total: {metric.totalCount}</div>
              <div>Average: {metric.avgValue.toFixed(2)}</div>
              <div>Max: {metric.maxValue}</div>
              <div>Updated: {new Date(metric.timestamp).toLocaleTimeString()}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 🔄 **Advanced Integration Patterns**

### **Pattern A: Bidirectional Communication**

```csharp
// Allow WebSocket clients to trigger Fabric operations
[Function("ClientToFabric")]
public static async Task ClientTriggeredAnalysis(
    [SignalRTrigger("fabricHub", "category", "TriggerAnalysis")] 
    SignalRInvocationContext invocationContext,
    
    [EventHub("fabric-requests", Connection = "EventHubConnection")] 
    IAsyncCollector<string> eventCollector)
{
    var request = new
    {
        UserId = invocationContext.UserId,
        RequestType = "CustomAnalysis",
        Parameters = invocationContext.Arguments[0],
        Timestamp = DateTime.UtcNow
    };
    
    // Send request to Fabric for processing
    await eventCollector.AddAsync(JsonSerializer.Serialize(request));
}
```

### **Pattern B: Multi-Channel Broadcasting**

```javascript
// Client: Subscribe to specific Fabric data streams
const connection = new HubConnectionBuilder()
  .withUrl('/api/signalr')
  .build();

// Subscribe to different Fabric event types
connection.invoke('JoinGroup', 'SalesMetrics');
connection.invoke('JoinGroup', 'UserAnalytics');
connection.invoke('JoinGroup', 'SystemHealth');

// Handle different types of Fabric updates
connection.on('SalesUpdate', handleSalesData);
connection.on('UserUpdate', handleUserData);
connection.on('HealthUpdate', handleSystemHealth);
```

### **Pattern C: Fabric Notebook Integration**

```python
# Python Notebook in Fabric that publishes to WebSocket
import requests
import json
from datetime import datetime

# Fabric analytics computation
df_results = spark.sql("""
    SELECT 
        date_trunc('minute', timestamp) as minute,
        count(*) as events,
        avg(value) as avg_value
    FROM your_fabric_table 
    WHERE timestamp >= current_timestamp - interval 5 minutes
    GROUP BY date_trunc('minute', timestamp)
    ORDER BY minute DESC
""")

# Convert to JSON for WebSocket
results_json = df_results.toPandas().to_json(orient='records')

# Send to Event Hub (which triggers SignalR)
event_data = {
    "eventType": "NotebookResults",
    "source": "FabricNotebook",
    "data": json.loads(results_json),
    "timestamp": datetime.utcnow().isoformat()
}

# Publish to Event Hub
requests.post(
    "https://your-eventhub-namespace.servicebus.windows.net/fabric-events/messages",
    headers={"Authorization": f"Bearer {access_token}"},
    json=event_data
)
```

## 📊 **Real-World Use Cases**

### **Use Case 1: Live Trading Dashboard**
```
Fabric (Market Data) → Event Hub → SignalR → Trading Web App
- Real-time price updates from Fabric analytics
- Live portfolio calculations
- Instant trade notifications
```

### **Use Case 2: IoT Monitoring System**
```
Fabric (Sensor Analysis) → KQL Database → Function → WebSocket → Control Panel
- Real-time sensor anomaly detection
- Live system health monitoring
- Instant alert broadcasting
```

### **Use Case 3: Social Media Analytics**
```
Fabric (Social Sentiment) → Streaming → SignalR → Marketing Dashboard
- Real-time sentiment analysis
- Live engagement metrics
- Instant campaign adjustments
```

### **Use Case 4: Supply Chain Monitoring**
```
Fabric (Logistics Data) → Pipeline → WebSocket → Operations Center
- Real-time shipment tracking
- Live inventory updates
- Instant shortage alerts
```

## ⚡ **Performance Optimization**

### **Batching Strategy**
```csharp
// Batch multiple Fabric events before sending to WebSocket
private static readonly List<FabricEvent> _eventBatch = new();
private static readonly Timer _batchTimer = new Timer(ProcessBatch, null, 1000, 1000);

public static void ProcessBatch(object state)
{
    if (_eventBatch.Count == 0) return;
    
    var batchedEvents = _eventBatch.ToArray();
    _eventBatch.Clear();
    
    // Send batch to SignalR
    var batchMessage = new SignalRMessage
    {
        Target = "FabricBatchUpdate",
        Arguments = new[] { batchedEvents }
    };
    
    // Broadcast to all clients
    hubContext.Clients.All.SendAsync("FabricBatchUpdate", batchedEvents);
}
```

### **Filtering and Targeting**
```javascript
// Client-side filtering to reduce unnecessary updates
connection.on('FabricDataUpdate', (data) => {
  // Only process updates relevant to current user/view
  if (data.filters && data.filters.includes(currentUserRole)) {
    updateUI(data);
  }
});
```

## 💰 **Cost Analysis for Integration**

### **Small Scale (1K concurrent users)**
```
Azure SignalR: $1.20/month (1 unit)
Event Hub: $11/month (1 throughput unit)  
Azure Functions: $10/month (consumption)
Fabric: $10/month (F2 capacity)
Total: ~$32/month
```

### **Medium Scale (10K concurrent users)**
```
Azure SignalR: $12/month (10 units)
Event Hub: $22/month (2 throughput units)
Azure Functions: $50/month
Fabric: $50/month (F8 capacity)
Total: ~$134/month
```

### **Enterprise Scale (100K concurrent users)**
```
Azure SignalR: $120/month (100 units)
Event Hub: $110/month (10 throughput units)
Azure Functions: $200/month
Fabric: $200/month (F64 capacity)
Load Balancer: $25/month
Total: ~$655/month
```

## 🔧 **Development Tools & Templates**

### **Azure CLI Setup Script**
```bash
#!/bin/bash
# Complete Fabric + WebSocket integration setup

# Create resource group
az group create --name fabric-websocket-rg --location eastus

# Create SignalR Service
az signalr create \
  --name fabric-signalr-hub \
  --resource-group fabric-websocket-rg \
  --location eastus \
  --unit-count 1

# Create Event Hub Namespace
az eventhubs namespace create \
  --name fabric-events-ns \
  --resource-group fabric-websocket-rg \
  --location eastus

# Create Event Hub
az eventhubs eventhub create \
  --name fabric-events \
  --namespace-name fabric-events-ns \
  --resource-group fabric-websocket-rg

# Create Function App
az functionapp create \
  --name fabric-websocket-functions \
  --resource-group fabric-websocket-rg \
  --consumption-plan-location eastus \
  --runtime node \
  --storage-account fabricstorageacct
```

### **Infrastructure as Code (Bicep)**
```bicep
param location string = resourceGroup().location
param signalRName string = 'fabric-signalr'
param eventHubName string = 'fabric-events'

resource signalR 'Microsoft.SignalRService/SignalR@2022-02-01' = {
  name: signalRName
  location: location
  sku: {
    name: 'Free_F1'
    capacity: 1
  }
  properties: {
    features: [
      {
        flag: 'ServiceMode'
        value: 'Serverless'
      }
    ]
  }
}

resource eventHub 'Microsoft.EventHub/namespaces@2022-01-01-preview' = {
  name: eventHubName
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
}
```

## 🎯 **Best Practices**

### **1. Error Handling & Resilience**
```typescript
// Implement reconnection strategy
connection.onclose(async () => {
  console.log('SignalR connection lost. Attempting to reconnect...');
  await startConnection();
});

connection.onreconnecting(() => {
  console.log('SignalR reconnecting...');
  setConnectionStatus('Reconnecting');
});
```

### **2. Authentication & Security**
```csharp
// Secure SignalR with Azure AD
[Authorize]
public class FabricHub : Hub
{
    public async Task JoinUserGroup()
    {
        var userId = Context.UserIdentifier;
        await Groups.AddToGroupAsync(Context.ConnectionId, $"User_{userId}");
    }
}
```

### **3. Monitoring & Diagnostics**
```javascript
// Add comprehensive logging
connection.start()
  .then(() => console.log('✅ Fabric WebSocket connected'))
  .catch(err => {
    console.error('❌ Fabric WebSocket failed:', err);
    // Send telemetry to Application Insights
    appInsights.trackException({ exception: err });
  });
```

## 🚀 **Your AMA App Integration Example**

Here's how you could integrate your AMA app with Fabric:

```typescript
// Real-time analytics for your AMA app powered by Fabric
connection.on('AMAAnalytics', (analytics) => {
  // Real-time engagement metrics from Fabric
  updateEngagementChart(analytics.participationRate);
  updateQuestionTrends(analytics.topicTrends);
  updateSentimentAnalysis(analytics.sentiment);
  
  // Live moderator insights
  if (isModeratorView) {
    showHotTopics(analytics.emergingTopics);
    highlightActiveUsers(analytics.topContributors);
  }
});
```

## 🏆 **Summary**

**Fabric + WebSocket integration is powerful and mature**, offering:

✅ **Real-time analytics dashboards**  
✅ **Event-driven architectures**  
✅ **Enterprise-scale reliability**  
✅ **Rich Azure ecosystem integration**  
✅ **Proven patterns and tools**  

**Trade-offs vs Supabase:**
- **More complex** (multiple services vs single platform)
- **Higher cost** at small scale  
- **Enterprise features** (compliance, AD integration)
- **Unlimited scalability** potential

**Recommendation**: For your current AMA app, Supabase is simpler. But if you grow to enterprise scale or need complex analytics, Fabric + SignalR becomes very attractive!

---
*Complete integration guide: From Fabric data pipelines to real-time WebSocket clients* 🔗
