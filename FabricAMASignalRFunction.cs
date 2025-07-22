// Azure Function: Bridge between Fabric and SignalR for AMA App
// This function receives events from Fabric and broadcasts them via SignalR to your AMA app

using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using System.Text.Json;
using Microsoft.Azure.SignalR.Management;

namespace FabricAMAIntegration
{
    public class FabricToAMASignalR
    {
        private readonly ILogger<FabricToAMASignalR> _logger;
        private readonly ServiceManager _serviceManager;

        public FabricToAMASignalR(ILogger<FabricToAMASignalR> logger)
        {
            _logger = logger;
            _serviceManager = new ServiceManagerBuilder()
                .WithOptions(option =>
                {
                    option.ConnectionString = Environment.GetEnvironmentVariable("AzureSignalRConnectionString");
                })
                .BuildServiceManager();
        }

        // Function 1: Process Fabric Event Hub data and broadcast to AMA app
        [Function("ProcessFabricAMAEvents")]
        public async Task ProcessFabricEvents(
            [EventHubTrigger("fabric-ama-events", Connection = "EventHubConnection")] 
            EventData[] events,
            FunctionContext context)
        {
            _logger.LogInformation($"Processing {events.Length} events from Fabric");

            var hubContext = await _serviceManager.CreateHubContextAsync("AMAHub", context.CancellationToken);

            foreach (var eventData in events)
            {
                try
                {
                    var fabricEvent = JsonSerializer.Deserialize<FabricAMAEvent>(
                        eventData.EventBody.ToString());

                    _logger.LogInformation($"Processing Fabric event: {fabricEvent.EventType} for AMA {fabricEvent.EventId}");

                    // Transform Fabric data for AMA app consumption
                    var amaUpdate = TransformFabricEventToAMA(fabricEvent);

                    // Broadcast to specific AMA event group
                    await hubContext.Clients.Group($"AMA_{fabricEvent.EventId}")
                        .SendAsync("AMAAnalyticsUpdate", amaUpdate);

                    // Send specific insights to moderators
                    if (amaUpdate.ModeratorInsights?.Count > 0)
                    {
                        await hubContext.Clients.Group($"AMA_{fabricEvent.EventId}_Moderators")
                            .SendAsync("ModeratorInsights", amaUpdate.ModeratorInsights);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error processing Fabric event");
                }
            }
        }

        // Function 2: Handle custom analysis requests from AMA app
        [Function("HandleCustomAnalysisRequest")]
        public async Task<HttpResponseData> HandleAnalysisRequest(
            [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequestData req,
            [EventHub("fabric-analysis-requests", Connection = "EventHubConnection")] 
            IAsyncCollector<string> eventCollector,
            FunctionContext context)
        {
            var request = await JsonSerializer.DeserializeAsync<CustomAnalysisRequest>(req.Body);
            
            _logger.LogInformation($"Custom analysis requested: {request.AnalysisType} for event {request.EventId}");

            // Forward request to Fabric for processing
            var fabricRequest = new FabricAnalysisRequest
            {
                RequestId = Guid.NewGuid().ToString(),
                EventId = request.EventId,
                AnalysisType = request.AnalysisType,
                Parameters = request.Parameters,
                Timestamp = DateTime.UtcNow,
                Source = "AMAApp"
            };

            await eventCollector.AddAsync(JsonSerializer.Serialize(fabricRequest));

            var response = req.CreateResponse(HttpStatusCode.OK);
            await response.WriteStringAsync(JsonSerializer.Serialize(new { 
                RequestId = fabricRequest.RequestId,
                Status = "Submitted",
                EstimatedProcessingTime = "30-60 seconds"
            }));

            return response;
        }

        // Function 3: SignalR negotiate function for AMA app clients
        [Function("SignalRNegotiate")]
        public async Task<HttpResponseData> Negotiate(
            [HttpTrigger(AuthorizationLevel.Anonymous, "post")] HttpRequestData req,
            FunctionContext context)
        {
            var negotiateResponse = await _serviceManager.GetClientAccessUriAsync("AMAHub");
            
            var response = req.CreateResponse(HttpStatusCode.OK);
            await response.WriteAsJsonAsync(new
            {
                url = negotiateResponse.ToString()
            });

            return response;
        }

        // Function 4: Join AMA event group (called when user opens specific AMA)
        [Function("JoinAMAEvent")]
        public async Task<HttpResponseData> JoinAMAEvent(
            [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequestData req,
            FunctionContext context)
        {
            var joinRequest = await JsonSerializer.DeserializeAsync<JoinEventRequest>(req.Body);
            
            var hubContext = await _serviceManager.CreateHubContextAsync("AMAHub", context.CancellationToken);
            
            // Add user to AMA event group
            await hubContext.Groups.AddToGroupAsync(joinRequest.ConnectionId, $"AMA_{joinRequest.EventId}");
            
            // Add to moderator group if applicable
            if (joinRequest.IsModerator)
            {
                await hubContext.Groups.AddToGroupAsync(joinRequest.ConnectionId, $"AMA_{joinRequest.EventId}_Moderators");
            }

            _logger.LogInformation($"User {joinRequest.UserId} joined AMA {joinRequest.EventId}");

            var response = req.CreateResponse(HttpStatusCode.OK);
            await response.WriteStringAsync(JsonSerializer.Serialize(new { Status = "Joined" }));
            return response;
        }

        // Transform Fabric analytics data to AMA app format
        private AMAAnalyticsUpdate TransformFabricEventToAMA(FabricAMAEvent fabricEvent)
        {
            return fabricEvent.EventType switch
            {
                "QuestionAnalytics" => new AMAAnalyticsUpdate
                {
                    EventId = fabricEvent.EventId,
                    Timestamp = fabricEvent.Timestamp,
                    Metrics = new AMAMetrics
                    {
                        ActiveParticipants = fabricEvent.Data.GetProperty("active_users").GetInt32(),
                        QuestionsPerMinute = fabricEvent.Data.GetProperty("questions_per_minute").GetDouble(),
                        AvgEngagementScore = fabricEvent.Data.GetProperty("engagement_score").GetDouble(),
                        SentimentScore = fabricEvent.Data.GetProperty("sentiment_avg").GetDouble(),
                        TopTopics = fabricEvent.Data.GetProperty("top_topics").EnumerateArray()
                            .Select(t => t.GetString()).ToArray()
                    },
                    Insights = ExtractInsights(fabricEvent.Data),
                    ModeratorInsights = ExtractModeratorInsights(fabricEvent.Data)
                },
                
                "RealTimeEngagement" => new AMAAnalyticsUpdate
                {
                    EventId = fabricEvent.EventId,
                    Timestamp = fabricEvent.Timestamp,
                    QuestionTrends = fabricEvent.Data.GetProperty("question_trends").EnumerateArray()
                        .Select(qt => new QuestionTrend
                        {
                            TimeWindow = qt.GetProperty("time_window").GetString(),
                            QuestionCount = qt.GetProperty("count").GetInt32(),
                            AvgUpvotes = qt.GetProperty("avg_upvotes").GetDouble(),
                            TopKeywords = qt.GetProperty("keywords").EnumerateArray()
                                .Select(k => k.GetString()).ToArray()
                        }).ToArray()
                },
                
                _ => new AMAAnalyticsUpdate
                {
                    EventId = fabricEvent.EventId,
                    Timestamp = fabricEvent.Timestamp,
                    RawFabricData = fabricEvent.Data
                }
            };
        }

        private AMAInsights ExtractInsights(JsonElement data)
        {
            return new AMAInsights
            {
                PeakActivity = data.TryGetProperty("peak_activity", out var peak) ? 
                    peak.GetString() : "Not detected",
                EmergingTopics = data.TryGetProperty("emerging_topics", out var topics) ?
                    topics.EnumerateArray().Select(t => new EmergingTopic
                    {
                        Topic = t.GetProperty("topic").GetString(),
                        Growth = t.GetProperty("growth_rate").GetDouble()
                    }).ToArray() : new EmergingTopic[0],
                UserSegments = data.TryGetProperty("user_segments", out var segments) ?
                    segments.EnumerateArray().Select(s => new UserSegment
                    {
                        Segment = s.GetProperty("segment").GetString(),
                        Count = s.GetProperty("count").GetInt32()
                    }).ToArray() : new UserSegment[0]
            };
        }

        private List<string> ExtractModeratorInsights(JsonElement data)
        {
            var insights = new List<string>();

            if (data.TryGetProperty("moderator_alerts", out var alerts))
            {
                insights.AddRange(alerts.EnumerateArray().Select(a => a.GetString()));
            }

            if (data.TryGetProperty("suggested_actions", out var actions))
            {
                insights.AddRange(actions.EnumerateArray().Select(a => $"💡 {a.GetString()}"));
            }

            return insights;
        }
    }

    // Data models for Fabric integration
    public class FabricAMAEvent
    {
        public string EventType { get; set; }
        public string EventId { get; set; }
        public DateTime Timestamp { get; set; }
        public JsonElement Data { get; set; }
        public string Source { get; set; }
    }

    public class AMAAnalyticsUpdate
    {
        public string EventId { get; set; }
        public string Timestamp { get; set; }
        public AMAMetrics Metrics { get; set; }
        public AMAInsights Insights { get; set; }
        public QuestionTrend[] QuestionTrends { get; set; }
        public List<string> ModeratorInsights { get; set; }
        public JsonElement? RawFabricData { get; set; }
    }

    public class AMAMetrics
    {
        public int ActiveParticipants { get; set; }
        public double QuestionsPerMinute { get; set; }
        public double AvgEngagementScore { get; set; }
        public double SentimentScore { get; set; }
        public double ModeratorEfficiency { get; set; }
        public string[] TopTopics { get; set; }
    }

    public class AMAInsights
    {
        public string PeakActivity { get; set; }
        public EmergingTopic[] EmergingTopics { get; set; }
        public UserSegment[] UserSegments { get; set; }
    }

    public class EmergingTopic
    {
        public string Topic { get; set; }
        public double Growth { get; set; }
    }

    public class UserSegment
    {
        public string Segment { get; set; }
        public int Count { get; set; }
    }

    public class QuestionTrend
    {
        public string TimeWindow { get; set; }
        public int QuestionCount { get; set; }
        public double AvgUpvotes { get; set; }
        public string[] TopKeywords { get; set; }
    }

    public class CustomAnalysisRequest
    {
        public string EventId { get; set; }
        public string AnalysisType { get; set; }
        public Dictionary<string, object> Parameters { get; set; }
        public string UserId { get; set; }
    }

    public class FabricAnalysisRequest
    {
        public string RequestId { get; set; }
        public string EventId { get; set; }
        public string AnalysisType { get; set; }
        public Dictionary<string, object> Parameters { get; set; }
        public DateTime Timestamp { get; set; }
        public string Source { get; set; }
    }

    public class JoinEventRequest
    {
        public string ConnectionId { get; set; }
        public string EventId { get; set; }
        public string UserId { get; set; }
        public bool IsModerator { get; set; }
    }
}
