#!/usr/bin/env python3
"""
Enhanced Real-Time Dashboard
Integrates with real-time analytics engine for live social media monitoring
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import sqlite3
from datetime import datetime, timedelta
import threading
import time
import logging
from pathlib import Path

# Import our modules
from real_time_analytics import real_time_engine, start_real_time_analytics
from linkedin_real_api import linkedin_real_api
from twitter_real_api import twitter_real_api
from social_media_analytics import SocialMediaAnalyticsManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
MONITORING_CONFIG = {
    'platforms': ['twitter', 'linkedin'],
    'entities': {
        'twitter': 'elonmusk',  # Example - can be made configurable
        'linkedin': '1441'      # Example LinkedIn company ID
    },
    'update_interval': 60  # seconds
}

class EnhancedDashboard:
    """Enhanced dashboard with real-time capabilities"""

    def __init__(self):
        self.is_monitoring = False
        self.current_config = MONITORING_CONFIG
        self.social_manager = SocialMediaAnalyticsManager()

    def start_monitoring(self):
        """Start real-time monitoring"""
        if not self.is_monitoring:
            logger.info("Starting enhanced dashboard monitoring...")

            # Start real-time analytics
            self.analytics_engine = start_real_time_analytics(
                platforms=self.current_config['platforms'],
                entities=self.current_config['entities']
            )

            self.is_monitoring = True

            # Start background thread for Socket.IO updates
            self.start_socketio_updates()

            logger.info("Enhanced dashboard monitoring started")

    def start_socketio_updates(self):
        """Start background thread to push updates via Socket.IO"""
        def update_loop():
            while self.is_monitoring:
                try:
                    # Get latest analytics
                    summary = self.analytics_engine.get_analytics_summary()

                    # Get recent alerts
                    alerts = self.analytics_engine.get_recent_alerts(limit=5)

                    # Emit updates to all connected clients
                    socketio.emit('analytics_update', {
                        'summary': summary,
                        'alerts': alerts,
                        'timestamp': datetime.now().isoformat()
                    })

                    time.sleep(30)  # Update every 30 seconds

                except Exception as e:
                    logger.error(f"Error in Socket.IO update loop: {e}")
                    time.sleep(10)

        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if self.is_monitoring:
            logger.info("Stopping enhanced dashboard monitoring...")
            self.is_monitoring = False
            if hasattr(self, 'analytics_engine'):
                self.analytics_engine.stop()

    def get_historical_data(self, platform: str, metric: str, hours: int = 24):
        """Get historical data for charts"""
        try:
            return self.analytics_engine.get_historical_metrics(platform, metric, hours)
        except:
            return []

    def get_trending_analysis(self):
        """Get trending analysis across platforms"""
        try:
            summary = self.analytics_engine.get_analytics_summary()
            trends = {}

            for platform, metrics in summary.items():
                platform_trends = []
                for metric_name, metric_data in metrics.items():
                    if metric_data.get('trend') != 'stable':
                        platform_trends.append({
                            'metric': metric_name,
                            'trend': metric_data['trend'],
                            'change_percent': metric_data['change_percent'],
                            'value': metric_data['value']
                        })

                if platform_trends:
                    trends[platform] = sorted(platform_trends,
                                             key=lambda x: abs(x['change_percent']),
                                             reverse=True)

            return trends
        except Exception as e:
            logger.error(f"Error getting trending analysis: {e}")
            return {}

    def get_performance_insights(self):
        """Generate performance insights and recommendations"""
        try:
            insights = []
            summary = self.analytics_engine.get_analytics_summary()

            for platform, metrics in summary.items():
                # Engagement analysis
                if 'engagement' in metrics:
                    engagement = metrics['engagement']['value']
                    if engagement > 5.0:
                        insights.append({
                            'type': 'success',
                            'platform': platform,
                            'message': f"Excellent engagement rate of {engagement}%",
                            'recommendation': "Keep up the great content strategy!"
                        })
                    elif engagement < 2.0:
                        insights.append({
                            'type': 'warning',
                            'platform': platform,
                            'message': f"Low engagement rate of {engagement}%",
                            'recommendation': "Consider using more engaging content formats"
                        })

                # Follower growth
                if 'followers' in metrics:
                    followers = metrics['followers']
                    change = followers.get('change_percent', 0)
                    if change > 10:
                        insights.append({
                            'type': 'success',
                            'platform': platform,
                            'message': f"Strong follower growth of {change}%",
                            'recommendation': "Analyze what content drove this growth"
                        })
                    elif change < -5:
                        insights.append({
                            'type': 'alert',
                            'platform': platform,
                            'message': f"Followers decreased by {abs(change)}%",
                            'recommendation': "Review recent content and engagement patterns"
                        })

            return sorted(insights, key=lambda x: x['type'] == 'alert', reverse=True)
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []

# Create dashboard instance
dashboard = EnhancedDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('enhanced_dashboard.html')

@app.route('/api/analytics/summary')
def get_analytics_summary():
    """Get current analytics summary"""
    try:
        summary = dashboard.analytics_engine.get_analytics_summary() if dashboard.is_monitoring else {}
        return jsonify({
            'success': True,
            'data': summary,
            'monitoring': dashboard.is_monitoring,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/history/<platform>/<metric>')
def get_analytics_history(platform, metric):
    """Get historical analytics data"""
    try:
        hours = int(request.args.get('hours', 24))
        history = dashboard.get_historical_data(platform, metric, hours)
        return jsonify({
            'success': True,
            'data': history,
            'platform': platform,
            'metric': metric,
            'hours': hours
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts"""
    try:
        platform = request.args.get('platform')
        limit = int(request.args.get('limit', 10))
        alerts = dashboard.analytics_engine.get_recent_alerts(platform, limit) if dashboard.is_monitoring else []
        return jsonify({
            'success': True,
            'data': alerts,
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/insights')
def get_insights():
    """Get performance insights"""
    try:
        insights = dashboard.get_performance_insights()
        trends = dashboard.get_trending_analysis()
        return jsonify({
            'success': True,
            'insights': insights,
            'trends': trends,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start real-time monitoring"""
    try:
        data = request.get_json() or {}

        # Update configuration if provided
        if data:
            dashboard.current_config.update(data)

        dashboard.start_monitoring()

        return jsonify({
            'success': True,
            'message': 'Real-time monitoring started',
            'config': dashboard.current_config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop real-time monitoring"""
    try:
        dashboard.stop_monitoring()
        return jsonify({
            'success': True,
            'message': 'Real-time monitoring stopped'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'config': dashboard.current_config,
            'monitoring': dashboard.is_monitoring
        })
    else:
        try:
            data = request.get_json()
            dashboard.current_config.update(data)
            return jsonify({
                'success': True,
                'message': 'Configuration updated',
                'config': dashboard.current_config
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {
        'message': 'Connected to enhanced dashboard',
        'monitoring': dashboard.is_monitoring
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('request_update')
def handle_request_update():
    """Handle manual update request"""
    try:
        summary = dashboard.analytics_engine.get_analytics_summary() if dashboard.is_monitoring else {}
        alerts = dashboard.analytics_engine.get_recent_alerts(limit=5) if dashboard.is_monitoring else []

        emit('analytics_update', {
            'summary': summary,
            'alerts': alerts,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('subscribe_platform')
def handle_subscribe_platform(data):
    """Handle platform subscription"""
    platform = data.get('platform')
    logger.info(f"Client {request.sid} subscribed to {platform}")
    emit('subscribed', {'platform': platform})

# Create enhanced dashboard template
def create_enhanced_template():
    """Create the enhanced dashboard HTML template"""
    template_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Real-Time Analytics Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .metric-card {
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .trend-up { color: #10b981; }
        .trend-down { color: #ef4444; }
        .trend-stable { color: #6b7280; }
        .pulse-dot {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .alert-item {
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from {
                transform: translateX(-100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-chart-line text-blue-600 text-2xl"></i>
                    <h1 class="text-2xl font-bold text-gray-900">Enhanced Real-Time Analytics</h1>
                    <div id="connection-status" class="flex items-center">
                        <span class="pulse-dot w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                        <span class="text-sm text-gray-600">Connecting...</span>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <button id="toggle-monitoring" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                        <i class="fas fa-play mr-2"></i>Start Monitoring
                    </button>
                    <button id="config-btn" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition">
                        <i class="fas fa-cog"></i>
                    </button>
                </div>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="metric-card bg-white rounded-lg shadow p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Total Followers</p>
                        <p id="total-followers" class="text-2xl font-bold text-gray-900">-</p>
                    </div>
                    <div class="bg-blue-100 rounded-full p-3">
                        <i class="fas fa-users text-blue-600"></i>
                    </div>
                </div>
            </div>

            <div class="metric-card bg-white rounded-lg shadow p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Avg Engagement</p>
                        <p id="avg-engagement" class="text-2xl font-bold text-gray-900">-</p>
                    </div>
                    <div class="bg-green-100 rounded-full p-3">
                        <i class="fas fa-heart text-green-600"></i>
                    </div>
                </div>
            </div>

            <div class="metric-card bg-white rounded-lg shadow p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Total Impressions</p>
                        <p id="total-impressions" class="text-2xl font-bold text-gray-900">-</p>
                    </div>
                    <div class="bg-purple-100 rounded-full p-3">
                        <i class="fas fa-eye text-purple-600"></i>
                    </div>
                </div>
            </div>

            <div class="metric-card bg-white rounded-lg shadow p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Active Alerts</p>
                        <p id="active-alerts" class="text-2xl font-bold text-gray-900">0</p>
                    </div>
                    <div class="bg-red-100 rounded-full p-3">
                        <i class="fas fa-exclamation-triangle text-red-600"></i>
                    </div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Real-time Metrics -->
            <div class="lg:col-span-2 space-y-6">
                <!-- Platform Metrics -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h2 class="text-lg font-semibold text-gray-900">Real-Time Metrics</h2>
                    </div>
                    <div class="p-6">
                        <div id="platform-metrics" class="space-y-6">
                            <p class="text-gray-500 text-center py-8">Start monitoring to see real-time metrics</p>
                        </div>
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex justify-between items-center">
                            <h2 class="text-lg font-semibold text-gray-900">Performance Trends</h2>
                            <select id="chart-metric" class="border border-gray-300 rounded px-3 py-1 text-sm">
                                <option value="followers">Followers</option>
                                <option value="engagement">Engagement</option>
                                <option value="impressions">Impressions</option>
                            </select>
                        </div>
                    </div>
                    <div class="p-6">
                        <canvas id="trends-chart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Alerts -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h2 class="text-lg font-semibold text-gray-900">Recent Alerts</h2>
                    </div>
                    <div class="p-6">
                        <div id="alerts-list" class="space-y-3">
                            <p class="text-gray-500 text-center py-4">No recent alerts</p>
                        </div>
                    </div>
                </div>

                <!-- Insights -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h2 class="text-lg font-semibold text-gray-900">Performance Insights</h2>
                    </div>
                    <div class="p-6">
                        <div id="insights-list" class="space-y-3">
                            <p class="text-gray-500 text-center py-4">Start monitoring for insights</p>
                        </div>
                    </div>
                </div>

                <!-- Trending Analysis -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h2 class="text-lg font-semibold text-gray-900">Trending Now</h2>
                    </div>
                    <div class="p-6">
                        <div id="trending-list" class="space-y-3">
                            <p class="text-gray-500 text-center py-4">No trending data</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Configuration Modal -->
    <div id="config-modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div class="mt-3">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Configuration</h3>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Twitter Username</label>
                        <input type="text" id="twitter-username" class="w-full border border-gray-300 rounded px-3 py-2"
                               placeholder="e.g., elonmusk" value="elonmusk">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">LinkedIn Company ID</label>
                        <input type="text" id="linkedin-id" class="w-full border border-gray-300 rounded px-3 py-2"
                               placeholder="e.g., 1441" value="1441">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Update Interval (seconds)</label>
                        <input type="number" id="update-interval" class="w-full border border-gray-300 rounded px-3 py-2"
                               value="60" min="30" max="300">
                    </div>
                </div>
                <div class="flex justify-end space-x-3 mt-6">
                    <button id="cancel-config" class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400">
                        Cancel
                    </button>
                    <button id="save-config" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                        Save Changes
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let socket;
        let monitoring = false;
        let chart = null;

        // Initialize Socket.IO
        function initializeSocket() {
            socket = io();

            socket.on('connect', function() {
                updateConnectionStatus(true);
                console.log('Connected to server');
            });

            socket.on('disconnect', function() {
                updateConnectionStatus(false);
                console.log('Disconnected from server');
            });

            socket.on('analytics_update', function(data) {
                updateDashboard(data);
            });

            socket.on('connected', function(data) {
                console.log(data.message);
                monitoring = data.monitoring;
                updateMonitoringButton();
            });
        }

        // Update connection status indicator
        function updateConnectionStatus(connected) {
            const status = document.getElementById('connection-status');
            const dot = status.querySelector('.pulse-dot');
            const text = status.querySelector('span:last-child');

            if (connected) {
                dot.classList.remove('bg-gray-400');
                dot.classList.add('bg-green-500');
                text.textContent = 'Connected';
                text.classList.remove('text-gray-600');
                text.classList.add('text-green-600');
            } else {
                dot.classList.remove('bg-green-500');
                dot.classList.add('bg-gray-400');
                text.textContent = 'Disconnected';
                text.classList.remove('text-green-600');
                text.classList.add('text-gray-600');
            }
        }

        // Update monitoring button
        function updateMonitoringButton() {
            const btn = document.getElementById('toggle-monitoring');
            if (monitoring) {
                btn.innerHTML = '<i class="fas fa-stop mr-2"></i>Stop Monitoring';
                btn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                btn.classList.add('bg-red-600', 'hover:bg-red-700');
            } else {
                btn.innerHTML = '<i class="fas fa-play mr-2"></i>Start Monitoring';
                btn.classList.remove('bg-red-600', 'hover:bg-red-700');
                btn.classList.add('bg-blue-600', 'hover:bg-blue-700');
            }
        }

        // Toggle monitoring
        document.getElementById('toggle-monitoring').addEventListener('click', async function() {
            try {
                const endpoint = monitoring ? '/api/monitoring/stop' : '/api/monitoring/start';
                const response = await fetch(endpoint, { method: 'POST' });
                const data = await response.json();

                if (data.success) {
                    monitoring = !monitoring;
                    updateMonitoringButton();

                    if (monitoring) {
                        loadInitialData();
                    }
                }
            } catch (error) {
                console.error('Error toggling monitoring:', error);
            }
        });

        // Load initial data
        async function loadInitialData() {
            try {
                // Load analytics summary
                const summaryResponse = await fetch('/api/analytics/summary');
                const summaryData = await summaryResponse.json();

                if (summaryData.success) {
                    updateSummaryCards(summaryData.data);
                }

                // Load insights
                const insightsResponse = await fetch('/api/insights');
                const insightsData = await insightsResponse.json();

                if (insightsData.success) {
                    updateInsights(insightsData.insights);
                    updateTrending(insightsData.trends);
                }

                // Load alerts
                const alertsResponse = await fetch('/api/alerts');
                const alertsData = await alertsResponse.json();

                if (alertsData.success) {
                    updateAlerts(alertsData.data);
                }
            } catch (error) {
                console.error('Error loading initial data:', error);
            }
        }

        // Update dashboard with new data
        function updateDashboard(data) {
            updateSummaryCards(data.summary);
            updateAlerts(data.alerts);
            updateMetrics(data.summary);
        }

        // Update summary cards
        function updateSummaryCards(summary) {
            let totalFollowers = 0;
            let totalEngagement = 0;
            let totalImpressions = 0;
            let engagementCount = 0;

            for (const [platform, metrics] of Object.entries(summary)) {
                if (metrics.followers) {
                    totalFollowers += metrics.followers.value;
                }
                if (metrics.engagement) {
                    totalEngagement += metrics.engagement.value;
                    engagementCount++;
                }
                if (metrics.impressions) {
                    totalImpressions += metrics.impressions.value;
                }
            }

            document.getElementById('total-followers').textContent = totalFollowers.toLocaleString();
            document.getElementById('avg-engagement').textContent =
                engagementCount > 0 ? (totalEngagement / engagementCount).toFixed(1) + '%' : '-';
            document.getElementById('total-impressions').textContent = totalImpressions.toLocaleString();
        }

        // Update metrics display
        function updateMetrics(summary) {
            const container = document.getElementById('platform-metrics');
            container.innerHTML = '';

            for (const [platform, metrics] of Object.entries(summary)) {
                const platformDiv = document.createElement('div');
                platformDiv.className = 'border-b border-gray-200 pb-4 last:border-b-0';

                const platformTitle = document.createElement('h3');
                platformTitle.className = 'text-lg font-medium text-gray-900 mb-4 capitalize';
                platformTitle.innerHTML = `<i class="fab fa-${platform} mr-2"></i>${platform}`;
                platformDiv.appendChild(platformTitle);

                const metricsGrid = document.createElement('div');
                metricsGrid.className = 'grid grid-cols-2 gap-4';

                for (const [metricName, metricData] of Object.entries(metrics)) {
                    const metricDiv = document.createElement('div');
                    metricDiv.className = 'flex justify-between items-center';

                    const trendClass = metricData.trend === 'up' ? 'trend-up' :
                                      metricData.trend === 'down' ? 'trend-down' : 'trend-stable';
                    const trendIcon = metricData.trend === 'up' ? 'fa-arrow-up' :
                                     metricData.trend === 'down' ? 'fa-arrow-down' : 'fa-minus';

                    metricDiv.innerHTML = `
                        <div>
                            <p class="text-sm font-medium text-gray-600">${metricName.replace('_', ' ')}</p>
                            <p class="text-lg font-semibold text-gray-900">${metricData.value.toLocaleString()}</p>
                        </div>
                        <div class="${trendClass} text-sm">
                            <i class="fas ${trendIcon} mr-1"></i>
                            ${metricData.change_percent > 0 ? '+' : ''}${metricData.change_percent}%
                        </div>
                    `;

                    metricsGrid.appendChild(metricDiv);
                }

                platformDiv.appendChild(metricsGrid);
                container.appendChild(platformDiv);
            }
        }

        // Update alerts
        function updateAlerts(alerts) {
            const container = document.getElementById('alerts-list');
            container.innerHTML = '';

            document.getElementById('active-alerts').textContent = alerts.length;

            if (alerts.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-center py-4">No recent alerts</p>';
                return;
            }

            alerts.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert-item border-l-4 border-red-500 bg-red-50 p-3 rounded';

                const alertType = alert.alert_type.replace('_', ' ');
                const timeAgo = new Date(alert.timestamp).toLocaleString();

                alertDiv.innerHTML = `
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="text-sm font-medium text-red-800">${alertType}</p>
                            <p class="text-sm text-red-600">${alert.message}</p>
                            <p class="text-xs text-red-500 mt-1">${timeAgo}</p>
                        </div>
                        <i class="fas fa-exclamation-circle text-red-500"></i>
                    </div>
                `;

                container.appendChild(alertDiv);
            });
        }

        // Update insights
        function updateInsights(insights) {
            const container = document.getElementById('insights-list');
            container.innerHTML = '';

            if (insights.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-center py-4">No insights available</p>';
                return;
            }

            insights.forEach(insight => {
                const insightDiv = document.createElement('div');
                const typeColors = {
                    'success': 'border-green-500 bg-green-50 text-green-800',
                    'warning': 'border-yellow-500 bg-yellow-50 text-yellow-800',
                    'alert': 'border-red-500 bg-red-50 text-red-800'
                };

                const colors = typeColors[insight.type] || typeColors['success'];
                insightDiv.className = `border-l-4 ${colors} p-3 rounded alert-item`;

                const icon = insight.type === 'success' ? 'fa-check-circle' :
                             insight.type === 'warning' ? 'fa-exclamation-triangle' : 'fa-times-circle';

                insightDiv.innerHTML = `
                    <div class="flex items-start">
                        <i class="fas ${icon} mr-2 mt-1"></i>
                        <div>
                            <p class="text-sm font-medium">${insight.message}</p>
                            <p class="text-xs mt-1 opacity-75">${insight.recommendation}</p>
                        </div>
                    </div>
                `;

                container.appendChild(insightDiv);
            });
        }

        // Update trending analysis
        function updateTrending(trends) {
            const container = document.getElementById('trending-list');
            container.innerHTML = '';

            if (Object.keys(trends).length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-center py-4">No trending data</p>';
                return;
            }

            for (const [platform, platformTrends] of Object.entries(trends)) {
                const platformDiv = document.createElement('div');
                platformDiv.className = 'mb-4';

                const title = document.createElement('h4');
                title.className = 'text-sm font-medium text-gray-700 mb-2 capitalize';
                title.innerHTML = `<i class="fab fa-${platform} mr-1"></i>${platform}`;
                platformDiv.appendChild(title);

                platformTrends.slice(0, 3).forEach(trend => {
                    const trendDiv = document.createElement('div');
                    trendDiv.className = 'flex justify-between items-center text-sm py-1';

                    const trendClass = trend.trend === 'up' ? 'trend-up' :
                                      trend.trend === 'down' ? 'trend-down' : 'trend-stable';
                    const trendIcon = trend.trend === 'up' ? 'fa-arrow-up' :
                                     trend.trend === 'down' ? 'fa-arrow-down' : 'fa-minus';

                    trendDiv.innerHTML = `
                        <span class="text-gray-600">${trend.metric.replace('_', ' ')}</span>
                        <span class="${trendClass}">
                            <i class="fas ${trendIcon} mr-1 text-xs"></i>
                            ${trend.change_percent > 0 ? '+' : ''}${trend.change_percent}%
                        </span>
                    `;

                    platformDiv.appendChild(trendDiv);
                });

                container.appendChild(platformDiv);
            }
        }

        // Initialize chart
        function initializeChart() {
            const ctx = document.getElementById('trends-chart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Load chart data
        async function loadChartData() {
            const metric = document.getElementById('chart-metric').value;

            try {
                const response = await fetch(`/api/analytics/history/twitter/${metric}?hours=24`);
                const data = await response.json();

                if (data.success) {
                    updateChart(data.data, metric);
                }
            } catch (error) {
                console.error('Error loading chart data:', error);
            }
        }

        // Update chart
        function updateChart(data, metric) {
            if (!chart) return;

            const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
            const values = data.map(d => d.value);

            chart.data.labels = labels;
            chart.data.datasets = [{
                label: `Twitter ${metric}`,
                data: values,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4
            }];

            chart.update();
        }

        // Configuration modal handlers
        document.getElementById('config-btn').addEventListener('click', function() {
            document.getElementById('config-modal').classList.remove('hidden');
        });

        document.getElementById('cancel-config').addEventListener('click', function() {
            document.getElementById('config-modal').classList.add('hidden');
        });

        document.getElementById('save-config').addEventListener('click', async function() {
            const config = {
                platforms: ['twitter', 'linkedin'],
                entities: {
                    twitter: document.getElementById('twitter-username').value,
                    linkedin: document.getElementById('linkedin-id').value
                },
                update_interval: parseInt(document.getElementById('update-interval').value)
            };

            try {
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });

                const data = await response.json();
                if (data.success) {
                    document.getElementById('config-modal').classList.add('hidden');

                    // Restart monitoring if it was running
                    if (monitoring) {
                        await fetch('/api/monitoring/stop', { method: 'POST' });
                        await fetch('/api/monitoring/start', { method: 'POST' });
                    }
                }
            } catch (error) {
                console.error('Error saving configuration:', error);
            }
        });

        // Chart metric change handler
        document.getElementById('chart-metric').addEventListener('change', loadChartData);

        // Initialize everything when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initializeSocket();
            initializeChart();

            // Load chart data periodically
            setInterval(loadChartData, 60000); // Every minute
        });
    </script>
</body>
</html>
    '''

    # Create templates directory if it doesn't exist
    Path('templates').mkdir(exist_ok=True)

    # Write the template file
    with open('templates/enhanced_dashboard.html', 'w') as f:
        f.write(template_content)

    logger.info("Enhanced dashboard template created")

if __name__ == '__main__':
    # Create the template
    create_enhanced_template()

    # Start the enhanced dashboard
    print("🚀 Starting Enhanced Real-Time Analytics Dashboard")
    print("=" * 60)
    print("📊 Dashboard URL: http://localhost:5001")
    print("🔧 Features:")
    print("   - Real-time social media monitoring")
    print("   - Live metrics updates")
    print("   - Performance insights and recommendations")
    print("   - Trend analysis and alerts")
    print("   - Interactive charts and visualizations")
    print("=" * 60)

    # Start monitoring automatically
    dashboard.start_monitoring()

    # Run the Flask app with Socket.IO
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)