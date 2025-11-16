#!/usr/bin/env python3
"""
PROPER Twitter Integration - Connect real Twitter API data to backend
This is the correct way to do it
"""

import os
import sys
import json
import requests
import time
from datetime import datetime, timezone

class ProperTwitterIntegration:
    """Proper Twitter API integration for backend"""

    def __init__(self):
        self.bearer_token = None
        self.client_id = None
        self.base_url = "https://api.twitter.com/2"
        self.backend_endpoint = "http://172.29.89.92:5000/api/social/connections"
        self.setup_credentials()

    def setup_credentials(self):
        """Setup proper Twitter API credentials"""
        from dotenv import load_dotenv
        load_dotenv()

        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.client_id = os.getenv('TWITTER_CLIENT_ID')

        if not self.bearer_token or not self.client_id:
            raise ValueError("❌ Twitter API credentials not found")

        print(f"✅ Using proper credentials:")
        print(f"   Client ID: {self.client_id}")
        print(f"   Bearer Token: {self.bearer_token[:20]}...")

    def check_rate_limit_status(self):
        """Check if we can make API calls"""
        try:
            headers = {'Authorization': f'Bearer {self.bearer_token}'}
            test_response = requests.get(
                f"{self.base_url}/users/by/username/twitter",
                headers=headers,
                timeout=5
            )

            remaining = test_response.headers.get('x-rate-limit-remaining', '0')
            print(f"📊 Rate limit status: {remaining} requests remaining")

            return remaining != '0'

        except:
            print("⚠️ Could not check rate limit")
            return False

    def get_real_twitter_data(self, username="Presica_Pinto"):
        """Get real data from Twitter API"""
        print(f"\n🐦 Fetching REAL data for @{username}")

        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        # Get user data
        user_params = {
            'user.fields': 'created_at,description,public_metrics,verified,url,username,profile_image_url'
        }

        user_response = requests.get(
            f"{self.base_url}/users/by/username/{username}",
            headers=headers,
            params=user_params
        )

        if user_response.status_code != 200:
            print(f"❌ Failed to get user data: {user_response.status_code}")
            return None

        user_data = user_response.json()['data']
        public_metrics = user_data.get('public_metrics', {})

        # Get recent tweets
        user_id = user_data.get('id')
        tweet_params = {
            'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
            'max_results': 10,
            'exclude': 'retweets'
        }

        tweet_response = requests.get(
            f"{self.base_url}/users/{user_id}/tweets",
            headers=headers,
            params=tweet_params
        )

        # Calculate real metrics
        real_metrics = {
            'recent_likes': 0,
            'recent_retweets': 0,
            'recent_replies': 0,
            'recent_impressions': 0,
            'tweets_analyzed': 0
        }

        if tweet_response.status_code == 200:
            tweets = tweet_response.json().get('data', [])
            real_metrics['tweets_analyzed'] = len(tweets)

            for tweet in tweets:
                tweet_metrics = tweet.get('public_metrics', {})
                real_metrics['recent_likes'] += tweet_metrics.get('like_count', 0)
                real_metrics['recent_retweets'] += tweet_metrics.get('retweet_count', 0)
                real_metrics['recent_replies'] += tweet_metrics.get('reply_count', 0)
                real_metrics['recent_impressions'] += tweet_metrics.get('impression_count', 0)

        # Build proper data structure
        current_time = datetime.now(timezone.utc).isoformat()

        # Calculate engagement rate
        engagement = 0.0
        if real_metrics['recent_impressions'] > 0:
            total_engagement = (real_metrics['recent_likes'] +
                              real_metrics['recent_retweets'] +
                              real_metrics['recent_replies'])
            engagement = round((total_engagement / real_metrics['recent_impressions']) * 100, 2)

        proper_data = {
            "twitter": {
                "account_name": user_data.get('username'),
                "account_type": "user",
                "analytics": {
                    "data_source": "real_twitter_api",
                    "engagement": engagement,
                    "followers": public_metrics.get('followers_count', 0),
                    "following": public_metrics.get('following_count', 0),
                    "impressions": real_metrics['recent_impressions'],
                    "likes": real_metrics['recent_likes'],
                    "posts": public_metrics.get('tweet_count', 0),
                    "profile_views": public_metrics.get('profile_views', 0),
                    "quality_score": 0,
                    "reach": public_metrics.get('followers_count', 0),
                    "replies": real_metrics['recent_replies'],
                    "retweets": real_metrics['recent_retweets'],
                    "tweets": public_metrics.get('tweet_count', 0),
                    "verified": user_data.get('verified', False)
                },
                "client_id": self.client_id,  # Use YOUR client ID
                "connected": True,
                "created_at": current_time,
                "last_connected": current_time,
                "platform": "twitter",
                "username": user_data.get('username')
            }
        }

        return proper_data

    def update_backend_properly(self, data):
        """Proper way to update backend"""
        print(f"\n🔄 PROPER backend update methods:")

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ProperTwitterIntegration/1.0'
        }

        # Method 1: Check if backend supports any POST endpoints
        alternative_endpoints = [
            f"{self.backend_endpoint}/update",
            f"{self.backend_endpoint}/sync",
            f"{self.backend_endpoint}/twitter/update",
            f"http://172.29.89.92:5000/api/social/twitter/update",
            f"http://172.29.89.92:5000/api/analytics/update"
        ]

        for endpoint in alternative_endpoints:
            try:
                print(f"📤 Trying: {endpoint}")
                response = requests.post(endpoint, json=data, headers=headers, timeout=5)
                if response.status_code in [200, 201, 204]:
                    print(f"✅ SUCCESS: Backend updated via {endpoint}")
                    return True
                else:
                    print(f"   Status: {response.status_code}")
            except:
                print(f"   Failed to connect")

        print(f"\n❌ No POST endpoints work")
        return False

    def show_current_backend_state(self):
        """Show what's currently in backend"""
        print(f"\n📊 CURRENT BACKEND STATE:")

        try:
            response = requests.get(self.backend_endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                twitter_data = data.get('connections', {}).get('twitter', {})

                if twitter_data:
                    analytics = twitter_data.get('analytics', {})
                    print(f"   Followers: {analytics.get('followers', 'N/A')}")
                    print(f"   Following: {analytics.get('following', 'N/A')}")
                    print(f"   Tweets: {analytics.get('tweets', 'N/A')}")
                    print(f"   Client ID: {twitter_data.get('client_id', 'N/A')}")
                    print(f"   Last Updated: {twitter_data.get('last_connected', 'N/A')}")
                    print(f"   Data Source: {analytics.get('data_source', 'N/A')}")

                    # Check if data is old
                    last_updated = twitter_data.get('last_connected', '')
                    if last_updated:
                        try:
                            update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                            now = datetime.now(timezone.utc)
                            hours_old = (now - update_time).total_seconds() / 3600
                            print(f"   Data Age: {hours_old:.1f} hours old")

                            if hours_old > 1:
                                print(f"   ⚠️ Data is old - needs update!")
                        except:
                            pass
                else:
                    print(f"   No Twitter data found in backend")
            else:
                print(f"   Cannot fetch backend data: {response.status_code}")

        except Exception as e:
            print(f"   Error checking backend: {str(e)}")

    def save_proper_data_locally(self, data):
        """Save proper data locally"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"PROPER_TWITTER_DATA_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Proper data saved to: {filename}")
        return filename

    def run_proper_integration(self):
        """Run the proper integration process"""
        print("🚀 PROPER TWITTER INTEGRATION")
        print("=" * 60)
        print("This is the correct way to integrate Twitter data with backend")

        # Step 1: Check current backend state
        self.show_current_backend_state()

        # Step 2: Check rate limit
        if not self.check_rate_limit_status():
            print(f"\n⏰ Rate limit active. Wait 15 minutes and try again.")
            return

        # Step 3: Get real data
        real_data = self.get_real_twitter_data()

        if not real_data:
            print(f"❌ Failed to get real Twitter data")
            return

        # Step 4: Display real data
        analytics = real_data['twitter']['analytics']
        print(f"\n📊 REAL TWITTER DATA:")
        print(f"   Followers: {analytics['followers']:,}")
        print(f"   Following: {analytics['following']:,}")
        print(f"   Tweets: {analytics['tweets']:,}")
        print(f"   Recent Likes: {analytics['likes']}")
        print(f"   Recent Retweets: {analytics['retweets']}")
        print(f"   Recent Replies: {analytics['replies']}")
        print(f"   Engagement Rate: {analytics['engagement']:.2f}%")
        print(f"   Client ID: {real_data['twitter']['client_id']}")
        print(f"   Data Source: {analytics['data_source']}")

        # Step 5: Save locally
        self.save_proper_data_locally(real_data)

        # Step 6: Try to update backend
        backend_updated = self.update_backend_properly(real_data)

        if not backend_updated:
            print(f"\n💡 BACKEND UPDATE OPTIONS:")
            print(f"   1. Contact backend admin to enable POST endpoints")
            print(f"   2. Manually update database with the data above")
            print(f"   3. Use the saved JSON file to update via admin panel")
            print(f"   4. Set up a proper API endpoint for social media updates")

        print(f"\n✅ Proper integration completed!")

def main():
    """Main function"""
    try:
        integration = ProperTwitterIntegration()
        integration.run_proper_integration()
    except Exception as e:
        print(f"❌ Integration failed: {str(e)}")

if __name__ == "__main__":
    main()