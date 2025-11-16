#!/usr/bin/env python3
"""
EXAMPLE: How your backend should look after Option A fix
This is what your backend code should become
"""

# ==============================================================
# THIS IS AN EXAMPLE - SHOWS WHAT YOUR BACKEND SHOULD LOOK LIKE
# ==============================================================

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ==============================================================
# THIS IS THE ROUTE YOU NEED TO MODIFY
# ==============================================================

@app.route('/api/social/connections', methods=['GET', 'POST'])  # ← ADD 'POST' HERE
def social_connections():
    if request.method == 'GET':
        # Your existing GET code (keep unchanged)
        return jsonify({
            "connections": {
                "linkedin": {
                    "account_name": None,
                    "account_type": None,
                    "analytics": {
                        "engagement": 0,
                        "followers": 0,
                        "posts": 0
                    },
                    "client_id": "your-linkedin-client-id",
                    "connected": False,
                    "created_at": "2025-11-06 13:43:02",
                    "last_connected": "2025-11-06 13:43:02.291391",
                    "platform": "linkedin",
                    "username": None
                },
                "twitter": {
                    "account_name": "Presica_Pinto",
                    "account_type": "user",
                    "analytics": {
                        "data_source": "api",
                        "engagement": 2.5,
                        "followers": 850,  # ← This will become 0 after POST
                        "following": 92,  # ← This will become 2 after POST
                        "impressions": 100120,
                        "likes": 7612,
                        "posts": 446,
                        "profile_views": 66,
                        "quality_score": 0,
                        "reach": 1700,
                        "replies": 1808,
                        "retweets": 1441,
                        "tweets": 446,
                        "verified": False
                    },
                    "client_id": "0NAg7eyLuTIFImtKoTPRkpkXj",  # ← This becomes your client ID
                    "connected": True,
                    "created_at": "2025-11-06 13:44:05",
                    "last_connected": "2025-11-06 13:44:05.621238",  # ← This updates to current time
                    "platform": "twitter",
                    "username": "Presica_Pinto"
                }
            },
            "success": True
        })

    elif request.method == 'POST':
        # NEW: Handle POST requests (add this entire section)
        try:
            data = request.json

            if 'twitter' in data:
                twitter_data = data['twitter']
                analytics = twitter_data['analytics']

                # Here you would update your database
                # For example:
                update_database_with_real_data(
                    followers=analytics['followers'],      # ← 0 (real value)
                    following=analytics['following'],      # ← 2 (real value)
                    tweets=analytics['tweets'],            # ← 0 (real value)
                    client_id=twitter_data['client_id'],   # ← "rDHHOI7jpi97n5i5HgxLqKIvw"
                    engagement=analytics['engagement'],   # ← 0.0 (real value)
                    last_connected=datetime.now().isoformat()
                )

                return jsonify({
                    "success": True,
                    "message": "Twitter data updated with real API values"
                })

            return jsonify({
                "success": False,
                "error": "No Twitter data provided"
            }), 400

        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

# ==============================================================
# EXAMPLE DATABASE UPDATE FUNCTION
# ==============================================================

def update_database_with_real_data(followers, following, tweets, client_id, engagement, last_connected):
    """
    This is an example of how to update your database
    Replace with your actual database connection code
    """

    # Example for SQLite:
    import sqlite3
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE social_connections
        SET followers = ?,
            following = ?,
            tweets = ?,
            client_id = ?,
            engagement = ?,
            last_connected = ?,
            data_source = 'real_twitter_api'
        WHERE platform = 'twitter'
    """, (followers, following, tweets, client_id, engagement, last_connected))

    conn.commit()
    conn.close()

    print(f"✅ Database updated with real Twitter data:")
    print(f"   Followers: {followers}")
    print(f"   Following: {following}")
    print(f"   Tweets: {tweets}")
    print(f"   Client ID: {client_id}")

# ==============================================================
# RUN THE EXAMPLE
# ==============================================================

if __name__ == '__main__':
    print("🔧 This is an EXAMPLE backend")
    print("Use this code as a reference to fix your actual backend")
    print("==========================================================")

    # Start the example server on port 5001 (so it doesn't conflict)
    app.run(host='0.0.0.0', port=5001, debug=True)