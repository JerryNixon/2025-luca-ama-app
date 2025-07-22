// Practical Example: AMA App + Fabric + WebSocket Integration
// This shows how to add real-time Fabric analytics to your existing AMA application

import React, { useState, useEffect } from 'react';
import { HubConnectionBuilder, HubConnection } from '@microsoft/signalr';

interface FabricAMAAnalytics {
  eventId: string;
  timestamp: string;
  metrics: {
    activeParticipants: number;
    questionsPerMinute: number;
    avgEngagementScore: number;
    topTopics: string[];
    sentimentScore: number;
    moderatorEfficiency: number;
  };
  insights: {
    peakActivity: string;
    emergingTopics: Array<{topic: string, growth: number}>;
    userSegments: Array<{segment: string, count: number}>;
  };
}

interface QuestionTrend {
  timeWindow: string;
  questionCount: number;
  avgUpvotes: number;
  topKeywords: string[];
}

export default function FabricEnhancedAMADashboard({ eventId }: { eventId: string }) {
  const [connection, setConnection] = useState<HubConnection | null>(null);
  const [analytics, setAnalytics] = useState<FabricAMAAnalytics | null>(null);
  const [questionTrends, setQuestionTrends] = useState<QuestionTrend[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [insights, setInsights] = useState<string[]>([]);

  useEffect(() => {
    // Set up SignalR connection to Fabric analytics hub
    const newConnection = new HubConnectionBuilder()
      .withUrl('/api/fabric-signalr', {
        accessTokenFactory: () => getAuthToken() // Your auth token
      })
      .withAutomaticReconnect([0, 2000, 10000, 30000])
      .build();

    const startConnection = async () => {
      try {
        await newConnection.start();
        console.log('🔗 Connected to Fabric Analytics Hub');
        setConnection(newConnection);
        setIsConnected(true);

        // Subscribe to analytics for this specific AMA event
        await newConnection.invoke('JoinEventAnalytics', eventId);

        // Listen for real-time Fabric analytics
        newConnection.on('AMAAnalyticsUpdate', (data: FabricAMAAnalytics) => {
          console.log('📊 Fabric Analytics Update:', data);
          setAnalytics(data);
          
          // Add insights to the insights feed
          if (data.insights.emergingTopics.length > 0) {
            const newInsight = `🔥 Trending: ${data.insights.emergingTopics[0].topic} (+${data.insights.emergingTopics[0].growth}%)`;
            setInsights(prev => [newInsight, ...prev.slice(0, 9)]);
          }
        });

        // Listen for question trend analysis
        newConnection.on('QuestionTrends', (trends: QuestionTrend[]) => {
          console.log('📈 Question Trends from Fabric:', trends);
          setQuestionTrends(trends);
        });

        // Listen for real-time insights from Fabric AI analysis
        newConnection.on('FabricInsight', (insight: string) => {
          setInsights(prev => [insight, ...prev.slice(0, 9)]);
        });

        // Handle connection events
        newConnection.onreconnecting(() => {
          console.log('🔄 Reconnecting to Fabric...');
          setIsConnected(false);
        });

        newConnection.onreconnected(() => {
          console.log('✅ Reconnected to Fabric');
          setIsConnected(true);
          newConnection.invoke('JoinEventAnalytics', eventId);
        });

      } catch (error) {
        console.error('❌ Fabric connection failed:', error);
        setIsConnected(false);
      }
    };

    startConnection();

    return () => {
      if (newConnection) {
        newConnection.stop();
      }
    };
  }, [eventId]);

  const requestCustomAnalysis = async (analysisType: string) => {
    if (connection && isConnected) {
      try {
        await connection.invoke('RequestCustomAnalysis', {
          eventId,
          analysisType,
          parameters: { timeWindow: '15m' }
        });
      } catch (error) {
        console.error('Failed to request analysis:', error);
      }
    }
  };

  return (
    <div className="fabric-enhanced-ama-dashboard">
      {/* Connection Status */}
      <div className={`fabric-status ${isConnected ? 'connected' : 'disconnected'}`}>
        <span className={`status-indicator ${isConnected ? 'online' : 'offline'}`}></span>
        {isConnected ? '🧠 Fabric AI Connected' : '⚠️ Fabric Disconnected'}
      </div>

      {/* Real-time Analytics Panel */}
      {analytics && (
        <div className="analytics-panel">
          <h2>🚀 Live Event Analytics</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>👥 Active Participants</h3>
              <div className="metric-value">{analytics.metrics.activeParticipants}</div>
            </div>
            <div className="metric-card">
              <h3>❓ Questions/Min</h3>
              <div className="metric-value">{analytics.metrics.questionsPerMinute.toFixed(1)}</div>
            </div>
            <div className="metric-card">
              <h3>💯 Engagement Score</h3>
              <div className="metric-value">{analytics.metrics.avgEngagementScore.toFixed(1)}%</div>
            </div>
            <div className="metric-card">
              <h3>😊 Sentiment</h3>
              <div className={`metric-value sentiment-${getSentimentClass(analytics.metrics.sentimentScore)}`}>
                {getSentimentEmoji(analytics.metrics.sentimentScore)} {analytics.metrics.sentimentScore.toFixed(1)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Question Trends Chart */}
      {questionTrends.length > 0 && (
        <div className="trends-panel">
          <h2>📈 Question Trends (Fabric Analysis)</h2>
          <div className="trends-chart">
            {questionTrends.map((trend, index) => (
              <div key={index} className="trend-bar">
                <div className="trend-time">{trend.timeWindow}</div>
                <div 
                  className="trend-bar-fill"
                  style={{ width: `${(trend.questionCount / Math.max(...questionTrends.map(t => t.questionCount))) * 100}%` }}
                >
                  {trend.questionCount}
                </div>
                <div className="trend-keywords">
                  {trend.topKeywords.slice(0, 3).map(keyword => (
                    <span key={keyword} className="keyword-tag">{keyword}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Insights Feed */}
      <div className="insights-panel">
        <h2>🤖 Fabric AI Insights</h2>
        <div className="insights-actions">
          <button onClick={() => requestCustomAnalysis('engagement')}>
            Analyze Engagement Patterns
          </button>
          <button onClick={() => requestCustomAnalysis('topics')}>
            Deep Topic Analysis
          </button>
          <button onClick={() => requestCustomAnalysis('sentiment')}>
            Sentiment Breakdown
          </button>
        </div>
        <div className="insights-feed">
          {insights.length === 0 ? (
            <div className="no-insights">Waiting for Fabric insights...</div>
          ) : (
            insights.map((insight, index) => (
              <div key={index} className="insight-item">
                <span className="insight-time">
                  {new Date().toLocaleTimeString()}
                </span>
                <span className="insight-text">{insight}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Moderator Intelligence */}
      {analytics && analytics.insights && (
        <div className="moderator-intelligence">
          <h2>🎯 Moderator Intelligence</h2>
          <div className="intelligence-cards">
            <div className="intel-card">
              <h4>🔥 Hot Topics</h4>
              <ul>
                {analytics.insights.emergingTopics.map(topic => (
                  <li key={topic.topic}>
                    <strong>{topic.topic}</strong>
                    <span className="growth">+{topic.growth}%</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="intel-card">
              <h4>👥 Audience Segments</h4>
              <ul>
                {analytics.insights.userSegments.map(segment => (
                  <li key={segment.segment}>
                    {segment.segment}: {segment.count} users
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {analytics && (
        <div className="performance-panel">
          <h2>⚡ Event Performance</h2>
          <div className="performance-indicators">
            <div className={`indicator ${analytics.metrics.moderatorEfficiency > 80 ? 'good' : 'needs-attention'}`}>
              <span>Moderator Efficiency</span>
              <span>{analytics.metrics.moderatorEfficiency.toFixed(1)}%</span>
            </div>
            <div className="indicator">
              <span>Peak Activity Period</span>
              <span>{analytics.insights.peakActivity}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper functions
function getSentimentClass(score: number): string {
  if (score > 0.6) return 'positive';
  if (score > 0.4) return 'neutral';
  return 'negative';
}

function getSentimentEmoji(score: number): string {
  if (score > 0.7) return '😊';
  if (score > 0.5) return '😐';
  return '😔';
}

function getAuthToken(): string {
  // Return your authentication token for Fabric SignalR
  return localStorage.getItem('fabric-auth-token') || '';
}

// CSS styles would go in a separate file
const styles = `
.fabric-enhanced-ama-dashboard {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  padding: 20px;
}

.fabric-status {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.fabric-status.connected {
  background: #e7f5e7;
  color: #2d5a2d;
}

.fabric-status.disconnected {
  background: #fce7e7;
  color: #5a2d2d;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.status-indicator.online {
  background: #4caf50;
  animation: pulse 2s infinite;
}

.status-indicator.offline {
  background: #f44336;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.metric-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-left: 4px solid #2196f3;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #2196f3;
}

.sentiment-positive { color: #4caf50; }
.sentiment-neutral { color: #ff9800; }
.sentiment-negative { color: #f44336; }

.insights-feed {
  max-height: 300px;
  overflow-y: auto;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
}

.insight-item {
  display: flex;
  margin-bottom: 12px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  border-left: 3px solid #4caf50;
}

.insight-time {
  font-size: 12px;
  color: #666;
  margin-right: 12px;
  min-width: 80px;
}

.keyword-tag {
  background: #e3f2fd;
  color: #1565c0;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-right: 4px;
}

.trends-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trend-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.trend-bar-fill {
  background: linear-gradient(90deg, #2196f3, #21cbf3);
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  min-width: 40px;
}
`;

export { styles as FabricAMADashboardStyles };
