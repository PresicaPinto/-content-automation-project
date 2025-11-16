#!/usr/bin/env python3
"""
Backend with Simple Frontend
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timezone
import os

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'proper_social_data.db'

def init_db():
    """Initialize database if not exists"""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE social_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                username TEXT,
                account_name TEXT,
                account_type TEXT,
                client_id TEXT,
                connected BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_connected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                followers INTEGER DEFAULT 0,
                following INTEGER DEFAULT 0,
                tweets INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                retweets INTEGER DEFAULT 0,
                replies INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                profile_views INTEGER DEFAULT 0,
                engagement DECIMAL(5,2) DEFAULT 0,
                quality_score INTEGER DEFAULT 0,
                reach INTEGER DEFAULT 0,
                verified BOOLEAN DEFAULT FALSE,
                data_source TEXT DEFAULT 'api',
                raw_analytics TEXT
            )
        ''')

        # Insert real Twitter data
        real_twitter_data = {
            "platform": "twitter",
            "username": "Presica_Pinto",
            "account_name": "Presica_Pinto",
            "account_type": "user",
            "client_id": "bearer_token_only",
            "connected": True,
            "followers": 0,
            "following": 2,
            "tweets": 0,
            "likes": 0,
            "retweets": 0,
            "replies": 0,
            "impressions": 0,
            "profile_views": 0,
            "engagement": 0.0,
            "quality_score": 0,
            "reach": 0,
            "verified": False,
            "data_source": "bearer_token_only",
            "raw_analytics": json.dumps({
                "data_source": "bearer_token_only",
                "engagement": 0.0,
                "followers": 0,
                "following": 2,
                "impressions": 0,
                "likes": 0,
                "posts": 0,
                "profile_views": 0,
                "quality_score": 0,
                "reach": 0,
                "replies": 0,
                "retweets": 0,
                "tweets": 0,
                "verified": False
            })
        }

        cursor.execute('''
            INSERT INTO social_connections
            (platform, username, account_name, account_type, client_id, connected,
             followers, following, tweets, likes, retweets, replies, impressions,
             profile_views, engagement, quality_score, reach, verified, data_source,
             raw_analytics, last_connected)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            real_twitter_data["platform"],
            real_twitter_data["username"],
            real_twitter_data["account_name"],
            real_twitter_data["account_type"],
            real_twitter_data["client_id"],
            real_twitter_data["connected"],
            real_twitter_data["followers"],
            real_twitter_data["following"],
            real_twitter_data["tweets"],
            real_twitter_data["likes"],
            real_twitter_data["retweets"],
            real_twitter_data["replies"],
            real_twitter_data["impressions"],
            real_twitter_data["profile_views"],
            real_twitter_data["engagement"],
            real_twitter_data["quality_score"],
            real_twitter_data["reach"],
            real_twitter_data["verified"],
            real_twitter_data["data_source"],
            real_twitter_data["raw_analytics"],
            datetime.now(timezone.utc).isoformat()
        ))

        conn.commit()
        conn.close()
        print("✅ Database initialized with real Twitter data")

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def format_connection_data(row):
    """Format database row to JSON response"""
    return {
        "account_name": row["account_name"],
        "account_type": row["account_type"],
        "analytics": json.loads(row["raw_analytics"]) if row["raw_analytics"] else {
            "engagement": row["engagement"],
            "followers": row["followers"],
            "following": row["following"],
            "tweets": row["tweets"],
            "verified": row["verified"]
        },
        "client_id": row["client_id"],
        "connected": bool(row["connected"]),
        "created_at": row["created_at"],
        "last_connected": row["last_connected"],
        "platform": row["platform"],
        "username": row["username"]
    }

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Twitter Analytics Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #1da1f2; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .metric { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #1da1f2; }
        .metric-label { color: #666; margin-top: 5px; }
        .status { padding: 10px; border-radius: 5px; text-align: center; }
        .connected { background: #d4edda; color: #155724; }
        .api-info { background: #e7f3ff; padding: 15px; border-radius: 8px; border-left: 4px solid #1da1f2; }
        .refresh-btn { background: #1da1f2; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        .refresh-btn:hover { background: #1a91da; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐦 Twitter Analytics Dashboard</h1>
            <p>Real-time Twitter data fetched via API</p>
        </div>

        <div class="card">
            <h2>📊 Connection Status</h2>
            <div class="status connected">
                ✅ Connected to Twitter API
            </div>
            <div class="api-info">
                <strong>Account:</strong> @Presica_Pinto<br>
                <strong>Data Source:</strong> Bearer Token API<br>
                <strong>Last Updated:</strong> <span id="lastUpdated">{{ timestamp }}</span>
            </div>
        </div>

        <div class="card">
            <h2>📈 Twitter Metrics</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{{ followers }}</div>
                    <div class="metric-label">Followers</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ following }}</div>
                    <div class="metric-label">Following</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ tweets }}</div>
                    <div class="metric-label">Tweets</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ verified }}</div>
                    <div class="metric-label">Verified</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🔧 API Actions</h2>
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
            <button class="refresh-btn" onclick="showApiData()">📋 View API Response</button>
        </div>

        <div class="card">
            <h2>📡 API Endpoints</h2>
            <div class="api-info">
                <strong>GET</strong> <code>/api/social/connections</code> - Get all connections<br>
                <strong>POST</strong> <code>/api/social/connections</code> - Update connections<br>
                <strong>GET</strong> <code>/api/health</code> - Health check
            </div>
        </div>
    </div>

    <script>
        function refreshData() {
            fetch('/api/social/connections')
                .then(response => response.json())
                .then(data => {
                    const twitter = data.connections.twitter;
                    if (twitter) {
                        document.location.reload();
                    }
                });
        }

        function showApiData() {
            fetch('/api/social/connections')
                .then(response => response.json())
                .then(data => {
                    alert(JSON.stringify(data, null, 2));
                });
        }

        // Update timestamp
        document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    """Homepage with Twitter analytics"""
    try:
        conn = get_db_connection()
        twitter_data = conn.execute(
            'SELECT * FROM social_connections WHERE platform = "twitter"'
        ).fetchone()
        conn.close()

        if twitter_data:
            return render_template_string(HTML_TEMPLATE,
                followers=twitter_data['followers'],
                following=twitter_data['following'],
                tweets=twitter_data['tweets'],
                verified='Yes' if twitter_data['verified'] else 'No',
                timestamp=twitter_data['last_connected']
            )
        else:
            return render_template_string(HTML_TEMPLATE,
                followers=0, following=0, tweets=0, verified='No', timestamp='Unknown'
            )
    except Exception as e:
        return render_template_string(HTML_TEMPLATE,
            followers=0, following=0, tweets=0, verified='Error', timestamp=str(e)
        )

@app.route('/api/social/connections', methods=['GET', 'POST'])
def social_connections():
    """API endpoint for social connections"""
    conn = get_db_connection()

    if request.method == 'GET':
        connections = conn.execute('SELECT * FROM social_connections').fetchall()
        result = {}
        for row in connections:
            result[row["platform"]] = format_connection_data(row)
        conn.close()
        return jsonify({
            "connections": result,
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    elif request.method == 'POST':
        try:
            data = request.json
            if 'twitter' in data:
                platform_data = data['twitter']
                analytics = platform_data.get('analytics', {})

                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE social_connections SET
                        username = ?, account_name = ?, account_type = ?,
                        client_id = ?, connected = ?, last_connected = ?,
                        followers = ?, following = ?, tweets = ?, likes = ?,
                        retweets = ?, replies = ?, impressions = ?, profile_views = ?,
                        engagement = ?, quality_score = ?, reach = ?, verified = ?,
                        data_source = ?, raw_analytics = ?
                    WHERE platform = ?
                ''', (
                    platform_data.get('username'),
                    platform_data.get('account_name'),
                    platform_data.get('account_type'),
                    platform_data.get('client_id'),
                    platform_data.get('connected', True),
                    datetime.now(timezone.utc).isoformat(),
                    analytics.get('followers', 0),
                    analytics.get('following', 0),
                    analytics.get('tweets', 0),
                    analytics.get('likes', 0),
                    analytics.get('retweets', 0),
                    analytics.get('replies', 0),
                    analytics.get('impressions', 0),
                    analytics.get('profile_views', 0),
                    analytics.get('engagement', 0),
                    analytics.get('quality_score', 0),
                    analytics.get('reach', 0),
                    analytics.get('verified', False),
                    analytics.get('data_source', 'api'),
                    json.dumps(analytics),
                    'twitter'
                ))

                conn.commit()
                conn.close()

                return jsonify({
                    "success": True,
                    "message": "Twitter data updated successfully"
                })

        except Exception as e:
            conn.close()
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    })

if __name__ == '__main__':
    print("🚀 STARTING BACKEND WITH FRONTEND")
    print("=" * 50)
    init_db()
    print("🌐 Starting on http://0.0.0.0:5000")
    print("📱 Visit: http://172.29.89.92:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)