#!/usr/bin/env python3
"""
Simple Twitter API Integration - Like the working port 5000 system
Fetches and stores real Twitter data for analysis
"""

import os
import requests
import json
import sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv

class SimpleTwitterAPI:
    def __init__(self):
        load_dotenv()
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.base_url = "https://api.twitter.com/2"
        self.init_database()

    def init_database(self):
        """Initialize database for storing Twitter data"""
        os.makedirs('data', exist_ok=True)

        with sqlite3.connect('data/twitter_data.db') as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS twitter_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    followers INTEGER,
                    following INTEGER,
                    tweets INTEGER,
                    verified BOOLEAN,
                    engagement_rate REAL,
                    data_source TEXT,
                    created_at TIMESTAMP,
                    last_updated TIMESTAMP
                )
            ''')
            conn.commit()

    def fetch_twitter_data(self, username="Presica_Pinto"):
        """Fetch real Twitter data using Bearer Token"""
        if not self.bearer_token:
            print("❌ Bearer Token not found")
            return None

        headers = {'Authorization': f'Bearer {self.bearer_token}'}
        params = {'user.fields': 'public_metrics,verified,description,created_at'}

        try:
            response = requests.get(
                f'{self.base_url}/users/by/username/{username}',
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                user_data = response.json()['data']
                public_metrics = user_data.get('public_metrics', {})

                # Calculate engagement rate
                followers = public_metrics.get('followers_count', 0)
                tweets = public_metrics.get('tweet_count', 0)
                engagement_rate = 0.0
                if followers > 0 and tweets > 0:
                    engagement_rate = min((tweets / followers) * 10, 100.0)

                twitter_data = {
                    'username': user_data.get('username'),
                    'followers': followers,
                    'following': public_metrics.get('following_count', 0),
                    'tweets': tweets,
                    'verified': user_data.get('verified', False),
                    'engagement_rate': round(engagement_rate, 2),
                    'data_source': 'twitter_api_v2',
                    'created_at': user_data.get('created_at'),
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }

                print(f"✅ Real Twitter data fetched for @{username}")
                print(f"   Followers: {followers}")
                print(f"   Following: {twitter_data['following']}")
                print(f"   Tweets: {tweets}")
                print(f"   Engagement: {engagement_rate}%")

                return twitter_data
            else:
                print(f"❌ Twitter API Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error fetching Twitter data: {str(e)}")
            return None

    def store_twitter_data(self, data):
        """Store Twitter data in database"""
        if not data:
            return False

        try:
            with sqlite3.connect('data/twitter_data.db') as conn:
                conn.execute('''
                    INSERT INTO twitter_analytics
                    (username, followers, following, tweets, verified, engagement_rate, data_source, created_at, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['username'],
                    data['followers'],
                    data['following'],
                    data['tweets'],
                    data['verified'],
                    data['engagement_rate'],
                    data['data_source'],
                    data['created_at'],
                    data['last_updated']
                ))
                conn.commit()
            print(f"✅ Twitter data stored for @{data['username']}")
            return True
        except Exception as e:
            print(f"❌ Error storing Twitter data: {str(e)}")
            return False

    def get_latest_twitter_data(self, username="Presica_Pinto"):
        """Get latest stored Twitter data"""
        try:
            with sqlite3.connect('data/twitter_data.db') as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM twitter_analytics
                    WHERE username = ?
                    ORDER BY last_updated DESC
                    LIMIT 1
                ''', (username,))
                row = cursor.fetchone()

                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"❌ Error retrieving Twitter data: {str(e)}")
            return None

    def run_twitter_integration(self):
        """Run complete Twitter integration"""
        print("🚀 Starting Twitter API Integration")
        print("=" * 50)

        # Step 1: Fetch real data
        twitter_data = self.fetch_twitter_data()

        if twitter_data:
            # Step 2: Store data
            if self.store_twitter_data(twitter_data):
                print("✅ Twitter integration completed successfully!")
                return twitter_data
            else:
                print("❌ Failed to store Twitter data")
                return None
        else:
            print("❌ Failed to fetch Twitter data")
            return None

# API endpoints for Flask integration
def get_twitter_analytics_for_dashboard():
    """Get Twitter analytics for dashboard display"""
    try:
        api = SimpleTwitterAPI()

        # Try to get fresh data first
        fresh_data = api.fetch_twitter_data()
        if fresh_data:
            api.store_twitter_data(fresh_data)
            return fresh_data

        # Fallback to stored data
        stored_data = api.get_latest_twitter_data()
        if stored_data:
            return stored_data

        # Final fallback with basic data
        return {
            'username': 'Presica_Pinto',
            'followers': 0,
            'following': 0,
            'tweets': 0,
            'verified': False,
            'engagement_rate': 0.0,
            'data_source': 'fallback',
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        print(f"❌ Error in get_twitter_analytics_for_dashboard: {str(e)}")
        return None

def check_twitter_connection_status():
    """Check if Twitter credentials are configured for connection"""
    try:
        # Check if Twitter credentials are configured in environment
        from dotenv import load_dotenv
        import os
        load_dotenv()

        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        client_id = os.getenv('TWITTER_CLIENT_ID')
        client_secret = os.getenv('TWITTER_CLIENT_SECRET')

        # Connection status based on credentials availability
        if bearer_token and client_id and client_secret:
            print("✅ Twitter connection status: Credentials configured")

            # Try to get latest cached data for display (but don't fail connection status)
            try:
                with sqlite3.connect('data/twitter_data.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT username, followers, last_updated
                        FROM twitter_analytics
                        ORDER BY last_updated DESC
                        LIMIT 1
                    ''')
                    latest_data = cursor.fetchone()

                    if latest_data:
                        username, followers, last_updated = latest_data
                        return {
                            'connected': True,
                            'account_name': username or 'Twitter Account',
                            'followers': followers or 0,
                            'data_source': 'Credentials configured',
                            'last_connected': last_updated,
                            'note': 'Click "Refresh Data" for latest analytics'
                        }
            except:
                pass

            return {
                'connected': True,
                'account_name': 'Twitter Account',
                'followers': 0,
                'data_source': 'Credentials configured',
                'note': 'Click "Refresh Data" for latest analytics'
            }
        else:
            print("❌ Twitter connection status: Missing credentials")
            return {
                'connected': False,
                'reason': 'Twitter credentials not configured'
            }

    except Exception as e:
        print(f"❌ Error checking Twitter connection status: {str(e)}")
        return {'connected': False, 'reason': f'Configuration error: {str(e)}'}

if __name__ == "__main__":
    # Run integration test
    api = SimpleTwitterAPI()
    result = api.run_twitter_integration()

    if result:
        print("\n📊 Analysis Ready!")
        print(f"Real Twitter data for @{result['username']} is now available for analysis")
    else:
        print("\n❌ Integration failed")