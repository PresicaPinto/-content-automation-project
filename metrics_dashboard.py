from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta
import sqlite3
import logging
from typing import Dict, List, Optional
import csv

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricsDatabase:
    """Database handler for metrics storage and retrieval"""

    def __init__(self, db_path: str = "outputs/metrics.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize the metrics database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    post_number INTEGER,
                    topic TEXT,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT UNIQUE,
                    platform TEXT,
                    topic TEXT,
                    publish_date TEXT,
                    status TEXT,
                    total_views INTEGER DEFAULT 0,
                    total_likes INTEGER DEFAULT 0,
                    total_comments INTEGER DEFAULT 0,
                    total_shares INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()

    def insert_metrics(self, metrics_data: dict):
        """Insert new metrics data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO metrics
                (date, platform, post_number, topic, views, likes, comments, shares, engagement_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics_data['date'],
                metrics_data['platform'],
                metrics_data.get('post_number'),
                metrics_data.get('topic'),
                metrics_data.get('views', 0),
                metrics_data.get('likes', 0),
                metrics_data.get('comments', 0),
                metrics_data.get('shares', 0),
                float(metrics_data.get('engagement_rate', 0).rstrip('%'))
            ))
            conn.commit()

    def get_metrics_summary(self, days: int = 30) -> List[dict]:
        """Get metrics summary for the last N days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT
                    platform,
                    COUNT(*) as total_posts,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares,
                    AVG(engagement_rate) as avg_engagement_rate,
                    date
                FROM metrics
                WHERE date >= date('now', '-{} days')
                GROUP BY platform, date
                ORDER BY date DESC
            '''.format(days))

            return [dict(row) for row in cursor.fetchall()]

    def get_top_performing_content(self, limit: int = 10) -> List[dict]:
        """Get top performing content by engagement"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT
                    topic,
                    platform,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares,
                    AVG(engagement_rate) as avg_engagement_rate,
                    COUNT(*) as post_count
                FROM metrics
                GROUP BY topic, platform
                ORDER BY avg_engagement_rate DESC
                LIMIT ?
            ''', (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def get_platform_comparison(self) -> dict:
        """Compare performance across platforms"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            platforms = {}
            for platform in ['linkedin', 'twitter']:
                cursor = conn.execute('''
                    SELECT
                        COUNT(*) as total_posts,
                        SUM(views) as total_views,
                        SUM(likes) as total_likes,
                        SUM(comments) as total_comments,
                        SUM(shares) as total_shares,
                        AVG(engagement_rate) as avg_engagement_rate
                    FROM metrics
                    WHERE platform = ?
                ''', (platform,))

                result = cursor.fetchone()
                platforms[platform] = dict(result) if result else {
                    'total_posts': 0,
                    'total_views': 0,
                    'total_likes': 0,
                    'total_comments': 0,
                    'total_shares': 0,
                    'avg_engagement_rate': 0.0
                }

            return platforms

class MetricsDashboard:
    """Main dashboard application"""

    def __init__(self):
        self.db = MetricsDatabase()
        self.load_csv_metrics()

    def load_csv_metrics(self):
        """Load existing CSV metrics into database"""
        csv_file = 'outputs/metrics.csv'
        if not os.path.exists(csv_file):
            return

        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Platform') and row.get('Views'):
                        self.db.insert_metrics({
                            'date': row.get('Date', datetime.now().strftime('%Y-%m-%d')),
                            'platform': row['Platform'].lower(),
                            'post_number': int(row.get('Post_Number', 0)),
                            'topic': row.get('Topic', ''),
                            'views': int(row.get('Views', 0)),
                            'likes': int(row.get('Likes', 0)),
                            'comments': int(row.get('Comments', 0)),
                            'shares': int(row.get('Shares', 0)),
                            'engagement_rate': row.get('Engagement_Rate', '0.0%')
                        })

            logger.info("Loaded CSV metrics into database")
        except Exception as e:
            logger.error(f"Error loading CSV metrics: {e}")

dashboard = MetricsDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/metrics/summary')
def get_metrics_summary():
    """Get metrics summary for dashboard"""
    days = int(request.args.get('days', 30))
    data = dashboard.db.get_metrics_summary(days)
    return jsonify(data)

@app.route('/api/metrics/top-content')
def get_top_content():
    """Get top performing content"""
    limit = int(request.args.get('limit', 10))
    data = dashboard.db.get_top_performing_content(limit)
    return jsonify(data)

@app.route('/api/metrics/platform-comparison')
def get_platform_comparison():
    """Get platform comparison data"""
    data = dashboard.db.get_platform_comparison()
    return jsonify(data)

@app.route('/api/metrics/add', methods=['POST'])
def add_metrics():
    """Add new metrics data"""
    try:
        data = request.json
        dashboard.db.insert_metrics(data)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error adding metrics: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/scheduler/status')
def get_scheduler_status():
    """Get scheduler status if running"""
    try:
        # Check if scheduler state file exists
        state_file = 'outputs/scheduler_state.json'
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)

            return jsonify({
                'has_scheduler': True,
                'state': state
            })
        else:
            return jsonify({
                'has_scheduler': False,
                'message': 'Scheduler state file not found'
            })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/content/calendar')
def get_content_calendar():
    """Get content calendar data"""
    try:
        calendars = {}

        # Load LinkedIn calendar
        linkedin_file = 'outputs/content_calendar.json'
        if os.path.exists(linkedin_file):
            with open(linkedin_file, 'r') as f:
                calendars['linkedin'] = json.load(f)

        # Load Twitter calendar
        twitter_file = 'outputs/twitter_calendar.json'
        if os.path.exists(twitter_file):
            with open(twitter_file, 'r') as f:
                calendars['twitter'] = json.load(f)

        return jsonify(calendars)
    except Exception as e:
        return jsonify({'error': str(e)})

# Create templates directory and dashboard template
os.makedirs('templates', exist_ok=True)

dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Automation Metrics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2rem;
            font-weight: 600;
        }

        .header p {
            opacity: 0.9;
            margin-top: 0.5rem;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }

        .stat-card:hover {
            transform: translateY(-2px);
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .chart-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .chart-card h3 {
            margin-bottom: 1rem;
            color: #333;
        }

        .chart-container {
            position: relative;
            height: 300px;
        }

        .top-content {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .content-item {
            padding: 1rem;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .content-item:last-child {
            border-bottom: none;
        }

        .content-title {
            font-weight: 500;
            color: #333;
        }

        .content-platform {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-left: 0.5rem;
        }

        .platform-linkedin {
            background: #0077b5;
            color: white;
        }

        .platform-twitter {
            background: #1da1f2;
            color: white;
        }

        .engagement-rate {
            font-weight: 600;
            color: #28a745;
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: #666;
        }

        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            transition: background 0.2s;
        }

        .refresh-btn:hover {
            background: #5a6fd8;
        }

        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }

        .status-running {
            background: #28a745;
        }

        .status-stopped {
            background: #dc3545;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Content Automation Dashboard</h1>
        <p>Real-time metrics and performance analytics for your content automation system</p>
    </div>

    <div class="container">
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>

        <div id="scheduler-status"></div>

        <div class="stats-grid" id="stats-grid">
            <div class="loading">Loading metrics...</div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <h3>📊 Engagement Over Time</h3>
                <div class="chart-container">
                    <canvas id="engagement-chart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>📈 Platform Performance</h3>
                <div class="chart-container">
                    <canvas id="platform-chart"></canvas>
                </div>
            </div>
        </div>

        <div class="top-content">
            <h3>🏆 Top Performing Content</h3>
            <div id="top-content-list">
                <div class="loading">Loading top content...</div>
            </div>
        </div>
    </div>

    <script>
        let engagementChart, platformChart;

        async function fetchData(endpoint) {
            try {
                const response = await fetch(`/api/${endpoint}`);
                return await response.json();
            } catch (error) {
                console.error(`Error fetching ${endpoint}:`, error);
                return null;
            }
        }

        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toString();
        }

        function updateStatsGrid(platformData) {
            const statsGrid = document.getElementById('stats-grid');

            let totalStats = {
                posts: 0,
                views: 0,
                likes: 0,
                engagement: 0
            };

            Object.entries(platformData).forEach(([platform, stats]) => {
                totalStats.posts += stats.total_posts;
                totalStats.views += stats.total_views;
                totalStats.likes += stats.total_likes;
                totalStats.engagement += stats.avg_engagement_rate;
            });

            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${totalStats.posts}</div>
                    <div class="stat-label">Total Posts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${formatNumber(totalStats.views)}</div>
                    <div class="stat-label">Total Views</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${formatNumber(totalStats.likes)}</div>
                    <div class="stat-label">Total Likes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${(totalStats.engagement / 2).toFixed(1)}%</div>
                    <div class="stat-label">Avg Engagement</div>
                </div>
            `;
        }

        function updateEngagementChart(data) {
            const ctx = document.getElementById('engagement-chart').getContext('2d');

            const dates = [...new Set(data.map(d => d.date))].sort().reverse().slice(0, 14);
            const linkedinData = dates.map(date => {
                const item = data.find(d => d.date === date && d.platform === 'linkedin');
                return item ? parseFloat(item.avg_engagement_rate) : 0;
            });
            const twitterData = dates.map(date => {
                const item = data.find(d => d.date === date && d.platform === 'twitter');
                return item ? parseFloat(item.avg_engagement_rate) : 0;
            });

            if (engagementChart) {
                engagementChart.destroy();
            }

            engagementChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates.reverse(),
                    datasets: [{
                        label: 'LinkedIn',
                        data: linkedinData.reverse(),
                        borderColor: '#0077b5',
                        backgroundColor: 'rgba(0, 119, 181, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Twitter',
                        data: twitterData.reverse(),
                        borderColor: '#1da1f2',
                        backgroundColor: 'rgba(29, 161, 242, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }

        function updatePlatformChart(platformData) {
            const ctx = document.getElementById('platform-chart').getContext('2d');

            if (platformChart) {
                platformChart.destroy();
            }

            platformChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['LinkedIn', 'Twitter'],
                    datasets: [{
                        label: 'Total Views',
                        data: [platformData.linkedin?.total_views || 0, platformData.twitter?.total_views || 0],
                        backgroundColor: ['#0077b5', '#1da1f2']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return formatNumber(value);
                                }
                            }
                        }
                    }
                }
            });
        }

        function updateTopContent(content) {
            const contentList = document.getElementById('top-content-list');

            contentList.innerHTML = content.map(item => `
                <div class="content-item">
                    <div>
                        <div class="content-title">${item.topic}</div>
                        <span class="content-platform platform-${item.platform}">${item.platform}</span>
                    </div>
                    <div class="engagement-rate">${parseFloat(item.avg_engagement_rate).toFixed(1)}%</div>
                </div>
            `).join('');
        }

        async function updateSchedulerStatus() {
            const status = await fetchData('scheduler/status');
            const statusDiv = document.getElementById('scheduler-status');

            if (status && status.has_scheduler) {
                const pending = Object.values(status.state.scheduled_posts || {}).filter(p => p.status === 'pending').length;
                statusDiv.innerHTML = `
                    <div class="stat-card">
                        <span class="status-indicator status-running"></span>
                        Scheduler Running
                        <small style="margin-left: 1rem;">${pending} posts pending</small>
                    </div>
                `;
            } else {
                statusDiv.innerHTML = `
                    <div class="stat-card">
                        <span class="status-indicator status-stopped"></span>
                        Scheduler Not Running
                    </div>
                `;
            }
        }

        async function refreshData() {
            console.log('Refreshing dashboard data...');

            // Update scheduler status
            await updateSchedulerStatus();

            // Fetch platform comparison
            const platformData = await fetchData('metrics/platform-comparison');
            if (platformData) {
                updateStatsGrid(platformData);
                updatePlatformChart(platformData);
            }

            // Fetch metrics summary
            const summaryData = await fetchData('metrics/summary?days=30');
            if (summaryData) {
                updateEngagementChart(summaryData);
            }

            // Fetch top content
            const topContent = await fetchData('metrics/top-content?limit=5');
            if (topContent) {
                updateTopContent(topContent);
            }
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', refreshData);

        // Auto-refresh every 5 minutes
        setInterval(refreshData, 300000);
    </script>
</body>
</html>
"""

# Write the template
with open('templates/dashboard.html', 'w') as f:
    f.write(dashboard_template)

if __name__ == '__main__':
    print("🚀 Starting Content Automation Metrics Dashboard")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔄 Auto-refresh enabled (every 5 minutes)")
    print("\nPress Ctrl+C to stop the server")

    app.run(debug=False, host='0.0.0.0', port=5000)