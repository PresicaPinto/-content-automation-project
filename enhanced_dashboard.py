from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta
import sqlite3
import logging
import subprocess
import threading
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TopicManager:
    """Manage topics for content generation"""

    def __init__(self, topics_file='topics.json'):
        self.topics_file = topics_file
        self.load_topics()

    def load_topics(self):
        """Load topics from file"""
        try:
            with open(self.topics_file, 'r') as f:
                self.topics = json.load(f)
        except FileNotFoundError:
            self.topics = []
            self.save_topics()

    def save_topics(self):
        """Save topics to file"""
        with open(self.topics_file, 'w') as f:
            json.dump(self.topics, f, indent=2)

    def add_topic(self, topic_data):
        """Add a new topic"""
        topic_data['id'] = len(self.topics) + 1
        topic_data['created_date'] = datetime.now().isoformat()
        topic_data['status'] = 'pending'
        self.topics.append(topic_data)
        self.save_topics()
        return topic_data

    def get_topics(self):
        """Get all topics"""
        return self.topics

    def update_topic_status(self, topic_id, status):
        """Update topic status"""
        for topic in self.topics:
            if topic.get('id') == topic_id:
                topic['status'] = status
                if status == 'completed':
                    topic['completed_date'] = datetime.now().isoformat()
                self.save_topics()
                return True
        return False

class ContentGenerator:
    """Handle content generation"""

    def __init__(self):
        self.generation_status = 'idle'
        self.generation_progress = 0

    def generate_content(self, num_posts=5):
        """Generate content from topics"""
        try:
            # Run content generation
            result = subprocess.run([
                'python', 'main.py', 'linkedin_batch', str(num_posts)
            ], capture_output=True, text=True, cwd='.')

            if result.returncode == 0:
                return {'success': True, 'message': 'Content generated successfully!'}
            else:
                return {'success': False, 'message': result.stderr}

        except Exception as e:
            return {'success': False, 'message': str(e)}

class MetricsDatabase:
    """Database handler for metrics"""

    def __init__(self, db_path="outputs/metrics.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize database"""
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
            conn.commit()

    def get_metrics_summary(self, days=30):
        """Get metrics summary"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT platform, COUNT(*) as total_posts,
                       SUM(views) as total_views, SUM(likes) as total_likes,
                       AVG(engagement_rate) as avg_engagement
                FROM metrics
                WHERE date >= date('now', '-{} days')
                GROUP BY platform
            '''.format(days))
            return [dict(row) for row in cursor.fetchall()]

# Initialize managers
topic_manager = TopicManager()
content_generator = ContentGenerator()
metrics_db = MetricsDatabase()

@app.route('/')
def dashboard():
    """Main dashboard with topic management"""
    return render_template('enhanced_dashboard.html')

@app.route('/api/topics')
def get_topics():
    """Get all topics"""
    return jsonify(topic_manager.get_topics())

@app.route('/api/topics/add', methods=['POST'])
def add_topic():
    """Add a new topic"""
    try:
        data = request.json
        required_fields = ['topic', 'points', 'style']

        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': 'Missing required fields'})

        topic = topic_manager.add_topic(data)
        return jsonify({'success': True, 'topic': topic})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/topics/<int:topic_id>/generate', methods=['POST'])
def generate_content_for_topic(topic_id):
    """Generate content for specific topic"""
    try:
        # Update topic status
        topic_manager.update_topic_status(topic_id, 'generating')

        # Generate content
        result = content_generator.generate_content(3)

        if result['success']:
            topic_manager.update_topic_status(topic_id, 'completed')
            return jsonify({'success': True, 'message': 'Content generated successfully!'})
        else:
            topic_manager.update_topic_status(topic_id, 'failed')
            return jsonify({'success': False, 'message': result['message']})

    except Exception as e:
        topic_manager.update_topic_status(topic_id, 'failed')
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/generate-batch', methods=['POST'])
def generate_batch_content():
    """Generate content for multiple topics"""
    try:
        data = request.json
        num_posts = data.get('num_posts', 5)

        # Generate content
        result = content_generator.generate_content(num_posts)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/metrics/summary')
def get_metrics_summary():
    """Get metrics summary"""
    data = metrics_db.get_metrics_summary()
    return jsonify(data)

@app.route('/api/content/status')
def get_content_status():
    """Get content generation status"""
    # Check if content files exist
    linkedin_exists = os.path.exists('outputs/content_calendar.json')
    twitter_exists = os.path.exists('outputs/twitter_calendar.json')

    if linkedin_exists:
        with open('outputs/content_calendar.json', 'r') as f:
            linkedin_posts = json.load(f)
    else:
        linkedin_posts = []

    if twitter_exists:
        with open('outputs/twitter_calendar.json', 'r') as f:
            twitter_posts = json.load(f)
    else:
        twitter_posts = []

    return jsonify({
        'linkedin_posts': len(linkedin_posts),
        'twitter_posts': len(twitter_posts),
        'last_generated': os.path.getmtime('outputs/content_calendar.json') if linkedin_exists else None
    })

# Create enhanced dashboard template
dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Automation Control Center</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #334155;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1rem;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e2e8f0;
        }

        .tab {
            padding: 1rem 2rem;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            color: #64748b;
            transition: all 0.3s;
        }

        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .action-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }

        .action-card:hover {
            transform: translateY(-2px);
        }

        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-1px);
        }

        .btn-success {
            background: #10b981;
            color: white;
        }

        .btn-secondary {
            background: #64748b;
            color: white;
        }

        .topics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }

        .topic-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }

        .topic-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1e293b;
        }

        .topic-points {
            margin-bottom: 1rem;
        }

        .topic-point {
            padding: 0.25rem 0;
            color: #64748b;
            font-size: 0.9rem;
        }

        .topic-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
        }

        .topic-style {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: #f1f5f9;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .topic-status {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .status-pending { background: #fef3c7; color: #92400e; }
        .status-generating { background: #dbeafe; color: #1e40af; }
        .status-completed { background: #d1fae5; color: #065f46; }
        .status-failed { background: #fee2e2; color: #991b1b; }

        .add-topic-form {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #374151;
        }

        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 1rem;
        }

        .form-group textarea {
            resize: vertical;
            min-height: 100px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: #64748b;
            font-size: 0.9rem;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }

        .modal-content {
            background: white;
            margin: 5% auto;
            padding: 2rem;
            border-radius: 12px;
            width: 90%;
            max-width: 500px;
        }

        .notification {
            position: fixed;
            top: 2rem;
            right: 2rem;
            padding: 1rem 1.5rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border-left: 4px solid #10b981;
            z-index: 1001;
            display: none;
        }

        .notification.error {
            border-left-color: #ef4444;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Content Automation Control Center</h1>
        <p>Generate content, manage topics, and track performance - all in one place</p>
    </div>

    <div class="container">
        <div class="tabs">
            <button class="tab active" onclick="showTab('dashboard')">📊 Dashboard</button>
            <button class="tab" onclick="showTab('topics')">📝 Topics</button>
            <button class="tab" onclick="showTab('generate')">⚡ Generate</button>
            <button class="tab" onclick="showTab('metrics')">📈 Metrics</button>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="linkedin-count">-</div>
                    <div class="stat-label">LinkedIn Posts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="twitter-count">-</div>
                    <div class="stat-label">Twitter Threads</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="topics-count">-</div>
                    <div class="stat-label">Topics Available</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="status-indicator">✅</div>
                    <div class="stat-label">System Status</div>
                </div>
            </div>

            <div class="quick-actions">
                <div class="action-card">
                    <h3>⚡ Quick Generate</h3>
                    <p>Generate 5 posts immediately</p>
                    <button class="btn btn-primary" onclick="quickGenerate()">Generate Now</button>
                </div>
                <div class="action-card">
                    <h3>📝 Add Topic</h3>
                    <p>Add a new topic for content generation</p>
                    <button class="btn btn-secondary" onclick="showAddTopic()">Add Topic</button>
                </div>
                <div class="action-card">
                    <h3>📊 View Content</h3>
                    <p>Check generated content</p>
                    <button class="btn btn-secondary" onclick="viewContent()">View Content</button>
                </div>
                <div class="action-card">
                    <h3>🚀 Start Scheduler</h3>
                    <p>Launch the posting scheduler</p>
                    <button class="btn btn-success" onclick="startScheduler()">Start Scheduler</button>
                </div>
            </div>
        </div>

        <!-- Topics Tab -->
        <div id="topics" class="tab-content">
            <div class="add-topic-form">
                <h3>➕ Add New Topic</h3>
                <form id="addTopicForm">
                    <div class="form-group">
                        <label>Topic Title</label>
                        <input type="text" id="topicTitle" required>
                    </div>
                    <div class="form-group">
                        <label>Key Points (one per line)</label>
                        <textarea id="topicPoints" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Style</label>
                        <select id="topicStyle">
                            <option value="educational">Educational</option>
                            <option value="case_study">Case Study</option>
                            <option value="story">Story</option>
                            <option value="insight">Insight</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Add Topic</button>
                </form>
            </div>

            <h3>📋 Available Topics</h3>
            <div class="topics-grid" id="topicsGrid">
                <div class="loading">Loading topics...</div>
            </div>
        </div>

        <!-- Generate Tab -->
        <div id="generate" class="tab-content">
            <div class="action-card">
                <h3>🚀 Batch Content Generation</h3>
                <p>Generate multiple posts at once from your topic pool</p>
                <div class="form-group">
                    <label>Number of posts to generate:</label>
                    <input type="number" id="batchCount" value="10" min="1" max="50">
                </div>
                <button class="btn btn-primary" onclick="generateBatch()">Generate Content</button>
            </div>

            <div id="generationStatus" style="display: none;">
                <h3>⏳ Generation Progress</h3>
                <div class="stat-card">
                    <div class="stat-number" id="progressIndicator">0%</div>
                    <div class="stat-label">Progress</div>
                </div>
            </div>
        </div>

        <!-- Metrics Tab -->
        <div id="metrics" class="tab-content">
            <h3>📈 Performance Metrics</h3>
            <div class="stats-grid" id="metricsGrid">
                <div class="loading">Loading metrics...</div>
            </div>
        </div>
    </div>

    <!-- Notification -->
    <div id="notification" class="notification">
        <span id="notificationText"></span>
    </div>

    <script>
        let currentTopics = [];

        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');

            // Load tab-specific data
            if (tabName === 'topics') loadTopics();
            if (tabName === 'metrics') loadMetrics();
            if (tabName === 'dashboard') loadDashboard();
        }

        function showNotification(message, isError = false) {
            const notification = document.getElementById('notification');
            const notificationText = document.getElementById('notificationText');

            notificationText.textContent = message;
            notification.className = isError ? 'notification error' : 'notification';
            notification.style.display = 'block';

            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }

        async function loadDashboard() {
            // Load content status
            const response = await fetch('/api/content/status');
            const data = await response.json();

            document.getElementById('linkedin-count').textContent = data.linkedin_posts;
            document.getElementById('twitter-count').textContent = data.twitter_posts;

            // Load topics count
            const topicsResponse = await fetch('/api/topics');
            const topics = await topicsResponse.json();
            document.getElementById('topics-count').textContent = topics.length;
        }

        async function loadTopics() {
            const response = await fetch('/api/topics');
            currentTopics = await response.json();

            const topicsGrid = document.getElementById('topicsGrid');

            topicsGrid.innerHTML = currentTopics.map(topic => `
                <div class="topic-card">
                    <div class="topic-title">${topic.topic}</div>
                    <div class="topic-points">
                        ${topic.points.map(point => `<div class="topic-point">• ${point}</div>`).join('')}
                    </div>
                    <div class="topic-meta">
                        <span class="topic-style">${topic.style}</span>
                        <span class="topic-status status-${topic.status || 'pending'}">${topic.status || 'pending'}</span>
                    </div>
                    <div style="margin-top: 1rem;">
                        <button class="btn btn-primary" onclick="generateForTopic(${topic.id || topic.topic.length})">Generate</button>
                    </div>
                </div>
            `).join('');
        }

        async function loadMetrics() {
            const response = await fetch('/api/metrics/summary');
            const metrics = await response.json();

            const metricsGrid = document.getElementById('metricsGrid');

            if (metrics.length === 0) {
                metricsGrid.innerHTML = '<div class="stat-card"><p>No metrics data available yet</p></div>';
                return;
            }

            metricsGrid.innerHTML = metrics.map(metric => `
                <div class="stat-card">
                    <div class="stat-number">${metric.total_posts}</div>
                    <div class="stat-label">${metric.platform.toUpperCase()} Posts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${formatNumber(metric.total_views)}</div>
                    <div class="stat-label">${metric.platform.toUpperCase()} Views</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${formatNumber(metric.total_likes)}</div>
                    <div class="stat-label">${metric.platform.toUpperCase()} Likes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${(metric.avg_engagement || 0).toFixed(1)}%</div>
                    <div class="stat-label">${metric.platform.toUpperCase()} Engagement</div>
                </div>
            `).join('');
        }

        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toString();
        }

        // Add topic form handler
        document.getElementById('addTopicForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const topicData = {
                topic: document.getElementById('topicTitle').value,
                points: document.getElementById('topicPoints').value.split('\\n').filter(p => p.trim()),
                style: document.getElementById('topicStyle').value
            };

            const response = await fetch('/api/topics/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(topicData)
            });

            const result = await response.json();

            if (result.success) {
                showNotification('Topic added successfully!');
                document.getElementById('addTopicForm').reset();
                loadTopics();
            } else {
                showNotification(result.message, true);
            }
        });

        async function quickGenerate() {
            showNotification('Starting content generation...');
            const response = await fetch('/api/generate-batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ num_posts: 5 })
            });

            const result = await response.json();

            if (result.success) {
                showNotification('Content generated successfully!');
                loadDashboard();
            } else {
                showNotification(result.message, true);
            }
        }

        async function generateBatch() {
            const count = document.getElementById('batchCount').value;

            document.getElementById('generationStatus').style.display = 'block';

            const response = await fetch('/api/generate-batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ num_posts: parseInt(count) })
            });

            const result = await response.json();

            if (result.success) {
                showNotification(`${count} posts generated successfully!`);
                loadDashboard();
            } else {
                showNotification(result.message, true);
            }

            document.getElementById('generationStatus').style.display = 'none';
        }

        function showAddTopic() {
            showTab('topics');
        }

        function viewContent() {
            showNotification('Opening content folder...');
            // In production, this could open a modal with content preview
        }

        function startScheduler() {
            showNotification('Scheduler starting... (This would start the background service)');
        }

        function generateForTopic(topicId) {
            showNotification(`Generating content for topic ${topicId}...`);
        }

        // Initialize dashboard on load
        document.addEventListener('DOMContentLoaded', loadDashboard);
    </script>
</body>
</html>
"""

# Write the enhanced template
with open('templates/enhanced_dashboard.html', 'w') as f:
    f.write(dashboard_template)

if __name__ == '__main__':
    print("🚀 Enhanced Content Automation Dashboard")
    print("📊 Features: Topic Management, Content Generation, Metrics")
    print("🌐 Available at: http://localhost:5000")
    print("\n🎯 New Features:")
    print("   ✅ Add topics via web interface")
    print("   ✅ Generate content from topics")
    print("   ✅ Track topic status (pending, generating, completed)")
    print("   ✅ Quick actions for common tasks")
    print("   ✅ Real-time content status")

    app.run(debug=False, host='0.0.0.0', port=5000)